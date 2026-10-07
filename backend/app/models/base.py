"""
SQLAlchemy Declarative Base and Shared Model Mixins.
Provides UUID primary keys, UTC timestamp auditing, and metadata registration.
"""

import uuid
from datetime import datetime, timezone
from typing import Any
import sqlalchemy as sa
from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector


def utc_now() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """
    Base class for all CoachPath SQLAlchemy models.
    Enables automatic metadata detection for Alembic migrations.
    """
    pass


class UUIDMixin:
    """Mixin adding a standard UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier (UUID v4)",
    )


class TimestampMixin:
    """Mixin adding created_at and updated_at UTC timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=utc_now,
        nullable=False,
        doc="Timestamp of last update (UTC)",
    )


def StringArray(length: int = 64) -> Any:
    """PostgreSQL VARCHAR(length)[] array with SQLite JSON fallback."""
    return ARRAY(sa.String(length)).with_variant(sa.JSON(), "sqlite")


def TextArray() -> Any:
    """PostgreSQL TEXT[] array with SQLite JSON fallback."""
    return ARRAY(sa.Text()).with_variant(sa.JSON(), "sqlite")


def JsonB() -> Any:
    """PostgreSQL JSONB with SQLite JSON fallback."""
    return JSONB().with_variant(sa.JSON(), "sqlite")


def Inet() -> Any:
    """PostgreSQL INET with SQLite VARCHAR(45) fallback."""
    return INET().with_variant(sa.String(45), "sqlite")


def VectorType(dim: int = 1536) -> Any:
    """PostgreSQL vector(dim) with SQLite JSON fallback."""
    return Vector(dim).with_variant(sa.JSON(), "sqlite")
