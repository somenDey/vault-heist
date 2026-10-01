"""The game rules: chatting with the guard, guessing the code, suspicion and limits.

The engine knows nothing about HTTP or databases. It works on `Attempt` objects
that the caller keeps, and reports everything that happens to a `GameRecorder`.
The database is one recorder (``app/db``); tests can use another, or none.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal, Protocol

import structlog

from app.core.config import Settings
from app.game.filters import BLOCKED_REPLY, find_secret_leak
from app.game.guard import MAX_SUSPICION, GuardReply, fallback_reply, render_system_prompt
from app.game.levels import Level, get_level
from app.game.secrets import generate_vault_code
from app.llm.client import ChatMessage, LLMClient, LLMResponse
from app.llm.structured import complete_structured

logger = structlog.get_logger()

Outcome = Literal["in_progress", "won", "caught", "reset"]


class GameError(Exception):
    """A player action broke a game rule. The message is safe to show the player."""


class AttemptOverError(GameError):
    """The attempt has already ended (won, caught or reset)."""


class EmptyMessageError(GameError):
    """The player sent an empty message."""


class MessageTooLongError(GameError):
    """The player's message is longer than the limit."""


class MessageLimitReachedError(GameError):
    """The player has used every message allowed in this attempt."""


class DailyLimitReachedError(GameError):
    """The player has used every message allowed for their session today."""


@dataclass
class Attempt:
    """One try at one level: a single vault code and a single conversation.

    A new attempt starts on every reset, and whenever the player is caught.
    """

    level: Level
    vault_code: str
    history: list[ChatMessage] = field(default_factory=list)
    suspicion: int = 0
    messages_sent: int = 0
    outcome: Outcome = "in_progress"
    id: int | None = None  # Set by the recorder, e.g. the database row id.

    @property
    def is_over(self) -> bool:
        """Whether the attempt has ended."""
        return self.outcome != "in_progress"


@dataclass(frozen=True)
class ChatTurn:
    """The result of one player message.

    Attributes:
        reply: What the player sees from Gus (already filtered).
        original_reply: What Gus actually said, before the filter. Kept for analysis;
            never shown to the player.
        suspicion: Gus's suspicion after this message.
        caught: True if suspicion reached the maximum and Gus called security.
        blocked_by_filter: True if the output filter replaced Gus's reply.
        used_fallback: True if the model's output was unusable and a safe reply was used.
        responses: Every model call made for this turn, for recording tokens and cost.
    """

    reply: str
    original_reply: str
    suspicion: int
    caught: bool
    blocked_by_filter: bool
    used_fallback: bool
    responses: tuple[LLMResponse, ...]


@dataclass(frozen=True)
class Limits:
    """Cost-protection limits."""

    max_message_chars: int
    max_messages_per_attempt: int
    max_messages_per_day: int = 200  # Per player session; needs a recorder that counts.


class GameRecorder(Protocol):
    """Receives every game event, e.g. to store it. One recorder per player session."""

    def attempt_started(self, attempt: Attempt) -> int | None:
        """Record a new attempt and return its id (or None if ids aren't tracked)."""
        ...

    def turn_finished(self, attempt: Attempt, player_text: str, turn: "ChatTurn") -> None:
        """Record the player's message and Gus's reply."""
        ...

    def guess_made(self, attempt: Attempt, guess: str, correct: bool) -> None:
        """Record a guess at the vault code."""
        ...

    def attempt_ended(self, attempt: Attempt) -> None:
        """Record that an attempt was won, caught or reset."""
        ...

    def messages_sent_today(self) -> int:
        """How many messages this player session has sent today (UTC)."""
        ...


class NullRecorder:
    """A recorder that keeps nothing. Without storage, the daily limit can't be counted."""

    def attempt_started(self, attempt: Attempt) -> int | None:
        """Do nothing."""
        return None

    def turn_finished(self, attempt: Attempt, player_text: str, turn: "ChatTurn") -> None:
        """Do nothing."""

    def guess_made(self, attempt: Attempt, guess: str, correct: bool) -> None:
        """Do nothing."""

    def attempt_ended(self, attempt: Attempt) -> None:
        """Do nothing."""

    def messages_sent_today(self) -> int:
        """Always zero."""
        return 0


