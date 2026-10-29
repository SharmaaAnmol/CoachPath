"""
Role Resolution, Normalization, and Canonical Catalog Registry for CoachPath.
Ensures strict role personalization: validates target roles against canonical benchmark
definitions, normalizes historical and user-facing aliases, and prevents silent fallbacks.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set

from app.core.exceptions import ValidationException

# Canonical 11 CoachPath Benchmark Target Roles
CANONICAL_ROLE_IDS: Set[str] = {
    "backend-developer",
    "frontend-developer",
    "fullstack-developer",
    "devops-cloud-engineer",
    "data-scientist",
    "data-analyst",
    "data-engineer",
    "machine-learning-engineer",
    "ai-engineer",
    "mobile-engineer",
    "software-engineer",
}

# Mapping of common aliases, variations, and human-readable titles to canonical role IDs
ROLE_ALIASES: Dict[str, str] = {
    # Full-Stack Developer
    "fullstack-developer": "fullstack-developer",
    "fullstack": "fullstack-developer",
    "full-stack": "fullstack-developer",
    "full stack": "fullstack-developer",
    "full-stack developer": "fullstack-developer",
    "full stack developer": "fullstack-developer",
    "full-stack engineer": "fullstack-developer",
    "full stack engineer": "fullstack-developer",
    "mern developer": "fullstack-developer",
    "mean developer": "fullstack-developer",
    "web developer": "fullstack-developer",

    # Frontend Developer
    "frontend-developer": "frontend-developer",
    "frontend": "frontend-developer",
    "front-end": "frontend-developer",
    "frontend developer": "frontend-developer",
    "front-end developer": "frontend-developer",
    "frontend engineer": "frontend-developer",
    "front-end engineer": "frontend-developer",
    "ui engineer": "frontend-developer",
    "client engineer": "frontend-developer",

    # Backend Developer
    "backend-developer": "backend-developer",
    "backend": "backend-developer",
    "back-end": "backend-developer",
    "backend developer": "backend-developer",
    "back-end developer": "backend-developer",
    "backend engineer": "backend-developer",
    "back-end engineer": "backend-developer",
    "server engineer": "backend-developer",
    "api engineer": "backend-developer",

    # DevOps & Cloud Engineer
    "devops-cloud-engineer": "devops-cloud-engineer",
    "devops": "devops-cloud-engineer",
    "devops engineer": "devops-cloud-engineer",
    "devops / cloud engineer": "devops-cloud-engineer",
    "devops / platform engineer": "devops-cloud-engineer",
    "cloud engineer": "devops-cloud-engineer",
    "platform engineer": "devops-cloud-engineer",
    "site reliability engineer": "devops-cloud-engineer",
    "sre": "devops-cloud-engineer",
    "infrastructure engineer": "devops-cloud-engineer",

    # Data Engineer
    "data-engineer": "data-engineer",
    "data engineer": "data-engineer",
    "data engineering": "data-engineer",
    "etl engineer": "data-engineer",
    "data pipeline engineer": "data-engineer",
    "analytics engineer": "data-engineer",
    "data platform engineer": "data-engineer",
    "big data engineer": "data-engineer",

    # Data Scientist
    "data-scientist": "data-scientist",
    "data scientist": "data-scientist",
    "data science": "data-scientist",
    "applied data scientist": "data-scientist",

    # Data Analyst
    "data-analyst": "data-analyst",
    "data analyst": "data-analyst",
    "bi analyst": "data-analyst",
    "business intelligence analyst": "data-analyst",
    "analytics analyst": "data-analyst",

    # Machine Learning Engineer
    "machine-learning-engineer": "machine-learning-engineer",
    "machine learning engineer": "machine-learning-engineer",
    "ml engineer": "machine-learning-engineer",
    "mle": "machine-learning-engineer",
    "deep learning engineer": "machine-learning-engineer",

    # AI Engineer
    "ai-engineer": "ai-engineer",
    "ai engineer": "ai-engineer",
    "artificial intelligence engineer": "ai-engineer",
    "llm engineer": "ai-engineer",
    "generative ai engineer": "ai-engineer",
    "genai engineer": "ai-engineer",

    # Mobile Engineer
    "mobile-engineer": "mobile-engineer",
    "mobile engineer": "mobile-engineer",
    "mobile developer": "mobile-engineer",
    "android developer": "mobile-engineer",
    "android engineer": "mobile-engineer",
    "ios developer": "mobile-engineer",
    "ios engineer": "mobile-engineer",
    "react native developer": "mobile-engineer",
    "react native engineer": "mobile-engineer",
    "flutter developer": "mobile-engineer",
    "flutter engineer": "mobile-engineer",
    "ios/android engineer": "mobile-engineer",

    # Software Engineer
    "software-engineer": "software-engineer",
    "software engineer": "software-engineer",
    "software developer": "software-engineer",
    "swe": "software-engineer",
    "systems engineer": "software-engineer",
    "general software engineer": "software-engineer",
}


def normalize_role_identifier(raw_role: Optional[str]) -> Optional[str]:
    """
    Normalizes a role input (slug, title, or alias) to its canonical benchmark role ID.
    Returns the canonical role ID if recognized, or None if unrecognized/empty.
    """
    if not raw_role or not isinstance(raw_role, str):
        return None

    cleaned = raw_role.strip().lower()
    if not cleaned:
        return None

    # 1. Direct canonical match
    if cleaned in CANONICAL_ROLE_IDS:
        return cleaned

    # 2. Replaced underscores with hyphens
    hyphenated = cleaned.replace("_", "-")
    if hyphenated in CANONICAL_ROLE_IDS:
        return hyphenated

    # 3. Direct alias match
    if cleaned in ROLE_ALIASES:
        return ROLE_ALIASES[cleaned]

    if hyphenated in ROLE_ALIASES:
        return ROLE_ALIASES[hyphenated]

    # 4. Normalized whitespace & punctuation
    sanitized = re.sub(r"\s+", " ", re.sub(r"[^\w\s-]", "", cleaned)).strip()
    if sanitized in ROLE_ALIASES:
        return ROLE_ALIASES[sanitized]

    return None


def validate_and_resolve_role_id(
    raw_role: Optional[str],
    field_name: str = "target_role",
) -> str:
    """
    Validates and resolves a target role into a canonical benchmark role ID.
    Raises ValidationException if missing or unsupported. Never silently defaults.
    """
    if not raw_role or not str(raw_role).strip():
        raise ValidationException(
            f"No {field_name} specified. A target role must be explicitly provided or configured in your profile."
        )

    resolved = normalize_role_identifier(raw_role)
    if not resolved or resolved not in CANONICAL_ROLE_IDS:
        supported = ", ".join(sorted(CANONICAL_ROLE_IDS))
        raise ValidationException(
            f"The role '{raw_role}' is not currently supported. Supported benchmark roles are: {supported}."
        )

    return resolved


def get_supported_role_ids() -> List[str]:
    """Returns a sorted list of all supported canonical role IDs."""
    return sorted(CANONICAL_ROLE_IDS)
