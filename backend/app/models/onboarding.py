"""
Onboarding Domain Models for CoachPath.
Implements OnboardingSession and OnboardingTurn for persistent,
resumable, AI-powered career discovery interviews.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JsonB, TimestampMixin, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.auth import User


class OnboardingSession(Base, UUIDMixin, TimestampMixin):
    """
    Persistent, resumable AI career onboarding interview session.
    Strictly 1:1 per candidate user account.
    """

    __tablename__ = "onboarding_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'awaiting_confirmation', 'completed')",
            name="onboarding_status_check",
        ),
        Index("onboarding_sessions_user_id_idx", "user_id", unique=True),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Owning candidate user account reference",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="in_progress",
        server_default="in_progress",
        nullable=False,
        doc="Lifecycle state ('not_started', 'in_progress', 'awaiting_confirmation', 'completed')",
    )
    current_question: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="The active question presented to the candidate awaiting response",
    )
    current_question_category: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        doc="Category taxonomy of the active question",
    )
    turn_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        doc="Total number of answered conversation turns",
    )
    collected_facts: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=dict,
        server_default=sa.text("'{}'"),
        nullable=True,
        doc="Accumulated facts extracted by AI from candidate answers",
    )
    areas_covered: Mapped[Optional[List[str]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=True,
        doc="List of question domain categories covered so far",
    )
    ai_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JsonB(),
        nullable=True,
        doc="AI-synthesized career summary awaiting user review and confirmation",
    )
    summary_generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when AI generated the summary",
    )
    is_summary_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=sa.text("FALSE"),
        nullable=False,
        doc="True once candidate explicitly approves the career summary",
    )
    summary_confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when candidate approved summary",
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of most recent candidate interaction",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when onboarding was fully finalized and applied to profile",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="onboarding_session")
    turns: Mapped[List[OnboardingTurn]] = relationship(
        "OnboardingTurn",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="OnboardingTurn.turn_number",
    )


class OnboardingTurn(Base, UUIDMixin):
    """
    A single question-and-answer exchange within an onboarding session.
    Preserves audit provenance of the conversation.
    """

    __tablename__ = "onboarding_turns"
    __table_args__ = (
        Index("onboarding_turns_session_idx", "session_id"),
        Index("onboarding_turns_session_turn_idx", "session_id", "turn_number", unique=True),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("onboarding_sessions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent onboarding session ID",
    )
    turn_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Monotonically increasing turn sequence index (1-indexed)",
    )
    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Question text generated by AI or initial prompt",
    )
    question_category: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Category taxonomy identifier for this question",
    )
    user_response: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Candidate's raw textual response (None if question pending)",
    )
    extracted_facts: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JsonB(),
        nullable=True,
        doc="Facts extracted by AI from this specific response",
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when candidate submitted their response",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp when question turn was issued",
    )

    # Relationships
    session: Mapped[OnboardingSession] = relationship("OnboardingSession", back_populates="turns")
