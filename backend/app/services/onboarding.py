"""
AI-Powered Career Onboarding Service.
Orchestrates the onboarding interview conversation, LLM provider integration,
structured output validation, session state transitions, and truthful profile merging.

Core Architecture Invariants:
1. LLM proposes questions, extracts stated facts, and synthesizes summaries.
2. The application controls state transitions, enforces data constraints, and persists to DB.
3. The LLM never queries or writes to the database directly.
4. Truthfulness: Only user-stated facts are preserved; zero hallucinated credentials.
"""

from __future__ import annotations

import decimal
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.base import LLMProvider
from app.ai.prompts.onboarding_v1 import (
    NEXT_QUESTION_PROMPT_TEMPLATE,
    ONBOARDING_SYSTEM_PROMPT,
    SUMMARY_GENERATION_PROMPT_TEMPLATE,
)
from app.core.config import settings
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ServiceUnavailableException,
    ValidationException,
)
from app.models.auth import User
from app.models.career import CareerProfile, Role
from app.models.onboarding import OnboardingSession, OnboardingTurn
from app.schemas.onboarding import (
    ConfirmSummaryRequest,
    ConversationTurnResponse,
    OnboardingAIResponse,
    OnboardingProgressResponse,
    OnboardingSessionResponse,
    OnboardingStatus,
    OnboardingSummaryResponse,
    OnboardingSummarySchema,
    StartOnboardingResponse,
    SubmitResponseResult,
)

logger = logging.getLogger(__name__)

# Canonical discovery categories
ONBOARDING_AREAS: List[str] = [
    "target_role",
    "career_stage",
    "education",
    "skills",
    "technologies",
    "projects",
    "experience",
    "learning_time",
    "learning_resources",
    "timeline",
    "industries",
    "companies",
    "salary",
    "goals",
    "preferences",
]

CORE_REQUIRED_AREAS = {"target_role", "career_stage", "education", "skills"}

OPENING_QUESTION = (
    "Hi there! I'm your CoachPath career onboarding guide. Let's start with your target — "
    "what specific role or career path are you aiming for? "
    "(For example: Backend Developer, Full Stack Engineer, AI Engineer, Data Scientist, etc.)"
)
OPENING_CATEGORY = "target_role"


