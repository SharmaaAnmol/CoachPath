"""
Resumes and Truthful Tailoring Domain Models.
Implements Resume and ResumeVersion.
"""

from __future__ import annotations

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
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JsonB, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.applications import Application
    from app.models.auth import User
    from app.models.jobs import Job


class Resume(Base, UUIDMixin):
    """
    Original uploaded candidate resume documents and master extracted structure.
    """

    __tablename__ = "resumes"
    __table_args__ = (
        CheckConstraint("file_size_bytes <= 10485760", name="resumes_file_size_check"),
        CheckConstraint(
            "mime_type IN ('application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')",
            name="resumes_mime_type_check",
        ),
        CheckConstraint(
            "status IN ('uploaded', 'parsing', 'parsed', 'failed')",
            name="resumes_status_check",
        ),
        Index("resumes_user_id_idx", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning user account reference",
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Original client filename",
    )
    storage_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Private object storage file path",
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Document file size in bytes (max 10MB)",
    )
    mime_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="MIME content type (PDF or DOCX)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="uploaded",
        server_default=sa.text("'uploaded'"),
        nullable=False,
        doc="Document processing status ('uploaded', 'parsing', 'parsed', 'failed')",
    )
    parsed_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Full raw text extracted from uploaded document",
    )
    extracted_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JsonB(),
        nullable=True,
        doc="Structured candidate resume entities (JSON)",
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="True if this is the user's primary source resume",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of file upload (UTC)",
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="resumes")
    versions: Mapped[List[ResumeVersion]] = relationship(
        "ResumeVersion",
        back_populates="resume",
        cascade="all, delete-orphan",
    )


class ResumeVersion(Base, UUIDMixin):
    """
    Tailored resume variants aligned with a specific job posting,
    including anti-hallucination diff verification and explicit approval timestamps.
    """

    __tablename__ = "resume_versions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'approved', 'archived')",
            name="resume_versions_status_check",
        ),
        Index("resume_versions_resume_job_idx", "resume_id", "target_job_id"),
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent source resume reference",
    )
    target_job_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Target job posting reference",
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default=sa.text("1"),
        nullable=False,
        doc="Sequential iteration version number",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="draft",
        server_default=sa.text("'draft'"),
        nullable=False,
        doc="Artifact lifecycle status ('draft', 'approved', 'archived')",
    )
    tailored_content: Mapped[Dict[str, Any]] = mapped_column(
        JsonB(),
        nullable=False,
        doc="Structured tailored resume payload",
    )
    diff_summary: Mapped[Dict[str, Any]] = mapped_column(
        JsonB(),
        nullable=False,
        doc="Structured before/after diff summary {additions, rephrasings, deletions}",
    )
    anti_hallucination_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=sa.text("FALSE"),
        nullable=False,
        doc="True if zero-hallucination verification checks passed against profile facts",
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp candidate reviewed and approved this version (UTC)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
        doc="Timestamp of generation (UTC)",
    )

    # Relationships
    resume: Mapped[Resume] = relationship("Resume", back_populates="versions")
    target_job: Mapped[Job] = relationship(
        "Job",
        back_populates="tailored_resume_versions",
    )
    applications: Mapped[List[Application]] = relationship(
        "Application",
        back_populates="tailored_resume_version",
    )
