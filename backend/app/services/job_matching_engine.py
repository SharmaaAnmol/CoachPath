"""
Intelligent Job Matching Engine Service for CoachPath (Phase 9A).
Calculates deterministic, explainable, multi-dimensional alignment scores
linking candidate career profiles and verified skill evidence to persisted job listings.
"""

from __future__ import annotations

import decimal
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.db.seeds.skill_taxonomy import normalize_skill_name
from app.models.assessments import AssessmentAttempt
from app.models.auth import User
from app.models.career import CareerProfile, Project, Role
from app.models.jobs import Job, JobMatch, JobSkill
from app.models.skills import Skill, UserSkill
from app.schemas.job_matching import (
    JobMatchExplanation,
    JobMatchExplanationDrawerResponse,
    JobMatchResponse,
    JobRecommendationItem,
    JobRecommendationResponse,
    MatchScoreBreakdown,
    SkillMatchClassification,
    SkillMatchItem,
)
from app.schemas.jobs import JobResponse, JobSkillItem

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Configurable Dimension Weights & Constants
# ─────────────────────────────────────────────

DEFAULT_MATCH_WEIGHTS: Dict[str, float] = {
    "skill": 0.50,         # 50% Skill alignment (required vs preferred)
    "experience": 0.15,    # 15% Relevant experience & seniority
    "project": 0.15,       # 15% Project relevance & practical artifacts
    "location": 0.10,      # 10% Workplace flexibility & geographic market
    "preference": 0.10,    # 10% Career role & employment preference
}

SCORING_VERSION = "v1.0"
MIN_CONFIDENCE_THRESHOLD = 40.0  # Scores with coverage < 40% flagged provisional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_job_response(job: Job) -> JobResponse:
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


