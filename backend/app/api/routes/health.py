"""Health check endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas import HealthResponse
from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Report that the service is up and which model it is configured to use."""
    return HealthResponse(status="ok", model=settings.llm_model)
