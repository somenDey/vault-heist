"""Structured logging setup using structlog."""

import logging

import structlog
from structlog.typing import Processor

from app.core.config import LogFormat, LogLevel


def configure_logging(level: LogLevel, log_format: LogFormat) -> None:
    """Configure structlog for the whole application.

    Args:
        level: The minimum level to emit, e.g. ``"INFO"``.
        log_format: ``"console"`` for readable, coloured lines while developing;
            ``"json"`` for one JSON object per line, for machines to parse.
    """
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]
    if log_format == "json":
        processors += [structlog.processors.format_exc_info, structlog.processors.JSONRenderer()]
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelNamesMapping()[level]),
        logger_factory=structlog.PrintLoggerFactory(),
    )
