"""
Resume Ingestion and Parsing Orchestration Service for CoachPath.
Orchestrates secure upload, storage, document text extraction, structured AI interpretation,
skill normalization, draft persistence, and retry workflows.

CRITICAL INVARIANT: This service persists extracted resume data strictly as a reviewable
draft attached to the Resume entity. It NEVER automatically creates, overwrites, or mutates
the user's canonical CareerProfile or UserSkill records.
"""
from __future__ import annotations

import decimal
import logging
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import UploadFile
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.base import LLMProvider
from app.ai.prompts.resume_v1 import (
    RESUME_EXTRACTION_PROMPT_TEMPLATE,
    RESUME_EXTRACTION_SYSTEM_PROMPT,
)
from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ServiceUnavailableException,
)
from app.models.auth import User, UserProfile
from app.models.career import (
    CareerProfile,
    Certification,
    Education,
    Experience,
    Project,
)
from app.models.resume import Resume
from app.models.skills import Skill, UserSkill
from app.schemas.resume import (
    ConfirmCertificationItem,
    ConfirmEducationItem,
    ConfirmExperienceItem,
    ConfirmPersonalInfo,
    ConfirmProjectItem,
    ExtractedResumeSchema,
    NormalizedSkillItem,
    ParsedResumePreview,
    ParsedResumeResponse,
    ParsingErrorCategory,
    ResumeConfirmationRequest,
    ResumeConfirmationResponse,
    ResumeMergeSummary,
    ResumeStatus,
)
from app.services.document_extractor import (
    DocumentExtractionException,
    ExtractedDocumentText,
    document_extractor,
)
from app.services.profile import (
    calculate_profile_completeness,
    profile_service,
)
from app.services.skill_normalizer import skill_normalizer
from app.services.storage import storage_service

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_fuzzy_date(val: Optional[str], default_to_today: bool = False) -> Optional[date]:
    """Robust fuzzy date parsing for extracted resume date strings."""
    if not val or not val.strip():
        return datetime.now(timezone.utc).date() if default_to_today else None

    clean = val.strip()
    # Try ISO YYYY-MM-DD
    try:
        return datetime.strptime(clean, "%Y-%m-%d").date()
    except ValueError:
        pass

    # Try YYYY-MM
    try:
        return datetime.strptime(clean, "%Y-%m").date().replace(day=1)
    except ValueError:
        pass

    # Try Month Year (e.g. "Aug 2018", "August 2018", "08/2018")
    for fmt in ("%b %Y", "%B %Y", "%m/%Y", "%m/%d/%Y", "%b. %Y"):
        try:
            return datetime.strptime(clean, fmt).date().replace(day=1)
        except ValueError:
            pass

    # Try 4-digit Year
    if len(clean) >= 4 and clean[:4].isdigit():
        try:
            return datetime.strptime(clean[:4], "%Y").date().replace(month=1, day=1)
        except ValueError:
            pass

    return datetime.now(timezone.utc).date() if default_to_today else None


