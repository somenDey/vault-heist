"""Turn exceptions into consistent JSON error responses.

Every error looks like ``{"error": {"code": "...", "message": "..."}}``. The
``code`` is stable, so the frontend can react to it; the ``message`` is for people.
"""

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api.dependencies import InvalidSessionError
from app.api.schemas import ErrorDetail, ErrorResponse
from app.game.engine import (
    AttemptOverError,
    DailyLimitReachedError,
    EmptyMessageError,
    GameError,
    MessageLimitReachedError,
    MessageTooLongError,
)
from app.game.levels import UnknownLevelError
from app.llm.client import LLMError

logger = structlog.get_logger()

# Game rule broken -> (HTTP status, error code)
GAME_ERRORS: dict[type[GameError], tuple[int, str]] = {
    EmptyMessageError: (status.HTTP_400_BAD_REQUEST, "empty_message"),
    MessageTooLongError: (status.HTTP_400_BAD_REQUEST, "message_too_long"),
    AttemptOverError: (status.HTTP_409_CONFLICT, "attempt_over"),
    MessageLimitReachedError: (status.HTTP_429_TOO_MANY_REQUESTS, "message_limit_reached"),
    DailyLimitReachedError: (status.HTTP_429_TOO_MANY_REQUESTS, "daily_limit_reached"),
}


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Build a response in the standard error shape."""
    body = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(status_code=status_code, content=body.model_dump())


async def handle_game_error(_: Request, exc: Exception) -> JSONResponse:
    """A player broke a game rule: tell them which, in words they understand."""
    status_code, code = next(
        (mapping for kind, mapping in GAME_ERRORS.items() if isinstance(exc, kind)),
        (status.HTTP_400_BAD_REQUEST, "game_error"),
    )
    return error_response(status_code, code, str(exc))


async def handle_unknown_level(_: Request, exc: Exception) -> JSONResponse:
    """The level in the URL doesn't exist."""
    return error_response(status.HTTP_404_NOT_FOUND, "unknown_level", str(exc))


async def handle_invalid_session(_: Request, exc: Exception) -> JSONResponse:
    """The session header is missing or unknown."""
    return error_response(status.HTTP_401_UNAUTHORIZED, "invalid_session", str(exc))


async def handle_llm_error(_: Request, exc: Exception) -> JSONResponse:
    """The model call failed. Log the details; don't show provider errors to players."""
    logger.error("llm_call_failed", error=str(exc))
    return error_response(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "guard_unavailable",
        "Gus isn't answering right now. Try again in a moment.",
    )


async def handle_validation_error(_: Request, exc: Exception) -> JSONResponse:
    """The request body or parameters didn't match the schema."""
    errors = exc.errors() if isinstance(exc, RequestValidationError) else []
    details = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in errors)
    return error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "invalid_request", details or "Invalid request."
    )


async def handle_http_error(_: Request, exc: Exception) -> JSONResponse:
    """Framework errors such as 404 for an unknown URL, in the same shape."""
    if not isinstance(exc, HTTPException):
        raise exc
    code = "not_found" if exc.status_code == status.HTTP_404_NOT_FOUND else "http_error"
    return error_response(exc.status_code, code, str(exc.detail))


def register_error_handlers(app: FastAPI) -> None:
    """Attach all the handlers above to the app."""
    app.add_exception_handler(GameError, handle_game_error)
    app.add_exception_handler(UnknownLevelError, handle_unknown_level)
    app.add_exception_handler(InvalidSessionError, handle_invalid_session)
    app.add_exception_handler(LLMError, handle_llm_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(HTTPException, handle_http_error)
