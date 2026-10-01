"""Database connections.

The rest of the app asks for a `sessionmaker` and opens short-lived sessions:
one per unit of work, committed or rolled back as a whole.
"""

from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


def create_db_engine(database_url: str) -> Engine:
    """Create the connection pool for ``database_url``.

    For SQLite, foreign keys are switched on for every connection. SQLite
    ignores them by default, which would let a message point at an attempt
    that doesn't exist.
    """
    engine = create_engine(database_url)
    if engine.dialect.name == "sqlite":
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a factory for database sessions bound to ``engine``."""
    return sessionmaker(engine, expire_on_commit=False)


def _enable_sqlite_foreign_keys(dbapi_connection: Any, _record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
