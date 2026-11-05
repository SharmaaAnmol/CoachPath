"""
Recruiter Outreach Service for CoachPath.
Orchestrates personalized networking outreach drafts with strict word-count limits (<= 90 words),
explicit candidate approval gates, safe manual handoff tracking, and multi-tenant security.

CRITICAL INVARIANTS:
1. STRICT WORD LIMIT: Message body must not exceed 90 words.
2. ZERO FABRICATION: No invented contact details, emails, recruiter identities, or candidate achievements.
3. LIMIT ENFORCEMENT: Maximum 3 active outreach drafts per application/job enforced on backend.
4. NO AUTOMATED DISPATCH: Never automatically sends emails or LinkedIn messages.
5. HONEST SENT STATE: Only marked 'sent' upon explicit candidate confirmation.
"""

from __future__ import annotations

import json
import logging
import urllib.parse
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.base import LLMProvider
from app.ai.prompts.recruiter_outreach_v1 import (
    AIRecruiterOutreachOutput,
    RECRUITER_OUTREACH_PROMPT_TEMPLATE,
    RECRUITER_OUTREACH_SYSTEM_PROMPT,
)
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
)
from app.models.applications import Application, ApplicationPackage, RecruiterOutreachDraft
from app.models.audit import AuditLog
from app.models.auth import User
from app.models.career import CareerProfile
from app.models.jobs import Job
from app.models.resume import ResumeVersion
from app.schemas.applications import (
    RecruiterOutreachApproveRequest,
    RecruiterOutreachCreateRequest,
    RecruiterOutreachHandoffResponse,
    RecruiterOutreachResponse,
    RecruiterOutreachSentConfirmRequest,
    RecruiterOutreachUpdateRequest,
)

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _count_words(text: str) -> int:
    """Counts non-empty words in string."""
    return len([w for w in text.strip().split() if w])


def _truncate_to_90_words(text: str) -> str:
    """Ensures message body strictly does not exceed 90 words."""
    words = [w for w in text.strip().split() if w]
    if len(words) <= 90:
        return text.strip()
    return " ".join(words[:90])


