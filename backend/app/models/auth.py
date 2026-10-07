"""
Authentication and User Identity Domain Models.
Implements users, user_profiles, and user_sessions.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
import sqlalchemy as sa
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, Inet, TimestampMixin, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.applications import Application
    from app.models.assessments import AssessmentAttempt
    from app.models.audit import ActivityLog, AuditLog
    from app.models.career import CareerProfile
    from app.models.readiness import CareerReadinessScore
    from app.models.resume import Resume


class User(Base, UUIDMixin, TimestampMixin):
    """
    Master account identity, authentication credentials, security timestamps,
    and role permissions.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('candidate', 'admin')", name="users_role_check"),
        CheckConstraint(
            "status IN ('pending_verification', 'active', 'suspended', 'deleted')",
            name="users_status_check",
        ),
        Index("users_email_idx", "email", unique=True),
        Index("users_status_idx", "status"),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        doc="Normalized lowercase email address",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Argon2id encoded password hash",
    )
    role: Mapped[str] = mapped_column(
        String(32),
        default="candidate",
        nullable=False,
        doc="Authorization role ('candidate', 'admin')",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending_verification",
        nullable=False,
        doc="Account lifecycle status",
    )
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of email verification confirmation",
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of last successful authentication",
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp for soft-deletion",
    )

    # Relationships
    profile: Mapped[Optional[UserProfile]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    career_profile: Mapped[Optional[CareerProfile]] = relationship(
        "CareerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    sessions: Mapped[List[UserSession]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    resumes: Mapped[List[Resume]] = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    assessment_attempts: Mapped[List[AssessmentAttempt]] = relationship(
        "AssessmentAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    applications: Mapped[List[Application]] = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    readiness_scores: Mapped[List[CareerReadinessScore]] = relationship(
        "CareerReadinessScore",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    activity_logs: Mapped[List[ActivityLog]] = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[List[AuditLog]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserProfile(Base, UUIDMixin, TimestampMixin):
    """
    General candidate demographic, contact information, personal bio,
    and public social links.
    """

    __tablename__ = "user_profiles"
    __table_args__ = (
        Index("user_profiles_user_id_idx", "user_id", unique=True),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Owning user reference",
    )
    full_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Candidate full legal or professional name",
    )
    headline: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Professional headline or candidate positioning statement",
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Candidate primary geographic location",
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        doc="Candidate phone contact number",
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Verified LinkedIn public profile link",
    )
    github_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Verified GitHub profile link",
    )
    portfolio_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Personal portfolio or website link",
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Personal summary bio",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="profile")


class UserSession(Base, UUIDMixin):
    """
    Persistent authentication refresh tokens, device fingerprints,
    and revocation ledger.
    """

    __tablename__ = "user_sessions"
    __table_args__ = (
        Index("user_sessions_token_hash_idx", "refresh_token_hash", unique=True),
        Index("user_sessions_user_id_idx", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning user reference",
    )
    refresh_token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        doc="Cryptographic SHA-256 hash of refresh token",
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Client browser user agent string",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        Inet(),
        nullable=True,
        doc="Client IP address",
    )
    is_revoked: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        nullable=False,
        doc="Explicit revocation indicator",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp when refresh token expires",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of session creation (UTC)",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="sessions")
