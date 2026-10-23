"""
Comprehensive Test Suite for Phase 8A: Job Market Intelligence and Job Ingestion Engine.
Covers:
1. Permitted source adapters (Seed, Manual, Mock, and Factory).
2. Data normalization (HTML cleaning, role mapping, remote classification, seniority, salary).
3. Canonical skill extraction and job section parsing.
4. Pipeline execution, duplicate prevention, and atomic upsert semantics.
5. Search API endpoints with multi-facet filters.
6. Market intelligence aggregate indicators and provisional calculations.
7. Audit trail records for ingestion runs.
"""

from __future__ import annotations

import decimal
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.jobs import Job, JobIngestionRun, JobSkill, JobSource
from app.schemas.jobs import JobImportRequest
from app.services.job_description_parser import (
    extract_sections,
    extract_skills_deterministic,
)
from app.services.job_ingestion_pipeline import JobIngestionPipelineService
from app.services.job_normalization import (
    classify_canonical_role,
    classify_experience_level,
    classify_remote_type,
    clean_html,
    compute_data_quality_score,
    compute_deduplication_hash,
    normalize_company_name,
    parse_salary_range,
)
from app.services.job_source_adapters import (
    JobSourceAdapterFactory,
    ManualImportAdapter,
    MockJobSourceAdapter,
    RawJobListing,
    SeedJobAdapter,
)


# ─── Auth Helper ──────────────────────────────────────────────────────

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


# ─── Unit Tests: Source Adapters ──────────────────────────────────────

@pytest.mark.asyncio
async def test_seed_job_adapter_returns_curated_data():
    adapter = SeedJobAdapter()
    assert adapter.source_name == "seed"
    assert adapter.provider_type == "seed"

    jobs = await adapter.fetch_jobs(batch_size=10, page=1)
    assert len(jobs) == 10
    assert all(isinstance(j, RawJobListing) for j in jobs)
    assert jobs[0].title
    assert jobs[0].company_name
    assert jobs[0].source == "seed"


@pytest.mark.asyncio
async def test_manual_import_adapter():
    adapter = ManualImportAdapter()
    assert adapter.source_name == "manual"
    assert adapter.provider_type == "manual"

    req = JobImportRequest(
        title="Junior Backend Python Engineer",
        company_name="Acme Corp",
        location="Remote",
        description_text="We need a Python developer who knows FastAPI, PostgreSQL, and Docker.",
        application_url="https://acme.com/apply",
        remote_type="remote",
        experience_level="entry_level",
        min_salary=100000,
        max_salary=120000,
        currency="USD",
    )

    listings = await adapter.fetch_jobs(import_request=req)
    assert len(listings) == 1
    raw = listings[0]
    assert raw.title == "Junior Backend Python Engineer"
    assert raw.company_name == "Acme Corp"
    assert raw.source == "manual"
    assert raw.min_salary == 100000


@pytest.mark.asyncio
async def test_mock_adapter_and_factory():
    JobSourceAdapterFactory.reset()
    mock_adapter = MockJobSourceAdapter()
    sample_jobs = [
        RawJobListing(
            title="SWE Intern",
            company_name="Tech Co",
            location="Remote",
            description_text="Internship for computer science students with Python and SQL.",
            application_url="https://tech.co/jobs/1",
            source="mock",
        )
    ]
    mock_adapter.set_jobs(sample_jobs)
    JobSourceAdapterFactory.register_adapter("mock", mock_adapter)

    retrieved = JobSourceAdapterFactory.get_adapter("mock")
    assert retrieved is mock_adapter

    fetched = await retrieved.fetch_jobs(batch_size=10)
    assert len(fetched) == 1
    assert fetched[0].title == "SWE Intern"


# ─── Unit Tests: Normalization Service ────────────────────────────────

def test_normalization_clean_html():
    raw_html = "<p>Join our <strong>infrastructure</strong> team.</p><br><li>Develop APIs in Python</li>"
    cleaned = clean_html(raw_html)
    assert "<p>" not in cleaned
    assert "<strong>" not in cleaned
    assert "• Develop APIs in Python" in cleaned


def test_normalization_canonical_role_classification():
    assert classify_canonical_role("Senior Python Backend Engineer") == "backend-developer"
    assert classify_canonical_role("React Frontend UI Developer") == "frontend-developer"
    assert classify_canonical_role("Fullstack Web Engineer") == "fullstack-developer"
    assert classify_canonical_role("Machine Learning Research Scientist") == "machine-learning-engineer"
    assert classify_canonical_role("Generative AI Prompt Engineer") == "ai-engineer"
    assert classify_canonical_role("DevOps & SRE Engineer") == "devops-cloud-engineer"
    assert classify_canonical_role("Data Scientist, Algorithms") == "data-scientist"
    assert classify_canonical_role("Business Intelligence SQL Analyst") == "data-analyst"
    assert classify_canonical_role("Core Software Engineer") == "software-engineer"


