"""
Resume Ingestion and Parsing API Routes for CoachPath.
Implements secure document upload, listing, parsed draft preview, retry,
download, and deletion matching /docs/api-specification.md Group 5.

All endpoints require authentication and enforce strict user ownership.
Profile merging is explicitly deferred to candidate confirmation in Phase 5B.
"""
from __future__ import annotations

import logging
import uuid
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import LLMProvider
from app.ai.factory import get_llm_provider
from app.api.dependencies import get_session, require_active_user
from app.models.auth import User
from app.schemas.resume import (
    ParsedResumeResponse,
    ResumeConfirmationRequest,
    ResumeConfirmationResponse,
    ResumeDetailResponse,
    ResumeListItem,
    ResumeListResponse,
    ResumeTailorRequest,
    ResumeUploadResponse,
    RetryParsingResponse,
    TailoredResumeAnalysisResponse,
    TailoredResumeApprovalRequest,
    TailoredResumeDiffResponse,
    TailoredResumeListResponse,
    TailoredResumeResponse,
    TailoredResumeUpdateRequest,
)
from app.services.resume import resume_service
from app.services.resume_tailoring import resume_tailoring_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Group 5: Resume Ingestion & Parsing"])


def _get_llm() -> LLMProvider:
    """Dependency injection for the configured LLM provider."""
    return get_llm_provider()


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and Parse Resume Document",
    description="Uploads a PDF or DOCX resume document (max 10MB). Extracts text and parses career entities into a draft.",
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume document file (PDF or DOCX, max 10MB)"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
    llm: LLMProvider = Depends(_get_llm),
) -> ResumeUploadResponse:
    """Uploads and initiates parsing on candidate resume document."""
    resume = await resume_service.upload_and_parse(
        user=current_user,
        file=file,
        db=db,
        llm=llm,
    )
    message = (
        "Resume parsed successfully. Review extracted data before approving."
        if resume.status == "parsed"
        else f"Resume uploaded but parsing failed: {resume.parsing_error}"
    )
    return ResumeUploadResponse(
        resume_id=resume.id,
        file_name=resume.file_name,
        file_size_bytes=resume.file_size_bytes,
        mime_type=resume.mime_type,
        status=resume.status,
        message=message,
        created_at=resume.created_at,
    )


