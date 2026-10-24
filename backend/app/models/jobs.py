"""
Jobs and Semantic Matching Domain Models.
Implements JobSource, JobIngestionRun, Job, JobSkill, and JobMatch.
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
    TimestampMixin,
    UUIDMixin,
    VectorType,
    utc_now,
)

if TYPE_CHECKING:
    from app.models.applications import Application
    from app.models.career import CareerProfile, Role
    from app.models.resume import ResumeVersion
    from app.models.skills import Skill


class JobSource(Base, UUIDMixin, TimestampMixin):
    """
    Permitted job data source configuration (seed datasets, APIs, manual import).
    Tracks provider capabilities, rate limits, and ingestion state.
    """

    __tablename__ = "job_sources"
    __table_args__ = (
        CheckConstraint(
            "provider_type IN ('seed', 'manual', 'api', 'mock')",
            name="job_sources_provider_type_check",
        ),
        Index("job_sources_name_idx", "name", unique=True),
    )

    name: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        doc="Unique identifier for the job source ('seed', 'manual', 'arbeitnow', 'mock')",
    )
    provider_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Source modality ('seed', 'manual', 'api', 'mock')",
    )
    base_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="API root endpoint or documentation URL",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="Whether this ingestion source is currently enabled",
    )
    rate_limit_per_minute: Mapped[int] = mapped_column(
        Integer,
        default=30,
        server_default=sa.text("30"),
        nullable=False,
        doc="Allowed rate limit in calls/batches per minute",
    )
    last_ingested_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of most recent successful ingestion run",
    )
    config_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JsonB(),
        nullable=True,
        default=dict,
        doc="Provider-specific configuration or pagination offsets",
    )

    # Relationships
    ingestion_runs: Mapped[List[JobIngestionRun]] = relationship(
        "JobIngestionRun",
        back_populates="source",
        cascade="all, delete-orphan",
        order_by="desc(JobIngestionRun.started_at)",
    )


class JobIngestionRun(Base, UUIDMixin):
    """
    Audit log of an execution run of the job ingestion engine.
    Records fetch, insert, update, skip, and error metrics.
    """

    __tablename__ = "job_ingestion_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'partial')",
            name="job_ingestion_runs_status_check",
        ),
        Index("job_ingestion_runs_source_idx", "source_name", "started_at"),
    )

    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("job_sources.id", ondelete="SET NULL"),
        nullable=True,
        doc="Associated JobSource foreign key (if known)",
    )
    source_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Name of the ingestion source adapter",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        server_default=sa.text("'pending'"),
        nullable=False,
        doc="Run execution state ('pending', 'running', 'completed', 'failed', 'partial')",
    )
    items_fetched: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Raw job records fetched from source",
    )
    items_inserted: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="New jobs inserted into catalog",
    )
    items_updated: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Existing jobs refreshed or updated",
    )
    items_skipped: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Jobs skipped due to quality filters or duplicates",
    )
    items_errored: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Record processing failures",
    )
    error_log: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JsonB(),
        nullable=True,
        default=list,
        doc="Structured error details for failed items",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Run initiation timestamp (UTC)",
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Run completion timestamp (UTC)",
    )

    # Relationships
    source: Mapped[Optional[JobSource]] = relationship(
        "JobSource",
        back_populates="ingestion_runs",
    )


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
        CheckConstraint(
            "freshness_status IN ('active', 'needs_refresh', 'expired', 'closed')",
            name="jobs_freshness_status_check",
        ),
        Index("jobs_role_active_idx", "role_id", "is_active"),
        Index("jobs_company_title_loc_idx", "company_name", "title", "location"),
        Index("jobs_source_external_idx", "source", "external_id"),
        Index("jobs_freshness_idx", "freshness_status", "is_active"),
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
        doc="Ingestion source pipeline ('seed', 'manual', 'arbeitnow', 'mock')",
    )
    source_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        doc="Original external source job URL",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Job title",
    )
    normalized_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Normalized canonical title for aggregation",
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
    normalized_location: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Standardized city/region or Remote identifier",
    )
    remote_type: Mapped[str] = mapped_column(
        String(32),
        default="hybrid",
        server_default=sa.text("'hybrid'"),
        nullable=False,
        doc="Workplace flexibility ('remote', 'hybrid', 'onsite')",
    )
    employment_type: Mapped[Optional[str]] = mapped_column(
        String(32),
        default="full_time",
        server_default=sa.text("'full_time'"),
        nullable=True,
        doc="Employment modality ('full_time', 'contract', 'part_time', 'internship')",
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
    responsibilities: Mapped[Optional[List[str]]] = mapped_column(
        JsonB(),
        nullable=True,
        default=list,
        doc="Extracted key job responsibilities",
    )
    required_qualifications: Mapped[Optional[List[str]]] = mapped_column(
        JsonB(),
        nullable=True,
        default=list,
        doc="Extracted mandatory qualifications",
    )
    preferred_qualifications: Mapped[Optional[List[str]]] = mapped_column(
        JsonB(),
        nullable=True,
        default=list,
        doc="Extracted preferred / nice-to-have qualifications",
    )
    application_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Direct application or careers page URL",
    )
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        VectorType(1536),
        nullable=True,
        doc="Semantic embedding of job requirements (1536-dim)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="Active recruitment posting status",
    )
    freshness_status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        server_default=sa.text("'active'"),
        nullable=False,
        doc="Listing freshness lifecycle ('active', 'needs_refresh', 'expired', 'closed')",
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp posting was last confirmed alive and available",
    )
    raw_source_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JsonB(),
        nullable=True,
        doc="Unprocessed provider response payload for data lineage",
    )
    data_quality_score: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
        doc="Data completeness score from 0.00 to 1.00",
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
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(4, 2),
        default=decimal.Decimal("1.00"),
        server_default=sa.text("1.00"),
        nullable=True,
        doc="Confidence score of skill extraction (0.00 to 1.00)",
    )
    source_phrase: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Matched source text fragment from job description",
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
        Index("job_matches_is_stale_idx", "is_stale"),
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
    project_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        default=decimal.Decimal("0.0"),
        server_default=sa.text("0.0"),
        nullable=False,
        doc="Project relevance and hands-on artifact alignment (0.0 to 100.0)",
    )
    location_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        default=decimal.Decimal("0.0"),
        server_default=sa.text("0.0"),
        nullable=False,
        doc="Location and workplace flexibility alignment (0.0 to 100.0)",
    )
    preference_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        default=decimal.Decimal("0.0"),
        server_default=sa.text("0.0"),
        nullable=False,
        doc="Career and employment preference alignment (0.0 to 100.0)",
    )
    evidence_coverage: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        default=decimal.Decimal("0.0"),
        server_default=sa.text("0.0"),
        nullable=False,
        doc="Data completeness and evidence coverage score (0.0 to 100.0)",
    )
    vector_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        default=decimal.Decimal("0.0"),
        server_default=sa.text("0.0"),
        nullable=False,
        doc="Semantic vector cosine similarity factor (0.0 to 100.0)",
    )
    scoring_version: Mapped[str] = mapped_column(
        String(32),
        default="v1.0",
        server_default=sa.text("'v1.0'"),
        nullable=False,
        doc="Scoring algorithm version identifier",
    )
    is_stale: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=sa.text("FALSE"),
        nullable=False,
        doc="True if underlying profile, assessment, or job changed since last calculation",
    )
    matched_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Candidate verified skills present in job requirements",
    )
    matched_preferred_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Candidate verified/supported preferred skills present in job requirements",
    )
    missing_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Job mandatory/preferred skills not yet verified in candidate profile",
    )
    unknown_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Job skills for which candidate evidence is unrecorded or indeterminate",
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
