"""
Diagnostic Skill Assessments API Router.
Provides endpoints for diagnostic catalog browsing, multi-question test sessions,
server-side deterministic answer submission, grading, pedagogical reviews, and attempt history.
"""

from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session, require_active_user
from app.models.auth import User
from app.schemas.assessments import (
    AssessmentCategoryListItem,
    AssessmentDetailResponse,
    AssessmentResultResponse,
    AttemptHistoryItem,
    AttemptSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.assessments import AssessmentService

router = APIRouter(prefix="/assessments", tags=["Group 5: Assessments"])
_service = AssessmentService()


@router.get(
    "",
    response_model=List[AssessmentCategoryListItem],
    status_code=status.HTTP_200_OK,
    summary="List Diagnostic Assessment Categories",
    description="Returns all 9 technical domain assessment categories annotated with the authenticated user's attempt status and score.",
)
async def list_assessments(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> List[AssessmentCategoryListItem]:
    return await _service.list_categories(current_user, db)


@router.get(
    "/history",
    response_model=List[AttemptHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get User Assessment History",
    description="Returns all past and in-progress assessment attempts for the authenticated candidate.",
)
async def get_assessment_history(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> List[AttemptHistoryItem]:
    return await _service.get_user_history(current_user, db)


@router.get(
    "/attempts/{attempt_id}",
    response_model=AttemptSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Active Attempt Session",
    description="Retrieves the ordered questions and recorded answers for an in-progress attempt. Correct answer keys are strictly withheld.",
)
async def get_active_attempt(
    attempt_id: uuid.UUID = Path(..., description="Unique UUID of the assessment attempt"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> AttemptSessionResponse:
    return await _service.get_active_attempt(attempt_id, current_user, db)


@router.post(
    "/attempts/{attempt_id}/answer",
    response_model=SubmitAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit or Update Question Answer",
    description="Saves or updates a candidate's selected option index for a question within an active attempt.",
)
async def submit_answer(
    request: SubmitAnswerRequest,
    attempt_id: uuid.UUID = Path(..., description="Unique UUID of the assessment attempt"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> SubmitAnswerResponse:
    return await _service.submit_answer(attempt_id, request, current_user, db)


@router.post(
    "/attempts/{attempt_id}/complete",
    response_model=AssessmentResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalize and Grade Assessment Attempt",
    description="Finalizes the attempt, calculates deterministic score (0-100), evaluates topic and difficulty breakdowns, updates career skills, and reveals complete review with pedagogical explanations.",
)
async def complete_attempt(
    attempt_id: uuid.UUID = Path(..., description="Unique UUID of the assessment attempt"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> AssessmentResultResponse:
    return await _service.complete_attempt(attempt_id, current_user, db)


@router.get(
    "/attempts/{attempt_id}/result",
    response_model=AssessmentResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Graded Assessment Result",
    description="Retrieves the full diagnostic result, score breakdown, proficiency band, and pedagogical review for a completed attempt.",
)
async def get_attempt_result(
    attempt_id: uuid.UUID = Path(..., description="Unique UUID of the assessment attempt"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> AssessmentResultResponse:
    return await _service.get_attempt_result(attempt_id, current_user, db)


@router.get(
    "/{category_id}",
    response_model=AssessmentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Assessment Category Details",
    description="Retrieves category metadata, total question bank count, difficulty distribution, and syllabus topics by assessment UUID or skill ID.",
)
async def get_assessment_detail(
    category_id: str = Path(..., description="Assessment UUID or skill identifier (e.g. 'python', 'dsa')"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> AssessmentDetailResponse:
    return await _service.get_assessment_detail(category_id, db)


@router.post(
    "/{category_id}/start",
    response_model=AttemptSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Start or Resume Assessment Attempt",
    description="Starts a new 20-question diagnostic attempt (7 basic, 7 intermediate, 6 advanced) or resumes an existing active attempt for the specified domain.",
)
async def start_or_resume_attempt(
    category_id: str = Path(..., description="Assessment UUID or skill identifier (e.g. 'python', 'c-cpp')"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> AttemptSessionResponse:
    return await _service.start_or_resume_attempt(category_id, current_user, db)
