"""FastAPI application factory.

Run with: ``uvicorn app.main:create_app --factory`` (or ``just dev``).
"""

import structlog
from fastapi import FastAPI

from app.api.routes import health
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging


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

    app = FastAPI(title=settings.app_name)
    app.include_router(health.router, prefix="/api")

    structlog.get_logger().info("app_created", model=settings.llm_model)
    return app
