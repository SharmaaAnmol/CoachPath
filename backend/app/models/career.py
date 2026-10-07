"""
Career Profile and Evidence Graph Domain Models.
Implements Role, CareerProfile, Education, Experience, Project, and Certification.
"""

from __future__ import annotations

import decimal
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional
import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    StringArray,
    TextArray,
    TimestampMixin,
    UUIDMixin,
    utc_now,
)

if TYPE_CHECKING:
    from app.models.applications import InterviewQuestion
    from app.models.auth import User
    from app.models.jobs import Job, JobMatch
    from app.models.roadmap import Roadmap
    from app.models.skills import RoleRequirement, SkillGap, UserSkill


class Role(Base):
    """
    Master canonical benchmark career targets (e.g., 'backend-developer', 'ai-engineer').
    """

    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        doc="Canonical role identifier (e.g., 'backend-developer')",
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Display title of the role",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed summary of role competencies and expectations",
    )
    category: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Functional category (e.g., 'engineering', 'data')",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    # Relationships
    requirements: Mapped[List[RoleRequirement]] = relationship(
        "RoleRequirement",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    career_profiles_as_primary: Mapped[List[CareerProfile]] = relationship(
        "CareerProfile",
        foreign_keys="CareerProfile.primary_role_id",
        back_populates="primary_role",
    )
    career_profiles_as_secondary: Mapped[List[CareerProfile]] = relationship(
        "CareerProfile",
        foreign_keys="CareerProfile.secondary_role_id",
        back_populates="secondary_role",
    )
    skill_gaps: Mapped[List[SkillGap]] = relationship(
        "SkillGap",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    roadmaps: Mapped[List[Roadmap]] = relationship(
        "Roadmap",
        back_populates="target_role",
    )
    jobs: Mapped[List[Job]] = relationship(
        "Job",
        back_populates="role",
    )
    interview_questions: Mapped[List[InterviewQuestion]] = relationship(
        "InterviewQuestion",
        back_populates="role",
        cascade="all, delete-orphan",
    )


class CareerProfile(Base, UUIDMixin, TimestampMixin):
    """
    Central root career record linking candidate preferences, stage, and targets.
    """

    __tablename__ = "career_profiles"
    __table_args__ = (
        CheckConstraint(
            "career_stage IN ('student', 'recent_graduate', 'early_career')",
            name="career_profiles_stage_check",
        ),
        CheckConstraint(
            "work_preference IN ('remote', 'hybrid', 'onsite', 'flexible')",
            name="career_profiles_preference_check",
        ),
        CheckConstraint(
            "years_of_experience >= 0.0",
            name="career_profiles_years_exp_check",
        ),
        Index("career_profiles_user_id_idx", "user_id", unique=True),
        Index("career_profiles_primary_role_idx", "primary_role_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        doc="Owning user account reference",
    )
    primary_role_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Target primary benchmark role",
    )
    secondary_role_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=True,
        doc="Target secondary or stretch benchmark role",
    )
    career_stage: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Candidate career stage ('student', 'recent_graduate', 'early_career')",
    )
    work_preference: Mapped[str] = mapped_column(
        String(32),
        default="hybrid",
        nullable=False,
        doc="Workplace flexibility preference ('remote', 'hybrid', 'onsite', 'flexible')",
    )
    target_locations: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Target metropolitan or geographic markets",
    )
    years_of_experience: Mapped[decimal.Decimal] = mapped_column(
        Numeric(3, 1),
        default=decimal.Decimal("0.0"),
        server_default=sa.text("0.0"),
        nullable=False,
        doc="Total cumulative verified professional experience in years",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="career_profile")
    primary_role: Mapped[Role] = relationship(
        "Role",
        foreign_keys=[primary_role_id],
        back_populates="career_profiles_as_primary",
    )
    secondary_role: Mapped[Optional[Role]] = relationship(
        "Role",
        foreign_keys=[secondary_role_id],
        back_populates="career_profiles_as_secondary",
    )
    education: Mapped[List[Education]] = relationship(
        "Education",
        back_populates="career_profile",
        cascade="all, delete-orphan",
    )
    experience: Mapped[List[Experience]] = relationship(
        "Experience",
        back_populates="career_profile",
        cascade="all, delete-orphan",
    )
    projects: Mapped[List[Project]] = relationship(
        "Project",
        back_populates="career_profile",
        cascade="all, delete-orphan",
    )
    certifications: Mapped[List[Certification]] = relationship(
        "Certification",
        back_populates="career_profile",
        cascade="all, delete-orphan",
    )
    user_skills: Mapped[List[UserSkill]] = relationship(
        "UserSkill",
        back_populates="career_profile",
        cascade="all, delete-orphan",
    )
    skill_gaps: Mapped[List[SkillGap]] = relationship(
        "SkillGap",
        back_populates="career_profile",
        cascade="all, delete-orphan",
    )
    roadmaps: Mapped[List[Roadmap]] = relationship(
        "Roadmap",
        back_populates="career_profile",
        cascade="all, delete-orphan",
    )
    job_matches: Mapped[List[JobMatch]] = relationship(
        "JobMatch",
        back_populates="career_profile",
        cascade="all, delete-orphan",
    )