class RecruiterOutreachService:
    """Service managing recruiter outreach drafts, approvals, and handoffs."""

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Create Recruiter Outreach Draft
    # ─────────────────────────────────────────────────────────────────────────

    async def create_outreach_draft(
        self,
        user: User,
        request: RecruiterOutreachCreateRequest,
        db: AsyncSession,
        llm: LLMProvider,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> RecruiterOutreachDraft:
        """
        Creates a new personalized recruiter outreach draft.
        Enforces backend limit of up to 3 drafts per application.
        Generates structured AI output with strict <= 90 word count constraint.
        """
        # 1. Resolve target job and optional application package
        job, package = await self._resolve_target_job_and_package(
            user=user,
            request=request,
            db=db,
        )

        # 2. Enforce limit of 3 drafts per application / job
        existing_drafts_count = await self._count_active_drafts_for_job(
            user_id=user.id,
            job_id=job.id,
            db=db,
        )
        if existing_drafts_count >= 3:
            raise ValidationException(
                "Maximum limit of 3 recruiter outreach drafts per application reached. "
                "Please cancel or delete an existing draft to create a new one."
            )

        # 3. Retrieve authentic candidate facts
        career_profile = await self._fetch_candidate_profile(user_id=user.id, db=db)
        verified_skills_list = []
        if career_profile and career_profile.user_skills:
            verified_skills_list = [us.skill.name for us in career_profile.user_skills if us.skill]

        key_projects_summary = "None specified"
        if career_profile and career_profile.projects:
            key_projects_summary = "; ".join(
                f"{p.name}: {p.description or 'Project'}" for p in career_profile.projects[:2]
            )

        experience_summary = "None specified"
        if career_profile and career_profile.experience:
            experience_summary = "; ".join(
                f"{exp.job_title} at {exp.employer}" for exp in career_profile.experience[:2]
            )

        # 4. Format prompt
        job_reqs = (
            job.description_markdown
            or job.description_text
            or " ".join(job.required_qualifications or [])
        )

        candidate_name = user.full_name or "Candidate"
        recruiter_name = request.recruiter_name or "Not provided"
        recruiter_role = request.recruiter_role_type or "Not provided"
        recruiter_contact = request.recruiter_contact_info or request.recruiter_profile_url or "None provided"

        prompt = RECRUITER_OUTREACH_PROMPT_TEMPLATE.format(
            job_title=job.title,
            company_name=job.company_name,
            job_requirements=job_reqs[:4000],
            candidate_name=candidate_name,
            verified_skills=", ".join(verified_skills_list[:8]) or "Technical background",
            key_projects=key_projects_summary,
            experience_summary=experience_summary,
            recruiter_name=recruiter_name,
            recruiter_role_type=recruiter_role,
            recruiter_contact_info=recruiter_contact,
            candidate_notes=request.candidate_notes or "None provided",
        )

        # 5. Invoke Gemini structured generation
        try:
            ai_output: AIRecruiterOutreachOutput = await llm.generate_structured(
                prompt=prompt,
                schema=AIRecruiterOutreachOutput,
                system_prompt=RECRUITER_OUTREACH_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1000,
            )
        except Exception as e:
            logger.error(f"Recruiter outreach generation failed: {e}", exc_info=True)
            raise ServiceUnavailableException("Gemini", f"Recruiter outreach generation failed: {str(e)}")

        # 6. Enforce strict 90-word ceiling
        body = _truncate_to_90_words(ai_output.message_body)
        word_count = _count_words(body)

        # 7. Persist draft
        draft = RecruiterOutreachDraft(
            id=uuid.uuid4(),
            user_id=user.id,
            job_id=job.id,
            application_package_id=package.id if package else None,
            application_id=package.application_id if package else None,
            recruiter_name=request.recruiter_name,
            recruiter_role_type=request.recruiter_role_type,
            recruiter_profile_url=request.recruiter_profile_url,
            recruiter_contact_info=request.recruiter_contact_info,
            candidate_notes=request.candidate_notes,
            subject_line=ai_output.subject_line,
            message_body=body,
            word_count=word_count,
            suggested_role_types=ai_output.suggested_role_types or [
                "Technical Recruiter",
                "Talent Acquisition Partner",
                "Engineering Hiring Manager",
            ],
            status="draft",
            approved_at=None,
            handoff_initiated_at=None,
            handoff_type=None,
            sent_at=None,
            user_confirmed_sent=False,
        )
        db.add(draft)
        await db.commit()
        await db.refresh(draft)

        logger.info(f"Recruiter outreach draft {draft.id} created for user {user.id}, job {job.id}")
        return draft

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Retrieve & List Drafts
    # ─────────────────────────────────────────────────────────────────────────

    async def get_outreach_draft(
        self,
        draft_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> RecruiterOutreachDraft:
        """Retrieves a recruiter outreach draft ensuring candidate ownership."""
        stmt = (
            select(RecruiterOutreachDraft)
            .options(
                selectinload(RecruiterOutreachDraft.job),
                selectinload(RecruiterOutreachDraft.package),
            )
            .where(RecruiterOutreachDraft.id == draft_id)
        )
        draft = await db.scalar(stmt)
        if not draft:
            raise NotFoundException("RecruiterOutreachDraft")

        if draft.user_id != user.id and user.role != "admin":
            raise ForbiddenException("You do not have permission to access this recruiter outreach draft.")

        return draft

    async def list_outreach_drafts(
        self,
        user: User,
        package_id: Optional[uuid.UUID],
        job_id: Optional[uuid.UUID],
        db: AsyncSession,
    ) -> List[RecruiterOutreachDraft]:
        """Lists outreach drafts belonging to the candidate."""
        stmt = (
            select(RecruiterOutreachDraft)
            .options(selectinload(RecruiterOutreachDraft.job))
            .where(RecruiterOutreachDraft.user_id == user.id)
        )
        if package_id:
            stmt = stmt.where(RecruiterOutreachDraft.application_package_id == package_id)
        if job_id:
            stmt = stmt.where(RecruiterOutreachDraft.job_id == job_id)

        stmt = stmt.order_by(RecruiterOutreachDraft.created_at.desc())
        result = await db.scalars(stmt)
        return list(result.all())

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Update Draft
    # ─────────────────────────────────────────────────────────────────────────

    async def update_outreach_draft(
        self,
        draft_id: uuid.UUID,
        user: User,
        request: RecruiterOutreachUpdateRequest,
        db: AsyncSession,
    ) -> RecruiterOutreachDraft:
        """Updates user-edited recruiter outreach draft, enforcing word count <= 90."""
        draft = await self.get_outreach_draft(draft_id=draft_id, user=user, db=db)

        if draft.status in ("sent", "cancelled"):
            raise ConflictException(f"Cannot edit outreach draft in '{draft.status}' status.")

        if request.message_body is not None:
            words = _count_words(request.message_body)
            if words > 90:
                raise ValidationException(
                    f"Outreach message body must not exceed 90 words. (Current: {words} words)"
                )
            draft.message_body = request.message_body.strip()
            draft.word_count = words

        if request.subject_line is not None:
            draft.subject_line = request.subject_line.strip()
        if request.recruiter_name is not None:
            draft.recruiter_name = request.recruiter_name.strip() or None
        if request.recruiter_role_type is not None:
            draft.recruiter_role_type = request.recruiter_role_type.strip() or None
        if request.recruiter_profile_url is not None:
            draft.recruiter_profile_url = request.recruiter_profile_url.strip() or None
        if request.recruiter_contact_info is not None:
            draft.recruiter_contact_info = request.recruiter_contact_info.strip() or None
        if request.candidate_notes is not None:
            draft.candidate_notes = request.candidate_notes

        # Transition status to awaiting_approval and reset approval
        if draft.status in ("draft", "approved"):
            draft.status = "awaiting_approval"
            draft.approved_at = None

        draft.updated_at = _utc_now()
        await db.commit()
        await db.refresh(draft)
        return draft

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Explicit Approval Gateway
    # ─────────────────────────────────────────────────────────────────────────

    async def approve_outreach_draft(
        self,
        draft_id: uuid.UUID,
        user: User,
        request: RecruiterOutreachApproveRequest,
        db: AsyncSession,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> RecruiterOutreachDraft:
        """Explicit candidate approval gate for recruiter outreach message."""
        draft = await self.get_outreach_draft(draft_id=draft_id, user=user, db=db)

        if not request.user_confirmation:
            raise ValidationException(
                "Explicit user_confirmation=True is required to approve the recruiter outreach draft."
            )

        if draft.status in ("sent", "cancelled"):
            raise ConflictException(f"Cannot approve outreach draft in '{draft.status}' status.")

        draft.status = "approved"
        draft.approved_at = _utc_now()
        draft.updated_at = _utc_now()

        # Record security audit log
        meta = request_metadata or {}
        audit_entry = AuditLog(
            user_id=user.id,
            action_type="RECRUITER_OUTREACH_APPROVED",
            target_entity_type="recruiter_outreach_draft",
            target_entity_id=draft.id,
            diff_payload={
                "status": "approved",
                "subject_line": draft.subject_line,
                "word_count": draft.word_count,
            },
            human_approved=True,
            client_ip_hash=meta.get("client_ip_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            user_agent=meta.get("user_agent", "CoachPath API"),
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(draft)

        logger.info(f"Recruiter outreach draft {draft.id} approved by user {user.id}")
        return draft

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Safe Outreach Handoff
    # ─────────────────────────────────────────────────────────────────────────

    async def initiate_outreach_handoff(
        self,
        draft_id: uuid.UUID,
        user: User,
        db: AsyncSession,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> RecruiterOutreachHandoffResponse:
        """
        Initiates manual handoff (mailto URL, profile URL, or copy-to-clipboard text).
        Requires explicit prior approval. Opening a client does NOT mark message as sent.
        """
        draft = await self.get_outreach_draft(draft_id=draft_id, user=user, db=db)

        if draft.status not in ("approved", "handoff_initiated", "sent"):
            raise ConflictException(
                "Recruiter outreach draft must be approved before initiating handoff."
            )

        # Determine handoff type and payload
        mailto_url = None
        profile_url = draft.recruiter_profile_url

        if draft.recruiter_contact_info and "@" in draft.recruiter_contact_info:
            encoded_subject = urllib.parse.quote(draft.subject_line)
            encoded_body = urllib.parse.quote(draft.message_body)
            mailto_url = f"mailto:{draft.recruiter_contact_info.strip()}?subject={encoded_subject}&body={encoded_body}"
            handoff_type = "email_mailto"
        elif profile_url:
            handoff_type = "profile_url"
        else:
            handoff_type = "copy_text"

        now = _utc_now()
        if draft.status == "approved":
            draft.status = "handoff_initiated"
            draft.handoff_initiated_at = now
            draft.handoff_type = handoff_type
            draft.updated_at = now

            meta = request_metadata or {}
            audit_entry = AuditLog(
                user_id=user.id,
                action_type="RECRUITER_OUTREACH_HANDOFF_INITIATED",
                target_entity_type="recruiter_outreach_draft",
                target_entity_id=draft.id,
                diff_payload={
                    "status": "handoff_initiated",
                    "handoff_type": handoff_type,
                },
                human_approved=True,
                client_ip_hash=meta.get("client_ip_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
                user_agent=meta.get("user_agent", "CoachPath API"),
            )
            db.add(audit_entry)
            await db.commit()
            await db.refresh(draft)

        return RecruiterOutreachHandoffResponse(
            outreach_id=draft.id,
            status=draft.status,
            handoff_type=handoff_type,
            copy_text=draft.message_body,
            subject_line=draft.subject_line,
            mailto_url=mailto_url,
            profile_url=profile_url,
            instructions=(
                "Copy the message or open the contact URL to send manually. "
                "Once sent, return to CoachPath to confirm."
            ),
            handoff_initiated_at=draft.handoff_initiated_at or now,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Confirm Sent
    # ─────────────────────────────────────────────────────────────────────────

    async def confirm_outreach_sent(
        self,
        draft_id: uuid.UUID,
        user: User,
        request: RecruiterOutreachSentConfirmRequest,
        db: AsyncSession,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> RecruiterOutreachDraft:
        """
        Records candidate explicit confirmation that message was manually sent.
        """
        draft = await self.get_outreach_draft(draft_id=draft_id, user=user, db=db)

        if not request.user_confirmation:
            raise ValidationException(
                "Explicit user_confirmation=True is required to confirm outreach sent."
            )

        if draft.status not in ("approved", "handoff_initiated", "sent"):
            raise ConflictException(
                "Recruiter outreach draft must be approved before sent status can be confirmed."
            )

        # Idempotent handling for duplicate confirmation
        if draft.user_confirmed_sent and draft.status == "sent":
            return draft

        now = _utc_now()
        draft.user_confirmed_sent = True
        draft.status = "sent"
        draft.sent_at = now
        draft.updated_at = now

        # Record security audit log
        meta = request_metadata or {}
        audit_entry = AuditLog(
            user_id=user.id,
            action_type="RECRUITER_OUTREACH_SENT_CONFIRMED",
            target_entity_type="recruiter_outreach_draft",
            target_entity_id=draft.id,
            diff_payload={
                "status": "sent",
                "user_confirmed": True,
                "notes": request.notes,
            },
            human_approved=True,
            client_ip_hash=meta.get("client_ip_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            user_agent=meta.get("user_agent", "CoachPath API"),
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(draft)

        logger.info(f"Recruiter outreach draft {draft.id} sent confirmed by candidate {user.id}")
        return draft

    # ─────────────────────────────────────────────────────────────────────────
    # 7. Cancel & Delete
    # ─────────────────────────────────────────────────────────────────────────

    async def cancel_outreach_draft(
        self,
        draft_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> RecruiterOutreachDraft:
        """Cancels an outreach draft."""
        draft = await self.get_outreach_draft(draft_id=draft_id, user=user, db=db)

        if draft.status == "sent":
            raise ConflictException("Cannot cancel an outreach draft that has already been confirmed as sent.")

        draft.status = "cancelled"
        draft.updated_at = _utc_now()
        await db.commit()
        await db.refresh(draft)
        return draft

    async def delete_outreach_draft(
        self,
        draft_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> None:
        """Permanently deletes an outreach draft."""
        draft = await self.get_outreach_draft(draft_id=draft_id, user=user, db=db)
        await db.delete(draft)
        await db.commit()

    # ─────────────────────────────────────────────────────────────────────────
    # 8. Helper Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def _resolve_target_job_and_package(
        self,
        user: User,
        request: RecruiterOutreachCreateRequest,
        db: AsyncSession,
    ) -> Tuple[Job, Optional[ApplicationPackage]]:
        """Resolves target job and optional application package with ownership checks."""
        package = None
        if request.application_package_id:
            stmt = (
                select(ApplicationPackage)
                .options(selectinload(ApplicationPackage.job))
                .where(ApplicationPackage.id == request.application_package_id)
            )
            package = await db.scalar(stmt)
            if not package:
                raise NotFoundException("ApplicationPackage")
            if package.user_id != user.id and user.role != "admin":
                raise ForbiddenException("You do not have permission to access this application package.")
            return package.job, package

        if request.job_id:
            stmt = select(Job).where(Job.id == request.job_id)
            job = await db.scalar(stmt)
            if not job:
                raise NotFoundException("Job")
            return job, None

        raise ValidationException("Either application_package_id or job_id must be provided.")

    async def _count_active_drafts_for_job(
        self,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        db: AsyncSession,
    ) -> int:
        """Counts existing non-cancelled drafts for candidate and job."""
        stmt = (
            select(func.count(RecruiterOutreachDraft.id))
            .where(
                RecruiterOutreachDraft.user_id == user_id,
                RecruiterOutreachDraft.job_id == job_id,
                RecruiterOutreachDraft.status != "cancelled",
            )
        )
        count = await db.scalar(stmt)
        return count or 0

    async def _fetch_candidate_profile(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> Optional[CareerProfile]:
        """Loads candidate's career profile with evidence graph."""
        stmt = (
            select(CareerProfile)
            .options(
                selectinload(CareerProfile.user_skills),
                selectinload(CareerProfile.experience),
                selectinload(CareerProfile.projects),
            )
            .where(CareerProfile.user_id == user_id)
        )
        return await db.scalar(stmt)


recruiter_outreach_service = RecruiterOutreachService()
