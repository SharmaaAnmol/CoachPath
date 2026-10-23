"""
Dynamic Personalized Roadmaps Domain Models.
Implements Roadmap, RoadmapPhase, and RoadmapTask with Phase 7A curriculum enhancements.
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
    from app.models.skills import Skill, SkillGapAnalysis


class Roadmap(Base, UUIDMixin, TimestampMixin):
    """
    Active personalized learning roadmap tied to the candidate's primary target role.
    Integrates with deterministic skill-gap analysis snapshots and user time constraints.
    """

    __tablename__ = "roadmaps"
    __table_args__ = (
        Index("roadmaps_profile_active_idx", "career_profile_id", "is_active"),
        Index("roadmaps_gap_analysis_idx", "skill_gap_analysis_id"),
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
    skill_gap_analysis_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        ForeignKey("skill_gap_analyses.id", ondelete="SET NULL"),
        nullable=True,
        doc="Skill gap analysis snapshot reference used for roadmap generation",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Roadmap curriculum title",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Curriculum summary narrative and strategic learning path overview",
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
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        server_default=sa.text("'active'"),
        nullable=False,
        doc="Lifecycle status ('active', 'completed', 'archived')",
    )
    generation_mode: Mapped[str] = mapped_column(
        String(32),
        default="deterministic_ai",
        server_default=sa.text("'deterministic_ai'"),
        nullable=False,
        doc="Generation method ('deterministic', 'deterministic_ai')",
    )
    weekly_hours: Mapped[int] = mapped_column(
        Integer,
        default=10,
        server_default=sa.text("10"),
        nullable=False,
        doc="Planned weekly study effort in hours",
    )
    total_estimated_hours: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Total estimated study effort required across all phases",
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
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Curriculum start timestamp",
    )
    target_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Projected completion timestamp based on weekly hours",
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
    skill_gap_analysis: Mapped[Optional[SkillGapAnalysis]] = relationship(
        "SkillGapAnalysis",
    )
    phases: Mapped[List[RoadmapPhase]] = relationship(
        "RoadmapPhase",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapPhase.order_index",
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
    objective: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Specific technical milestone objective for this phase",
    )
    estimated_hours: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sa.text("0"),
        nullable=False,
        doc="Sum of task hours in phase",
    )
    prerequisites: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Entry prerequisites for phase",
    )
    completion_criteria: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Criteria required to complete phase",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        server_default=sa.text("'pending'"),
        nullable=False,
        doc="Phase status ('pending', 'in_progress', 'completed')",
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
        order_by="RoadmapTask.order_index",
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
        Index("roadmap_tasks_skill_idx", "skill_id"),
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
    learning_objective: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Concrete learning objective or competence verified",
    )
    task_type: Mapped[str] = mapped_column(
        String(32),
        default="project",
        server_default=sa.text("'project'"),
        nullable=False,
        doc="Task type ('course', 'reading', 'practice', 'project', 'assessment')",
    )
    priority: Mapped[str] = mapped_column(
        String(16),
        default="medium",
        server_default=sa.text("'medium'"),
        nullable=False,
        doc="Task priority ('critical', 'high', 'medium', 'low')",
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
    prerequisite_task_ids: Mapped[List[str]] = mapped_column(
        JsonB(),
        default=list,
        server_default=sa.text("'[]'"),
        nullable=False,
        doc="Prerequisite task IDs within this roadmap",
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
    completion_criteria: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed verification / acceptance criteria",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        server_default=sa.text("'pending'"),
        nullable=False,
        doc="Task status ('pending', 'in_progress', 'completed', 'skipped')",
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Estimated scheduled milestone due date",
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
    source_gap_priority: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        doc="Source gap priority from skill gap analysis (e.g. 'CRITICAL', 'HIGH')",
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
