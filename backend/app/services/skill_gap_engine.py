"""
Deterministic Skill Gap Analysis Engine for CoachPath.
Calibrates multi-source candidate evidence (assessments, user skills, projects, resumes)
against target role requirements, calculates alignment & coverage metrics,
ranks skill gaps, and generates deterministic diagnostic narratives.
NO LLM calls are used in core scoring or gap classification.
"""

from __future__ import annotations

import decimal
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ValidationException
from app.db.seeds.skill_taxonomy import normalize_skill_name
from app.models.assessments import Assessment, AssessmentAttempt, AssessmentResult
from app.models.auth import User
from app.models.career import CareerProfile, Project, Role
from app.models.skills import RoleRequirement, Skill, SkillGap, SkillGapAnalysis, UserSkill
from app.schemas.skill_gap import (
    EvidenceItem,
    LegacySkillGapResponse,
    PrioritizedGap,
    RecommendedAssessment,
    RoleDetailResponse,
    RoleListResponse,
    RoleRequirementResponse,
    SkillCompetencyDetail,
    SkillEvidenceDetailResponse,
    SkillGapAnalysisListResponse,
    SkillGapAnalysisResponse,
    SkillGapAnalysisSummary,
    SkillResponse,
)
from app.services.assessment_skill_mapper import (
    SKILL_TO_ASSESSMENT_MAP,
    get_assessment_id_for_skill,
    get_recommended_assessment_for_skill,
)

logger = logging.getLogger(__name__)

# Proficiency level mappings
PROFICIENCY_TIER_TO_LEVEL: Dict[str, int] = {
    "basic": 1,
    "unverified": 1,
    "demonstrated": 2,
    "proficient": 3,
    "mastered": 4,
}

