"""
Remediation Step 2 Test Suite: Target Role Personalization Reconciler.
Validates:
1. Canonical role catalog extension: data-engineer and mobile-engineer
2. Existing supported role definitions resolve correctly
3. Deterministic skill-gap analysis for Data Engineer and Mobile Engineer with distinct competencies
4. Role-relevant recommendations without Backend Developer fallback
5. Strict rejection of unsupported roles with 422 validation errors and supported role listings
6. Missing target role handling without silent fallback
7. Supported human-readable aliases normalize to canonical identifiers
8. Onboarding and profile updates preserve intended role
9. Learning-roadmap generation integration for new and existing roles
10. Switching roles triggers recalculation without reusing stale snapshots
11. Multi-tenant isolation and ownership checks
"""

from __future__ import annotations

import decimal
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.assessment_seeder import seed_diagnostic_assessments
from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.auth import User
from app.models.career import CareerProfile, Role
from app.models.skills import RoleRequirement, Skill, SkillGapAnalysis
from app.services.role_resolution import (
    CANONICAL_ROLE_IDS,
    ROLE_ALIASES,
    normalize_role_identifier,
    validate_and_resolve_role_id,
)


# ─── Helpers ─────────────────────────────────────────────────────────

async def register_and_login(client: AsyncClient, email: str, full_name: str) -> tuple[str, uuid.UUID]:
    pw = "SecurePassword123!"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": full_name},
    )
    assert r.status_code == 201, r.text
    user_id = uuid.UUID(r.json()["user_id"])

    r2 = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert r2.status_code == 200, r2.text
    return r2.json()["access_token"], user_id


# ─── 1. Canonical Role Definitions & Catalog Checks ───────────────────