def test_normalization_remote_and_experience():
    assert classify_remote_type("San Francisco, CA (Remote)") == "remote"
    assert classify_remote_type("New York, NY", description="Hybrid work schedule 2 days in office") == "hybrid"
    assert classify_remote_type("Seattle, WA", description="On-site required") == "onsite"

    assert classify_experience_level("Software Engineer Intern") == "internship"
    assert classify_experience_level("Junior Developer", description="0-2 years experience") == "junior"
    assert classify_experience_level("Associate Engineer", description="Entry level graduates welcome") == "entry_level"
    assert classify_experience_level("Software Engineer II", description="3-5 years required") == "mid"


def test_normalization_salary_and_deduplication():
    min_sal, max_sal = parse_salary_range(None, None, "Base salary range is $110,000 to $130,000 per year.")
    assert min_sal == 110000
    assert max_sal == 130000

    hash1 = compute_deduplication_hash("Stripe, Inc.", "Junior Backend Engineer", "Seattle, WA")
    hash2 = compute_deduplication_hash("Stripe", "junior backend engineer", "Seattle, WA")
    assert hash1 == hash2


def test_normalization_quality_score():
    score = compute_data_quality_score(
        title="Junior Backend Engineer",
        description="Detailed description exceeding 200 characters containing comprehensive requirements, responsibilities, technical requirements, and company mission.",
        company="Stripe",
        location="Seattle, WA",
        skill_count=5,
        has_salary=True,
    )
    assert float(score) >= 0.90


# ─── Unit Tests: Description Parser & Skill Extraction ────────────────

def test_parser_extracts_canonical_skills():
    text = """
    We are seeking a Backend Developer proficient in Python, PostgreSQL, and FastAPI.
    Must have experience with Docker, Git, and REST APIs.
    Experience with Kubernetes and AWS is a plus.
    """
    skills = extract_skills_deterministic(text)
    skill_ids = {s["skill_id"] for s in skills}

    assert "python" in skill_ids
    assert "postgresql" in skill_ids
    assert "fastapi" in skill_ids
    assert "docker" in skill_ids
    assert "git" in skill_ids
    assert "rest-apis" in skill_ids
    assert "kubernetes" in skill_ids
    assert "aws" in skill_ids

    # Verify mandatory vs preferred flags
    k8s_skill = next(s for s in skills if s["skill_id"] == "kubernetes")
    assert k8s_skill["is_mandatory"] is False  # "is a plus" in context


def test_parser_extracts_sections():
    text = """
    ## Responsibilities
    - Build scalable payment pipelines
    - Optimize relational database queries

    ## Requirements
    - 2+ years of software experience
    - Proficiency in Python and SQL

    ## Nice to have
    - Experience with Redis
    """
    resp, req, pref = extract_sections(text)
    assert len(resp) >= 2
    assert "Build scalable payment pipelines" in resp[0]
    assert len(req) >= 2
    assert "Proficiency in Python and SQL" in req[1]
    assert len(pref) >= 1
    assert "Experience with Redis" in pref[0]


# ─── Integration Tests: Ingestion Pipeline & Persistence ──────────────

@pytest.mark.asyncio
async def test_pipeline_seed_ingestion(test_session: AsyncSession):
    # Seed canonical taxonomy first
    await seed_skill_taxonomy_and_roles(test_session)

    pipeline = JobIngestionPipelineService()
    summary = await pipeline.run_ingestion(
        source_name="seed",
        batch_size=10,
        db=test_session,
    )

    assert summary.status == "completed"
    assert summary.items_fetched == 10
    assert summary.items_inserted == 10
    assert summary.items_errored == 0

    # Verify persisted in database
    jobs_count = await test_session.scalar(select(func.count(Job.id)))
    assert jobs_count == 10

    # Verify skills were tagged
    skills_count = await test_session.scalar(select(func.count(JobSkill.id)))
    assert skills_count > 0

    # Idempotency / Upsert test: re-running does not duplicate
    summary2 = await pipeline.run_ingestion(
        source_name="seed",
        batch_size=10,
        db=test_session,
    )
    assert summary2.items_inserted == 0
    assert summary2.items_updated == 10

    jobs_count_after = await test_session.scalar(select(func.count(Job.id)))
    assert jobs_count_after == 10


# ─── API Integration Tests ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_jobs_api_unauthenticated_rejected(client: AsyncClient):
    r = await client.get("/api/v1/jobs")
    assert r.status_code == 401

    r2 = await client.get("/api/v1/jobs/market-intelligence")
    assert r2.status_code == 401

    r3 = await client.get("/api/v1/jobs/ingestion-runs")
    assert r3.status_code == 401


