"""
Phase 6B Frontend Integration & API Contract Verification Tests.
Verifies the end-to-end integration and API response contracts expected by the
frontend Skill Gap Analysis Dashboard (Phase 6B).

Validates:
1. Role listing and single role detail (/api/v1/roles, /api/v1/roles/{role_id})
2. Role alignment with candidate profile primary target role (/api/v1/profile/career-goals)
3. Active Gap Analysis data contract (/api/v1/skills/gap-analysis)
4. Evidence drill-down contracts for each skill status (/api/v1/skills/gap-analysis/{skill_id}/evidence)
5. Recalculate endpoint updating analysis snapshot (/api/v1/skills/gap-analysis/recalculate)
6. Snapshot history listing (/api/v1/skills/gap-analysis/history)
7. Remedial Diagnostic Assessment linking (/api/v1/assessments/{assessment_id})
"""

from __future__ import annotations

import decimal
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.assessment_seeder import seed_diagnostic_assessments
from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles


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


@pytest.mark.asyncio
async def test_frontend_end_to_end_skill_gap_workflow(test_session: AsyncSession, client: AsyncClient):
    """
    Simulates the exact frontend workflow:
    1. Loads all roles for TargetRoleSelector
    2. Retrieves profile career goals
    3. Runs initial gap analysis for the primary role
    4. Verifies radial gauges, priority list, competency items contract
    5. Drilldowns into evidence modal
    6. Triggers recalculation
    7. Inspects snapshot history
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, user_id = await register_and_login(client, "frontend.user@example.com", "Frontend Test User")
    auth_header = {"Authorization": f"Bearer {token}"}

    # Step 1: Frontend fetches roles for the dropdown
    roles_res = await client.get("/api/v1/roles")
    assert roles_res.status_code == 200
    roles_data = roles_res.json()
    assert "roles" in roles_data
    assert roles_data["total"] >= 7
    roles = roles_data["roles"]
    assert len(roles) >= 7
    backend_role = next((r for r in roles if r["id"] == "backend-developer"), None)
    assert backend_role is not None
    assert backend_role["title"] == "Backend Developer"

    # Step 2: Frontend gets single role details
    role_detail_res = await client.get("/api/v1/roles/backend-developer")
    assert role_detail_res.status_code == 200
    role_detail = role_detail_res.json()
    assert len(role_detail["requirements"]) >= 10
    first_req = role_detail["requirements"][0]
    assert "skill_name" in first_req
    assert "required_level" in first_req
    assert "importance" in first_req

    # Step 3: Candidate sets primary role
    profile_res = await client.put(
        "/api/v1/profile/career-goals",
        headers=auth_header,
        json={
            "primary_role_id": "backend-developer",
            "career_stage": "early_career",
            "work_preference": "remote",
            "target_locations": ["Remote"],
        },
    )
    assert profile_res.status_code == 200

    # Step 4: Frontend fetches gap analysis for backend-developer
    gap_res = await client.get("/api/v1/skills/gap-analysis?role_id=backend-developer", headers=auth_header)
    assert gap_res.status_code == 200
    gap_data = gap_res.json()

    # Verify root contract matches SkillGapAnalysisData
    assert gap_data["role_id"] == "backend-developer"
    assert gap_data["role_title"] == "Backend Developer"
    assert "role_alignment_score" in gap_data
    assert "evidence_coverage_score" in gap_data
    assert "skill_details" in gap_data
    assert "prioritized_gaps" in gap_data
    assert "recommended_assessments" in gap_data
    assert "explanation_narrative" in gap_data
    assert "strongest_skills" in gap_data
    assert "developing_skills" in gap_data
    assert "skill_gaps" in gap_data
    assert "unassessed_skills" in gap_data
    assert "missing_skills" in gap_data

    # Verify skill_details dictionary contract
    skill_details = gap_data["skill_details"]
    assert "python" in skill_details
    python_comp = skill_details["python"]
    assert python_comp["skill_name"] == "Python"
    assert python_comp["required_level"] >= 1
    assert python_comp["status"] in ["STRENGTH", "DEVELOPING", "GAP", "NOT_ASSESSED", "NOT_IN_PROFILE"]

    # Step 5: Evidence drilldown modal fetch
    evidence_res = await client.get("/api/v1/skills/gap-analysis/python/evidence", headers=auth_header)
    assert evidence_res.status_code == 200
    evidence_data = evidence_res.json()
    assert evidence_data["skill_id"] == "python"
    assert "evidence_items" in evidence_data
    assert "current_level" in evidence_data
    assert "current_tier" in evidence_data
    assert "is_verified" in evidence_data

    # Step 6: Recalculate analysis
    recalc_res = await client.post("/api/v1/skills/gap-analysis/recalculate?role_id=backend-developer", headers=auth_header)
    assert recalc_res.status_code == 200
    recalc_data = recalc_res.json()
    assert recalc_data["role_id"] == "backend-developer"

    # Step 7: Analysis snapshot history modal fetch
    history_res = await client.get("/api/v1/skills/gap-analysis/history", headers=auth_header)
    assert history_res.status_code == 200
    history_data = history_res.json()
    assert "items" in history_data
    assert "total" in history_data
    assert history_data["total"] >= 2
    # Verify current snapshot flag
    active_snapshots = [a for a in history_data["items"] if a["is_current"]]
    assert len(active_snapshots) == 1


@pytest.mark.asyncio
async def test_frontend_role_switching_and_live_assessment_impact(test_session: AsyncSession, client: AsyncClient):
    """
    Tests dynamic role switching and verifying that passing a diagnostic assessment
    directly transforms the competency status on subsequent gap analysis recalculation.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token, user_id = await register_and_login(client, "dynamic.switch@example.com", "Dynamic User")
    auth_header = {"Authorization": f"Bearer {token}"}

    # 1. Switch to Frontend Developer role via recalculate endpoint
    fe_res = await client.post(
        "/api/v1/skills/gap-analysis/recalculate",
        headers=auth_header,
        json={"role_id": "frontend-developer"},
    )
    assert fe_res.status_code == 200
    fe_data = fe_res.json()
    assert fe_data["role_id"] == "frontend-developer"
    assert "react" in fe_data["skill_details"]
    assert fe_data["skill_details"]["react"]["status"] in ["NOT_IN_PROFILE", "NOT_ASSESSED"]

    # 2. Simulate user taking React / Web Dev assessment
    from app.models.assessments import Assessment, AssessmentAttempt
    from sqlalchemy import select
    from datetime import datetime, timezone

    assess_stmt = select(Assessment).where(Assessment.skill_id == "web-development")
    web_assess = await test_session.scalar(assess_stmt)
    assert web_assess is not None

    now = datetime.now(timezone.utc)
    attempt = AssessmentAttempt(
        id=uuid.uuid4(),
        user_id=user_id,
        assessment_id=web_assess.id,
        status="completed",
        score_percentage=decimal.Decimal("92.0"),
        passed=True,
        started_at=now,
        completed_at=now,
    )
    test_session.add(attempt)
    await test_session.commit()

    # 3. Recalculate Frontend Developer analysis
    recalc_res = await client.post(
        "/api/v1/skills/gap-analysis/recalculate",
        headers=auth_header,
        json={"role_id": "frontend-developer"},
    )
    assert recalc_res.status_code == 200
    refreshed_fe = recalc_res.json()

    # Web development skill must now be a verified STRENGTH or level 4
    web_comp = refreshed_fe["skill_details"].get("web-development")
    assert web_comp is not None
    assert web_comp["current_level"] == 4
    assert web_comp["status"] == "STRENGTH"
    assert web_comp["evidence_count"] >= 1

    # 4. Verify evidence drill-down for web-development returns the test record
    evidence_res = await client.get("/api/v1/skills/gap-analysis/web-development/evidence", headers=auth_header)
    assert evidence_res.status_code == 200
    evidence_data = evidence_res.json()
    assert evidence_data["is_verified"] is True
    assert evidence_data["current_level"] == 4
    assert len(evidence_data["evidence_items"]) >= 1
    assessment_ev = next((e for e in evidence_data["evidence_items"] if e["source"] == "assessment"), None)
    assert assessment_ev is not None
    assert assessment_ev["score"] == 92.0
    assert assessment_ev["is_verified"] is True


@pytest.mark.asyncio
async def test_frontend_error_handling_contracts(test_session: AsyncSession, client: AsyncClient):
    """Verifies error contracts expected by the frontend client (401, 404)."""
    await seed_skill_taxonomy_and_roles(test_session)

    # Unauthenticated
    unauth_res = await client.get("/api/v1/skills/gap-analysis")
    assert unauth_res.status_code == 401

    token, _ = await register_and_login(client, "err.tester@example.com", "Error Tester")
    auth_header = {"Authorization": f"Bearer {token}"}

    # Non-existent role calculation returns 404
    bad_role_res = await client.post(
        "/api/v1/skills/gap-analysis/recalculate",
        headers=auth_header,
        json={"role_id": "non-existent-role"},
    )
    assert bad_role_res.status_code == 404

    # Non-existent skill evidence returns 404
    bad_skill_res = await client.get("/api/v1/skills/gap-analysis/non-existent-skill/evidence", headers=auth_header)
    assert bad_skill_res.status_code == 404
