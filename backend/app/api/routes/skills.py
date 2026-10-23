"""
Skill Taxonomy and Deterministic Gap Analysis API Routes.
Implements endpoints for canonical skills, latest gap analysis snapshot,
historical snapshots, on-demand recalculation, and skill evidence drill-down.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session, require_active_user
from app.models.auth import User
from app.schemas.skill_gap import (
    LegacySkillGapResponse,
    SkillEvidenceDetailResponse,
    SkillGapAnalysisListResponse,
    SkillGapAnalysisRequest,
    SkillGapAnalysisResponse,
    SkillResponse,
)
from app.services.skill_gap_engine import SkillGapEngine

router = APIRouter(prefix="/skills", tags=["Group 6: Skills"])
_engine = SkillGapEngine()


@router.get(
    "",
    response_model=List[SkillResponse],
    status_code=status.HTTP_200_OK,
    summary="List Canonical Skills",
    description="Retrieves the master standardized taxonomy of technical skills, categories, and aliases.",
)
async def list_canonical_skills(
    db: AsyncSession = Depends(get_session),
) -> List[SkillResponse]:
    """Returns all standardized technical skills from the taxonomy."""
    return await _engine.get_canonical_skills(db=db)


@router.get(
    "/gaps",
    response_model=LegacySkillGapResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Skill Readiness and Gaps (Legacy)",
    description="Returns high-level role readiness percentage, met skills, developing skills, and missing skills.",
)
async def get_legacy_skill_gaps(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> LegacySkillGapResponse:
    """Returns legacy-compatible readiness and skill gap summary."""
    return await _engine.get_legacy_gaps(user=current_user, db=db)


@router.post(
    "/gap-analysis",
    response_model=SkillGapAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate Skill Gap Analysis",
    description="Executes deterministic gap analysis comparing verified candidate evidence against the target role requirements.",
)
async def calculate_skill_gap_analysis(
    payload: Optional[SkillGapAnalysisRequest] = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> SkillGapAnalysisResponse:
    """Calculates and persists a new deterministic skill gap analysis snapshot."""
    role_id = payload.role_id if payload else None
    return await _engine.calculate_gap_analysis(
        user=current_user,
        db=db,
        role_id=role_id,
    )


@router.get(
    "/gap-analysis",
    response_model=SkillGapAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Latest Skill Gap Analysis",
    description="Retrieves the active, latest deterministic gap analysis snapshot for the authenticated user.",
)
async def get_latest_skill_gap_analysis(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> SkillGapAnalysisResponse:
    """Returns the latest active skill gap analysis snapshot."""
    return await _engine.get_latest_gap_analysis(user=current_user, db=db)


@router.get(
    "/gap-analysis/history",
    response_model=SkillGapAnalysisListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Gap Analysis Snapshot History",
    description="Returns the timeline history of all gap analysis snapshots calculated for the user.",
)
async def get_gap_analysis_history(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> SkillGapAnalysisListResponse:
    """Returns historical list of gap analysis snapshots."""
    return await _engine.get_history(user=current_user, db=db)


@router.post(
    "/gap-analysis/recalculate",
    response_model=SkillGapAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Recalculate Skill Gap Analysis",
    description="Forces recalculation of the gap analysis snapshot incorporating latest assessment results and profile updates.",
)
async def recalculate_skill_gap_analysis(
    payload: Optional[SkillGapAnalysisRequest] = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> SkillGapAnalysisResponse:
    """Forces recalculation and persists updated current snapshot."""
    role_id = payload.role_id if payload else None
    return await _engine.calculate_gap_analysis(
        user=current_user,
        db=db,
        role_id=role_id,
    )


@router.get(
    "/gap-analysis/{skill_id}/evidence",
    response_model=SkillEvidenceDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Skill Evidence Breakdown",
    description="Returns granular evidence items (assessments, projects, claims) supporting a specific skill.",
)
async def get_skill_evidence_breakdown(
    skill_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> SkillEvidenceDetailResponse:
    """Returns evidence supporting a canonical skill."""
    return await _engine.get_skill_evidence(
        skill_id=skill_id,
        user=current_user,
        db=db,
    )
