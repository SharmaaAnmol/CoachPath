"""
Comprehensive Test Suite for Phase 9A: Intelligent Job Matching Engine.
Covers deterministic scoring, canonical skill matching, provenance weighting,
experience & project alignment, location flexibility, explainability drawers,
persistence, staleness & recalculation, ranking, pagination, security, and authorization.
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
from app.models.career import CareerProfile, Experience, Project, Role
from app.models.jobs import Job, JobMatch, JobSkill
from app.models.skills import Skill, UserSkill
from app.schemas.job_matching import SkillMatchClassification
from app.services.job_ingestion_pipeline import JobIngestionPipelineService
from app.services.job_matching_engine import JobMatchingEngine


# ─────────────────────────────────────────────────────────────────────────────
# Test Fixtures & Setup Helpers
# ─────────────────────────────────────────────────────────────────────────────

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
    target_locations: list[str] | None = None,
    years_of_experience: float = 2.0,
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.put(
        "/api/v1/profile/career-goals",
        headers=headers,
        json={
            "primary_role_id": target_role_id,
            "career_stage": "early_career",
            "work_preference": work_preference,
            "target_locations": target_locations or ["San Francisco, CA"],
        },
    )
    assert r.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# 1. Unit & Formula Tests: Determinism, Provenance, Weights
# ─────────────────────────────────────────────────────────────────────────────

def test_deterministic_scoring_repeatability():
    """Identical candidate and job inputs must produce identical scores across executions."""
    engine = JobMatchingEngine()

    # Create dummy mock objects
    job = Job(
        id=uuid.uuid4(),
        title="Junior Backend Engineer",
        company_name="Acme Corp",
        location="Remote",
        remote_type="remote",
        role_id="backend-developer",
        experience_level="entry_level",
        freshness_status="active",
        is_active=True,
    )
    job.skills = [
        JobSkill(skill_id="python", is_mandatory=True),
        JobSkill(skill_id="postgresql", is_mandatory=True),
        JobSkill(skill_id="docker", is_mandatory=False),
    ]

    profile = CareerProfile(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        primary_role_id="backend-developer",
        career_stage="early_career",
        work_preference="remote",
        target_locations=["Remote"],
        years_of_experience=decimal.Decimal("1.5"),
    )
    profile.user_skills = [
        UserSkill(
            skill_id="python",
            confidence_score=decimal.Decimal("0.90"),
            proficiency_tier="proficient",
            primary_source="assessment",
            is_verified=True,
        ),
        UserSkill(
            skill_id="postgresql",
            confidence_score=decimal.Decimal("0.80"),
            proficiency_tier="demonstrated",
            primary_source="extracted",
            is_verified=False,
        ),
    ]
    profile.experience = []
    profile.projects = [
        Project(
            title="API Backend",
            description="Built with Python and Postgres",
            technologies=["python", "postgresql"],
            github_url="https://github.com/test/repo",
        )
    ]

    # Compute twice
    res1 = engine.compute_match(profile, job)
    res2 = engine.compute_match(profile, job)

    assert res1["overall_score"] == res2["overall_score"]
    assert res1["skill_score"] == res2["skill_score"]
    assert res1["experience_score"] == res2["experience_score"]
    assert res1["project_score"] == res2["project_score"]
    assert res1["location_score"] == res2["location_score"]
    assert res1["preference_score"] == res2["preference_score"]
    assert res1["evidence_coverage"] == res2["evidence_coverage"]
    assert res1["matched_skills"] == res2["matched_skills"]
    assert res1["missing_skills"] == res2["missing_skills"]
    assert res1["unknown_skills"] == res2["unknown_skills"]


def test_differentiate_required_vs_preferred_skills():
    """Missing required skills must penalize heavily (80% weight), missing preferred lightly (20%)."""
    engine = JobMatchingEngine()

    job = Job(
        id=uuid.uuid4(),
        title="Software Engineer",
        company_name="TechCo",
        location="Remote",
        remote_type="remote",
        role_id="backend-developer",
        experience_level="entry_level",
    )
    job.skills = [
        JobSkill(skill_id="python", is_mandatory=True),
        JobSkill(skill_id="fastapi", is_mandatory=True),
        JobSkill(skill_id="kubernetes", is_mandatory=False),  # preferred
    ]

    profile_has_required = CareerProfile(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        primary_role_id="backend-developer",
        years_of_experience=decimal.Decimal("1.0"),
        work_preference="remote",
    )
    profile_has_required.user_skills = [
        UserSkill(skill_id="python", confidence_score=decimal.Decimal("0.90"), proficiency_tier="proficient", primary_source="assessment", is_verified=True),
        UserSkill(skill_id="fastapi", confidence_score=decimal.Decimal("0.85"), proficiency_tier="proficient", primary_source="extracted", is_verified=False),
    ]
    profile_has_required.experience = []
    profile_has_required.projects = []

    res_req = engine.compute_match(profile_has_required, job)
    # Required skills matched, only preferred missing -> high skill score
    assert res_req["skill_score"] >= 60.0
    assert "Kubernetes" in res_req["unknown_skills"]

    # Candidate with only preferred skill, missing both required
    profile_only_pref = CareerProfile(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        primary_role_id="backend-developer",
        years_of_experience=decimal.Decimal("1.0"),
        work_preference="remote",
    )
    profile_only_pref.user_skills = [
        UserSkill(skill_id="kubernetes", confidence_score=decimal.Decimal("0.90"), proficiency_tier="proficient", primary_source="assessment", is_verified=True),
    ]
    profile_only_pref.experience = []
    profile_only_pref.projects = []

    res_pref = engine.compute_match(profile_only_pref, job)
    # Both required missing -> skill score should be low
    assert res_pref["skill_score"] <= 25.0
    assert "Python" in res_pref["missing_skills"]
    assert "Fastapi" in res_pref["missing_skills"]


def test_provenance_weighting_hierarchy():
    """Assessment evidence (1.0) scores higher than project evidence (0.85) than self-reported (0.60)."""
    engine = JobMatchingEngine()

    job = Job(id=uuid.uuid4(), title="Python Dev", company_name="C", location="Remote", remote_type="remote", role_id="backend-developer", experience_level="entry_level")
    job.skills = [JobSkill(skill_id="python", is_mandatory=True)]

    def make_profile(source: str, tier: str) -> CareerProfile:
        p = CareerProfile(id=uuid.uuid4(), user_id=uuid.uuid4(), primary_role_id="backend-developer", work_preference="remote")
        p.user_skills = [
            UserSkill(skill_id="python", confidence_score=decimal.Decimal("0.80"), proficiency_tier=tier, primary_source=source, is_verified=(source == "assessment"))
        ]
        p.experience = []
        p.projects = []
        return p

    asmt_res = engine.compute_match(make_profile("assessment", "mastered"), job)
    proj_res = engine.compute_match(make_profile("project_evidence", "mastered"), job)
    self_res = engine.compute_match(make_profile("self_reported", "unverified"), job)

    assert asmt_res["skill_score"] > proj_res["skill_score"]
    assert proj_res["skill_score"] > self_res["skill_score"]


def test_location_and_workplace_compatibility_rules():
    """Tests remote match, onsite mismatch, and target location filtering."""
    engine = JobMatchingEngine()

    remote_job = Job(id=uuid.uuid4(), title="Dev", company_name="A", location="San Francisco, CA", remote_type="remote", role_id="backend-developer", experience_level="entry_level")
    onsite_job = Job(id=uuid.uuid4(), title="Dev", company_name="B", location="Seattle, WA", remote_type="onsite", role_id="backend-developer", experience_level="entry_level")

    # Remote candidate
    remote_cand = CareerProfile(
        id=uuid.uuid4(), user_id=uuid.uuid4(), primary_role_id="backend-developer",
        work_preference="remote", target_locations=["New York, NY"]
    )
    remote_cand.user_skills = []
    remote_cand.experience = []
    remote_cand.projects = []

    res_rem = engine.compute_match(remote_cand, remote_job)
    assert res_rem["location_score"] == 100.0

    res_onsite = engine.compute_match(remote_cand, onsite_job)
    # Remote candidate on onsite job is a strict mismatch
    assert res_onsite["location_score"] == 25.0

    # Hybrid candidate with matching target location
    hybrid_seattle_cand = CareerProfile(
        id=uuid.uuid4(), user_id=uuid.uuid4(), primary_role_id="backend-developer",
        work_preference="hybrid", target_locations=["Seattle, WA"]
    )
    hybrid_seattle_cand.user_skills = []
    hybrid_seattle_cand.experience = []
    hybrid_seattle_cand.projects = []

    res_hybrid_match = engine.compute_match(hybrid_seattle_cand, onsite_job)
    assert res_hybrid_match["location_score"] == 100.0


def test_experience_alignment_levels():
    """Tests 0 years for entry level vs mid level."""
    engine = JobMatchingEngine()

    entry_job = Job(id=uuid.uuid4(), title="Junior Dev", company_name="A", location="Remote", remote_type="remote", role_id="backend-developer", experience_level="entry_level")
    mid_job = Job(id=uuid.uuid4(), title="Mid Dev", company_name="B", location="Remote", remote_type="remote", role_id="backend-developer", experience_level="mid")

    zero_exp_cand = CareerProfile(
        id=uuid.uuid4(), user_id=uuid.uuid4(), primary_role_id="backend-developer",
        years_of_experience=decimal.Decimal("0.0"), work_preference="remote"
    )
    zero_exp_cand.user_skills = []
    zero_exp_cand.experience = []
    zero_exp_cand.projects = []

    res_entry = engine.compute_match(zero_exp_cand, entry_job)
    assert res_entry["experience_score"] == 100.0

    res_mid = engine.compute_match(zero_exp_cand, mid_job)
    assert res_mid["experience_score"] <= 30.0


def test_provisional_confidence_flag():
    """Sparse profile with minimal data receives low evidence coverage (< 40%) and is flagged provisional."""
    engine = JobMatchingEngine()

    job = Job(id=uuid.uuid4(), title="Dev", company_name="A", location="Remote", remote_type="remote", role_id="backend-developer", experience_level="entry_level")
    job.skills = []

    sparse_cand = CareerProfile(
        id=uuid.uuid4(), user_id=uuid.uuid4(), primary_role_id=None,
        years_of_experience=decimal.Decimal("0.0"), work_preference=None
    )
    sparse_cand.user_skills = []
    sparse_cand.experience = []
    sparse_cand.projects = []

    res = engine.compute_match(sparse_cand, job)
    assert res["evidence_coverage"] < 40.0
    assert res["is_provisional"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 2. Integration Tests: API Endpoints, DB Seeding & Recommendations Ranking
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_job_matching_unauthenticated_rejected(client: AsyncClient):
    """Unauthenticated access to any matching endpoint must return HTTP 401."""
    random_id = uuid.uuid4()
    assert (await client.get("/api/v1/jobs/recommendations")).status_code == 401
    assert (await client.get("/api/v1/jobs/matches")).status_code == 401
    assert (await client.post("/api/v1/jobs/matches/refresh")).status_code == 401
    assert (await client.get(f"/api/v1/jobs/{random_id}/match")).status_code == 401
    assert (await client.get(f"/api/v1/jobs/{random_id}/match-explanation")).status_code == 401
    assert (await client.post(f"/api/v1/jobs/{random_id}/match/recalculate")).status_code == 401


@pytest.mark.asyncio
async def test_recommendations_ranking_and_filters(test_session: AsyncSession, client: AsyncClient):
    """Verifies that recommendations return jobs sorted descending by match score with valid filters."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    # Ingest benchmark seed catalog (22 jobs)
    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=22, db=test_session)

    token, user_id = await register_and_login(client, "ranking.candidate@test.com", "Ranking Candidate")
    headers = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(
        client, token, target_role_id="backend-developer", work_preference="remote", target_locations=["San Francisco, CA"]
    )

    # Add verified Python assessment evidence to candidate profile
    profile_stmt = select(CareerProfile).where(CareerProfile.user_id == user_id)
    profile = await test_session.scalar(profile_stmt)
    assert profile is not None

    profile.years_of_experience = decimal.Decimal("2.5")
    test_session.add(
        UserSkill(
            career_profile_id=profile.id,
            skill_id="python",
            confidence_score=decimal.Decimal("0.95"),
            proficiency_tier="mastered",
            primary_source="assessment",
            is_verified=True,
        )
    )
    test_session.add(
        UserSkill(
            career_profile_id=profile.id,
            skill_id="postgresql",
            confidence_score=decimal.Decimal("0.85"),
            proficiency_tier="proficient",
            primary_source="extracted",
            is_verified=False,
        )
    )
    test_session.add(
        Project(
            career_profile_id=profile.id,
            title="FastAPI Microservice",
            description="Scalable REST API with PostgreSQL and Docker",
            technologies=["python", "postgresql", "fastapi", "docker"],
            github_url="https://github.com/candidate/fastapi-app",
        )
    )
    await test_session.commit()

    # 1. Fetch Recommendations
    res = await client.get("/api/v1/jobs/recommendations", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    items = data["items"]
    assert len(items) > 0

    # Verify descending sort order
    scores = [it["match"]["overall_score"] for it in items]
    assert scores == sorted(scores, reverse=True)

    # Top match should have strong Python & backend alignment
    top_match = items[0]["match"]
    assert top_match["overall_score"] >= 50.0
    assert "Python" in top_match["matched_skills"] or "python" in [s.lower() for s in top_match["matched_skills"]]

    # 2. Filter by min_score
    res_min = await client.get("/api/v1/jobs/recommendations?min_score=50.0", headers=headers)
    assert res_min.status_code == 200
    assert len(res_min.json()["items"]) >= 1
    for it in res_min.json()["items"]:
        assert it["match"]["overall_score"] >= 50.0

    # 3. Filter by role_id
    res_role = await client.get("/api/v1/jobs/recommendations?role_id=backend-developer", headers=headers)
    assert res_role.status_code == 200
    for it in res_role.json()["items"]:
        assert it["job"]["role_id"] == "backend-developer"

    # 4. Filter by remote_type
    res_remote = await client.get("/api/v1/jobs/recommendations?remote_type=remote", headers=headers)
    assert res_remote.status_code == 200
    for it in res_remote.json()["items"]:
        assert it["job"]["remote_type"] == "remote"

    # 5. Pagination
    res_p1 = await client.get("/api/v1/jobs/recommendations?page=1&page_size=5", headers=headers)
    res_p2 = await client.get("/api/v1/jobs/recommendations?page=2&page_size=5", headers=headers)
    assert res_p1.status_code == 200
    assert res_p2.status_code == 200
    assert len(res_p1.json()["items"]) == 5
    assert res_p1.json()["page"] == 1
    assert res_p2.json()["page"] == 2
    # Distinct job IDs across pages
    ids_p1 = [x["job"]["id"] for x in res_p1.json()["items"]]
    ids_p2 = [x["job"]["id"] for x in res_p2.json()["items"]]
    assert set(ids_p1).isdisjoint(set(ids_p2))


@pytest.mark.asyncio
async def test_single_job_match_and_drawer_explanation(test_session: AsyncSession, client: AsyncClient):
    """Verifies single job match computation and the Section 8.2 explainability drawer endpoint."""
    await seed_skill_taxonomy_and_roles(test_session)
    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    token, user_id = await register_and_login(client, "drawer.candidate@test.com", "Drawer Candidate")
    headers = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token, target_role_id="backend-developer")

    # Pick first backend job
    job = await test_session.scalar(select(Job).where(Job.role_id == "backend-developer"))
    assert job is not None

    # 1. Fetch match details
    r_match = await client.get(f"/api/v1/jobs/{job.id}/match", headers=headers)
    assert r_match.status_code == 200
    match_data = r_match.json()
    assert match_data["job_id"] == str(job.id)
    assert "breakdown" in match_data
    assert "skills_detail" in match_data
    assert "explanation" in match_data
    assert "summary" in match_data["explanation"]
    assert isinstance(match_data["explanation"]["strengths"], list)
    assert isinstance(match_data["explanation"]["gaps"], list)

    # 2. Fetch drawer explanation
    r_drawer = await client.get(f"/api/v1/jobs/{job.id}/match-explanation", headers=headers)
    assert r_drawer.status_code == 200
    drawer_data = r_drawer.json()
    assert drawer_data["job_id"] == str(job.id)
    assert "hiring_rationale" in drawer_data
    assert "breakdown" in drawer_data
    assert "skill_score" in drawer_data["breakdown"]
    assert "experience_score" in drawer_data["breakdown"]
    assert "matched_skills" in drawer_data
    assert "missing_skills" in drawer_data


