"""
FastAPI Route Handlers for Phase 7A: Personalized Learning Roadmap Engine.
Implements endpoints for Curriculum Generation, Status Retrieval, Progress Tracking,
Milestone Task Updates, and Dynamic Evidence Adaptation.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import LLMProvider
from app.ai.factory import get_llm_provider
from app.api.dependencies import get_session, require_active_user
from app.models.auth import User
from app.schemas.roadmap import (
    RoadmapAdaptationResponse,
    RoadmapGenerateRequest,
    RoadmapHistoryResponse,
    RoadmapProgressResponse,
    RoadmapResponse,
    RoadmapTaskResponse,
    UpdateRoadmapTaskRequest,
)
from app.services.roadmap_engine import RoadmapEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/roadmap", tags=["Group 7: Roadmap"])
_engine = RoadmapEngine()


def _get_llm() -> LLMProvider:
    """Dependency injection for the configured LLM provider."""
    return get_llm_provider()


@router.post(
    "/generate",
    response_model=RoadmapResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Personalized Learning Roadmap",
    description=(
        "Generates a multi-phase, milestone-based learning roadmap grounded in the candidate's "
        "latest skill gap analysis, benchmark role requirements, study hours, and target timeline."
    ),
)
async def generate_roadmap(
    request: Optional[RoadmapGenerateRequest] = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
    llm: LLMProvider = Depends(_get_llm),
) -> RoadmapResponse:
    return await _engine.generate_roadmap(
        user=current_user,
        db=db,
        request=request,
        llm=llm,
    )


@router.get(
    "",
    response_model=RoadmapResponse,
    summary="Get Active Roadmap",
    description="Returns the currently active personalized roadmap for the authenticated user.",
)
async def get_active_roadmap(
    role_id: Optional[str] = Query(None, description="Optional target role ID filter"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RoadmapResponse:
    return await _engine.get_active_roadmap(
        user=current_user,
        db=db,
        role_id=role_id,
    )


@router.get(
    "/active",
    response_model=RoadmapResponse,
    summary="Get Active Roadmap (Alias)",
    description="Alias endpoint returning the active personalized roadmap for the user.",
)
async def get_active_roadmap_alias(
    role_id: Optional[str] = Query(None, description="Optional target role ID filter"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RoadmapResponse:
    return await _engine.get_active_roadmap(
        user=current_user,
        db=db,
        role_id=role_id,
    )


@router.get(
    "/history",
    response_model=RoadmapHistoryResponse,
    summary="Get Roadmap History",
    description="Returns the historical list of all generated roadmap versions (both active and archived) for the authenticated user.",
)
async def get_roadmap_history(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RoadmapHistoryResponse:
    return await _engine.get_roadmap_history(
        user=current_user,
        db=db,
    )


@router.get(
    "/{roadmap_id}",
    response_model=RoadmapResponse,
    summary="Get Roadmap By ID",
    description="Returns full phase and task details for a specific roadmap by ID.",
)
async def get_roadmap_by_id(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RoadmapResponse:
    return await _engine.get_roadmap_by_id(
        roadmap_id=roadmap_id,
        user=current_user,
        db=db,
    )


@router.get(
    "/{roadmap_id}/progress",
    response_model=RoadmapProgressResponse,
    summary="Get Roadmap Progress Summary",
    description=(
        "Returns calculated real-time progress percentages, hours completed vs remaining, "
        "current active phase, and next recommended tasks."
    ),
)
async def get_roadmap_progress(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RoadmapProgressResponse:
    return await _engine.get_roadmap_progress(
        roadmap_id=roadmap_id,
        user=current_user,
        db=db,
    )


@router.patch(
    "/tasks/{task_id}",
    response_model=RoadmapTaskResponse,
    summary="Update Task Progress / Deliverable",
    description=(
        "Updates the status ('pending', 'in_progress', 'completed', 'skipped') or deliverable "
        "submission URL of a roadmap task and updates phase completion status."
    ),
)
async def update_roadmap_task(
    task_id: uuid.UUID,
    request: UpdateRoadmapTaskRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RoadmapTaskResponse:
    return await _engine.update_task_status(
        task_id=task_id,
        request=request,
        user=current_user,
        db=db,
    )


@router.post(
    "/{roadmap_id}/adapt",
    response_model=RoadmapAdaptationResponse,
    summary="Adapt Roadmap to Assessment Evidence",
    description=(
        "Scans for newly verified diagnostic skill assessments and automatically completes "
        "corresponding pending milestones, adjusting remaining curriculum hours."
    ),
)
async def adapt_roadmap(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RoadmapAdaptationResponse:
    return await _engine.adapt_roadmap(
        roadmap_id=roadmap_id,
        user=current_user,
        db=db,
    )
