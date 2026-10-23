"""
Assessment to Canonical Skill Mapping Service.
Bridges objective diagnostic assessment questions, topic mastery, and assessment IDs
to canonical skill taxonomy IDs and benchmark competencies.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

# Stable namespace used in assessment_seeder
COACHPATH_DNS_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "coachpath.dev")

# Mapping from canonical skill ID to primary diagnostic assessment domain
SKILL_TO_ASSESSMENT_MAP: Dict[str, Dict[str, Any]] = {
    "python": {
        "assessment_skill_id": "python",
        "title": "Python Programming Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "javascript": {
        "assessment_skill_id": "javascript-typescript",
        "title": "JavaScript & TypeScript Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "typescript": {
        "assessment_skill_id": "javascript-typescript",
        "title": "JavaScript & TypeScript Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "javascript-typescript": {
        "assessment_skill_id": "javascript-typescript",
        "title": "JavaScript & TypeScript Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "java": {
        "assessment_skill_id": "java",
        "title": "Java Programming Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "c-cpp": {
        "assessment_skill_id": "c-cpp",
        "title": "C & C++ Systems Programming Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "sql-databases": {
        "assessment_skill_id": "sql-databases",
        "title": "SQL & Relational Databases Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "sql": {
        "assessment_skill_id": "sql-databases",
        "title": "SQL & Relational Databases Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "postgresql": {
        "assessment_skill_id": "sql-databases",
        "title": "SQL & Relational Databases Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "dsa": {
        "assessment_skill_id": "dsa",
        "title": "Data Structures & Algorithms Diagnostic",
        "estimated_minutes": 45,
        "question_count": 30,
    },
    "web-development": {
        "assessment_skill_id": "web-development",
        "title": "Full-Stack Web Development Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "react": {
        "assessment_skill_id": "web-development",
        "title": "Full-Stack Web Development Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "rest-apis": {
        "assessment_skill_id": "web-development",
        "title": "Full-Stack Web Development Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "machine-learning": {
        "assessment_skill_id": "machine-learning",
        "title": "Machine Learning Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "deep-learning": {
        "assessment_skill_id": "machine-learning",
        "title": "Machine Learning Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "pytorch": {
        "assessment_skill_id": "machine-learning",
        "title": "Machine Learning Diagnostic",
        "estimated_minutes": 40,
        "question_count": 30,
    },
    "ai-llm": {
        "assessment_skill_id": "ai-llm",
        "title": "Artificial Intelligence & LLMs Diagnostic",
        "estimated_minutes": 45,
        "question_count": 30,
    },
    "rag": {
        "assessment_skill_id": "ai-llm",
        "title": "Artificial Intelligence & LLMs Diagnostic",
        "estimated_minutes": 45,
        "question_count": 30,
    },
    "nlp": {
        "assessment_skill_id": "ai-llm",
        "title": "Artificial Intelligence & LLMs Diagnostic",
        "estimated_minutes": 45,
        "question_count": 30,
    },
}


def get_assessment_id_for_skill(skill_id: str) -> Optional[uuid.UUID]:
    """Returns stable deterministic Assessment UUID for a canonical skill, if one exists."""
    info = SKILL_TO_ASSESSMENT_MAP.get(skill_id)
    if not info:
        return None
    return uuid.uuid5(COACHPATH_DNS_NAMESPACE, f"assessment.{info['assessment_skill_id']}")


def get_recommended_assessment_for_skill(skill_id: str, reason: str = "") -> Optional[Dict[str, Any]]:
    """Generates recommendation metadata for a skill with an available diagnostic assessment."""
    info = SKILL_TO_ASSESSMENT_MAP.get(skill_id)
    if not info:
        return None
    asmt_id = uuid.uuid5(COACHPATH_DNS_NAMESPACE, f"assessment.{info['assessment_skill_id']}")
    return {
        "assessment_id": str(asmt_id),
        "title": info["title"],
        "skill_id": skill_id,
        "reason": reason or f"Take the {info['title']} to verify your competency in {skill_id}.",
        "estimated_minutes": info["estimated_minutes"],
        "question_count": info["question_count"],
    }
