"""
Deterministic Personalized Learning Roadmap Engine for CoachPath.
Converts candidate career objectives, skill-gap analysis snapshots, learning constraints,
and evidence provenance into structured, dependency-validated milestone curriculums.
Includes optional LLM task description personalization with guaranteed deterministic fallback.
"""

from __future__ import annotations

import logging
import math
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.base import LLMProvider
from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.assessments import AssessmentAttempt, AssessmentResult
from app.models.auth import User
from app.models.career import CareerProfile, Role
from app.models.roadmap import Roadmap, RoadmapPhase, RoadmapTask
from app.models.skills import RoleRequirement, Skill, SkillGapAnalysis
from app.schemas.roadmap import (
    RoadmapAdaptationResponse,
    RoadmapGenerateRequest,
    RoadmapHistoryItem,
    RoadmapHistoryResponse,
    RoadmapPhaseResponse,
    RoadmapProgressResponse,
    RoadmapResponse,
    RoadmapTaskResponse,
    UpdateRoadmapTaskRequest,
)
from app.schemas.skill_gap import SkillGapAnalysisResponse
from app.services.roadmap_catalog import (
    SKILL_PREREQUISITES,
    get_task_templates_for_skill,
)
from app.services.skill_gap_engine import SkillGapEngine

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RoadmapEngine:
    """
    Core service responsible for generating, scheduling, validating,
    persisting, and adapting personalized learning roadmaps.
    """

    def __init__(self, gap_engine: Optional[SkillGapEngine] = None) -> None:
        self._gap_engine = gap_engine or SkillGapEngine()

    async def generate_roadmap(
        self,
        user: User,
        db: AsyncSession,
        request: Optional[RoadmapGenerateRequest] = None,
        llm: Optional[LLMProvider] = None,
    ) -> RoadmapResponse:
        """
        Generates a personalized, structured learning roadmap from the user's
        latest skill-gap analysis, target role requirements, and learning constraints.
        """
        # 1. Fetch user CareerProfile
        profile_stmt = (
            select(CareerProfile)
            .where(CareerProfile.user_id == user.id)
        )
        profile = await db.scalar(profile_stmt)

        # 2. Determine and validate Target Role
        role_id = request.role_id if (request and request.role_id) else (profile.primary_role_id if profile else None)
        if not role_id:
            raise ValidationException(
                "A target role must be selected to generate a learning roadmap."
            )

        role_stmt = (
            select(Role)
            .options(
                selectinload(Role.requirements).selectinload(RoleRequirement.skill)
            )
            .where(Role.id == role_id)
        )
        role = await db.scalar(role_stmt)
        if not role:
            raise NotFoundException("Role", role_id)
        if not role.is_complete or not role.requirements:
            raise ValidationException(
                f"Target role '{role_id}' is incomplete or lacks benchmark requirements."
            )

        # 3. Initialize CareerProfile if not yet created
        if not profile:
            profile = CareerProfile(
                user_id=user.id,
                primary_role_id=role.id,
                career_stage="early_career",
                work_preference="remote",
            )
            db.add(profile)
            await db.flush()

        # 3. Obtain or calculate latest SkillGapAnalysis snapshot
        force = request.force_regenerate if request else False
        if force:
            gap_analysis = await self._gap_engine.calculate_gap_analysis(user, db, role_id=role.id)
        else:
            gap_analysis = await self._gap_engine.get_latest_gap_analysis(user, db, role_id=role.id)

        # 4. Resolve constraints and scheduling parameters
        weekly_hours = (
            request.weekly_hours
            if (request and request.weekly_hours)
            else 10
        )
        timeline_months = (
            request.target_timeline_months
            if (request and request.target_timeline_months)
            else 6
        )

        # 5. Determine version and archive any active roadmaps for this profile and role
        archived_stmt = (
            update(Roadmap)
            .where(
                Roadmap.career_profile_id == profile.id,
                Roadmap.target_role_id == role.id,
                Roadmap.is_active == True,
            )
            .values(is_active=False, status="archived")
        )
        await db.execute(archived_stmt)

        version_stmt = (
            select(Roadmap.version)
            .where(
                Roadmap.career_profile_id == profile.id,
                Roadmap.target_role_id == role.id,
            )
            .order_by(desc(Roadmap.version))
            .limit(1)
        )
        latest_ver = await db.scalar(version_stmt)
        new_version = (latest_ver + 1) if latest_ver is not None else 1

        # 6. Build curriculum phases and milestone tasks
        phases_data, total_estimated_hours = self._plan_phases_and_tasks(
            role=role,
            gap_analysis=gap_analysis,
            profile=profile,
        )

        # 7. Evaluate Feasibility and Scheduling
        start_date = _utc_now()
        estimated_weeks = math.ceil(total_estimated_hours / max(1, weekly_hours))
        target_completion_date = start_date + timedelta(days=int(timeline_months * 30.4375))

        target_weeks = timeline_months * 4.33
        if estimated_weeks <= target_weeks:
            feasibility_status = "feasible"
            feasibility_note = (
                f"Feasible pace: {total_estimated_hours} total hours fits comfortably within your "
                f"{timeline_months}-month target timeline ({estimated_weeks} weeks needed at {weekly_hours} hrs/week)."
            )
        elif estimated_weeks <= target_weeks * 1.35:
            feasibility_status = "demanding"
            rec_hours = math.ceil(total_estimated_hours / target_weeks)
            feasibility_note = (
                f"Demanding schedule: At {weekly_hours} hrs/week, curriculum requires {estimated_weeks} weeks. "
                f"To finish within {timeline_months} months, increase study commitment to {rec_hours} hrs/week."
            )
        else:
            feasibility_status = "unrealistic"
            rec_hours = math.ceil(total_estimated_hours / target_weeks)
            feasibility_note = (
                f"Timeline conflict: Your target of {timeline_months} months ({int(target_weeks)} weeks) "
                f"is insufficient for {total_estimated_hours} total study hours at {weekly_hours} hrs/week. "
                f"Recommended pace: {rec_hours} hrs/week or extend your timeline."
            )

        # 8. Optional Personalization via LLM (with deterministic fallback)
        title = f"{role.title} Milestone Learning Roadmap"
        description = (
            f"Personalized career roadmap for {role.title}. Tailored to your benchmark alignment "
            f"({gap_analysis.role_alignment_score:.1f}%) and evidence coverage ({gap_analysis.evidence_coverage_score:.1f}%). "
            f"Structured across {len(phases_data)} progressive phases to close confirmed skill gaps."
        )

        if llm and llm.is_available:
            try:
                description = await self._personalize_description_with_ai(
                    llm=llm,
                    role_title=role.title,
                    profile=profile,
                    alignment_score=gap_analysis.role_alignment_score,
                    total_hours=total_estimated_hours,
                    default_description=description,
                )
            except Exception as e:
                logger.warning("LLM personalization skipped due to error: %s", e)

        # 9. Create Roadmap record
        total_tasks_count = sum(len(p["tasks"]) for p in phases_data)
        roadmap = Roadmap(
            career_profile_id=profile.id,
            target_role_id=role.id,
            skill_gap_analysis_id=gap_analysis.id,
            title=title,
            description=description,
            version=new_version,
            is_active=True,
            status="active",
            generation_mode="deterministic_ai" if (llm and llm.is_available) else "deterministic",
            weekly_hours=weekly_hours,
            total_estimated_hours=total_estimated_hours,
            total_tasks=total_tasks_count,
            completed_tasks=0,
            start_date=start_date,
            target_completion_date=target_completion_date,
        )
        db.add(roadmap)
        await db.flush()

        # 10. Persist Phases and Tasks
        created_phases: List[RoadmapPhase] = []
        task_id_map: Dict[str, uuid.UUID] = {}

        # Pre-assign UUIDs to all tasks across all phases
        for p_data in phases_data:
            for t_data in p_data["tasks"]:
                t_uuid = uuid.uuid4()
                t_data["_uuid"] = t_uuid
                if "temp_key" in t_data:
                    task_id_map[t_data["temp_key"]] = t_uuid
                if t_data.get("skill_id"):
                    task_id_map[t_data["skill_id"]] = t_uuid

        for p_idx, p_data in enumerate(phases_data):
            phase = RoadmapPhase(
                roadmap_id=roadmap.id,
                title=p_data["title"],
                description=p_data["description"],
                objective=p_data.get("objective"),
                estimated_hours=p_data["estimated_hours"],
                prerequisites=p_data.get("prerequisites"),
                completion_criteria=p_data.get("completion_criteria"),
                status="in_progress" if p_idx == 0 else "pending",
                order_index=p_idx + 1,
                is_completed=False,
            )
            db.add(phase)
            await db.flush()

            for t_idx, t_data in enumerate(p_data["tasks"]):
                task_uuid = t_data["_uuid"]

                # Resolve prerequisites: only keep valid UUID strings of existing tasks, preventing self-dependencies
                resolved_prereqs = [
                    str(task_id_map[k])
                    for k in t_data.get("prerequisite_task_ids", [])
                    if k in task_id_map and task_id_map[k] != task_uuid
                ]

                task = RoadmapTask(
                    id=task_uuid,
                    phase_id=phase.id,
                    skill_id=t_data.get("skill_id"),
                    title=t_data["title"],
                    description=t_data["description"],
                    learning_objective=t_data.get("learning_objective"),
                    task_type=t_data.get("task_type", "project"),
                    priority=t_data.get("priority", "medium"),
                    estimated_hours=t_data.get("estimated_hours", 5),
                    resource_urls=t_data.get("resource_urls", []),
                    prerequisite_task_ids=resolved_prereqs,
                    deliverable_requirement=t_data.get("deliverable_requirement"),
                    completion_criteria=t_data.get("completion_criteria"),
                    status="pending",
                    order_index=t_idx + 1,
                    source_gap_priority=t_data.get("source_gap_priority"),
                )
                db.add(task)

            created_phases.append(phase)

        await db.commit()

        # 11. Return formatted response
        return await self.get_roadmap_by_id(roadmap.id, user, db)

    def _plan_phases_and_tasks(
        self,
        role: Role,
        gap_analysis: SkillGapAnalysisResponse,
        profile: CareerProfile,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Deterministically plans sequential phases and actionable tasks
        based on role requirements and skill gap priorities.
        """
        # Phase 1: Foundations & Core Prerequisites
        # Phase 2: Applied Frameworks & Deep Practice
        # Phase 3: System Architecture & Production Engineering
        # Phase 4: Capstone Deliverable & Diagnostic Verification

        phase_1_tasks: List[Dict[str, Any]] = []
        phase_2_tasks: List[Dict[str, Any]] = []
        phase_3_tasks: List[Dict[str, Any]] = []
        phase_4_tasks: List[Dict[str, Any]] = []

        total_hours = 0
        allocated_skills: Set[str] = set()

        # Prioritize gaps from gap analysis
        skill_details = gap_analysis.skill_details

        # 1. Inspect all role requirements and their gap status
        for req in role.requirements:
            s_id = req.skill_id
            s_detail = skill_details.get(s_id)
            current_level = s_detail.current_level if s_detail else 0
            required_level = req.required_level
            priority = "medium"

            if s_detail:
                if s_detail.status == "STRENGTH" and current_level >= required_level:
                    # Skill is already verified at or above target level; no baseline task needed
                    continue
                elif s_detail.status == "GAP":
                    priority = "critical" if req.importance == "mandatory" else "high"
                elif s_detail.status == "DEVELOPING":
                    priority = "high" if req.importance == "mandatory" else "medium"
                elif s_detail.status in ("NOT_ASSESSED", "NOT_IN_PROFILE"):
                    priority = "high" if req.importance == "mandatory" else "medium"

            # Retrieve curated progression tasks
            templates = get_task_templates_for_skill(s_id, current_level, required_level)
            allocated_skills.add(s_id)

            for tpl in templates:
                task_item = dict(tpl)
                task_item["skill_id"] = s_id
                task_item["priority"] = priority
                task_item["source_gap_priority"] = priority.upper()
                task_item["temp_key"] = f"{s_id}_{tpl.get('level', 1)}"
                task_item["prerequisite_task_ids"] = []

                # Link skill prerequisite DAG rules
                prereq_skills = SKILL_PREREQUISITES.get(s_id, [])
                for prereq_id in prereq_skills:
                    if prereq_id in allocated_skills:
                        task_item["prerequisite_task_ids"].append(f"{prereq_id}_1")

                # Phase assignment based on skill category and level
                category = req.skill.category if req.skill else "technology"
                t_level = tpl.get("level", 1)

                if category in ("language", "database") and t_level <= 1:
                    phase_1_tasks.append(task_item)
                elif category in ("framework", "web", "language", "database") and t_level == 2:
                    phase_2_tasks.append(task_item)
                elif category in ("systems", "devops", "cloud", "security") or t_level >= 3:
                    phase_3_tasks.append(task_item)
                else:
                    if len(phase_1_tasks) < 4:
                        phase_1_tasks.append(task_item)
                    elif len(phase_2_tasks) < 5:
                        phase_2_tasks.append(task_item)
                    else:
                        phase_3_tasks.append(task_item)

                total_hours += task_item["estimated_hours"]

        # Ensure Phase 1 has at least foundational tasks if role requires them
        if not phase_1_tasks and phase_2_tasks:
            # Rebalance first task to Phase 1 for pedagogical progression
            moved = phase_2_tasks.pop(0)
            phase_1_tasks.append(moved)

        # 2. Add Phase 4 tasks: Recommended Diagnostic Assessments + Role Capstone
        for asmt in gap_analysis.recommended_assessments[:3]:
            asmt_hours = max(1, math.ceil(asmt.question_count * 2 / 60))
            phase_4_tasks.append({
                "skill_id": asmt.skill_id,
                "title": f"Diagnostic Assessment: {asmt.title}",
                "description": (
                    f"Take the objective diagnostic skill assessment for {asmt.skill_id} to verify your "
                    f"technical knowledge against benchmark standards."
                ),
                "learning_objective": f"Achieve verified benchmark proficiency in {asmt.skill_id}.",
                "task_type": "assessment",
                "priority": "high",
                "estimated_hours": asmt_hours,
                "resource_urls": [
                    {"title": f"CoachPath {asmt.title} Test", "url": f"/assessments/{asmt.assessment_id}", "type": "course"}
                ],
                "deliverable_requirement": "Submit assessment with score >= 70% passing threshold.",
                "completion_criteria": "Assessment scored and recorded with passing verification tier.",
                "source_gap_priority": "BENCHMARK",
                "temp_key": f"asmt_{asmt.assessment_id}",
                "prerequisite_task_ids": [],
            })
            total_hours += asmt_hours

        # Add Comprehensive Capstone Project in Phase 4
        capstone_hours = 15
        capstone_prereqs = [t["temp_key"] for t in (phase_2_tasks + phase_3_tasks)[:4] if "temp_key" in t]
        phase_4_tasks.append({
            "skill_id": None,
            "title": f"{role.title} Production Capstone Deliverable",
            "description": (
                f"Design, implement, and deploy a production-grade capstone project integrating "
                f"your learned skills for the {role.title} benchmark. Must include automated testing, "
                f"containerization, and thorough documentation."
            ),
            "learning_objective": (
                f"Demonstrate end-to-end engineering competence aligned with {role.title} industry expectations."
            ),
            "task_type": "project",
            "priority": "critical",
            "estimated_hours": capstone_hours,
            "resource_urls": [
                {"title": "System Design & Project Architecture Guide", "url": "https://github.com/donnemartin/system-design-primer", "type": "reading"}
            ],
            "deliverable_requirement": "GitHub repository with passing CI/CD pipeline, Dockerfile, API documentation, and test suite.",
            "completion_criteria": "Passes automated verification; test suite achieves >85% coverage; Docker container runs cleanly.",
            "source_gap_priority": "CRITICAL",
            "temp_key": "capstone_final",
            "prerequisite_task_ids": capstone_prereqs,
        })
        total_hours += capstone_hours

        # Construct Phase structures
        phases = [
            {
                "title": "Phase 1: Foundations & Core Prerequisites",
                "description": "Establish core programming syntax, relational data modeling, and foundational developer workflows.",
                "objective": "Close baseline language and database gaps required by senior role competencies.",
                "prerequisites": "None. Starting baseline phase.",
                "completion_criteria": "All foundational practice tasks completed and verified.",
                "estimated_hours": sum(t["estimated_hours"] for t in phase_1_tasks),
                "tasks": phase_1_tasks,
            },
            {
                "title": "Phase 2: Applied Frameworks & Deep Practice",
                "description": "Construct practical services, implement REST APIs, and master modern application libraries.",
                "objective": "Build hands-on engineering experience using the primary tech stack of the role.",
                "prerequisites": "Completion of Phase 1 foundational competencies.",
                "completion_criteria": "Working microservices and component projects built with automated tests.",
                "estimated_hours": sum(t["estimated_hours"] for t in phase_2_tasks),
                "tasks": phase_2_tasks,
            },
            {
                "title": "Phase 3: System Architecture & Production Engineering",
                "description": "Harden services with distributed caching, Docker containerization, security policies, and CI/CD pipelines.",
                "objective": "Attain production engineering readiness and scalable system design principles.",
                "prerequisites": "Completion of Phase 2 framework deliverables.",
                "completion_criteria": "Containerized multi-service deployment running with health checks and CI/CD.",
                "estimated_hours": sum(t["estimated_hours"] for t in phase_3_tasks),
                "tasks": phase_3_tasks,
            },
            {
                "title": "Phase 4: Capstone Deliverable & Diagnostic Verification",
                "description": "Verify acquired competencies with objective diagnostic assessments and complete an industry capstone project.",
                "objective": "Provide indisputable technical evidence and portfolio artifacts for job applications.",
                "prerequisites": "Completion of Phase 3 production architecture.",
                "completion_criteria": "Passing scores on diagnostic tests and published capstone repository.",
                "estimated_hours": sum(t["estimated_hours"] for t in phase_4_tasks),
                "tasks": phase_4_tasks,
            },
        ]

        # Filter out empty phases if any
        active_phases = [p for p in phases if p["tasks"]]
        return active_phases, total_hours

    async def _personalize_description_with_ai(
        self,
        llm: LLMProvider,
        role_title: str,
        profile: CareerProfile,
        alignment_score: float,
        total_hours: int,
        default_description: str,
    ) -> str:
        """Personalizes the curriculum summary using Gemini while preserving deterministic facts."""
        prompt = (
            f"Candidate targeting: {role_title}\n"
            f"Current Role Alignment Score: {alignment_score:.1f}%\n"
            f"Total Estimated Effort: {total_hours} hours\n"
            f"Career Stage: {profile.career_stage or 'early career'}\n"
            f"Target Industries: {', '.join(profile.target_locations or ['Technology'])}\n\n"
            f"Write a 2-3 sentence strategic executive roadmap summary inspiring the candidate. "
            f"Focus on practical milestones and closing gaps. Do not make false employment guarantees."
        )
        try:
            summary_text = await llm.generate_text(
                prompt=prompt,
                system_prompt="You are CoachPath's Career Advisor. Output concise, professional coaching text only.",
                max_tokens=256,
            )
            return summary_text.strip() if summary_text else default_description
        except Exception as exc:
            logger.debug("AI personalization failed, falling back to deterministic template: %s", exc)
            return default_description

    async def get_active_roadmap(
        self,
        user: User,
        db: AsyncSession,
        role_id: Optional[str] = None,
    ) -> RoadmapResponse:
        """Retrieves the active roadmap for the authenticated user."""
        profile_stmt = select(CareerProfile).where(CareerProfile.user_id == user.id)
        profile = await db.scalar(profile_stmt)
        if not profile:
            raise NotFoundException("CareerProfile")

        conditions = [
            Roadmap.career_profile_id == profile.id,
            Roadmap.is_active == True,
        ]
        if role_id:
            conditions.append(Roadmap.target_role_id == role_id)

        stmt = (
            select(Roadmap)
            .options(
                selectinload(Roadmap.target_role),
                selectinload(Roadmap.phases).selectinload(RoadmapPhase.tasks).selectinload(RoadmapTask.skill),
            )
            .where(*conditions)
            .order_by(desc(Roadmap.version))
        )
        roadmap = await db.scalar(stmt)
        if not roadmap:
            raise NotFoundException("Roadmap")

        return self._format_roadmap_response(roadmap)

    async def get_roadmap_by_id(
        self,
        roadmap_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> RoadmapResponse:
        """Retrieves a specific roadmap by ID, enforcing strict ownership."""
        stmt = (
            select(Roadmap)
            .options(
                selectinload(Roadmap.career_profile),
                selectinload(Roadmap.target_role),
                selectinload(Roadmap.phases).selectinload(RoadmapPhase.tasks).selectinload(RoadmapTask.skill),
            )
            .where(Roadmap.id == roadmap_id)
        )
        roadmap = await db.scalar(stmt)
        if not roadmap:
            raise NotFoundException("Roadmap", str(roadmap_id))

        if roadmap.career_profile.user_id != user.id:
            raise ForbiddenException("You do not have permission to view this roadmap.")

        return self._format_roadmap_response(roadmap)

    async def get_roadmap_history(
        self,
        user: User,
        db: AsyncSession,
    ) -> RoadmapHistoryResponse:
        """Retrieves chronological history of all roadmap versions for the user."""
        profile_stmt = select(CareerProfile).where(CareerProfile.user_id == user.id)
        profile = await db.scalar(profile_stmt)
        if not profile:
            return RoadmapHistoryResponse(items=[], total=0)

        stmt = (
            select(Roadmap)
            .options(selectinload(Roadmap.target_role))
            .where(Roadmap.career_profile_id == profile.id)
            .order_by(desc(Roadmap.version))
        )
        roadmaps = (await db.scalars(stmt)).all()

        items = [
            RoadmapHistoryItem(
                id=r.id,
                target_role_id=r.target_role_id,
                target_role_title=r.target_role.title if r.target_role else r.target_role_id,
                version=r.version,
                is_active=r.is_active,
                status=r.status,
                generation_mode=r.generation_mode,
                weekly_hours=r.weekly_hours,
                total_estimated_hours=r.total_estimated_hours,
                total_tasks=r.total_tasks,
                completed_tasks=r.completed_tasks,
                progress_percentage=(
                    round((r.completed_tasks / max(1, r.total_tasks)) * 100, 1)
                    if r.total_tasks > 0
                    else 0.0
                ),
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in roadmaps
        ]
        return RoadmapHistoryResponse(items=items, total=len(items))

    async def get_roadmap_progress(
        self,
        roadmap_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> RoadmapProgressResponse:
        """Calculates granular real-time progress metrics and returns next recommended tasks."""
        roadmap_resp = await self.get_roadmap_by_id(roadmap_id, user, db)

        completed_tasks = 0
        total_tasks = 0
        completed_hours = 0
        remaining_hours = 0
        next_tasks: List[RoadmapTaskResponse] = []
        current_phase_index = 1
        current_phase_title = None

        for p_idx, phase in enumerate(roadmap_resp.phases):
            phase_has_pending = False
            for task in phase.tasks:
                total_tasks += 1
                if task.status == "completed":
                    completed_tasks += 1
                    completed_hours += task.estimated_hours
                else:
                    phase_has_pending = True
                    remaining_hours += task.estimated_hours
                    if len(next_tasks) < 3 and task.status != "skipped":
                        next_tasks.append(task)

            if phase_has_pending and current_phase_title is None:
                current_phase_index = phase.order_index
                current_phase_title = phase.title

        progress_pct = round((completed_tasks / max(1, total_tasks)) * 100, 1)
        weeks_remaining = round(remaining_hours / max(1, roadmap_resp.weekly_hours), 1)

        return RoadmapProgressResponse(
            roadmap_id=roadmap_resp.id,
            target_role_id=roadmap_resp.target_role_id,
            target_role_title=roadmap_resp.target_role_title,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=total_tasks - completed_tasks,
            progress_percentage=progress_pct,
            total_estimated_hours=roadmap_resp.total_estimated_hours,
            completed_hours=completed_hours,
            remaining_hours=remaining_hours,
            weekly_hours=roadmap_resp.weekly_hours,
            estimated_weeks_remaining=weeks_remaining,
            current_phase_index=current_phase_index,
            current_phase_title=current_phase_title or (roadmap_resp.phases[-1].title if roadmap_resp.phases else "Completed"),
            next_recommended_tasks=next_tasks,
        )

    async def update_task_status(
        self,
        task_id: uuid.UUID,
        request: UpdateRoadmapTaskRequest,
        user: User,
        db: AsyncSession,
    ) -> RoadmapTaskResponse:
        """
        Updates task status (in_progress, completed, skipped) and deliverable proof,
        then updates phase and roadmap progress atomically.
        """
        task_stmt = (
            select(RoadmapTask)
            .options(
                selectinload(RoadmapTask.phase).selectinload(RoadmapPhase.roadmap).selectinload(Roadmap.career_profile),
                selectinload(RoadmapTask.skill),
            )
            .where(RoadmapTask.id == task_id)
        )
        task = await db.scalar(task_stmt)
        if not task:
            raise NotFoundException("RoadmapTask", str(task_id))

        roadmap = task.phase.roadmap
        if roadmap.career_profile.user_id != user.id:
            raise ForbiddenException("You do not have permission to modify this roadmap task.")

        # Update status and timestamps
        if request.status:
            old_status = task.status
            task.status = request.status
            if request.status == "completed" and old_status != "completed":
                task.completed_at = _utc_now()
            elif request.status != "completed":
                task.completed_at = None

        if request.submission_url is not None:
            task.submission_url = request.submission_url

        # Check and update parent Phase completion
        phase = task.phase
        phase_tasks_stmt = select(RoadmapTask).where(RoadmapTask.phase_id == phase.id)
        all_phase_tasks = (await db.scalars(phase_tasks_stmt)).all()

        all_completed = all(t.status in ("completed", "skipped") for t in all_phase_tasks)
        phase.is_completed = all_completed
        if all_completed:
            phase.status = "completed"
        elif any(t.status in ("in_progress", "completed") for t in all_phase_tasks):
            phase.status = "in_progress"
        else:
            phase.status = "pending"

        # Recompute roadmap completed task count
        roadmap_tasks_stmt = (
            select(RoadmapTask)
            .join(RoadmapPhase, RoadmapTask.phase_id == RoadmapPhase.id)
            .where(RoadmapPhase.roadmap_id == roadmap.id)
        )
        all_roadmap_tasks = (await db.scalars(roadmap_tasks_stmt)).all()
        roadmap.completed_tasks = sum(1 for t in all_roadmap_tasks if t.status == "completed")
        roadmap.total_tasks = len(all_roadmap_tasks)

        if all(t.status in ("completed", "skipped") for t in all_roadmap_tasks):
            roadmap.status = "completed"
        else:
            roadmap.status = "active"

        await db.commit()
        await db.refresh(task)

        return self._format_task_response(task)

    async def adapt_roadmap(
        self,
        roadmap_id: uuid.UUID,
        user: User,
        db: AsyncSession,
    ) -> RoadmapAdaptationResponse:
        """
        Adapts the roadmap based on new diagnostic assessment attempts and verified skills.
        Auto-completes pending milestones where the user has achieved verified proficiency.
        """
        # Load roadmap with full phase/task tree
        roadmap_stmt = (
            select(Roadmap)
            .options(
                selectinload(Roadmap.career_profile),
                selectinload(Roadmap.phases).selectinload(RoadmapPhase.tasks),
            )
            .where(Roadmap.id == roadmap_id)
        )
        roadmap = await db.scalar(roadmap_stmt)
        if not roadmap:
            raise NotFoundException("Roadmap", str(roadmap_id))

        if roadmap.career_profile.user_id != user.id:
            raise ForbiddenException("You do not have permission to adapt this roadmap.")

        # Check user's verified assessments
        passed_stmt = (
            select(AssessmentAttempt)
            .options(selectinload(AssessmentAttempt.assessment))
            .where(
                AssessmentAttempt.user_id == user.id,
                AssessmentAttempt.passed == True,
            )
        )
        passed_attempts = (await db.scalars(passed_stmt)).all()
        verified_skill_ids = {
            a.assessment.skill_id
            for a in passed_attempts
            if a.assessment and a.assessment.skill_id
        }

        tasks_auto_completed = 0
        for phase in roadmap.phases:
            for task in phase.tasks:
                if task.status == "pending" and task.skill_id and task.skill_id in verified_skill_ids:
                    task.status = "completed"
                    task.completed_at = _utc_now()
                    tasks_auto_completed += 1

            # Update phase completion
            if all(t.status in ("completed", "skipped") for t in phase.tasks):
                phase.is_completed = True
                phase.status = "completed"

        # Update roadmap completed tasks
        all_tasks = [t for p in roadmap.phases for t in p.tasks]
        roadmap.completed_tasks = sum(1 for t in all_tasks if t.status == "completed")
        if all(t.status in ("completed", "skipped") for t in all_tasks):
            roadmap.status = "completed"

        await db.commit()

        roadmap_resp = await self.get_roadmap_by_id(roadmap.id, user, db)
        message = (
            f"Roadmap adapted successfully. {tasks_auto_completed} milestone(s) automatically "
            f"completed based on verified diagnostic assessment scores."
            if tasks_auto_completed > 0
            else "Roadmap is fully up-to-date with your current assessment evidence."
        )

        return RoadmapAdaptationResponse(
            roadmap_id=roadmap.id,
            adapted=tasks_auto_completed > 0,
            tasks_auto_completed=tasks_auto_completed,
            tasks_adjusted=tasks_auto_completed,
            message=message,
            roadmap=roadmap_resp,
        )

    def _format_task_response(self, task: RoadmapTask) -> RoadmapTaskResponse:
        """Formats a RoadmapTask entity into its public response model."""
        return RoadmapTaskResponse(
            id=task.id,
            phase_id=task.phase_id,
            skill_id=task.skill_id,
            skill_name=task.skill.name if task.skill else (task.skill_id.replace("-", " ").title() if task.skill_id else None),
            title=task.title,
            description=task.description,
            learning_objective=task.learning_objective,
            task_type=task.task_type,
            priority=task.priority,
            estimated_hours=task.estimated_hours,
            resource_urls=task.resource_urls or [],
            prerequisite_task_ids=task.prerequisite_task_ids or [],
            deliverable_requirement=task.deliverable_requirement,
            submission_url=task.submission_url,
            completion_criteria=task.completion_criteria,
            status=task.status,
            due_date=task.due_date,
            completed_at=task.completed_at,
            order_index=task.order_index,
            source_gap_priority=task.source_gap_priority,
        )

    def _format_roadmap_response(self, roadmap: Roadmap) -> RoadmapResponse:
        """Formats a Roadmap entity tree into RoadmapResponse."""
        phases_resp: List[RoadmapPhaseResponse] = []
        for phase in roadmap.phases:
            tasks_resp = [self._format_task_response(t) for t in phase.tasks]
            phases_resp.append(
                RoadmapPhaseResponse(
                    id=phase.id,
                    roadmap_id=phase.roadmap_id,
                    title=phase.title,
                    description=phase.description,
                    objective=phase.objective,
                    estimated_hours=phase.estimated_hours,
                    prerequisites=phase.prerequisites,
                    completion_criteria=phase.completion_criteria,
                    status=phase.status,
                    order_index=phase.order_index,
                    is_completed=phase.is_completed,
                    tasks=tasks_resp,
                )
            )

        progress_pct = (
            round((roadmap.completed_tasks / max(1, roadmap.total_tasks)) * 100, 1)
            if roadmap.total_tasks > 0
            else 0.0
        )

        # Feasibility check
        weekly_hours = max(1, roadmap.weekly_hours)
        weeks_needed = math.ceil(roadmap.total_estimated_hours / weekly_hours)
        if roadmap.target_completion_date and roadmap.start_date:
            target_weeks = (roadmap.target_completion_date - roadmap.start_date).days / 7.0
            if weeks_needed <= target_weeks:
                feasibility_status = "feasible"
                note = f"Feasible: curriculum estimated at {weeks_needed} weeks fits target schedule."
            elif weeks_needed <= target_weeks * 1.35:
                feasibility_status = "demanding"
                note = f"Demanding: requires steady {weekly_hours} hrs/week to stay on schedule."
            else:
                feasibility_status = "unrealistic"
                note = f"Unrealistic: schedule requires more hours per week or extending timeline."
        else:
            feasibility_status = "feasible"
            note = "Roadmap ready for execution."

        return RoadmapResponse(
            id=roadmap.id,
            career_profile_id=roadmap.career_profile_id,
            target_role_id=roadmap.target_role_id,
            target_role_title=roadmap.target_role.title if roadmap.target_role else roadmap.target_role_id,
            skill_gap_analysis_id=roadmap.skill_gap_analysis_id,
            title=roadmap.title,
            description=roadmap.description,
            version=roadmap.version,
            is_active=roadmap.is_active,
            status=roadmap.status,
            generation_mode=roadmap.generation_mode,
            weekly_hours=roadmap.weekly_hours,
            total_estimated_hours=roadmap.total_estimated_hours,
            total_tasks=roadmap.total_tasks,
            completed_tasks=roadmap.completed_tasks,
            progress_percentage=progress_pct,
            start_date=roadmap.start_date,
            target_completion_date=roadmap.target_completion_date,
            feasibility_status=feasibility_status,
            feasibility_note=note,
            phases=phases_resp,
            created_at=roadmap.created_at,
            updated_at=roadmap.updated_at,
        )
