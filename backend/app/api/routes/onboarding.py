"""
AI Career Onboarding API Routes for CoachPath.
Exposes REST endpoints for the complete conversational discovery lifecycle:
start → progress → respond → history → summary → confirm.

All endpoints require candidate authentication and enforce resource ownership.
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import LLMProvider
from app.ai.factory import get_llm_provider
from app.api.dependencies import get_session, require_active_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.auth import User
from app.schemas.onboarding import (
    ConfirmSummaryRequest,
    ConversationTurnResponse,
    OnboardingProgressResponse,
    OnboardingSessionResponse,
    OnboardingSummaryResponse,
    StartOnboardingResponse,
    SubmitResponseRequest,
    SubmitResponseResult,
)
from app.services.onboarding import OnboardingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["Group 2: Onboarding"])
_service = OnboardingService()


def _get_llm() -> LLMProvider:
    """FastAPI dependency injecting the configured singleton LLMProvider."""
    return get_llm_provider()


@router.get("", summary="Onboarding Module Status")
async def onboarding_status() -> dict:
    """Status endpoint for the AI Career Onboarding module."""
    return {"module": "onboarding", "status": "operational", "phase": "Phase 4A"}


@router.post(
    "/start",
    response_model=StartOnboardingResponse,
    status_code=200,
    summary="Start or Resume Onboarding Interview",
    description="Initiates a new conversational discovery session or resumes an ongoing session. "
                "Returns the current question.",
)
async def start_onboarding(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> StartOnboardingResponse:
    return await _service.start_or_resume(current_user, db)


@router.get(
    "/session",
    response_model=OnboardingSessionResponse,
    summary="Get Onboarding Session Status",
    description="Returns the active onboarding state, current question, and turn counts.",
)
async def get_session_status(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> OnboardingSessionResponse:
    session = await _service.get_session_for_user(current_user.id, db)
    if not session:
        raise NotFoundException("OnboardingSession", identifier=str(current_user.id))

    if session.user_id != current_user.id and current_user.role != "admin":
        raise ForbiddenException("You do not have permission to view this onboarding session.")

    return OnboardingSessionResponse(
        session_id=session.id,
        status=session.status,
        current_question=session.current_question,
        current_question_category=session.current_question_category,
        turn_count=session.turn_count,
        started_at=session.created_at,
        last_activity_at=session.last_activity_at,
        completed_at=session.completed_at,
    )


@router.get(
    "/progress",
    response_model=OnboardingProgressResponse,
    summary="Get Onboarding Discovery Progress",
    description="Reports the proportion of career discovery categories covered versus remaining.",
)
async def get_onboarding_progress(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> OnboardingProgressResponse:
    return await _service.get_progress(current_user, db)


@router.post(
    "/respond",
    response_model=SubmitResponseResult,
    summary="Submit Response to Active Question",
    description="Submits the candidate's answer. The AI extracts facts, evaluates progress, "
                "and returns the next contextual question or triggers summary readiness.",
)
async def submit_response(
    request: SubmitResponseRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
    llm: LLMProvider = Depends(_get_llm),
) -> SubmitResponseResult:
    return await _service.submit_response(current_user, request.response_text, llm, db)


@router.get(
    "/history",
    response_model=List[ConversationTurnResponse],
    summary="Get Conversation History",
    description="Returns the complete chronological question-and-answer exchange for the session.",
)
async def get_conversation_history(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> List[ConversationTurnResponse]:
    return await _service.get_history(current_user, db)


@router.get(
    "/summary",
    response_model=OnboardingSummaryResponse,
    summary="Get Synthesized Career Summary",
    description="Returns the AI-synthesized career profile summary awaiting candidate review. "
                "Only accessible when session is in 'awaiting_confirmation' or 'completed'.",
)
async def get_onboarding_summary(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> OnboardingSummaryResponse:
    return await _service.get_summary(current_user, db)


@router.post(
    "/confirm",
    response_model=OnboardingSessionResponse,
    summary="Confirm Career Summary and Complete Onboarding",
    description="Confirms the career summary (with optional candidate edits), updates the CareerProfile, "
                "and marks onboarding complete in a transactional operation.",
)
async def confirm_onboarding_summary(
    request: ConfirmSummaryRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> OnboardingSessionResponse:
    return await _service.confirm_summary(current_user, request, db)
