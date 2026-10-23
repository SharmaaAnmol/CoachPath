"""
Integration Tests for Phase 3C: Central Career Profile Management.
Verifies master profile retrieval, personal info updates, career goals calibration,
scoped CRUD for education, experience, projects, and certifications,
strict cross-user multi-tenant authorization, and deterministic completeness calculation.
"""

from __future__ import annotations

import uuid
from datetime import date
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import UserProfile
from app.models.career import CareerProfile, Certification, Education, Experience, Project, Role
from app.services.profile import calculate_profile_completeness


async def register_and_login(client: AsyncClient, email: str, full_name: str) -> str:
    """Helper to register and login a candidate, returning access_token."""
    pw = "SecurePassword123!"
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": full_name},
    )
    assert reg_res.status_code == 201

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert login_res.status_code == 200
    return login_res.json()["access_token"]


@pytest.mark.asyncio
async def test_get_master_profile_auto_created(client: AsyncClient):
    """Verifies a freshly registered candidate can retrieve their master profile."""
    token = await register_and_login(client, "profile.init@example.com", "Priya Sharma")

    response = await client.get(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["full_name"] == "Priya Sharma"
    assert data["email"] == "profile.init@example.com"
    assert "profile_id" in data
    assert data["education"] == []
    assert data["experience"] == []
    assert data["projects"] == []
    assert data["certifications"] == []
    assert data["completeness_score"] >= 5.0


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client: AsyncClient):
    """Verifies that accessing /profile without auth returns 401."""
    response = await client.get("/api/v1/profile")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