@pytest.mark.asyncio
async def test_canonical_catalog_contains_all_11_roles(test_session: AsyncSession):
    """Verifies all 11 canonical benchmark roles are seeded and queryable."""
    await seed_skill_taxonomy_and_roles(test_session)
    stmt = select(Role)
    roles = (await test_session.scalars(stmt)).all()
    role_ids = {r.id for r in roles}

    expected_roles = {
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
    assert expected_roles.issubset(role_ids), f"Missing roles: {expected_roles - role_ids}"


@pytest.mark.asyncio
async def test_data_engineer_role_definition(test_session: AsyncSession):
    """Verifies data-engineer benchmark requirements and competencies."""
    await seed_skill_taxonomy_and_roles(test_session)
    stmt = select(Role).where(Role.id == "data-engineer")
    role = await test_session.scalar(stmt)
    assert role is not None
    assert role.title == "Data Engineer"
    assert role.category == "data"
    assert role.is_complete is True

    req_stmt = select(RoleRequirement).where(RoleRequirement.role_id == "data-engineer")
    reqs = (await test_session.scalars(req_stmt)).all()
    skill_ids = {r.skill_id for r in reqs}

    # Core data engineering skills must be present
    assert "sql-databases" in skill_ids
    assert "python" in skill_ids
    assert "data-modeling" in skill_ids
    assert "etl-pipelines" in skill_ids
    assert "data-warehousing" in skill_ids
    assert "stream-processing" in skill_ids
    # Backend-only frameworks must NOT be mandatory in data engineering
    assert "fastapi" not in skill_ids


@pytest.mark.asyncio
async def test_mobile_engineer_role_definition(test_session: AsyncSession):
    """Verifies mobile-engineer benchmark requirements and competencies."""
    await seed_skill_taxonomy_and_roles(test_session)
    stmt = select(Role).where(Role.id == "mobile-engineer")
    role = await test_session.scalar(stmt)
    assert role is not None
    assert role.title == "Mobile Engineer"
    assert role.category == "engineering"
    assert role.is_complete is True

    req_stmt = select(RoleRequirement).where(RoleRequirement.role_id == "mobile-engineer")
    reqs = (await test_session.scalars(req_stmt)).all()
    skill_ids = {r.skill_id for r in reqs}

    # Core mobile engineering skills must be present
    assert "mobile-architecture" in skill_ids
    assert "rest-apis" in skill_ids
    assert "dsa" in skill_ids
    assert "kotlin" in skill_ids
    assert "swift" in skill_ids
    assert "react-native" in skill_ids
    assert "flutter" in skill_ids
    # Relational database modeling must NOT be core requirement for mobile
    assert "sql-databases" not in skill_ids


# ─── 2. Alias Normalization & Strict Role Validation ──────────────────

def test_alias_normalization():
    """Verifies that human-readable titles and aliases normalize to canonical slugs."""
    test_cases = [
        ("Data Engineer", "data-engineer"),
        ("data engineering", "data-engineer"),
        ("ETL Engineer", "data-engineer"),
        ("Mobile Engineer", "mobile-engineer"),
        ("Mobile Developer", "mobile-engineer"),
        ("iOS Developer", "mobile-engineer"),
        ("Android Engineer", "mobile-engineer"),
        ("React Native Developer", "mobile-engineer"),
        ("Flutter Engineer", "mobile-engineer"),
        ("Backend Engineer", "backend-developer"),
        ("Full-Stack Engineer", "fullstack-developer"),
        ("DevOps / Cloud Engineer", "devops-cloud-engineer"),
        ("Machine Learning Engineer", "machine-learning-engineer"),
        ("AI Engineer", "ai-engineer"),
        ("Data Scientist", "data-scientist"),
        ("Data Analyst", "data-analyst"),
        ("Software Engineer", "software-engineer"),
    ]
    for raw, expected in test_cases:
        assert normalize_role_identifier(raw) == expected, f"Failed for {raw}"


def test_unsupported_role_validation_raises():
    """Verifies that unrecognized roles strictly raise ValidationException with supported roles list."""
    from app.core.exceptions import ValidationException

    unsupported_roles = [
        "blockchain-developer",
        "quantum-computing-specialist",
        "game-designer",
        "Astronaut",
        "invalid-random-string",
    ]
    for bad_role in unsupported_roles:
        with pytest.raises(ValidationException) as exc_info:
            validate_and_resolve_role_id(bad_role)
        assert "not currently supported" in exc_info.value.message
        assert "data-engineer" in exc_info.value.message
        assert "mobile-engineer" in exc_info.value.message


def test_missing_role_validation_raises():
    """Verifies that empty or None role inputs raise ValidationException without fallback."""
    from app.core.exceptions import ValidationException

    for empty_val in [None, "", "   "]:
        with pytest.raises(ValidationException) as exc_info:
            validate_and_resolve_role_id(empty_val)
        assert "No target_role specified" in exc_info.value.message


# ─── 3. Skill-Gap Analysis: Data Engineer vs Mobile Engineer ─────────

@pytest.mark.asyncio
async def test_data_engineer_skill_gap_analysis(client: AsyncClient, test_session: AsyncSession):
    """Verifies gap analysis for Data Engineer returns data-pipeline competencies."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, _ = await register_and_login(client, "de_candidate@example.com", "Priya Sharma")
    headers = {"Authorization": f"Bearer {token}"}

    # Set profile to Data Engineer
    r = await client.put(
        "/api/v1/profile/career-goals",
        headers=headers,
        json={"primary_role_id": "data-engineer", "career_stage": "early_career", "work_preference": "remote"},
    )
    assert r.status_code == 200
    assert r.json()["primary_role"]["id"] == "data-engineer"

    # Execute gap analysis
    res = await client.post(
        "/api/v1/skills/gap-analysis",
        headers=headers,
        json={"role_id": "data-engineer"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["role_id"] == "data-engineer"
    assert data["role_title"] == "Data Engineer"

    # Must contain data engineering skills in details
    details = data["skill_details"]
    assert "etl-pipelines" in details
    assert "data-modeling" in details
    assert "data-warehousing" in details
    assert "sql-databases" in details

    # Must NOT contain backend-specific frameworks
    assert "fastapi" not in details
    assert "django" not in details


@pytest.mark.asyncio
async def test_mobile_engineer_skill_gap_analysis(client: AsyncClient, test_session: AsyncSession):
    """Verifies gap analysis for Mobile Engineer returns mobile architecture & frameworks."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, _ = await register_and_login(client, "mobile_candidate@example.com", "Rohan Joshi")
    headers = {"Authorization": f"Bearer {token}"}

    # Set profile to Mobile Engineer
    r = await client.put(
        "/api/v1/profile/career-goals",
        headers=headers,
        json={"primary_role_id": "mobile-engineer", "career_stage": "early_career", "work_preference": "hybrid"},
    )
    assert r.status_code == 200
    assert r.json()["primary_role"]["id"] == "mobile-engineer"

    # Execute gap analysis using alias
    res = await client.post(
        "/api/v1/skills/gap-analysis",
        headers=headers,
        json={"role_id": "Mobile Engineer"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["role_id"] == "mobile-engineer"
    assert data["role_title"] == "Mobile Engineer"

    details = data["skill_details"]
    assert "mobile-architecture" in details
    assert "kotlin" in details
    assert "swift" in details
    assert "rest-apis" in details


@pytest.mark.asyncio
async def test_unsupported_role_in_api_rejected_with_422(client: AsyncClient, test_session: AsyncSession):
    """Verifies API explicitly returns domain error for unsupported roles without silent fallback."""
    await seed_skill_taxonomy_and_roles(test_session)

    token, _ = await register_and_login(client, "fail_candidate@example.com", "Alex Turner")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Attempt to calculate gap analysis for unsupported role
    res = await client.post(
        "/api/v1/skills/gap-analysis",
        headers=headers,
        json={"role_id": "blockchain-developer"},
    )
    assert res.status_code in [404, 422]
    data = res.json()
    err_msg = data.get("error", {}).get("message") or data.get("message", "")
    assert "not supported" in err_msg.lower()
    assert "data-engineer" in err_msg
    assert "mobile-engineer" in err_msg

    # 2. Attempt to update profile career goals with unsupported role returns 422
    res_prof = await client.put(
        "/api/v1/profile/career-goals",
        headers=headers,
        json={"primary_role_id": "blockchain-developer"},
    )
    assert res_prof.status_code == 422
    data_prof = res_prof.json()
    err_prof = data_prof.get("error", {}).get("message") or data_prof.get("message", "")
    assert "not currently supported" in err_prof.lower()
    assert "data-engineer" in err_prof


@pytest.mark.asyncio
async def test_changing_role_triggers_recalculation(client: AsyncClient, test_session: AsyncSession):
    """Verifies switching from backend-developer to data-engineer generates new snapshot."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, _ = await register_and_login(client, "switch_candidate@example.com", "Vikram Sen")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Initial backend-developer analysis
    res1 = await client.post(
        "/api/v1/skills/gap-analysis",
        headers=headers,
        json={"role_id": "backend-developer"},
    )
    assert res1.status_code == 201
    assert res1.json()["role_id"] == "backend-developer"

    # 2. Switch to data-engineer
    res2 = await client.post(
        "/api/v1/skills/gap-analysis",
        headers=headers,
        json={"role_id": "data-engineer"},
    )
    assert res2.status_code == 201
    assert res2.json()["role_id"] == "data-engineer"
    assert res2.json()["id"] != res1.json()["id"]

    # 3. Fetching latest for specific role returns the correct snapshot
    res3 = await client.get(
        "/api/v1/skills/gap-analysis?role_id=backend-developer",
        headers=headers,
    )
    assert res3.status_code == 200
    assert res3.json()["role_id"] == "backend-developer"


@pytest.mark.asyncio
async def test_roadmap_generation_supports_new_roles(client: AsyncClient, test_session: AsyncSession):
    """Verifies roadmap engine creates tailored learning plans for data-engineer."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, _ = await register_and_login(client, "roadmap_de@example.com", "Anita Roy")
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.post(
        "/api/v1/roadmap/generate",
        headers=headers,
        json={"role_id": "data-engineer", "weekly_hours": 12},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["target_role_id"] == "data-engineer"
    assert len(data["phases"]) > 0


@pytest.mark.asyncio
async def test_missing_role_without_profile_fails_explicitly(client: AsyncClient, test_session: AsyncSession):
    """Verifies that requesting roadmap with an unsupported role fails explicitly without silent fallback."""
    await seed_skill_taxonomy_and_roles(test_session)

    token, _ = await register_and_login(client, "norole_user@example.com", "No Role User")
    headers = {"Authorization": f"Bearer {token}"}

    # Request roadmap generation with invalid/unsupported role
    res = await client.post(
        "/api/v1/roadmap/generate",
        headers=headers,
        json={"role_id": "quantum-computing-engineer", "weekly_hours": 10},
    )
    assert res.status_code == 422
    data = res.json()
    err_msg = data.get("error", {}).get("message") or data.get("message", "")
    assert "not currently supported" in err_msg
    assert "data-engineer" in err_msg
    assert "mobile-engineer" in err_msg


@pytest.mark.asyncio
async def test_multi_tenant_authorization_isolation(client: AsyncClient, test_session: AsyncSession):
    """Verifies that candidate snapshots and analyses are strictly isolated across accounts."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    # Candidate 1
    token1, _ = await register_and_login(client, "user1@example.com", "User One")
    res1 = await client.post(
        "/api/v1/skills/gap-analysis",
        headers={"Authorization": f"Bearer {token1}"},
        json={"role_id": "mobile-engineer"},
    )
    assert res1.status_code == 201
    snap1_id = res1.json()["id"]

    # Candidate 2
    token2, _ = await register_and_login(client, "user2@example.com", "User Two")
    res2 = await client.get(
        "/api/v1/skills/gap-analysis/history",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert res2.status_code == 200
    user2_snapshots = res2.json()["items"]
    assert all(s["id"] != snap1_id for s in user2_snapshots)


@pytest.mark.asyncio
async def test_regression_existing_roles_still_pass(client: AsyncClient, test_session: AsyncSession):
    """Verifies existing roles (backend-developer, frontend-developer) calculate without regression."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, _ = await register_and_login(client, "reg_candidate@example.com", "Regression Test")
    headers = {"Authorization": f"Bearer {token}"}

    for role_id in ["backend-developer", "frontend-developer", "data-scientist"]:
        res = await client.post(
            "/api/v1/skills/gap-analysis",
            headers=headers,
            json={"role_id": role_id},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["role_id"] == role_id
        assert "role_alignment_score" in data
        assert "evidence_coverage_score" in data
        assert len(data["skill_details"]) > 0
