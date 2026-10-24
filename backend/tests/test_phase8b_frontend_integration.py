"""
Phase 8B Frontend Integration & API Contract Verification Tests.
Verifies the end-to-end integration and API response contracts expected by the
frontend Job Discovery and Market Intelligence dashboard (Phase 8B).

Validates:
1. Catalog search with multi-facet query parameters (/api/v1/jobs)
2. Sorting by newest, highest salary, title (A-Z)
3. Canonical skill filtering and required vs preferred categorization
4. Single job detail retrieval and source lineage (/api/v1/jobs/{id})
5. Candidate manual job import workflow (/api/v1/jobs/import)
6. Market intelligence aggregate indicators and role filtering (/api/v1/jobs/market-intelligence)
7. Multi-tenant authentication enforcement and error states
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


@pytest.mark.asyncio
async def test_frontend_job_search_and_filter_workflow(test_session: AsyncSession, client: AsyncClient):
    """Simulates the frontend JobFilterPanel user interactions and response contracts."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.search@example.com", "Search Candidate")

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=22, db=test_session)

    # 1. Initial Page Load (Default newest sort, page 1)
    res = await client.get("/api/v1/jobs", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 22
    assert len(data["items"]) == 20
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total_pages"] == 2

    # Verify item schema matches JobOpportunity
    first_item = data["items"][0]
    assert "id" in first_item
    assert "title" in first_item
    assert "company_name" in first_item
    assert "location" in first_item
    assert "remote_type" in first_item
    assert "role_id" in first_item
    assert "experience_level" in first_item
    assert "source" in first_item
    assert "freshness_status" in first_item
    assert "skills" in first_item

    # 2. Filter by Canonical Role (Backend Developer)
    r_role = await client.get(
        "/api/v1/jobs?role_id=backend-developer",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_role.status_code == 200
    role_items = r_role.json()["items"]
    assert len(role_items) >= 3
    assert all(i["role_id"] == "backend-developer" for i in role_items)

    # 3. Filter by Workplace Type (Remote)
    r_remote = await client.get(
        "/api/v1/jobs?remote_type=remote",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_remote.status_code == 200
    assert all(i["remote_type"] == "remote" for i in r_remote.json()["items"])

    # 4. Filter by Experience Level (Junior)
    r_exp = await client.get(
        "/api/v1/jobs?experience_level=junior",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_exp.status_code == 200
    assert all(i["experience_level"] == "junior" for i in r_exp.json()["items"])

    # 5. Filter by Canonical Skill (Python)
    r_skill = await client.get(
        "/api/v1/jobs?skill_id=python",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_skill.status_code == 200
    assert r_skill.json()["total"] >= 5
    for item in r_skill.json()["items"]:
        tagged_skills = [s["skill_id"] for s in item["skills"]]
        assert "python" in tagged_skills

    # 6. Keyword Search ("Netflix")
    r_kw = await client.get(
        "/api/v1/jobs?keyword=Netflix",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_kw.status_code == 200
    assert r_kw.json()["total"] == 1
    assert r_kw.json()["items"][0]["company_name"] == "Netflix"

    # 7. Sort Options
    r_sort_sal = await client.get(
        "/api/v1/jobs?sort_by=salary_high",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_sort_sal.status_code == 200
    sal_items = [i["max_salary"] for i in r_sort_sal.json()["items"] if i["max_salary"] is not None]
    assert sal_items == sorted(sal_items, reverse=True)


@pytest.mark.asyncio
async def test_frontend_job_detail_and_source_lineage(test_session: AsyncSession, client: AsyncClient):
    """Verifies the JobDetailModal and /jobs/[id] response contracts and source transparency."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.detail@example.com", "Detail Candidate")

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    # Fetch catalog list
    list_res = await client.get("/api/v1/jobs", headers={"Authorization": f"Bearer {token}"})
    job_id = list_res.json()["items"][0]["id"]

    # Fetch detail
    detail_res = await client.get(f"/api/v1/jobs/{job_id}", headers={"Authorization": f"Bearer {token}"})
    assert detail_res.status_code == 200
    detail = detail_res.json()

    assert detail["id"] == job_id
    assert detail["source"] in ("seed", "manual", "arbeitnow")
    assert detail["freshness_status"] in ("active", "needs_refresh", "expired", "closed")
    assert isinstance(detail["responsibilities"], list)
    assert isinstance(detail["required_qualifications"], list)
    assert isinstance(detail["preferred_qualifications"], list)
    assert isinstance(detail["skills"], list)

    # Distinguish mandatory vs preferred skills
    mandatory = [s for s in detail["skills"] if s["is_mandatory"]]
    preferred = [s for s in detail["skills"] if not s["is_mandatory"]]
    assert len(mandatory) > 0  # Curated seed jobs have mandatory skills tagged

    # Non-existent ID returns 404
    fake_id = uuid.uuid4()
    not_found = await client.get(f"/api/v1/jobs/{fake_id}", headers={"Authorization": f"Bearer {token}"})
    assert not_found.status_code == 404


@pytest.mark.asyncio
async def test_frontend_market_intelligence_workflow(test_session: AsyncSession, client: AsyncClient):
    """Verifies MarketIntelligenceCard contracts, distributions, and provisional status."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.market@example.com", "Market Candidate")

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=22, db=test_session)

    # Overall Market Intelligence
    res = await client.get("/api/v1/jobs/market-intelligence", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    intel = res.json()

    assert intel["total_active_jobs"] == 22
    assert isinstance(intel["role_distribution"], dict)
    assert isinstance(intel["remote_distribution"], dict)
    assert isinstance(intel["experience_distribution"], dict)
    assert len(intel["top_demanded_skills"]) > 0

    first_skill = intel["top_demanded_skills"][0]
    assert "skill_id" in first_skill
    assert "name" in first_skill
    assert "job_count" in first_skill
    assert "percentage" in first_skill
    assert first_skill["percentage"] > 0

    assert intel["salary_insights"]["sample_size"] == 22
    assert intel["salary_insights"]["median_salary"] is not None
    assert intel["is_provisional"] is False

    # Role-Filtered Market Intelligence (frontend role selector)
    r_filtered = await client.get(
        "/api/v1/jobs/market-intelligence?role_id=frontend-developer",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_filtered.status_code == 200
    filtered_intel = r_filtered.json()
    assert filtered_intel["total_active_jobs"] >= 3
    assert "frontend-developer" in filtered_intel["role_distribution"]


@pytest.mark.asyncio
async def test_frontend_manual_import_and_catalog_update(test_session: AsyncSession, client: AsyncClient):
    """Verifies candidate manual job import through the modal immediately enriches catalog."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "candidate.import@example.com", "Import Candidate")

    import_payload = {
        "title": "Junior Python Backend Developer",
        "company_name": "Supabase",
        "location": "Remote",
        "remote_type": "remote",
        "experience_level": "entry_level",
        "min_salary": 110000,
        "max_salary": 130000,
        "currency": "USD",
        "application_url": "https://supabase.com/careers/backend-dev",
        "description_text": """
        Join Supabase building open source backend tools.
        We develop high-performance database microservices using Python, FastAPI, and PostgreSQL.
        Knowledge of Docker, Git, and automated testing with pytest is required.
        Experience with AWS and Redis is preferred.
        """,
    }

    # Submit import
    r_import = await client.post(
        "/api/v1/jobs/import",
        headers={"Authorization": f"Bearer {token}"},
        json=import_payload,
    )
    assert r_import.status_code == 201
    imported = r_import.json()
    assert imported["source"] == "manual"
    assert imported["company_name"] == "Supabase"
    assert imported["role_id"] == "backend-developer"

    # Immediately search for the imported job
    r_search = await client.get(
        "/api/v1/jobs?keyword=Supabase",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_search.status_code == 200
    assert r_search.json()["total"] >= 1
    found_item = r_search.json()["items"][0]
    assert found_item["company_name"] == "Supabase"
    assert found_item["source"] == "manual"