@router.get(
    "",
    response_model=ResumeListResponse,
    summary="List Uploaded Resumes",
    description="Returns all uploaded resumes belonging to the authenticated candidate.",
)
async def list_resumes(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ResumeListResponse:
    """Lists resumes owned by the authenticated candidate."""
    resumes = await resume_service.list_user_resumes(
        user_id=current_user.id,
        db=db,
    )
    items = [
        ResumeListItem(
            id=r.id,
            file_name=r.file_name,
            file_size_bytes=r.file_size_bytes,
            mime_type=r.mime_type,
            status=r.status,
            is_primary=r.is_primary,
            parsing_error=r.parsing_error,
            parsing_error_category=r.parsing_error_category,
            parsed_at=r.parsed_at,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in resumes
    ]
    return ResumeListResponse(resumes=items, total=len(items))


# ─── Phase 10A: Tailored Resume Versions Endpoints ───────────────────

@router.get(
    "/versions",
    response_model=TailoredResumeListResponse,
    summary="List Tailored Resume Versions",
    description="Returns all tailored resume versions belonging to the authenticated candidate with optional filtering.",
)
async def list_tailored_versions(
    resume_id: Optional[uuid.UUID] = Query(None, description="Filter by source resume UUID"),
    job_id: Optional[uuid.UUID] = Query(None, description="Filter by target job UUID"),
    status: Optional[str] = Query(None, pattern="^(draft|approved|archived)$", description="Filter by version status"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> TailoredResumeListResponse:
    return await resume_tailoring_service.list_tailored_versions(
        user=current_user,
        db=db,
        resume_id=resume_id,
        job_id=job_id,
        status_filter=status,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/versions/{version_id}",
    response_model=TailoredResumeResponse,
    summary="Get Tailored Resume Version",
    description="Retrieves a specific tailored resume draft or approved version by its UUID.",
)
async def get_tailored_version(
    version_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> TailoredResumeResponse:
    return await resume_tailoring_service.get_tailored_version(
        user=current_user,
        version_id=version_id,
        db=db,
    )


@router.put(
    "/versions/{version_id}",
    response_model=TailoredResumeResponse,
    summary="Update Editable Tailored Resume Draft",
    description="Updates user-modified content or notes on a tailored version. Only allowed while status is 'draft'.",
)
async def update_tailored_version(
    version_id: uuid.UUID,
    request: TailoredResumeUpdateRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> TailoredResumeResponse:
    return await resume_tailoring_service.update_tailored_version(
        user=current_user,
        version_id=version_id,
        request=request,
        db=db,
    )


@router.delete(
    "/versions/{version_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Tailored Resume Version",
    description="Permanently deletes a tailored resume version under strict ownership check.",
)
async def delete_tailored_version(
    version_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> Response:
    await resume_tailoring_service.delete_tailored_version(
        user=current_user,
        version_id=version_id,
        db=db,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/versions/{version_id}/approve",
    response_model=TailoredResumeResponse,
    summary="Approve Tailored Resume Version",
    description="Explicit human approval gate: certifies the tailored draft as candidate-approved.",
)
async def approve_tailored_version(
    version_id: uuid.UUID,
    request: TailoredResumeApprovalRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> TailoredResumeResponse:
    return await resume_tailoring_service.approve_tailored_version(
        user=current_user,
        version_id=version_id,
        request=request,
        db=db,
    )


@router.get(
    "/versions/{version_id}/diff",
    response_model=TailoredResumeDiffResponse,
    summary="Get Tailored Resume Visual Diff",
    description="Retrieves structured before-and-after change list for visual review.",
)
async def get_tailored_diff(
    version_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> TailoredResumeDiffResponse:
    return await resume_tailoring_service.get_diff(
        user=current_user,
        version_id=version_id,
        db=db,
    )


@router.get(
    "/versions/{version_id}/analysis",
    response_model=TailoredResumeAnalysisResponse,
    summary="Get Resume Optimization Analysis",
    description="Retrieves quantitative optimization analysis, keyword coverage, and evidence gaps.",
)
async def get_tailored_analysis(
    version_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> TailoredResumeAnalysisResponse:
    return await resume_tailoring_service.get_analysis(
        user=current_user,
        version_id=version_id,
        db=db,
    )


# ─── Source Resume Document Endpoints ─────────────────────────────────

@router.get(
    "/{resume_id}",
    response_model=ResumeDetailResponse,
    summary="Get Resume Metadata",
    description="Retrieves metadata, file properties, and processing status for a specific resume.",
)
async def get_resume_detail(
    resume_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ResumeDetailResponse:
    """Retrieves resume metadata by ID."""
    resume = await resume_service.get_user_resume(
        resume_id=resume_id,
        user=current_user,
        db=db,
    )
    return ResumeDetailResponse(
        id=resume.id,
        user_id=resume.user_id,
        file_name=resume.file_name,
        file_size_bytes=resume.file_size_bytes,
        mime_type=resume.mime_type,
        status=resume.status,
        is_primary=resume.is_primary,
        parsing_error=resume.parsing_error,
        parsing_error_category=resume.parsing_error_category,
        parsed_at=resume.parsed_at,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


@router.get(
    "/{resume_id}/parsed",
    response_model=ParsedResumeResponse,
    summary="Get Parsed Resume Draft",
    description="Retrieves the structured parsed draft awaiting candidate verification and review in Phase 5B.",
)
async def get_parsed_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ParsedResumeResponse:
    """Retrieves structured parsed draft for verification."""
    return await resume_service.get_parsed_draft(
        resume_id=resume_id,
        user=current_user,
        db=db,
    )


@router.post(
    "/{resume_id}/retry",
    response_model=RetryParsingResponse,
    summary="Retry Resume Parsing",
    description="Re-attempts text extraction and AI parsing for an existing uploaded resume document.",
)
async def retry_resume_parsing(
    resume_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
    llm: LLMProvider = Depends(_get_llm),
) -> RetryParsingResponse:
    """Re-attempts text extraction and parsing for a failed document."""
    resume = await resume_service.retry_parsing(
        resume_id=resume_id,
        user=current_user,
        db=db,
        llm=llm,
    )
    message = (
        "Resume parsing succeeded."
        if resume.status == "parsed"
        else f"Parsing retry finished with status: {resume.status}"
    )
    return RetryParsingResponse(
        resume_id=resume.id,
        status=resume.status,
        message=message,
    )


@router.get(
    "/{resume_id}/download",
    summary="Download Original Resume Document",
    description="Streams the original uploaded PDF or DOCX document securely to the owning candidate.",
)
async def download_resume_document(
    resume_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> Response:
    """Streams the original uploaded document for download."""
    content, filename, mime_type = await resume_service.get_document_file(
        resume_id=resume_id,
        user=current_user,
        db=db,
    )
    # Sanitize filename for HTTP header
    safe_filename = filename.replace('"', '\\"')
    return Response(
        content=content,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Content-Length": str(len(content)),
        },
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Resume Document",
    description="Deletes a resume record, its parsed draft, and the physical stored document.",
)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> Response:
    """Deletes resume and its physical file."""
    await resume_service.delete_resume(
        resume_id=resume_id,
        user=current_user,
        db=db,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{resume_id}/confirm",
    response_model=ResumeConfirmationResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm Extracted Resume and Merge into Profile",
    description="Explicit human approval gate: merges approved and corrected resume entities into the canonical career profile.",
)
async def confirm_resume(
    resume_id: uuid.UUID,
    request: ResumeConfirmationRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> ResumeConfirmationResponse:
    """Explicitly approves extracted entities and merges them into CareerProfile."""
    return await resume_service.confirm_and_merge_profile(
        resume_id=resume_id,
        request=request,
        user=current_user,
        db=db,
    )


@router.post(
    "/{resume_id}/tailor",
    response_model=TailoredResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Tailored Resume Draft",
    description="Generates an evidence-grounded tailored resume draft aligned with the target job posting.",
)
async def tailor_resume(
    resume_id: uuid.UUID,
    request: ResumeTailorRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
    llm: LLMProvider = Depends(_get_llm),
) -> TailoredResumeResponse:
    """Generates a job-specific tailored resume draft without mutating the source resume."""
    return await resume_tailoring_service.tailor_resume(
        user=current_user,
        resume_id=resume_id,
        request=request,
        db=db,
        llm=llm,
    )
