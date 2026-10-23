"""
Gap Analysis Engine Database Seeder for CoachPath.
Idempotently seeds the master canonical skill taxonomy, 7 benchmark target roles,
and their respective role requirements.
"""

from __future__ import annotations

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.role_catalog import ROLE_CATALOG
from app.db.seeds.skill_taxonomy import SKILL_TAXONOMY
from app.models.career import Role
from app.models.skills import RoleRequirement, Skill

logger = logging.getLogger(__name__)


async def seed_skill_taxonomy_and_roles(db: AsyncSession) -> None:
    """
    Idempotently seeds canonical skills and benchmark target roles.
    Never duplicates records or destroys existing relations.
    """
    # 1. Seed Canonical Skills
    skills_created = 0
    skills_updated = 0
    for s_data in SKILL_TAXONOMY:
        stmt = select(Skill).where(Skill.id == s_data["id"])
        existing_skill = await db.scalar(stmt)
        if not existing_skill:
            skill = Skill(
                id=s_data["id"],
                name=s_data["name"],
                category=s_data["category"],
                description=s_data["description"],
                synonyms=s_data.get("synonyms", []),
            )
            db.add(skill)
            skills_created += 1
        else:
            # Update metadata if needed
            existing_skill.name = s_data["name"]
            existing_skill.category = s_data["category"]
            existing_skill.description = s_data["description"]
            existing_skill.synonyms = s_data.get("synonyms", [])
            skills_updated += 1

    await db.flush()

    # 2. Seed Roles and Role Requirements
    roles_created = 0
    roles_updated = 0
    requirements_synced = 0

    for r_data in ROLE_CATALOG:
        stmt = select(Role).where(Role.id == r_data["id"])
        existing_role = await db.scalar(stmt)

        if not existing_role:
            role = Role(
                id=r_data["id"],
                title=r_data["title"],
                category=r_data["category"],
                description=r_data["description"],
                version=r_data.get("version", "1.0.0"),
                source=r_data.get("source", "curated_baseline"),
                is_complete=True,
            )
            db.add(role)
            roles_created += 1
        else:
            existing_role.title = r_data["title"]
            existing_role.category = r_data["category"]
            existing_role.description = r_data["description"]
            existing_role.version = r_data.get("version", "1.0.0")
            existing_role.source = r_data.get("source", "curated_baseline")
            existing_role.is_complete = True
            roles_updated += 1

        await db.flush()

        # Sync role requirements
        # Fetch current requirements for this role
        req_stmt = select(RoleRequirement).where(RoleRequirement.role_id == r_data["id"])
        existing_reqs = {r.skill_id: r for r in (await db.scalars(req_stmt)).all()}

        for req_data in r_data.get("requirements", []):
            skill_id = req_data["skill_id"]
            if skill_id in existing_reqs:
                # Update existing requirement
                curr_req = existing_reqs[skill_id]
                curr_req.importance = req_data["importance"]
                curr_req.min_proficiency = req_data["min_proficiency"]
                curr_req.required_level = req_data["required_level"]
                curr_req.weight = req_data["weight"]
                curr_req.rationale = req_data.get("rationale")
            else:
                # Add new requirement
                new_req = RoleRequirement(
                    role_id=r_data["id"],
                    skill_id=skill_id,
                    importance=req_data["importance"],
                    min_proficiency=req_data["min_proficiency"],
                    required_level=req_data["required_level"],
                    weight=req_data["weight"],
                    rationale=req_data.get("rationale"),
                )
                db.add(new_req)
            requirements_synced += 1

    await db.commit()
    logger.info(
        f"Skill taxonomy & roles seeded successfully: "
        f"{skills_created} skills created, {skills_updated} updated | "
        f"{roles_created} roles created, {roles_updated} updated | "
        f"{requirements_synced} requirements synced."
    )