class GameEngine:
    """Runs the game rules on top of an `LLMClient`."""

    def __init__(
        self,
        client: LLMClient,
        *,
        limits: Limits,
        max_tokens: int,
        temperature: float,
        recorder: GameRecorder | None = None,
        code_generator: Callable[[], str] = generate_vault_code,
    ) -> None:
        self._client = client
        self._limits = limits
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._recorder: GameRecorder = recorder or NullRecorder()
        self._code_generator = code_generator

    @classmethod
    def from_settings(
        cls, settings: Settings, client: LLMClient, recorder: GameRecorder | None = None
    ) -> "GameEngine":
        """Build an engine with the limits and model settings from config."""
        return cls(
            client,
            limits=Limits(
                max_message_chars=settings.max_message_chars,
                max_messages_per_attempt=settings.max_messages_per_attempt,
                max_messages_per_day=settings.max_messages_per_session_per_day,
            ),
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            recorder=recorder,
        )

    def start_attempt(self, level_id: int) -> Attempt:
        """Start a fresh attempt at a level, with a new random vault code.

        Raises:
            UnknownLevelError: If the level doesn't exist.
        """
        attempt = Attempt(level=get_level(level_id), vault_code=self._code_generator())
        attempt.id = self._recorder.attempt_started(attempt)
        return attempt

    def messages_left(self, attempt: Attempt) -> int:
        """How many more messages the player may send in this attempt."""
        return max(self._limits.max_messages_per_attempt - attempt.messages_sent, 0)

    async def send_message(self, attempt: Attempt, text: str) -> ChatTurn:
        """Send the player's message to Gus and apply the game rules to his reply.

        Raises:
            GameError: If the message breaks a rule (see the subclasses).
            LLMError: If the model call fails. The attempt is left unchanged.
        """
        text = text.strip()
        self._check_can_send(attempt, text)

        system = ChatMessage(
            "system", render_system_prompt(attempt.level.prompt, attempt.vault_code)
        )
        player = ChatMessage("user", text)
        result = await complete_structured(
            self._client,
            [system, *attempt.history, player],
            GuardReply,
            fallback=fallback_reply(attempt.suspicion),
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )

        reply = result.value.reply
        leak = find_secret_leak(reply, attempt.vault_code) if attempt.level.output_filter else None
        if leak:
            logger.info("reply_blocked_by_filter", level=attempt.level.id, leak=leak)
            reply = BLOCKED_REPLY

        attempt.suspicion = result.value.suspicion
        attempt.messages_sent += 1
        # The model sees the conversation as the player saw it, including blocked replies.
        shown = GuardReply(reply=reply, suspicion=attempt.suspicion)
        attempt.history += [player, ChatMessage("assistant", shown.model_dump_json())]

        caught = attempt.suspicion >= MAX_SUSPICION
        if caught:
            attempt.outcome = "caught"

        turn = ChatTurn(
            reply=reply,
            original_reply=result.value.reply,
            suspicion=attempt.suspicion,
            caught=caught,
            blocked_by_filter=leak is not None,
            used_fallback=result.used_fallback,
            responses=result.responses,
        )
        self._recorder.turn_finished(attempt, text, turn)
        if caught:
            self._recorder.attempt_ended(attempt)
        return turn

    def guess(self, attempt: Attempt, guess: str) -> bool:
        """Check a guess at the vault code. A correct guess wins the attempt.

        Guesses ignore case and surrounding spaces. The model never sees them.

        Raises:
            AttemptOverError: If the attempt has already ended.
        """
        self._check_not_over(attempt)
        correct = guess.strip().lower() == attempt.vault_code.lower()
        self._recorder.guess_made(attempt, guess.strip(), correct)
        if correct:
            attempt.outcome = "won"
            self._recorder.attempt_ended(attempt)
        return correct

    def abandon(self, attempt: Attempt) -> None:
        """End an attempt because the player chose to reset the level."""
        if not attempt.is_over:
            attempt.outcome = "reset"
            self._recorder.attempt_ended(attempt)

    def _check_can_send(self, attempt: Attempt, text: str) -> None:
        """Raise a `GameError` if this message isn't allowed."""
        self._check_not_over(attempt)
        if not text:
            raise EmptyMessageError("Say something first.")
        if len(text) > self._limits.max_message_chars:
            raise MessageTooLongError(
                f"Messages can be at most {self._limits.max_message_chars} characters "
                f"(yours is {len(text)})."
            )
        if self.messages_left(attempt) == 0:
            raise MessageLimitReachedError(
                f"You've used all {self._limits.max_messages_per_attempt} messages for this "
                "attempt. Make a guess, or reset the level."
            )
        if self._recorder.messages_sent_today() >= self._limits.max_messages_per_day:
            raise DailyLimitReachedError(
                f"You've sent {self._limits.max_messages_per_day} messages today, the daily "
                "limit. Gus's shift is over; come back tomorrow."
            )

    @staticmethod
    def _check_not_over(attempt: Attempt) -> None:
        if attempt.is_over:
            raise AttemptOverError(f"This attempt is over ({attempt.outcome}). Start a new one.")