class ResumeParsingService:
    """
    Manages the lifecycle of uploaded resume documents and structured AI parsing.
    """

    async def upload_and_parse(
        self,
        user: User,
        file: UploadFile,
        db: AsyncSession,
        llm: LLMProvider,
    ) -> Resume:
        """
        Validates, persists, extracts text, and parses structured career entities from an uploaded resume.
        Saves extraction results as a reviewable draft.
        """
        filename = file.filename or "resume.pdf"

        # 1. Read file content and check size limit (10MB)
        try:
            content = await file.read()
        except Exception as exc:
            logger.error("Failed to read uploaded file: %s", exc)
            raise BadRequestException("Could not read uploaded file content.") from exc

        file_size = len(content)
        if file_size == 0:
            raise BadRequestException("Uploaded file is empty (0 bytes).")
        if file_size > settings.MAX_RESUME_SIZE_BYTES:
            raise BadRequestException(
                f"File size ({file_size} bytes) exceeds maximum allowable limit of "
                f"{settings.MAX_RESUME_SIZE_BYTES} bytes (10 MB)."
            )

        # 2. Validate MIME magic bytes and extension
        try:
            mime_type, extension = document_extractor.detect_format_and_validate(content, filename)
        except DocumentExtractionException as exc:
            raise BadRequestException(exc.message) from exc

        # 3. Store original document safely
        try:
            relative_storage_path = await storage_service.save_file(
                user_id=user.id,
                file_bytes=content,
                extension=extension,
            )
        except Exception as exc:
            logger.error("File storage failed for user %s: %s", user.id, exc)
            raise BadRequestException("Failed to persist file in storage.") from exc

        # 4. Check if user already has resumes; set is_primary if this is the first
        existing_stmt = select(Resume).where(Resume.user_id == user.id)
        existing_resumes = (await db.scalars(existing_stmt)).all()
        is_primary = len(existing_resumes) == 0

        # 5. Create Resume database entity
        resume = Resume(
            user_id=user.id,
            file_name=filename,
            storage_path=relative_storage_path,
            file_size_bytes=file_size,
            mime_type=mime_type,
            status=ResumeStatus.PARSING,
            is_primary=is_primary,
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)

        # 6. Run text extraction and AI parsing pipeline
        await self._process_resume_content(resume, content, db, llm)

        return resume

    async def _process_resume_content(
        self,
        resume: Resume,
        content: bytes,
        db: AsyncSession,
        llm: LLMProvider,
    ) -> None:
        """
        Executes text extraction, AI parsing, and skill normalization.
        Safely records errors without leaving the resume in an inconsistent state.
        """
        # Step A: Text extraction
        try:
            doc_text: ExtractedDocumentText = document_extractor.extract_text(
                content=content,
                mime_type=resume.mime_type,
            )
            resume.parsed_text = doc_text.raw_text
        except DocumentExtractionException as exc:
            logger.warning("Document extraction failed for resume %s: %s", resume.id, exc.message)
            resume.status = ResumeStatus.FAILED
            resume.parsing_error = exc.message
            resume.parsing_error_category = exc.category
            resume.updated_at = _utc_now()
            await db.commit()
            await db.refresh(resume)
            return
        except Exception as exc:
            logger.error("Unexpected text extraction error for resume %s: %s", resume.id, exc)
            resume.status = ResumeStatus.FAILED
            resume.parsing_error = f"Text extraction failed: {exc}"
            resume.parsing_error_category = ParsingErrorCategory.CORRUPTED_DOCUMENT
            resume.updated_at = _utc_now()
            await db.commit()
            await db.refresh(resume)
            return

        # Step B: AI Structured Extraction
        prompt = RESUME_EXTRACTION_PROMPT_TEMPLATE.format(
            document_text=doc_text.raw_text[:16000]  # Safe token budget envelope
        )

        try:
            extracted_schema: ExtractedResumeSchema = await llm.generate_structured(
                prompt=prompt,
                schema=ExtractedResumeSchema,
                system_prompt=RESUME_EXTRACTION_SYSTEM_PROMPT,
                temperature=0.1,  # Low temperature for strict factual extraction
                max_tokens=4096,
            )
        except ServiceUnavailableException as exc:
            logger.warning("AI provider unavailable for resume parsing %s: %s", resume.id, exc)
            resume.status = ResumeStatus.FAILED
            resume.parsing_error = exc.message or "AI provider service is currently unavailable."
            resume.parsing_error_category = ParsingErrorCategory.AI_PROVIDER_UNAVAILABLE
            resume.updated_at = _utc_now()
            await db.commit()
            await db.refresh(resume)
            return
        except Exception as exc:
            logger.error("AI parsing error for resume %s: %s", resume.id, exc)
            resume.status = ResumeStatus.FAILED
            resume.parsing_error = f"AI structured extraction failed: {exc}"
            resume.parsing_error_category = ParsingErrorCategory.AI_OUTPUT_INVALID
            resume.updated_at = _utc_now()
            await db.commit()
            await db.refresh(resume)
            return

        # Step C: Skill Normalization
        raw_skill_names = [s.name for s in extracted_schema.skills]
        # Also include tech from projects
        for proj in extracted_schema.projects:
            raw_skill_names.extend(proj.technologies)

        normalized_skills, unmatched_skills = await skill_normalizer.normalize_skills(
            extracted_skills=raw_skill_names,
            db=db,
        )

        # Step D: Assemble Draft Structured Data and Persist
        extracted_dict = extracted_schema.model_dump()
        extracted_dict["normalized_skills"] = [s.model_dump() for s in normalized_skills]
        extracted_dict["raw_unmatched_skills"] = unmatched_skills

        resume.extracted_data = extracted_dict
        resume.status = ResumeStatus.PARSED
        resume.parsing_error = None
        resume.parsing_error_category = None
        resume.parsed_at = _utc_now()
        resume.updated_at = _utc_now()

        await db.commit()
        await db.refresh(resume)
        logger.info(
            "Resume %s parsed successfully (education: %d, experience: %d, skills: %d)",
            resume.id,
            len(extracted_schema.education),
            len(extracted_schema.experience),
            len(normalized_skills),
        )

    async def list_user_resumes(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> List[Resume]:
        """Lists all uploaded resumes belonging to the authenticated candidate."""
        stmt = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
        )
        return (await db.scalars(stmt)).all()

    async def get_user_resume(
        self,
        resume_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> Resume:
        """Retrieves resume by ID, strictly enforcing user ownership."""
        stmt = select(Resume).where(Resume.id == resume_id)
        resume = await db.scalar(stmt)
        if not resume:
            raise NotFoundException("Resume", resume_id)
        if resume.user_id != user.id and user.role != "admin":
            raise ForbiddenException("You do not have permission to access this resume.")
        return resume

    async def get_parsed_draft(
        self,
        resume_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> ParsedResumeResponse:
        """
        Retrieves the structured parsed draft awaiting candidate review.
        Enforces human approval gate (requires_human_confirmation=True).
        """
        resume = await self.get_user_resume(resume_id, user, db)

        preview: Optional[ParsedResumePreview] = None
        if resume.status in (ResumeStatus.PARSED, ResumeStatus.NEEDS_REVIEW) and resume.extracted_data:
            data = resume.extracted_data
            preview = ParsedResumePreview(
                personal_info=data.get("personal_info"),
                education=data.get("education", []),
                experience=data.get("experience", []),
                projects=data.get("projects", []),
                certifications=data.get("certifications", []),
                detected_skills=[s["name"] for s in data.get("skills", [])],
                normalized_skills=[
                    NormalizedSkillItem.model_validate(ns)
                    for ns in data.get("normalized_skills", [])
                ],
                raw_unmatched_skills=data.get("raw_unmatched_skills", []),
                executive_summary=data.get("executive_summary"),
            )

        return ParsedResumeResponse(
            resume_id=resume.id,
            status=resume.status,
            file_name=resume.file_name,
            extracted_preview=preview,
            requires_human_confirmation=True,
            parsed_at=resume.parsed_at,
            parsing_error=resume.parsing_error,
            parsing_error_category=resume.parsing_error_category,
        )

    async def retry_parsing(
        self,
        resume_id: uuid.UUID,
        user: User,
        db: AsyncSession,
        llm: LLMProvider,
    ) -> Resume:
        """
        Re-attempts text extraction and AI parsing for an existing uploaded resume.
        Useful when an AI service temporarily timed out or recovered from outage.
        """
        resume = await self.get_user_resume(resume_id, user, db)

        if not await storage_service.file_exists(resume.storage_path):
            raise NotFoundException("Stored resume file is missing from filesystem.")

        content = await storage_service.read_file(resume.storage_path)

        resume.status = ResumeStatus.PARSING
        resume.parsing_error = None
        resume.parsing_error_category = None
        resume.updated_at = _utc_now()
        await db.commit()
        await db.refresh(resume)

        await self._process_resume_content(resume, content, db, llm)
        return resume

    async def get_document_file(
        self,
        resume_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> Tuple[bytes, str, str]:
        """
        Returns document content, original filename, and MIME type for secure download.
        """
        resume = await self.get_user_resume(resume_id, user, db)

        if not await storage_service.file_exists(resume.storage_path):
            raise NotFoundException("Stored resume file was not found on server.")

        content = await storage_service.read_file(resume.storage_path)
        return content, resume.file_name, resume.mime_type

    async def delete_resume(
        self,
        resume_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> None:
        """
        Deletes the resume entity and deletes the physical file from storage.
        """
        resume = await self.get_user_resume(resume_id, user, db)

        # 1. Delete physical file
        if resume.storage_path:
            await storage_service.delete_file(resume.storage_path)

        # 2. Delete database record
        await db.delete(resume)
        await db.commit()
        logger.info("Deleted resume %s for user %s", resume_id, user.id)

    async def confirm_and_merge_profile(
        self,
        resume_id: uuid.UUID,
        request: ResumeConfirmationRequest,
        user: User,
        db: AsyncSession,
    ) -> ResumeConfirmationResponse:
        """
        Explicit candidate approval gateway:
        Atomically merges reviewed & user-corrected resume entities into the canonical
        CareerProfile and UserSkills in PostgreSQL.
        Guarantees idempotency and duplicate prevention.
        Does NOT alter unselected fields or overwrite existing verified skills.
        """
        resume = await self.get_user_resume(resume_id, user, db)

        if resume.status not in (ResumeStatus.PARSED, ResumeStatus.NEEDS_REVIEW):
            raise ConflictException(
                f"Cannot confirm resume in '{resume.status}' status. Document must be successfully parsed first."
            )

        # 1. Fetch or create candidate UserProfile & CareerProfile
        profile_stmt = select(UserProfile).where(UserProfile.user_id == user.id)
        user_profile = await db.scalar(profile_stmt)
        if not user_profile:
            user_profile = UserProfile(user_id=user.id, full_name=user.email.split("@")[0])
            db.add(user_profile)
            await db.flush()

        career_profile = await profile_service.get_or_create_career_profile(db, user.id)

        summary = ResumeMergeSummary()

        # 2. Merge approved Personal Info (if provided)
        if request.personal_info:
            p_info = request.personal_info
            updated = False
            if p_info.headline:
                user_profile.headline = p_info.headline
                updated = True
            if p_info.location:
                user_profile.location = p_info.location
                updated = True
            if p_info.phone_number:
                user_profile.phone_number = p_info.phone_number
                updated = True
            if p_info.linkedin_url:
                user_profile.linkedin_url = p_info.linkedin_url
                updated = True
            if p_info.github_url:
                user_profile.github_url = p_info.github_url
                updated = True
            if p_info.portfolio_url:
                user_profile.portfolio_url = p_info.portfolio_url
                updated = True
            if p_info.bio:
                user_profile.bio = p_info.bio
                updated = True
            summary.profile_updated = updated

        # 3. Merge approved Education (avoid duplicates by institution + degree)
        existing_edu_res = await db.execute(
            select(Education.institution_name, Education.degree)
            .where(Education.career_profile_id == career_profile.id)
        )
        existing_edu_keys = {
            (row[0].lower().strip(), row[1].lower().strip())
            for row in existing_edu_res.all()
        }
        for edu_item in request.education:
            key = (edu_item.institution_name.lower().strip(), edu_item.degree.lower().strip())
            if key not in existing_edu_keys:
                s_date = _parse_fuzzy_date(edu_item.start_date, default_to_today=True)
                e_date = _parse_fuzzy_date(edu_item.end_date, default_to_today=False)
                if s_date and e_date and e_date < s_date:
                    e_date = s_date

                new_edu = Education(
                    career_profile_id=career_profile.id,
                    institution_name=edu_item.institution_name.strip(),
                    degree=edu_item.degree.strip(),
                    field_of_study=edu_item.field_of_study.strip(),
                    start_date=s_date,
                    end_date=e_date,
                    is_current=edu_item.is_current,
                    gpa=decimal.Decimal(str(edu_item.gpa)) if edu_item.gpa is not None else None,
                )
                db.add(new_edu)
                existing_edu_keys.add(key)
                summary.education_added += 1

        # 4. Merge approved Work Experience (avoid duplicates by company + role)
        existing_exp_res = await db.execute(
            select(Experience.company_name, Experience.role_title)
            .where(Experience.career_profile_id == career_profile.id)
        )
        existing_exp_keys = {
            (row[0].lower().strip(), row[1].lower().strip())
            for row in existing_exp_res.all()
        }
        for exp_item in request.experience:
            key = (exp_item.company_name.lower().strip(), exp_item.role_title.lower().strip())
            if key not in existing_exp_keys:
                s_date = _parse_fuzzy_date(exp_item.start_date, default_to_today=True)
                e_date = _parse_fuzzy_date(exp_item.end_date, default_to_today=False)
                if s_date and e_date and e_date < s_date:
                    e_date = s_date

                new_exp = Experience(
                    career_profile_id=career_profile.id,
                    company_name=exp_item.company_name.strip(),
                    role_title=exp_item.role_title.strip(),
                    location=exp_item.location.strip() if exp_item.location else None,
                    start_date=s_date,
                    end_date=e_date,
                    is_current=exp_item.is_current,
                    bullet_points=exp_item.bullet_points or [],
                )
                db.add(new_exp)
                existing_exp_keys.add(key)
                summary.experience_added += 1

        # 5. Merge approved Projects (avoid duplicates by title)
        existing_proj_res = await db.execute(
            select(Project.title).where(Project.career_profile_id == career_profile.id)
        )
        existing_proj_keys = {row[0].lower().strip() for row in existing_proj_res.all()}
        for proj_item in request.projects:
            key = proj_item.title.lower().strip()
            if key not in existing_proj_keys:
                new_proj = Project(
                    career_profile_id=career_profile.id,
                    title=proj_item.title.strip(),
                    description=proj_item.description.strip(),
                    technologies=proj_item.technologies or [],
                    github_url=proj_item.github_url.strip() if proj_item.github_url else None,
                    live_url=proj_item.live_url.strip() if proj_item.live_url else None,
                    bullet_points=proj_item.bullet_points or [],
                )
                db.add(new_proj)
                existing_proj_keys.add(key)
                summary.projects_added += 1

        # 6. Merge approved Certifications (avoid duplicates by name + org)
        existing_cert_res = await db.execute(
            select(Certification.name, Certification.issuing_organization)
            .where(Certification.career_profile_id == career_profile.id)
        )
        existing_cert_keys = {
            (row[0].lower().strip(), row[1].lower().strip())
            for row in existing_cert_res.all()
        }
        for cert_item in request.certifications:
            key = (cert_item.name.lower().strip(), cert_item.issuing_organization.lower().strip())
            if key not in existing_cert_keys:
                i_date = _parse_fuzzy_date(cert_item.issue_date, default_to_today=True)
                e_date = _parse_fuzzy_date(cert_item.expiration_date, default_to_today=False)
                if i_date and e_date and e_date < i_date:
                    e_date = i_date

                new_cert = Certification(
                    career_profile_id=career_profile.id,
                    name=cert_item.name.strip(),
                    issuing_organization=cert_item.issuing_organization.strip(),
                    issue_date=i_date,
                    expiration_date=e_date,
                    credential_id=cert_item.credential_id.strip() if cert_item.credential_id else None,
                    credential_url=cert_item.credential_url.strip() if cert_item.credential_url else None,
                )
                db.add(new_cert)
                existing_cert_keys.add(key)
                summary.certifications_added += 1

        # 7. Merge approved Skills (match against canonical Skill repository)
        if request.confirmed_skills:
            user_skills_stmt = select(UserSkill.skill_id).where(UserSkill.career_profile_id == career_profile.id)
            existing_skill_ids = set((await db.scalars(user_skills_stmt)).all())

            normalized_targets = [s.strip().lower() for s in request.confirmed_skills if s.strip()]
            if normalized_targets:
                canonical_skills_stmt = select(Skill).where(
                    sa.func.lower(Skill.id).in_(normalized_targets) | sa.func.lower(Skill.name).in_(normalized_targets)
                )
                canonical_skills = (await db.scalars(canonical_skills_stmt)).all()

                for sk in canonical_skills:
                    if sk.id not in existing_skill_ids:
                        new_us = UserSkill(
                            career_profile_id=career_profile.id,
                            skill_id=sk.id,
                            confidence_score=decimal.Decimal("0.50"),
                            proficiency_tier="unverified",
                            is_verified=False,
                            primary_source="extracted",
                        )
                        db.add(new_us)
                        existing_skill_ids.add(sk.id)
                        summary.skills_added += 1

        # 8. Primary Resume Management
        if request.make_primary:
            all_resumes_stmt = select(Resume).where(Resume.user_id == user.id)
            all_resumes = (await db.scalars(all_resumes_stmt)).all()
            for r in all_resumes:
                r.is_primary = (r.id == resume.id)

        resume.updated_at = _utc_now()

        # Flush additions and reload career profile with relations for scoring
        await db.flush()

        # 9. Compute deterministic profile completeness
        profile_reload_stmt = (
            select(CareerProfile)
            .options(
                selectinload(CareerProfile.education),
                selectinload(CareerProfile.experience),
                selectinload(CareerProfile.projects),
                selectinload(CareerProfile.certifications),
            )
            .where(CareerProfile.id == career_profile.id)
        )
        loaded_career_profile = await db.scalar(profile_reload_stmt)
        completeness = calculate_profile_completeness(user_profile, loaded_career_profile)

        await db.commit()
        await db.refresh(resume)

        logger.info(
            "Confirmed resume %s for user %s: edu=%d, exp=%d, proj=%d, cert=%d, skills=%d",
            resume_id, user.id, summary.education_added, summary.experience_added,
            summary.projects_added, summary.certifications_added, summary.skills_added,
        )

        return ResumeConfirmationResponse(
            resume_id=resume.id,
            status="confirmed",
            message="Resume data merged into career profile successfully.",
            merged_summary=summary,
            completeness_score=completeness,
        )


# Singleton resume parsing service
resume_service = ResumeParsingService()
