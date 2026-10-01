"""Levels: list them, look at one, chat, guess and reset.

Every route is thin: find the player's current attempt, call the game engine,
and translate the result into a response. The rules live in ``app/game``.
"""

from fastapi import APIRouter

from app.api.dependencies import GameEngineDep, RecorderDep
from app.api.schemas import (
    AttemptState,
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    GuessRequest,
    GuessResponse,
    LevelState,
    LevelSummary,
    MessageOut,
)
from app.db.repositories import DatabaseRecorder
from app.game.engine import Attempt, GameEngine
from app.game.guard import GuardReply
from app.game.levels import LEVELS, Level, get_level

# Documented in the OpenAPI page, so API users can see every error they may get.
ERRORS: dict[int | str, dict[str, object]] = {
    401: {"model": ErrorResponse, "description": "Missing or unknown `X-Session-ID`"},
    404: {"model": ErrorResponse, "description": "Unknown level"},
}
CHAT_ERRORS: dict[int | str, dict[str, object]] = {
    400: {"model": ErrorResponse, "description": "Empty or too-long message"},
    409: {"model": ErrorResponse, "description": "The attempt has already ended"},
    429: {"model": ErrorResponse, "description": "Message limit reached (attempt or daily)"},
    503: {"model": ErrorResponse, "description": "The model is unavailable"},
}

router = APIRouter(prefix="/levels", tags=["levels"], responses=ERRORS)


@router.get("")
def list_levels(recorder: RecorderDep) -> list[LevelSummary]:
    """All levels, and whether this player has cleared each one."""
    cleared = recorder.cleared_levels()
    return [summarise(level, level.id in cleared) for level in LEVELS]


@router.get("/{level_id}")
def get_level_state(level_id: int, engine: GameEngineDep, recorder: RecorderDep) -> LevelState:
    """One level, with the player's attempt in progress (if any) and its conversation."""
    level = get_level(level_id)
    attempt = recorder.current_attempt(level_id)
    return level_state(level, attempt, engine, recorder)


@router.post("/{level_id}/chat", responses=CHAT_ERRORS)
async def chat(
    level_id: int, body: ChatRequest, engine: GameEngineDep, recorder: RecorderDep
) -> ChatResponse:
    """Send a message to Gus. Starts a new attempt if none is under way."""
    attempt = current_or_new_attempt(level_id, engine, recorder)
    turn = await engine.send_message(attempt, body.message)
    return ChatResponse(
        reply=turn.reply,
        suspicion=turn.suspicion,
        caught=turn.caught,
        blocked_by_filter=turn.blocked_by_filter,
        messages_left=engine.messages_left(attempt),
    )


@router.post("/{level_id}/guess")
def guess(
    level_id: int, body: GuessRequest, engine: GameEngineDep, recorder: RecorderDep
) -> GuessResponse:
    """Try a vault code. A correct guess clears the level and ends the attempt."""
    attempt = current_or_new_attempt(level_id, engine, recorder)
    return GuessResponse(correct=engine.guess(attempt, body.guess))


@router.post("/{level_id}/reset")
def reset(level_id: int, engine: GameEngineDep, recorder: RecorderDep) -> LevelState:
    """Restart the level: end the current attempt, start a new one with a new code."""
    level = get_level(level_id)
    current = recorder.current_attempt(level_id)
    if current is not None:
        engine.abandon(current)
    return level_state(level, engine.start_attempt(level_id), engine, recorder)


# ---- Helpers ----


def current_or_new_attempt(
    level_id: int, engine: GameEngine, recorder: DatabaseRecorder
) -> Attempt:
    """The attempt under way at this level, or a fresh one."""
    get_level(level_id)  # Raises UnknownLevelError (404) before anything is stored.
    return recorder.current_attempt(level_id) or engine.start_attempt(level_id)


def summarise(level: Level, cleared: bool) -> LevelSummary:
    """A level as the API presents it."""
    return LevelSummary(
        id=level.id, name=level.name, description=level.description, cleared=cleared
    )


def level_state(
    level: Level, attempt: Attempt | None, engine: GameEngine, recorder: DatabaseRecorder
) -> LevelState:
    """A level and the conversation so far, as the player sees it."""
    summary = summarise(level, level.id in recorder.cleared_levels())
    if attempt is None:
        return LevelState(level=summary, attempt=None)
    return LevelState(
        level=summary,
        attempt=AttemptState(
            suspicion=attempt.suspicion,
            messages_left=engine.messages_left(attempt),
            messages=[to_message_out(m.role, m.content) for m in attempt.history],
        ),
    )


def to_message_out(role: str, content: str) -> MessageOut:
    """Convert a history entry. Gus's entries are stored as JSON, so unpack them."""
    if role == "assistant":
        guard = GuardReply.model_validate_json(content)
        return MessageOut(role="guard", text=guard.reply, suspicion=guard.suspicion)
    return MessageOut(role="player", text=content, suspicion=None)
