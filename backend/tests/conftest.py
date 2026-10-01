"""Shared pytest fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.db.models import Base
from app.db.session import create_db_engine, make_session_factory
from app.main import create_app


@pytest.fixture
def anyio_backend() -> str:
    """Run `@pytest.mark.anyio` tests on asyncio (the anyio plugin ships with FastAPI)."""
    return "asyncio"


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


@pytest.fixture
def session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    """A fresh, empty SQLite database file for one test, deleted afterwards by pytest."""
    engine = create_db_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(engine)
    yield make_session_factory(engine)
    engine.dispose()
