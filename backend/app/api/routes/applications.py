"""
Application Package Preparation & Pipeline API Routes for CoachPath.
Implements Phase 11A intelligent application preparation, grounding-verified Q&A,
explicit human approval gate, external application handoff, and submission tracking.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import LLMProvider
from app.ai.factory import get_llm_provider
from app.api.dependencies import get_session, require_active_user
from app.models.auth import User
from app.schemas.applications import (
    ApplicationPackageApproveRequest,
    ApplicationPackageCreateRequest,
    ApplicationPackageHandoffResponse,
    ApplicationPackageListResponse,
    ApplicationPackageResponse,
    ApplicationPackageUpdateRequest,
    ApplicationSubmissionConfirmRequest,
    RecruiterOutreachCreateRequest,
    RecruiterOutreachListResponse,
    RecruiterOutreachResponse,
)
from app.services.application_preparation import application_preparation_service
from app.services.recruiter_outreach import recruiter_outreach_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/applications", tags=["Group 9: Applications"])


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


@router.get("", summary="Applications Module Status")
async def applications_status() -> Dict[str, str]:
    """Structural router status check for application pipeline & preparation."""
    return {"module": "applications", "status": "operational", "phase": "Phase 11A"}


@router.post(
    "/prepare",
    response_model=ApplicationPackageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Prepare Evidence-Grounded Application Package",
    description=(
        "Prepares a full job application package (cover note, common questions/answers, "
        "and links to tailored resume version) strictly grounded in candidate background."
    ),
)
@router.post(
    "/packages/prepare",
    response_model=ApplicationPackageResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def prepare_application_package(
    payload: ApplicationPackageCreateRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
    llm: LLMProvider = Depends(_get_llm),
) -> ApplicationPackageResponse:
    """Initiates generation of an evidence-grounded application package."""
    meta = _get_request_metadata(request)
    package = await application_preparation_service.prepare_package(
        user=current_user,
        request=payload,
        db=db,
        llm=llm,
        request_metadata=meta,
    )
    return ApplicationPackageResponse.model_validate(package)


@router.get(
    "/packages",
    response_model=ApplicationPackageListResponse,
    summary="List Application Packages",
    description="Retrieves candidate-owned application preparation packages with optional job and status filters.",
)
async def list_application_packages(
    job_id: Optional[uuid.UUID] = Query(None, description="Filter by target job ID"),
    status: Optional[str] = Query(None, description="Filter by package status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ApplicationPackageListResponse:
    """List application packages for the authenticated candidate."""
    return await application_preparation_service.list_packages(
        user=current_user,
        db=db,
        job_id=job_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/packages/{package_id}",
    response_model=ApplicationPackageResponse,
    summary="Get Application Package Details",
    description="Retrieves a specific application package owned by the candidate.",
)
async def get_application_package(
    package_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ApplicationPackageResponse:
    """Retrieves full application package by ID."""
    package = await application_preparation_service.get_package(
        package_id=package_id,
        user=current_user,
        db=db,
    )
    return ApplicationPackageResponse.model_validate(package)


@router.put(
    "/packages/{package_id}",
    response_model=ApplicationPackageResponse,
    summary="Update Application Package Content",
    description="Allows candidate to edit cover note, question answers, or candidate notes. Transitions to 'edited'.",
)
async def update_application_package(
    package_id: uuid.UUID,
    payload: ApplicationPackageUpdateRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ApplicationPackageResponse:
    """Updates application package content and resets approval status."""
    package = await application_preparation_service.update_package(
        package_id=package_id,
        user=current_user,
        request=payload,
        db=db,
    )
    return ApplicationPackageResponse.model_validate(package)


@router.post(
    "/packages/{package_id}/approve",
    response_model=ApplicationPackageResponse,
    summary="Approve Application Package",
    description="Explicit human approval gate: candidate certifies the package as complete and accurate.",
)
async def approve_application_package(
    package_id: uuid.UUID,
    payload: ApplicationPackageApproveRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ApplicationPackageResponse:
    """Certifies the package as approved by candidate."""
    meta = _get_request_metadata(request)
    package = await application_preparation_service.approve_package(
        package_id=package_id,
        user=current_user,
        request=payload,
        db=db,
        request_metadata=meta,
    )
    return ApplicationPackageResponse.model_validate(package)


@router.post(
    "/packages/{package_id}/handoff",
    response_model=ApplicationPackageHandoffResponse,
    summary="Initiate Application External Handoff",
    description="Generates exportable submission checklist, external employer URL, and clipboard payload for manual submission.",
)
async def handoff_application_package(
    package_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ApplicationPackageHandoffResponse:
    """Initiates external application handoff for candidate-driven submission."""
    meta = _get_request_metadata(request)
    return await application_preparation_service.initiate_handoff(
        package_id=package_id,
        user=current_user,
        db=db,
        request_metadata=meta,
    )


@router.post(
    "/packages/{package_id}/confirm-submission",
    response_model=ApplicationPackageResponse,
    summary="Confirm External Job Submission",
    description=(
        "Candidate explicitly confirms they completed the official application on the employer portal. "
        "Marks package as 'submitted' and transitions linked Application to 'applied'."
    ),
)
async def confirm_application_submission(
    package_id: uuid.UUID,
    payload: ApplicationSubmissionConfirmRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ApplicationPackageResponse:
    """Confirms official submission completion on employer portal."""
    meta = _get_request_metadata(request)
    package = await application_preparation_service.confirm_submission(
        package_id=package_id,
        user=current_user,
        request=payload,
        db=db,
        request_metadata=meta,
    )
    return ApplicationPackageResponse.model_validate(package)


@router.post(
    "/packages/{package_id}/outreach",
    response_model=RecruiterOutreachResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Recruiter Outreach Draft for Package",
    description="Creates a concise (<= 90 words) recruiter outreach draft tied to this application package.",
)
async def create_package_outreach(
    package_id: uuid.UUID,
    payload: RecruiterOutreachCreateRequest,
    request: Request,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
    llm: LLMProvider = Depends(_get_llm),
) -> RecruiterOutreachResponse:
    """Generates an outreach draft linked to the application package."""
    meta = _get_request_metadata(request)
    if not payload.application_package_id:
        payload.application_package_id = package_id
    draft = await recruiter_outreach_service.create_outreach_draft(
        user=current_user,
        request=payload,
        db=db,
        llm=llm,
        request_metadata=meta,
    )
    return RecruiterOutreachResponse.model_validate(draft)


@router.get(
    "/packages/{package_id}/outreach",
    response_model=RecruiterOutreachListResponse,
    summary="List Recruiter Outreach Drafts for Package",
    description="Retrieves all recruiter outreach drafts associated with this application package.",
)
async def list_package_outreach(
    package_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> RecruiterOutreachListResponse:
    """List outreach drafts linked to this application package."""
    return await recruiter_outreach_service.list_outreach_drafts(
        user=current_user,
        db=db,
        package_id=package_id,
    )