@pytest.mark.asyncio
async def test_recalculation_after_assessment_evidence(test_session: AsyncSession, client: AsyncClient):
    """When a candidate passes a new assessment, recalculating match increases score and updates evidence."""
    await seed_skill_taxonomy_and_roles(test_session)
    await seed_diagnostic_assessments(test_session)

    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    token, user_id = await register_and_login(client, "recalc.candidate@test.com", "Recalc Candidate")
    headers = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token, target_role_id="backend-developer")

    job = await test_session.scalar(select(Job).where(Job.role_id == "backend-developer"))
    assert job is not None

    # Initial score with empty profile
    r_initial = await client.get(f"/api/v1/jobs/{job.id}/match", headers=headers)
    assert r_initial.status_code == 200
    initial_score = r_initial.json()["overall_score"]

    # Candidate completes diagnostic assessment for python with high score
    asmt = await test_session.scalar(select(Assessment).where(Assessment.skill_id == "python"))
    assert asmt is not None

    attempt = AssessmentAttempt(
        user_id=user_id,
        assessment_id=asmt.id,
        status="completed",
        score_percentage=decimal.Decimal("95.0"),
        passed=True,
        completed_at=datetime.now(timezone.utc),
    )
    test_session.add(attempt)
    await test_session.commit()

    # Force recalculation
    r_recalc = await client.post(
        f"/api/v1/jobs/{job.id}/match/recalculate",
        headers=headers,
        json={"force": True},
    )
    assert r_recalc.status_code == 200
    recalc_score = r_recalc.json()["overall_score"]

    # Score should have increased with verified assessment evidence
    assert recalc_score > initial_score
    assert any(
        s["skill_id"] == "python" and s["user_evidence_source"] == "assessment"
        for s in r_recalc.json()["skills_detail"]
    )


