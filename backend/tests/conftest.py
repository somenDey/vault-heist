"""Shared pytest fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_llm_client
from app.core.config import Settings, get_settings
from app.db.models import Base
from app.db.session import create_db_engine, make_session_factory
from app.llm.fake_client import FakeLLMClient
from app.main import create_app


@pytest.fixture
def anyio_backend() -> str:
    """Run `@pytest.mark.anyio` tests on asyncio (the anyio plugin ships with FastAPI)."""
    return "asyncio"


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Settings for tests.

    Ignores the developer's .env, so tests behave the same everywhere, and points
    at a fresh SQLite file that pytest deletes afterwards.
    """
    return Settings(
        _env_file=None,
        llm_model="fake/test-model",
        database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        max_message_chars=100,
        max_messages_per_attempt=3,
    )


@pytest.fixture
def session_factory(settings: Settings) -> Iterator[sessionmaker[Session]]:
    """The test database, with all tables created."""
    engine = create_db_engine(settings.database_url)
    Base.metadata.create_all(engine)
    yield make_session_factory(engine)
    engine.dispose()


@pytest.fixture
def fake_llm() -> FakeLLMClient:
    """The model the API uses in tests. Add replies with ``fake_llm.replies.append(...)``."""
    return FakeLLMClient(replies=[])


@pytest.fixture
def client(
    settings: Settings, session_factory: sessionmaker[Session], fake_llm: FakeLLMClient
) -> Iterator[TestClient]:
    """An HTTP client for the app, wired to the test settings, database and fake model."""
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_llm_client] = lambda: fake_llm
    with TestClient(app) as test_client:
        yield test_client
