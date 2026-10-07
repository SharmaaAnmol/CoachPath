"""
Assessment and Diagnostic Evidence Domain Models.
Implements Assessment, AssessmentQuestion, AssessmentAttempt, AssessmentAnswer, and AssessmentResult.
"""

from __future__ import annotations

import decimal
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JsonB, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.skills import Skill


class Assessment(Base, UUIDMixin):
    """
    Curated diagnostic examinations calibrating specific skills.
    """

    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint("time_limit_minutes > 0", name="assessments_time_limit_check"),
        CheckConstraint(
            "passing_threshold >= 0.0 AND passing_threshold <= 100.0",
            name="assessments_passing_threshold_check",
        ),
        Index("assessments_skill_id_idx", "skill_id"),
    )

    skill_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Evaluated skill reference",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Assessment examination title",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Diagnostic rubric and instructions",
    )
    time_limit_minutes: Mapped[int] = mapped_column(
        Integer,
        default=15,
        server_default=sa.text("15"),
        nullable=False,
        doc="Maximum examination duration in minutes",
    )
    passing_threshold: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        default=decimal.Decimal("75.0"),
        server_default=sa.text("75.0"),
        nullable=False,
        doc="Minimum score percentage required to verify skill",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="Availability flag",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    # Relationships
    skill: Mapped[Skill] = relationship("Skill", back_populates="assessments")
    questions: Mapped[List[AssessmentQuestion]] = relationship(
        "AssessmentQuestion",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    attempts: Mapped[List[AssessmentAttempt]] = relationship(
        "AssessmentAttempt",
        back_populates="assessment",
    )


class AssessmentQuestion(Base, UUIDMixin):
    """
    Scenario-based conceptual or practical coding questions belonging to an assessment.
    """

    __tablename__ = "assessment_questions"
    __table_args__ = (
        CheckConstraint(
            "correct_option_index >= 0 AND correct_option_index <= 3",
            name="assessment_questions_option_idx_check",
        ),
        CheckConstraint(
            "difficulty IN ('basic', 'intermediate', 'advanced')",
            name="assessment_questions_difficulty_check",
        ),
        Index("assessment_questions_test_id_idx", "assessment_id"),
    )

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent assessment reference",
    )
    prompt_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Scenario description or question prompt",
    )
    code_snippet: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Code sample or configuration file context",
    )
    options: Mapped[List[str]] = mapped_column(
        JsonB(),
        nullable=False,
        doc="Array of candidate choices (JSON list)",
    )
    correct_option_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Zero-based index of the correct response choice",
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Diagnostic pedagogical feedback explaining why the answer is correct",
    )
    difficulty: Mapped[str] = mapped_column(
        String(32),
        default="intermediate",
        server_default=sa.text("'intermediate'"),
        nullable=False,
        doc="Difficulty rating ('basic', 'intermediate', 'advanced')",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    # Relationships
    assessment: Mapped[Assessment] = relationship(
        "Assessment",
        back_populates="questions",
    )
    answers: Mapped[List[AssessmentAnswer]] = relationship(
        "AssessmentAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class AssessmentAttempt(Base, UUIDMixin):
    """
    Candidate test execution instances, timing, scores, and pass/fail states.
    """

    __tablename__ = "assessment_attempts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'timed_out', 'abandoned')",
            name="assessment_attempts_status_check",
        ),
        CheckConstraint(
            "score_percentage IS NULL OR (score_percentage >= 0.0 AND score_percentage <= 100.0)",
            name="assessment_attempts_score_check",
        ),
        Index("assessment_attempts_user_id_idx", "user_id"),
        Index("assessment_attempts_assessment_id_idx", "assessment_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Candidate user reference",
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("assessments.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Assessment examination reference",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="in_progress",
        server_default=sa.text("'in_progress'"),
        nullable=False,
        doc="Execution status ('in_progress', 'completed', 'timed_out', 'abandoned')",
    )
    score_percentage: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
        doc="Calibrated diagnostic score achieved (0.0 to 100.0)",
    )
    passed: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        doc="True if score achieved >= passing threshold",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp test commenced (UTC)",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp test was finalized (UTC)",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="assessment_attempts")
    assessment: Mapped[Assessment] = relationship(
        "Assessment",
        back_populates="attempts",
    )
    answers: Mapped[List[AssessmentAnswer]] = relationship(
        "AssessmentAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )
    result: Mapped[Optional[AssessmentResult]] = relationship(
        "AssessmentResult",
        back_populates="attempt",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AssessmentAnswer(Base, UUIDMixin):
    """
    Granular candidate responses per question within an attempt.
    """

    __tablename__ = "assessment_answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_assessment_answers_attempt_q"),
        Index("assessment_answers_attempt_q_idx", "attempt_id", "question_id", unique=True),
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("assessment_attempts.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent assessment attempt reference",
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("assessment_questions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Answered question reference",
    )
    selected_option_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Candidate selected option index",
    )
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        doc="Evaluation verdict",
    )
    response_time_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Time elapsed in seconds before submitting answer",
    )

    # Relationships
    attempt: Mapped[AssessmentAttempt] = relationship(
        "AssessmentAttempt",
        back_populates="answers",
    )
    question: Mapped[AssessmentQuestion] = relationship(
        "AssessmentQuestion",
        back_populates="answers",
    )


class AssessmentResult(Base, UUIDMixin):
    """
    Diagnostic feedback summary and recommended remedial actions resulting from an attempt.
    """

    __tablename__ = "assessment_results"
    __table_args__ = (
        Index("assessment_results_attempt_idx", "attempt_id", unique=True),
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("assessment_attempts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Evaluated attempt reference",
    )
    strengths_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed breakdown of demonstrated strengths",
    )
    weaknesses_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed breakdown of concept deficiencies and missed mechanics",
    )
    remedial_milestones: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="Array of recommended learning roadmap injection tasks",
    )
    confidence_lift: Mapped[decimal.Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        doc="Score improvement delta applied to candidate user_skills",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    # Relationships
    attempt: Mapped[AssessmentAttempt] = relationship(
        "AssessmentAttempt",
        back_populates="result",
    )
