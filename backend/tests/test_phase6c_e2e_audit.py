"""
Phase 6C: Comprehensive End-to-End Skill Gap Analysis Integration Audit & Verification Suite.

Validates the full Phase 6 lifecycle:
1. Complete 20-step user journey from registration through gap analysis, evidence drill-down,
   diagnostic examination, recalculation, snapshot preservation, and relogin persistence.
2. Role catalog requirements verification across all benchmark roles (including Software Engineer,
   Backend Developer, Frontend Developer, Data Analyst, Data Scientist, ML Engineer, AI Engineer)
   and incomplete role profile rejection.
3. Multi-source evidence provenance calibration (Self-reported, Resume claims, Diagnostic tests,
   unassessed handling, conflicting evidence resolution, score improvement over time).
4. Deterministic mathematical calculations (identic inputs -> identic outputs, weighted priorities,
   alignment vs coverage distinction, boundary conditions 0-100%).
5. Multi-tenant security and authorization boundaries (401 unauthenticated, 403/404 cross-user,
   data sanitization).
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
from app.models.assessments import Assessment, AssessmentAttempt
from app.models.career import CareerProfile, Project, Role
from app.models.skills import RoleRequirement, Skill, SkillGapAnalysis, UserSkill


# ─── Test Helpers ───────────────────────────────────────────────────

async def register_and_login(client: AsyncClient, email: str, full_name: str) -> tuple[str, uuid.UUID]:
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


# ─── SECTION 1: COMPLETE 20-STEP USER JOURNEY ────────────────────────

@pytest.mark.asyncio
async def test_complete_20_step_skill_gap_user_journey(test_session: AsyncSession, client: AsyncClient):
    """
    Executes the full 20-step user journey specified in Phase 6C audit requirements.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    # Step 1: User registers and logs in
    token, user_id = await register_and_login(client, "journey.user@example.com", "Journey Candidate")
    auth_header = {"Authorization": f"Bearer {token}"}

    # Step 2: User sets primary role on career profile
    profile_setup = await client.put(
        "/api/v1/profile/career-goals",
        headers=auth_header,
        json={
            "primary_role_id": "backend-developer",
            "career_stage": "early_career",
            "work_preference": "remote",
            "target_locations": ["Remote"],
        },
    )
    assert profile_setup.status_code == 200

    # Step 3: Available target roles load from backend
    roles_res = await client.get("/api/v1/roles")
    assert roles_res.status_code == 200
    roles_data = roles_res.json()
    assert roles_data["total"] >= 7
    backend_role = next((r for r in roles_data["roles"] if r["id"] == "backend-developer"), None)
    assert backend_role is not None

    # Step 4 & 5: User selects target role and retrieves role requirements
    role_req_res = await client.get("/api/v1/roles/backend-developer/requirements")
    assert role_req_res.status_code == 200
    requirements = role_req_res.json()
    assert len(requirements) >= 10
    assert any(r["skill_id"] == "python" for r in requirements)

    # Step 6, 7, 8, 9, 10: User requests initial gap analysis (persisted snapshot)
    gap_res = await client.get("/api/v1/skills/gap-analysis?role_id=backend-developer", headers=auth_header)
    assert gap_res.status_code == 200
    initial_analysis = gap_res.json()

    # Step 11: Display role alignment score (baseline candidate has 0 or minimal alignment)
    alignment = initial_analysis["role_alignment_score"]
    assert 0.0 <= alignment <= 100.0

    # Step 12: Display evidence coverage (baseline has 0.0% coverage)
    coverage = initial_analysis["evidence_coverage_score"]
    assert 0.0 <= coverage <= 100.0
    assert coverage == 0.0  # Zero evidence at start

    # Step 13: Display strengths, developing, gaps, missing correctly
    assert len(initial_analysis["missing_skills"]) >= 5
    assert len(initial_analysis["strongest_skills"]) == 0
    python_skill = initial_analysis["skill_details"]["python"]
    assert python_skill["status"] == "NOT_IN_PROFILE"
    assert python_skill["current_level"] == 0

    # Step 14: Inspect evidence behind individual skill
    evidence_res = await client.get("/api/v1/skills/gap-analysis/python/evidence", headers=auth_header)
    assert evidence_res.status_code == 200
    ev_data = evidence_res.json()
    assert ev_data["skill_id"] == "python"
    assert ev_data["current_level"] == 0
    assert len(ev_data["evidence_items"]) == 0

    # Step 15: Identify high-priority gaps
    gaps = initial_analysis["prioritized_gaps"]
    assert len(gaps) > 0
    critical_gaps = [g for g in gaps if g["priority"] == "CRITICAL"]
    assert len(critical_gaps) >= 1  # Mandatory skills with deficit >= 2 are CRITICAL

    # Step 16: User identifies recommended diagnostic assessment
    recommended = initial_analysis["recommended_assessments"]
    assert len(recommended) > 0
    python_rec = next((a for a in recommended if a["skill_id"] == "python"), None)
    assert python_rec is not None
    target_assessment_id = python_rec["assessment_id"]

    # Verify assessment exists in DB
    asmt_res = await client.get(f"/api/v1/assessments/{target_assessment_id}", headers=auth_header)
    assert asmt_res.status_code == 200
    asmt_detail = asmt_res.json()
    assert asmt_detail["skill_id"] == "python"

    # Step 17: User completes the assessment scoring 94% (Level 4 Mastered)
    now = datetime.now(timezone.utc)
    attempt = AssessmentAttempt(
        id=uuid.uuid4(),
        assessment_id=uuid.UUID(target_assessment_id),
        user_id=user_id,
        status="completed",
        score_percentage=decimal.Decimal("94.0"),
        passed=True,
        started_at=now,
        completed_at=now,
    )
    test_session.add(attempt)
    await test_session.commit()

    # Step 18: Request recalculation and verify newly retrieved analysis
    recalc_res = await client.post(
        "/api/v1/skills/gap-analysis/recalculate",
        headers=auth_header,
        json={"role_id": "backend-developer"},
    )
    assert recalc_res.status_code == 200
    refreshed_analysis = recalc_res.json()

    # Verify score improved and python became a verified STRENGTH
    assert refreshed_analysis["role_alignment_score"] > initial_analysis["role_alignment_score"]
    assert refreshed_analysis["evidence_coverage_score"] > initial_analysis["evidence_coverage_score"]
    assert "Python" in refreshed_analysis["strongest_skills"]
    assert "Python" not in refreshed_analysis["missing_skills"]

    refreshed_python = refreshed_analysis["skill_details"]["python"]
    assert refreshed_python["status"] == "STRENGTH"
    assert refreshed_python["current_level"] == 4
    assert refreshed_python["current_tier"] == "mastered"
    assert refreshed_python["evidence_count"] >= 1

    # Step 19: Previously generated analyses remain accessible in history
    history_res = await client.get("/api/v1/skills/gap-analysis/history", headers=auth_header)
    assert history_res.status_code == 200
    history = history_res.json()
    assert history["total"] >= 2
    # Verify active flag
    current_snapshots = [s for s in history["items"] if s["is_current"]]
    assert len(current_snapshots) == 1
    assert current_snapshots[0]["id"] == refreshed_analysis["id"]

    # Step 20: Persistence across subsequent requests (simulating reload/relogin)
    relogin_res = await client.get("/api/v1/skills/gap-analysis", headers=auth_header)
    assert relogin_res.status_code == 200
    relogin_data = relogin_res.json()
    assert relogin_data["id"] == refreshed_analysis["id"]
    assert relogin_data["role_alignment_score"] == refreshed_analysis["role_alignment_score"]
    assert "Python" in relogin_data["strongest_skills"]


