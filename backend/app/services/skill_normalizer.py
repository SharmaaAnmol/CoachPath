"""
Skill Normalization Service for CoachPath.
Maps extracted candidate skills against the canonical skills taxonomy in PostgreSQL.
Matches canonical IDs, display names, and industry synonyms.
"""
from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skills import Skill
from app.schemas.resume import NormalizedSkillItem

logger = logging.getLogger(__name__)


def _clean_term(term: str) -> str:
    """Normalizes a raw skill term for fuzzy/exact dictionary matching."""
    t = term.lower().strip()
    # Strip common punctuation wrapping
    t = re.sub(r"^[\s\-_.,/]+|[\s\-_.,/]+$", "", t)
    return t


class SkillNormalizationService:
    """
    Normalizes arbitrary resume-extracted skill strings against the CoachPath
    canonical skill taxonomy seeded in PostgreSQL.
    """

    async def normalize_skills(
        self,
        extracted_skills: List[str],
        db: AsyncSession,
    ) -> Tuple[List[NormalizedSkillItem], List[str]]:
        """
        Maps a list of raw skill strings to canonical taxonomy entries.
        Returns (normalized_skills, raw_unmatched_skills).
        """
        if not extracted_skills:
            return [], []

        # 1. Fetch master skills from taxonomy table
        stmt = select(Skill)
        all_skills = (await db.scalars(stmt)).all()

        # Build lookup indexes
        id_map: Dict[str, Skill] = {}
        name_map: Dict[str, Skill] = {}
        synonym_map: Dict[str, Skill] = {}

        for skill in all_skills:
            id_map[_clean_term(skill.id)] = skill
            name_map[_clean_term(skill.name)] = skill
            for syn in (skill.synonyms or []):
                synonym_map[_clean_term(syn)] = skill

        normalized_items: List[NormalizedSkillItem] = []
        seen_skill_ids: Set[str] = set()
        unmatched_skills: List[str] = []

        for raw in extracted_skills:
            clean = _clean_term(raw)
            if not clean:
                continue

            matched_skill: Optional[Skill] = None

            # Priority 1: Match canonical ID
            if clean in id_map:
                matched_skill = id_map[clean]
            # Priority 2: Match canonical Name
            elif clean in name_map:
                matched_skill = name_map[clean]
            # Priority 3: Match Synonyms
            elif clean in synonym_map:
                matched_skill = synonym_map[clean]

            if matched_skill:
                if matched_skill.id not in seen_skill_ids:
                    seen_skill_ids.add(matched_skill.id)
                    normalized_items.append(
                        NormalizedSkillItem(
                            skill_id=matched_skill.id,
                            name=matched_skill.name,
                            category=matched_skill.category,
                            raw_matched=raw,
                        )
                    )
            else:
                if raw not in unmatched_skills:
                    unmatched_skills.append(raw)

        logger.debug(
            "Skill normalization: %d raw terms -> %d canonical, %d unmatched",
            len(extracted_skills),
            len(normalized_items),
            len(unmatched_skills),
        )
        return normalized_items, unmatched_skills


# Singleton normalizer service
skill_normalizer = SkillNormalizationService()