@pytest.mark.asyncio
async def test_jobs_api_search_and_filters(client: AsyncClient, test_session: AsyncSession):
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "job.search@example.com", "Job Searcher")

    # Ingest seed jobs
    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=22, db=test_session)

    # 1. Search all jobs
    r = await client.get("/api/v1/jobs", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 22
    assert len(data["items"]) == 20  # Default page size 20
    assert data["total_pages"] == 2

    # 2. Filter by role_id
    r_role = await client.get(
        "/api/v1/jobs?role_id=backend-developer",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_role.status_code == 200
    role_data = r_role.json()
    assert role_data["total"] >= 3
    assert all(item["role_id"] == "backend-developer" for item in role_data["items"])

    # 3. Filter by remote_type
    r_remote = await client.get(
        "/api/v1/jobs?remote_type=remote",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_remote.status_code == 200
    assert all(item["remote_type"] == "remote" for item in r_remote.json()["items"])

    # 4. Search by keyword
    r_kw = await client.get(
        "/api/v1/jobs?keyword=Stripe",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_kw.status_code == 200
    assert r_kw.json()["total"] >= 1
    assert "Stripe" in r_kw.json()["items"][0]["company_name"]


@pytest.mark.asyncio
async def test_jobs_api_get_by_id(client: AsyncClient, test_session: AsyncSession):
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "job.detail@example.com", "Job Detailer")

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    # Fetch a job id from search
    search_r = await client.get("/api/v1/jobs", headers={"Authorization": f"Bearer {token}"})
    job_id = search_r.json()["items"][0]["id"]

    # Fetch by ID
    detail_r = await client.get(f"/api/v1/jobs/{job_id}", headers={"Authorization": f"Bearer {token}"})
    assert detail_r.status_code == 200
    detail = detail_r.json()
    assert detail["id"] == job_id
    assert len(detail["skills"]) > 0

    # Non-existent job
    fake_id = uuid.uuid4()
    not_found_r = await client.get(f"/api/v1/jobs/{fake_id}", headers={"Authorization": f"Bearer {token}"})
    assert not_found_r.status_code == 404


@pytest.mark.asyncio
async def test_jobs_api_manual_import(client: AsyncClient, test_session: AsyncSession):
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "job.importer@example.com", "Job Importer")

    payload = {
        "title": "Junior Python Backend Engineer",
        "company_name": "NextGen Cloud",
        "location": "Remote",
        "remote_type": "remote",
        "experience_level": "entry_level",
        "min_salary": 95000,
        "max_salary": 115000,
        "currency": "USD",
        "application_url": "https://nextgen.cloud/jobs/junior-swe",
        "description_text": """
        Join NextGen Cloud building modern microservices.
        We develop APIs in Python using FastAPI and PostgreSQL.
        Knowledge of Docker, Git, and automated testing with pytest is required.
        Experience with AWS and Kubernetes is preferred.
        """,
    }

    r = await client.post(
        "/api/v1/jobs/import",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert r.status_code == 201
    imported = r.json()
    assert imported["title"] == "Junior Python Backend Engineer"
    assert imported["company_name"] == "NextGen Cloud"
    assert imported["source"] == "manual"
    assert imported["role_id"] == "backend-developer"

    skill_names = {s["skill_id"] for s in imported["skills"]}
    assert "python" in skill_names
    assert "postgresql" in skill_names
    assert "fastapi" in skill_names
    assert "docker" in skill_names


@pytest.mark.asyncio
async def test_jobs_api_market_intelligence(client: AsyncClient, test_session: AsyncSession):
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "job.market@example.com", "Market Analyst")

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=22, db=test_session)

    r = await client.get(
        "/api/v1/jobs/market-intelligence",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    intel = r.json()
    assert intel["total_active_jobs"] == 22
    assert "backend-developer" in intel["role_distribution"]
    assert "remote" in intel["remote_distribution"]
    assert len(intel["top_demanded_skills"]) > 0
    assert intel["salary_insights"]["sample_size"] > 0
    assert intel["salary_insights"]["average_min_salary"] > 0
    assert intel["is_provisional"] is False

    # Filter market intelligence by role
    r_role = await client.get(
        "/api/v1/jobs/market-intelligence?role_id=backend-developer",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_role.status_code == 200
    intel_role = r_role.json()
    assert intel_role["total_active_jobs"] >= 3
    assert "backend-developer" in intel_role["role_distribution"]


@pytest.mark.asyncio
async def test_jobs_api_ingestion_runs_audit(client: AsyncClient, test_session: AsyncSession):
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "job.audit@example.com", "Pipeline Auditor")

    # Trigger ingestion via API with mock
    mock_adapter = MockJobSourceAdapter([
        RawJobListing(
            title="Junior DevOps Engineer",
            company_name="CloudOps",
            location="Remote",
            description_text="Manage Linux systems, Docker containers, and CI/CD with Git.",
            application_url="https://cloudops.dev/jobs/1",
            source="mock",
        )
    ])
    JobSourceAdapterFactory.register_adapter("mock", mock_adapter)

    r_ingest = await client.post(
        "/api/v1/jobs/ingest",
        headers={"Authorization": f"Bearer {token}"},
        json={"source": "mock", "batch_size": 10, "force_refresh": False},
    )
    assert r_ingest.status_code == 200
    summary = r_ingest.json()
    assert summary["source_name"] == "mock"
    assert summary["status"] == "completed"
    assert summary["items_inserted"] == 1

    # Check ingestion runs audit endpoint
    r_runs = await client.get(
        "/api/v1/jobs/ingestion-runs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_runs.status_code == 200
    runs = r_runs.json()
    assert len(runs) >= 1
    assert runs[0]["source_name"] == "mock"