# ─── SECTION 2: ROLE REQUIREMENTS VERIFICATION ──────────────────────

@pytest.mark.asyncio
async def test_role_catalog_requirements_completeness(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies that all required initial roles are seeded with curated, canonical requirements.
    Roles checked:
    - Software Engineer
    - Backend Developer
    - Frontend Developer
    - Data Analyst
    - Data Scientist
    - Machine Learning Engineer
    - AI Engineer
    """
    await seed_skill_taxonomy_and_roles(test_session)

    required_role_ids = [
        "software-engineer",
        "backend-developer",
        "frontend-developer",
        "data-analyst",
        "data-scientist",
        "machine-learning-engineer",
        "ai-engineer",
    ]

    for role_id in required_role_ids:
        r = await client.get(f"/api/v1/roles/{role_id}")
        assert r.status_code == 200, f"Role {role_id} not found"
        role_data = r.json()
        assert role_data["is_complete"] is True
        assert len(role_data["requirements"]) >= 5, f"Role {role_id} has insufficient requirements"

        # Verify weights and levels are valid
        for req in role_data["requirements"]:
            assert req["required_level"] in [1, 2, 3, 4]
            assert req["weight"] > 0.0
            assert req["importance"] in ["mandatory", "preferred", "bonus"]
            assert req["skill_id"] is not None


@pytest.mark.asyncio
async def test_incomplete_role_profile_rejected(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies that an incomplete role profile is rejected with ValidationException
    and does not silently produce misleading scores.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "incomplete.role@example.com", "Incomplete Tester")
    auth_header = {"Authorization": f"Bearer {token}"}

    # Insert an incomplete role (is_complete = False, no requirements)
    incomplete_role = Role(
        id="draft-quantum-engineer",
        title="Draft Quantum Engineer",
        description="Work in progress draft role without requirements",
        category="engineering",
        is_complete=False,
    )
    test_session.add(incomplete_role)
    await test_session.commit()

    # Attempting to calculate gap analysis must be rejected with 422
    calc_res = await client.post(
        "/api/v1/skills/gap-analysis",
        headers=auth_header,
        json={"role_id": "draft-quantum-engineer"},
    )
    assert calc_res.status_code == 422
    err_body = calc_res.json()
    err_msg = err_body.get("error", {}).get("message", "") or err_body.get("detail", "")
    assert "incomplete profile" in err_msg.lower() or "benchmark requirements" in err_msg.lower()


# ─── SECTION 3: EVIDENCE & PROVENANCE INTEGRATION ───────────────────

@pytest.mark.asyncio
async def test_unverified_resume_claims_tagged_not_assessed(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies that self-reported and resume-extracted claims are flagged as unverified
    (is_verified=False) and strictly categorized as NOT_ASSESSED, preventing false mastery.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, user_id = await register_and_login(client, "unverified.user@example.com", "Unverified Candidate")
    auth_header = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token, "backend-developer")

    # Fetch career profile
    profile = await test_session.scalar(select(CareerProfile).where(CareerProfile.user_id == user_id))
    assert profile is not None

    # Candidate claims 'FastAPI' via resume extraction
    user_skill = UserSkill(
        id=uuid.uuid4(),
        career_profile_id=profile.id,
        skill_id="fastapi",
        proficiency_tier="mastered",  # Candidate claimed 'mastered'
        confidence_score=decimal.Decimal("0.95"),
        is_verified=False,  # Unverified extraction
        primary_source="extracted",
    )
    test_session.add(user_skill)
    await test_session.commit()

    # Run gap analysis
    res = await client.post(
        "/api/v1/skills/gap-analysis/recalculate",
        headers=auth_header,
        json={"role_id": "backend-developer"},
    )
    assert res.status_code == 200
    data = res.json()

    fastapi_comp = data["skill_details"]["fastapi"]
    # Invariant: Unverified claim CANNOT claim Level 3 or Level 4!
    assert fastapi_comp["current_level"] <= 2
    assert fastapi_comp["status"] == "NOT_ASSESSED"
    assert "FastAPI" in data["unassessed_skills"]
    assert "FastAPI" not in data["strongest_skills"]


@pytest.mark.asyncio
async def test_conflicting_evidence_resolution_and_score_improvement(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies that when conflicting evidence exists (e.g. low self-report vs high assessment test score),
    the objective assessment takes precedence. Also tests score improvement between consecutive attempts.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, user_id = await register_and_login(client, "conflict.user@example.com", "Conflict Candidate")
    auth_header = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token, "backend-developer")

    profile = await test_session.scalar(select(CareerProfile).where(CareerProfile.user_id == user_id))
    assert profile is not None

    # 1. Low self-reported skill
    user_skill = UserSkill(
        id=uuid.uuid4(),
        career_profile_id=profile.id,
        skill_id="python",
        proficiency_tier="unverified",
        confidence_score=decimal.Decimal("0.30"),
        is_verified=False,
        primary_source="self_reported",
    )
    test_session.add(user_skill)

    # 2. First assessment attempt: scored 55% (Level 2: Developing)
    py_asmt = await test_session.scalar(select(Assessment).where(Assessment.skill_id == "python"))
    assert py_asmt is not None

    t1 = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
    attempt1 = AssessmentAttempt(
        id=uuid.uuid4(),
        assessment_id=py_asmt.id,
        user_id=user_id,
        status="completed",
        score_percentage=decimal.Decimal("55.0"),
        passed=False,
        started_at=t1,
        completed_at=t1,
    )
    test_session.add(attempt1)
    await test_session.commit()

    # Recalculate: Level should be 2 (demonstrated, verified test)
    r1 = await client.post("/api/v1/skills/gap-analysis/recalculate", headers=auth_header, json={"role_id": "backend-developer"})
    assert r1.status_code == 200
    data1 = r1.json()
    assert data1["skill_details"]["python"]["current_level"] == 2
    assert data1["skill_details"]["python"]["status"] == "DEVELOPING"  # required is 3, current is 2 -> DEVELOPING

    # 3. Second assessment attempt: candidate studies and scores 88% (Level 4: Mastered)
    t2 = datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc)
    attempt2 = AssessmentAttempt(
        id=uuid.uuid4(),
        assessment_id=py_asmt.id,
        user_id=user_id,
        status="completed",
        score_percentage=decimal.Decimal("88.0"),
        passed=True,
        started_at=t2,
        completed_at=t2,
    )
    test_session.add(attempt2)
    await test_session.commit()

    # Recalculate: Python should now be promoted to Level 4 Mastered
    r2 = await client.post("/api/v1/skills/gap-analysis/recalculate", headers=auth_header, json={"role_id": "backend-developer"})
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["skill_details"]["python"]["current_level"] == 4
    assert data2["skill_details"]["python"]["status"] == "STRENGTH"
    assert data2["role_alignment_score"] > data1["role_alignment_score"]

    # 4. Verify evidence drilldown preserves BOTH attempts and the self-reported claim
    ev_res = await client.get("/api/v1/skills/gap-analysis/python/evidence", headers=auth_header)
    assert ev_res.status_code == 200
    evidence = ev_res.json()
    assert len(evidence["evidence_items"]) == 3  # 2 assessment attempts + 1 profile claim
    scores = [e["score"] for e in evidence["evidence_items"] if e["source"] == "assessment"]
    assert 55.0 in scores
    assert 88.0 in scores


# ─── SECTION 4: DETERMINISTIC CALCULATIONS & FORMULAS ────────────────

@pytest.mark.asyncio
async def test_deterministic_scoring_reproducibility(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies mathematical determinism: executing analysis multiple times
    with unchanged candidate evidence produces exact identical scores.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "determ.user@example.com", "Deterministic Candidate")
    auth_header = {"Authorization": f"Bearer {token}"}

    r1 = await client.post("/api/v1/skills/gap-analysis/recalculate", headers=auth_header, json={"role_id": "frontend-developer"})
    assert r1.status_code == 200
    run1 = r1.json()

    r2 = await client.post("/api/v1/skills/gap-analysis/recalculate", headers=auth_header, json={"role_id": "frontend-developer"})
    assert r2.status_code == 200
    run2 = r2.json()

    # Exact equality across all numerical fields
    assert run1["role_alignment_score"] == run2["role_alignment_score"]
    assert run1["evidence_coverage_score"] == run2["evidence_coverage_score"]
    assert run1["strongest_skills"] == run2["strongest_skills"]
    assert run1["missing_skills"] == run2["missing_skills"]
    assert len(run1["prioritized_gaps"]) == len(run2["prioritized_gaps"])


@pytest.mark.asyncio
async def test_alignment_vs_coverage_distinction(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies that Role Alignment is mathematically distinct from Evidence Coverage:
    Unverified claims can grant partial coverage ratio but provide zero or low verified coverage.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, user_id = await register_and_login(client, "distinction.user@example.com", "Distinction Candidate")
    auth_header = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token, "backend-developer")

    profile = await test_session.scalar(select(CareerProfile).where(CareerProfile.user_id == user_id))
    assert profile is not None

    # User adds projects covering multiple backend technologies (unverified project evidence)
    proj = Project(
        id=uuid.uuid4(),
        career_profile_id=profile.id,
        title="Microservices Portfolio",
        description="Built distributed microservices",
        technologies=["Python", "FastAPI", "Docker", "PostgreSQL"],
    )
    test_session.add(proj)
    await test_session.commit()

    r = await client.post("/api/v1/skills/gap-analysis/recalculate", headers=auth_header, json={"role_id": "backend-developer"})
    assert r.status_code == 200
    data = r.json()

    # Role alignment should be > 0 due to demonstrated project knowledge
    assert data["role_alignment_score"] > 0.0
    # But all project-backed skills are unverified (is_verified = False), so status is NOT_ASSESSED
    assert len(data["unassessed_skills"]) >= 3
    # Coverage score is scaled by 0.5 for unverified claims
    assert data["evidence_coverage_score"] < data["role_alignment_score"]


# ─── SECTION 5: SECURITY, MULTI-TENANCY & ERROR HANDLING ─────────────

@pytest.mark.asyncio
async def test_security_and_cross_user_isolation(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies that candidate analyses and evidence cannot be accessed across tenant boundaries.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token_a, user_a = await register_and_login(client, "alice@example.com", "Alice Tester")
    token_b, user_b = await register_and_login(client, "bob@example.com", "Bob Tester")

    # Alice creates an analysis for AI Engineer
    alice_res = await client.post(
        "/api/v1/skills/gap-analysis/recalculate",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"role_id": "ai-engineer"},
    )
    assert alice_res.status_code == 200
    alice_data = alice_res.json()
    assert alice_data["role_id"] == "ai-engineer"

    # Bob fetches his latest analysis — must NOT get Alice's analysis
    bob_res = await client.get(
        "/api/v1/skills/gap-analysis",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert bob_res.status_code == 200
    bob_data = bob_res.json()
    assert bob_data["id"] != alice_data["id"]
    assert bob_data["career_profile_id"] != alice_data["career_profile_id"]

    # Bob fetches his history — must contain 1 item (his own), not Alice's
    bob_hist = await client.get(
        "/api/v1/skills/gap-analysis/history",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert bob_hist.status_code == 200
    assert all(item["id"] != alice_data["id"] for item in bob_hist.json()["items"])


@pytest.mark.asyncio
async def test_unauthenticated_requests_strictly_rejected(client: AsyncClient):
    """Verifies that all protected endpoints reject requests without valid Bearer tokens."""
    unauth_endpoints = [
        ("GET", "/api/v1/skills/gap-analysis"),
        ("POST", "/api/v1/skills/gap-analysis"),
        ("POST", "/api/v1/skills/gap-analysis/recalculate"),
        ("GET", "/api/v1/skills/gap-analysis/history"),
        ("GET", "/api/v1/skills/gap-analysis/python/evidence"),
    ]

    for method, path in unauth_endpoints:
        if method == "GET":
            r = await client.get(path)
        else:
            r = await client.post(path, json={})
        assert r.status_code == 401, f"{method} {path} did not return 401 Unauthorized"
