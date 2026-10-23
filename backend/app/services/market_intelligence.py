"""
Market Intelligence Aggregation Engine for CoachPath.
Computes real-time market metrics, canonical skill demand distributions,
workplace flexibility breakdown, and salary benchmarks directly from verified job postings.
"""

from __future__ import annotations

from datetime import datetime, timezone
import statistics
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.jobs import Job, JobSkill
from app.models.skills import Skill
from app.schemas.jobs import (
    MarketIntelligenceResponse,
    SalaryInsights,
    TopSkillDemand,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MarketIntelligenceService:
    """Service generating aggregated market intelligence indicators."""

    async def get_market_overview(
        self,
        db: AsyncSession,
        role_id_filter: Optional[str] = None,
    ) -> MarketIntelligenceResponse:
        """
        Computes aggregate metrics across active catalog postings.
        Can optionally be filtered by a specific canonical role.
        """
        # Base filter for active, fresh jobs
        base_criteria = [
            Job.is_active == True,
            Job.freshness_status.in_(["active", "needs_refresh"]),
        ]
        if role_id_filter:
            base_criteria.append(Job.role_id == role_id_filter)

        # 1. Total active jobs
        total_stmt = select(func.count(Job.id)).where(*base_criteria)
        total_active_jobs: int = (await db.scalar(total_stmt)) or 0

        # 2. Role distribution
        role_stmt = (
            select(Job.role_id, func.count(Job.id))
            .where(*base_criteria)
            .group_by(Job.role_id)
        )
        role_rows = (await db.execute(role_stmt)).all()
        role_distribution: Dict[str, int] = {r[0]: r[1] for r in role_rows if r[0]}

        # 3. Remote type distribution
        remote_stmt = (
            select(Job.remote_type, func.count(Job.id))
            .where(*base_criteria)
            .group_by(Job.remote_type)
        )
        remote_rows = (await db.execute(remote_stmt)).all()
        remote_distribution: Dict[str, int] = {r[0]: r[1] for r in remote_rows if r[0]}

        # 4. Experience distribution
        exp_stmt = (
            select(Job.experience_level, func.count(Job.id))
            .where(*base_criteria)
            .group_by(Job.experience_level)
        )
        exp_rows = (await db.execute(exp_stmt)).all()
        experience_distribution: Dict[str, int] = {r[0]: r[1] for r in exp_rows if r[0]}

        # 5. Top demanded skills
        skill_stmt = (
            select(
                JobSkill.skill_id,
                Skill.name,
                Skill.category,
                func.count(JobSkill.job_id).label("skill_count"),
            )
            .join(Job, JobSkill.job_id == Job.id)
            .join(Skill, JobSkill.skill_id == Skill.id)
            .where(*base_criteria)
            .group_by(JobSkill.skill_id, Skill.name, Skill.category)
            .order_by(func.count(JobSkill.job_id).desc())
            .limit(20)
        )
        skill_rows = (await db.execute(skill_stmt)).all()

        top_skills: List[TopSkillDemand] = []
        for s_id, s_name, s_cat, count in skill_rows:
            pct = round((count / total_active_jobs * 100.0), 1) if total_active_jobs > 0 else 0.0
            top_skills.append(
                TopSkillDemand(
                    skill_id=s_id,
                    name=s_name,
                    category=s_cat,
                    job_count=count,
                    percentage=pct,
                )
            )

        # 6. Salary insights
        salary_stmt = (
            select(Job.min_salary, Job.max_salary)
            .where(
                *base_criteria,
                Job.min_salary.isnot(None),
                Job.max_salary.isnot(None),
            )
        )
        salary_rows = (await db.execute(salary_stmt)).all()

        salary_sample_size = len(salary_rows)
        avg_min: Optional[int] = None
        avg_max: Optional[int] = None
        median_salary: Optional[int] = None

        if salary_sample_size > 0:
            mins = [r[0] for r in salary_rows if r[0]]
            maxs = [r[1] for r in salary_rows if r[1]]
            midpoints = [int((r[0] + r[1]) / 2) for r in salary_rows if r[0] and r[1]]

            if mins:
                avg_min = int(sum(mins) / len(mins))
            if maxs:
                avg_max = int(sum(maxs) / len(maxs))
            if midpoints:
                median_salary = int(statistics.median(midpoints))

        salary_insights = SalaryInsights(
            sample_size=salary_sample_size,
            average_min_salary=avg_min,
            average_max_salary=avg_max,
            median_salary=median_salary,
            currency="USD",
        )

        # 7. Provisional sample indicator
        is_provisional = total_active_jobs < 20
        provisional_reason = (
            f"Catalog sample size ({total_active_jobs} jobs) is currently developing. "
            "Aggregates represent initial market indicators."
            if is_provisional
            else None
        )

        return MarketIntelligenceResponse(
            total_active_jobs=total_active_jobs,
            role_distribution=role_distribution,
            remote_distribution=remote_distribution,
            experience_distribution=experience_distribution,
            top_demanded_skills=top_skills,
            salary_insights=salary_insights,
            is_provisional=is_provisional,
            provisional_reason=provisional_reason,
            generated_at=_utc_now(),
        )
