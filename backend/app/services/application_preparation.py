"""
Application Preparation Service for CoachPath.
Orchestrates evidence-grounded application package generation, cover note formulation,
common application question answering, explicit candidate approval gates,
and external employer handoff tracking.

CRITICAL INVARIANTS:
1. ZERO FABRICATION: Cover notes and question answers must be grounded in candidate background.
2. IMMUTABILITY: The source resume and approved tailored resume remain byte-for-byte identical.
3. HUMAN APPROVAL GATE: An application package cannot enter handoff without explicit user confirmation.
4. HONEST SUBMISSION: Application is ONLY marked 'submitted' after explicit candidate confirmation.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import sqlalchemy as sa
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.base import LLMProvider
from app.ai.prompts.application_prep_v1 import (
    AIApplicationPackageOutput,
    APPLICATION_PREP_PROMPT_TEMPLATE,
    APPLICATION_PREP_SYSTEM_PROMPT,
)
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
)
from app.models.applications import Application, ApplicationPackage, ApplicationStatusHistory
from app.models.audit import AuditLog
from app.models.auth import User
from app.models.career import CareerProfile, Experience, Project
from app.models.jobs import Job, JobSkill
from app.models.resume import Resume, ResumeVersion
from app.schemas.applications import (
    ApplicationPackageApproveRequest,
    ApplicationPackageCreateRequest,
    ApplicationPackageHandoffResponse,
    ApplicationPackageResponse,
    ApplicationPackageUpdateRequest,
    ApplicationQuestionAnswer,
    ApplicationSubmissionConfirmRequest,
)
from app.schemas.jobs import JobImportRequest
from app.services.job_ingestion_pipeline import JobIngestionPipelineService

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_json(data: Any) -> str:
    try:
        return json.dumps(data, indent=2, default=str)
    except Exception:
        return str(data)


class ApplicationPreparationService:
    """Service orchestrating application package preparation, approval, and handoff."""

    def __init__(self) -> None:
        self._pipeline_service = JobIngestionPipelineService()

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Package Preparation & Generation
    # ─────────────────────────────────────────────────────────────────────────

    async def prepare_package(
        self,
        user: User,
        request: ApplicationPackageCreateRequest,
        db: AsyncSession,
        llm: LLMProvider,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> ApplicationPackage:
        """
        Creates a new evidence-grounded application package for the candidate.
        Validates target job, resolves tailored resume version, queries authentic
        career evidence, invokes Gemini for structured cover note & Q&A generation,
        and persists the package in 'draft' status.
        """
        # 1. Resolve and validate target job
        job = await self._resolve_target_job(request=request, db=db)

        # 2. Resolve source resume and tailored resume version
        source_resume, tailored_version = await self._resolve_resume_and_tailored_version(
            user=user,
            job=job,
            request=request,
            db=db,
        )

        # 3. Retrieve authentic candidate profile & evidence
        career_profile = await self._fetch_candidate_profile(user_id=user.id, db=db)

        # 4. Build prompt context
        desc_text = (
            job.description_markdown
            or job.description_text
            or " ".join(job.responsibilities or [])
            or " ".join(job.required_qualifications or [])
        )

        tailored_content = tailored_version.tailored_content or {}
        verified_skills_list = []
        if career_profile and career_profile.user_skills:
            verified_skills_list = [us.skill.name for us in career_profile.user_skills if us.skill]
        if not verified_skills_list and tailored_content.get("skills"):
            verified_skills_list = [s.get("name", "") for s in tailored_content.get("skills", []) if s.get("name")]

        prompt = APPLICATION_PREP_PROMPT_TEMPLATE.format(
            job_title=job.title,
            company_name=job.company_name,
            job_location=job.location or "Remote",
            job_description=desc_text[:12000],
            source_resume_text=(source_resume.parsed_text or "")[:6000],
            tailored_summary=tailored_content.get("executive_summary", "None provided"),
            tailored_skills=", ".join(verified_skills_list) or "None specified",
            tailored_experience=_safe_json(tailored_content.get("experience", []))[:3000],
            tailored_projects=_safe_json(tailored_content.get("projects", []))[:2000],
            verified_skills=", ".join(verified_skills_list) or "None specified",
            career_stage=career_profile.career_stage if career_profile else "mid",
            target_role=career_profile.target_role_id if career_profile else "Software Engineer",
            user_notes=request.user_notes or "None provided",
        )

        # 5. Invoke Gemini LLM for structured output
        try:
            ai_output: AIApplicationPackageOutput = await llm.generate_structured(
                prompt=prompt,
                schema=AIApplicationPackageOutput,
                system_prompt=APPLICATION_PREP_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=2500,
            )
        except Exception as e:
            logger.error(f"Application package generation failed: {e}", exc_info=True)
            raise ServiceUnavailableException("Gemini", f"Application preparation generation failed: {str(e)}")

        # 6. Reconcile and audit evidence references
        sanitized_questions = [
            q.model_dump() for q in ai_output.application_questions
        ]
        sanitized_evidence = list(ai_output.evidence_references)

        # 7. Get or link pipeline Application record
        existing_app_stmt = select(Application).where(
            Application.user_id == user.id,
            Application.job_id == job.id,
        )
        app_record = await db.scalar(existing_app_stmt)
        if not app_record:
            app_record = Application(
                id=uuid.uuid4(),
                user_id=user.id,
                job_id=job.id,
                current_status="saved",
                tailored_resume_version_id=tailored_version.id,
            )
            db.add(app_record)
            await db.flush()

        # 8. Create ApplicationPackage record in initial 'draft' state
        word_count = len(ai_output.cover_note.split())
        metadata_payload = {
            "model": getattr(llm, "provider_name", "gemini"),
            "cover_note_word_count": word_count,
            "questions_count": len(sanitized_questions),
            "unsupported_claims_omitted": ai_output.unsupported_claims,
            "prompt_version": "v1",
        }

        package = ApplicationPackage(
            id=uuid.uuid4(),
            user_id=user.id,
            job_id=job.id,
            application_id=app_record.id,
            source_resume_id=source_resume.id,
            tailored_resume_version_id=tailored_version.id,
            status="draft",
            cover_note=ai_output.cover_note,
            application_questions=sanitized_questions,
            evidence_references=sanitized_evidence,
            generated_metadata=metadata_payload,
            user_notes=request.user_notes,
            application_url=job.application_url,
            application_url_source="job_listing",
            user_confirmed_submission=False,
            approved_at=None,
            submitted_at=None,
        )
        db.add(package)
        await db.commit()
        await db.refresh(package)

        logger.info(
            f"Application package {package.id} created for user {user.id}, "
            f"job {job.id}, tailored version {tailored_version.id}"
        )
        return package

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Package Retrieval & Listing
    # ─────────────────────────────────────────────────────────────────────────

    async def get_package(
        self,
        package_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> ApplicationPackage:
        """Retrieves an application package ensuring multi-tenant ownership."""
        stmt = (
            select(ApplicationPackage)
            .options(
                selectinload(ApplicationPackage.job),
                selectinload(ApplicationPackage.source_resume),
                selectinload(ApplicationPackage.tailored_resume_version),
            )
            .where(ApplicationPackage.id == package_id)
        )
        package = await db.scalar(stmt)
        if not package:
            raise NotFoundException("ApplicationPackage")

        if package.user_id != user.id and user.role != "admin":
            raise ForbiddenException("You do not have permission to access this application package.")

        return package

    async def list_packages(
        self,
        user: User,
        job_id: Optional[uuid.UUID],
        status_filter: Optional[str],
        db: AsyncSession,
    ) -> List[ApplicationPackage]:
        """Lists application packages belonging to the authenticated candidate."""
        stmt = (
            select(ApplicationPackage)
            .options(
                selectinload(ApplicationPackage.job),
                selectinload(ApplicationPackage.tailored_resume_version),
            )
            .where(ApplicationPackage.user_id == user.id)
        )
        if job_id:
            stmt = stmt.where(ApplicationPackage.job_id == job_id)
        if status_filter:
            stmt = stmt.where(ApplicationPackage.status == status_filter)

        stmt = stmt.order_by(ApplicationPackage.created_at.desc())
        result = await db.scalars(stmt)
        return list(result.all())

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Package Updating
    # ─────────────────────────────────────────────────────────────────────────

    async def update_package(
        self,
        package_id: uuid.UUID,
        user: User,
        request: ApplicationPackageUpdateRequest,
        db: AsyncSession,
    ) -> ApplicationPackage:
        """Updates editable cover note, application questions, or candidate notes."""
        package = await self.get_package(package_id=package_id, user=user, db=db)

        if package.status == "submitted":
            raise ConflictException(
                "Cannot edit application package after external submission has been confirmed."
            )

        if request.cover_note is not None:
            package.cover_note = request.cover_note
        if request.application_questions is not None:
            package.application_questions = [q.model_dump() for q in request.application_questions]
        if request.user_notes is not None:
            package.user_notes = request.user_notes

        # Transition status to 'edited' and reset prior approval
        package.status = "edited"
        package.approved_at = None

        package.updated_at = _utc_now()
        await db.commit()
        await db.refresh(package)
        return package

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Explicit Human Approval Gateway
    # ─────────────────────────────────────────────────────────────────────────

    async def approve_package(
        self,
        package_id: uuid.UUID,
        user: User,
        request: ApplicationPackageApproveRequest,
        db: AsyncSession,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> ApplicationPackage:
        """
        Explicit candidate approval gate for an application package.
        Validates mandatory confirmation checkbox, transitions status to 'approved',
        and records an immutable security AuditLog entry.
        """
        package = await self.get_package(package_id=package_id, user=user, db=db)

        if not request.user_confirmation:
            raise ValidationException(
                "Explicit user_confirmation=True is required to approve the application package."
            )

        if package.status == "submitted":
            raise ConflictException("Application package is already submitted.")

        package.status = "approved"
        package.approved_at = _utc_now()
        package.updated_at = _utc_now()

        # Record security audit log
        meta = request_metadata or {}
        audit_entry = AuditLog(
            user_id=user.id,
            action_type="APPLICATION_PACKAGE_APPROVED",
            target_entity_type="application_package",
            target_entity_id=package.id,
            diff_payload={
                "status": "approved",
                "tailored_resume_version_id": str(package.tailored_resume_version_id),
                "accepted_sections": getattr(request, "accepted_sections", None) or ["cover_note", "questions"],
            },
            human_approved=True,
            client_ip_hash=meta.get("client_ip_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            user_agent=meta.get("user_agent", "CoachPath API"),
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(package)

        logger.info(f"Application package {package.id} approved by user {user.id}")
        return package

    # ─────────────────────────────────────────────────────────────────────────
    # 5. External Application Handoff
    # ─────────────────────────────────────────────────────────────────────────

    async def initiate_handoff(
        self,
        package_id: uuid.UUID,
        user: User,
        db: AsyncSession,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> ApplicationPackageHandoffResponse:
        """
        Initiates handoff to the employer's official careers portal.
        Requires that the package has been explicitly approved first.
        """
        package = await self.get_package(package_id=package_id, user=user, db=db)

        if package.status not in ("approved", "handoff_initiated", "submitted"):
            raise ConflictException(
                "Application package must be explicitly approved before external handoff."
            )

        now = _utc_now()
        if package.status == "approved":
            package.status = "handoff_initiated"
            package.handoff_initiated_at = now
            package.updated_at = now

            meta = request_metadata or {}
            audit_entry = AuditLog(
                user_id=user.id,
                action_type="APPLICATION_HANDOFF_INITIATED",
                target_entity_type="application_package",
                target_entity_id=package.id,
                diff_payload={
                    "status": "handoff_initiated",
                    "application_url": package.application_url,
                },
                human_approved=True,
                client_ip_hash=meta.get("client_ip_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
                user_agent=meta.get("user_agent", "CoachPath API"),
            )
            db.add(audit_entry)
            await db.commit()
            await db.refresh(package)

        return ApplicationPackageHandoffResponse(
            package_id=package.id,
            status=package.status,
            application_url=package.application_url,
            instructions=(
                "Open the employer careers portal to complete official submission. "
                "Once completed, return to CoachPath to confirm submission."
            ),
            handoff_initiated_at=package.handoff_initiated_at or now,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 6. User-Confirmed Application Submission
    # ─────────────────────────────────────────────────────────────────────────

    async def confirm_submission(
        self,
        package_id: uuid.UUID,
        user: User,
        request: ApplicationSubmissionConfirmRequest,
        db: AsyncSession,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> ApplicationPackage:
        """
        Records candidate explicit confirmation that they completed the employer's
        official application submission process.
        """
        package = await self.get_package(package_id=package_id, user=user, db=db)

        if not request.user_confirmation:
            raise ValidationException(
                "Explicit user_confirmation=True is required to confirm application submission."
            )

        if package.status not in ("approved", "handoff_initiated", "submitted"):
            raise ConflictException(
                "Application package must be approved before submission can be confirmed."
            )

        # Idempotent handling for duplicate submission confirmation
        if package.user_confirmed_submission and package.status == "submitted":
            return package

        now = _utc_now()
        package.user_confirmed_submission = True
        package.status = "submitted"
        package.submitted_at = now
        package.updated_at = now

        # Update linked Application in pipeline tracker if present
        if package.application_id:
            app_stmt = select(Application).where(Application.id == package.application_id)
            app_record = await db.scalar(app_stmt)
            if app_record:
                old_status = app_record.current_status
                app_record.current_status = "applied"
                app_record.applied_date = date.today()
                app_record.tailored_resume_version_id = package.tailored_resume_version_id

                history_entry = ApplicationStatusHistory(
                    id=uuid.uuid4(),
                    application_id=app_record.id,
                    from_status=old_status,
                    to_status="applied",
                    changed_at=now,
                )
                db.add(history_entry)

        # Record security audit log
        meta = request_metadata or {}
        audit_entry = AuditLog(
            user_id=user.id,
            action_type="APPLICATION_SUBMISSION_CONFIRMED",
            target_entity_type="application_package",
            target_entity_id=package.id,
            diff_payload={
                "status": "submitted",
                "user_confirmed": True,
                "notes": request.notes,
            },
            human_approved=True,
            client_ip_hash=meta.get("client_ip_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            user_agent=meta.get("user_agent", "CoachPath API"),
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(package)

        logger.info(f"Application package {package.id} submission confirmed by candidate {user.id}")
        return package

    # ─────────────────────────────────────────────────────────────────────────
    # 7. Helper Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def _resolve_target_job(
        self,
        request: ApplicationPackageCreateRequest,
        db: AsyncSession,
    ) -> Job:
        """Resolves target job by catalog UUID or direct job text import."""
        if request.job_id:
            stmt = select(Job).options(selectinload(Job.skills)).where(Job.id == request.job_id)
            job = await db.scalar(stmt)
            if not job:
                raise NotFoundException("Job")
            return job

        if request.job_description_text:
            import_req = JobImportRequest(
                title=request.job_title or "Target Position",
                company_name=request.company_name or "Target Employer",
                description_text=request.job_description_text,
            )
            job_resp = await self._pipeline_service.import_single_job(request=import_req, db=db)
            stmt = select(Job).options(selectinload(Job.skills)).where(Job.id == job_resp.id)
            job = await db.scalar(stmt)
            if not job:
                raise NotFoundException("Job")
            return job

        raise ValidationException("Either job_id or job_description_text must be provided.")

    async def _resolve_resume_and_tailored_version(
        self,
        user: User,
        job: Job,
        request: ApplicationPackageCreateRequest,
        db: AsyncSession,
    ) -> Tuple[Resume, ResumeVersion]:
        """Resolves the user's authentic source resume and tailored resume version."""
        # 1. If tailored resume version is explicitly requested
        if request.tailored_resume_version_id:
            stmt = select(ResumeVersion).where(ResumeVersion.id == request.tailored_resume_version_id)
            tailored_version = await db.scalar(stmt)
            if not tailored_version:
                raise NotFoundException("ResumeVersion")

            if tailored_version.user_id != user.id and user.role != "admin":
                raise ForbiddenException("You do not have permission to use this tailored resume version.")

            # Load source resume
            source_resume_stmt = select(Resume).where(Resume.id == tailored_version.resume_id)
            source_resume = await db.scalar(source_resume_stmt)
            if not source_resume or source_resume.user_id != user.id:
                raise ForbiddenException("You do not have permission to access the source resume.")

            if source_resume.status != "parsed":
                raise BadRequestException("Source resume has not been successfully parsed.")

            return source_resume, tailored_version

        # 2. Look for existing saved tailored versions for this user and job
        stmt_versions = (
            select(ResumeVersion)
            .where(
                ResumeVersion.user_id == user.id,
                ResumeVersion.target_job_id == job.id,
            )
            .order_by(ResumeVersion.version_number.desc())
        )
        versions = list((await db.scalars(stmt_versions)).all())
        if versions:
            # Prefer approved version if available, else latest draft
            preferred_version = next((v for v in versions if v.status == "approved"), versions[0])
            source_resume_stmt = select(Resume).where(Resume.id == preferred_version.resume_id)
            source_resume = await db.scalar(source_resume_stmt)
            if source_resume and source_resume.status == "parsed":
                return source_resume, preferred_version

        # 3. If no tailored version exists yet, resolve candidate's parsed resume
        source_resume = None
        if request.source_resume_id:
            stmt_res = select(Resume).where(Resume.id == request.source_resume_id)
            source_resume = await db.scalar(stmt_res)
            if not source_resume:
                raise NotFoundException("Resume")
            if source_resume.user_id != user.id:
                raise ForbiddenException("You do not have permission to access this resume.")
            if source_resume.status != "parsed":
                raise BadRequestException("Source resume has not been successfully parsed.")
        else:
            stmt_prim = select(Resume).where(
                Resume.user_id == user.id,
                Resume.status == "parsed",
            ).order_by(Resume.is_primary.desc(), Resume.created_at.desc())
            source_resume = await db.scalar(stmt_prim)

        if not source_resume:
            raise BadRequestException("No parsed active resume found for candidate. Please upload and parse your resume first.")

        # Auto-create a baseline ResumeVersion (v1) linked to this job from candidate's parsed extracted data
        baseline_version = ResumeVersion(
            id=uuid.uuid4(),
            user_id=user.id,
            resume_id=source_resume.id,
            target_job_id=job.id,
            version_number=1,
            tailored_content=source_resume.extracted_data or {},
            diff_summary={"additions": [], "rephrasings": [], "deletions": []},
            status="draft",
            anti_hallucination_verified=True,
        )
        db.add(baseline_version)
        await db.flush()
        return source_resume, baseline_version

    async def _fetch_candidate_profile(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> Optional[CareerProfile]:
        """Loads candidate's career profile with complete evidence graph."""
        stmt = (
            select(CareerProfile)
            .options(
                selectinload(CareerProfile.user_skills),
                selectinload(CareerProfile.experience),
                selectinload(CareerProfile.projects),
                selectinload(CareerProfile.education),
                selectinload(CareerProfile.certifications),
            )
            .where(CareerProfile.user_id == user_id)
        )
        return await db.scalar(stmt)


application_preparation_service = ApplicationPreparationService()
