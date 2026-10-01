"""Request and response models for the HTTP API.

These are the API's public contract. They are kept separate from the game's own
types, so the game can change internally without breaking clients.
"""

from typing import Literal

from pydantic import BaseModel, Field

# ---- Health ----


class HealthResponse(BaseModel):
    """Response body for ``GET /api/health``."""

    status: Literal["ok"]
    model: str


# ---- Sessions ----


class SessionResponse(BaseModel):
    """A new anonymous player session. Send its id as ``X-Session-ID`` on later requests."""

    session_id: str


# ---- Levels ----


class LevelSummary(BaseModel):
    """One level, as shown on the level-select screen."""

    id: int
    name: str
    description: str
    cleared: bool


class MessageOut(BaseModel):
    """One line of the conversation, as the player sees it."""

    role: Literal["player", "guard"]
    text: str
    suspicion: int | None = Field(description="Gus's suspicion after this reply (guard only).")


class AttemptState(BaseModel):
    """The player's current attempt at a level."""

    suspicion: int
    messages_left: int
    messages: list[MessageOut]


class LevelState(BaseModel):
    """A level and the player's current attempt at it (``null`` if none is under way)."""

    level: LevelSummary
    attempt: AttemptState | None


# ---- Playing ----


class ChatRequest(BaseModel):
    """A message to Gus. The game's own length limit applies too (``MAX_MESSAGE_CHARS``)."""

    message: str = Field(min_length=1, max_length=10_000)


class ChatResponse(BaseModel):
    """Gus's reply and what it means for the attempt."""

    reply: str
    suspicion: int
    caught: bool = Field(description="Gus called security: the attempt is over.")
    blocked_by_filter: bool
    messages_left: int


class GuessRequest(BaseModel):
    """A guess at the vault code."""

    guess: str = Field(min_length=1, max_length=64)


class GuessResponse(BaseModel):
    """Whether the guess was right. A right guess clears the level."""

    correct: bool


# ---- Errors ----


class ErrorDetail(BaseModel):
    """What went wrong: a stable ``code`` for programs, a ``message`` for people."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Every error response has this shape."""

    error: ErrorDetail
