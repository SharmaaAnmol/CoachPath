"""
Applications, Kanban Tracker, Recruiters, and Interview Preparation Domain Models.
Implements Application, ApplicationStatusHistory, Recruiter, RecruiterContact,
RecruiterMessage, Interview, InterviewQuestion, and InterviewPreparation.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JsonB, TimestampMixin, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.career import Role
    from app.models.jobs import Job
    from app.models.resume import Resume, ResumeVersion
    from app.models.skills import Skill


class Application(Base, UUIDMixin, TimestampMixin):
    """
    Kanban pipeline tracker records linking candidates, jobs, and applied stages.
    """

    __tablename__ = "applications"
    __table_args__ = (
        CheckConstraint(
            "current_status IN ('saved', 'applied', 'screening', 'interviewing', 'offered', 'rejected', 'withdrawn')",
            name="applications_current_status_check",
        ),
        UniqueConstraint("user_id", "job_id", name="uq_applications_user_job"),
        Index("applications_user_status_idx", "user_id", "current_status"),
        Index("applications_job_idx", "job_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Candidate user reference",
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Target job listing reference",
    )
    current_status: Mapped[str] = mapped_column(
        String(32),
        default="saved",
        server_default=sa.text("'saved'"),
        nullable=False,
        doc="Pipeline stage ('saved', 'applied', 'screening', 'interviewing', 'offered', 'rejected', 'withdrawn')",
    )
    tailored_resume_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("resume_versions.id", ondelete="SET NULL"),
        nullable=True,
        doc="Tailored resume version submitted with application",
    )
    applied_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Date application was submitted to employer",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Private candidate notes",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="applications")
    job: Mapped[Job] = relationship("Job", back_populates="applications")
    tailored_resume_version: Mapped[Optional[ResumeVersion]] = relationship(
        "ResumeVersion",
        back_populates="applications",
    )
    status_history: Mapped[List[ApplicationStatusHistory]] = relationship(
        "ApplicationStatusHistory",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    recruiter_contacts: Mapped[List[RecruiterContact]] = relationship(
        "RecruiterContact",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    interviews: Mapped[List[Interview]] = relationship(
        "Interview",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    packages: Mapped[List[ApplicationPackage]] = relationship(
        "ApplicationPackage",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    outreach_drafts: Mapped[List[RecruiterOutreachDraft]] = relationship(
        "RecruiterOutreachDraft",
        back_populates="application",
        cascade="all, delete-orphan",
    )


class ApplicationStatusHistory(Base, UUIDMixin):
    """
    Immutable chronological audit of application stage movements and pipeline velocity.
    """

    __tablename__ = "application_status_history"
    __table_args__ = (
        Index("app_status_history_app_id_idx", "application_id", "changed_at"),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent application reference",
    )
    from_status: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        doc="Prior pipeline status (NULL for initial creation)",
    )
    to_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="New pipeline status transitioned into",
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of transition event (UTC)",
    )

    # Relationships
    application: Mapped[Application] = relationship(
        "Application",
        back_populates="status_history",
    )


class Recruiter(Base, UUIDMixin):
    """
    Hiring contacts, technical recruiters, and talent acquisition professionals.
    """

    __tablename__ = "recruiters"
    __table_args__ = (
        Index("recruiters_company_name_idx", "company_name"),
    )

    full_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Recruiter full name",
    )
    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hiring organization or employer",
    )
    role_title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Title (e.g., 'Senior Technical Recruiter')",
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Public LinkedIn profile URL",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    # Relationships
    contacts: Mapped[List[RecruiterContact]] = relationship(
        "RecruiterContact",
        back_populates="recruiter",
        cascade="all, delete-orphan",
    )


class RecruiterContact(Base, UUIDMixin):
    """
    Association linking a candidate's specific application with an outreach recruiter.
    """

    __tablename__ = "recruiter_contacts"
    __table_args__ = (
        UniqueConstraint("application_id", "recruiter_id", name="uq_recruiter_contacts_app_recruiter"),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        doc="Associated candidate application reference",
    )
    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("recruiters.id", ondelete="CASCADE"),
        nullable=False,
        doc="Associated recruiter reference",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp linkage was created (UTC)",
    )

    # Relationships
    application: Mapped[Application] = relationship(
        "Application",
        back_populates="recruiter_contacts",
    )
    recruiter: Mapped[Recruiter] = relationship(
        "Recruiter",
        back_populates="contacts",
    )
    messages: Mapped[List[RecruiterMessage]] = relationship(
        "RecruiterMessage",
        back_populates="recruiter_contact",
        cascade="all, delete-orphan",
    )


class RecruiterMessage(Base, UUIDMixin):
    """
    Contextual networking messages generated for candidate review and manual copy.
    """

    __tablename__ = "recruiter_messages"
    __table_args__ = (
        CheckConstraint(
            "intent IN ('introduction', 'application_follow_up', 'informational_chat')",
            name="recruiter_messages_intent_check",
        ),
        CheckConstraint(
            "status IN ('draft', 'copied_manually', 'archived')",
            name="recruiter_messages_status_check",
        ),
        Index("recruiter_messages_contact_idx", "recruiter_contact_id"),
    )

    recruiter_contact_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("recruiter_contacts.id", ondelete="CASCADE"),
        nullable=False,
        doc="Associated recruiter contact reference",
    )
    intent: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Communication goal ('introduction', 'application_follow_up', 'informational_chat')",
    )
    subject_line: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Email or InMail subject line",
    )
    message_body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Generated message copy for candidate review",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="draft",
        server_default=sa.text("'draft'"),
        nullable=False,
        doc="Message lifecycle status ('draft', 'copied_manually', 'archived')",
    )
    copied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp user clicked manual copy (UTC)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp created (UTC)",
    )

    # Relationships
    recruiter_contact: Mapped[RecruiterContact] = relationship(
        "RecruiterContact",
        back_populates="messages",
    )


class Interview(Base, UUIDMixin):
    """
    Scheduled and completed interview rounds.
    """

    __tablename__ = "interviews"
    __table_args__ = (
        CheckConstraint(
            "round_type IN ('recruiter_screen', 'technical_coding', 'system_design', 'behavioral', 'final_round')",
            name="interviews_round_type_check",
        ),
        CheckConstraint(
            "outcome IN ('pending', 'passed', 'failed', 'cancelled')",
            name="interviews_outcome_check",
        ),
        Index("interviews_app_scheduled_idx", "application_id", "scheduled_at"),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent job application reference",
    )
    round_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Interview format ('recruiter_screen', 'technical_coding', 'system_design', 'behavioral', 'final_round')",
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Scheduled date and time of the interview (UTC)",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Preparation notes or debrief reflections",
    )
    outcome: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        server_default=sa.text("'pending'"),
        nullable=False,
        doc="Round evaluation outcome ('pending', 'passed', 'failed', 'cancelled')",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp record was created (UTC)",
    )

    # Relationships
    application: Mapped[Application] = relationship(
        "Application",
        back_populates="interviews",
    )
    preparations: Mapped[List[InterviewPreparation]] = relationship(
        "InterviewPreparation",
        back_populates="interview",
        cascade="all, delete-orphan",
    )


class InterviewQuestion(Base, UUIDMixin):
    """
    Master repository of role-specific and gap-targeted interview questions.
    """

    __tablename__ = "interview_questions"
    __table_args__ = (
        CheckConstraint(
            "category IN ('technical', 'system_design', 'behavioral')",
            name="interview_questions_category_check",
        ),
        Index("interview_questions_role_cat_idx", "role_id", "category"),
    )

    role_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Target benchmark role reference",
    )
    skill_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
        doc="Targeted canonical skill reference",
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Prompt or behavioral scenario question",
    )
    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Interview category ('technical', 'system_design', 'behavioral')",
    )
    talking_points_framework: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Structured response outline (e.g., STAR framework points)",
    )
    sample_high_performing_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Exemplary benchmark answer demonstrating high seniority",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of creation (UTC)",
    )

    # Relationships
    role: Mapped[Role] = relationship("Role", back_populates="interview_questions")
    skill: Mapped[Optional[Skill]] = relationship(
        "Skill",
        back_populates="interview_questions",
    )
    preparations: Mapped[List[InterviewPreparation]] = relationship(
        "InterviewPreparation",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class InterviewPreparation(Base, UUIDMixin):
    """
    Candidate drill logs, practice notes, and readiness completions.
    """

    __tablename__ = "interview_preparations"
    __table_args__ = (
        UniqueConstraint("interview_id", "question_id", name="uq_interview_prep_interview_q"),
        Index("interview_prep_interview_q_idx", "interview_id", "question_id", unique=True),
    )

    interview_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent interview round reference",
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Target interview question reference",
    )
    candidate_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Candidate bullet points and personalized STAR stories",
    )
    is_reviewed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=sa.text("FALSE"),
        nullable=False,
        doc="True if candidate has rehearsed this question",
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of rehearsal completion (UTC)",
    )

    # Relationships
    interview: Mapped[Interview] = relationship(
        "Interview",
        back_populates="preparations",
    )
    question: Mapped[InterviewQuestion] = relationship(
        "InterviewQuestion",
        back_populates="preparations",
    )


class ApplicationPackage(Base, UUIDMixin, TimestampMixin):
    """
    Prepared job-specific application package containing cover note,
    grounded application-question answers, evidence citations,
    and multi-stage human approval & handoff lifecycle tracking.
    """

    __tablename__ = "application_packages"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'edited', 'reviewed', 'approved', 'handoff_initiated', 'submitted')",
            name="application_packages_status_check",
        ),
        Index("idx_application_packages_user_status", "user_id", "status"),
        Index("idx_application_packages_job", "job_id"),
        Index("idx_application_packages_tailored_version", "tailored_resume_version_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning candidate user reference",
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Target job listing reference",
    )
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        doc="Optional link to pipeline tracker application",
    )
    source_resume_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("resumes.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Immutable source master resume reference",
    )
    tailored_resume_version_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("resume_versions.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Specific tailored resume variant submitted with this package",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="draft",
        server_default=sa.text("'draft'"),
        nullable=False,
        doc="Package lifecycle: 'draft', 'edited', 'reviewed', 'approved', 'handoff_initiated', 'submitted'",
    )
    cover_note: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Personalized, grounded cover letter/note for target role",
    )
    application_questions: Mapped[list[dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="Itemized questions and evidence-grounded answers with clarification requirements",
    )
    evidence_references: Mapped[list[str]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="Citations of candidate skills, experience, and projects supporting this draft",
    )
    generated_metadata: Mapped[dict[str, Any]] = mapped_column(
        JsonB(),
        default=dict,
        server_default=sa.text("'{}'"),
        nullable=False,
        doc="AI generation metadata (model, tokens, word counts, prompts)",
    )
    user_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Candidate private notes or custom requirements",
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp user explicitly approved this application package (UTC)",
    )
    handoff_initiated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp user initiated external application handoff (UTC)",
    )
    application_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        doc="Preserved official employer application URL",
    )
    application_url_source: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        doc="Source of application URL ('job_listing', 'user_supplied')",
    )
    user_confirmed_submission: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=sa.text("FALSE"),
        nullable=False,
        doc="True only after candidate explicitly confirms completion of employer's application process",
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp candidate confirmed final external submission (UTC)",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="application_packages")
    job: Mapped[Job] = relationship("Job", back_populates="application_packages")
    application: Mapped[Optional[Application]] = relationship(
        "Application",
        back_populates="packages",
    )
    source_resume: Mapped[Resume] = relationship("Resume")
    tailored_resume_version: Mapped[ResumeVersion] = relationship(
        "ResumeVersion",
        back_populates="application_packages",
    )
    outreach_drafts: Mapped[List[RecruiterOutreachDraft]] = relationship(
        "RecruiterOutreachDraft",
        back_populates="package",
        cascade="all, delete-orphan",
    )


class RecruiterOutreachDraft(Base, UUIDMixin, TimestampMixin):
    """
    Personalized recruiter networking outreach drafts with strict word-count limits,
    explicit human approval gates, and safe manual handoff tracking.
    """

    __tablename__ = "recruiter_outreach_drafts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'awaiting_approval', 'approved', 'handoff_initiated', 'sent', 'cancelled')",
            name="recruiter_outreach_drafts_status_check",
        ),
        Index("idx_recruiter_outreach_user_status", "user_id", "status"),
        Index("idx_recruiter_outreach_package", "application_package_id"),
        Index("idx_recruiter_outreach_job", "job_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Candidate user reference",
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Target job listing reference",
    )
    application_package_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("application_packages.id", ondelete="SET NULL"),
        nullable=True,
        doc="Associated application package reference",
    )
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        doc="Associated pipeline application reference",
    )
    recruiter_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="User-supplied recruiter contact name",
    )
    recruiter_role_type: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Recruiter role category (e.g. 'Technical Recruiter', 'Hiring Manager')",
    )
    recruiter_profile_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        doc="User-supplied LinkedIn or public profile URL",
    )
    recruiter_contact_info: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="User-supplied email address or handle",
    )
    candidate_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User personalization notes or talking points",
    )
    subject_line: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Outreach message subject line",
    )
    message_body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Concise message body (strictly <= 90 words)",
    )
    word_count: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        doc="Calculated word count of message body",
    )
    suggested_role_types: Mapped[list[str]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="System-suggested recruiter personas when exact contact is unknown",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="draft",
        server_default=sa.text("'draft'"),
        nullable=False,
        doc="Outreach status: 'draft', 'awaiting_approval', 'approved', 'handoff_initiated', 'sent', 'cancelled'",
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp user explicitly approved this outreach message (UTC)",
    )
    handoff_initiated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp handoff was initiated (UTC)",
    )
    handoff_type: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        doc="Handoff channel ('email_mailto', 'profile_url', 'copy_text')",
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp user explicitly confirmed message was dispatched (UTC)",
    )
    user_confirmed_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=sa.text("FALSE"),
        nullable=False,
        doc="True only after candidate confirms manual sending",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="recruiter_outreach_drafts")
    job: Mapped[Job] = relationship("Job", back_populates="recruiter_outreach_drafts")
    package: Mapped[Optional[ApplicationPackage]] = relationship(
        "ApplicationPackage",
        back_populates="outreach_drafts",
    )
    application: Mapped[Optional[Application]] = relationship(
        "Application",
        back_populates="outreach_drafts",
    )
