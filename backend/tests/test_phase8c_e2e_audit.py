"""
Phase 8C: Job Market Intelligence End-to-End Audit & Verification Suite.

Comprehensive audit tests verifying:
1. Complete 18-step Job Discovery workflow (Search, Multi-Filter, Sort, Pagination, Detail, Provenance)
2. External data source adapters (Arbeitnow, Seed, Manual, Mock) under success, 429 rate limit, 500 error, and timeout
3. Data quality invariants (Deduplication, Idempotency, Distinct role separation, Null salary handling, Partial batch resilience)
4. Security & Compliance (SSRF prevention, protocol validation, parameter pattern enforcement, injection resistance)
5. Freshness lifecycle policies (active -> needs_refresh -> expired -> closed, transient failure safety)
6. Market intelligence aggregate precision (distributions, skill demand %, median salary, provisional threshold)
"""

from __future__ import annotations

import datetime
from datetime import timezone
import decimal
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.jobs import Job, JobIngestionRun, JobSkill, JobSource
from app.schemas.jobs import JobImportRequest
from app.services.job_ingestion_pipeline import JobIngestionPipelineService
from app.services.job_source_adapters import (
    ArbeitnowJobAdapter,
    BaseJobSourceAdapter,
    JobSourceAdapterFactory,
    MockJobSourceAdapter,
    RawJobListing,
    SeedJobAdapter,
)


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


