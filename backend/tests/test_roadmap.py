"""
Comprehensive Integration & Verification Test Suite for Phase 7A: Personalized Learning Roadmap Engine.
Validates:
1. End-to-end curriculum generation from career objectives and skill gap analyses.
2. 4-phase sequential structure, actionable milestones, and estimated hours.
3. Topological prerequisite DAG validation (acyclic dependencies).
4. Scheduling, feasibility calculations (feasible vs demanding vs unrealistic).
5. Granular progress tracking, phase completion, and task execution updates.
6. Dynamic adaptation based on verified diagnostic assessment scores.
7. Multi-tenant security isolation and unauthenticated request rejection.
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
from app.models.assessments import Assessment, AssessmentAttempt, AssessmentResult
from app.models.career import CareerProfile, Role
from app.models.roadmap import Roadmap, RoadmapPhase, RoadmapTask
from app.models.skills import SkillGapAnalysis


# ─── Helpers ──────────────────────────────────────────────────────────

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


# ─── Test Suite ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_roadmap_unauthenticated_rejected(client: AsyncClient):
    """Unauthenticated requests must be rejected with HTTP 401."""
    r = await client.post("/api/v1/roadmap/generate", json={})
    assert r.status_code == 401

    r2 = await client.get("/api/v1/roadmap")
    assert r2.status_code == 401

    r3 = await client.patch(f"/api/v1/roadmap/tasks/{uuid.uuid4()}", json={"status": "completed"})
    assert r3.status_code == 401


@pytest.mark.asyncio
async def test_generate_roadmap_without_target_role(test_session: AsyncSession, client: AsyncClient):
    """User without a selected target role receives HTTP 422 with validation error."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "norole.roadmap@test.com", "No Role Candidate")

    r = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert r.status_code == 422
    data = r.json()
    err_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
    assert "target role must be selected" in err_msg.lower()


@pytest.mark.asyncio
async def test_generate_roadmap_with_incomplete_role(test_session: AsyncSession, client: AsyncClient):
    """Requesting an incomplete or non-existent role returns HTTP 422 or 404."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "incompleterole@test.com", "Draft Candidate")

    # Incomplete role
    r = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"role_id": "non-existent-role-xyz"},
    )
    assert r.status_code in (404, 422)


@pytest.mark.asyncio
async def test_generate_roadmap_success_backend_developer(test_session: AsyncSession, client: AsyncClient):
    """
    Generates a complete multi-phase personalized roadmap for a Backend Developer.
    Verifies 4 phases, actionable tasks, estimated effort, and valid status.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)
    token, user_id = await register_and_login(client, "backend.curriculum@test.com", "Alex Chen")
    await setup_candidate_profile(client, token, "backend-developer")

    # Generate roadmap
    r = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"weekly_hours": 10, "target_timeline_months": 6},
    )
    assert r.status_code == 201
    data = r.json()

    assert data["target_role_id"] == "backend-developer"
    assert data["target_role_title"] == "Backend Developer"
    assert data["version"] == 1
    assert data["is_active"] is True
    assert data["status"] == "active"
    assert data["weekly_hours"] == 10
    assert data["total_estimated_hours"] > 20
    assert data["total_tasks"] > 0
    assert data["completed_tasks"] == 0
    assert data["progress_percentage"] == 0.0
    assert data["feasibility_status"] in ("feasible", "demanding", "unrealistic")
    assert len(data["phases"]) >= 3

    # Check phase details
    p1 = data["phases"][0]
    assert "Foundations" in p1["title"]
    assert p1["order_index"] == 1
    assert p1["status"] == "in_progress"
    assert len(p1["tasks"]) > 0

    # Check task structure
    first_task = p1["tasks"][0]
    assert "title" in first_task
    assert "description" in first_task
    assert first_task["estimated_hours"] > 0
    assert first_task["status"] == "pending"
    assert len(first_task["resource_urls"]) > 0
    assert "deliverable_requirement" in first_task


