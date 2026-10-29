"""
Diagnostic Skill Assessments Service.
Orchestrates multi-question category listings, attempt lifecycle management,
server-side deterministic grading, scoring, answer protection, and retake persistence.
"""

from __future__ import annotations

import decimal
import logging
import random
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
)
from app.models.assessments import (
    Assessment,
    AssessmentAnswer,
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentResult,
)
from app.models.auth import User
from app.models.career import CareerProfile
from app.models.skills import Skill, UserSkill
from app.models.base import utc_now
from app.schemas.assessments import (
    AssessmentCategoryListItem,
    AssessmentDetailResponse,
    AssessmentResultResponse,
    AttemptHistoryItem,
    AttemptQuestionPublic,
    AttemptSessionResponse,
    DifficultyScore,
    GradedQuestionResult,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TopicScore,
)

logger = logging.getLogger(__name__)

# Default question distribution per diagnostic assessment attempt
TARGET_ATTEMPT_COUNT = 20
TARGET_BASIC_COUNT = 7
TARGET_INTERMEDIATE_COUNT = 7
TARGET_ADVANCED_COUNT = 6


class AssessmentService:
    """
    Core business logic engine for CoachPath Diagnostic Skill Assessments.
    Enforces deterministic autograding without LLM hallucination.
    """

    async def list_categories(
        self,
        user: User,
        db: AsyncSession,
    ) -> List[AssessmentCategoryListItem]:
        """
        Lists all 9 diagnostic assessment categories annotated with the authenticated
        candidate's attempt history, status, and best score.
        """
        # 1. Fetch all active assessments
        stmt = (
            select(Assessment)
            .where(Assessment.is_active.is_(True))
            .order_by(Assessment.created_at)
        )
        assessments = (await db.scalars(stmt)).all()

        # 2. Fetch all user attempts across assessments
        user_attempts_stmt = (
            select(AssessmentAttempt)
            .where(AssessmentAttempt.user_id == user.id)
            .order_by(desc(AssessmentAttempt.started_at))
        )
        user_attempts = (await db.scalars(user_attempts_stmt)).all()

        # Group attempts by assessment_id
        attempts_by_assessment: Dict[uuid.UUID, List[AssessmentAttempt]] = {}
        for att in user_attempts:
            attempts_by_assessment.setdefault(att.assessment_id, []).append(att)

        result_list: List[AssessmentCategoryListItem] = []

        for asmt in assessments:
            # Query question count in question bank
            q_count_stmt = (
                select(func.count(AssessmentQuestion.id))
                .where(AssessmentQuestion.assessment_id == asmt.id)
            )
            q_count = await db.scalar(q_count_stmt) or 0

            cat_attempts = attempts_by_assessment.get(asmt.id, [])
            attempt_count = len(cat_attempts)

            # Determine status and best score
            user_status = "available"
            user_best_score: Optional[float] = None
            last_attempt_at: Optional[datetime] = None

            # Check for active in_progress attempt
            in_prog = next((a for a in cat_attempts if a.status == "in_progress"), None)
            completed_attempts = [a for a in cat_attempts if a.status == "completed" and a.score_percentage is not None]

            if in_prog:
                user_status = "in_progress"
                last_attempt_at = in_prog.started_at
            elif completed_attempts:
                user_status = "completed"
                last_attempt_at = completed_attempts[0].completed_at or completed_attempts[0].started_at

            if completed_attempts:
                best_decimal = max(a.score_percentage for a in completed_attempts if a.score_percentage is not None)
                user_best_score = float(best_decimal)

            result_list.append(
                AssessmentCategoryListItem(
                    id=asmt.id,
                    skill_id=asmt.skill_id,
                    title=asmt.title,
                    description=asmt.description,
                    time_limit_minutes=asmt.time_limit_minutes,
                    passing_threshold=float(asmt.passing_threshold),
                    question_count=q_count,
                    user_status=user_status,
                    user_best_score=user_best_score,
                    last_attempt_at=last_attempt_at,
                    attempt_count=attempt_count,
                )
            )

        return result_list

    async def get_assessment_detail(
        self,
        identifier: str,
        db: AsyncSession,
    ) -> AssessmentDetailResponse:
        """
        Retrieves detailed assessment metadata, difficulty distribution, and syllabus topics
        by assessment UUID or skill_id.
        """
        assessment = await self._resolve_assessment(identifier, db)

        # Query all questions for this assessment
        stmt = (
            select(AssessmentQuestion)
            .where(AssessmentQuestion.assessment_id == assessment.id)
        )
        questions = (await db.scalars(stmt)).all()

        diff_counts: Dict[str, int] = {"basic": 0, "intermediate": 0, "advanced": 0}
        unique_topics: set[str] = set()

        for q in questions:
            diff_counts[q.difficulty] = diff_counts.get(q.difficulty, 0) + 1
            if q.topic:
                unique_topics.add(q.topic)

        return AssessmentDetailResponse(
            id=assessment.id,
            skill_id=assessment.skill_id,
            title=assessment.title,
            description=assessment.description,
            time_limit_minutes=assessment.time_limit_minutes,
            passing_threshold=float(assessment.passing_threshold),
            total_bank_questions=len(questions),
            attempt_question_count=min(TARGET_ATTEMPT_COUNT, len(questions)),
            difficulty_breakdown=diff_counts,
            topics=sorted(list(unique_topics)),
        )

    async def start_or_resume_attempt(
        self,
        identifier: str,
        user: User,
        db: AsyncSession,
    ) -> AttemptSessionResponse:
        """
        Commences a new 20-question diagnostic attempt or resumes an existing active attempt.
        Drives the 7-7-6 difficulty distribution across basic, intermediate, and advanced tiers.
        """
        assessment = await self._resolve_assessment(identifier, db)

        # 1. Check for existing active attempt (Resume behavior)
        active_stmt = (
            select(AssessmentAttempt)
            .where(
                AssessmentAttempt.user_id == user.id,
                AssessmentAttempt.assessment_id == assessment.id,
                AssessmentAttempt.status == "in_progress",
            )
            .order_by(desc(AssessmentAttempt.started_at))
        )
        existing_attempt = await db.scalar(active_stmt)

        if existing_attempt and existing_attempt.question_ids:
            return await self._build_attempt_session(existing_attempt, assessment, db)

        # 2. Select 20 questions with difficulty distribution and retake diversity
        q_stmt = (
            select(AssessmentQuestion)
            .where(AssessmentQuestion.assessment_id == assessment.id)
        )
        all_questions = (await db.scalars(q_stmt)).all()

        if len(all_questions) < TARGET_ATTEMPT_COUNT:
            raise ValidationException(
                f"Question bank for '{assessment.title}' contains only {len(all_questions)} questions; "
                f"minimum {TARGET_ATTEMPT_COUNT} required to start diagnostic attempt."
            )

        # Query prior attempts to inform question exposure diversity
        history_stmt = (
            select(AssessmentAttempt)
            .where(
                AssessmentAttempt.user_id == user.id,
                AssessmentAttempt.assessment_id == assessment.id,
                AssessmentAttempt.status.in_(["completed", "timed_out", "in_progress"]),
            )
            .order_by(desc(AssessmentAttempt.started_at))
        )
        prior_attempts = (await db.scalars(history_stmt)).all()

        rng = random.Random(f"{user.id}_{assessment.id}_{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex[:8]}")
        ordered_questions = self._select_diverse_questions(
            all_questions=all_questions,
            prior_attempts=prior_attempts,
            rng=rng,
            assessment_title=assessment.title,
        )
        selected_uuids = [str(q.id) for q in ordered_questions]

        # 3. Generate attempt-scoped randomized option orders per question
        option_orders: Dict[str, List[int]] = {}
        for q in ordered_questions:
            n = len(q.options)
            if n > 1:
                option_orders[str(q.id)] = rng.sample(range(n), n)
            else:
                option_orders[str(q.id)] = list(range(n))

        # 4. Create persistent AssessmentAttempt record with question IDs and option orders
        new_attempt = AssessmentAttempt(
            user_id=user.id,
            assessment_id=assessment.id,
            status="in_progress",
            question_ids=selected_uuids,
            option_orders=option_orders,
            started_at=utc_now(),
        )
        db.add(new_attempt)
        await db.commit()
        await db.refresh(new_attempt)

        return await self._build_attempt_session(new_attempt, assessment, db)

    async def get_active_attempt(
        self,
        attempt_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> AttemptSessionResponse:
        """
        Fetches an active attempt's session for the runner interface without revealing answer keys.
        """
        attempt = await db.get(AssessmentAttempt, attempt_id)
        if not attempt:
            raise NotFoundException("AssessmentAttempt")

        self._enforce_ownership(attempt, user)

        if attempt.status != "in_progress":
            raise ConflictException(
                f"Assessment attempt '{attempt_id}' is already {attempt.status}. "
                "View the final graded result instead."
            )

        stmt = (
            select(Assessment)
            .options(selectinload(Assessment.skill))
            .where(Assessment.id == attempt.assessment_id)
        )
        assessment = await db.scalar(stmt)
        if not assessment:
            raise NotFoundException("Assessment")

        return await self._build_attempt_session(attempt, assessment, db)

    async def submit_answer(
        self,
        attempt_id: uuid.UUID,
        request: SubmitAnswerRequest,
        user: User,
        db: AsyncSession,
    ) -> SubmitAnswerResponse:
        """
        Records or updates a candidate's answer selection for a question within an active attempt.
        """
        attempt = await db.get(AssessmentAttempt, attempt_id)
        if not attempt:
            raise NotFoundException("AssessmentAttempt")

        self._enforce_ownership(attempt, user)

        if attempt.status != "in_progress":
            raise ConflictException(f"Cannot submit answers to an attempt with status '{attempt.status}'.")

        q_id_str = str(request.question_id)
        if not attempt.question_ids or q_id_str not in attempt.question_ids:
            raise ValidationException(f"Question '{request.question_id}' does not belong to this assessment attempt.")

        # Query question to verify option range and correct answer
        question = await db.get(AssessmentQuestion, request.question_id)
        if not question:
            raise NotFoundException("AssessmentQuestion")

        if request.selected_option_index >= len(question.options):
            raise ValidationException(
                f"Selected option index {request.selected_option_index} out of range (0-{len(question.options) - 1})."
            )

        # Map displayed option index back to canonical index using persisted option_orders
        canonical_option_index = request.selected_option_index
        if attempt.option_orders and q_id_str in attempt.option_orders:
            order = attempt.option_orders[q_id_str]
            if 0 <= request.selected_option_index < len(order):
                canonical_option_index = order[request.selected_option_index]

        is_correct = (canonical_option_index == question.correct_option_index)

        # Upsert answer record
        ans_stmt = (
            select(AssessmentAnswer)
            .where(
                AssessmentAnswer.attempt_id == attempt.id,
                AssessmentAnswer.question_id == request.question_id,
            )
        )
        existing_answer = await db.scalar(ans_stmt)

        if existing_answer:
            existing_answer.selected_option_index = request.selected_option_index
            existing_answer.is_correct = is_correct
            existing_answer.response_time_seconds = request.response_time_seconds
        else:
            new_answer = AssessmentAnswer(
                attempt_id=attempt.id,
                question_id=request.question_id,
                selected_option_index=request.selected_option_index,
                is_correct=is_correct,
                response_time_seconds=request.response_time_seconds,
            )
            db.add(new_answer)

        await db.commit()

        # Count total answered questions
        count_stmt = (
            select(func.count(AssessmentAnswer.id))
            .where(AssessmentAnswer.attempt_id == attempt.id)
        )
        answered_count = await db.scalar(count_stmt) or 0

        return SubmitAnswerResponse(
            attempt_id=attempt.id,
            question_id=request.question_id,
            selected_option_index=request.selected_option_index,
            answered_count=answered_count,
            total_questions=len(attempt.question_ids),
        )

    async def complete_attempt(
        self,
        attempt_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> AssessmentResultResponse:
        """
        Finalizes an assessment attempt, executes server-side grading, generates
        topic and difficulty breakdowns, creates the AssessmentResult, and updates user skill evidence.
        """
        stmt = (
            select(AssessmentAttempt)
            .options(
                selectinload(AssessmentAttempt.assessment).selectinload(Assessment.skill),
                selectinload(AssessmentAttempt.answers),
                selectinload(AssessmentAttempt.result),
            )
            .where(AssessmentAttempt.id == attempt_id)
        )
        attempt = await db.scalar(stmt)
        if not attempt:
            raise NotFoundException("AssessmentAttempt")

        self._enforce_ownership(attempt, user)

        # Idempotent return if already completed
        if attempt.status == "completed" and attempt.result:
            return await self.get_attempt_result(attempt_id, user, db)

        if attempt.status not in ("in_progress", "timed_out"):
            raise ConflictException(f"Cannot complete attempt with status '{attempt.status}'.")

        question_uuids = [uuid.UUID(qid) for qid in (attempt.question_ids or [])]
        if not question_uuids:
            raise ValidationException("Attempt has no associated question IDs.")

        # Load questions in ordered sequence
        q_stmt = (
            select(AssessmentQuestion)
            .where(AssessmentQuestion.id.in_(question_uuids))
        )
        questions_map = {q.id: q for q in (await db.scalars(q_stmt)).all()}

        # Load existing answers
        ans_map = {a.question_id: a for a in attempt.answers}

        total_questions = len(question_uuids)
        graded_questions, correct_count, topic_stats, diff_stats = self._grade_attempt_questions(
            attempt=attempt,
            question_uuids=question_uuids,
            questions_map=questions_map,
            ans_map=ans_map,
        )

        # Calculate calibrated percentage score (0.0 to 100.0)
        score_float = round((correct_count / total_questions) * 100.0, 1)
        score_decimal = decimal.Decimal(str(score_float))
        passing_threshold_float = float(attempt.assessment.passing_threshold)
        passed = (score_float >= passing_threshold_float)

        # Proficiency classification
        if score_float >= 85.0:
            proficiency_band = "Strong"
        elif score_float >= 70.0:
            proficiency_band = "Proficient"
        elif score_float >= 50.0:
            proficiency_band = "Developing"
        else:
            proficiency_band = "Foundational"

        # Topic breakdown list
        topic_breakdown_list: List[TopicScore] = []
        strong_topics: List[str] = []
        weak_topics: List[str] = []

        for topic_name, stats in topic_stats.items():
            tot = stats["total"]
            corr = stats["correct"]
            pct = round((corr / tot) * 100.0, 1) if tot > 0 else 0.0
            topic_breakdown_list.append(
                TopicScore(
                    topic=topic_name,
                    total=tot,
                    correct=corr,
                    percentage=pct,
                )
            )
            if pct >= 70.0:
                strong_topics.append(f"{topic_name} ({pct:.0f}%)")
            else:
                weak_topics.append(f"{topic_name} ({pct:.0f}%)")

        diff_breakdown_dict = {
            diff_name: DifficultyScore(
                total=s["total"],
                correct=s["correct"],
                percentage=round((s["correct"] / s["total"]) * 100.0, 1) if s["total"] > 0 else 0.0,
            )
            for diff_name, s in diff_stats.items()
        }

        # Synthesize deterministic pedagogical feedback
        strengths_str = (
            f"Demonstrated solid competency in: {', '.join(strong_topics)}."
            if strong_topics
            else "Foundation established; focus on core fundamentals to build mastery."
        )
        weaknesses_str = (
            f"Key focus areas for remediation: {', '.join(weak_topics)}."
            if weak_topics
            else "Exceptional performance across all assessed subtopics with minimal gaps."
        )

        remedial_milestones = [
            {
                "topic": t.topic,
                "recommendation": f"Review pedagogical mechanics and practice applied drills in {t.topic}.",
                "priority": "high" if t.percentage < 50.0 else "medium",
            }
            for t in topic_breakdown_list
            if t.percentage < 70.0
        ]

        # Confidence lift applied to UserSkill
        confidence_delta = decimal.Decimal(str(round(min(1.0, score_float / 100.0 * 0.40), 2)))

        # Update attempt fields
        now = utc_now()
        attempt.status = "completed"
        attempt.score_percentage = score_decimal
        attempt.passed = passed
        attempt.completed_at = now

        # Create or update AssessmentResult
        if not attempt.result:
            result = AssessmentResult(
                attempt_id=attempt.id,
                strengths_summary=strengths_str,
                weaknesses_summary=weaknesses_str,
                remedial_milestones=remedial_milestones,
                confidence_lift=confidence_delta,
                topic_breakdown=[t.model_dump() for t in topic_breakdown_list],
                difficulty_breakdown={k: v.model_dump() for k, v in diff_breakdown_dict.items()},
                created_at=now,
            )
            db.add(result)
        else:
            attempt.result.strengths_summary = strengths_str
            attempt.result.weaknesses_summary = weaknesses_str
            attempt.result.remedial_milestones = remedial_milestones
            attempt.result.confidence_lift = confidence_delta
            attempt.result.topic_breakdown = [t.model_dump() for t in topic_breakdown_list]
            attempt.result.difficulty_breakdown = {k: v.model_dump() for k, v in diff_breakdown_dict.items()}

        # 4. Atomically update CareerProfile UserSkill evidence
        await self._apply_diagnostic_to_user_skills(user, attempt.assessment.skill_id, score_float, passed, db)

        await db.commit()
        await db.refresh(attempt)

        return AssessmentResultResponse(
            attempt_id=attempt.id,
            assessment_id=attempt.assessment.id,
            assessment_title=attempt.assessment.title,
            skill_id=attempt.assessment.skill_id,
            skill_name=attempt.assessment.skill.name,
            status=attempt.status,
            score_percentage=score_float,
            passed=passed,
            passing_threshold=passing_threshold_float,
            proficiency_band=proficiency_band,
            strengths_summary=strengths_str,
            weaknesses_summary=weaknesses_str,
            remedial_milestones=remedial_milestones,
            topic_breakdown=topic_breakdown_list,
            difficulty_breakdown=diff_breakdown_dict,
            total_questions=total_questions,
            correct_count=correct_count,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            questions=graded_questions,
        )

    async def get_attempt_result(
        self,
        attempt_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> AssessmentResultResponse:
        """
        Retrieves the complete graded result and pedagogical review for a completed attempt.
        """
        stmt = (
            select(AssessmentAttempt)
            .options(
                selectinload(AssessmentAttempt.assessment).selectinload(Assessment.skill),
                selectinload(AssessmentAttempt.answers),
                selectinload(AssessmentAttempt.result),
            )
            .where(AssessmentAttempt.id == attempt_id)
        )
        attempt = await db.scalar(stmt)
        if not attempt:
            raise NotFoundException("AssessmentAttempt")

        self._enforce_ownership(attempt, user)

        if attempt.status != "completed" or not attempt.result:
            raise ConflictException(f"Attempt '{attempt_id}' is not yet finalized.")

        question_uuids = [uuid.UUID(qid) for qid in (attempt.question_ids or [])]
        q_stmt = (
            select(AssessmentQuestion)
            .where(AssessmentQuestion.id.in_(question_uuids))
        )
        questions_map = {q.id: q for q in (await db.scalars(q_stmt)).all()}
        ans_map = {a.question_id: a for a in attempt.answers}

        graded_questions, correct_count, _, _ = self._grade_attempt_questions(
            attempt=attempt,
            question_uuids=question_uuids,
            questions_map=questions_map,
            ans_map=ans_map,
        )

        score_float = float(attempt.score_percentage) if attempt.score_percentage is not None else 0.0
        if score_float >= 85.0:
            band = "Strong"
        elif score_float >= 70.0:
            band = "Proficient"
        elif score_float >= 50.0:
            band = "Developing"
        else:
            band = "Foundational"

        raw_topics = attempt.result.topic_breakdown or []
        raw_diffs = attempt.result.difficulty_breakdown or {}

        topic_breakdown = [TopicScore(**t) for t in raw_topics]
        difficulty_breakdown = {k: DifficultyScore(**v) for k, v in raw_diffs.items()}

        return AssessmentResultResponse(
            attempt_id=attempt.id,
            assessment_id=attempt.assessment.id,
            assessment_title=attempt.assessment.title,
            skill_id=attempt.assessment.skill_id,
            skill_name=attempt.assessment.skill.name,
            status=attempt.status,
            score_percentage=score_float,
            passed=bool(attempt.passed),
            passing_threshold=float(attempt.assessment.passing_threshold),
            proficiency_band=band,
            strengths_summary=attempt.result.strengths_summary,
            weaknesses_summary=attempt.result.weaknesses_summary,
            remedial_milestones=attempt.result.remedial_milestones or [],
            topic_breakdown=topic_breakdown,
            difficulty_breakdown=difficulty_breakdown,
            total_questions=len(question_uuids),
            correct_count=correct_count,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            questions=graded_questions,
        )

    async def get_user_history(
        self,
        user: User,
        db: AsyncSession,
    ) -> List[AttemptHistoryItem]:
        """
        Returns all historical assessment attempts for the user, preserving retake history.
        """
        stmt = (
            select(AssessmentAttempt)
            .options(
                selectinload(AssessmentAttempt.assessment).selectinload(Assessment.skill)
            )
            .where(AssessmentAttempt.user_id == user.id)
            .order_by(desc(AssessmentAttempt.started_at))
        )
        attempts = (await db.scalars(stmt)).all()

        return [
            AttemptHistoryItem(
                attempt_id=att.id,
                assessment_id=att.assessment.id,
                assessment_title=att.assessment.title,
                skill_id=att.assessment.skill_id,
                skill_name=att.assessment.skill.name,
                status=att.status,
                score_percentage=float(att.score_percentage) if att.score_percentage is not None else None,
                passed=att.passed,
                started_at=att.started_at,
                completed_at=att.completed_at,
            )
            for att in attempts
        ]

    # ─── Internal Helper Methods ─────────────────────────────────────────

    def _select_diverse_questions(
        self,
        all_questions: List[AssessmentQuestion],
        prior_attempts: List[AssessmentAttempt],
        rng: random.Random,
        assessment_title: str = "",
        target_count: int = TARGET_ATTEMPT_COUNT,
        target_basic: int = TARGET_BASIC_COUNT,
        target_inter: int = TARGET_INTERMEDIATE_COUNT,
        target_adv: int = TARGET_ADVANCED_COUNT,
    ) -> List[AssessmentQuestion]:
        """
        Selects target_count questions adhering to difficulty distribution while maximizing
        exposure diversity across successive attempts via a least-recently-seen (LRS) algorithm.
        """
        if len(all_questions) < target_count:
            raise ValidationException(
                f"Question bank for '{assessment_title}' contains only {len(all_questions)} questions; "
                f"minimum {target_count} required to start diagnostic attempt."
            )

        # 1. Map exposure history from prior attempts (most recent first)
        valid_priors = [a for a in prior_attempts if a.question_ids and len(a.question_ids) > 0]

        times_seen_map: Dict[str, int] = {}
        last_seen_idx_map: Dict[str, int] = {}  # 0 = immediately preceding attempt, 1 = 2 attempts ago, etc.

        for attempt_idx, att in enumerate(valid_priors):
            for q_id_str in (att.question_ids or []):
                times_seen_map[q_id_str] = times_seen_map.get(q_id_str, 0) + 1
                if q_id_str not in last_seen_idx_map:
                    last_seen_idx_map[q_id_str] = attempt_idx

        # 2. Partition question bank into difficulty pools
        basic_pool = [q for q in all_questions if (q.difficulty or "").lower() == "basic"]
        inter_pool = [q for q in all_questions if (q.difficulty or "").lower() == "intermediate"]
        adv_pool = [q for q in all_questions if (q.difficulty or "").lower() == "advanced"]

        # Validate difficulty distribution availability
        if len(basic_pool) < target_basic or len(inter_pool) < target_inter or len(adv_pool) < target_adv:
            available_total = len(basic_pool) + len(inter_pool) + len(adv_pool)
            if available_total < target_count:
                raise ValidationException(
                    f"Insufficient difficulty distribution in question bank: "
                    f"{len(basic_pool)} basic, {len(inter_pool)} intermediate, {len(adv_pool)} advanced."
                )

        # 3. Helper to rank questions within a pool by diversity
        def rank_pool_by_diversity(pool: List[AssessmentQuestion]) -> List[AssessmentQuestion]:
            # Tier 1: Questions never encountered in any prior attempt
            tier1 = [q for q in pool if times_seen_map.get(str(q.id), 0) == 0]
            rng.shuffle(tier1)

            # Tier 2: Questions not seen in immediately preceding attempt (last_seen_idx > 0)
            tier2 = [
                q for q in pool
                if str(q.id) in last_seen_idx_map and last_seen_idx_map[str(q.id)] > 0
            ]
            # Seen longest ago first (-last_seen_idx), then least frequently seen (times_seen ASC)
            tier2_scored = [
                (-last_seen_idx_map[str(q.id)], times_seen_map.get(str(q.id), 0), rng.random(), q)
                for q in tier2
            ]
            tier2_scored.sort(key=lambda x: (x[0], x[1], x[2]))
            tier2_sorted = [x[3] for x in tier2_scored]

            # Tier 3: Questions seen in immediately preceding attempt (last_seen_idx == 0)
            tier3 = [
                q for q in pool
                if str(q.id) in last_seen_idx_map and last_seen_idx_map[str(q.id)] == 0
            ]
            tier3_scored = [
                (times_seen_map.get(str(q.id), 0), rng.random(), q)
                for q in tier3
            ]
            tier3_scored.sort(key=lambda x: (x[0], x[1]))
            tier3_sorted = [x[2] for x in tier3_scored]

            return tier1 + tier2_sorted + tier3_sorted

        # Rank each tier
        ranked_basic = rank_pool_by_diversity(basic_pool)
        ranked_inter = rank_pool_by_diversity(inter_pool)
        ranked_adv = rank_pool_by_diversity(adv_pool)

        actual_basic_count = min(len(ranked_basic), target_basic)
        actual_inter_count = min(len(ranked_inter), target_inter)
        actual_adv_count = min(len(ranked_adv), target_adv)

        selected_basic = ranked_basic[:actual_basic_count]
        selected_inter = ranked_inter[:actual_inter_count]
        selected_adv = ranked_adv[:actual_adv_count]

        # Graceful shortfall handling if a tier has fewer questions than target
        selected_ids = {q.id for q in (selected_basic + selected_inter + selected_adv)}
        if len(selected_ids) < target_count:
            surplus_candidates = (
                [q for q in ranked_inter if q.id not in selected_ids]
                + [q for q in ranked_basic if q.id not in selected_ids]
                + [q for q in ranked_adv if q.id not in selected_ids]
            )
            for q in surplus_candidates:
                if len(selected_ids) >= target_count:
                    break
                selected_ids.add(q.id)
                if (q.difficulty or "").lower() == "basic":
                    selected_basic.append(q)
                elif (q.difficulty or "").lower() == "intermediate":
                    selected_inter.append(q)
                else:
                    selected_adv.append(q)

        # Maintain difficulty progression: basic -> intermediate -> advanced
        ordered_selection = selected_basic + selected_inter + selected_adv

        # Validate invariants: exact target count, zero duplicates
        if len(ordered_selection) != target_count:
            raise ValidationException(
                f"Selected {len(ordered_selection)} questions, expected {target_count}."
            )
        if len(set(q.id for q in ordered_selection)) != len(ordered_selection):
            raise ValidationException("Question selection contained duplicate items.")

        return ordered_selection

    def _grade_attempt_questions(
        self,
        attempt: AssessmentAttempt,
        question_uuids: List[uuid.UUID],
        questions_map: Dict[uuid.UUID, AssessmentQuestion],
        ans_map: Dict[uuid.UUID, AssessmentAnswer],
    ) -> Tuple[List[GradedQuestionResult], int, Dict[str, Dict[str, int]], Dict[str, Dict[str, int]]]:
        """
        Autogrades attempt questions, securely mapping displayed shuffled options back
        to canonical answers and calculating statistics.
        """
        correct_count = 0
        topic_stats: Dict[str, Dict[str, int]] = {}
        diff_stats: Dict[str, Dict[str, int]] = {
            "basic": {"total": 0, "correct": 0},
            "intermediate": {"total": 0, "correct": 0},
            "advanced": {"total": 0, "correct": 0},
        }
        graded_questions: List[GradedQuestionResult] = []

        for idx, q_id in enumerate(question_uuids, 1):
            q = questions_map.get(q_id)
            if not q:
                continue

            ans = ans_map.get(q_id)
            q_id_str = str(q.id)

            # Determine displayed options and displayed correct option index
            displayed_options = list(q.options)
            displayed_correct_idx = q.correct_option_index

            if attempt.option_orders and q_id_str in attempt.option_orders:
                order = attempt.option_orders[q_id_str]
                if len(order) == len(q.options):
                    displayed_options = [q.options[i] for i in order]
                    if q.correct_option_index in order:
                        displayed_correct_idx = order.index(q.correct_option_index)

            # Re-verify is_correct safely from canonical mapping
            selected_idx = ans.selected_option_index if ans else None
            if ans and attempt.option_orders and q_id_str in attempt.option_orders:
                order = attempt.option_orders[q_id_str]
                if 0 <= ans.selected_option_index < len(order):
                    canonical_selected = order[ans.selected_option_index]
                    is_correct = (canonical_selected == q.correct_option_index)
                else:
                    is_correct = False
            else:
                is_correct = bool(ans and ans.is_correct)

            if is_correct:
                correct_count += 1

            # Track difficulty stats
            diff_key = (q.difficulty or "").lower()
            if diff_key in diff_stats:
                diff_stats[diff_key]["total"] += 1
                if is_correct:
                    diff_stats[diff_key]["correct"] += 1

            # Track topic stats
            topic = q.topic or "General Concepts"
            if topic not in topic_stats:
                topic_stats[topic] = {"total": 0, "correct": 0}
            topic_stats[topic]["total"] += 1
            if is_correct:
                topic_stats[topic]["correct"] += 1

            graded_questions.append(
                GradedQuestionResult(
                    id=q.id,
                    index=idx,
                    prompt_text=q.prompt_text,
                    code_snippet=q.code_snippet,
                    options=displayed_options,
                    selected_option_index=selected_idx,
                    correct_option_index=displayed_correct_idx,
                    is_correct=is_correct,
                    explanation=q.explanation,
                    difficulty=q.difficulty,
                    topic=topic,
                )
            )

        return graded_questions, correct_count, topic_stats, diff_stats

    async def _resolve_assessment(
        self,
        identifier: str,
        db: AsyncSession,
    ) -> Assessment:
        """Resolves an assessment by its UUID string or canonical skill_id."""
        stmt = (
            select(Assessment)
            .options(selectinload(Assessment.skill))
            .where(Assessment.is_active.is_(True))
        )
        try:
            val_uuid = uuid.UUID(identifier)
            stmt = stmt.where(Assessment.id == val_uuid)
        except ValueError:
            stmt = stmt.where(Assessment.skill_id == identifier.lower())

        asmt = await db.scalar(stmt)
        if not asmt:
            raise NotFoundException("Assessment")
        return asmt

    async def _build_attempt_session(
        self,
        attempt: AssessmentAttempt,
        assessment: Assessment,
        db: AsyncSession,
    ) -> AttemptSessionResponse:
        """Constructs the public attempt session response hiding answer keys."""
        q_uuids = [uuid.UUID(qid) for qid in (attempt.question_ids or [])]

        stmt = (
            select(AssessmentQuestion)
            .where(AssessmentQuestion.id.in_(q_uuids))
        )
        questions_map = {q.id: q for q in (await db.scalars(stmt)).all()}

        # Fetch current answers
        ans_stmt = (
            select(AssessmentAnswer)
            .where(AssessmentAnswer.attempt_id == attempt.id)
        )
        answers = (await db.scalars(ans_stmt)).all()
        current_answers = {str(a.question_id): a.selected_option_index for a in answers}

        # Build ordered public question list with attempt-scoped option ordering
        public_questions: List[AttemptQuestionPublic] = []
        for idx, q_id in enumerate(q_uuids, 1):
            q = questions_map.get(q_id)
            if q:
                displayed_options = list(q.options)
                q_id_str = str(q.id)
                if attempt.option_orders and q_id_str in attempt.option_orders:
                    order = attempt.option_orders[q_id_str]
                    if len(order) == len(q.options):
                        displayed_options = [q.options[i] for i in order]

                public_questions.append(
                    AttemptQuestionPublic(
                        id=q.id,
                        index=idx,
                        prompt_text=q.prompt_text,
                        code_snippet=q.code_snippet,
                        options=displayed_options,
                        difficulty=q.difficulty,
                        topic=q.topic,
                    )
                )

        skill_name = assessment.skill_id
        if "skill" in assessment.__dict__ and assessment.skill:
            skill_name = assessment.skill.name
        else:
            sk = await db.get(Skill, assessment.skill_id)
            if sk:
                skill_name = sk.name

        return AttemptSessionResponse(
            attempt_id=attempt.id,
            assessment_id=assessment.id,
            assessment_title=assessment.title,
            skill_id=assessment.skill_id,
            skill_name=skill_name,
            status=attempt.status,
            total_questions=len(public_questions),
            time_limit_minutes=assessment.time_limit_minutes,
            started_at=attempt.started_at,
            questions=public_questions,
            current_answers=current_answers,
        )

    def _enforce_ownership(self, attempt: AssessmentAttempt, user: User) -> None:
        """Verifies candidate ownership over an attempt to prevent cross-user snooping."""
        if attempt.user_id != user.id and user.role != "admin":
            raise ForbiddenException("You do not have permission to access this assessment attempt.")

    async def _apply_diagnostic_to_user_skills(
        self,
        user: User,
        skill_id: str,
        score: float,
        passed: bool,
        db: AsyncSession,
    ) -> None:
        """Calibrates profile user_skills evidence based on the diagnostic result."""
        profile_stmt = (
            select(CareerProfile)
            .where(CareerProfile.user_id == user.id)
        )
        profile = await db.scalar(profile_stmt)
        if not profile:
            return

        user_skill_stmt = (
            select(UserSkill)
            .where(
                UserSkill.career_profile_id == profile.id,
                UserSkill.skill_id == skill_id,
            )
        )
        user_skill = await db.scalar(user_skill_stmt)

        confidence_val = decimal.Decimal(str(round(score / 100.0, 2)))

        if score >= 85.0:
            tier = "mastered"
        elif score >= 70.0:
            tier = "proficient"
        elif score >= 50.0:
            tier = "demonstrated"
        else:
            tier = "unverified"

        if user_skill:
            # Upgrade confidence if higher
            if confidence_val > user_skill.confidence_score:
                user_skill.confidence_score = confidence_val
                user_skill.proficiency_tier = tier
            user_skill.is_verified = (user_skill.is_verified or passed)
            user_skill.primary_source = "assessment"
            user_skill.last_evidence_at = utc_now()
        else:
            new_user_skill = UserSkill(
                career_profile_id=profile.id,
                skill_id=skill_id,
                confidence_score=confidence_val,
                proficiency_tier=tier,
                primary_source="assessment",
                is_verified=passed,
                last_evidence_at=utc_now(),
            )
            db.add(new_user_skill)

        await db.flush()
