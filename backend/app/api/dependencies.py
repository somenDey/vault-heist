"""FastAPI dependencies: how each request gets its settings, database, model and engine.

Routes declare what they need (e.g. ``engine: GameEngineDep``) and FastAPI builds it.
Tests swap pieces with ``app.dependency_overrides``, e.g. a fake LLM client.
"""

from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.db.repositories import DatabaseRecorder, get_session
from app.game.engine import GameEngine
from app.llm.client import LLMClient
from app.llm.litellm_client import LiteLLMClient

SESSION_HEADER = "X-Session-ID"


class InvalidSessionError(Exception):
    """The request has no session id, or one the server doesn't know."""


SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_session_factory(request: Request) -> sessionmaker[Session]:
    """The database session factory created with the app."""
    factory: sessionmaker[Session] = request.app.state.session_factory
    return factory


SessionFactoryDep = Annotated[sessionmaker[Session], Depends(get_session_factory)]


def get_llm_client(request: Request, settings: SettingsDep) -> LLMClient:
    """The model client, created on first use and then shared by all requests."""
    client: LLMClient | None = getattr(request.app.state, "llm_client", None)
    if client is None:
        client = LiteLLMClient.from_settings(settings)
        request.app.state.llm_client = client
    return client


def get_player_session_id(
    session_factory: SessionFactoryDep,
    session_id: Annotated[str | None, Header(alias=SESSION_HEADER)] = None,
) -> str:
    """The caller's player session, from the ``X-Session-ID`` header.

    Raises:
        InvalidSessionError: If the header is missing or the session doesn't exist.
    """
    if not session_id:
        raise InvalidSessionError(f"Missing {SESSION_HEADER} header. Create a session first.")
    with session_factory() as db:
        if get_session(db, session_id) is None:
            raise InvalidSessionError("Unknown session. Create a new one.")
    return session_id


PlayerSessionDep = Annotated[str, Depends(get_player_session_id)]


def get_recorder(
    session_factory: SessionFactoryDep, session_id: PlayerSessionDep
) -> DatabaseRecorder:
    """Storage for this player's session."""
    return DatabaseRecorder(session_factory, session_id)


RecorderDep = Annotated[DatabaseRecorder, Depends(get_recorder)]


def get_game_engine(
    settings: SettingsDep,
    client: Annotated[LLMClient, Depends(get_llm_client)],
    recorder: RecorderDep,
) -> GameEngine:
    """A game engine that records everything for this player's session."""
    return GameEngine.from_settings(settings, client, recorder)


GameEngineDep = Annotated[GameEngine, Depends(get_game_engine)]
