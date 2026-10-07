"""
Audit and Activity Logging Domain Models.
Implements ActivityLog and AuditLog for security, GDPR tracking, and candidate achievement history.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict
import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JsonB, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.auth import User


class ActivityLog(Base, UUIDMixin):
    """
    User-visible chronological timeline of achievements, assessments, and pipeline events.
    """

    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("activity_logs_user_created_idx", "user_id", "created_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning candidate user reference",
    )
    activity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Categorical activity event code (e.g., 'ASSESSMENT_PASSED', 'MILESTONE_COMPLETED')",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human-readable event headline",
    )
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
        JsonB(),
        default=dict,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Polymorphic event payload details",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp event occurred (UTC)",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="activity_logs")


class AuditLog(Base, UUIDMixin):
    """
    Security, legal, and human-approval immutable audit trail.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("audit_logs_user_action_idx", "user_id", "action_type"),
        Index("audit_logs_created_at_idx", "created_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Actor candidate user reference",
    )
    action_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Consequential action code (e.g., 'PROFILE_CONFIRMED', 'RESUME_TAILOR_APPROVED')",
    )
    target_entity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Target entity domain type (e.g., 'resume_version', 'job_application')",
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        nullable=False,
        doc="Target entity record primary key",
    )
    diff_payload: Mapped[Dict[str, Any]] = mapped_column(
        JsonB(),
        nullable=False,
        doc="Structured before/after diff snapshot",
    )
    human_approved: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="True if action had explicit human consent or approval",
    )
    client_ip_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Anonymized SHA-256 hash of client IP address",
    )
    user_agent: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Client user agent string",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp audit entry was committed (UTC)",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="audit_logs")