@pytest.mark.asyncio
async def test_batch_refresh_user_matches(test_session: AsyncSession, client: AsyncClient):
    """Batch refresh endpoint invalidates stale results and updates matches."""
    await seed_skill_taxonomy_and_roles(test_session)
    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    token, _ = await register_and_login(client, "refresh.candidate@test.com", "Refresh Candidate")
    headers = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token, target_role_id="backend-developer")

    res = await client.post("/api/v1/jobs/matches/refresh", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["recalculated_count"] >= 1


@pytest.mark.asyncio
async def test_nonexistent_job_returns_404(test_session: AsyncSession, client: AsyncClient):
    """Querying match for non-existent job UUID returns HTTP 404."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "notfound.candidate@test.com", "Not Found Candidate")
    headers = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token)

    fake_id = uuid.uuid4()
    r = await client.get(f"/api/v1/jobs/{fake_id}/match", headers=headers)
    assert r.status_code == 404
    assert "Job" in r.json()["error"]["message"]


@pytest.mark.asyncio
async def test_empty_job_catalog_returns_empty_recommendations(test_session: AsyncSession, client: AsyncClient):
    """When catalog is empty, returns honest empty state rather than fabricated jobs."""
    await seed_skill_taxonomy_and_roles(test_session)
    token, _ = await register_and_login(client, "empty.candidate@test.com", "Empty Candidate")
    headers = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token)

    r = await client.get("/api/v1/jobs/recommendations", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_cross_user_isolation(test_session: AsyncSession, client: AsyncClient):
    """User B cannot access or view User A's match records; calculations are strictly isolated."""
    await seed_skill_taxonomy_and_roles(test_session)
    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=3, db=test_session)

    # Register User A and User B
    token_a, user_a_id = await register_and_login(client, "user.a@test.com", "User Alpha")
    token_b, user_b_id = await register_and_login(client, "user.b@test.com", "User Beta")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    await setup_candidate_profile(client, token_a, target_role_id="backend-developer")
    await setup_candidate_profile(client, token_b, target_role_id="data-scientist")

    job = await test_session.scalar(select(Job))
    assert job is not None

    # User A calculates match
    r_a = await client.get(f"/api/v1/jobs/{job.id}/match", headers=headers_a)
    assert r_a.status_code == 200
    match_a = r_a.json()

    # User B lists matches -> should be empty
    r_b_list = await client.get("/api/v1/jobs/matches", headers=headers_b)
    assert r_b_list.status_code == 200
    assert len(r_b_list.json()) == 0

    # User B calculates match on same job -> gets their own separate match record
    r_b = await client.get(f"/api/v1/jobs/{job.id}/match", headers=headers_b)
    assert r_b.status_code == 200
    match_b = r_b.json()

    # Profile IDs must be distinct
    assert match_a["career_profile_id"] != match_b["career_profile_id"]
    assert match_a["match_id"] != match_b["match_id"]


