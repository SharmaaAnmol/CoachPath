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
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
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
    ResumeUploadResponse,
    RetryParsingResponse,
)
from app.services.resume import resume_service

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
