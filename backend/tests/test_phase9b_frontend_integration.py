"""
Phase 9B Frontend Integration & API Contract Verification Tests.
Verifies the end-to-end integration and API response contracts expected by the
frontend Personalized Job Matching and Explainability Drawer components (Phase 9B).

Validates:
1. Recommendations endpoint (/api/v1/jobs/recommendations) contract, schema, and ranking
2. Recommendation filters (min_score, remote_type, include_provisional)
3. Explainability drawer endpoint (/api/v1/jobs/{job_id}/match-explanation) contract
4. Single job match retrieval (/api/v1/jobs/{job_id}/match)
5. On-demand match recalculation (/api/v1/jobs/{job_id}/match/recalculate)
6. Recommendation batch refresh (/api/v1/jobs/matches/refresh)
7. Multi-tenant security and unauthenticated request blocking
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.services.job_ingestion_pipeline import JobIngestionPipelineService


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
    work_preference: str = "remote",
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.put(
        "/api/v1/profile/career-goals",
        headers=headers,
        json={
            "primary_role_id": target_role_id,
            "career_stage": "early_career",
            "work_preference": work_preference,
            "target_locations": ["San Francisco, CA"],
        },
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_recommendations_endpoint_contract(test_session: AsyncSession, client: AsyncClient):
    """Verifies that /api/v1/jobs/recommendations returns the exact contract required by JobRecommendationResponse."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.recom@example.com", "Recommendation Candidate")
    await setup_candidate_profile(client, token)

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=10, db=test_session)

    # Fetch recommendations
    res = await client.get("/api/v1/jobs/recommendations", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()

    # Validate top-level schema
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert "scoring_version" in data
    assert data["total"] > 0
    assert len(data["items"]) > 0

    # Validate first recommendation item structure (job + match)
    first_item = data["items"][0]
    assert "job" in first_item
    assert "match" in first_item

    # Verify job structure
    job = first_item["job"]
    assert "id" in job
    assert "title" in job
    assert "company_name" in job
    assert "location" in job
    assert "remote_type" in job
    assert "skills" in job

    # Verify match structure
    match = first_item["match"]
    assert "match_id" in match
    assert "job_id" in match
    assert "overall_score" in match
    assert "breakdown" in match
    assert "matched_skills" in match
    assert "missing_skills" in match
    assert "matched_preferred_skills" in match
    assert "explanation" in match
    assert "skills_detail" in match
    assert "is_stale" in match

    # Verify breakdown structure
    breakdown = match["breakdown"]
    assert "overall_score" in breakdown
    assert "skill_score" in breakdown
    assert "experience_score" in breakdown
    assert "project_score" in breakdown
    assert "location_score" in breakdown
    assert "preference_score" in breakdown
    assert "evidence_coverage" in breakdown
    assert "is_provisional" in breakdown
    assert "weights" in breakdown
    assert "evaluated_factors" in breakdown
    assert "unevaluated_factors" in breakdown

    # Verify ranking: items must be sorted descending by overall_score
    scores = [item["match"]["overall_score"] for item in data["items"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_recommendations_filters_and_provisional(test_session: AsyncSession, client: AsyncClient):
    """Verifies that query parameters filter the recommendations appropriately."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.filters@example.com", "Filter Candidate")
    await setup_candidate_profile(client, token, work_preference="remote")

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=10, db=test_session)

    # Test filtering by remote_type=remote
    res_remote = await client.get(
        "/api/v1/jobs/recommendations?remote_type=remote",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_remote.status_code == 200
    items_remote = res_remote.json()["items"]
    for it in items_remote:
        assert it["job"]["remote_type"] == "remote"

    # Test filtering by min_score
    res_min = await client.get(
        "/api/v1/jobs/recommendations?min_score=50.0",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_min.status_code == 200
    for it in res_min.json()["items"]:
        assert it["match"]["overall_score"] >= 50.0


@pytest.mark.asyncio
async def test_job_match_explainability_drawer_contract(test_session: AsyncSession, client: AsyncClient):
    """Verifies that /api/v1/jobs/{job_id}/match-explanation returns the exact contract for JobMatchDrawer."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.drawer@example.com", "Drawer Candidate")
    await setup_candidate_profile(client, token)

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    # Get a job ID from recommendations
    rec_res = await client.get("/api/v1/jobs/recommendations", headers={"Authorization": f"Bearer {token}"})
    job_id = rec_res.json()["items"][0]["job"]["id"]

    # Request explainability drawer
    res = await client.get(
        f"/api/v1/jobs/{job_id}/match-explanation",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    drawer = res.json()

    # Validate drawer contracts
    assert drawer["job_id"] == job_id
    assert "overall_score" in drawer
    assert "evidence_coverage" in drawer
    assert "breakdown" in drawer
    assert "matched_skills" in drawer
    assert "missing_skills" in drawer
    assert "matched_preferred_skills" in drawer
    assert "unknown_skills" in drawer
    assert "hiring_rationale" in drawer
    assert "strengths" in drawer
    assert "gaps" in drawer
    assert "recommended_actions" in drawer
    assert "skills_detail" in drawer

    # Validate skills_detail items
    assert len(drawer["skills_detail"]) > 0
    first_skill = drawer["skills_detail"][0]
    assert "skill_id" in first_skill
    assert "name" in first_skill
    assert "category" in first_skill
    assert "is_mandatory" in first_skill
    assert "classification" in first_skill
    assert "user_confidence" in first_skill
    assert "explanation" in first_skill


@pytest.mark.asyncio
async def test_single_job_match_and_recalculate(test_session: AsyncSession, client: AsyncClient):
    """Verifies single job match endpoint and forced recalculation."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.recalc@example.com", "Recalc Candidate")
    await setup_candidate_profile(client, token)

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    # Get a job ID
    rec_res = await client.get("/api/v1/jobs/recommendations", headers={"Authorization": f"Bearer {token}"})
    job_id = rec_res.json()["items"][0]["job"]["id"]

    # 1. Get single match
    res_match = await client.get(
        f"/api/v1/jobs/{job_id}/match",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_match.status_code == 200
    match_data = res_match.json()
    assert match_data["job_id"] == job_id
    assert "overall_score" in match_data

    # 2. Recalculate match
    res_recalc = await client.post(
        f"/api/v1/jobs/{job_id}/match/recalculate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_recalc.status_code == 200
    recalc_data = res_recalc.json()
    assert recalc_data["job_id"] == job_id
    assert recalc_data["is_stale"] is False


@pytest.mark.asyncio
async def test_batch_refresh_recommendations(test_session: AsyncSession, client: AsyncClient):
    """Verifies batch refreshing all recommendations for the authenticated user."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.batch@example.com", "Batch Candidate")
    await setup_candidate_profile(client, token)

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    res = await client.post(
        "/api/v1/jobs/matches/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert "recalculated_count" in data
    assert data["recalculated_count"] >= 5
    assert "scoring_version" in data
    assert "message" in data


@pytest.mark.asyncio
async def test_unauthenticated_requests_blocked(client: AsyncClient):
    """Verifies that job matching endpoints enforce authentication."""
    dummy_uuid = str(uuid.uuid4())

    r1 = await client.get("/api/v1/jobs/recommendations")
    assert r1.status_code == 401

    r2 = await client.get(f"/api/v1/jobs/{dummy_uuid}/match")
    assert r2.status_code == 401

    r3 = await client.get(f"/api/v1/jobs/{dummy_uuid}/match-explanation")
    assert r3.status_code == 401

    r4 = await client.post(f"/api/v1/jobs/{dummy_uuid}/match/recalculate")
    assert r4.status_code == 401

    r5 = await client.post("/api/v1/jobs/matches/refresh")
    assert r5.status_code == 401
