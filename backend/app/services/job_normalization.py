"""
Job Normalization and Data Quality Engine for CoachPath.
Cleans raw posting content, classifies canonical benchmark roles,
standardizes workplace flexibility and seniority levels, and computes
deduplication hashes and data completeness scores.
"""

from __future__ import annotations

import decimal
import hashlib
import re
from typing import Any, Dict, Optional, Tuple

CANONICAL_ROLE_KEYWORDS = {
    "backend-developer": [
        "backend", "back-end", "server-side", "api engineer", "fastapi", "django",
        "spring boot", "golang backend", "distributed systems", "database engineer",
    ],
    "frontend-developer": [
        "frontend", "front-end", "react", "next.js", "vue", "angular",
        "ui engineer", "web developer", "client-side", "javascript engineer",
    ],
    "fullstack-developer": [
        "full stack", "fullstack", "full-stack", "mern", "web engineer",
    ],
    "machine-learning-engineer": [
        "machine learning", "ml engineer", "mle", "computer vision",
        "deep learning", "nlp engineer", "model deployment", "pytorch",
    ],
    "ai-engineer": [
        "ai engineer", "artificial intelligence", "llm engineer", "generative ai",
        "genai", "prompt engineer", "rag", "langchain",
    ],
    "data-scientist": [
        "data scientist", "data science", "statistical model", "predictive analytics",
    ],
    "data-analyst": [
        "data analyst", "business intelligence", "bi analyst", "tableau", "power bi", "sql analyst",
    ],
    "devops-cloud-engineer": [
        "devops", "cloud engineer", "site reliability", "sre", "infrastructure engineer",
        "kubernetes", "aws engineer", "terraform", "platform engineer",
    ],
    "software-engineer": [
        "software engineer", "swe", "software developer", "programmer", "systems engineer",
    ],
}

EXPERIENCE_KEYWORDS = {
    "internship": ["intern", "internship", "co-op", "trainee", "student"],
    "entry_level": ["entry level", "entry-level", "graduate", "new grad", "associate", "junior 0-1", "0-2 years", "no experience required"],
    "junior": ["junior", "jr", "jr.", "1-3 years", "1 to 3 years", "early career"],
    "mid": ["mid level", "mid-level", "intermediate", "3-5 years", "3 to 5 years", "experienced"],
}


def clean_html(text: str) -> str:
    """Converts HTML markup into readable markdown/plain text."""
    if not text:
        return ""
    # Replace common HTML breaks with newlines
    text = re.sub(r"<(?:br|/p|/div|/li)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li>", "• ", text, flags=re.IGNORECASE)
    # Strip remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Unescape HTML entities
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&nbsp;", " ")
    )
    # Normalize multiple blank lines
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def normalize_string(val: Optional[str]) -> str:
    """Lowercases, trims, and collapses multiple whitespace characters."""
    if not val:
        return ""
    return re.sub(r"\s+", " ", val.lower().strip())


def normalize_company_name(name: str) -> str:
    """Strips punctuation and corporate suffixes for normalized matching."""
    norm = normalize_string(name)
    norm = re.sub(r"[^\w\s]", "", norm)
    norm = re.sub(r"\b(inc|llc|ltd|corp|corporation|technologies|gmbh|co)\b", "", norm)
    return re.sub(r"\s+", " ", norm).strip()


def classify_canonical_role(title: str, description: str = "", hint_role: Optional[str] = None) -> str:
    """
    Classifies a job into one of the 9 benchmark CoachPath roles.
    Uses title priority, followed by description density, falling back to 'software-engineer'.
    """
    if hint_role and hint_role in CANONICAL_ROLE_KEYWORDS:
        return hint_role

    combined_text = normalize_string(f"{title} {description[:600]}")
    title_lower = normalize_string(title)

    # 1. Title direct match
    for role_id, keywords in CANONICAL_ROLE_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", title_lower):
                return role_id

    # 2. Combined text match
    for role_id, keywords in CANONICAL_ROLE_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
                return role_id

    return "software-engineer"


