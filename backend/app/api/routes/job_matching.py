"""
Intelligent Job Matching API Router for CoachPath (Phase 9A).
Provides endpoints for personalized recommendation ranking, match explainability drawers,
deterministic scoring breakdowns, and match recalculation.
"""

from __future__ import annotations

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_session, require_active_user
from app.core.exceptions import NotFoundException
from app.models.auth import User
from app.models.career import CareerProfile
from app.models.jobs import Job, JobMatch, JobSkill
from app.schemas.job_matching import (
    JobMatchBatchRefreshResponse,
    JobMatchExplanationDrawerResponse,
    JobMatchRecalculateRequest,
    JobMatchResponse,
    JobRecommendationResponse,
)
from app.services.job_matching_engine import JobMatchingEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Group 9: Job Matching"])
_engine = JobMatchingEngine()


# ─────────────────────────────────────────────
# 1. Recommendations Endpoint
# ─────────────────────────────────────────────

@router.get(
    "/recommendations",
    response_model=JobRecommendationResponse,
    summary="Get Recommended Jobs",
    description="Returns personalized job opportunities ranked by deterministic multi-factor match score.",
)
async def get_recommendations(
    min_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum match percentage filter (0-100)"),
    role_id: Optional[str] = Query(None, description="Target canonical role filter"),
    remote_type: Optional[str] = Query(None, pattern="^(remote|hybrid|onsite)$", description="Workplace type filter"),
    include_provisional: bool = Query(True, description="Include matches with low evidence coverage (< 40%)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobRecommendationResponse:
    return await _engine.get_recommendations(
        db=db,
        user=current_user,
        min_score=min_score,
        role_id=role_id,
        remote_type=remote_type,
        include_provisional=include_provisional,
        page=page,
        page_size=page_size,
    )


# ─────────────────────────────────────────────
# 2. Batch Matches List & Refresh Endpoints
# ─────────────────────────────────────────────

@router.get(
    "/matches",
    response_model=List[JobMatchResponse],
    summary="List Evaluated Job Matches",
    description="Returns all previously calculated job matches for the authenticated user, ordered by score descending.",
)
async def list_matches(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> List[JobMatchResponse]:
    profile = await _engine._get_or_create_profile(db=db, user=current_user)

    matches_stmt = (
        select(JobMatch)
        .options(selectinload(JobMatch.job).selectinload(Job.skills).selectinload(JobSkill.skill))
        .where(JobMatch.career_profile_id == profile.id)
        .order_by(JobMatch.overall_score.desc())
    )
    records = (await db.scalars(matches_stmt)).all()
    return [_engine._orm_to_response(r, r.job) for r in records if r.job]


@router.post(
    "/matches/refresh",
    response_model=JobMatchBatchRefreshResponse,
    summary="Batch Refresh User Recommendations",
    description="Forces full recalculation of match scores across all active jobs for the current user.",
)
async def batch_refresh_matches(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobMatchBatchRefreshResponse:
    count = await _engine.batch_refresh_user_matches(db=db, user=current_user)
    return JobMatchBatchRefreshResponse(
        recalculated_count=count,
        status="completed",
        scoring_version=_engine.scoring_version,
        message=f"Successfully updated match scores for {count} active opportunities.",
    )


# ─────────────────────────────────────────────
# 3. Single Job Match & Recalculate Endpoints
# ─────────────────────────────────────────────

@router.get(
    "/{job_id}/match",
    response_model=JobMatchResponse,
    summary="Get Job Match Details",
    description="Retrieves or calculates the multi-factor match breakdown for a specific job posting.",
)
async def get_job_match(
    job_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobMatchResponse:
    return await _engine.get_or_calculate_job_match(
        db=db,
        user=current_user,
        job_id=job_id,
        force_recalculate=False,
    )


@router.get(
    "/{job_id}/match-explanation",
    response_model=JobMatchExplanationDrawerResponse,
    summary="Get Job Match Explainability Drawer",
    description="Returns detailed evidence alignment, strengths, gaps, and hiring rationale conforming to API Spec Section 8.2.",
)
async def get_job_match_explanation(
    job_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobMatchExplanationDrawerResponse:
    match_resp = await _engine.get_or_calculate_job_match(
        db=db,
        user=current_user,
        job_id=job_id,
        force_recalculate=False,
    )

    breakdown_dict = {
        "skill_score": match_resp.breakdown.skill_score,
        "experience_score": match_resp.breakdown.experience_score,
        "project_score": match_resp.breakdown.project_score,
        "location_score": match_resp.breakdown.location_score,
        "preference_score": match_resp.breakdown.preference_score,
        "vector_semantic_score": match_resp.breakdown.vector_score,
    }

    return JobMatchExplanationDrawerResponse(
        job_id=match_resp.job_id,
        overall_score=match_resp.overall_score,
        evidence_coverage=match_resp.breakdown.evidence_coverage,
        breakdown=breakdown_dict,
        matched_skills=match_resp.matched_skills,
        missing_skills=match_resp.missing_skills,
        matched_preferred_skills=match_resp.matched_preferred_skills,
        unknown_skills=match_resp.unknown_skills,
        hiring_rationale=match_resp.explanation.summary,
        strengths=match_resp.explanation.strengths,
        gaps=match_resp.explanation.gaps,
        recommended_actions=match_resp.explanation.recommended_actions,
        skills_detail=match_resp.skills_detail,
    )


@router.post(
    "/{job_id}/match/recalculate",
    response_model=JobMatchResponse,
    summary="Recalculate Job Match",
    description="Forces immediate recalculation of match score and explainability factors for a specific job.",
)
async def recalculate_job_match(
    job_id: uuid.UUID,
    payload: Optional[JobMatchRecalculateRequest] = None,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobMatchResponse:
    return await _engine.get_or_calculate_job_match(
        db=db,
        user=current_user,
        job_id=job_id,
        force_recalculate=True,
    )
