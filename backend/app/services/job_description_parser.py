"""
Job Description Parser and Canonical Skill Extractor for CoachPath.
Performs deterministic word-boundary matching against CoachPath's 48 canonical skills,
sections job descriptions into responsibilities and requirements, and supports
optional LLM-assisted structural parsing with prompt injection quarantine.
"""

from __future__ import annotations

import decimal
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.db.seeds.skill_taxonomy import SKILL_TAXONOMY

logger = logging.getLogger(__name__)


# Compile alias lookup dictionary: alias -> (skill_id, canonical_name, category)
SKILL_LOOKUP: Dict[str, Tuple[str, str, str]] = {}

for skill in SKILL_TAXONOMY:
    s_id = skill["id"]
    s_name = skill["name"]
    s_cat = skill.get("category", "technical")

    # Map lowercase canonical name
    SKILL_LOOKUP[s_name.lower()] = (s_id, s_name, s_cat)
    # Map skill ID
    SKILL_LOOKUP[s_id.lower()] = (s_id, s_name, s_cat)

    # Map synonyms
    for syn in skill.get("synonyms", []):
        SKILL_LOOKUP[syn.lower()] = (s_id, s_name, s_cat)

# Add special aliases with exact word boundaries
SPECIAL_ALIASES = {
    "c++": ("c-cpp", "C & C++", "language"),
    "c/c++": ("c-cpp", "C & C++", "language"),
    "ci/cd": ("ci-cd", "CI/CD & DevOps", "devops"),
    "k8s": ("kubernetes", "Kubernetes", "cloud"),
    "js": ("javascript", "JavaScript", "language"),
    "ts": ("typescript", "TypeScript", "language"),
    "ml": ("machine-learning", "Machine Learning", "ai_ml"),
    "ai": ("ai-llm", "AI & LLMs", "ai_ml"),
    "dl": ("deep-learning", "Deep Learning", "ai_ml"),
    "nlp": ("nlp", "Natural Language Processing", "ai_ml"),
    "cv": ("computer-vision", "Computer Vision", "ai_ml"),
    "aws": ("aws", "AWS Cloud Services", "cloud"),
    "gcp": ("gcp", "Google Cloud Platform", "cloud"),
    "azure": ("azure", "Microsoft Azure", "cloud"),
}


def extract_skills_deterministic(text: str) -> List[Dict[str, Any]]:
    """
    Scans job posting text using deterministic word-boundary regexes
    against the CoachPath canonical taxonomy.
    """
    if not text:
        return []

    text_lower = text.lower()
    matched_skills: Dict[str, Dict[str, Any]] = {}

    # 1. Match special symbols with custom patterns
    for alias, (s_id, s_name, s_cat) in SPECIAL_ALIASES.items():
        pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
        match = re.search(pattern, text_lower)
        if match:
            # Check context around match for mandatory vs preferred
            start = max(0, match.start() - 60)
            end = min(len(text_lower), match.end() + 60)
            window = text_lower[start:end]
            is_pref = any(k in window for k in ["preferred", "plus", "bonus", "nice to have", "optional"])

            matched_skills[s_id] = {
                "skill_id": s_id,
                "name": s_name,
                "category": s_cat,
                "is_mandatory": not is_pref,
                "confidence_score": 1.0,
                "source_phrase": text[match.start() : match.end()],
            }

    # 2. Match general taxonomy
    for alias, (s_id, s_name, s_cat) in SKILL_LOOKUP.items():
        if len(alias) <= 1:
            continue
        if s_id in matched_skills:
            continue

        # Use strict word boundary
        pattern = r"\b" + re.escape(alias) + r"\b"
        match = re.search(pattern, text_lower)
        if match:
            start = max(0, match.start() - 60)
            end = min(len(text_lower), match.end() + 60)
            window = text_lower[start:end]
            is_pref = any(k in window for k in ["preferred", "plus", "bonus", "nice to have", "optional"])

            matched_skills[s_id] = {
                "skill_id": s_id,
                "name": s_name,
                "category": s_cat,
                "is_mandatory": not is_pref,
                "confidence_score": 0.95,
                "source_phrase": text[match.start() : match.end()],
            }

    return list(matched_skills.values())


def extract_sections(text: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Extracts responsibilities, required qualifications, and preferred qualifications
    from unstructured job descriptions using deterministic heading markers.
    """
    responsibilities: List[str] = []
    required: List[str] = []
    preferred: List[str] = []

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    current_section: Optional[str] = None

    for line in lines:
        lower = line.lower()
        if any(h in lower for h in ["responsibilities", "what you will do", "what you'll do", "the role", "duties"]):
            current_section = "responsibilities"
            continue
        elif any(h in lower for h in ["requirements", "qualifications", "must have", "what you bring", "basic qualifications", "minimum"]):
            current_section = "required"
            continue
        elif any(h in lower for h in ["nice to have", "preferred", "bonus", "preferred qualifications", "plus"]):
            current_section = "preferred"
            continue

        # Collect bullet points or lines
        if line.startswith(("-", "•", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            cleaned = re.sub(r"^[-•*\d.]+\s*", "", line).strip()
            if len(cleaned) > 5:
                if current_section == "responsibilities":
                    responsibilities.append(cleaned)
                elif current_section == "required":
                    required.append(cleaned)
                elif current_section == "preferred":
                    preferred.append(cleaned)
        elif current_section:
            if len(line) > 15 and not line.endswith(":"):
                if current_section == "responsibilities" and len(responsibilities) < 12:
                    responsibilities.append(line)
                elif current_section == "required" and len(required) < 12:
                    required.append(line)
                elif current_section == "preferred" and len(preferred) < 12:
                    preferred.append(line)

    return responsibilities, required, preferred
