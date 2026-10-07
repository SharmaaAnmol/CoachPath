"""
SQLAlchemy Declarative Base and Shared Model Mixins.
Provides UUID primary keys, UTC timestamp auditing, and metadata registration.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique identifier (UUID v4)",
    )


class TimestampMixin:
    """Mixin adding created_at and updated_at UTC timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
        doc="Timestamp of last update (UTC)",
    )
