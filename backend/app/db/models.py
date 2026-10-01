"""Database tables, as SQLAlchemy 2.x typed models.

Every interaction is stored. In Phase 4 these rows become the attack dataset
that the guard's defences are evaluated against.

All timestamps are UTC.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    """The current time in UTC, without timezone info (SQLite doesn't store it)."""
    return datetime.now(UTC).replace(tzinfo=None)


def new_session_id() -> str:
    """A random, unguessable id for an anonymous player session."""
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Base class for all tables."""


class SessionRecord(Base):
    """An anonymous player session."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_session_id)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    attempts: Mapped[list["AttemptRecord"]] = relationship(back_populates="session")


class AttemptRecord(Base):
    """One try at one level, with one vault code."""

    __tablename__ = "level_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    level_id: Mapped[int] = mapped_column(Integer)
    secret_code: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    outcome: Mapped[str] = mapped_column(String(16), default="in_progress")

    session: Mapped[SessionRecord] = relationship(back_populates="attempts")
    messages: Mapped[list["MessageRecord"]] = relationship(
        back_populates="attempt", order_by="MessageRecord.id"
    )
    guesses: Mapped[list["GuessRecord"]] = relationship(back_populates="attempt")


class MessageRecord(Base):
    """One message in an attempt: the player's (``user``) or Gus's (``assistant``).

    Model, token, cost and latency columns are only filled in for Gus's replies.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("level_attempts.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    # What Gus really said, when the filter replaced it. The best data for Phase 4.
    unfiltered_content: Mapped[str | None] = mapped_column(Text, default=None)
    suspicion: Mapped[int | None] = mapped_column(Integer, default=None)
    blocked_by_filter: Mapped[bool] = mapped_column(Boolean, default=False)
    used_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    model: Mapped[str | None] = mapped_column(String(128), default=None)
    llm_calls: Mapped[int | None] = mapped_column(Integer, default=None)
    input_tokens: Mapped[int | None] = mapped_column(Integer, default=None)
    output_tokens: Mapped[int | None] = mapped_column(Integer, default=None)
    cost_usd: Mapped[float | None] = mapped_column(Float, default=None)
    latency_ms: Mapped[float | None] = mapped_column(Float, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    attempt: Mapped[AttemptRecord] = relationship(back_populates="messages")


class GuessRecord(Base):
    """One guess at the vault code."""

    __tablename__ = "guesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("level_attempts.id"), index=True)
    guess: Mapped[str] = mapped_column(String(64))
    correct: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    attempt: Mapped[AttemptRecord] = relationship(back_populates="guesses")