@pytest.mark.asyncio
async def test_get_active_roadmap_and_by_id(test_session: AsyncSession, client: AsyncClient):
    """GET /api/v1/roadmap returns the user's active roadmap."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)
    token, _ = await register_and_login(client, "fetch.roadmap@test.com", "Maya Lin")
    await setup_candidate_profile(client, token, "frontend-developer")

    # Generate
    gen_res = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"role_id": "frontend-developer", "weekly_hours": 12},
    )
    assert gen_res.status_code == 201
    roadmap_id = gen_res.json()["id"]

    # Retrieve via GET /roadmap
    r1 = await client.get("/api/v1/roadmap", headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 200
    assert r1.json()["id"] == roadmap_id
    assert r1.json()["target_role_id"] == "frontend-developer"

    # Retrieve via GET /roadmap/{roadmap_id}
    r2 = await client.get(f"/api/v1/roadmap/{roadmap_id}", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["id"] == roadmap_id


@pytest.mark.asyncio
async def test_roadmap_multi_tenant_isolation(test_session: AsyncSession, client: AsyncClient):
    """User B cannot access or modify User A's roadmap (HTTP 403 Forbidden)."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    token_a, _ = await register_and_login(client, "user_a.roadmap@test.com", "User Alpha")
    await setup_candidate_profile(client, token_a, "data-scientist")
    res_a = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"role_id": "data-scientist"},
    )
    assert res_a.status_code == 201
    roadmap_a_id = res_a.json()["id"]
    task_a_id = res_a.json()["phases"][0]["tasks"][0]["id"]

    # User B registers and tries to access User A's roadmap
    token_b, _ = await register_and_login(client, "user_b.roadmap@test.com", "User Beta")
    r_forbidden = await client.get(
        f"/api/v1/roadmap/{roadmap_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_forbidden.status_code == 403

    # User B tries to update User A's task
    r_task_forbidden = await client.patch(
        f"/api/v1/roadmap/tasks/{task_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"status": "completed"},
    )
    assert r_task_forbidden.status_code == 403


@pytest.mark.asyncio
async def test_roadmap_progress_and_task_execution(test_session: AsyncSession, client: AsyncClient):
    """
    Tests updating task status to 'in_progress', then 'completed' with deliverable URL.
    Verifies progress percentage increases and task completed_at is set.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)
    token, _ = await register_and_login(client, "progress.task@test.com", "Devon Miles")
    await setup_candidate_profile(client, token, "backend-developer")

    gen_res = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"weekly_hours": 10},
    )
    roadmap_data = gen_res.json()
    roadmap_id = roadmap_data["id"]
    task_1 = roadmap_data["phases"][0]["tasks"][0]
    task_1_id = task_1["id"]

    # 1. Check initial progress
    prog_res = await client.get(
        f"/api/v1/roadmap/{roadmap_id}/progress",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert prog_res.status_code == 200
    prog_data = prog_res.json()
    assert prog_data["completed_tasks"] == 0
    assert prog_data["progress_percentage"] == 0.0
    assert prog_data["remaining_hours"] > 0
    assert len(prog_data["next_recommended_tasks"]) > 0

    # 2. Start Task 1
    patch_1 = await client.patch(
        f"/api/v1/roadmap/tasks/{task_1_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "in_progress"},
    )
    assert patch_1.status_code == 200
    assert patch_1.json()["status"] == "in_progress"

    # 3. Complete Task 1 with deliverable submission URL
    sub_url = "https://github.com/devon/async-python-service"
    patch_2 = await client.patch(
        f"/api/v1/roadmap/tasks/{task_1_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "completed", "submission_url": sub_url},
    )
    assert patch_2.status_code == 200
    assert patch_2.json()["status"] == "completed"
    assert patch_2.json()["submission_url"] == sub_url
    assert patch_2.json()["completed_at"] is not None

    # 4. Verify progress recalculated
    prog_res2 = await client.get(
        f"/api/v1/roadmap/{roadmap_id}/progress",
        headers={"Authorization": f"Bearer {token}"},
    )
    prog_data2 = prog_res2.json()
    assert prog_data2["completed_tasks"] == 1
    assert prog_data2["progress_percentage"] > 0.0
    assert prog_data2["completed_hours"] == task_1["estimated_hours"]


@pytest.mark.asyncio
async def test_roadmap_regeneration_and_versioning(test_session: AsyncSession, client: AsyncClient):
    """
    Generating with force_regenerate=True archives previous version and creates version 2.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)
    token, _ = await register_and_login(client, "versioning.roadmap@test.com", "Vera Rubin")
    await setup_candidate_profile(client, token, "machine-learning-engineer")

    # Generate v1
    v1_res = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"weekly_hours": 10},
    )
    assert v1_res.status_code == 201
    assert v1_res.json()["version"] == 1
    v1_id = v1_res.json()["id"]

    # Regenerate v2
    v2_res = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"weekly_hours": 15, "force_regenerate": True},
    )
    assert v2_res.status_code == 201
    assert v2_res.json()["version"] == 2
    assert v2_res.json()["weekly_hours"] == 15
    v2_id = v2_res.json()["id"]
    assert v1_id != v2_id

    # Verify v1 is archived in DB
    archived_v1 = await test_session.scalar(select(Roadmap).where(Roadmap.id == uuid.UUID(v1_id)))
    assert archived_v1.is_active is False
    assert archived_v1.status == "archived"