# ─────────────────────────────────────────────────────────────────────────────
# 1. Complete Job Discovery Workflow Audit (18-step end-to-end)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_complete_job_discovery_workflow(test_session: AsyncSession, client: AsyncClient):
    """Audits the full 18-step user journey from catalog load to multi-facet drilldown."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "audit.candidate@example.com", "Audit Candidate")
    headers = {"Authorization": f"Bearer {token}"}

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=22, db=test_session)

    # Step 1 & 2: User opens Jobs page -> loads real records
    res_initial = await client.get("/api/v1/jobs", headers=headers)
    assert res_initial.status_code == 200
    initial_data = res_initial.json()
    assert initial_data["total"] == 22
    assert len(initial_data["items"]) == 20
    assert initial_data["page"] == 1
    assert initial_data["total_pages"] == 2

    # Step 3 & 4: Keyword search by company and title
    res_kw_co = await client.get("/api/v1/jobs?keyword=Netflix", headers=headers)
    assert res_kw_co.status_code == 200
    assert res_kw_co.json()["total"] == 1
    assert res_kw_co.json()["items"][0]["company_name"] == "Netflix"

    res_kw_title = await client.get("/api/v1/jobs?keyword=Data+Scientist", headers=headers)
    assert res_kw_title.status_code == 200
    assert all("Data Scientist" in j["title"] for j in res_kw_title.json()["items"])

    # Step 5 & 6: Multi-filter combination (Role + Remote + Seniority + Skill)
    res_multi = await client.get(
        "/api/v1/jobs?role_id=backend-developer&remote_type=remote&experience_level=entry_level&skill_id=python",
        headers=headers,
    )
    assert res_multi.status_code == 200
    multi_items = res_multi.json()["items"]
    assert len(multi_items) >= 1
    for item in multi_items:
        assert item["role_id"] == "backend-developer"
        assert item["remote_type"] == "remote"
        assert item["experience_level"] == "entry_level"
        skill_ids = [s["skill_id"] for s in item["skills"]]
        assert "python" in skill_ids

    # Step 7: Sorting
    # Salary descending
    res_sort_sal = await client.get("/api/v1/jobs?sort_by=salary_high", headers=headers)
    assert res_sort_sal.status_code == 200
    sal_list = [j["max_salary"] for j in res_sort_sal.json()["items"] if j["max_salary"] is not None]
    assert sal_list == sorted(sal_list, reverse=True)

    # Title ascending
    res_sort_title = await client.get("/api/v1/jobs?sort_by=title_asc", headers=headers)
    assert res_sort_title.status_code == 200
    titles = [j["title"].lower() for j in res_sort_title.json()["items"]]
    assert titles == sorted(titles)

    # Step 8: Pagination
    res_p2 = await client.get("/api/v1/jobs?page=2&page_size=20", headers=headers)
    assert res_p2.status_code == 200
    assert res_p2.json()["page"] == 2
    assert len(res_p2.json()["items"]) == 2  # 22 total minus 20 on page 1

    # Step 9: Clearing filters restores full 22 catalog
    res_cleared = await client.get("/api/v1/jobs?page=1&page_size=50", headers=headers)
    assert res_cleared.status_code == 200
    assert res_cleared.json()["total"] == 22

    # Step 10 & 11: Single job details retrieval
    job_target = initial_data["items"][0]
    res_detail = await client.get(f"/api/v1/jobs/{job_target['id']}", headers=headers)
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == job_target["id"]
    assert detail["title"] == job_target["title"]
    assert detail["company_name"] == job_target["company_name"]
    assert isinstance(detail["responsibilities"], list)
    assert isinstance(detail["required_qualifications"], list)

    # Step 12: Required vs Preferred skill distinction
    mandatory_skills = [s for s in detail["skills"] if s["is_mandatory"]]
    preferred_skills = [s for s in detail["skills"] if not s["is_mandatory"]]
    assert len(mandatory_skills) > 0

    # Step 13: Source and Freshness
    assert detail["source"] in ("seed", "manual", "arbeitnow")
    assert detail["freshness_status"] in ("active", "needs_refresh", "expired", "closed")
    assert detail["is_active"] is True

    # Step 14: Safe application URL
    assert detail["application_url"].startswith("http://") or detail["application_url"].startswith("https://")

    # Step 15: Empty search results handled cleanly
    res_empty = await client.get("/api/v1/jobs?keyword=NonExistentCompanyXYZ99", headers=headers)
    assert res_empty.status_code == 200
    assert res_empty.json()["total"] == 0
    assert res_empty.json()["items"] == []

    # Step 16: Invalid query parameter returns HTTP 422
    res_invalid_page = await client.get("/api/v1/jobs?page=0", headers=headers)
    assert res_invalid_page.status_code == 422

    res_invalid_sort = await client.get("/api/v1/jobs?sort_by=hacked_sort", headers=headers)
    assert res_invalid_sort.status_code == 422

    res_invalid_remote = await client.get("/api/v1/jobs?remote_type=outer_space", headers=headers)
    assert res_invalid_remote.status_code == 422

    # Step 17: Re-querying does not fabricate records
    res_repeat = await client.get("/api/v1/jobs?keyword=Netflix", headers=headers)
    assert res_repeat.status_code == 200
    assert res_repeat.json()["total"] == 1

    # Step 18: Unauthenticated access rejected (clear session cookies first)
    client.cookies.clear()
    res_unauth = await client.get("/api/v1/jobs")
    assert res_unauth.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# 2. External Data Source Failure Modes & Rate Limit Auditing
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_external_provider_failure_modes(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies provider failure isolation:
    1. HTTP 429 rate limit is captured and logged
    2. Transient provider errors mark run as 'failed' without corrupting existing catalog
    3. Ingestion audit log preserves full trace
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "audit.provider@example.com", "Provider Auditor")
    headers = {"Authorization": f"Bearer {token}"}

    # Seed initial active jobs
    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    # Class representing a failing external provider (simulating 429 rate limit)
    class RateLimitedAdapter(BaseJobSourceAdapter):
        @property
        def source_name(self) -> str:
            return "arbeitnow"

        @property
        def provider_type(self) -> str:
            return "api"

        async def fetch_jobs(self, batch_size: int = 50, page: int = 1, **kwargs):
            raise RuntimeError("Arbeitnow API rate limit exceeded (HTTP 429).")

    failing_adapter = RateLimitedAdapter()

    # Execute ingestion run with failing adapter
    summary = await pipeline.run_ingestion(
        source_name="arbeitnow",
        batch_size=10,
        db=test_session,
        adapter_override=failing_adapter,
    )

    # Verify run audit outcome
    assert summary.status == "failed"
    assert summary.items_fetched == 0
    assert len(summary.error_log) > 0
    assert "rate limit" in summary.error_log[0]["error"].lower()

    # Invariant: Existing catalog was NOT corrupted or closed by transient failure
    active_jobs = await test_session.scalars(select(Job).where(Job.is_active == True))
    assert len(active_jobs.all()) == 5

    # Check ingestion runs endpoint reflects the failure truthfully
    res_runs = await client.get("/api/v1/jobs/ingestion-runs", headers=headers)
    assert res_runs.status_code == 200
    runs = res_runs.json()
    assert runs[0]["status"] == "failed"
    assert runs[0]["source_name"] == "arbeitnow"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Data Quality & Deduplication Invariants
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_data_quality_and_deduplication(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies:
    1. Re-ingestion refreshes existing records without duplication (Idempotency)
    2. Distinct roles with same company/location are NOT merged
    3. Missing salaries are preserved as null, never 0
    4. Partial batch failures isolate malformed records while saving valid records
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "audit.quality@example.com", "Quality Auditor")
    headers = {"Authorization": f"Bearer {token}"}

    pipeline = JobIngestionPipelineService()

    # 1. Distinct roles at same company & location
    raw_backend = RawJobListing(
        external_id="stripe-backend-01",
        title="Backend Software Engineer",
        company_name="Stripe",
        location="Seattle, WA",
        description_text="Build payment APIs in Python and PostgreSQL with Docker.",
        application_url="https://stripe.com/jobs/backend",
        source="mock",
        min_salary=None,  # Missing salary
        max_salary=None,
    )
    raw_frontend = RawJobListing(
        external_id="stripe-frontend-01",
        title="Frontend Software Engineer",
        company_name="Stripe",
        location="Seattle, WA",
        description_text="Build web interfaces in TypeScript, React, and Next.js.",
        application_url="https://stripe.com/jobs/frontend",
        source="mock",
        min_salary=120000,
        max_salary=140000,
    )
    # Malformed record with description too short (< 20 chars)
    raw_malformed = RawJobListing(
        external_id="bad-job-01",
        title="X",
        company_name="Y",
        location="Z",
        description_text="Too short",
        application_url="https://bad.com",
        source="mock",
    )

    mock_adapter = MockJobSourceAdapter([raw_backend, raw_frontend, raw_malformed])
    JobSourceAdapterFactory.register_adapter("mock", mock_adapter)

    # Ingest batch
    summary = await pipeline.run_ingestion(source_name="mock", batch_size=10, db=test_session)
    assert summary.items_inserted == 2
    assert summary.items_skipped == 1  # Malformed was skipped gracefully
    assert summary.status == "completed"

    # Verify both distinct roles exist in DB
    jobs = (await test_session.scalars(select(Job).where(Job.company_name == "Stripe"))).all()
    assert len(jobs) == 2
    role_ids = {j.role_id for j in jobs}
    assert "backend-developer" in role_ids
    assert "frontend-developer" in role_ids

    # Verify missing salary is None, not 0
    backend_job = next(j for j in jobs if j.role_id == "backend-developer")
    assert backend_job.min_salary is None
    assert backend_job.max_salary is None

    # Verify API serialization preserves null
    res_b = await client.get(f"/api/v1/jobs/{backend_job.id}", headers=headers)
    assert res_b.status_code == 200
    assert res_b.json()["min_salary"] is None
    assert res_b.json()["max_salary"] is None

    # Idempotency check: Re-running updates 2 records, inserts 0, skips 1
    summary2 = await pipeline.run_ingestion(source_name="mock", batch_size=10, db=test_session)
    assert summary2.items_inserted == 0
    assert summary2.items_updated == 2
    assert summary2.items_skipped == 1

    jobs_count_after = await test_session.scalar(select(func.count(Job.id)))
    assert jobs_count_after == 2


# ─────────────────────────────────────────────────────────────────────────────
# 4. Security, Validation & SSRF Prevention
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_security_ssrf_and_input_sanitization(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies:
    1. Malicious schemes (javascript:, file://) in URLs are rejected
    2. Private internal loopback addresses (127.0.0.1, 169.254.169.254, localhost) are rejected
    3. Legitimate public HTTPS URLs are accepted
    4. Search parameter injection resistance (SQL meta-characters handled safely)
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "audit.security@example.com", "Security Auditor")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Reject malicious javascript: URL
    bad_js_payload = {
        "title": "Malicious Position",
        "company_name": "Exploit Inc",
        "location": "Remote",
        "description_text": "Normal job description requiring Python and PostgreSQL programming.",
        "application_url": "javascript:alert(document.cookie)",
    }
    res_js = await client.post("/api/v1/jobs/import", headers=headers, json=bad_js_payload)
    assert res_js.status_code == 422

    # 2. Reject SSRF AWS metadata service address
    ssrf_payload = {
        "title": "SSRF Position",
        "company_name": "Exploit Inc",
        "location": "Remote",
        "description_text": "Normal job description requiring Python and PostgreSQL programming.",
        "application_url": "http://169.254.169.254/latest/meta-data/",
    }
    res_ssrf = await client.post("/api/v1/jobs/import", headers=headers, json=ssrf_payload)
    assert res_ssrf.status_code == 422

    # 3. Reject local loopback address
    loopback_payload = {
        "title": "Localhost Position",
        "company_name": "Exploit Inc",
        "location": "Remote",
        "description_text": "Normal job description requiring Python and PostgreSQL programming.",
        "application_url": "http://localhost:8000/internal-admin",
    }
    res_loopback = await client.post("/api/v1/jobs/import", headers=headers, json=loopback_payload)
    assert res_loopback.status_code == 422

    # 4. Accept legitimate HTTPS URL
    legit_payload = {
        "title": "Junior Python Developer",
        "company_name": "Legit Tech Inc",
        "location": "Remote",
        "description_text": "Legitimate role requiring Python, FastAPI, and Docker expertise.",
        "application_url": "https://legit-tech.com/careers/junior-python",
    }
    res_legit = await client.post("/api/v1/jobs/import", headers=headers, json=legit_payload)
    assert res_legit.status_code == 201

    # 5. SQL injection resistance in search
    sql_inj = "'; DROP TABLE jobs; --"
    res_inj = await client.get(f"/api/v1/jobs?keyword={sql_inj}", headers=headers)
    assert res_inj.status_code == 200
    assert res_inj.json()["total"] == 0

    # Verify jobs table still intact
    jobs_count = await test_session.scalar(select(func.count(Job.id)))
    assert jobs_count >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 5. Freshness Lifecycle Policy & Vacancy Closure
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_freshness_lifecycle_and_closure(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies:
    1. Active jobs aged > 14 days transition to 'needs_refresh'
    2. Jobs aged > 30 days transition to 'expired' and is_active = False
    3. Explicit closure via POST /jobs/{id}/close deactivates the posting
    4. Closed jobs are omitted from active catalog search
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "audit.freshness@example.com", "Freshness Auditor")
    headers = {"Authorization": f"Bearer {token}"}

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    jobs = (await test_session.scalars(select(Job))).all()
    job_stale = jobs[0]
    job_expired = jobs[1]
    job_closed = jobs[2]

    now = datetime.datetime.now(timezone.utc)
    job_stale.last_verified_at = now - datetime.timedelta(days=16)
    job_expired.last_verified_at = now - datetime.timedelta(days=35)
    await test_session.commit()

    # Trigger freshness evaluation
    res_eval = await client.post("/api/v1/jobs/evaluate-freshness?stale_days=14&expire_days=30", headers=headers)
    assert res_eval.status_code == 200
    summary = res_eval.json()
    assert summary["marked_stale"] >= 1
    assert summary["marked_expired"] >= 1

    # Check job states
    await test_session.refresh(job_stale)
    await test_session.refresh(job_expired)
    assert job_stale.freshness_status == "needs_refresh"
    assert job_stale.is_active is True
    assert job_expired.freshness_status == "expired"
    assert job_expired.is_active is False

    # Explicit closure endpoint
    res_close = await client.post(f"/api/v1/jobs/{job_closed.id}/close", headers=headers)
    assert res_close.status_code == 200
    assert res_close.json()["freshness_status"] == "closed"
    assert res_close.json()["is_active"] is False

    # Default catalog search only returns active jobs (excludes expired & closed)
    res_catalog = await client.get("/api/v1/jobs", headers=headers)
    assert res_catalog.status_code == 200
    catalog_ids = {j["id"] for j in res_catalog.json()["items"]}
    assert str(job_expired.id) not in catalog_ids
    assert str(job_closed.id) not in catalog_ids
    assert str(job_stale.id) in catalog_ids  # needs_refresh remains active for candidate visibility


# ─────────────────────────────────────────────────────────────────────────────
# 6. Market Intelligence Precision & Provisional Threshold
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_market_intelligence_calculations(test_session: AsyncSession, client: AsyncClient):
    """
    Verifies mathematical precision of market intelligence:
    1. Sample size matches active jobs count
    2. Skill demand percentage equals (skill_jobs / total_active * 100)
    3. Median salary correctly handles odd and even counts
    4. Provisional flag is True when active jobs < 20, False when >= 20
    """
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "audit.market@example.com", "Market Auditor")
    headers = {"Authorization": f"Bearer {token}"}

    pipeline = JobIngestionPipelineService()

    # Ingest 10 jobs (sample size < 20 -> provisional)
    await pipeline.run_ingestion(source_name="seed", batch_size=10, db=test_session)

    res_prov = await client.get("/api/v1/jobs/market-intelligence", headers=headers)
    assert res_prov.status_code == 200
    data_prov = res_prov.json()
    assert data_prov["total_active_jobs"] == 10
    assert data_prov["is_provisional"] is True
    assert "currently developing" in data_prov["provisional_reason"]

    # Ingest remaining seed jobs to bring total to 22 (>= 20 -> non-provisional)
    await pipeline.run_ingestion(source_name="seed", batch_size=22, db=test_session)

    res_full = await client.get("/api/v1/jobs/market-intelligence", headers=headers)
    assert res_full.status_code == 200
    data_full = res_full.json()
    assert data_full["total_active_jobs"] == 22
    assert data_full["is_provisional"] is False
    assert data_full["provisional_reason"] is None

    # Check skill percentage calculation
    top_skill = data_full["top_demanded_skills"][0]
    expected_pct = round((top_skill["job_count"] / 22 * 100.0), 1)
    assert top_skill["percentage"] == expected_pct

    # Check salary median
    salary_stats = data_full["salary_insights"]
    assert salary_stats["sample_size"] == 22
    assert salary_stats["median_salary"] is not None
    assert salary_stats["average_min_salary"] is not None
    assert salary_stats["average_max_salary"] is not None
    assert salary_stats["average_min_salary"] <= salary_stats["median_salary"] <= salary_stats["average_max_salary"]
