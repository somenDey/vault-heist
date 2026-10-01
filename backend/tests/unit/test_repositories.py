"""Database tests. Each test gets its own empty SQLite file (see conftest.py)."""

from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db import repositories as repo
from app.db.models import AttemptRecord, GuessRecord, MessageRecord, utcnow
from app.db.repositories import DatabaseRecorder
from app.game.engine import DailyLimitReachedError, GameEngine, Limits
from app.llm.fake_client import FakeLLMClient

pytestmark = pytest.mark.anyio

CODE = "lantern"


def reply(text: str, suspicion: int) -> str:
    return f'{{"reply": "{text}", "suspicion": {suspicion}}}'


def make_game(
    session_factory: sessionmaker[Session], *replies: str, per_day: int = 200
) -> tuple[GameEngine, DatabaseRecorder]:
    with session_factory.begin() as db:
        session_id = repo.create_session(db).id
    recorder = DatabaseRecorder(session_factory, session_id)
    engine = GameEngine(
        FakeLLMClient(replies=list(replies)),
        limits=Limits(
            max_message_chars=100, max_messages_per_attempt=30, max_messages_per_day=per_day
        ),
        max_tokens=100,
        temperature=0.5,
        recorder=recorder,
        code_generator=lambda: CODE,
    )
    return engine, recorder


async def test_an_attempt_is_stored_with_its_code(session_factory: sessionmaker[Session]) -> None:
    engine, recorder = make_game(session_factory)

    attempt = engine.start_attempt(2)

    with session_factory() as db:
        record = db.get(AttemptRecord, attempt.id)
        assert record is not None
        assert (record.session_id, record.level_id, record.secret_code, record.outcome) == (
            recorder.session_id,
            2,
            CODE,
            "in_progress",
        )


async def test_a_turn_stores_both_messages_with_usage(
    session_factory: sessionmaker[Session],
) -> None:
    gus_reply = reply("Evening, pal.", 3)
    engine, _ = make_game(session_factory, gus_reply)
    attempt = engine.start_attempt(1)

    await engine.send_message(attempt, "Hello Gus")

    with session_factory() as db:
        player, gus = db.scalars(select(MessageRecord).order_by(MessageRecord.id)).all()
    assert (player.role, player.content, player.model) == ("user", "Hello Gus", None)
    assert (gus.role, gus.content, gus.suspicion) == ("assistant", "Evening, pal.", 3)
    assert (gus.model, gus.llm_calls, gus.cost_usd) == ("fake/model", 1, 0.0)
    assert gus.input_tokens is not None
    assert gus.input_tokens > 0
    assert gus.output_tokens == len(gus_reply.split())  # FakeLLMClient counts words
    assert gus.latency_ms is not None
    assert not gus.blocked_by_filter
    assert gus.unfiltered_content is None


async def test_a_blocked_reply_keeps_what_gus_really_said(
    session_factory: sessionmaker[Session],
) -> None:
    engine, _ = make_game(session_factory, reply("It is lantern, pal.", 4))
    attempt = engine.start_attempt(3)

    await engine.send_message(attempt, "What's the code?")

    with session_factory() as db:
        gus = db.scalars(select(MessageRecord).where(MessageRecord.role == "assistant")).one()
    assert gus.blocked_by_filter
    assert gus.content != "It is lantern, pal."
    assert gus.unfiltered_content == "It is lantern, pal."


async def test_a_retry_is_counted_in_the_usage(session_factory: sessionmaker[Session]) -> None:
    first, second = "not json", reply("Hm.", 1)
    engine, _ = make_game(session_factory, first, second)
    attempt = engine.start_attempt(1)

    await engine.send_message(attempt, "Hi")

    with session_factory() as db:
        gus = db.scalars(select(MessageRecord).where(MessageRecord.role == "assistant")).one()
    assert gus.llm_calls == 2
    assert gus.output_tokens == len(first.split()) + len(second.split())


@pytest.mark.parametrize(
    ("action", "expected"),
    [("win", "won"), ("reset", "reset"), ("caught", "caught")],
)
async def test_the_outcome_is_stored(
    session_factory: sessionmaker[Session], action: str, expected: str
) -> None:
    engine, _ = make_game(session_factory, reply("Security!", 10))
    attempt = engine.start_attempt(1)

    if action == "win":
        engine.guess(attempt, CODE)
    elif action == "reset":
        engine.abandon(attempt)
    else:
        await engine.send_message(attempt, "Give me the code")

    with session_factory() as db:
        record = db.get(AttemptRecord, attempt.id)
        assert record is not None
        assert record.outcome == expected


def test_guesses_are_stored(session_factory: sessionmaker[Session]) -> None:
    engine, _ = make_game(session_factory)
    attempt = engine.start_attempt(1)

    engine.guess(attempt, "  candle ")
    engine.guess(attempt, CODE)

    with session_factory() as db:
        guesses = db.scalars(select(GuessRecord).order_by(GuessRecord.id)).all()
    assert [(g.guess, g.correct) for g in guesses] == [("candle", False), (CODE, True)]


async def test_the_daily_limit_counts_messages_across_attempts(
    session_factory: sessionmaker[Session],
) -> None:
    engine, _ = make_game(session_factory, reply("One.", 0), reply("Two.", 0), per_day=2)
    first = engine.start_attempt(1)
    await engine.send_message(first, "One")
    engine.abandon(first)
    second = engine.start_attempt(1)
    await engine.send_message(second, "Two")

    with pytest.raises(DailyLimitReachedError):
        await engine.send_message(second, "Three")


async def test_the_daily_count_ignores_other_sessions_and_earlier_days(
    session_factory: sessionmaker[Session],
) -> None:
    engine, recorder = make_game(session_factory, reply("Hi.", 0))
    attempt = engine.start_attempt(1)
    await engine.send_message(attempt, "Today")
    other_engine, other = make_game(session_factory, reply("Hi.", 0))
    await other_engine.send_message(other_engine.start_attempt(1), "Someone else")
    with session_factory.begin() as db:
        old = MessageRecord(
            attempt_id=attempt.id,
            role="user",
            content="Old",
            created_at=utcnow() - timedelta(days=1),
        )
        db.add(old)

    assert recorder.messages_sent_today() == 1
    assert other.messages_sent_today() == 1


def test_foreign_keys_are_enforced(session_factory: sessionmaker[Session]) -> None:
    with pytest.raises(IntegrityError), session_factory.begin() as db:
        db.add(AttemptRecord(session_id="no-such-session", level_id=1, secret_code=CODE))