class Education(Base, UUIDMixin, TimestampMixin):
    """
    Verified academic credentials, degrees, institutions, and periods of study.
    """

    __tablename__ = "education"
    __table_args__ = (
        CheckConstraint(
            "gpa IS NULL OR (gpa >= 0.0 AND gpa <= 4.0)",
            name="education_gpa_check",
        ),
        Index("education_profile_id_idx", "career_profile_id"),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning career profile reference",
    )
    institution_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Name of college, university, or educational provider",
    )
    degree: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Degree or certificate name (e.g., 'Bachelor of Science')",
    )
    field_of_study: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Academic major or specialization (e.g., 'Computer Science')",
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date program of study commenced",
    )
    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Date of graduation or expected completion (NULL if active)",
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="True if candidate is currently enrolled",
    )
    gpa: Mapped[Optional[decimal.Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        doc="Cumulative grade point average on a 4.0 scale",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="education",
    )


class Experience(Base, UUIDMixin, TimestampMixin):
    """
    Verified professional employment history, internships, and work experience.
    """

    __tablename__ = "experience"
    __table_args__ = (
        Index("experience_profile_id_idx", "career_profile_id"),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning career profile reference",
    )
    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Name of employer or organization",
    )
    role_title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Job title held (e.g., 'Software Engineering Intern')",
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Geographic location of role",
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Start date of employment",
    )
    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="End date of employment (NULL if currently active)",
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="True if currently employed in this position",
    )
    bullet_points: Mapped[List[str]] = mapped_column(
        TextArray(),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Quantified accomplishment bullet points",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="experience",
    )


class Project(Base, UUIDMixin, TimestampMixin):
    """
    Technical software artifacts, academic capstones, and open-source contributions.
    """

    __tablename__ = "projects"
    __table_args__ = (
        Index("projects_profile_id_idx", "career_profile_id"),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning career profile reference",
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Project display title",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Overview of problem solved, architecture, and engineering scope",
    )
    technologies: Mapped[List[str]] = mapped_column(
        StringArray(64),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Technologies, languages, and frameworks utilized",
    )
    github_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Public GitHub repository URL",
    )
    live_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Public production deployment URL",
    )
    bullet_points: Mapped[List[str]] = mapped_column(
        TextArray(),
        default=list,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="Key architectural achievements and metrics",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="projects",
    )


class Certification(Base, UUIDMixin):
    """
    Verified professional credentials and industry certifications (e.g., AWS, GCP).
    """

    __tablename__ = "certifications"
    __table_args__ = (
        Index("certifications_profile_id_idx", "career_profile_id"),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning career profile reference",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Official certification title",
    )
    issuing_organization: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Issuing authority (e.g., 'Amazon Web Services')",
    )
    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date credential was earned",
    )
    expiration_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Date credential expires (if applicable)",
    )
    credential_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Official certificate or badge verification ID",
    )
    credential_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Public verification URL",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="certifications",
    )