def _utc_now() -> datetime:
    """Returns current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


def _safe_json(obj: Any) -> str:
    """Serializes arbitrary Python objects to sanitized JSON for prompt quarantine."""
    try:
        return json.dumps(obj, default=str, ensure_ascii=False, indent=2)
    except Exception:
        return "{}"


class OnboardingService:
    """
    Encapsulates business operations and state management for career onboarding.
    """

    async def get_session_for_user(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> Optional[OnboardingSession]:
        """Loads the single onboarding session for the specified user ID."""
        stmt = (
            select(OnboardingSession)
            .options(selectinload(OnboardingSession.turns))
            .where(OnboardingSession.user_id == user_id)
        )
        return await db.scalar(stmt)

    async def _require_session(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> OnboardingSession:
        """Loads the session or raises 404 NotFoundException."""
        session = await self.get_session_for_user(user_id, db)
        if not session:
            raise NotFoundException("OnboardingSession", identifier=str(user_id))
        return session

    def _enforce_ownership(self, session: OnboardingSession, user: User) -> None:
        """Blocks cross-user access unless caller is an administrator."""
        if session.user_id != user.id and user.role != "admin":
            raise ForbiddenException("You do not have permission to access this onboarding session.")

    async def start_or_resume(
        self,
        user: User,
        db: AsyncSession,
    ) -> StartOnboardingResponse:
        """
        Starts a new onboarding session or resumes an ongoing session.
        If onboarding was already completed, raises 409 ConflictException.
        """
        existing = await self.get_session_for_user(user.id, db)

        if existing:
            if existing.status == OnboardingStatus.COMPLETED:
                raise ConflictException("Onboarding has already been completed for this account.")

            # Resuming existing in-progress or awaiting-confirmation session
            q = existing.current_question or OPENING_QUESTION
            cat = existing.current_question_category or OPENING_CATEGORY
            return StartOnboardingResponse(
                session_id=existing.id,
                status=existing.status,
                is_resumed=True,
                first_question=q,
                first_question_category=cat,
                message="Welcome back! Resuming your career onboarding where you left off.",
            )

        # Fresh session initialization
        new_session = OnboardingSession(
            user_id=user.id,
            status=OnboardingStatus.IN_PROGRESS,
            current_question=OPENING_QUESTION,
            current_question_category=OPENING_CATEGORY,
            turn_count=0,
            collected_facts={},
            areas_covered=[],
        )
        db.add(new_session)
        await db.flush()

        # Create turn 1 awaiting user response
        turn_1 = OnboardingTurn(
            session_id=new_session.id,
            turn_number=1,
            question=OPENING_QUESTION,
            question_category=OPENING_CATEGORY,
        )
        db.add(turn_1)
        await db.commit()
        await db.refresh(new_session)

        return StartOnboardingResponse(
            session_id=new_session.id,
            status=new_session.status,
            is_resumed=False,
            first_question=OPENING_QUESTION,
            first_question_category=OPENING_CATEGORY,
            message="Welcome to CoachPath! Let's build your career profile together.",
        )

    async def get_progress(
        self,
        user: User,
        db: AsyncSession,
    ) -> OnboardingProgressResponse:
        """Returns progress indicators on covered areas and summary readiness."""
        session = await self._require_session(user.id, db)
        self._enforce_ownership(session, user)

        areas_covered = session.areas_covered or []
        remaining = [a for a in ONBOARDING_AREAS if a not in areas_covered]
        core_met = CORE_REQUIRED_AREAS.issubset(set(areas_covered))

        return OnboardingProgressResponse(
            session_id=session.id,
            status=session.status,
            turn_count=session.turn_count,
            areas_covered=areas_covered,
            areas_remaining=remaining,
            ready_to_summarize=core_met and len(areas_covered) >= 5,
            current_question=session.current_question,
        )

    async def get_history(
        self,
        user: User,
        db: AsyncSession,
    ) -> List[ConversationTurnResponse]:
        """Returns all conversational turns chronologically."""
        session = await self._require_session(user.id, db)
        self._enforce_ownership(session, user)

        stmt = (
            select(OnboardingTurn)
            .where(OnboardingTurn.session_id == session.id)
            .order_by(OnboardingTurn.turn_number)
        )
        turns = (await db.scalars(stmt)).all()

        return [
            ConversationTurnResponse(
                turn_id=t.id,
                turn_number=t.turn_number,
                question=t.question,
                question_category=t.question_category,
                user_response=t.user_response,
                responded_at=t.responded_at,
                created_at=t.created_at,
            )
            for t in turns
        ]

    async def submit_response(
        self,
        user: User,
        response_text: str,
        llm: LLMProvider,
        db: AsyncSession,
    ) -> SubmitResponseResult:
        """
        Validates and records candidate response, invokes AI to extract facts and plan
        the next question, updates session state, and checks for summary completion.
        """
        session = await self._require_session(user.id, db)
        self._enforce_ownership(session, user)

        if session.status != OnboardingStatus.IN_PROGRESS:
            raise ConflictException(
                f"Cannot submit response when onboarding status is '{session.status}'. "
                "The session is either awaiting confirmation or already completed."
            )

        sanitized_input = response_text.strip()[:2000]

        # Locate the active pending turn
        stmt = (
            select(OnboardingTurn)
            .where(
                OnboardingTurn.session_id == session.id,
                OnboardingTurn.user_response.is_(None),
            )
            .order_by(OnboardingTurn.turn_number)
        )
        current_turn = await db.scalar(stmt)

        if not current_turn:
            raise ConflictException("No active question pending response in this session.")

        # Record answer
        now = _utc_now()
        current_turn.user_response = sanitized_input
        current_turn.responded_at = now

        # Enforce maximum conversation turns cap (default 20)
        if session.turn_count >= settings.ONBOARDING_MAX_TURNS - 1:
            session.turn_count += 1
            session.last_activity_at = now
            session.status = OnboardingStatus.AWAITING_CONFIRMATION
            session.current_question = None
            session.current_question_category = None
            current_turn.extracted_facts = {}
            await db.commit()
            await db.refresh(session)

            await self._generate_summary_internal(session, llm, db)
            return SubmitResponseResult(
                turn_completed=ConversationTurnResponse(
                    turn_id=current_turn.id,
                    turn_number=current_turn.turn_number,
                    question=current_turn.question,
                    question_category=current_turn.question_category,
                    user_response=current_turn.user_response,
                    responded_at=current_turn.responded_at,
                    created_at=current_turn.created_at,
                ),
                next_question=None,
                next_question_category=None,
                session_status=OnboardingStatus.AWAITING_CONFIRMATION,
                ready_to_summarize=True,
            )

        # Assemble recent conversation context for the model
        history_stmt = (
            select(OnboardingTurn)
            .where(OnboardingTurn.session_id == session.id)
            .order_by(OnboardingTurn.turn_number.desc())
            .limit(8)
        )
        recent_turns = list(reversed((await db.scalars(history_stmt)).all()))
        history_records = [
            {
                "turn": t.turn_number,
                "question": t.question,
                "category": t.question_category,
                "response": t.user_response,
            }
            for t in recent_turns
        ]

        areas_covered = list(session.areas_covered or [])
        remaining = [a for a in ONBOARDING_AREAS if a not in areas_covered]

        prompt = NEXT_QUESTION_PROMPT_TEMPLATE.format(
            collected_facts_json=_safe_json(session.collected_facts or {}),
            areas_covered_json=_safe_json(areas_covered),
            areas_remaining_json=_safe_json(remaining),
            history_json=_safe_json(history_records),
            user_input=sanitized_input,
        )

        try:
            ai_response: OnboardingAIResponse = await llm.generate_structured(
                prompt=prompt,
                schema=OnboardingAIResponse,
                system_prompt=ONBOARDING_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1024,
            )
        except ServiceUnavailableException:
            raise
        except Exception as exc:
            logger.error("LLM reasoning error during onboarding turn: %s", exc)
            raise ServiceUnavailableException("AI", f"Onboarding reasoning failure: {exc}") from exc

        # Extract and accumulate only user-stated facts
        accumulated_facts = dict(session.collected_facts or {})
        turn_extracted: Dict[str, Any] = {}
        for fact in ai_response.extracted_facts:
            if fact.confidence == "user_stated":
                accumulated_facts[fact.field] = fact.value
                turn_extracted[fact.field] = fact.value

        current_turn.extracted_facts = turn_extracted

        # Track areas covered
        if current_turn.question_category not in areas_covered:
            areas_covered.append(current_turn.question_category)

        # Update session state
        session.collected_facts = accumulated_facts
        session.areas_covered = areas_covered
        session.turn_count += 1
        session.last_activity_at = now

        # Determine if conversation is ready to transition to summary
        is_ready = (
            ai_response.ready_to_summarize
            or (CORE_REQUIRED_AREAS.issubset(set(areas_covered)) and len(areas_covered) >= 6)
            or len(remaining) <= 2
        )

        if is_ready:
            session.status = OnboardingStatus.AWAITING_CONFIRMATION
            session.current_question = None
            session.current_question_category = None
            await db.commit()
            await db.refresh(session)

            await self._generate_summary_internal(session, llm, db)

            return SubmitResponseResult(
                turn_completed=ConversationTurnResponse(
                    turn_id=current_turn.id,
                    turn_number=current_turn.turn_number,
                    question=current_turn.question,
                    question_category=current_turn.question_category,
                    user_response=current_turn.user_response,
                    responded_at=current_turn.responded_at,
                    created_at=current_turn.created_at,
                ),
                next_question=None,
                next_question_category=None,
                session_status=OnboardingStatus.AWAITING_CONFIRMATION,
                ready_to_summarize=True,
            )

        # Plan next turn
        next_q = ai_response.clarification_needed or ai_response.next_question
        next_cat = ai_response.question_category

        next_turn = OnboardingTurn(
            session_id=session.id,
            turn_number=session.turn_count + 1,
            question=next_q,
            question_category=next_cat,
        )
        db.add(next_turn)
        session.current_question = next_q
        session.current_question_category = next_cat

        await db.commit()
        await db.refresh(current_turn)

        return SubmitResponseResult(
            turn_completed=ConversationTurnResponse(
                turn_id=current_turn.id,
                turn_number=current_turn.turn_number,
                question=current_turn.question,
                question_category=current_turn.question_category,
                user_response=current_turn.user_response,
                responded_at=current_turn.responded_at,
                created_at=current_turn.created_at,
            ),
            next_question=next_q,
            next_question_category=next_cat,
            session_status=OnboardingStatus.IN_PROGRESS,
            ready_to_summarize=False,
        )

    async def _generate_summary_internal(
        self,
        session: OnboardingSession,
        llm: LLMProvider,
        db: AsyncSession,
    ) -> OnboardingSummaryResponse:
        """Generates structured career summary from gathered conversation facts."""
        history_stmt = (
            select(OnboardingTurn)
            .where(OnboardingTurn.session_id == session.id)
            .order_by(OnboardingTurn.turn_number)
        )
        all_turns = (await db.scalars(history_stmt)).all()
        history_records = [
            {"turn": t.turn_number, "question": t.question, "response": t.user_response}
            for t in all_turns
            if t.user_response
        ]

        prompt = SUMMARY_GENERATION_PROMPT_TEMPLATE.format(
            collected_facts_json=_safe_json(session.collected_facts or {}),
            history_json=_safe_json(history_records),
        )

        try:
            summary: OnboardingSummarySchema = await llm.generate_structured(
                prompt=prompt,
                schema=OnboardingSummarySchema,
                system_prompt=ONBOARDING_SYSTEM_PROMPT,
                temperature=0.2,
                max_tokens=2048,
            )
        except ServiceUnavailableException:
            # Fallback summary constructed directly from accumulated facts
            summary = self._build_deterministic_summary(session.collected_facts or {})

        now = _utc_now()
        session.ai_summary = summary.model_dump()
        session.summary_generated_at = now
        await db.commit()
        await db.refresh(session)

        return OnboardingSummaryResponse(
            session_id=session.id,
            summary=summary,
            generated_at=now,
            is_confirmed=False,
            confirmed_at=None,
        )

    def _build_deterministic_summary(self, facts: Dict[str, Any]) -> OnboardingSummarySchema:
        """Constructs an unembellished summary directly from raw extracted facts."""
        skills = facts.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]

        techs = facts.get("technologies", [])
        if isinstance(techs, str):
            techs = [t.strip() for t in techs.split(",") if t.strip()]

        locs = facts.get("target_locations", [])
        if isinstance(locs, str):
            locs = [l.strip() for l in locs.split(",") if l.strip()]

        return OnboardingSummarySchema(
            target_role=facts.get("target_role"),
            career_stage=facts.get("career_stage"),
            current_education=facts.get("education"),
            education_field=facts.get("education_field"),
            skills=skills if isinstance(skills, list) else [],
            technologies=techs if isinstance(techs, list) else [],
            career_goals=facts.get("goals"),
            work_preference=facts.get("work_preference"),
            target_locations=locs if isinstance(locs, list) else [],
            missing_areas=[a for a in CORE_REQUIRED_AREAS if a not in facts],
            uncertain_fields=["Deterministic summary synthesized without live LLM inference."],
        )

    async def get_summary(
        self,
        user: User,
        db: AsyncSession,
    ) -> OnboardingSummaryResponse:
        """Retrieves the candidate's synthesized career summary awaiting review."""
        session = await self._require_session(user.id, db)
        self._enforce_ownership(session, user)

        if session.status not in (OnboardingStatus.AWAITING_CONFIRMATION, OnboardingStatus.COMPLETED):
            raise ConflictException(
                f"Summary is not available when session status is '{session.status}'. "
                "Complete the discovery interview first."
            )

        if not session.ai_summary:
            raise NotFoundException("OnboardingSummary", identifier=str(session.id))

        return OnboardingSummaryResponse(
            session_id=session.id,
            summary=OnboardingSummarySchema.model_validate(session.ai_summary),
            generated_at=session.summary_generated_at or session.created_at,
            is_confirmed=session.is_summary_confirmed,
            confirmed_at=session.summary_confirmed_at,
        )

    async def confirm_summary(
        self,
        user: User,
        request: ConfirmSummaryRequest,
        db: AsyncSession,
    ) -> OnboardingSessionResponse:
        """
        Finalizes onboarding: validates user confirmation, applies career profile updates,
        and marks the session completed in an atomic transaction.
        """
        session = await self._require_session(user.id, db)
        self._enforce_ownership(session, user)

        if session.status == OnboardingStatus.COMPLETED:
            raise ConflictException("Onboarding has already been confirmed and completed.")

        if session.status != OnboardingStatus.AWAITING_CONFIRMATION:
            raise ConflictException(
                f"Cannot confirm summary when session status is '{session.status}'."
            )

        if not request.confirmed:
            raise ValidationException("Field 'confirmed' must be explicitly set to True.")

        # Determine effective summary (user edits supersede AI-generated summary)
        if request.edits is not None:
            effective_summary = request.edits
        else:
            effective_summary = OnboardingSummarySchema.model_validate(session.ai_summary or {})

        # Atomically apply confirmed values to CareerProfile
        await self._apply_summary_to_career_profile(user, effective_summary, db)

        now = _utc_now()
        session.status = OnboardingStatus.COMPLETED
        session.is_summary_confirmed = True
        session.summary_confirmed_at = now
        session.completed_at = now
        session.last_activity_at = now
        # Store user edits if provided
        if request.edits is not None:
            session.ai_summary = request.edits.model_dump()

        await db.commit()
        await db.refresh(session)

        return OnboardingSessionResponse(
            session_id=session.id,
            status=session.status,
            current_question=None,
            current_question_category=None,
            turn_count=session.turn_count,
            started_at=session.created_at,
            last_activity_at=session.last_activity_at,
            completed_at=session.completed_at,
        )

    async def _apply_summary_to_career_profile(
        self,
        user: User,
        summary: OnboardingSummarySchema,
        db: AsyncSession,
    ) -> None:
        """
        Truthful, non-destructive merging of confirmed onboarding facts into CareerProfile.
        Preserves existing evidence records; updates baseline preferences and targets.
        """
        stmt = (
            select(CareerProfile)
            .where(CareerProfile.user_id == user.id)
        )
        profile = await db.scalar(stmt)
        if not profile:
            # Ensure fallback default role exists in database
            default_role_id = "backend-developer"
            role = await db.scalar(select(Role).where(Role.id == default_role_id))
            if role is None:
                role = await db.scalar(select(Role))
                if role is None:
                    role = Role(
                        id="backend-developer",
                        title="Backend Developer",
                        description="Server-side web applications and scalable APIs.",
                        category="engineering",
                    )
                    db.add(role)
                    await db.flush()
                default_role_id = role.id

            profile = CareerProfile(
                user_id=user.id,
                primary_role_id=default_role_id,
                career_stage="student",
                work_preference="hybrid",
                target_locations=["Remote"],
                years_of_experience=decimal.Decimal("0.0"),
            )
            db.add(profile)
            await db.flush()

        # 1. Map work_preference
        valid_preferences = {"remote", "hybrid", "onsite", "flexible"}
        if summary.work_preference:
            norm_pref = summary.work_preference.strip().lower()
            if norm_pref in valid_preferences:
                profile.work_preference = norm_pref
            elif "remote" in norm_pref:
                profile.work_preference = "remote"
            elif "hybrid" in norm_pref:
                profile.work_preference = "hybrid"
            elif "onsite" in norm_pref or "office" in norm_pref:
                profile.work_preference = "onsite"

        # 2. Map career_stage
        valid_stages = {
            "student": "student",
            "recent_graduate": "recent_graduate",
            "recent graduate": "recent_graduate",
            "early_career": "early_career",
            "early career": "early_career",
            "junior": "early_career",
            "entry": "early_career",
        }
        if summary.career_stage:
            norm_stage = summary.career_stage.strip().lower()
            mapped = valid_stages.get(norm_stage)
            if mapped:
                profile.career_stage = mapped

        # 3. Target locations
        if summary.target_locations:
            clean_locs = [loc.strip() for loc in summary.target_locations if loc.strip()]
            if clean_locs:
                profile.target_locations = clean_locs

        # 4. Years of experience
        if summary.years_of_experience is not None and summary.years_of_experience >= 0.0:
            profile.years_of_experience = decimal.Decimal(str(round(summary.years_of_experience, 1)))

        # 5. Target primary role matching
        if summary.target_role:
            role_query = summary.target_role.strip().lower()
            role_stmt = select(Role).where(
                sa.or_(
                    sa.func.lower(Role.title) == role_query,
                    sa.func.lower(Role.id) == role_query,
                    sa.func.lower(Role.title).contains(role_query),
                )
            )
            matched_role = await db.scalar(role_stmt)
            if matched_role:
                profile.primary_role_id = matched_role.id

        await db.flush()