LEVEL_TO_PROFICIENCY_TIER: Dict[int, str] = {
    0: "unverified",
    1: "basic",
    2: "demonstrated",
    3: "proficient",
    4: "mastered",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SkillGapEngine:
    """
    Engine executing deterministic skill gap analyses, role alignment scoring,
    and historical snapshot persistence.
    """

    async def get_roles(self, db: AsyncSession) -> RoleListResponse:
        """Returns all supported canonical target roles with requirement summaries."""
        stmt = (
            select(Role)
            .options(
                selectinload(Role.requirements).selectinload(RoleRequirement.skill)
            )
            .order_by(Role.category, Role.title)
        )
        roles = (await db.scalars(stmt)).all()

        role_details: List[RoleDetailResponse] = []
        for role in roles:
            reqs = [
                RoleRequirementResponse(
                    skill_id=r.skill_id,
                    skill_name=r.skill.name if r.skill else r.skill_id,
                    category=r.skill.category if r.skill else None,
                    importance=r.importance,
                    min_proficiency=r.min_proficiency,
                    required_level=r.required_level,
                    weight=float(r.weight),
                    rationale=r.rationale,
                )
                for r in role.requirements
            ]
            role_details.append(
                RoleDetailResponse(
                    id=role.id,
                    title=role.title,
                    description=role.description,
                    category=role.category,
                    version=role.version,
                    source=role.source,
                    is_complete=role.is_complete,
                    requirements=reqs,
                )
            )

        return RoleListResponse(roles=role_details, total=len(role_details))

    async def get_role(self, role_id: str, db: AsyncSession) -> RoleDetailResponse:
        """Returns a single role with its full requirement specifications."""
        stmt = (
            select(Role)
            .options(
                selectinload(Role.requirements).selectinload(RoleRequirement.skill)
            )
            .where(Role.id == role_id)
        )
        role = await db.scalar(stmt)
        if not role:
            raise NotFoundException("Role")

        reqs = [
            RoleRequirementResponse(
                skill_id=r.skill_id,
                skill_name=r.skill.name if r.skill else r.skill_id,
                category=r.skill.category if r.skill else None,
                importance=r.importance,
                min_proficiency=r.min_proficiency,
                required_level=r.required_level,
                weight=float(r.weight),
                rationale=r.rationale,
            )
            for r in role.requirements
        ]
        return RoleDetailResponse(
            id=role.id,
            title=role.title,
            description=role.description,
            category=role.category,
            version=role.version,
            source=role.source,
            is_complete=role.is_complete,
            requirements=reqs,
        )

    async def get_canonical_skills(self, db: AsyncSession) -> List[SkillResponse]:
        """Returns all canonical skills registered in the taxonomy."""
        stmt = select(Skill).order_by(Skill.category, Skill.name)
        skills = (await db.scalars(stmt)).all()
        return [
            SkillResponse(
                id=s.id,
                name=s.name,
                category=s.category,
                description=s.description,
                synonyms=s.synonyms or [],
            )
            for s in skills
        ]

    async def calculate_gap_analysis(
        self,
        user: User,
        db: AsyncSession,
        role_id: Optional[str] = None,
    ) -> SkillGapAnalysisResponse:
        """
        Executes a deterministic skill gap analysis for the user and target role.
        Persists a new snapshot with is_current=True and archives previous snapshots.
        """
        # 1. Fetch User Career Profile
        profile_stmt = (
            select(CareerProfile)
            .options(
                selectinload(CareerProfile.user_skills).selectinload(UserSkill.skill),
                selectinload(CareerProfile.projects),
            )
            .where(CareerProfile.user_id == user.id)
        )
        profile = await db.scalar(profile_stmt)

        # 2. Resolve Target Role
        target_role_id = role_id or (profile.primary_role_id if profile else "backend-developer")
        if not target_role_id:
            raise ValidationException(
                "No target role selected. Please specify a role_id or set a primary target role in your profile."
            )

        role_stmt = (
            select(Role)
            .options(
                selectinload(Role.requirements).selectinload(RoleRequirement.skill)
            )
            .where(Role.id == target_role_id)
        )
        role = await db.scalar(role_stmt)
        if not role:
            raise NotFoundException("Role")

        if not role.is_complete or not role.requirements:
            raise ValidationException(f"Target role '{role.title}' is an incomplete profile and has insufficient benchmark requirements defined.")

        if not profile:
            profile = CareerProfile(
                user_id=user.id,
                primary_role_id=role.id,
                career_stage="early_career",
                work_preference="hybrid",
                target_locations=["Remote"],
                years_of_experience=decimal.Decimal("0.0"),
            )
            db.add(profile)
            await db.commit()
            profile = await db.scalar(profile_stmt)

        # 3. Gather Evidence Graph
        evidence_graph = await self._gather_candidate_evidence(user.id, profile, db)

        # 4. Process Each Role Requirement Deterministically
        skill_details: Dict[str, SkillCompetencyDetail] = {}
        strongest_skills: List[str] = []
        developing_skills: List[str] = []
        skill_gaps: List[str] = []
        missing_skills: List[str] = []
        unassessed_skills: List[str] = []

        total_weight = 0.0
        weighted_coverage_sum = 0.0
        weighted_sufficient_evidence_sum = 0.0

        for req in role.requirements:
            skill = req.skill
            skill_id = req.skill_id
            skill_name = skill.name if skill else skill_id
            category = skill.category if skill else "concept"
            req_weight = float(req.weight)
            total_weight += req_weight

            # Calibrate evidence for this skill
            skill_evidence = evidence_graph.get(skill_id, [])
            current_level, current_tier, is_verified = self._calibrate_skill_competency(skill_evidence)

            # Coverage ratio: min(current_level / required_level, 1.0)
            required_level = max(1, req.required_level)
            coverage_ratio = min(round(current_level / required_level, 2), 1.0)
            weighted_coverage_sum += coverage_ratio * req_weight

            # Evidence coverage check: has verified diagnostic or demonstrated evidence
            if is_verified and current_level >= 1:
                weighted_sufficient_evidence_sum += req_weight
            elif len(skill_evidence) > 0 and current_level >= 1:
                # Partial evidence credit for coverage score
                weighted_sufficient_evidence_sum += 0.5 * req_weight

            # Determine Competency Classification Status
            if current_level == 0 and len(skill_evidence) == 0:
                status = "NOT_IN_PROFILE"
                missing_skills.append(skill_name)
                recommended_action = f"Add {skill_name} to profile and begin foundational study."
            elif not is_verified and current_level > 0:
                status = "NOT_ASSESSED"
                unassessed_skills.append(skill_name)
                recommended_action = f"Take diagnostic assessment to verify claimed proficiency in {skill_name}."
            elif current_level >= required_level:
                status = "STRENGTH"
                strongest_skills.append(skill_name)
                recommended_action = f"Benchmark met. Maintain proficiency through active implementation."
            elif current_level == required_level - 1:
                status = "DEVELOPING"
                developing_skills.append(skill_name)
                recommended_action = f"Targeted practice required to bridge level {current_level} to {required_level}."
            else:
                status = "GAP"
                skill_gaps.append(skill_name)
                recommended_action = f"Substantial gap identified. Structured learning and hands-on practice required."

            detail = SkillCompetencyDetail(
                skill_id=skill_id,
                skill_name=skill_name,
                category=category,
                importance=req.importance,
                min_proficiency=req.min_proficiency,
                required_level=required_level,
                current_level=current_level,
                current_tier=current_tier,
                coverage_ratio=coverage_ratio,
                status=status,
                weight=req_weight,
                rationale=req.rationale,
                evidence_count=len(skill_evidence),
                evidence_items=skill_evidence,
                recommended_action=recommended_action,
            )
            skill_details[skill_id] = detail

        # 5. Compute Aggregate Scores
        if total_weight > 0.0:
            role_alignment_score = round((weighted_coverage_sum / total_weight) * 100.0, 1)
            evidence_coverage_score = round((weighted_sufficient_evidence_sum / total_weight) * 100.0, 1)
        else:
            role_alignment_score = 0.0
            evidence_coverage_score = 0.0

        # Clamp between 0.0 and 100.0
        role_alignment_score = max(0.0, min(100.0, role_alignment_score))
        evidence_coverage_score = max(0.0, min(100.0, evidence_coverage_score))

        # 6. Prioritize Skill Gaps
        prioritized_gaps = self._prioritize_skill_gaps(skill_details)

        # 7. Generate Recommended Assessments
        recommended_assessments = self._determine_recommended_assessments(skill_details)

        # 8. Generate Deterministic Diagnostic Narrative
        explanation_narrative = self._generate_diagnostic_narrative(
            role_title=role.title,
            alignment_score=role_alignment_score,
            coverage_score=evidence_coverage_score,
            strongest=strongest_skills,
            developing=developing_skills,
            gaps=skill_gaps,
            missing=missing_skills,
            unassessed=unassessed_skills,
            prioritized_gaps=prioritized_gaps,
        )

        # 9. Persist Snapshot Transactionally
        # Archive previous active snapshots for this profile
        await db.execute(
            update(SkillGapAnalysis)
            .where(
                SkillGapAnalysis.career_profile_id == profile.id,
                SkillGapAnalysis.is_current == True,
            )
            .values(is_current=False)
        )

        now = _utc_now()
        analysis_record = SkillGapAnalysis(
            id=uuid.uuid4(),
            career_profile_id=profile.id,
            role_id=role.id,
            is_current=True,
            role_version=role.version,
            algorithm_version="1.0.0",
            role_alignment_score=decimal.Decimal(str(role_alignment_score)),
            evidence_coverage_score=decimal.Decimal(str(evidence_coverage_score)),
            status="completed",
            strongest_skills=strongest_skills,
            developing_skills=developing_skills,
            skill_gaps=skill_gaps,
            missing_skills=missing_skills,
            unassessed_skills=unassessed_skills,
            skill_details={k: v.model_dump() for k, v in skill_details.items()},
            prioritized_gaps=[g.model_dump() for g in prioritized_gaps],
            recommended_assessments=[a.model_dump() for a in recommended_assessments],
            explanation_narrative=explanation_narrative,
            created_at=now,
            calculated_at=now,
        )
        db.add(analysis_record)

        # 10. Update or Upsert Legacy SkillGap Row (for backward compatibility)
        legacy_stmt = select(SkillGap).where(
            SkillGap.career_profile_id == profile.id,
            SkillGap.role_id == role.id,
        )
        legacy_gap = await db.scalar(legacy_stmt)
        if legacy_gap:
            legacy_gap.readiness_percentage = decimal.Decimal(str(role_alignment_score))
            legacy_gap.met_skills = strongest_skills
            legacy_gap.developing_skills = developing_skills
            legacy_gap.missing_skills = missing_skills + skill_gaps
            legacy_gap.explanation_narrative = explanation_narrative
            legacy_gap.calculated_at = now
        else:
            legacy_gap = SkillGap(
                id=uuid.uuid4(),
                career_profile_id=profile.id,
                role_id=role.id,
                readiness_percentage=decimal.Decimal(str(role_alignment_score)),
                met_skills=strongest_skills,
                developing_skills=developing_skills,
                missing_skills=missing_skills + skill_gaps,
                explanation_narrative=explanation_narrative,
                calculated_at=now,
            )
            db.add(legacy_gap)

        await db.commit()
        await db.refresh(analysis_record)

        return SkillGapAnalysisResponse(
            id=analysis_record.id,
            career_profile_id=analysis_record.career_profile_id,
            role_id=role.id,
            role_title=role.title,
            is_current=analysis_record.is_current,
            role_version=analysis_record.role_version,
            algorithm_version=analysis_record.algorithm_version,
            role_alignment_score=float(analysis_record.role_alignment_score),
            evidence_coverage_score=float(analysis_record.evidence_coverage_score),
            status=analysis_record.status,
            strongest_skills=analysis_record.strongest_skills,
            developing_skills=analysis_record.developing_skills,
            skill_gaps=analysis_record.skill_gaps,
            missing_skills=analysis_record.missing_skills,
            unassessed_skills=analysis_record.unassessed_skills,
            skill_details=skill_details,
            prioritized_gaps=prioritized_gaps,
            recommended_assessments=recommended_assessments,
            explanation_narrative=analysis_record.explanation_narrative,
            calculated_at=analysis_record.calculated_at,
        )

    async def get_latest_gap_analysis(
        self,
        user: User,
        db: AsyncSession,
        role_id: Optional[str] = None,
    ) -> SkillGapAnalysisResponse:
        """Retrieves the active gap analysis snapshot for the user (optionally filtered by role_id)."""
        profile_stmt = select(CareerProfile).where(CareerProfile.user_id == user.id)
        profile = await db.scalar(profile_stmt)
        if not profile:
            return await self.calculate_gap_analysis(user, db, role_id=role_id)

        conditions = [
            SkillGapAnalysis.career_profile_id == profile.id,
        ]
        if role_id:
            conditions.append(SkillGapAnalysis.role_id == role_id)
        else:
            conditions.append(SkillGapAnalysis.is_current == True)

        stmt = (
            select(SkillGapAnalysis)
            .options(selectinload(SkillGapAnalysis.role))
            .where(*conditions)
            .order_by(desc(SkillGapAnalysis.calculated_at))
        )
        record = await db.scalar(stmt)
        if not record:
            # Trigger calculation if none exists
            return await self.calculate_gap_analysis(user, db, role_id=role_id)

        # Reconstruct typed skill details
        typed_details: Dict[str, SkillCompetencyDetail] = {}
        for k, v in record.skill_details.items():
            typed_details[k] = SkillCompetencyDetail.model_validate(v)

        typed_gaps = [PrioritizedGap.model_validate(g) for g in record.prioritized_gaps]
        typed_assessments = [
            RecommendedAssessment.model_validate(a) for a in record.recommended_assessments
        ]

        return SkillGapAnalysisResponse(
            id=record.id,
            career_profile_id=record.career_profile_id,
            role_id=record.role_id,
            role_title=record.role.title if record.role else record.role_id,
            is_current=record.is_current,
            role_version=record.role_version,
            algorithm_version=record.algorithm_version,
            role_alignment_score=float(record.role_alignment_score),
            evidence_coverage_score=float(record.evidence_coverage_score),
            status=record.status,
            strongest_skills=record.strongest_skills,
            developing_skills=record.developing_skills,
            skill_gaps=record.skill_gaps,
            missing_skills=record.missing_skills,
            unassessed_skills=record.unassessed_skills,
            skill_details=typed_details,
            prioritized_gaps=typed_gaps,
            recommended_assessments=typed_assessments,
            explanation_narrative=record.explanation_narrative,
            calculated_at=record.calculated_at,
        )

    async def get_history(
        self,
        user: User,
        db: AsyncSession,
    ) -> SkillGapAnalysisListResponse:
        """Returns the timeline history of all gap analysis snapshots for the user."""
        profile_stmt = select(CareerProfile).where(CareerProfile.user_id == user.id)
        profile = await db.scalar(profile_stmt)
        if not profile:
            return SkillGapAnalysisListResponse(items=[], total=0)

        stmt = (
            select(SkillGapAnalysis)
            .options(selectinload(SkillGapAnalysis.role))
            .where(SkillGapAnalysis.career_profile_id == profile.id)
            .order_by(desc(SkillGapAnalysis.calculated_at))
        )
        records = (await db.scalars(stmt)).all()

        items = [
            SkillGapAnalysisSummary(
                id=r.id,
                role_id=r.role_id,
                role_title=r.role.title if r.role else r.role_id,
                is_current=r.is_current,
                role_alignment_score=float(r.role_alignment_score),
                evidence_coverage_score=float(r.evidence_coverage_score),
                status=r.status,
                strongest_skills_count=len(r.strongest_skills),
                developing_skills_count=len(r.developing_skills),
                skill_gaps_count=len(r.skill_gaps),
                missing_skills_count=len(r.missing_skills),
                unassessed_skills_count=len(r.unassessed_skills),
                calculated_at=r.calculated_at,
            )
            for r in records
        ]

        return SkillGapAnalysisListResponse(items=items, total=len(items))

    async def get_skill_evidence(
        self,
        skill_id: str,
        user: User,
        db: AsyncSession,
    ) -> SkillEvidenceDetailResponse:
        """Returns all evidence items supporting a specific canonical skill for the user."""
        # Validate skill exists
        skill = await db.scalar(select(Skill).where(Skill.id == skill_id))
        if not skill:
            raise NotFoundException("Skill")

        profile_stmt = (
            select(CareerProfile)
            .options(
                selectinload(CareerProfile.user_skills).selectinload(UserSkill.skill),
                selectinload(CareerProfile.projects),
            )
            .where(CareerProfile.user_id == user.id)
        )
        profile = await db.scalar(profile_stmt)
        if not profile:
            return SkillEvidenceDetailResponse(
                skill_id=skill.id,
                skill_name=skill.name,
                category=skill.category,
                current_level=0,
                current_tier="unverified",
                is_verified=False,
                evidence_items=[],
            )

        evidence_graph = await self._gather_candidate_evidence(user.id, profile, db)
        items = evidence_graph.get(skill_id, [])
        level, tier, is_verified = self._calibrate_skill_competency(items)

        return SkillEvidenceDetailResponse(
            skill_id=skill.id,
            skill_name=skill.name,
            category=skill.category,
            current_level=level,
            current_tier=tier,
            is_verified=is_verified,
            evidence_items=items,
        )

    async def get_legacy_gaps(
        self,
        user: User,
        db: AsyncSession,
    ) -> LegacySkillGapResponse:
        """Legacy compatibility method returning the latest readiness and gap snapshot."""
        analysis = await self.get_latest_gap_analysis(user, db)
        return LegacySkillGapResponse(
            readiness_percentage=analysis.role_alignment_score,
            met_skills=analysis.strongest_skills,
            developing_skills=analysis.developing_skills,
            missing_skills=analysis.missing_skills + analysis.skill_gaps,
            explanation_narrative=analysis.explanation_narrative,
            calculated_at=analysis.calculated_at,
        )

    # ─── Internal Calibration & Gathering Helpers ───────────────────────

    async def _gather_candidate_evidence(
        self,
        user_id: uuid.UUID,
        profile: CareerProfile,
        db: AsyncSession,
    ) -> Dict[str, List[EvidenceItem]]:
        """
        Gathers and normalizes all candidate evidence from:
        1. Completed Diagnostic Assessment Results
        2. UserSkills calibrated on CareerProfile
        3. Projects listed on CareerProfile
        """
        evidence_by_skill: Dict[str, List[EvidenceItem]] = {}

        def add_evidence(canonical_id: str, item: EvidenceItem):
            if canonical_id not in evidence_by_skill:
                evidence_by_skill[canonical_id] = []
            evidence_by_skill[canonical_id].append(item)

        # 1. Gather Assessment Results from completed attempts
        asmt_stmt = (
            select(AssessmentAttempt)
            .options(
                selectinload(AssessmentAttempt.assessment)
            )
            .where(
                AssessmentAttempt.user_id == user_id,
                AssessmentAttempt.status == "completed",
            )
            .order_by(desc(AssessmentAttempt.completed_at))
        )
        attempts = (await db.scalars(asmt_stmt)).all()

        for att in attempts:
            asmt = att.assessment
            if not asmt or att.score_percentage is None:
                continue

            asmt_skill_id = asmt.skill_id
            overall_pct = float(att.score_percentage)

            # Map to canonical skill
            canonical_skill = normalize_skill_name(asmt_skill_id) or asmt_skill_id
            completed_str = att.completed_at.strftime("%Y-%m-%d") if att.completed_at else "recent"

            evidence_item = EvidenceItem(
                source="assessment",
                title=f"{asmt.title} ({overall_pct:.0f}%)",
                description=f"Objective diagnostic test completed on {completed_str}. Scored {overall_pct:.1f}%.",
                score=overall_pct,
                confidence_score=0.90 if att.passed else 0.70,
                is_verified=True,
                date=att.completed_at.isoformat() if att.completed_at else None,
            )
            add_evidence(canonical_skill, evidence_item)

            # Check if this assessment also validates related skills
            # (e.g. sql-databases validates postgresql and sql)
            if canonical_skill == "sql-databases":
                add_evidence("sql", evidence_item)
                add_evidence("postgresql", evidence_item)
            elif canonical_skill == "javascript-typescript":
                add_evidence("javascript", evidence_item)
                add_evidence("typescript", evidence_item)
            elif canonical_skill == "web-development":
                add_evidence("rest-apis", evidence_item)
            elif canonical_skill == "ai-llm":
                add_evidence("rag", evidence_item)

        # 2. Gather UserSkills
        for us in profile.user_skills:
            canonical_id = normalize_skill_name(us.skill_id) or us.skill_id
            conf = float(us.confidence_score)
            evidence_item = EvidenceItem(
                source="profile",
                title=f"Profile Skill: {us.skill.name if us.skill else us.skill_id}",
                description=f"Confidence {conf:.2f}, tier '{us.proficiency_tier}', primary source '{us.primary_source}'.",
                score=conf * 100.0,
                confidence_score=conf,
                is_verified=us.is_verified,
                date=us.last_evidence_at.isoformat() if us.last_evidence_at else None,
            )
            add_evidence(canonical_id, evidence_item)

        # 3. Gather Projects
        for proj in profile.projects:
            technologies = proj.technologies or []
            for tech in technologies:
                canonical_id = normalize_skill_name(tech)
                if canonical_id:
                    evidence_item = EvidenceItem(
                        source="project",
                        title=f"Project: {proj.title}",
                        description=f"Applied in project '{proj.title}' with {len(proj.bullet_points or [])} implementation highlights.",
                        confidence_score=0.50,
                        is_verified=False,  # Unverified unless tested
                        date=proj.created_at.isoformat() if proj.created_at else None,
                    )
                    add_evidence(canonical_id, evidence_item)

        return evidence_by_skill

    def _calibrate_skill_competency(
        self,
        evidence_items: List[EvidenceItem],
    ) -> Tuple[int, str, bool]:
        """
        Calibrates candidate evidence into a deterministic proficiency level (0-4),
        tier name, and verification flag.
        Levels:
          0: No Evidence (Unobserved)
          1: Foundational (Score < 50% or basic self-report)
          2: Developing (Score 50-69% or demonstrated profile/project claim)
          3: Proficient (Score 70-84% passed test)
          4: Advanced (Score >= 85% passed test)
        """
        if not evidence_items:
            return 0, "unverified", False

        has_assessment = any(e.source == "assessment" for e in evidence_items)
        max_assessment_score = max(
            [e.score for e in evidence_items if e.source == "assessment" and e.score is not None] or [0.0]
        )
        is_verified = has_assessment or any(e.is_verified for e in evidence_items)

        # 1. Assessment-backed calibration (highest authority)
        if has_assessment:
            if max_assessment_score >= 85.0:
                return 4, "mastered", True
            elif max_assessment_score >= 70.0:
                return 3, "proficient", True
            elif max_assessment_score >= 50.0:
                return 2, "demonstrated", True
            else:
                return 1, "basic", True

        # 2. Verified UserSkill calibration
        verified_us = [e for e in evidence_items if e.is_verified]
        if verified_us:
            max_conf = max(e.confidence_score for e in verified_us)
            if max_conf >= 0.85:
                return 4, "mastered", True
            elif max_conf >= 0.70:
                return 3, "proficient", True
            elif max_conf >= 0.50:
                return 2, "demonstrated", True
            else:
                return 1, "basic", True

        # 3. Unverified evidence (Resume / Profile claims / Projects)
        # Note: Unverified claims can NEVER reach Proficient (3) or Mastered (4)!
        # At most they reach Developing (2) if supported by projects, or Foundational (1).
        has_projects = any(e.source == "project" for e in evidence_items)
        if has_projects:
            return 2, "demonstrated", False

        return 1, "basic", False

    def _prioritize_skill_gaps(
        self,
        skill_details: Dict[str, SkillCompetencyDetail],
    ) -> List[PrioritizedGap]:
        """
        Deterministically ranks all gaps, missing skills, and developing skills
        to produce actionable next steps.
        """
        gap_items: List[SkillCompetencyDetail] = [
            d for d in skill_details.values()
            if d.status in ("GAP", "NOT_IN_PROFILE", "NOT_ASSESSED", "DEVELOPING")
        ]

        def sort_key(d: SkillCompetencyDetail) -> Tuple[int, int, float]:
            # 1. Importance (mandatory = 0, preferred = 1, bonus = 2)
            imp_order = {"mandatory": 0, "preferred": 1, "bonus": 2}.get(d.importance, 3)
            # 2. Deficit gap size (required_level - current_level) descending
            gap_size = d.required_level - d.current_level
            # 3. Weight descending
            return (imp_order, -gap_size, -d.weight)

        gap_items.sort(key=sort_key)

        prioritized: List[PrioritizedGap] = []
        for rank, item in enumerate(gap_items, start=1):
            gap_size = item.required_level - item.current_level

            # Priority assignment
            if item.importance == "mandatory":
                priority = "CRITICAL" if gap_size >= 2 else "HIGH"
            elif item.importance == "preferred":
                priority = "HIGH" if gap_size >= 2 else "MEDIUM"
            else:
                priority = "LOW"

            # Action determination
            asmt_id = get_assessment_id_for_skill(item.skill_id)
            if item.status == "NOT_ASSESSED" and asmt_id:
                action_type = "TAKE_ASSESSMENT"
                action_desc = f"Complete the diagnostic test for {item.skill_name} to verify your claimed knowledge."
            elif item.status == "NOT_IN_PROFILE":
                action_type = "STUDY_TOPIC"
                action_desc = f"Study foundational {item.skill_name} concepts and complete hands-on introductory tutorials."
            elif item.status == "DEVELOPING":
                action_type = "PRACTICE_TOPIC"
                action_desc = f"Bridge from level {item.current_level} to {item.required_level} through targeted problem sets."
            else:
                action_type = "BUILD_PROJECT"
                action_desc = f"Build an applied software project implementing {item.skill_name} in production-like conditions."

            reason = (
                f"{item.importance.capitalize()} requirement for target role. "
                f"Current level {item.current_level} vs required level {item.required_level}."
            )

            prioritized.append(
                PrioritizedGap(
                    rank=rank,
                    skill_id=item.skill_id,
                    skill_name=item.skill_name,
                    priority=priority,
                    importance=item.importance,
                    required_level=item.required_level,
                    current_level=item.current_level,
                    reason=reason,
                    action_type=action_type,
                    action_description=action_desc,
                    assessment_id=str(asmt_id) if asmt_id else None,
                )
            )

        return prioritized

    def _determine_recommended_assessments(
        self,
        skill_details: Dict[str, SkillCompetencyDetail],
    ) -> List[RecommendedAssessment]:
        """Identifies diagnostic assessments recommended to verify gaps and unassessed skills."""
        recommended: List[RecommendedAssessment] = []
        seen_asmt_ids: Set[str] = set()

        # Prioritize mandatory gaps, missing, and unassessed skills
        for item in skill_details.values():
            if item.status in ("NOT_IN_PROFILE", "NOT_ASSESSED", "GAP", "DEVELOPING"):
                asmt_info = get_recommended_assessment_for_skill(
                    item.skill_id,
                    reason=f"Recommended to diagnose and verify competency in {item.skill_name} ({item.importance} requirement).",
                )
                if asmt_info and asmt_info["assessment_id"] not in seen_asmt_ids:
                    seen_asmt_ids.add(asmt_info["assessment_id"])
                    recommended.append(
                        RecommendedAssessment(
                            assessment_id=asmt_info["assessment_id"],
                            title=asmt_info["title"],
                            skill_id=asmt_info["skill_id"],
                            reason=asmt_info["reason"],
                            estimated_minutes=asmt_info["estimated_minutes"],
                            question_count=asmt_info["question_count"],
                        )
                    )

        return recommended

    def _generate_diagnostic_narrative(
        self,
        role_title: str,
        alignment_score: float,
        coverage_score: float,
        strongest: List[str],
        developing: List[str],
        gaps: List[str],
        missing: List[str],
        unassessed: List[str],
        prioritized_gaps: List[PrioritizedGap],
    ) -> str:
        """Constructs a deterministic, human-readable explanatory report."""
        paragraphs = []

        # Paragraph 1: Executive Alignment Summary
        paragraphs.append(
            f"Based on your validated diagnostic assessments and career profile evidence, your benchmark "
            f"alignment for the {role_title} role is {alignment_score:.1f}% with an evidence coverage score of {coverage_score:.1f}%."
        )

        # Paragraph 2: Strengths
        if strongest:
            strong_str = ", ".join(strongest[:5])
            paragraphs.append(
                f"Your primary verified strengths meeting or exceeding role standards include: {strong_str}."
            )
        else:
            paragraphs.append(
                "No verified competencies currently meet the required role benchmarks. "
                "Completing diagnostic skill assessments will establish verified baseline scores."
            )

        # Paragraph 3: Core Gaps and Unassessed Competencies
        issues = []
        if unassessed:
            issues.append(f"{len(unassessed)} unverified claimed skills ({', '.join(unassessed[:3])})")
        if gaps:
            issues.append(f"{len(gaps)} confirmed gaps ({', '.join(gaps[:3])})")
        if missing:
            issues.append(f"{len(missing)} missing competencies ({', '.join(missing[:3])})")

        if issues:
            paragraphs.append(
                f"Key areas requiring attention include: {'; '.join(issues)}."
            )

        # Paragraph 4: Top Actionable Next Step
        if prioritized_gaps:
            top_gap = prioritized_gaps[0]
            paragraphs.append(
                f"Highest priority action ({top_gap.priority}): {top_gap.action_description}"
            )

        return " \n\n".join(paragraphs)
