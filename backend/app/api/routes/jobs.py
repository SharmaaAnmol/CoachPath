"""
Job Market Intelligence and Ingestion API Router for CoachPath.
Provides endpoints for catalog search, job details, candidate job imports,
pipeline ingestion runs, and deterministic market intelligence indicators.
"""

from __future__ import annotations

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_session, require_active_user
from app.core.exceptions import NotFoundException, ValidationException
from app.models.auth import User
from app.models.jobs import Job, JobIngestionRun, JobSkill
from app.schemas.jobs import (
    JobImportRequest,
    JobIngestRequest,
    JobIngestionSummary,
    JobResponse,
    JobSearchResponse,
    JobSkillItem,
    MarketIntelligenceResponse,
)
from app.services.job_ingestion_pipeline import JobIngestionPipelineService
from app.services.market_intelligence import MarketIntelligenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Group 8: Jobs"])

_pipeline_service = JobIngestionPipelineService()
_market_service = MarketIntelligenceService()


def _format_job(job: Job) -> JobResponse:
    """Helper to convert Job ORM entity into JobResponse."""
    skill_items: List[JobSkillItem] = []
    for js in job.skills or []:
        name = js.skill.name if js.skill else js.skill_id.replace("-", " ").title()
        cat = js.skill.category if js.skill else "technical"
        skill_items.append(
            JobSkillItem(
                skill_id=js.skill_id,
                name=name,
                category=cat,
                is_mandatory=js.is_mandatory,
                confidence_score=float(js.confidence_score) if js.confidence_score else 1.0,
                source_phrase=js.source_phrase,
            )
        )

    return JobResponse(
        id=job.id,
        external_id=job.external_id,
        source=job.source,
        source_url=job.source_url,
        title=job.title,
        normalized_title=job.normalized_title,
        company_name=job.company_name,
        location=job.location,
        normalized_location=job.normalized_location,
        remote_type=job.remote_type,
        employment_type=job.employment_type or "full_time",
        role_id=job.role_id,
        experience_level=job.experience_level,
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        currency=job.currency,
        description_markdown=job.description_markdown,
        responsibilities=job.responsibilities or [],
        required_qualifications=job.required_qualifications or [],
        preferred_qualifications=job.preferred_qualifications or [],
        application_url=job.application_url,
        is_active=job.is_active,
        freshness_status=job.freshness_status,
        last_verified_at=job.last_verified_at,
        data_quality_score=float(job.data_quality_score) if job.data_quality_score else None,
        posted_at=job.posted_at,
        created_at=job.created_at,
        skills=skill_items,
    )


# ─────────────────────────────────────────────
# 1. Market Intelligence Endpoint
# ─────────────────────────────────────────────

