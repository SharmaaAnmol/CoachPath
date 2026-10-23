"""
Comprehensive Integration Tests for Phase 6A: Skill Gap Analysis Engine.
Tests canonical skill taxonomy, 7 target roles, deterministic alignment and coverage scoring,
evidence provenance calibration (assessments, claims, projects), gap prioritization,
snapshot history preservation, legacy compatibility, and multi-tenant security.
"""

from __future__ import annotations

import decimal
import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.assessment_seeder import seed_diagnostic_assessments
from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.assessments import Assessment, AssessmentAttempt, AssessmentResult
from app.models.auth import User
from app.models.career import CareerProfile, Project, Role
from app.models.skills import RoleRequirement, Skill, SkillGap, SkillGapAnalysis, UserSkill


# ─── Test Helpers ───────────────────────────────────────────────────

async def register_and_login(client: AsyncClient, email: str, full_name: str) -> Tuple[str, uuid.UUID]:
    pw = "SecurePassword123!"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": full_name},
    )
    assert r.status_code == 201
    user_id = uuid.UUID(r.json()["user_id"])
    r2 = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert r2.status_code == 200
    return r2.json()["access_token"], user_id


async def setup_candidate_profile(
    client: AsyncClient,
    token: str,
    target_role_id: str = "backend-developer",
) -> None:
    """Sets target role and preferences on the authenticated user's career profile."""
    r = await client.put(
        "/api/v1/profile/career-goals",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "primary_role_id": target_role_id,
            "career_stage": "early_career",
            "work_preference": "remote",
            "target_locations": ["San Francisco, CA"],
        },
    )
    assert r.status_code == 200


# ─── 1. Taxonomy and Role Catalog Tests ──────────────────────────────

@pytest.mark.asyncio
async def test_seed_and_list_canonical_skills(test_session: AsyncSession, client: AsyncClient):
    """Verifies that seeding populates canonical skills and GET /api/v1/skills returns them."""
    await seed_skill_taxonomy_and_roles(test_session)

    r = await client.get("/api/v1/skills")
    assert r.status_code == 200
    skills = r.json()
    assert len(skills) >= 40

    skill_ids = {s["id"] for s in skills}
    assert "python" in skill_ids
    assert "sql-databases" in skill_ids
    assert "postgresql" in skill_ids
    assert "fastapi" in skill_ids
    assert "docker" in skill_ids
    assert "ai-llm" in skill_ids
    assert "dsa" in skill_ids


@pytest.mark.asyncio
async def test_list_and_get_target_roles(test_session: AsyncSession, client: AsyncClient):
    """Verifies listing supported roles and retrieving role requirements."""
    await seed_skill_taxonomy_and_roles(test_session)

    # 1. List roles
    r = await client.get("/api/v1/roles")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 7
    role_ids = {role["id"] for role in data["roles"]}
    expected_roles = {
        "backend-developer",
        "frontend-developer",
        "fullstack-developer",
        "data-scientist",
        "machine-learning-engineer",
        "ai-engineer",
        "devops-cloud-engineer",
    }
    assert expected_roles.issubset(role_ids)

    # 2. Get role detail with requirements
    r_detail = await client.get("/api/v1/roles/backend-developer")
    assert r_detail.status_code == 200
    detail = r_detail.json()
    assert detail["id"] == "backend-developer"
    assert detail["is_complete"] is True
    assert len(detail["requirements"]) >= 8

    # Check python requirement
    py_req = next((req for req in detail["requirements"] if req["skill_id"] == "python"), None)
    assert py_req is not None
    assert py_req["importance"] == "mandatory"
    assert py_req["required_level"] >= 3
    assert py_req["weight"] > 1.0
    assert py_req["rationale"] is not None

    # 3. Get role requirements endpoint
    r_reqs = await client.get("/api/v1/roles/backend-developer/requirements")
    assert r_reqs.status_code == 200
    reqs_list = r_reqs.json()
    assert len(reqs_list) == len(detail["requirements"])

    # 4. Non-existent role returns 404
    r_404 = await client.get("/api/v1/roles/non-existent-role")
    assert r_404.status_code == 404


