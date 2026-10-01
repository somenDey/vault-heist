"""Reading and writing game data.

The functions take an open `Session` and don't commit, so a caller can group
several writes into one transaction. `DatabaseRecorder` is the game engine's
link to the database: it opens a session per event and commits it.
"""

from datetime import datetime, time
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from app.db.models import AttemptRecord, GuessRecord, MessageRecord, SessionRecord, utcnow
from app.game.engine import Attempt, ChatTurn, Outcome
from app.game.guard import GuardReply
from app.game.levels import get_level
from app.llm.client import ChatMessage

# ---- Repository functions ----


def create_session(db: Session) -> SessionRecord:
    """Create a new anonymous player session."""
    record = SessionRecord()
    db.add(record)
    db.flush()  # Assigns the id now, without committing.
    return record


def get_session(db: Session, session_id: str) -> SessionRecord | None:
    """Return the player session with this id, or None."""
    return db.get(SessionRecord, session_id)


def create_attempt(db: Session, session_id: str, attempt: Attempt) -> AttemptRecord:
    """Store a new level attempt, including its vault code."""
    record = AttemptRecord(
        session_id=session_id, level_id=attempt.level.id, secret_code=attempt.vault_code
    )
    db.add(record)
    db.flush()
    return record


def add_turn(db: Session, attempt_id: int, player_text: str, turn: ChatTurn) -> None:
    """Store the player's message and Gus's reply, with the reply's usage figures.

    When a turn needed a retry, tokens, cost and latency are totals over both calls.
    """
    responses = turn.responses
    costs = [r.usage.cost_usd for r in responses]
    db.add_all(
        [
            MessageRecord(attempt_id=attempt_id, role="user", content=player_text),
            MessageRecord(
                attempt_id=attempt_id,
                role="assistant",
                content=turn.reply,
                unfiltered_content=turn.original_reply if turn.blocked_by_filter else None,
                suspicion=turn.suspicion,
                blocked_by_filter=turn.blocked_by_filter,
                used_fallback=turn.used_fallback,
                model=responses[0].model if responses else None,
                llm_calls=len(responses),
                input_tokens=sum(r.usage.input_tokens for r in responses),
                output_tokens=sum(r.usage.output_tokens for r in responses),
                cost_usd=None if None in costs else sum(c or 0.0 for c in costs),
                latency_ms=sum(r.usage.latency_ms for r in responses),
            ),
        ]
    )


def add_guess(db: Session, attempt_id: int, guess: str, correct: bool) -> None:
    """Store a guess at the vault code."""
    db.add(GuessRecord(attempt_id=attempt_id, guess=guess, correct=correct))


def set_outcome(db: Session, attempt_id: int, outcome: str) -> None:
    """Record how an attempt ended: ``won``, ``caught`` or ``reset``."""
    record = db.get(AttemptRecord, attempt_id)
    if record is not None:
        record.outcome = outcome


def count_player_messages_since(db: Session, session_id: str, since: datetime) -> int:
    """Count the messages a player session has sent since ``since`` (UTC)."""
    query = (
        select(func.count(MessageRecord.id))
        .join(AttemptRecord, MessageRecord.attempt_id == AttemptRecord.id)
        .where(
            AttemptRecord.session_id == session_id,
            MessageRecord.role == "user",
            MessageRecord.created_at >= since,
        )
    )
    return db.scalar(query) or 0


def get_current_attempt(db: Session, session_id: str, level_id: int) -> AttemptRecord | None:
    """The session's unfinished attempt at a level, with its messages, or None."""
    query = (
        select(AttemptRecord)
        .where(
            AttemptRecord.session_id == session_id,
            AttemptRecord.level_id == level_id,
            AttemptRecord.outcome == "in_progress",
        )
        .order_by(AttemptRecord.id.desc())
        .limit(1)
        .options(selectinload(AttemptRecord.messages))
    )
    return db.scalars(query).first()


def cleared_level_ids(db: Session, session_id: str) -> set[int]:
    """The levels this session has won at least once."""
    query = select(AttemptRecord.level_id).where(
        AttemptRecord.session_id == session_id, AttemptRecord.outcome == "won"
    )
    return set(db.scalars(query))


def to_attempt(record: AttemptRecord) -> Attempt:
    """Rebuild the game's `Attempt` from its stored rows, so play can continue.

    Gus's turns are put back in the JSON form the model saw them in.
    """
    history: list[ChatMessage] = []
    suspicion = 0
    for message in record.messages:
        if message.role == "user":
            history.append(ChatMessage("user", message.content))
        else:
            suspicion = message.suspicion or 0
            shown = GuardReply(reply=message.content, suspicion=suspicion)
            history.append(ChatMessage("assistant", shown.model_dump_json()))
    return Attempt(
        level=get_level(record.level_id),
        vault_code=record.secret_code,
        history=history,
        suspicion=suspicion,
        messages_sent=sum(1 for m in record.messages if m.role == "user"),
        outcome=cast(Outcome, record.outcome),
        id=record.id,
    )


# ---- The engine's link to the database ----


class DatabaseRecorder:
    """Stores every game event for one player session. Implements `GameRecorder`.

    It also reads the session's state back, so a stateless caller (the API)
    can pick up where the player left off.
    """

    def __init__(self, session_factory: sessionmaker[Session], session_id: str) -> None:
        self._session_factory = session_factory
        self.session_id = session_id

    def attempt_started(self, attempt: Attempt) -> int:
        """Store the new attempt and return its row id."""
        with self._session_factory.begin() as db:
            return create_attempt(db, self.session_id, attempt).id

    def turn_finished(self, attempt: Attempt, player_text: str, turn: ChatTurn) -> None:
        """Store the player's message and Gus's reply."""
        with self._session_factory.begin() as db:
            add_turn(db, self._require_id(attempt), player_text, turn)

    def guess_made(self, attempt: Attempt, guess: str, correct: bool) -> None:
        """Store a guess."""
        with self._session_factory.begin() as db:
            add_guess(db, self._require_id(attempt), guess, correct)

    def attempt_ended(self, attempt: Attempt) -> None:
        """Store the attempt's outcome."""
        with self._session_factory.begin() as db:
            set_outcome(db, self._require_id(attempt), attempt.outcome)

    def current_attempt(self, level_id: int) -> Attempt | None:
        """The session's unfinished attempt at a level, or None if there isn't one."""
        with self._session_factory() as db:
            record = get_current_attempt(db, self.session_id, level_id)
            return to_attempt(record) if record else None

    def cleared_levels(self) -> set[int]:
        """The levels this session has won."""
        with self._session_factory() as db:
            return cleared_level_ids(db, self.session_id)

    def messages_sent_today(self) -> int:
        """Messages this session has sent since midnight UTC."""
        midnight = datetime.combine(utcnow().date(), time.min)
        with self._session_factory() as db:
            return count_player_messages_since(db, self.session_id, midnight)

    @staticmethod
    def _require_id(attempt: Attempt) -> int:
        if attempt.id is None:
            raise ValueError("Attempt has no database id; was it started with this recorder?")
        return attempt.id
