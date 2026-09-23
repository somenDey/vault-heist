"""Request and response models for the HTTP API."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for ``GET /api/health``."""

    status: Literal["ok"]
    model: str
