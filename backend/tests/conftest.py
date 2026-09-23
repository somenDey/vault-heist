"""Shared pytest fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    """Settings for tests: ignores the developer's .env, so tests behave the same everywhere."""
    return Settings(_env_file=None, llm_model="fake/test-model")


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    """An HTTP client for the app, wired to the test settings."""
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
