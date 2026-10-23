"""
Skills Taxonomy and Evidence Calibration Domain Models.
Implements Skill, RoleRequirement, UserSkill, and SkillGap.
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
    from app.models.applications import InterviewQuestion
    from app.models.assessments import Assessment
    from app.models.career import CareerProfile, Role
    from app.models.jobs import JobSkill
    from app.models.roadmap import RoadmapTask


class Skill(Base):
    """
    Standardized master repository of technical skills, frameworks, databases, and concepts.
    """

    __tablename__ = "skills"
    __table_args__ = (
        CheckConstraint(
            "category IN ('language', 'framework', 'database', 'tool', 'cloud', 'architecture', 'concept')",
            name="skills_category_check",
        ),
        Index("skills_name_idx", "name", unique=True),
        Index("skills_category_idx", "category"),
    )

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        doc="Canonical skill identifier (e.g., 'postgresql', 'fastapi')",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        doc="Canonical display name of the skill",
    )
    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Ontological category",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Technical scope and definition of competency",
    )
    synonyms: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Common aliases, abbreviations, and synonyms (e.g., ['postgres', 'pgsql'])",
    )
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        VectorType(1536),
        nullable=True,
        doc="Semantic vector embedding (1536-dim)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    # Relationships
    role_requirements: Mapped[List[RoleRequirement]] = relationship(
        "RoleRequirement",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    user_skills: Mapped[List[UserSkill]] = relationship(
        "UserSkill",
        back_populates="skill",
    )
    job_skills: Mapped[List[JobSkill]] = relationship(
        "JobSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    assessments: Mapped[List[Assessment]] = relationship(
        "Assessment",
        back_populates="skill",
    )
    roadmap_tasks: Mapped[List[RoadmapTask]] = relationship(
        "RoadmapTask",
        back_populates="skill",
    )
    interview_questions: Mapped[List[InterviewQuestion]] = relationship(
        "InterviewQuestion",
        back_populates="skill",
    )


class RoleRequirement(Base, UUIDMixin):
    """
    Benchmark requirements defining what skills each target role requires.
    """

    __tablename__ = "role_requirements"
    __table_args__ = (
        CheckConstraint(
            "importance IN ('mandatory', 'preferred', 'bonus')",
            name="role_req_importance_check",
        ),
        CheckConstraint(
            "min_proficiency IN ('basic', 'demonstrated', 'proficient', 'mastered')",
            name="role_req_min_proficiency_check",
        ),
        CheckConstraint("weight > 0.0", name="role_req_weight_check"),
        UniqueConstraint("role_id", "skill_id", name="uq_role_requirements_role_skill"),
        Index("role_req_role_skill_idx", "role_id", "skill_id", unique=True),
    )

    role_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Target benchmark role reference",
    )
    skill_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        doc="Benchmark skill reference",
    )
    importance: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Requirement tier ('mandatory', 'preferred', 'bonus')",
    )
    min_proficiency: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Minimum required proficiency ('basic', 'demonstrated', 'proficient', 'mastered')",
    )
    required_level: Mapped[int] = mapped_column(
        Integer,
        default=3,
        server_default=sa.text("3"),
        nullable=False,
        doc="Numeric proficiency level required on 1-4 scale (1: Foundational, 2: Developing, 3: Proficient, 4: Advanced)",
    )
    rationale: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Explanation of why this skill is required for the target role",
    )
    weight: Mapped[decimal.Decimal] = mapped_column(
        Numeric(3, 2),
        default=decimal.Decimal("1.00"),
        server_default=sa.text("1.0"),
        nullable=False,
        doc="Weight multiplier for readiness and matching calculations",
    )

    # Relationships
    role: Mapped[Role] = relationship("Role", back_populates="requirements")
    skill: Mapped[Skill] = relationship("Skill", back_populates="role_requirements")


class UserSkill(Base, UUIDMixin, TimestampMixin):
    """
    Dynamic link between a career profile and a skill, storing calibrated confidence
    and provenance evidence.
    """

    __tablename__ = "user_skills"
    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="user_skills_confidence_check",
        ),
        CheckConstraint(
            "proficiency_tier IN ('unverified', 'demonstrated', 'proficient', 'mastered')",
            name="user_skills_tier_check",
        ),
        CheckConstraint(
            "primary_source IN ('self_reported', 'extracted', 'assessment', 'project_evidence')",
            name="user_skills_source_check",
        ),
        UniqueConstraint("career_profile_id", "skill_id", name="uq_user_skills_profile_skill"),
        Index("user_skills_profile_skill_idx", "career_profile_id", "skill_id", unique=True),
        Index("user_skills_confidence_idx", "confidence_score"),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning career profile reference",
    )
    skill_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Calibrated canonical skill reference",
    )
    confidence_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(3, 2),
        default=decimal.Decimal("0.20"),
        server_default=sa.text("0.20"),
        nullable=False,
        doc="Calibrated confidence score between 0.00 and 1.00",
    )
    proficiency_tier: Mapped[str] = mapped_column(
        String(32),
        default="unverified",
        nullable=False,
        doc="Proficiency classification",
    )
    primary_source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Primary evidence genesis ('self_reported', 'extracted', 'assessment', 'project_evidence')",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="True if validated via objective diagnostic assessment or project",
    )
    last_evidence_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp when evidence was last refreshed or confirmed",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="user_skills",
    )
    skill: Mapped[Skill] = relationship("Skill", back_populates="user_skills")


class SkillGap(Base, UUIDMixin):
    """
    Point-in-time cached gap analysis snapshots comparing candidate skills
    against target role benchmarks.
    """

    __tablename__ = "skill_gaps"
    __table_args__ = (
        CheckConstraint(
            "readiness_percentage >= 0.0 AND readiness_percentage <= 100.0",
            name="skill_gaps_percentage_check",
        ),
        UniqueConstraint("career_profile_id", "role_id", name="uq_skill_gaps_profile_role"),
        Index("skill_gaps_profile_role_idx", "career_profile_id", "role_id", unique=True),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning career profile reference",
    )
    role_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Benchmarked role reference",
    )
    readiness_percentage: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Overall benchmark alignment percentage (0.0 to 100.0)",
    )
    met_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Skills meeting or exceeding role benchmark",
    )
    developing_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Skills present but below benchmark confidence/proficiency threshold",
    )
    missing_skills: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Mandatory or preferred skills not currently present in profile",
    )
    explanation_narrative: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Deterministic diagnostic summary explaining readiness and actionable steps",
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp when gap calculation was committed",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="skill_gaps",
    )
    role: Mapped[Role] = relationship("Role", back_populates="skill_gaps")


class SkillGapAnalysis(Base, UUIDMixin):
    """
    Comprehensive, immutable snapshot of skill gap analysis comparing candidate
    evidence against benchmark role requirements.
    Supports historical trending with an is_current active flag.
    """

    __tablename__ = "skill_gap_analyses"
    __table_args__ = (
        Index("skill_gap_analyses_profile_idx", "career_profile_id"),
        Index("skill_gap_analyses_profile_current_idx", "career_profile_id", "is_current"),
        Index("skill_gap_analyses_role_idx", "role_id"),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning career profile reference",
    )
    role_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Benchmarked role reference",
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="True if this is the active/latest gap analysis snapshot for the profile",
    )
    role_version: Mapped[str] = mapped_column(
        String(32),
        default="1.0.0",
        server_default="1.0.0",
        nullable=False,
        doc="Version of role benchmark used for analysis",
    )
    algorithm_version: Mapped[str] = mapped_column(
        String(32),
        default="1.0.0",
        server_default="1.0.0",
        nullable=False,
        doc="Version of scoring algorithm used",
    )
    role_alignment_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Overall benchmark role alignment score (0.0 to 100.0)",
    )
    evidence_coverage_score: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 1),
        nullable=False,
        doc="Evidence coverage score across required role competencies (0.0 to 100.0)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="completed",
        server_default="completed",
        nullable=False,
        doc="Analysis status ('completed', 'recalculating')",
    )
    strongest_skills: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="List of skills where user meets or exceeds benchmark requirements",
    )
    developing_skills: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="List of skills where user has demonstrated some competence but is below benchmark",
    )
    skill_gaps: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="List of confirmed skill gaps where user falls short of requirement",
    )
    missing_skills: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="List of mandatory or preferred skills with zero profile or assessment evidence",
    )
    unassessed_skills: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="List of claimed skills that lack objective diagnostic or project verification",
    )
    skill_details: Mapped[Dict[str, Any]] = mapped_column(
        JsonB(),
        default=dict,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Detailed per-skill breakdown dictionary indexed by skill_id",
    )
    prioritized_gaps: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="Deterministically ranked gaps with suggested next actions",
    )
    recommended_assessments: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="Diagnostic assessments recommended to verify unassessed or developing skills",
    )
    explanation_narrative: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Deterministic narrative explaining alignment, strengths, gaps, and recommendations",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of record creation",
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp when analysis was calculated",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="gap_analyses",
    )
    role: Mapped[Role] = relationship(
        "Role",
        back_populates="gap_analyses",
    )
