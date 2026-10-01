"""FastAPI application factory.

Run with: ``uvicorn app.main:create_app --factory`` (or ``just dev``).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import SESSION_HEADER
from app.api.errors import register_error_handlers
from app.api.routes import health, levels, sessions
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.session import create_db_engine, make_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application.

    Args:
        settings: Settings to use. Defaults to the ones loaded from the
            environment; tests pass their own.

    Returns:
        The configured application, ready to serve.
    """
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.log_format)
    db_engine = create_db_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        db_engine.dispose()  # Close database connections on shutdown.

    app = FastAPI(
        title=settings.app_name,
        summary="Talk your way into the vault. An AI security game.",
        lifespan=lifespan,
    )
    app.state.session_factory = make_session_factory(db_engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", SESSION_HEADER],
    )
    register_error_handlers(app)
    for module in (health, sessions, levels):
        app.include_router(module.router, prefix="/api")

    structlog.get_logger().info("app_created", model=settings.llm_model)
    return app