@pytest.mark.asyncio
async def test_list_user_matches_endpoint(test_session: AsyncSession, client: AsyncClient):
    """GET /api/v1/jobs/matches returns all previously calculated matches in descending order."""
    await seed_skill_taxonomy_and_roles(test_session)
    pipeline = JobIngestionPipelineService()
    await pipeline.run_ingestion(source_name="seed", batch_size=5, db=test_session)

    token, _ = await register_and_login(client, "list.candidate@test.com", "List Candidate")
    headers = {"Authorization": f"Bearer {token}"}
    await setup_candidate_profile(client, token, target_role_id="backend-developer")

    # Refresh / calculate matches
    await client.post("/api/v1/jobs/matches/refresh", headers=headers)

    # Fetch stored matches
    r = await client.get("/api/v1/jobs/matches", headers=headers)
    assert r.status_code == 200
    matches = r.json()
    assert len(matches) >= 1
    scores = [m["overall_score"] for m in matches]
    assert scores == sorted(scores, reverse=True)


def test_missing_factors_normalization_bounds():
    """Unevaluated factors are cleanly normalized without yielding false 100% or zeroing out."""
    engine = JobMatchingEngine()

    job_no_reqs = Job(
        id=uuid.uuid4(),
        title="General Engineer",
        company_name="Mystery Corp",
        location="",
        remote_type="remote",
        role_id="backend-developer",
        experience_level="",  # Missing
    )
    job_no_reqs.skills = []  # No tagged skills

    profile = CareerProfile(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        primary_role_id="backend-developer",
        work_preference="remote",
        years_of_experience=decimal.Decimal("0.0"),
    )
    profile.user_skills = []
    profile.experience = []
    profile.projects = []

    res = engine.compute_match(profile, job_no_reqs)
    # Skill is unevaluated, experience is unevaluated
    assert "skill" in res["unevaluated_factors"]
    assert "experience" in res["unevaluated_factors"]
    assert "location" in res["evaluated_factors"]
    assert "preference" in res["evaluated_factors"]

    # Score should be strictly between 0 and 100
    assert 0.0 <= res["overall_score"] <= 100.0
    # Evaluated: project (20.0, weight 0.15), location (100.0, weight 0.10), preference (100.0, weight 0.10)
    # Normalized score: (3.0 + 10.0 + 10.0) / 0.35 = 65.7
    assert res["overall_score"] == 65.7
    # But evidence coverage is low, so flagged provisional
    assert res["is_provisional"] is True