@router.get(
    "/market-intelligence",
    response_model=MarketIntelligenceResponse,
    summary="Get Job Market Intelligence Overview",
    description="Returns aggregated distributions of in-demand skills, workplace flexibility, and salary metrics.",
)
async def get_market_intelligence(
    role_id: Optional[str] = Query(None, description="Filter metrics by benchmark role ID"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> MarketIntelligenceResponse:
    return await _market_service.get_market_overview(db=db, role_id_filter=role_id)


# ─────────────────────────────────────────────
# 2. Ingestion Runs Audit Endpoint
# ─────────────────────────────────────────────

@router.get(
    "/ingestion-runs",
    response_model=List[JobIngestionSummary],
    summary="Get Recent Ingestion Runs",
    description="Returns audit history of pipeline execution runs and metrics.",
)
async def get_ingestion_runs(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> List[JobIngestionSummary]:
    stmt = (
        select(JobIngestionRun)
        .order_by(JobIngestionRun.started_at.desc())
        .limit(limit)
    )
    runs = (await db.scalars(stmt)).all()
    return [JobIngestionSummary.model_validate(r) for r in runs]


# ─────────────────────────────────────────────
# 3. Trigger Ingestion Run Endpoint
# ─────────────────────────────────────────────

@router.post(
    "/ingest",
    response_model=JobIngestionSummary,
    status_code=status.HTTP_200_OK,
    summary="Trigger Job Ingestion Pipeline",
    description="Initiates an ingestion batch from a permitted job data source ('seed', 'arbeitnow', 'mock').",
)
async def trigger_ingestion(
    request: JobIngestRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobIngestionSummary:
    try:
        summary = await _pipeline_service.run_ingestion(
            source_name=request.source,
            batch_size=request.batch_size,
            db=db,
        )
        return summary
    except Exception as exc:
        logger.error("Ingestion failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {exc}",
        )


# ─────────────────────────────────────────────
# 4. Manual Candidate Job Import Endpoint
# ─────────────────────────────────────────────

@router.post(
    "/import",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import Job Description Manually",
    description="Submits a target job description to be validated, normalized, parsed for skills, and saved.",
)
async def import_job(
    request: JobImportRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobResponse:
    try:
        job_response = await _pipeline_service.import_single_job(
            request=request,
            db=db,
        )
        return job_response
    except ValueError as ve:
        raise ValidationException(str(ve))
    except Exception as exc:
        logger.error("Manual job import failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process manual job import: {exc}",
        )


# ─────────────────────────────────────────────
# 5. Search / List Catalog Jobs Endpoint
# ─────────────────────────────────────────────

@router.get(
    "",
    response_model=JobSearchResponse,
    summary="Search Job Opportunities",
    description="Queries curated jobs with multi-facet filters: role, skills, remote flexibility, salary, and keywords.",
)
async def search_jobs(
    role_id: Optional[str] = Query(None, description="Canonical role filter"),
    remote_type: Optional[str] = Query(None, description="'remote', 'hybrid', or 'onsite'"),
    experience_level: Optional[str] = Query(None, description="'internship', 'entry_level', 'junior', 'mid'"),
    keyword: Optional[str] = Query(None, description="Search in title or company"),
    freshness_status: Optional[str] = Query(None, description="'active', 'needs_refresh', 'expired', 'closed'"),
    min_salary: Optional[int] = Query(None, ge=0, description="Minimum annualized salary"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobSearchResponse:
    criteria = [Job.is_active == True]

    if role_id:
        criteria.append(Job.role_id == role_id)
    if remote_type:
        criteria.append(Job.remote_type == remote_type)
    if experience_level:
        criteria.append(Job.experience_level == experience_level)
    if freshness_status:
        criteria.append(Job.freshness_status == freshness_status)
    if min_salary is not None:
        criteria.append(
            or_(
                Job.min_salary >= min_salary,
                Job.max_salary >= min_salary,
            )
        )
    if keyword:
        pattern = f"%{keyword.strip().lower()}%"
        criteria.append(
            or_(
                func.lower(Job.title).like(pattern),
                func.lower(Job.company_name).like(pattern),
                func.lower(Job.location).like(pattern),
            )
        )

    # Count total matching
    count_stmt = select(func.count(Job.id)).where(*criteria)
    total: int = (await db.scalar(count_stmt)) or 0

    # Paginated results with skills eagerly loaded
    offset = (page - 1) * page_size
    stmt = (
        select(Job)
        .options(selectinload(Job.skills).selectinload(JobSkill.skill))
        .where(*criteria)
        .order_by(Job.posted_at.desc(), Job.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    jobs = (await db.scalars(stmt)).all()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return JobSearchResponse(
        items=[_format_job(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ─────────────────────────────────────────────
# 6. Single Job Details Endpoint
# ─────────────────────────────────────────────

@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get Job Details",
    description="Retrieves a specific curated job opportunity by its UUID.",
)
async def get_job_by_id(
    job_id: uuid.UUID,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_session),
) -> JobResponse:
    stmt = (
        select(Job)
        .options(selectinload(Job.skills).selectinload(JobSkill.skill))
        .where(Job.id == job_id)
    )
    job = await db.scalar(stmt)
    if not job:
        raise NotFoundException("Job")

    return _format_job(job)
