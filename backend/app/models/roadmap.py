"""
Dynamic Personalized Roadmaps Domain Models.
Implements Roadmap, RoadmapPhase, and RoadmapTask.
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

from app.models.base import Base, JsonB, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.career import CareerProfile, Role
    from app.models.skills import Skill


class Roadmap(Base, UUIDMixin, TimestampMixin):
    """
    Active personalized learning roadmap tied to the candidate's primary target role.
    """

    __tablename__ = "roadmaps"
    __table_args__ = (
        Index("roadmaps_profile_active_idx", "career_profile_id", "is_active"),
    )

    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owning career profile reference",
    )
    target_role_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Target benchmark role reference",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Roadmap curriculum title",
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default=sa.text("1"),
        nullable=False,
        doc="Roadmap evolution version number",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=sa.text("TRUE"),
        nullable=False,
        doc="Active roadmap indicator",
    )
    total_tasks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Total number of tasks across all phases",
    )
    completed_tasks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Number of verified completed tasks",
    )

    # Relationships
    career_profile: Mapped[CareerProfile] = relationship(
        "CareerProfile",
        back_populates="roadmaps",
    )
    target_role: Mapped[Role] = relationship(
        "Role",
        back_populates="roadmaps",
    )
    phases: Mapped[List[RoadmapPhase]] = relationship(
        "RoadmapPhase",
        back_populates="roadmap",
        cascade="all, delete-orphan",
    )


class RoadmapPhase(Base, UUIDMixin):
    """
    Thematic sequential phases inside a roadmap (e.g., Phase 1: Core Async Architecture).
    """

    __tablename__ = "roadmap_phases"
    __table_args__ = (
        CheckConstraint("order_index >= 0", name="roadmap_phases_order_idx_check"),
        Index("roadmap_phases_roadmap_idx", "roadmap_id", "order_index"),
    )

    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent roadmap reference",
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Phase title",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Phase conceptual focus and goals",
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Sequential order of the phase",
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=sa.text("FALSE"),
        nullable=False,
        doc="True if all child tasks have been completed",
    )

    # Relationships
    roadmap: Mapped[Roadmap] = relationship(
        "Roadmap",
        back_populates="phases",
    )
    tasks: Mapped[List[RoadmapTask]] = relationship(
        "RoadmapTask",
        back_populates="phase",
        cascade="all, delete-orphan",
    )


class RoadmapTask(Base, UUIDMixin):
    """
    Concrete actionable milestones, curated resources, and required project deliverables.
    """

    __tablename__ = "roadmap_tasks"
    __table_args__ = (
        CheckConstraint("estimated_hours > 0", name="roadmap_tasks_est_hours_check"),
        CheckConstraint("order_index >= 0", name="roadmap_tasks_order_idx_check"),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'skipped')",
            name="roadmap_tasks_status_check",
        ),
        Index("roadmap_tasks_phase_idx", "phase_id", "order_index"),
        Index("roadmap_tasks_status_idx", "status"),
    )

    phase_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("roadmap_phases.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent roadmap phase reference",
    )
    skill_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
        doc="Targeted canonical skill reference",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Task deliverable title",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed milestone guidance and execution steps",
    )
    estimated_hours: Mapped[int] = mapped_column(
        Integer,
        default=5,
        server_default=sa.text("5"),
        nullable=False,
        doc="Expected completion effort in hours",
    )
    resource_urls: Mapped[List[Dict[str, Any]]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="Array of curated educational resources [{title, url, type}]",
    )
    deliverable_requirement: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Verification deliverable requirements (e.g., GitHub repo link)",
    )
    submission_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Candidate submitted deliverable proof URL",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        server_default=sa.text("'pending'"),
        nullable=False,
        doc="Task status ('pending', 'in_progress', 'completed', 'skipped')",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of task completion (UTC)",
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Sequential order of the task within its phase",
    )

    # Relationships
    phase: Mapped[RoadmapPhase] = relationship(
        "RoadmapPhase",
        back_populates="tasks",
    )
    skill: Mapped[Optional[Skill]] = relationship(
        "Skill",
        back_populates="roadmap_tasks",
    )
