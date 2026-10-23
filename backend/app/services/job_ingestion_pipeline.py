"""
Job Ingestion Pipeline Engine for CoachPath.
Coordinates raw data fetching, validation, normalization, deduplication,
canonical skill extraction, atomic PostgreSQL persistence, and audit run logging.
"""

from __future__ import annotations

import decimal
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.jobs import Job, JobIngestionRun, JobSkill, JobSource
from app.models.skills import Skill
from app.schemas.jobs import (
    JobImportRequest,
    JobIngestionSummary,
    JobResponse,
    JobSkillItem,
)
from app.services.job_description_parser import (
    extract_sections,
    extract_skills_deterministic,
)
from app.services.job_normalization import (
    classify_canonical_role,
    classify_experience_level,
    classify_remote_type,
    clean_html,
    compute_data_quality_score,
    compute_deduplication_hash,
    normalize_company_name,
    normalize_string,
    parse_salary_range,
)
from app.services.job_source_adapters import (
    BaseJobSourceAdapter,
    JobSourceAdapterFactory,
    RawJobListing,
)

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobIngestionPipelineService:
    """Core service executing job ingestion runs and manual imports."""

    async def get_or_create_source(
        self,
        source_name: str,
        provider_type: str,
        db: AsyncSession,
        base_url: Optional[str] = None,
    ) -> JobSource:
        """Finds or creates a registered JobSource record."""
        stmt = select(JobSource).where(JobSource.name == source_name)
        source = await db.scalar(stmt)
        if not source:
            source = JobSource(
                name=source_name,
                provider_type=provider_type,
                base_url=base_url,
                is_active=True,
                rate_limit_per_minute=settings.JOB_INGESTION_RATE_LIMIT_PER_MINUTE,
                config_metadata={},
            )
            db.add(source)
            await db.flush()
        return source

    async def run_ingestion(
        self,
        source_name: str,
        batch_size: int = 50,
        page: int = 1,
        db: Optional[AsyncSession] = None,
        adapter_override: Optional[BaseJobSourceAdapter] = None,
    ) -> JobIngestionSummary:
        """
        Executes an end-to-end ingestion run for the specified source.
        Atomic, idempotent, and resilient against single-item errors.
        """
        if db is None:
            raise ValueError("Database session is required for ingestion run.")

        adapter = adapter_override or JobSourceAdapterFactory.get_adapter(source_name)
        source_record = await self.get_or_create_source(
            source_name=adapter.source_name,
            provider_type=adapter.provider_type,
            db=db,
        )

        run = JobIngestionRun(
            source_id=source_record.id,
            source_name=adapter.source_name,
            status="running",
            items_fetched=0,
            items_inserted=0,
            items_updated=0,
            items_skipped=0,
            items_errored=0,
            error_log=[],
            started_at=_utc_now(),
        )
        db.add(run)
        await db.flush()

        # Fetch batch from provider
        try:
            raw_listings = await adapter.fetch_jobs(batch_size=batch_size, page=page)
            run.items_fetched = len(raw_listings)
        except Exception as exc:
            logger.error("Failed to fetch jobs from provider %s: %s", source_name, exc)
            run.status = "failed"
            run.finished_at = _utc_now()
            run.error_log = [{"error": str(exc), "stage": "fetch"}]
            await db.commit()
            return JobIngestionSummary.model_validate(run)

        # Cache valid canonical skills from DB to avoid FK violations
        skills_stmt = select(Skill.id)
        valid_skill_ids = set((await db.scalars(skills_stmt)).all())

        # Process each raw listing
        for raw in raw_listings:
            try:
                inserted, updated, skipped = await self._process_single_listing(
                    raw=raw,
                    valid_skill_ids=valid_skill_ids,
                    db=db,
                )
                if inserted:
                    run.items_inserted += 1
                elif updated:
                    run.items_updated += 1
                elif skipped:
                    run.items_skipped += 1
            except Exception as exc:
                logger.warning("Error processing listing '%s': %s", raw.title, exc)
                run.items_errored += 1
                err_entry = {
                    "title": raw.title,
                    "company": raw.company_name,
                    "error": str(exc),
                }
                current_log = list(run.error_log or [])
                current_log.append(err_entry)
                run.error_log = current_log

        # Determine run status
        if run.items_errored == 0:
            run.status = "completed"
        elif run.items_inserted + run.items_updated > 0:
            run.status = "partial"
        else:
            run.status = "failed"

        run.finished_at = _utc_now()
        source_record.last_ingested_at = _utc_now()

        await db.commit()
        await db.refresh(run)
        return JobIngestionSummary.model_validate(run)

    async def import_single_job(
        self,
        request: JobImportRequest,
        db: AsyncSession,
    ) -> JobResponse:
        """
        Manually imports and immediately processes a candidate-submitted job description.
        Returns the fully parsed and persisted JobResponse.
        """
        source_record = await self.get_or_create_source(
            source_name="manual",
            provider_type="manual",
            db=db,
        )

        adapter = JobSourceAdapterFactory.get_adapter("manual")
        raw_listings = await adapter.fetch_jobs(import_request=request)
        if not raw_listings:
            raise ValueError("Failed to prepare manual job listing.")

        raw = raw_listings[0]

        skills_stmt = select(Skill.id)
        valid_skill_ids = set((await db.scalars(skills_stmt)).all())

        await self._process_single_listing(
            raw=raw,
            valid_skill_ids=valid_skill_ids,
            db=db,
        )
        await db.commit()

        # Query the newly saved or updated job with skills loaded
        hash_id = compute_deduplication_hash(raw.company_name, raw.title, raw.location)
        stmt = (
            select(Job)
            .options(selectinload(Job.skills).selectinload(JobSkill.skill))
            .where(
                Job.source == "manual",
                Job.company_name == raw.company_name.strip(),
                Job.title == raw.title.strip(),
            )
            .order_by(Job.created_at.desc())
        )
        persisted = await db.scalar(stmt)
        if not persisted:
            raise RuntimeError("Job import failed to persist.")

        return self._format_job_response(persisted)

    async def _process_single_listing(
        self,
        raw: RawJobListing,
        valid_skill_ids: Set[str],
        db: AsyncSession,
    ) -> Tuple[bool, bool, bool]:
        """
        Internal processing step: normalizes, deduplicates, extracts skills, and upserts.
        Returns (is_inserted, is_updated, is_skipped).
        """
        # 1. Basic validation
        title = raw.title.strip()
        company = raw.company_name.strip()
        description = clean_html(raw.description_text)
        location = raw.location.strip() or "Remote"

        if len(title) < 2 or len(company) < 2 or len(description) < 20:
            return False, False, True  # Skipped due to quality threshold

        # 2. Normalization
        canonical_role = classify_canonical_role(title, description, hint_role=raw.role_id)
        remote_type = classify_remote_type(location, description, hint_remote=raw.remote_type)
        experience_level = classify_experience_level(title, description, hint_level=raw.experience_level)
        min_salary, max_salary = parse_salary_range(raw.min_salary, raw.max_salary, description)

        responsibilities, required_quals, preferred_quals = extract_sections(description)
        extracted_skills = extract_skills_deterministic(f"{title}\n{description}")

        # Compute quality score
        quality_score = compute_data_quality_score(
            title=title,
            description=description,
            company=company,
            location=location,
            skill_count=len(extracted_skills),
            has_salary=min_salary is not None,
        )

        # 3. Deduplication search
        existing_job: Optional[Job] = None
        if raw.external_id:
            stmt = (
                select(Job)
                .options(selectinload(Job.skills))
                .where(Job.source == raw.source, Job.external_id == raw.external_id)
            )
            existing_job = await db.scalar(stmt)

        if not existing_job:
            # Fallback identity matching on normalized company, title, and location
            stmt = (
                select(Job)
                .options(selectinload(Job.skills))
                .where(
                    Job.company_name == company,
                    Job.title == title,
                    Job.location == location,
                )
            )
            existing_job = await db.scalar(stmt)

        now = _utc_now()

        # 4. Upsert Logic
        if existing_job:
            # Refresh existing record
            existing_job.last_verified_at = now
            existing_job.freshness_status = "active"
            existing_job.is_active = True
            existing_job.description_markdown = description
            existing_job.responsibilities = responsibilities
            existing_job.required_qualifications = required_quals
            existing_job.preferred_qualifications = preferred_quals
            existing_job.data_quality_score = quality_score
            if min_salary:
                existing_job.min_salary = min_salary
            if max_salary:
                existing_job.max_salary = max_salary
            if raw.source_url:
                existing_job.source_url = raw.source_url

            # Refresh skills
            await self._sync_job_skills(
                job=existing_job,
                extracted_skills=extracted_skills,
                valid_skill_ids=valid_skill_ids,
                db=db,
            )
            await db.flush()
            return False, True, False

        else:
            # Insert new Job
            new_job = Job(
                external_id=raw.external_id,
                source=raw.source,
                source_url=raw.source_url,
                title=title,
                normalized_title=normalize_string(title),
                company_name=company,
                location=location,
                normalized_location=normalize_string(location),
                remote_type=remote_type,
                employment_type=raw.employment_type or "full_time",
                role_id=canonical_role,
                experience_level=experience_level,
                min_salary=min_salary,
                max_salary=max_salary,
                currency=raw.currency or "USD",
                description_markdown=description,
                responsibilities=responsibilities,
                required_qualifications=required_quals,
                preferred_qualifications=preferred_quals,
                application_url=raw.application_url,
                embedding=None,
                is_active=True,
                freshness_status="active",
                last_verified_at=now,
                raw_source_payload=raw.raw_payload or {},
                data_quality_score=quality_score,
                posted_at=raw.posted_at or now,
                created_at=now,
            )
            db.add(new_job)
            await db.flush()

            # Attach skills
            await self._sync_job_skills(
                job=new_job,
                extracted_skills=extracted_skills,
                valid_skill_ids=valid_skill_ids,
                db=db,
            )
            await db.flush()
            return True, False, False

    async def _sync_job_skills(
        self,
        job: Job,
        extracted_skills: List[Dict[str, Any]],
        valid_skill_ids: Set[str],
        db: AsyncSession,
    ) -> None:
        """Attaches validated canonical skills to the job record."""
        # Remove existing skills directly via execute to prevent lazy loading
        await db.execute(delete(JobSkill).where(JobSkill.job_id == job.id))

        # Add new matched skills that exist in the database catalog
        seen_skill_ids: Set[str] = set()
        for item in extracted_skills:
            s_id = item["skill_id"]
            if s_id in valid_skill_ids and s_id not in seen_skill_ids:
                seen_skill_ids.add(s_id)
                js = JobSkill(
                    job_id=job.id,
                    skill_id=s_id,
                    is_mandatory=item.get("is_mandatory", True),
                    confidence_score=decimal.Decimal(str(item.get("confidence_score", 1.0))),
                    source_phrase=item.get("source_phrase"),
                )
                db.add(js)

    def _format_job_response(self, job: Job) -> JobResponse:
        """Converts Job model to JobResponse schema."""
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
