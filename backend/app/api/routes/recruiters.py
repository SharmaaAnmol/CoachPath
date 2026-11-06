"""
Recruiter Outreach & Contact Gate API Routes for CoachPath.
Implements Phase 11A recruiter outreach generation (strict <= 90 words limit),
zero fabricated identities, explicit human approval gates, safe manual handoff
(mailto/profile/clipboard), and candidate-confirmed sent tracking.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import LLMProvider
from app.ai.factory import get_llm_provider
from app.api.dependencies import ai_rate_limit, get_session, require_active_user
from app.models.auth import User
from app.schemas.applications import (
    RecruiterOutreachApproveRequest,
    RecruiterOutreachCreateRequest,
    RecruiterOutreachHandoffResponse,
    RecruiterOutreachListResponse,
    RecruiterOutreachResponse,
    RecruiterOutreachSentConfirmRequest,
    RecruiterOutreachUpdateRequest,
)
from app.services.recruiter_outreach import recruiter_outreach_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recruiters", tags=["Group 10: Recruiters"])


def _get_llm() -> LLMProvider:
    """Dependency injection for the configured LLM provider."""
    return get_llm_provider()


def _get_request_metadata(request: Request) -> Dict[str, Any]:
    """Extract client IP hash and User-Agent header for immutable audit logging."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    client_ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()
    user_agent = request.headers.get("user-agent", "CoachPath API")
    return {
        "client_ip_hash": client_ip_hash,
        "user_agent": user_agent,
    }


@router.get("", summary="Recruiters Module Status")
async def recruiters_status() -> Dict[str, str]:
    """Structural router status check for recruiter discovery and manual dispatch."""
    return {"module": "recruiters", "status": "operational", "phase": "Phase 11A"}


@router.post(
    "/outreach",
    dependencies=[Depends(ai_rate_limit)],
    response_model=RecruiterOutreachResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Recruiter Outreach Draft",
    description=(
        "Drafts a personalized recruiter message strictly constrained to <= 90 words. "
        "Requires real candidate experience and genuine job context. Maximum 3 drafts per application."
    ),
)
async def create_recruiter_outreach(
    payload: RecruiterOutreachCreateRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
    llm: LLMProvider = Depends(_get_llm),
) -> RecruiterOutreachResponse:
    """Generates a bounded recruiter outreach draft."""
    meta = _get_request_metadata(request)
    draft = await recruiter_outreach_service.create_outreach_draft(
        user=current_user,
        request=payload,
        db=db,
        llm=llm,
        request_metadata=meta,
    )
    return RecruiterOutreachResponse.model_validate(draft)


