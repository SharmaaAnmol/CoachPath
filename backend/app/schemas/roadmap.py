"""
Pydantic Schemas for Phase 7A: Personalized Learning Roadmap Engine.
Defines strict validation contracts for Roadmap Generation, Scheduling Constraints,
Sequential Phases, Actionable Milestones, Progress Tracking, and Adaptation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ─── Request Schemas ──────────────────────────────────────────────────

class RoadmapGenerateRequest(BaseModel):
    """Parameters for generating or regenerating a personalized learning roadmap."""
    model_config = ConfigDict(extra="forbid")

    role_id: Optional[str] = Field(
        None,
        description="Optional target role ID. If omitted, uses user's primary target role from CareerProfile.",
    )
    weekly_hours: Optional[int] = Field(
        None,
        ge=1,
        le=80,
        description="Available study hours per week. Defaults to profile preference or 10 hours/week.",
    )
    target_timeline_months: Optional[int] = Field(
        None,
        ge=1,
        le=36,
        description="Target completion timeline in months. Defaults to profile preference or 6 months.",
    )
    preferred_resources: Optional[List[str]] = Field(
        None,
        description="Preferred learning resource formats (e.g. ['documentation', 'interactive', 'video', 'projects']).",
    )
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Optional list of specific skill IDs to prioritize.",
    )
    force_regenerate: bool = Field(
        False,
        description="If True, archives previous active roadmap and generates a fresh curriculum version.",
    )


class UpdateRoadmapTaskRequest(BaseModel):
    """Request payload to update the execution status or deliverable of a roadmap task."""
    model_config = ConfigDict(extra="forbid")

    status: Optional[str] = Field(
        None,
        pattern="^(pending|in_progress|completed|skipped)$",
        description="Updated lifecycle state of the milestone task.",
    )
    submission_url: Optional[str] = Field(
        None,
        max_length=255,
        pattern=r"^(https?://[^\s]+)?$",
        description="Deliverable proof link (e.g. GitHub repository or pull request).",
    )


# ─── Response Schemas ─────────────────────────────────────────────────

class ResourceLink(BaseModel):
    """Curated learning resource reference."""
    title: str
    url: str
    type: str  # 'documentation' | 'tutorial' | 'course' | 'repo' | 'book' | 'article'


class RoadmapTaskResponse(BaseModel):
    """Actionable milestone deliverable within a roadmap phase."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phase_id: uuid.UUID
    skill_id: Optional[str] = None
    skill_name: Optional[str] = None
    title: str
    description: str
    learning_objective: Optional[str] = None
    task_type: str  # 'course' | 'reading' | 'practice' | 'project' | 'assessment'
    priority: str  # 'critical' | 'high' | 'medium' | 'low'
    estimated_hours: int
    resource_urls: List[Dict[str, Any]] = Field(default_factory=list)
    prerequisite_task_ids: List[str] = Field(default_factory=list)
    deliverable_requirement: Optional[str] = None
    submission_url: Optional[str] = None
    completion_criteria: Optional[str] = None
    status: str  # 'pending' | 'in_progress' | 'completed' | 'skipped'
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    order_index: int
    source_gap_priority: Optional[str] = None


class RoadmapPhaseResponse(BaseModel):
    """Thematic sequential milestone phase inside a personalized roadmap."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    roadmap_id: uuid.UUID
    title: str
    description: str
    objective: Optional[str] = None
    estimated_hours: int
    prerequisites: Optional[str] = None
    completion_criteria: Optional[str] = None
    status: str  # 'pending' | 'in_progress' | 'completed'
    order_index: int
    is_completed: bool
    tasks: List[RoadmapTaskResponse] = Field(default_factory=list)


class RoadmapResponse(BaseModel):
    """Full personalized learning roadmap curriculum presentation model."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    career_profile_id: uuid.UUID
    target_role_id: str
    target_role_title: str
    skill_gap_analysis_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    version: int
    is_active: bool
    status: str
    generation_mode: str
    weekly_hours: int
    total_estimated_hours: int
    total_tasks: int
    completed_tasks: int
    progress_percentage: float
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    feasibility_status: str  # 'feasible' | 'demanding' | 'unrealistic'
    feasibility_note: Optional[str] = None
    phases: List[RoadmapPhaseResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class RoadmapProgressResponse(BaseModel):
    """Real-time progress overview and next actionable tasks for the active roadmap."""
    model_config = ConfigDict(from_attributes=True)

    roadmap_id: uuid.UUID
    target_role_id: str
    target_role_title: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    progress_percentage: float
    total_estimated_hours: int
    completed_hours: int
    remaining_hours: int
    weekly_hours: int
    estimated_weeks_remaining: float
    current_phase_index: int
    current_phase_title: Optional[str] = None
    next_recommended_tasks: List[RoadmapTaskResponse] = Field(default_factory=list)


class RoadmapAdaptationResponse(BaseModel):
    """Result of adapting the roadmap to newly verified skills or assessment results."""
    model_config = ConfigDict(from_attributes=True)

    roadmap_id: uuid.UUID
    adapted: bool
    tasks_auto_completed: int
    tasks_adjusted: int
    message: str
    roadmap: RoadmapResponse


class RoadmapHistoryItem(BaseModel):
    """Summary of a roadmap version for history listing."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    target_role_id: str
    target_role_title: str
    version: int
    is_active: bool
    status: str
    generation_mode: str
    weekly_hours: int
    total_estimated_hours: int
    total_tasks: int
    completed_tasks: int
    progress_percentage: float
    created_at: datetime
    updated_at: datetime


class RoadmapHistoryResponse(BaseModel):
    """Historical list of roadmap versions for the user."""
    items: List[RoadmapHistoryItem]
    total: int

