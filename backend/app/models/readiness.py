"""
Career Readiness Score Domain Model.
Implements CareerReadinessScore tracking historical index snapshots and factor pillars.
"""

from __future__ import annotations

import decimal
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Dict, List
import sqlalchemy as sa
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JsonB, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.auth import User


class CareerReadinessScore(Base, UUIDMixin):
    """
    Daily/historical snapshots of overall readiness index and constituent factor pillars.
    """

    __tablename__ = "career_readiness_scores"
    __table_args__ = (
        CheckConstraint(
            "overall_score >= 0.0 AND overall_score <= 100.0",
            name="readiness_overall_score_check",
        ),
        UniqueConstraint("user_id", "recorded_date", name="uq_readiness_user_date"),
        Index("readiness_user_date_idx", "user_id", "recorded_date", unique=True),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Candidate user reference",
    )
    overall_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Composite readiness score (0.0 to 100.0)",
    )
    profile_completeness_factor: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Profile completeness factor (0.0 to 100.0)",
    )
    skill_proficiency_factor: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Verified skill proficiency factor (0.0 to 100.0)",
    )
    roadmap_progress_factor: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Roadmap milestone completion factor (0.0 to 100.0)",
    )
    application_velocity_factor: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Application and pipeline velocity factor (0.0 to 100.0)",
    )
    top_next_actions: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="Array of prioritized recommended next actions",
    )
    recorded_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        server_default=sa.text("CURRENT_DATE"),
        nullable=False,
        doc="Snapshot calendar date",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp snapshot was recorded (UTC)",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="readiness_scores")
