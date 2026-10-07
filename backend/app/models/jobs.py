"""
Jobs and Semantic Matching Domain Models.
Implements Job, JobSkill, and JobMatch.
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

from app.models.base import (
    Base,
    JsonB,
    StringArray,
    UUIDMixin,
    VectorType,
    utc_now,
)

if TYPE_CHECKING:
    from app.models.applications import Application
    from app.models.career import CareerProfile, Role
    from app.models.resume import ResumeVersion
    from app.models.skills import Skill


class Job(Base, UUIDMixin):
    """
    Curated job postings ingested from permitted sources and seed datasets.
    """

    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint(
            "remote_type IN ('remote', 'hybrid', 'onsite')",
            name="jobs_remote_type_check",
        ),
        CheckConstraint(
            "experience_level IN ('internship', 'entry_level', 'junior', 'mid')",
            name="jobs_exp_level_check",
        ),
        Index("jobs_role_active_idx", "role_id", "is_active"),
        Index("jobs_company_title_loc_idx", "company_name", "title", "location"),
    )

    external_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Deduplication identifier from external job feed",
    )
    source: Mapped[str] = mapped_column(
        String(64),
        default="seed",
        server_default=sa.text("'seed'"),
        nullable=False,
        doc="Ingestion source pipeline ('seed', 'official_api', 'partner')",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Job title",
    )
    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Employer company or organization",
    )
    location: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Geographic location or primary metro market",
    )
    remote_type: Mapped[str] = mapped_column(
        String(32),
        default="hybrid",
        server_default=sa.text("'hybrid'"),
        nullable=False,
        doc="Workplace flexibility ('remote', 'hybrid', 'onsite')",
    )
    role_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Canonical benchmark role reference",
    )
    experience_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Seniority level ('internship', 'entry_level', 'junior', 'mid')",
    )
    min_salary: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Annualized minimum salary",
    )
    max_salary: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Annualized maximum salary",
    )
    currency: Mapped[str] = mapped_column(
        String(8),
        default="USD",
        server_default=sa.text("'USD'"),
        nullable=False,
        doc="Three-letter ISO currency code",
    )
    description_markdown: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Full job description in Markdown format",
    )
    application_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Direct application or careers page URL",
    )
    embedding: Mapped[List[float]] = mapped_column(
        VectorType(1536),
        nullable=False,
        doc="Semantic embedding of job requirements (1536-dim)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="Active recruitment posting status",
    )
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Posting publication timestamp (UTC)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Database ingestion timestamp (UTC)",
    )

    # Relationships
    role: Mapped[Role] = relationship("Role", back_populates="jobs")
    skills: Mapped[List[JobSkill]] = relationship(
        "JobSkill",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    matches: Mapped[List[JobMatch]] = relationship(
        "JobMatch",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    applications: Mapped[List[Application]] = relationship(
        "Application",
        back_populates="job",
    )
    tailored_resume_versions: Mapped[List[ResumeVersion]] = relationship(
        "ResumeVersion",
        back_populates="target_job",
    )


class JobSkill(Base, UUIDMixin):
    """
    Standardized skills tagged in a job posting.
    """

    __tablename__ = "job_skills"
    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="uq_job_skills_job_skill"),
        Index("job_skills_job_skill_idx", "job_id", "skill_id", unique=True),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent job posting reference",
    )
    skill_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        doc="Tagged canonical skill reference",
    )
    is_mandatory: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="True if requirement is mandatory/hard qualification",
    )

    # Relationships
    job: Mapped[Job] = relationship("Job", back_populates="skills")
    skill: Mapped[Skill] = relationship("Skill", back_populates="job_skills")


class JobMatch(Base, UUIDMixin):
    """
    Multi-factor match computations linking candidate career profiles to specific jobs.
    """

    __tablename__ = "job_matches"
    __table_args__ = (
        CheckConstraint(
            "overall_score >= 0.0 AND overall_score <= 100.0",
            name="job_matches_score_check",
        ),
        UniqueConstraint("career_profile_id", "job_id", name="uq_job_matches_profile_job"),
        Index("job_matches_profile_score_idx", "career_profile_id", "overall_score"),
        Index("job_matches_profile_job_idx", "career_profile_id", "job_id", unique=True),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Evaluated career profile reference",
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        doc="Target job posting reference",
    )
    overall_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Composite weighted match score (0.0 to 100.0)",
    )
    skill_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Weighted skill overlap factor (0.0 to 100.0)",
    )
    experience_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Experience and seniority alignment factor (0.0 to 100.0)",
    )
    vector_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Semantic vector cosine similarity factor (0.0 to 100.0)",
    )
    matched_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Candidate verified skills present in job requirements",
    )
    missing_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Job mandatory/preferred skills not yet verified in candidate profile",
    )
    explanation_json: Mapped[Dict[str, Any]] = mapped_column(
        JsonB(),
        nullable=False,
        doc="Structured explainability breakdown {score_breakdown, strengths, gaps, hiring_rationale}",
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp match score was computed (UTC)",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="job_matches",
    )
    job: Mapped[Job] = relationship("Job", back_populates="matches")