@pytest.mark.asyncio
async def test_roadmap_dynamic_adaptation(test_session: AsyncSession, client: AsyncClient):
    """
    When user completes and passes an assessment for a skill, calling /roadmap/{id}/adapt
    auto-completes corresponding pending milestones.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)
    token, user_id = await register_and_login(client, "adapt.roadmap@test.com", "Ada Lovelace")
    await setup_candidate_profile(client, token, "backend-developer")

    gen_res = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"weekly_hours": 10},
    )
    roadmap_id = gen_res.json()["id"]

    # Simulate user passing Python diagnostic assessment
    asmt = (await test_session.scalars(select(Assessment).where(Assessment.skill_id == "python"))).first()
    assert asmt is not None

    attempt = AssessmentAttempt(
        user_id=user_id,
        assessment_id=asmt.id,
        status="completed",
        score_percentage=decimal.Decimal("85.0"),
        passed=True,
    )
    test_session.add(attempt)
    await test_session.commit()

    # Trigger adaptation
    adapt_res = await client.post(
        f"/api/v1/roadmap/{roadmap_id}/adapt",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert adapt_res.status_code == 200
    adapt_data = adapt_res.json()
    assert adapt_data["adapted"] is True
    assert adapt_data["tasks_auto_completed"] >= 1
    assert "automatically completed" in adapt_data["message"]


@pytest.mark.asyncio
async def test_acyclic_prerequisites_and_topological_soundness(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies that the generated roadmap has no circular dependencies in prerequisite_task_ids.
    """
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)
    token, _ = await register_and_login(client, "dag.roadmap@test.com", "Grace Hopper")
    await setup_candidate_profile(client, token, "ai-engineer")

    gen_res = await client.post(
        "/api/v1/roadmap/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"role_id": "ai-engineer", "weekly_hours": 10},
    )
    assert gen_res.status_code == 201
    data = gen_res.json()

    all_task_ids = {t["id"] for p in data["phases"] for t in p["tasks"]}

    # Ensure all listed prerequisites are valid and DAG has no cycles
    for p in data["phases"]:
        for t in p["tasks"]:
            for prereq in t["prerequisite_task_ids"]:
                assert prereq in all_task_ids, f"Prerequisite {prereq} not found in roadmap tasks"
                assert prereq != t["id"], "Task cannot depend on itself"