# ─── 2. Baseline Gap Analysis Tests ─────────────────────────────────

@pytest.mark.asyncio
async def test_gap_analysis_baseline_no_evidence(test_session: AsyncSession, client: AsyncClient):
    """
    Tests gap analysis on a fresh candidate with a selected role but zero evidence.
    Verifies deterministic low alignment, 0% coverage, and prioritized missing skills.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, user_id = await register_and_login(client, "baseline@test.com", "Baseline Candidate")
    await setup_candidate_profile(client, token, "backend-developer")

    # Trigger calculation
    r = await client.post(
        "/api/v1/skills/gap-analysis",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    analysis = r.json()

    assert analysis["role_id"] == "backend-developer"
    assert analysis["is_current"] is True
    assert analysis["role_alignment_score"] == 0.0
    assert analysis["evidence_coverage_score"] == 0.0
    assert len(analysis["strongest_skills"]) == 0
    assert len(analysis["missing_skills"]) >= 8
    assert len(analysis["prioritized_gaps"]) >= 8

    # Prioritized gaps should put mandatory requirements with largest gap first
    top_gap = analysis["prioritized_gaps"][0]
    assert top_gap["priority"] == "CRITICAL"
    assert top_gap["importance"] == "mandatory"
    assert top_gap["current_level"] == 0
    assert top_gap["required_level"] >= 3

    # Recommended assessments should include diagnostic tests for missing skills
    assert len(analysis["recommended_assessments"]) >= 1
    asmt_skills = {a["skill_id"] for a in analysis["recommended_assessments"]}
    assert "python" in asmt_skills or "sql-databases" in asmt_skills

    # Diagnostic narrative must be generated and truthful
    narrative = analysis["explanation_narrative"]
    assert "0.0%" in narrative
    assert "No verified competencies" in narrative


# ─── 3. Calibrated Evidence Gap Analysis Tests ───────────────────────

@pytest.mark.asyncio
async def test_gap_analysis_with_objective_diagnostic_assessment(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """
    Verifies that objective diagnostic assessment scores provide verified evidence,
    elevate skill levels, increase role alignment & coverage scores, and populate strongest_skills.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, user_id = await register_and_login(client, "assessed@test.com", "Assessed Candidate")
    await setup_candidate_profile(client, token, "backend-developer")

    # 1. Simulate passing Python diagnostic assessment with 90.0% (Level 4: Mastered)
    py_asmt = await test_session.scalar(
        select(Assessment).where(Assessment.skill_id == "python")
    )
    assert py_asmt is not None

    now = datetime.now(timezone.utc)
    attempt = AssessmentAttempt(
        id=uuid.uuid4(),
        assessment_id=py_asmt.id,
        user_id=user_id,
        status="completed",
        score_percentage=decimal.Decimal("90.0"),
        passed=True,
        started_at=now,
        completed_at=now,
    )
    test_session.add(attempt)
    await test_session.commit()

    # 2. Trigger gap analysis recalculation
    r = await client.post(
        "/api/v1/skills/gap-analysis/recalculate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    analysis = r.json()

    # Python must now be a verified strength meeting required level 3
    assert "Python" in analysis["strongest_skills"]
    assert "Python" not in analysis["missing_skills"]

    py_detail = analysis["skill_details"]["python"]
    assert py_detail["status"] == "STRENGTH"
    assert py_detail["current_level"] == 4
    assert py_detail["current_tier"] == "mastered"
    assert py_detail["coverage_ratio"] == 1.0
    assert py_detail["evidence_count"] >= 1
    assert py_detail["evidence_items"][0]["is_verified"] is True
    assert py_detail["evidence_items"][0]["score"] == 90.0

    # Role alignment and evidence coverage scores must be strictly greater than 0
    assert analysis["role_alignment_score"] > 0.0
    assert analysis["evidence_coverage_score"] > 0.0

    # Narrative must celebrate verified Python strength
    assert "Python" in analysis["explanation_narrative"]


@pytest.mark.asyncio
async def test_unverified_claims_cannot_grant_mastery(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """
    Verifies the critical CoachPath invariant:
    Skills claimed via resume or profile without diagnostic assessment are classified as
    NOT_ASSESSED and can NEVER claim level 3 (Proficient) or level 4 (Mastered).
    """
    await seed_skill_taxonomy_and_roles(test_session)

    token, user_id = await register_and_login(client, "claimed@test.com", "Claimed Candidate")
    await setup_candidate_profile(client, token, "backend-developer")

    # Add unverified UserSkill (self-reported FastAPI)
    profile = await test_session.scalar(
        select(CareerProfile).where(CareerProfile.user_id == user_id)
    )
    us = UserSkill(
        id=uuid.uuid4(),
        career_profile_id=profile.id,
        skill_id="fastapi",
        confidence_score=decimal.Decimal("0.30"),
        proficiency_tier="unverified",
        primary_source="self_reported",
        is_verified=False,
    )
    test_session.add(us)
    await test_session.commit()

    # Calculate gap analysis
    r = await client.post(
        "/api/v1/skills/gap-analysis",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    analysis = r.json()

    # FastAPI must be in unassessed_skills, NOT in strongest_skills
    assert "FastAPI" in analysis["unassessed_skills"]
    assert "FastAPI" not in analysis["strongest_skills"]

    fastapi_detail = analysis["skill_details"]["fastapi"]
    assert fastapi_detail["status"] == "NOT_ASSESSED"
    assert fastapi_detail["current_level"] <= 2
    assert fastapi_detail["evidence_items"][0]["is_verified"] is False


@pytest.mark.asyncio
async def test_project_evidence_integration(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """Verifies that projects listed on the career profile provide calibrated project evidence."""
    await seed_skill_taxonomy_and_roles(test_session)

    token, user_id = await register_and_login(client, "project@test.com", "Project Candidate")
    await setup_candidate_profile(client, token, "backend-developer")

    profile = await test_session.scalar(
        select(CareerProfile).where(CareerProfile.user_id == user_id)
    )

    # Add a project using Docker and Redis
    proj = Project(
        id=uuid.uuid4(),
        career_profile_id=profile.id,
        title="Microservice Cache Gateway",
        description="High throughput caching reverse-proxy built with Docker and Redis.",
        technologies=["docker", "redis"],
        bullet_points=["Reduced latency by 45%", "Deployed multi-container cluster"],
    )
    test_session.add(proj)
    await test_session.commit()

    r = await client.post(
        "/api/v1/skills/gap-analysis",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    analysis = r.json()

    docker_detail = analysis["skill_details"]["docker"]
    assert docker_detail["evidence_count"] >= 1
    assert docker_detail["evidence_items"][0]["source"] == "project"
    assert docker_detail["current_level"] == 2  # Level 2 demonstrated via project
    assert docker_detail["evidence_items"][0]["is_verified"] is False


# ─── 4. History and Snapshot Preservation Tests ──────────────────────

@pytest.mark.asyncio
async def test_snapshot_history_preservation(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """
    Verifies that recalculating gap analysis creates a new snapshot without
    overwriting historical snapshots, properly managing is_current flags.
    """
    await seed_skill_taxonomy_and_roles(test_session)

    token, user_id = await register_and_login(client, "history@test.com", "History Candidate")
    await setup_candidate_profile(client, token, "backend-developer")

    # Snapshot 1
    r1 = await client.post(
        "/api/v1/skills/gap-analysis",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r1.status_code == 201
    snap1_id = r1.json()["id"]

    # Snapshot 2 (Recalculate)
    r2 = await client.post(
        "/api/v1/skills/gap-analysis/recalculate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    snap2_id = r2.json()["id"]

    assert snap1_id != snap2_id

    # Check history endpoint
    r_hist = await client.get(
        "/api/v1/skills/gap-analysis/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_hist.status_code == 200
    hist = r_hist.json()
    assert hist["total"] == 2
    assert len(hist["items"]) == 2

    # Latest should be is_current=True, older should be is_current=False
    latest = hist["items"][0]
    older = hist["items"][1]
    assert latest["id"] == snap2_id
    assert latest["is_current"] is True
    assert older["id"] == snap1_id
    assert older["is_current"] is False


# ─── 5. Evidence Drill-Down and Legacy Compatibility ─────────────────

@pytest.mark.asyncio
async def test_skill_evidence_drilldown_endpoint(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """Verifies GET /api/v1/skills/gap-analysis/{skill_id}/evidence endpoint."""
    await seed_skill_taxonomy_and_roles(test_session)

    token, user_id = await register_and_login(client, "drilldown@test.com", "Drilldown Candidate")
    await setup_candidate_profile(client, token, "backend-developer")

    # Request evidence for Python
    r = await client.get(
        "/api/v1/skills/gap-analysis/python/evidence",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["skill_id"] == "python"
    assert data["skill_name"] == "Python"
    assert data["current_level"] == 0
    assert data["is_verified"] is False
    assert isinstance(data["evidence_items"], list)

    # Unknown skill returns 404
    r_unknown = await client.get(
        "/api/v1/skills/gap-analysis/non-existent-skill/evidence",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_unknown.status_code == 404


@pytest.mark.asyncio
async def test_legacy_skills_gaps_endpoint(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """Verifies backward compatibility with GET /api/v1/skills/gaps."""
    await seed_skill_taxonomy_and_roles(test_session)

    token, user_id = await register_and_login(client, "legacy@test.com", "Legacy Candidate")
    await setup_candidate_profile(client, token, "backend-developer")

    r = await client.get(
        "/api/v1/skills/gaps",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "readiness_percentage" in data
    assert "met_skills" in data
    assert "developing_skills" in data
    assert "missing_skills" in data
    assert "explanation_narrative" in data


# ─── 6. Multi-Tenant Security and Validation Tests ───────────────────

@pytest.mark.asyncio
async def test_unauthenticated_gap_analysis_rejected(client: AsyncClient):
    """Verifies that all protected gap analysis endpoints return 401 when unauthenticated."""
    r1 = await client.get("/api/v1/skills/gap-analysis")
    assert r1.status_code == 401

    r2 = await client.post("/api/v1/skills/gap-analysis")
    assert r2.status_code == 401

    r3 = await client.get("/api/v1/skills/gap-analysis/history")
    assert r3.status_code == 401

    r4 = await client.get("/api/v1/skills/gaps")
    assert r4.status_code == 401


@pytest.mark.asyncio
async def test_cross_user_isolation(test_session: AsyncSession, client: AsyncClient):
    """Verifies that User A's gap analyses are isolated and invisible to User B."""
    await seed_skill_taxonomy_and_roles(test_session)

    token_a, user_a = await register_and_login(client, "user_a@test.com", "User Alpha")
    await setup_candidate_profile(client, token_a, "backend-developer")

    token_b, user_b = await register_and_login(client, "user_b@test.com", "User Beta")
    await setup_candidate_profile(client, token_b, "frontend-developer")

    # Calculate gap analysis for User A
    r_a = await client.post(
        "/api/v1/skills/gap-analysis",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r_a.status_code == 201
    data_a = r_a.json()
    assert data_a["role_id"] == "backend-developer"

    # User B should see their own target role (frontend-developer) when requesting gap analysis
    r_b = await client.get(
        "/api/v1/skills/gap-analysis",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_b.status_code == 200
    data_b = r_b.json()
    assert data_b["role_id"] == "frontend-developer"
    assert data_b["id"] != data_a["id"]