@router.get(
    "/outreach",
    response_model=RecruiterOutreachListResponse,
    summary="List Recruiter Outreach Drafts",
    description="Lists candidate's recruiter outreach drafts with optional application, package, or status filters.",
)
async def list_recruiter_outreach(
    package_id: Optional[uuid.UUID] = Query(None, description="Filter by application package ID"),
    application_id: Optional[uuid.UUID] = Query(None, description="Filter by application ID"),
    job_id: Optional[uuid.UUID] = Query(None, description="Filter by job ID"),
    status: Optional[str] = Query(None, description="Filter by outreach status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RecruiterOutreachListResponse:
    """List outreach drafts owned by candidate."""
    return await recruiter_outreach_service.list_outreach_drafts(
        user=current_user,
        db=db,
        package_id=package_id,
        application_id=application_id,
        job_id=job_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/outreach/{draft_id}",
    response_model=RecruiterOutreachResponse,
    summary="Get Recruiter Outreach Draft Details",
    description="Retrieves a single recruiter outreach draft by its UUID.",
)
async def get_recruiter_outreach(
    draft_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RecruiterOutreachResponse:
    """Retrieve full outreach draft details."""
    draft = await recruiter_outreach_service.get_outreach_draft(
        draft_id=draft_id,
        user=current_user,
        db=db,
    )
    return RecruiterOutreachResponse.model_validate(draft)


@router.put(
    "/outreach/{draft_id}",
    response_model=RecruiterOutreachResponse,
    summary="Update Recruiter Outreach Draft Content",
    description="Allows candidate to edit message text and recipient info. Enforces strict <= 90 words limit.",
)
async def update_recruiter_outreach(
    draft_id: uuid.UUID,
    payload: RecruiterOutreachUpdateRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RecruiterOutreachResponse:
    """Updates draft text and resets approval status."""
    draft = await recruiter_outreach_service.update_outreach_draft(
        draft_id=draft_id,
        user=current_user,
        request=payload,
        db=db,
    )
    return RecruiterOutreachResponse.model_validate(draft)


@router.post(
    "/outreach/{draft_id}/approve",
    response_model=RecruiterOutreachResponse,
    summary="Approve Recruiter Outreach Draft",
    description="Explicit human approval gate: certifies the draft as reviewed and approved by candidate.",
)
async def approve_recruiter_outreach(
    draft_id: uuid.UUID,
    payload: RecruiterOutreachApproveRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RecruiterOutreachResponse:
    """Certifies the draft as approved by candidate."""
    meta = _get_request_metadata(request)
    draft = await recruiter_outreach_service.approve_outreach_draft(
        draft_id=draft_id,
        user=current_user,
        request=payload,
        db=db,
        request_metadata=meta,
    )
    return RecruiterOutreachResponse.model_validate(draft)


@router.post(
    "/outreach/{draft_id}/handoff",
    response_model=RecruiterOutreachHandoffResponse,
    summary="Initiate Recruiter Outreach Handoff",
    description=(
        "Prepares safe manual handoff (mailto URI, recruiter profile URL, or copy-ready payload). "
        "Requires explicit candidate approval prior to handoff. Does NOT automatically dispatch messages."
    ),
)
async def handoff_recruiter_outreach(
    draft_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RecruiterOutreachHandoffResponse:
    """Initiates manual outreach handoff for candidate-driven communication."""
    meta = _get_request_metadata(request)
    return await recruiter_outreach_service.initiate_outreach_handoff(
        draft_id=draft_id,
        user=current_user,
        db=db,
        request_metadata=meta,
    )


@router.post(
    "/outreach/{draft_id}/confirm-sent",
    response_model=RecruiterOutreachResponse,
    summary="Confirm External Recruiter Message Sent",
    description="Candidate confirms they manually sent the message via email or social platform.",
)
async def confirm_recruiter_outreach_sent(
    draft_id: uuid.UUID,
    payload: RecruiterOutreachSentConfirmRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RecruiterOutreachResponse:
    """Confirms candidate dispatched the message externally."""
    meta = _get_request_metadata(request)
    draft = await recruiter_outreach_service.confirm_outreach_sent(
        draft_id=draft_id,
        user=current_user,
        request=payload,
        db=db,
        request_metadata=meta,
    )
    return RecruiterOutreachResponse.model_validate(draft)


@router.post(
    "/outreach/{draft_id}/cancel",
    response_model=RecruiterOutreachResponse,
    summary="Cancel Recruiter Outreach Draft",
    description="Candidate cancels or discards an outreach draft.",
)
async def cancel_recruiter_outreach(
    draft_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RecruiterOutreachResponse:
    """Cancels draft and marks it as cancelled."""
    draft = await recruiter_outreach_service.cancel_outreach_draft(
        draft_id=draft_id,
        user=current_user,
        db=db,
    )
    return RecruiterOutreachResponse.model_validate(draft)


@router.delete(
    "/outreach/{draft_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Recruiter Outreach Draft",
    description="Permanently deletes an unsubmitted recruiter outreach draft.",
)
async def delete_recruiter_outreach(
    draft_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> Response:
    """Deletes the outreach draft record."""
    await recruiter_outreach_service.delete_outreach_draft(
        draft_id=draft_id,
        user=current_user,
        db=db,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
