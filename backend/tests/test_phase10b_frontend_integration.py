"""
Phase 10B Frontend Integration & API Contract Verification Tests.
Verifies the end-to-end integration and API response contracts expected by the
frontend Resume Tailoring & Optimization Studio (Phase 10B).

Validates:
1. Source resume listing and eligible status check (/api/v1/resume)
2. Target job catalog search and listing for tailoring selector (/api/v1/jobs)
3. Tailored resume draft creation from catalog job (/api/v1/resume/{resume_id}/tailor)
4. Tailored resume draft creation from direct job text (/api/v1/resume/{resume_id}/tailor)
5. Tailored version listing with filtering (/api/v1/resume/versions)
6. Tailored version detail retrieval (/api/v1/resume/versions/{version_id})
7. Draft content editing and persistence (/api/v1/resume/versions/{version_id})
8. Explicit human approval gate (/api/v1/resume/versions/{version_id}/approve)
9. Modification lock rejection after approval (409 Conflict)
10. Visual diff endpoint contract (/api/v1/resume/versions/{version_id}/diff)
11. Optimization analysis endpoint contract (/api/v1/resume/versions/{version_id}/analysis)
12. Tailored version deletion (/api/v1/resume/versions/{version_id})
13. Multi-tenant privacy and IDOR protection (403 Forbidden)
14. Source resume immutability verification
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import override_llm_provider, reset_llm_provider
from app.ai.mock_adapter import MockLLMProvider
from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.jobs import Job, JobSource
from app.models.resume import Resume


def mock_ai_tailoring_payload() -> dict:
    return {
        "tailored_resume": {
            "personal_info": {"name": "Alex Mercer", "email": "alex@example.com"},
            "executive_summary": "Senior Python backend engineer specializing in high-throughput payment architectures.",
            "skills": [
                {"name": "Python", "category": "language"},
                {"name": "FastAPI", "category": "framework"},
                {"name": "PostgreSQL", "category": "database"},
                {"name": "Docker", "category": "tool"},
            ],
            "experience": [
                {
                    "employer": "Acme Cloud Corp",
                    "job_title": "Backend Software Engineer",
                    "start_date": "2023-01",
                    "end_date": "2026-01",
                    "is_current": False,
                    "responsibilities": [
                        "Designed and developed high-throughput REST APIs using FastAPI and Python.",
                        "Tuned PostgreSQL database queries to eliminate query latency bottlenecks.",
                    ],
                    "achievements": ["Reduced transaction processing latency by 40%."],
                }
            ],
            "education": [
                {
                    "institution": "State University",
                    "degree": "B.S. in Computer Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2019-09",
                    "end_date": "2023-05",
                }
            ],
            "projects": [
                {
                    "name": "QueryLens",
                    "description": "SQL performance analyzer and index recommender.",
                    "technologies": ["Python", "PostgreSQL", "FastAPI"],
                }
            ],
            "certifications": [],
        },
        "changes": [
            {
                "id": "chg_1",
                "section": "executive_summary",
                "change_type": "rephrasing",
                "original_text": "Backend engineer specializing in distributed systems.",
                "proposed_text": "Senior Python backend engineer specializing in high-throughput payment architectures.",
                "rationale": "Directly emphasizes payment system scale required by Apex Financial.",
                "target_job_requirement": "Architect resilient transaction processing systems",
                "supporting_evidence": "Source resume summary and API experience",
                "needs_clarification": False,
            }
        ],
        "matched_keywords": ["python", "fastapi", "postgresql", "docker"],
        "missing_keywords": ["distributed transactions"],
        "supported_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "missing_requirements": ["Distributed Transactions Mastery"],
        "readability_score": 94.0,
        "formatting_recommendations": ["Highlight PostgreSQL index optimization at the top of experience."],
        "actionable_suggestions": ["Complete the Advanced PostgreSQL Assessment to verify B-tree tuning."],
        "unsupported_claims": [],
    }


@pytest.fixture(autouse=True)
async def seed_base_data(test_session: AsyncSession):
    """Seeds canonical roles, skills, and job sources required for relational integrity."""
    await seed_skill_taxonomy_and_roles(test_session)
    for name, p_type in [("seed", "seed"), ("manual", "manual"), ("mock", "mock")]:
        source = await test_session.scalar(select(JobSource).where(JobSource.name == name))
        if not source:
            source = JobSource(
                name=name,
                provider_type=p_type,
                is_active=True,
            )
            test_session.add(source)
    await test_session.commit()

    mock = MockLLMProvider()
    mock.set_structured_response(mock_ai_tailoring_payload())
    override_llm_provider(mock)
    yield
    reset_llm_provider()


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


async def create_parsed_resume(test_session: AsyncSession, user_id: uuid.UUID) -> Resume:
    resume = Resume(
        id=uuid.uuid4(),
        user_id=user_id,
        file_name="Alex_Mercer_Backend_Resume.pdf",
        storage_path=f"uploads/{uuid.uuid4()}.pdf",
        file_size_bytes=42000,
        mime_type="application/pdf",
        status="parsed",
        is_primary=True,
        parsed_text="Alex Mercer. Experienced backend engineer specializing in Python and PostgreSQL.",
        extracted_data={
            "personal_info": {"name": "Alex Mercer", "email": "alex@example.com"},
            "executive_summary": "Backend engineer specializing in distributed systems.",
            "skills": [
                {"name": "Python", "category": "language"},
                {"name": "FastAPI", "category": "framework"},
                {"name": "PostgreSQL", "category": "database"},
                {"name": "Docker", "category": "tool"},
            ],
            "experience": [
                {
                    "employer": "Acme Cloud Corp",
                    "job_title": "Backend Software Engineer",
                    "start_date": "2023-01",
                    "end_date": "2026-01",
                    "is_current": False,
                    "responsibilities": [
                        "Designed and developed REST APIs using FastAPI and Python.",
                        "Tuned PostgreSQL database queries to improve performance.",
                    ],
                    "achievements": ["Reduced latency by 40%."],
                }
            ],
            "education": [
                {
                    "institution": "State University",
                    "degree": "B.S. in Computer Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2019-09",
                    "end_date": "2023-05",
                }
            ],
            "projects": [
                {
                    "name": "QueryLens",
                    "description": "SQL performance analyzer and index recommender.",
                    "technologies": ["Python", "PostgreSQL", "FastAPI"],
                }
            ],
        },
    )
    test_session.add(resume)
    await test_session.commit()
    await test_session.refresh(resume)
    return resume


async def create_target_job(test_session: AsyncSession) -> Job:
    job = Job(
        id=uuid.uuid4(),
        external_id=f"job_{uuid.uuid4().hex[:8]}",
        source="seed",
        source_url="https://example.com/jobs/apex-backend",
        title="Senior Python Backend Engineer",
        normalized_title="senior python backend engineer",
        company_name="Apex Financial Systems",
        location="Remote, US",
        normalized_location="remote",
        employment_type="full_time",
        remote_type="remote",
        role_id="backend-developer",
        experience_level="mid",
        min_salary=150000,
        max_salary=185000,
        currency="USD",
        description_markdown=(
            "Apex Financial Systems is seeking a Senior Python Backend Engineer to architect "
            "resilient transaction processing systems. Key requirements include mastery of Python, "
            "FastAPI, relational database design with PostgreSQL, high-throughput indexing, "
            "and asynchronous event workflows."
        ),
        responsibilities=["Build high-volume payment processing pipelines.", "Maintain database reliability."],
        required_qualifications=["Proficiency in Python and PostgreSQL.", "Docker container orchestration."],
        preferred_qualifications=["FastAPI experience.", "Knowledge of distributed transactions."],
        application_url="https://example.com/apply",
        is_active=True,
        freshness_status="active",
    )
    test_session.add(job)
    await test_session.commit()
    await test_session.refresh(job)
    return job


@pytest.mark.asyncio
async def test_frontend_full_tailoring_lifecycle_e2e(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """
    Simulates the exact Phase 10B frontend user journey:
    1. Authenticates candidate
    2. Loads source resumes and target jobs
    3. Triggers tailoring draft generation
    4. Retrieves visual diff and optimization analysis
    5. Edits draft wording and persists changes
    6. Verifies original resume immutability
    7. Submits explicit human approval
    8. Verifies editing lock after approval (409 Conflict)
    9. Deletes version cleanly
    """
    token, user_id = await register_and_login(client, "phase10b_user@example.com", "Alex Mercer")
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Create master resume and target job in database
    master_resume = await create_parsed_resume(test_session, user_id)
    target_job = await create_target_job(test_session)

    # Step 2: Frontend checks source resumes
    r_list = await client.get("/api/v1/resume", headers=headers)
    assert r_list.status_code == 200
    resumes_data = r_list.json()["resumes"]
    assert len(resumes_data) >= 1
    assert any(r["id"] == str(master_resume.id) and r["status"] == "parsed" for r in resumes_data)

    # Step 3: Frontend searches target jobs
    r_jobs = await client.get("/api/v1/jobs?keyword=Python", headers=headers)
    assert r_jobs.status_code == 200
    jobs_data = r_jobs.json()["items"]
    assert len(jobs_data) >= 1
    assert any(j["id"] == str(target_job.id) for j in jobs_data)

    # Step 4: Frontend initiates tailoring draft generation
    tailor_payload = {
        "job_id": str(target_job.id),
        "target_emphasis": ["PostgreSQL indexing", "FastAPI transaction processing"],
        "user_notes": "Emphasize high throughput payment pipeline",
    }
    r_tailor = await client.post(
        f"/api/v1/resume/{master_resume.id}/tailor",
        json=tailor_payload,
        headers=headers,
    )
    assert r_tailor.status_code == 201
    tailored_draft = r_tailor.json()
    version_id = tailored_draft["id"]

    assert tailored_draft["resume_id"] == str(master_resume.id)
    assert tailored_draft["target_job_id"] == str(target_job.id)
    assert tailored_draft["version_number"] == 1
    assert tailored_draft["status"] == "draft"
    assert tailored_draft["anti_hallucination_verified"] is True
    assert tailored_draft["approved_at"] is None
    assert "diff_summary" in tailored_draft
    assert "tailored_content" in tailored_draft

    # Step 5: Frontend lists tailored versions
    r_versions = await client.get("/api/v1/resume/versions", headers=headers)
    assert r_versions.status_code == 200
    v_items = r_versions.json()["items"]
    assert len(v_items) >= 1
    target_v = next((v for v in v_items if v["id"] == version_id), None)
    assert target_v is not None
    assert target_v["status"] == "draft"
    assert target_v["job_title"] == target_job.title
    assert target_v["company_name"] == target_job.company_name

    # Step 6: Frontend loads specific version detail
    r_detail = await client.get(f"/api/v1/resume/versions/{version_id}", headers=headers)
    assert r_detail.status_code == 200
    v_detail = r_detail.json()
    assert v_detail["id"] == version_id
    assert v_detail["status"] == "draft"

    # Step 7: Frontend inspects visual diff endpoint
    r_diff = await client.get(f"/api/v1/resume/versions/{version_id}/diff", headers=headers)
    assert r_diff.status_code == 200
    diff_data = r_diff.json()
    assert diff_data["version_id"] == version_id
    assert "changes" in diff_data
    assert isinstance(diff_data["changes"], list)

    # Step 8: Frontend inspects optimization analysis endpoint
    r_analysis = await client.get(f"/api/v1/resume/versions/{version_id}/analysis", headers=headers)
    assert r_analysis.status_code == 200
    analysis_data = r_analysis.json()
    assert analysis_data["version_id"] == version_id
    assert "optimization_analysis" in analysis_data
    assert "keyword_coverage" in analysis_data["optimization_analysis"]
    assert analysis_data["anti_hallucination_verified"] is True

    # Step 9: Frontend user edits draft content
    updated_content = dict(v_detail["tailored_content"])
    updated_content["executive_summary"] = (
        "User-edited: Senior Python backend engineer with 5+ years of experience tuning PostgreSQL."
    )
    r_update = await client.put(
        f"/api/v1/resume/versions/{version_id}",
        json={"tailored_content": updated_content, "user_notes": "Candidate updated summary manually"},
        headers=headers,
    )
    assert r_update.status_code == 200
    updated_draft = r_update.json()
    assert updated_draft["tailored_content"]["executive_summary"] == updated_content["executive_summary"]

    # Step 10: Original resume immutability check
    refetched_master = await test_session.get(Resume, master_resume.id)
    assert refetched_master.status == "parsed"
    assert "User-edited" not in refetched_master.parsed_text
    assert refetched_master.extracted_data["executive_summary"] == "Backend engineer specializing in distributed systems."

    # Step 11: Candidate explicitly approves version via Human Approval Gateway
    r_approve = await client.post(
        f"/api/v1/resume/versions/{version_id}/approve",
        json={
            "user_confirmation": True,
            "accepted_sections": ["executive_summary", "skills", "experience"],
        },
        headers=headers,
    )
    assert r_approve.status_code == 200
    approved_ver = r_approve.json()
    assert approved_ver["status"] == "approved"
    assert approved_ver["approved_at"] is not None

    # Step 12: Attempting to edit an approved version is rejected (409 Conflict)
    r_edit_after_lock = await client.put(
        f"/api/v1/resume/versions/{version_id}",
        json={"tailored_content": updated_content},
        headers=headers,
    )
    assert r_edit_after_lock.status_code == 409

    # Step 13: Delete version permanently
    r_delete = await client.delete(f"/api/v1/resume/versions/{version_id}", headers=headers)
    assert r_delete.status_code == 204

    # Verify version no longer exists
    r_get_deleted = await client.get(f"/api/v1/resume/versions/{version_id}", headers=headers)
    assert r_get_deleted.status_code == 404


@pytest.mark.asyncio
async def test_frontend_cross_user_isolation(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """
    Verifies that Candidate B cannot view, modify, approve, or delete Candidate A's tailored version.
    """
    token_a, user_a = await register_and_login(client, "user_a@example.com", "Alice A")
    token_b, user_b = await register_and_login(client, "user_b@example.com", "Bob B")

    resume_a = await create_parsed_resume(test_session, user_a)
    job = await create_target_job(test_session)

    # Candidate A creates draft
    r_create = await client.post(
        f"/api/v1/resume/{resume_a.id}/tailor",
        json={"job_id": str(job.id)},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r_create.status_code == 201
    version_id = r_create.json()["id"]

    # Candidate B tries to view Candidate A's version -> 403 Forbidden
    r_b_view = await client.get(
        f"/api/v1/resume/versions/{version_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_b_view.status_code == 403

    # Candidate B tries to update Candidate A's version -> 403 Forbidden
    r_b_edit = await client.put(
        f"/api/v1/resume/versions/{version_id}",
        json={"user_notes": "Malicious edit"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_b_edit.status_code == 403

    # Candidate B tries to approve Candidate A's version -> 403 Forbidden
    r_b_approve = await client.post(
        f"/api/v1/resume/versions/{version_id}/approve",
        json={"user_confirmation": True, "accepted_sections": ["skills"]},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_b_approve.status_code == 403

    # Candidate B tries to delete Candidate A's version -> 403 Forbidden
    r_b_delete = await client.delete(
        f"/api/v1/resume/versions/{version_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_b_delete.status_code == 403


@pytest.mark.asyncio
async def test_frontend_direct_text_job_tailoring(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """Verifies tailoring via direct pasted job text input from the frontend wizard."""
    token, user_id = await register_and_login(client, "direct_text@example.com", "Direct Candidate")
    resume = await create_parsed_resume(test_session, user_id)

    payload = {
        "job_title": "Staff Infrastructure Engineer",
        "company_name": "Linear Orbit",
        "job_description_text": (
            "Linear Orbit is building the next-generation issue tracking and developer platform. "
            "We are seeking a Staff Infrastructure Engineer with deep experience in Python, "
            "PostgreSQL database optimization, Redis caching tiers, and resilient cloud architectures."
        ),
        "target_emphasis": ["PostgreSQL optimization", "Redis caching"],
        "user_notes": "Focus on high reliability and developer velocity",
    }
    r = await client.post(
        f"/api/v1/resume/{resume.id}/tailor",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    res = r.json()
    assert res["status"] == "draft"
    assert res["version_number"] == 1


@pytest.mark.asyncio
async def test_frontend_short_job_description_validation(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """Verifies that direct job text shorter than 50 characters is rejected by backend schema validation (422)."""
    token, user_id = await register_and_login(client, "short_desc@example.com", "Short Candidate")
    resume = await create_parsed_resume(test_session, user_id)

    payload = {
        "job_title": "Engineer",
        "company_name": "TooShortCorp",
        "job_description_text": "Too short job description.",  # < 50 chars
    }
    r = await client.post(
        f"/api/v1/resume/{resume.id}/tailor",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_frontend_approval_without_confirmation_rejected(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """Verifies that approving without explicit user_confirmation is rejected by the Human Approval Gateway."""
    token, user_id = await register_and_login(client, "unconfirmed@example.com", "Unconfirmed Candidate")
    resume = await create_parsed_resume(test_session, user_id)
    job = await create_target_job(test_session)

    r_create = await client.post(
        f"/api/v1/resume/{resume.id}/tailor",
        json={"job_id": str(job.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_create.status_code == 201
    version_id = r_create.json()["id"]

    # Attempt approval with user_confirmation = False
    r_reject = await client.post(
        f"/api/v1/resume/versions/{version_id}/approve",
        json={"user_confirmation": False, "accepted_sections": ["skills"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_reject.status_code == 422


@pytest.mark.asyncio
async def test_frontend_version_filtering_by_status(
    test_session: AsyncSession,
    client: AsyncClient,
):
    """Verifies filtering tailored resume versions by status ('draft' vs 'approved')."""
    token, user_id = await register_and_login(client, "filter_user@example.com", "Filter Candidate")
    resume = await create_parsed_resume(test_session, user_id)
    job = await create_target_job(test_session)
    headers = {"Authorization": f"Bearer {token}"}

    # Create draft 1
    r1 = await client.post(f"/api/v1/resume/{resume.id}/tailor", json={"job_id": str(job.id)}, headers=headers)
    assert r1.status_code == 201
    v1_id = r1.json()["id"]

    # Approve draft 1
    await client.post(
        f"/api/v1/resume/versions/{v1_id}/approve",
        json={"user_confirmation": True, "accepted_sections": ["executive_summary"]},
        headers=headers,
    )

    # Create draft 2 (remains draft)
    r2 = await client.post(f"/api/v1/resume/{resume.id}/tailor", json={"job_id": str(job.id)}, headers=headers)
    assert r2.status_code == 201
    v2_id = r2.json()["id"]

    # Filter approved
    r_app = await client.get("/api/v1/resume/versions?status=approved", headers=headers)
    assert r_app.status_code == 200
    app_items = r_app.json()["items"]
    assert len(app_items) == 1
    assert app_items[0]["id"] == v1_id
    assert app_items[0]["status"] == "approved"

    # Filter draft
    r_draft = await client.get("/api/v1/resume/versions?status=draft", headers=headers)
    assert r_draft.status_code == 200
    draft_items = r_draft.json()["items"]
    assert len(draft_items) == 1
    assert draft_items[0]["id"] == v2_id
    assert draft_items[0]["status"] == "draft"