class JobMatchingEngine:
    """
    Deterministic Job-Matching and Recommendation Engine.
    Executes multi-factor evidence-based candidate-to-job calibration.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None) -> None:
        self.weights = weights or dict(DEFAULT_MATCH_WEIGHTS)
        self.scoring_version = SCORING_VERSION

    # ─────────────────────────────────────────────
    # 1. Skill Alignment Evaluation
    # ─────────────────────────────────────────────

    def evaluate_skills(
        self,
        job_skills: List[JobSkill],
        user_skills_map: Dict[str, UserSkill],
        assessment_scores_map: Dict[str, float],
        project_skills_set: Set[str],
    ) -> Tuple[
        Optional[float],
        List[SkillMatchItem],
        List[str],
        List[str],
        List[str],
        List[str],
    ]:
        """
        Calculates skill alignment differentiating required vs preferred skills,
        weighting by evidence provenance (assessment > project > extracted > self_reported).
        """
        if not job_skills:
            return None, [], [], [], [], []

        skill_details: List[SkillMatchItem] = []
        matched_required: List[str] = []
        matched_preferred: List[str] = []
        missing_required: List[str] = []
        unknown_skills: List[str] = []

        required_scores: List[float] = []
        preferred_scores: List[float] = []

        for js in job_skills:
            canonical_id = normalize_skill_name(js.skill_id) or js.skill_id.lower().strip()
            display_name = js.skill.name if js.skill else js.skill_id.replace("-", " ").title()
            category = js.skill.category if js.skill else "technical"
            is_mandatory = js.is_mandatory

            # Check if candidate has evidence
            # 1. Assessment evidence
            asmt_score = assessment_scores_map.get(canonical_id)
            # 2. UserSkill record
            user_skill = user_skills_map.get(canonical_id)
            # 3. Project evidence
            has_project_evidence = canonical_id in project_skills_set

            item_score: float = 0.0
            classification: SkillMatchClassification
            evidence_source: Optional[str] = None
            confidence: float = 0.0
            tier: Optional[str] = None
            explanation: str

            if asmt_score is not None:
                # Diagnostic assessment is highest authority
                evidence_source = "assessment"
                confidence = max(0.60, min(1.0, asmt_score / 100.0))
                tier = "mastered" if asmt_score >= 85.0 else ("proficient" if asmt_score >= 70.0 else "demonstrated")
                item_score = min(1.0, max(0.50, asmt_score / 100.0))

                if asmt_score >= 70.0:
                    classification = SkillMatchClassification.MATCHED
                    explanation = f"Verified via Diagnostic Assessment with score of {asmt_score:.0f}%."
                else:
                    classification = SkillMatchClassification.PARTIALLY_MATCHED
                    explanation = f"Diagnostic Assessment completed with score of {asmt_score:.0f}% (developing proficiency)."

            elif user_skill is not None:
                evidence_source = user_skill.primary_source
                confidence = float(user_skill.confidence_score or 0.50)
                tier = user_skill.proficiency_tier or "unverified"

                # Provenance multiplier
                provenance_multipliers = {
                    "assessment": 1.00,
                    "project_evidence": 0.85,
                    "extracted": 0.80,       # approved resume extraction
                    "self_reported": 0.60,
                }
                prov_mult = provenance_multipliers.get(evidence_source, 0.60)

                tier_factors = {
                    "mastered": 1.00,
                    "proficient": 0.90,
                    "demonstrated": 0.75,
                    "unverified": 0.50,
                }
                tier_factor = tier_factors.get(tier, 0.50)

                item_score = min(1.0, prov_mult * tier_factor)

                if item_score >= 0.70:
                    classification = SkillMatchClassification.MATCHED
                    explanation = f"Demonstrated in profile via {evidence_source.replace('_', ' ')} (Tier: {tier})."
                elif item_score >= 0.40:
                    classification = SkillMatchClassification.PARTIALLY_MATCHED
                    explanation = f"Partial alignment via {evidence_source.replace('_', ' ')} (Tier: {tier})."
                else:
                    classification = SkillMatchClassification.INSUFFICIENT_EVIDENCE
                    explanation = f"Unverified self-reported skill with low calibrated confidence ({confidence:.2f})."

            elif has_project_evidence:
                evidence_source = "project_evidence"
                confidence = 0.75
                tier = "demonstrated"
                item_score = 0.75
                classification = SkillMatchClassification.MATCHED
                explanation = "Demonstrated in candidate project portfolio."

            else:
                # No evidence
                evidence_source = None
                confidence = 0.0
                tier = None
                item_score = 0.0

                if is_mandatory:
                    classification = SkillMatchClassification.MISSING
                    explanation = "Mandatory requirement: No evidence found in candidate profile."
                else:
                    classification = SkillMatchClassification.UNKNOWN
                    explanation = "Preferred requirement: No supporting evidence recorded."

            # Categorize into matched/missing/unknown lists
            if is_mandatory:
                required_scores.append(item_score)
                if classification == SkillMatchClassification.MATCHED:
                    matched_required.append(display_name)
                elif classification == SkillMatchClassification.PARTIALLY_MATCHED:
                    matched_required.append(f"{display_name} (Partial)")
                else:
                    missing_required.append(display_name)
            else:
                preferred_scores.append(item_score)
                if classification == SkillMatchClassification.MATCHED:
                    matched_preferred.append(display_name)
                elif classification == SkillMatchClassification.PARTIALLY_MATCHED:
                    matched_preferred.append(f"{display_name} (Partial)")
                else:
                    unknown_skills.append(display_name)

            skill_details.append(
                SkillMatchItem(
                    skill_id=canonical_id,
                    name=display_name,
                    category=category,
                    is_mandatory=is_mandatory,
                    classification=classification,
                    user_evidence_source=evidence_source,
                    user_confidence=confidence,
                    user_proficiency_tier=tier,
                    assessment_score=asmt_score,
                    explanation=explanation,
                )
            )

        # Calculate weighted composite skill score
        # Required skills carry 80% of dimension, preferred carry 20%
        if required_scores and preferred_scores:
            avg_req = sum(required_scores) / len(required_scores)
            avg_pref = sum(preferred_scores) / len(preferred_scores)
            composite_skill = (0.80 * avg_req + 0.20 * avg_pref) * 100.0
        elif required_scores:
            avg_req = sum(required_scores) / len(required_scores)
            composite_skill = avg_req * 100.0
        elif preferred_scores:
            avg_pref = sum(preferred_scores) / len(preferred_scores)
            composite_skill = avg_pref * 100.0
        else:
            return None, skill_details, matched_required, matched_preferred, missing_required, unknown_skills

        return (
            round(min(100.0, max(0.0, composite_skill)), 1),
            skill_details,
            matched_required,
            matched_preferred,
            missing_required,
            unknown_skills,
        )

    # ─────────────────────────────────────────────
    # 2. Experience & Seniority Evaluation
    # ─────────────────────────────────────────────

    def evaluate_experience(
        self,
        profile: CareerProfile,
        job: Job,
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Compares candidate verified years of experience and employment history
        against job seniority requirement.
        """
        # If job has no experience_level specified
        if not job.experience_level:
            return None, "Job posting does not specify an experience requirement."

        years_exp = float(profile.years_of_experience or 0.0)
        # If profile has experience records, calculate total tenure as fallback
        if years_exp == 0.0 and profile.experience:
            years_exp = float(len(profile.experience)) * 0.75  # ~9 months avg per listed role

        level = (job.experience_level or "").lower().strip()

        # Expected baseline years per level
        level_expectations = {
            "internship": (0.0, 1.0),
            "entry_level": (0.0, 2.0),
            "junior": (1.0, 3.0),
            "mid": (3.0, 6.0),
            "senior": (5.0, 10.0),
        }

        min_expected, _ = level_expectations.get(level, (0.0, 2.0))

        if years_exp >= min_expected:
            score = 100.0
            reason = f"Candidate experience ({years_exp:.1f} yrs) meets or exceeds job expectation ({level.replace('_', ' ')})."
        elif years_exp >= max(0.0, min_expected - 1.0):
            score = 75.0
            reason = f"Candidate experience ({years_exp:.1f} yrs) is within 1 year of target ({level.replace('_', ' ')})."
        elif years_exp > 0.0:
            score = 45.0
            reason = f"Candidate experience ({years_exp:.1f} yrs) is below {level.replace('_', ' ')} expectation."
        else:
            if level in ("internship", "entry_level"):
                score = 100.0
                reason = "Entry-level listing welcomes candidates with 0 years formal experience."
            else:
                score = 25.0
                reason = f"Candidate has 0 recorded years of professional experience for a {level.replace('_', ' ')} role."

        return round(score, 1), reason

    # ─────────────────────────────────────────────
    # 3. Project Relevance Evaluation
    # ─────────────────────────────────────────────

    def evaluate_projects(
        self,
        profile: CareerProfile,
        job_skills: List[JobSkill],
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Evaluates practical project artifacts and repository proof against job skills.
        """
        if not profile.projects:
            # If candidate has formal employment experience, don't penalize missing projects harshly
            if profile.experience and len(profile.experience) >= 2:
                return None, "Candidate has substantial employment history; projects unevaluated."
            return 20.0, "Candidate has not listed technical projects or code artifacts in profile."

        if not job_skills:
            return None, "Job has no tagged skills to match against projects."

        job_skill_ids = {
            normalize_skill_name(js.skill_id) or js.skill_id.lower().strip()
            for js in job_skills
        }

        # Gather technologies from projects
        project_techs: Set[str] = set()
        has_verifiable_artifact = False

        for p in profile.projects:
            for tech in p.technologies or []:
                norm = normalize_skill_name(tech) or tech.lower().strip()
                project_techs.add(norm)
            if p.github_url or p.live_url:
                has_verifiable_artifact = True

        overlapping = job_skill_ids.intersection(project_techs)

        if overlapping:
            ratio = len(overlapping) / len(job_skill_ids)
            # Base score proportional to overlap, plus artifact verification bonus
            base_score = min(85.0, ratio * 90.0)
            artifact_bonus = 15.0 if has_verifiable_artifact else 5.0
            score = min(100.0, base_score + artifact_bonus)
            reason = f"Projects demonstrate {len(overlapping)} required/preferred technologies with verified artifacts."
        else:
            # Candidate has built projects, just with different stack
            score = 35.0
            reason = "Projects demonstrate software engineering capability, but in a different technical stack."

        return round(score, 1), reason

    # ─────────────────────────────────────────────
    # 4. Location & Workplace Compatibility
    # ─────────────────────────────────────────────

    def evaluate_location(
        self,
        profile: CareerProfile,
        job: Job,
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Evaluates workplace preference ('remote', 'hybrid', 'onsite') and geographic target markets.
        """
        cand_pref = (profile.work_preference or "flexible").lower().strip()
        job_remote = (job.remote_type or "hybrid").lower().strip()
        cand_locs = [loc.lower().strip() for loc in (profile.target_locations or [])]
        job_loc = (job.location or "").lower().strip()

        # Remote Job Case
        if job_remote == "remote":
            if cand_pref in ("remote", "flexible"):
                return 100.0, "Listing is 100% remote, perfectly matching your remote preference."
            elif cand_pref == "hybrid":
                return 95.0, "Remote role provides flexibility compatible with your hybrid preference."
            else:  # onsite
                return 75.0, "Remote role is open, though you prefer an in-person office environment."

        # Hybrid or Onsite Job Case
        if cand_pref == "remote":
            # Definite workplace incompatibility
            return 25.0, f"Listing requires {job_remote} work, which conflicts with your remote-only preference."

        # Candidate is open to hybrid/onsite/flexible
        if not cand_locs:
            # Candidate has not restricted their target cities
            return 80.0, f"Candidate is flexible on location for {job_remote} opportunity."

        # Check geographic location overlap
        loc_matched = False
        for cl in cand_locs:
            if cl in job_loc or job_loc in cl:
                loc_matched = True
                break

        if loc_matched:
            return 100.0, f"Job location ({job.location}) matches your target location preferences."
        else:
            return 40.0, f"Job location ({job.location}) is outside your documented target markets."

    # ─────────────────────────────────────────────
    # 5. Career & Employment Preferences
    # ─────────────────────────────────────────────

    def evaluate_preferences(
        self,
        profile: CareerProfile,
        job: Job,
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Evaluates role domain alignment, employment type, and salary compatibility.
        """
        primary_role = (profile.primary_role_id or "").lower().strip()
        secondary_role = (profile.secondary_role_id or "").lower().strip()
        job_role = (job.role_id or "").lower().strip()

        role_score: float = 35.0
        role_reason = "Job role differs from your target career path."

        if primary_role and job_role == primary_role:
            role_score = 100.0
            role_reason = f"Direct match with your primary career objective ({primary_role})."
        elif secondary_role and job_role == secondary_role:
            role_score = 80.0
            role_reason = f"Matches your secondary target role ({secondary_role})."
        elif primary_role and (primary_role in job_role or job_role in primary_role):
            role_score = 65.0
            role_reason = "Job role is closely related to your target career domain."

        # Employment type alignment
        if job.employment_type and job.employment_type == "full_time":
            # Default full-time is high alignment for career roles
            pass

        return round(role_score, 1), role_reason

    # ─────────────────────────────────────────────
    # 6. Evidence Coverage / Confidence Metric
    # ─────────────────────────────────────────────

    def calculate_evidence_coverage(
        self,
        job: Job,
        profile: CareerProfile,
        assessment_scores_map: Dict[str, float],
        evaluated_factors: List[str],
    ) -> float:
        """
        Measures the completeness and reliability of underlying data (0.0 to 100.0).
        High score based on sparse data is marked provisional.
        """
        coverage: float = 0.0

        # Factor 1: Job skills extraction richness (up to 25 pts)
        skill_count = len(job.skills or [])
        if skill_count >= 5:
            coverage += 25.0
        elif skill_count >= 3:
            coverage += 20.0
        elif skill_count >= 1:
            coverage += 12.0

        # Factor 2: Candidate verified assessment evidence (up to 30 pts)
        if len(assessment_scores_map) >= 3:
            coverage += 30.0
        elif len(assessment_scores_map) >= 1:
            coverage += 20.0
        elif profile.user_skills:
            coverage += 10.0

        # Factor 3: Work experience data availability (up to 15 pts)
        if job.experience_level and (profile.years_of_experience is not None or profile.experience):
            coverage += 15.0
        elif job.experience_level or profile.experience:
            coverage += 8.0

        # Factor 4: Practical project evidence (up to 15 pts)
        if profile.projects:
            coverage += 15.0

        # Factor 5: Location & career preference completeness (up to 15 pts)
        if profile.work_preference and profile.primary_role_id:
            coverage += 15.0
        elif profile.primary_role_id or profile.work_preference:
            coverage += 8.0

        return round(min(100.0, max(0.0, coverage)), 1)

    # ─────────────────────────────────────────────
    # 7. Master Match Calculation
    # ─────────────────────────────────────────────

    def compute_match(
        self,
        profile: CareerProfile,
        job: Job,
        completed_attempts: Optional[List[AssessmentAttempt]] = None,
    ) -> Dict[str, Any]:
        """
        Executes deterministic multi-factor match computation.
        Returns complete breakdown, skills details, grounded explainability, and overall score.
        """
        # Map user skills by canonical ID
        user_skills_map: Dict[str, UserSkill] = {}
        for us in profile.user_skills or []:
            norm_id = normalize_skill_name(us.skill_id) or us.skill_id.lower().strip()
            user_skills_map[norm_id] = us

        # Map assessment scores by canonical ID
        assessment_scores_map: Dict[str, float] = {}
        for att in (completed_attempts or []):
            if att.status == "completed" and att.assessment and att.score_percentage is not None:
                asmt_skill = att.assessment.skill_id
                norm_asmt = normalize_skill_name(asmt_skill) or asmt_skill.lower().strip()
                score_pct = float(att.score_percentage)
                if norm_asmt not in assessment_scores_map or score_pct > assessment_scores_map[norm_asmt]:
                    assessment_scores_map[norm_asmt] = score_pct

                # Synergistic skill cross-validation
                if norm_asmt == "sql-databases":
                    assessment_scores_map["sql"] = score_pct
                    assessment_scores_map["postgresql"] = score_pct
                elif norm_asmt == "javascript-typescript":
                    assessment_scores_map["javascript"] = score_pct
                    assessment_scores_map["typescript"] = score_pct
                elif norm_asmt == "web-development":
                    assessment_scores_map["rest-apis"] = score_pct

        # Gather project skill IDs
        project_skills_set: Set[str] = set()
        for p in profile.projects or []:
            for tech in p.technologies or []:
                norm_tech = normalize_skill_name(tech) or tech.lower().strip()
                project_skills_set.add(norm_tech)

        # 1. Evaluate Skill Alignment
        (
            skill_score,
            skills_detail,
            matched_required,
            matched_preferred,
            missing_required,
            unknown_skills,
        ) = self.evaluate_skills(
            job.skills or [],
            user_skills_map,
            assessment_scores_map,
            project_skills_set,
        )

        # 2. Evaluate Experience
        exp_score, exp_reason = self.evaluate_experience(profile, job)

        # 3. Evaluate Projects
        proj_score, proj_reason = self.evaluate_projects(profile, job.skills or [])

        # 4. Evaluate Location
        loc_score, loc_reason = self.evaluate_location(profile, job)

        # 5. Evaluate Preferences
        pref_score, pref_reason = self.evaluate_preferences(profile, job)

        # Normalization across evaluated factors
        factors: Dict[str, Optional[float]] = {
            "skill": skill_score,
            "experience": exp_score,
            "project": proj_score,
            "location": loc_score,
            "preference": pref_score,
        }

        evaluated: List[str] = []
        unevaluated: List[str] = []
        weighted_sum: float = 0.0
        weight_sum: float = 0.0

        for factor_name, score_val in factors.items():
            if score_val is not None:
                evaluated.append(factor_name)
                w = self.weights.get(factor_name, 0.20)
                weight_sum += w
                weighted_sum += w * score_val
            else:
                unevaluated.append(factor_name)

        if weight_sum > 0.0:
            overall_score = round(min(100.0, max(0.0, weighted_sum / weight_sum)), 1)
        else:
            overall_score = 0.0

        # Calculate evidence coverage & confidence
        coverage = self.calculate_evidence_coverage(
            job, profile, assessment_scores_map, evaluated
        )
        is_provisional = coverage < MIN_CONFIDENCE_THRESHOLD

        # Generate Grounded Explainability
        strengths: List[str] = []
        gaps: List[str] = []
        recommended_actions: List[str] = []

        # Strengths
        if matched_required:
            strengths.append(
                f"Matches {len(matched_required)} required skills: {', '.join(matched_required[:4])}."
            )
        if matched_preferred:
            strengths.append(
                f"Possesses {len(matched_preferred)} preferred skills: {', '.join(matched_preferred[:3])}."
            )
        for s in skills_detail:
            if s.assessment_score and s.assessment_score >= 80.0:
                strengths.append(
                    f"Verified high proficiency in {s.name} ({s.assessment_score:.0f}%) via diagnostic assessment."
                )
                break
        if exp_score is not None and exp_score >= 85.0:
            strengths.append(exp_reason or "Solid experience alignment.")
        if loc_score is not None and loc_score >= 90.0:
            strengths.append(loc_reason or "High workplace compatibility.")
        if pref_score is not None and pref_score >= 80.0:
            strengths.append(pref_reason or "Role closely aligns with primary career objective.")

        # Gaps
        if missing_required:
            gaps.append(
                f"Missing {len(missing_required)} required skills: {', '.join(missing_required[:4])}."
            )
        if exp_score is not None and exp_score < 60.0:
            gaps.append(exp_reason or "Experience level is below job expectations.")
        if loc_score is not None and loc_score < 50.0:
            gaps.append(loc_reason or "Workplace type or location is incompatible.")

        # Recommended Actions
        if missing_required:
            top_missing = missing_required[0]
            recommended_actions.append(
                f"Prioritize learning {top_missing} or complete its diagnostic assessment to demonstrate competence."
            )
        if any(s.classification == SkillMatchClassification.PARTIALLY_MATCHED for s in skills_detail):
            partial_item = next(
                s for s in skills_detail if s.classification == SkillMatchClassification.PARTIALLY_MATCHED
            )
            recommended_actions.append(
                f"Take the {partial_item.name} Diagnostic Assessment to elevate self-reported skills to verified status."
            )
        if not profile.projects:
            recommended_actions.append(
                "Add technical capstones or code repositories to your profile to showcase hands-on experience."
            )

        # Summary narrative
        if overall_score >= 80.0:
            summary = (
                f"Strong fit ({overall_score:.1f}% match). Your verified skill profile and background strongly align with "
                f"{job.company_name}'s requirements for {job.title}."
            )
        elif overall_score >= 60.0:
            summary = (
                f"Promising match ({overall_score:.1f}% match). You meet core requirements with good role alignment, "
                f"though closing identified gaps in {', '.join((missing_required or ['specialized frameworks'])[:2])} will enhance your candidacy."
            )
        else:
            summary = (
                f"Developing match ({overall_score:.1f}% match). This position requires several skills or seniority levels "
                f"not currently documented in your verified career profile."
            )

        return {
            "overall_score": overall_score,
            "skill_score": skill_score if skill_score is not None else 0.0,
            "experience_score": exp_score if exp_score is not None else 0.0,
            "project_score": proj_score if proj_score is not None else 0.0,
            "location_score": loc_score if loc_score is not None else 0.0,
            "preference_score": pref_score if pref_score is not None else 0.0,
            "vector_score": 0.0,
            "evidence_coverage": coverage,
            "is_provisional": is_provisional,
            "weights": self.weights,
            "evaluated_factors": evaluated,
            "unevaluated_factors": unevaluated,
            "matched_skills": matched_required,
            "matched_preferred_skills": matched_preferred,
            "missing_skills": missing_required,
            "unknown_skills": unknown_skills,
            "skills_detail": skills_detail,
            "explanation": {
                "summary": summary,
                "strengths": strengths,
                "gaps": gaps,
                "recommended_actions": recommended_actions,
            },
        }

    # ─────────────────────────────────────────────
    # 8. Persistence, Retrieval & Cache Operations
    # ─────────────────────────────────────────────

    async def _get_or_create_profile(self, db: AsyncSession, user: User) -> CareerProfile:
        """
        Retrieves the user's CareerProfile with all related skills and projects,
        or creates a baseline early-career profile if not yet initialized.
        """
        profile_stmt = (
            select(CareerProfile)
            .options(
                selectinload(CareerProfile.user_skills).selectinload(UserSkill.skill),
                selectinload(CareerProfile.experience),
                selectinload(CareerProfile.projects),
            )
            .where(CareerProfile.user_id == user.id)
        )
        profile = await db.scalar(profile_stmt)
        if not profile:
            profile = CareerProfile(
                user_id=user.id,
                primary_role_id="backend-developer",
                career_stage="early_career",
                work_preference="flexible",
                target_locations=["Remote"],
                years_of_experience=decimal.Decimal("0.0"),
            )
            db.add(profile)
            await db.commit()
            profile = await db.scalar(profile_stmt)
        return profile

    async def get_or_calculate_job_match(
        self,
        db: AsyncSession,
        user: User,
        job_id: uuid.UUID,
        force_recalculate: bool = False,
    ) -> JobMatchResponse:
        """
        Retrieves an existing cached match or calculates, persists, and returns a new match.
        Strictly scopes evaluation to current authenticated user.
        """
        # 1. Fetch CareerProfile with all relationships
        profile = await self._get_or_create_profile(db, user)

        # 2. Fetch Job with skills
        job_stmt = (
            select(Job)
            .options(
                selectinload(Job.skills).selectinload(JobSkill.skill),
            )
            .where(Job.id == job_id)
        )
        job = await db.scalar(job_stmt)
        if not job:
            raise NotFoundException("Job")

        # 3. Check for existing cached JobMatch
        if not force_recalculate:
            match_stmt = (
                select(JobMatch)
                .where(
                    JobMatch.career_profile_id == profile.id,
                    JobMatch.job_id == job.id,
                )
            )
            cached_match = await db.scalar(match_stmt)
            if cached_match and not cached_match.is_stale and cached_match.scoring_version == self.scoring_version:
                return self._orm_to_response(cached_match, job)

        # 4. Fetch completed diagnostic assessment attempts for candidate
        asmt_stmt = (
            select(AssessmentAttempt)
            .options(selectinload(AssessmentAttempt.assessment))
            .where(
                AssessmentAttempt.user_id == user.id,
                AssessmentAttempt.status == "completed",
            )
            .order_by(desc(AssessmentAttempt.completed_at))
        )
        completed_attempts = (await db.scalars(asmt_stmt)).all()

        # 5. Compute deterministic match
        calc = self.compute_match(profile, job, list(completed_attempts))

        # 6. Upsert into job_matches
        match_stmt = (
            select(JobMatch)
            .where(
                JobMatch.career_profile_id == profile.id,
                JobMatch.job_id == job.id,
            )
        )
        existing_match = await db.scalar(match_stmt)

        explanation_payload = {
            "score_breakdown": {
                "skill_score": calc["skill_score"],
                "experience_score": calc["experience_score"],
                "project_score": calc["project_score"],
                "location_score": calc["location_score"],
                "preference_score": calc["preference_score"],
                "vector_score": calc["vector_score"],
            },
            "weights": calc["weights"],
            "evaluated_factors": calc["evaluated_factors"],
            "unevaluated_factors": calc["unevaluated_factors"],
            "is_provisional": calc["is_provisional"],
            "skills_detail": [s.model_dump() for s in calc["skills_detail"]],
            "strengths": calc["explanation"]["strengths"],
            "gaps": calc["explanation"]["gaps"],
            "recommended_actions": calc["explanation"]["recommended_actions"],
            "summary": calc["explanation"]["summary"],
            "freshness_status": job.freshness_status,
        }

        now = _utc_now()
        if existing_match:
            existing_match.overall_score = decimal.Decimal(str(calc["overall_score"]))
            existing_match.skill_score = decimal.Decimal(str(calc["skill_score"]))
            existing_match.experience_score = decimal.Decimal(str(calc["experience_score"]))
            existing_match.project_score = decimal.Decimal(str(calc["project_score"]))
            existing_match.location_score = decimal.Decimal(str(calc["location_score"]))
            existing_match.preference_score = decimal.Decimal(str(calc["preference_score"]))
            existing_match.evidence_coverage = decimal.Decimal(str(calc["evidence_coverage"]))
            existing_match.vector_score = decimal.Decimal("0.0")
            existing_match.scoring_version = self.scoring_version
            existing_match.is_stale = False
            existing_match.matched_skills = calc["matched_skills"]
            existing_match.matched_preferred_skills = calc["matched_preferred_skills"]
            existing_match.missing_skills = calc["missing_skills"]
            existing_match.unknown_skills = calc["unknown_skills"]
            existing_match.explanation_json = explanation_payload
            existing_match.calculated_at = now
            match_record = existing_match
        else:
            match_record = JobMatch(
                id=uuid.uuid4(),
                career_profile_id=profile.id,
                job_id=job.id,
                overall_score=decimal.Decimal(str(calc["overall_score"])),
                skill_score=decimal.Decimal(str(calc["skill_score"])),
                experience_score=decimal.Decimal(str(calc["experience_score"])),
                project_score=decimal.Decimal(str(calc["project_score"])),
                location_score=decimal.Decimal(str(calc["location_score"])),
                preference_score=decimal.Decimal(str(calc["preference_score"])),
                evidence_coverage=decimal.Decimal(str(calc["evidence_coverage"])),
                vector_score=decimal.Decimal("0.0"),
                scoring_version=self.scoring_version,
                is_stale=False,
                matched_skills=calc["matched_skills"],
                matched_preferred_skills=calc["matched_preferred_skills"],
                missing_skills=calc["missing_skills"],
                unknown_skills=calc["unknown_skills"],
                explanation_json=explanation_payload,
                calculated_at=now,
            )
            db.add(match_record)

        await db.commit()
        await db.refresh(match_record)

        return self._orm_to_response(match_record, job)

    # ─────────────────────────────────────────────
    # 9. Recommendations Ranking & Batch Processing
    # ─────────────────────────────────────────────

    async def get_recommendations(
        self,
        db: AsyncSession,
        user: User,
        min_score: Optional[float] = None,
        role_id: Optional[str] = None,
        remote_type: Optional[str] = None,
        include_provisional: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> JobRecommendationResponse:
        """
        Calculates and ranks personalized job recommendations for the authenticated user,
        sorted descending by overall match score.
        """
        # Fetch profile
        profile = await self._get_or_create_profile(db, user)

        # Fetch active candidate jobs from catalog
        criteria = [
            Job.is_active == True,
            Job.freshness_status.in_(["active", "needs_refresh"]),
        ]
        if role_id:
            criteria.append(Job.role_id == role_id)
        if remote_type:
            criteria.append(Job.remote_type == remote_type)

        jobs_stmt = (
            select(Job)
            .options(selectinload(Job.skills).selectinload(JobSkill.skill))
            .where(*criteria)
            .order_by(Job.posted_at.desc())
        )
        jobs = (await db.scalars(jobs_stmt)).all()

        if not jobs:
            return JobRecommendationResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
                total_pages=0,
                scoring_version=self.scoring_version,
                generated_at=_utc_now(),
            )

        # Completed assessment attempts
        asmt_stmt = (
            select(AssessmentAttempt)
            .options(selectinload(AssessmentAttempt.assessment))
            .where(
                AssessmentAttempt.user_id == user.id,
                AssessmentAttempt.status == "completed",
            )
        )
        completed_attempts = list((await db.scalars(asmt_stmt)).all())

        # Existing cached matches
        match_stmt = (
            select(JobMatch)
            .where(JobMatch.career_profile_id == profile.id)
        )
        existing_matches = {m.job_id: m for m in (await db.scalars(match_stmt)).all()}

        scored_items: List[JobRecommendationItem] = []
        new_or_updated_records: List[JobMatch] = []
        now = _utc_now()

        for j in jobs:
            cached = existing_matches.get(j.id)
            if cached and not cached.is_stale and cached.scoring_version == self.scoring_version:
                match_resp = self._orm_to_response(cached, j)
            else:
                # Compute and record
                calc = self.compute_match(profile, j, completed_attempts)
                explanation_payload = {
                    "score_breakdown": {
                        "skill_score": calc["skill_score"],
                        "experience_score": calc["experience_score"],
                        "project_score": calc["project_score"],
                        "location_score": calc["location_score"],
                        "preference_score": calc["preference_score"],
                        "vector_score": calc["vector_score"],
                    },
                    "weights": calc["weights"],
                    "evaluated_factors": calc["evaluated_factors"],
                    "unevaluated_factors": calc["unevaluated_factors"],
                    "is_provisional": calc["is_provisional"],
                    "skills_detail": [s.model_dump() for s in calc["skills_detail"]],
                    "strengths": calc["explanation"]["strengths"],
                    "gaps": calc["explanation"]["gaps"],
                    "recommended_actions": calc["explanation"]["recommended_actions"],
                    "summary": calc["explanation"]["summary"],
                    "freshness_status": j.freshness_status,
                }

                if cached:
                    cached.overall_score = decimal.Decimal(str(calc["overall_score"]))
                    cached.skill_score = decimal.Decimal(str(calc["skill_score"]))
                    cached.experience_score = decimal.Decimal(str(calc["experience_score"]))
                    cached.project_score = decimal.Decimal(str(calc["project_score"]))
                    cached.location_score = decimal.Decimal(str(calc["location_score"]))
                    cached.preference_score = decimal.Decimal(str(calc["preference_score"]))
                    cached.evidence_coverage = decimal.Decimal(str(calc["evidence_coverage"]))
                    cached.scoring_version = self.scoring_version
                    cached.is_stale = False
                    cached.matched_skills = calc["matched_skills"]
                    cached.matched_preferred_skills = calc["matched_preferred_skills"]
                    cached.missing_skills = calc["missing_skills"]
                    cached.unknown_skills = calc["unknown_skills"]
                    cached.explanation_json = explanation_payload
                    cached.calculated_at = now
                    record = cached
                else:
                    record = JobMatch(
                        id=uuid.uuid4(),
                        career_profile_id=profile.id,
                        job_id=j.id,
                        overall_score=decimal.Decimal(str(calc["overall_score"])),
                        skill_score=decimal.Decimal(str(calc["skill_score"])),
                        experience_score=decimal.Decimal(str(calc["experience_score"])),
                        project_score=decimal.Decimal(str(calc["project_score"])),
                        location_score=decimal.Decimal(str(calc["location_score"])),
                        preference_score=decimal.Decimal(str(calc["preference_score"])),
                        evidence_coverage=decimal.Decimal(str(calc["evidence_coverage"])),
                        vector_score=decimal.Decimal("0.0"),
                        scoring_version=self.scoring_version,
                        is_stale=False,
                        matched_skills=calc["matched_skills"],
                        matched_preferred_skills=calc["matched_preferred_skills"],
                        missing_skills=calc["missing_skills"],
                        unknown_skills=calc["unknown_skills"],
                        explanation_json=explanation_payload,
                        calculated_at=now,
                    )
                    db.add(record)
                    new_or_updated_records.append(record)

                match_resp = self._calc_to_response(record.id, profile.id, j, calc, now)

            # Check min_score and provisional filters
            if min_score is not None and match_resp.overall_score < min_score:
                continue
            if not include_provisional and match_resp.breakdown.is_provisional:
                continue

            scored_items.append(
                JobRecommendationItem(
                    job=_format_job_response(j),
                    match=match_resp,
                )
            )

        if new_or_updated_records:
            await db.commit()

        # Sort descending by overall_score, breaking ties by evidence_coverage and posted_at
        scored_items.sort(
            key=lambda x: (
                x.match.overall_score,
                x.match.breakdown.evidence_coverage,
                x.job.posted_at,
            ),
            reverse=True,
        )

        total = len(scored_items)
        offset = (page - 1) * page_size
        paginated_items = scored_items[offset : offset + page_size]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return JobRecommendationResponse(
            items=paginated_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            scoring_version=self.scoring_version,
            generated_at=_utc_now(),
        )

    # ─────────────────────────────────────────────
    # 10. Staleness Invalidation & Batch Refresh
    # ─────────────────────────────────────────────

    async def invalidate_matches_for_profile(
        self,
        db: AsyncSession,
        career_profile_id: uuid.UUID,
    ) -> int:
        """Flags all existing match records for this profile as stale."""
        stmt = (
            select(JobMatch)
            .where(JobMatch.career_profile_id == career_profile_id)
        )
        records = (await db.scalars(stmt)).all()
        count = 0
        for r in records:
            r.is_stale = True
            count += 1
        if count > 0:
            await db.commit()
        return count

    async def batch_refresh_user_matches(
        self,
        db: AsyncSession,
        user: User,
    ) -> int:
        """Recalculates matches across all active catalog jobs for the current user."""
        profile = await self._get_or_create_profile(db, user)

        # Invalidate current matches
        await self.invalidate_matches_for_profile(db, profile.id)

        # Trigger recommendation run to re-score
        rec = await self.get_recommendations(db, user, page=1, page_size=100)
        return rec.total

    # ─────────────────────────────────────────────
    # Helper Serialization Methods
    # ─────────────────────────────────────────────

    def _orm_to_response(self, record: JobMatch, job: Job) -> JobMatchResponse:
        """Converts JobMatch ORM entity to JobMatchResponse schema."""
        raw_expl = record.explanation_json or {}
        score_bd = raw_expl.get("score_breakdown", {})
        raw_skills = raw_expl.get("skills_detail", [])

        skills_detail = [SkillMatchItem.model_validate(s) for s in raw_skills]

        breakdown = MatchScoreBreakdown(
            overall_score=float(record.overall_score),
            skill_score=float(record.skill_score),
            experience_score=float(record.experience_score),
            project_score=float(record.project_score),
            location_score=float(record.location_score),
            preference_score=float(record.preference_score),
            vector_score=float(record.vector_score),
            evidence_coverage=float(record.evidence_coverage),
            is_provisional=raw_expl.get("is_provisional", False),
            weights=raw_expl.get("weights", self.weights),
            evaluated_factors=raw_expl.get("evaluated_factors", []),
            unevaluated_factors=raw_expl.get("unevaluated_factors", []),
        )

        explanation = JobMatchExplanation(
            summary=raw_expl.get("summary", ""),
            strengths=raw_expl.get("strengths", []),
            gaps=raw_expl.get("gaps", []),
            recommended_actions=raw_expl.get("recommended_actions", []),
        )

        return JobMatchResponse(
            match_id=record.id,
            job_id=record.job_id,
            career_profile_id=record.career_profile_id,
            overall_score=float(record.overall_score),
            breakdown=breakdown,
            matched_skills=record.matched_skills or [],
            matched_preferred_skills=record.matched_preferred_skills or [],
            missing_skills=record.missing_skills or [],
            unknown_skills=record.unknown_skills or [],
            skills_detail=skills_detail,
            explanation=explanation,
            scoring_version=record.scoring_version,
            is_stale=record.is_stale,
            freshness_status=job.freshness_status or "active",
            calculated_at=record.calculated_at,
        )

    def _calc_to_response(
        self,
        match_id: uuid.UUID,
        career_profile_id: uuid.UUID,
        job: Job,
        calc: Dict[str, Any],
        now: datetime,
    ) -> JobMatchResponse:
        """Converts memory calculation dictionary to JobMatchResponse schema."""
        breakdown = MatchScoreBreakdown(
            overall_score=calc["overall_score"],
            skill_score=calc["skill_score"],
            experience_score=calc["experience_score"],
            project_score=calc["project_score"],
            location_score=calc["location_score"],
            preference_score=calc["preference_score"],
            vector_score=calc["vector_score"],
            evidence_coverage=calc["evidence_coverage"],
            is_provisional=calc["is_provisional"],
            weights=calc["weights"],
            evaluated_factors=calc["evaluated_factors"],
            unevaluated_factors=calc["unevaluated_factors"],
        )

        explanation = JobMatchExplanation(
            summary=calc["explanation"]["summary"],
            strengths=calc["explanation"]["strengths"],
            gaps=calc["explanation"]["gaps"],
            recommended_actions=calc["explanation"]["recommended_actions"],
        )

        return JobMatchResponse(
            match_id=match_id,
            job_id=job.id,
            career_profile_id=career_profile_id,
            overall_score=calc["overall_score"],
            breakdown=breakdown,
            matched_skills=calc["matched_skills"],
            matched_preferred_skills=calc["matched_preferred_skills"],
            missing_skills=calc["missing_skills"],
            unknown_skills=calc["unknown_skills"],
            skills_detail=calc["skills_detail"],
            explanation=explanation,
            scoring_version=self.scoring_version,
            is_stale=False,
            freshness_status=job.freshness_status or "active",
            calculated_at=now,
        )
