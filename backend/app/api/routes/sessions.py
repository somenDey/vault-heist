"""Player sessions."""

from fastapi import APIRouter, status

from app.api.dependencies import SessionFactoryDep
from app.api.schemas import SessionResponse
from app.db.repositories import create_session

router = APIRouter(tags=["sessions"])


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def start_session(session_factory: SessionFactoryDep) -> SessionResponse:
    """Start an anonymous player session. Send the returned id as ``X-Session-ID``."""
    with session_factory.begin() as db:
        return SessionResponse(session_id=create_session(db).id)