def classify_remote_type(location: str, description: str = "", hint_remote: Optional[str] = None) -> str:
    """Normalizes workplace flexibility to 'remote', 'hybrid', or 'onsite'."""
    if hint_remote in ("remote", "hybrid", "onsite"):
        return hint_remote

    loc_norm = normalize_string(location)
    desc_sample = normalize_string(description[:500])

    if "remote" in loc_norm or "remote" in desc_sample:
        if "hybrid" in loc_norm or "hybrid" in desc_sample:
            return "hybrid"
        return "remote"
    if "hybrid" in loc_norm or "hybrid" in desc_sample:
        return "hybrid"
    return "onsite"


def classify_experience_level(title: str, description: str = "", hint_level: Optional[str] = None) -> str:
    """Normalizes seniority level into CoachPath tiers."""
    if hint_level in ("internship", "entry_level", "junior", "mid"):
        return hint_level

    title_norm = normalize_string(title)
    if any(k in title_norm for k in ["intern", "co-op", "trainee", "student"]):
        return "internship"
    if any(k in title_norm for k in ["junior", "jr", "jr."]):
        return "junior"
    if any(k in title_norm for k in ["entry level", "entry-level", "associate", "graduate", "new grad"]):
        return "entry_level"
    if any(k in title_norm for k in ["mid level", "mid-level", "intermediate", "software engineer ii", "swe ii"]):
        return "mid"

    combined = normalize_string(f"{title} {description[:800]}")

    for level, kws in EXPERIENCE_KEYWORDS.items():
        for kw in kws:
            if re.search(r"\b" + re.escape(kw) + r"\b", combined):
                return level

    # Check years of experience numbers
    years_match = re.search(r"(\d+)\+?\s*(?:to|-)\s*(\d+)?\s*years?", combined)
    if years_match:
        min_years = int(years_match.group(1))
        if min_years == 0:
            return "entry_level"
        elif min_years <= 2:
            return "junior"
        else:
            return "mid"

    return "entry_level"


def parse_salary_range(
    min_sal: Optional[int],
    max_sal: Optional[int],
    text: str = "",
) -> Tuple[Optional[int], Optional[int]]:
    """Validates or extracts annualized salaries."""
    if min_sal and min_sal > 0:
        if max_sal and max_sal < min_sal:
            min_sal, max_sal = max_sal, min_sal
        return min_sal, max_sal

    # Search for $XX,XXX - $YY,YYY in description
    salary_match = re.search(r"\$(\d{2,3}),?(\d{3})\s*(?:-|to)\s*\$?(\d{2,3}),?(\d{3})", text)
    if salary_match:
        low = int(salary_match.group(1) + salary_match.group(2))
        high = int(salary_match.group(3) + salary_match.group(4))
        return low, high

    return None, None


def compute_deduplication_hash(company_name: str, title: str, location: str) -> str:
    """Generates a reproducible SHA-256 fingerprint for identity matching."""
    norm_comp = normalize_company_name(company_name)
    norm_title = normalize_string(title)
    norm_loc = normalize_string(location)
    key = f"{norm_comp}|{norm_title}|{norm_loc}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def compute_data_quality_score(
    title: str,
    description: str,
    company: str,
    location: str,
    skill_count: int,
    has_salary: bool,
) -> decimal.Decimal:
    """
    Computes a deterministic quality score from 0.00 to 1.00 based on posting completeness.
    """
    score = decimal.Decimal("0.00")
    if len(title.strip()) >= 5:
        score += decimal.Decimal("0.20")
    if len(description.strip()) >= 100:
        score += decimal.Decimal("0.30")
    elif len(description.strip()) >= 40:
        score += decimal.Decimal("0.15")

    if len(company.strip()) >= 2:
        score += decimal.Decimal("0.15")
    if len(location.strip()) >= 2:
        score += decimal.Decimal("0.10")

    if skill_count >= 5:
        score += decimal.Decimal("0.15")
    elif skill_count >= 1:
        score += decimal.Decimal("0.10")

    if has_salary:
        score += decimal.Decimal("0.10")

    return min(decimal.Decimal("1.00"), score)