@pytest.mark.asyncio
async def test_update_personal_profile(client: AsyncClient):
    """Verifies updating headline, location, bio, and portfolio links."""
    token = await register_and_login(client, "update.profile@example.com", "Rohan Patel")

    payload = {
        "headline": "Full-Stack Engineer | React & Python",
        "location": "Bengaluru, India",
        "bio": "Passionate about high-throughput distributed systems.",
        "github_url": "https://github.com/rohan-patel",
        "linkedin_url": "https://linkedin.com/in/rohan-patel",
    }
    response = await client.put(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["headline"] == payload["headline"]
    assert data["location"] == payload["location"]
    assert data["bio"] == payload["bio"]
    assert data["github_url"] == payload["github_url"]
    assert data["linkedin_url"] == payload["linkedin_url"]
    # Score should have increased after adding personal details
    assert data["completeness_score"] >= 20.0


@pytest.mark.asyncio
async def test_career_goals_get_and_update(client: AsyncClient, test_session: AsyncSession):
    """Verifies retrieving and updating career goals."""
    # Ensure role exists
    role = Role(
        id="backend-developer",
        title="Backend Developer",
        description="Backend engineering",
        category="engineering",
    )
    test_session.add(role)
    await test_session.commit()

    token = await register_and_login(client, "career.goals@example.com", "Ananya Sen")

    # 1. Get initial goals
    get_res = await client.get(
        "/api/v1/profile/career-goals",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200

    # 2. Update goals
    update_payload = {
        "primary_role_id": "backend-developer",
        "career_stage": "recent_graduate",
        "work_preference": "remote",
        "target_locations": ["Remote", "Bengaluru"],
        "years_of_experience": 1.5,
    }
    put_res = await client.put(
        "/api/v1/profile/career-goals",
        headers={"Authorization": f"Bearer {token}"},
        json=update_payload,
    )
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["primary_role"]["id"] == "backend-developer"
    assert data["career_stage"] == "recent_graduate"
    assert data["work_preference"] == "remote"
    assert "Bengaluru" in data["target_locations"]
    assert data["years_of_experience"] == 1.5


@pytest.mark.asyncio
async def test_education_crud_and_validation(client: AsyncClient):
    """Verifies full CRUD lifecycle and date validation for academic credentials."""
    token = await register_and_login(client, "education.test@example.com", "Dev User")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Invalid date order (end_date < start_date) -> 422
    bad_payload = {
        "institution_name": "Tech Institute",
        "degree": "B.Tech",
        "field_of_study": "Computer Science",
        "start_date": "2024-08-01",
        "end_date": "2022-05-01",
    }
    bad_res = await client.post("/api/v1/profile/education", headers=headers, json=bad_payload)
    assert bad_res.status_code == 422

    # 2. Valid creation
    create_payload = {
        "institution_name": "Indian Institute of Technology",
        "degree": "Bachelor of Technology",
        "field_of_study": "Computer Science & Engineering",
        "start_date": "2021-08-15",
        "end_date": "2025-05-30",
        "is_current": False,
        "gpa": 3.85,
    }
    create_res = await client.post("/api/v1/profile/education", headers=headers, json=create_payload)
    assert create_res.status_code == 201
    edu_data = create_res.json()
    edu_id = edu_data["id"]
    assert edu_data["institution_name"] == create_payload["institution_name"]
    assert edu_data["gpa"] == 3.85

    # 3. List education
    list_res = await client.get("/api/v1/profile/education", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 4. Update education
    update_payload = {"gpa": 3.92, "is_current": True}
    update_res = await client.put(f"/api/v1/profile/education/{edu_id}", headers=headers, json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["gpa"] == 3.92
    assert update_res.json()["is_current"] is True

    # 5. Delete education
    del_res = await client.delete(f"/api/v1/profile/education/{edu_id}", headers=headers)
    assert del_res.status_code == 204

    # 6. Verify empty list
    empty_res = await client.get("/api/v1/profile/education", headers=headers)
    assert len(empty_res.json()) == 0


@pytest.mark.asyncio
async def test_experience_crud(client: AsyncClient):
    """Verifies work experience CRUD operations."""
    token = await register_and_login(client, "exp.test@example.com", "Exp Candidate")
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "company_name": "Razorpay",
        "role_title": "Backend Engineering Intern",
        "location": "Bengaluru",
        "start_date": "2024-01-10",
        "end_date": "2024-06-30",
        "is_current": False,
        "bullet_points": [
            "Engineered idempotent payment reconciliation webhooks in Go and PostgreSQL.",
            "Reduced p99 webhook latency by 35% via Redis caching.",
        ],
    }
    res = await client.post("/api/v1/profile/experience", headers=headers, json=create_payload)
    assert res.status_code == 201
    exp_id = res.json()["id"]

    # Read
    list_res = await client.get("/api/v1/profile/experience", headers=headers)
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["company_name"] == "Razorpay"

    # Update
    up_res = await client.put(
        f"/api/v1/profile/experience/{exp_id}",
        headers=headers,
        json={"role_title": "Software Engineer Intern"},
    )
    assert up_res.status_code == 200
    assert up_res.json()["role_title"] == "Software Engineer Intern"

    # Delete
    del_res = await client.delete(f"/api/v1/profile/experience/{exp_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_projects_crud(client: AsyncClient):
    """Verifies project artifact CRUD operations."""
    token = await register_and_login(client, "project.test@example.com", "Dev Lead")
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "title": "Distributed Task Queue",
        "description": "Async job executor built with Python and RabbitMQ.",
        "technologies": ["Python", "FastAPI", "RabbitMQ", "Redis"],
        "github_url": "https://github.com/test/task-queue",
        "bullet_points": ["Handled 10,000 tasks/second with dead-letter queue retries."],
    }
    res = await client.post("/api/v1/profile/projects", headers=headers, json=create_payload)
    assert res.status_code == 201
    proj_id = res.json()["id"]

    list_res = await client.get("/api/v1/profile/projects", headers=headers)
    assert len(list_res.json()) == 1

    up_res = await client.put(
        f"/api/v1/profile/projects/{proj_id}",
        headers=headers,
        json={"title": "High-Throughput Task Queue"},
    )
    assert up_res.status_code == 200
    assert up_res.json()["title"] == "High-Throughput Task Queue"

    del_res = await client.delete(f"/api/v1/profile/projects/{proj_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_certifications_crud(client: AsyncClient):
    """Verifies certification credential CRUD operations."""
    token = await register_and_login(client, "cert.test@example.com", "Certified Cloud Architect")
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "name": "AWS Certified Solutions Architect – Associate",
        "issuing_organization": "Amazon Web Services",
        "issue_date": "2024-05-15",
        "expiration_date": "2027-05-15",
        "credential_id": "AWS-PSA-998822",
        "credential_url": "https://aws.amazon.com/verify/998822",
    }
    res = await client.post("/api/v1/profile/certifications", headers=headers, json=create_payload)
    assert res.status_code == 201
    cert_id = res.json()["id"]

    list_res = await client.get("/api/v1/profile/certifications", headers=headers)
    assert len(list_res.json()) == 1

    del_res = await client.delete(f"/api/v1/profile/certifications/{cert_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_cross_user_isolation_prevented(client: AsyncClient):
    """Verifies that User A cannot modify or delete User B's profile records (403)."""
    # 1. User A creates an education record
    token_a = await register_and_login(client, "usera@example.com", "User Alice")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    edu_res = await client.post(
        "/api/v1/profile/education",
        headers=headers_a,
        json={
            "institution_name": "Alice University",
            "degree": "B.S.",
            "field_of_study": "CS",
            "start_date": "2022-08-01",
        },
    )
    assert edu_res.status_code == 201
    edu_id_a = edu_res.json()["id"]

    # 2. User B logs in
    token_b = await register_and_login(client, "userb@example.com", "User Bob")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User B attempts to modify User A's education entry -> 403 Forbidden
    hack_put = await client.put(
        f"/api/v1/profile/education/{edu_id_a}",
        headers=headers_b,
        json={"institution_name": "Bob Hijacked University"},
    )
    assert hack_put.status_code == 403
    assert hack_put.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"

    # 4. User B attempts to delete User A's education entry -> 403 Forbidden
    hack_del = await client.delete(
        f"/api/v1/profile/education/{edu_id_a}",
        headers=headers_b,
    )
    assert hack_del.status_code == 403
    assert hack_del.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_deterministic_profile_completeness_calculation():
    """Unit test verifying deterministic weighted completeness logic."""
    # 1. Empty profile
    assert calculate_profile_completeness(None, None) == 0.0

    # 2. Only full name (signup state)
    u_prof = UserProfile(full_name="Aarav")
    assert calculate_profile_completeness(u_prof, None) == 5.0

    # 3. Full personal details (+15 -> 20.0)
    u_prof.headline = "Software Engineer"
    u_prof.location = "San Francisco"
    u_prof.bio = "Hello world"
    assert calculate_profile_completeness(u_prof, None) == 20.0

    # 4. Adding career goals (+20 -> 40.0)
    c_prof = CareerProfile(
        primary_role_id="backend-developer",
        career_stage="student",
        work_preference="remote",
    )
    c_prof.education = []
    c_prof.experience = []
    c_prof.projects = []
    c_prof.certifications = []
    assert calculate_profile_completeness(u_prof, c_prof) == 40.0

    # 5. Adding education (+20 -> 60.0)
    c_prof.education = [Education(institution_name="SJSU", degree="BS", field_of_study="CS", start_date=date(2021, 1, 1))]
    assert calculate_profile_completeness(u_prof, c_prof) == 60.0

    # 6. Adding experience (+20 -> 80.0)
    c_prof.experience = [Experience(company_name="Google", role_title="SWE", start_date=date(2023, 1, 1))]
    assert calculate_profile_completeness(u_prof, c_prof) == 80.0

    # 7. Adding project (+15 -> 95.0)
    c_prof.projects = [Project(title="API", description="FastAPI app")]
    assert calculate_profile_completeness(u_prof, c_prof) == 95.0

    # 8. Adding certification (+5 -> 100.0)
    c_prof.certifications = [Certification(name="AWS SAA", issuing_organization="AWS", issue_date=date(2024, 1, 1))]
    assert calculate_profile_completeness(u_prof, c_prof) == 100.0


@pytest.mark.asyncio
async def test_list_supported_roles(client: AsyncClient):
    """Verifies that canonical benchmark roles can be queried."""
    res = await client.get("/api/v1/profile/roles")
    assert res.status_code == 200
    roles = res.json()
    assert isinstance(roles, list)
    assert len(roles) >= 1
    assert any(r["id"] == "backend-developer" for r in roles)
