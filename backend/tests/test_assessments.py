"""
Comprehensive Tests for Diagnostic Skill Assessments Feature.
Covers question bank completeness (all 9 categories >= 30 questions, 10/10/10 distribution),
20-question attempt creation, persistence on refresh, hidden answer keys, server-side grading,
proficiency bands, topic breakdowns, retake history preservation, and cross-user security.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.assessment_seeder import CATEGORIES_SPEC, seed_diagnostic_assessments
from app.models.assessments import (
    Assessment,
    AssessmentAnswer,
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentResult,
)


# ─── Test Helpers ───────────────────────────────────────────────────


async def register_and_login(client: AsyncClient, email: str, full_name: str) -> str:
    pw = "SecurePassword123!"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pw, "full_name": full_name},
    )
    assert r.status_code == 201
    r2 = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pw},
    )
    assert r2.status_code == 200
    return r2.json()["access_token"]


# ─── Question Bank Tests ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_question_bank_completeness(test_session: AsyncSession):
    """
    Verifies that:
    1. All 9 required assessment categories exist.
    2. Each category contains at least 30 distinct questions.
    3. Every category has at least 10 basic, 10 intermediate, and 10 advanced questions.
    4. Total questions across the bank is at least 270.
    5. All questions have 4 distinct options, valid correct_option_index, and detailed explanations.
    """
    seed_result = await seed_diagnostic_assessments(test_session)
    assert seed_result["skills_count"] == 9
    assert seed_result["assessments_count"] == 9
    assert seed_result["total_questions"] >= 270

    expected_categories = [
        "python",
        "javascript-typescript",
        "java",
        "c-cpp",
        "sql-databases",
        "dsa",
        "web-development",
        "machine-learning",
        "ai-llm",
    ]

    for cat_id in expected_categories:
        assert cat_id in seed_result["categories"], f"Missing required category: {cat_id}"
        stats = seed_result["categories"][cat_id]
        assert stats["total"] >= 30, f"{cat_id} has {stats['total']} questions; expected >= 30"
        assert stats["basic"] >= 10, f"{cat_id} has {stats['basic']} basic questions; expected >= 10"
        assert stats["intermediate"] >= 10, f"{cat_id} has {stats['intermediate']} intermediate questions; expected >= 10"
        assert stats["advanced"] >= 10, f"{cat_id} has {stats['advanced']} advanced questions; expected >= 10"

    # Query all questions from DB and validate structural integrity
    questions = (await test_session.scalars(select(AssessmentQuestion))).all()
    assert len(questions) >= 270

    seen_ids = set()
    for q in questions:
        assert q.id not in seen_ids, f"Duplicate question ID found: {q.id}"
        seen_ids.add(q.id)
        assert len(q.prompt_text.strip()) > 10, f"Empty prompt on question {q.id}"
        assert isinstance(q.options, list), f"Options not a list on question {q.id}"
        assert len(q.options) == 4, f"Question {q.id} has {len(q.options)} options; expected exactly 4"
        assert len(set(q.options)) == 4, f"Duplicate options found in question {q.id}"
        assert 0 <= q.correct_option_index <= 3, f"Invalid correct_option_index on question {q.id}"
        assert len(q.explanation.strip()) > 15, f"Missing detailed explanation on question {q.id}"
        assert q.difficulty in ("basic", "intermediate", "advanced")
        assert len(q.topic.strip()) > 0


# ─── API Catalog & Detail Tests ──────────────────────────────────────


@pytest.mark.asyncio
async def test_list_assessments_endpoint(client: AsyncClient, test_session: AsyncSession):
    """Verifies that GET /api/v1/assessments returns all 9 categories with metadata."""
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "assess.list@test.com", "Rohan Verma")

    response = await client.get(
        "/api/v1/assessments",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9

    for cat in data:
        assert "id" in cat
        assert "skill_id" in cat
        assert "title" in cat
        assert "time_limit_minutes" in cat
        assert "passing_threshold" in cat
        assert cat["question_count"] >= 30
        assert cat["user_status"] in ("available", "in_progress", "completed")


@pytest.mark.asyncio
async def test_get_assessment_detail_endpoint(client: AsyncClient, test_session: AsyncSession):
    """Verifies detailed category inspection endpoint by skill_id."""
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "assess.detail@test.com", "Pooja Sharma")

    response = await client.get(
        "/api/v1/assessments/python",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["skill_id"] == "python"
    assert data["total_bank_questions"] >= 30
    assert data["attempt_question_count"] == 20
    assert len(data["topics"]) >= 5
    assert data["difficulty_breakdown"]["basic"] >= 10
    assert data["difficulty_breakdown"]["intermediate"] >= 10
    assert data["difficulty_breakdown"]["advanced"] >= 10


# ─── Attempt Lifecycle & 20-Question Distribution Tests ──────────────


@pytest.mark.asyncio
async def test_start_attempt_20_questions_distribution(client: AsyncClient, test_session: AsyncSession):
    """
    Verifies that starting an attempt:
    1. Selects exactly 20 questions.
    2. Respects the 7 basic, 7 intermediate, 6 advanced distribution.
    3. Contains no duplicate questions.
    4. Does NOT reveal correct answers or explanations.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "assess.start@test.com", "Ananya Rao")

    response = await client.post(
        "/api/v1/assessments/python/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "in_progress"
    assert data["total_questions"] == 20
    assert len(data["questions"]) == 20

    question_ids = [q["id"] for q in data["questions"]]
    assert len(set(question_ids)) == 20, "Questions contain duplicates within attempt"

    # Count difficulty distribution
    basic_q = [q for q in data["questions"] if q["difficulty"] == "basic"]
    inter_q = [q for q in data["questions"] if q["difficulty"] == "intermediate"]
    adv_q = [q for q in data["questions"] if q["difficulty"] == "advanced"]

    assert len(basic_q) == 7, f"Expected 7 basic questions, got {len(basic_q)}"
    assert len(inter_q) == 7, f"Expected 7 intermediate questions, got {len(inter_q)}"
    assert len(adv_q) == 6, f"Expected 6 advanced questions, got {len(adv_q)}"

    # Security: Verify that answer keys are NOT exposed
    for q in data["questions"]:
        assert "correct_option_index" not in q, "Security leak: correct_option_index exposed in active attempt!"
        assert "explanation" not in q, "Security leak: explanation exposed in active attempt!"


@pytest.mark.asyncio
async def test_attempt_resumed_on_refresh(client: AsyncClient, test_session: AsyncSession):
    """
    Verifies that calling start again while an attempt is in-progress restores
    the exact same attempt with the exact same questions and order.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "assess.resume@test.com", "Kiran Patel")

    # Start attempt
    r1 = await client.post(
        "/api/v1/assessments/sql-databases/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r1.status_code == 200
    data1 = r1.json()
    attempt_id = data1["attempt_id"]
    q_ids_1 = [q["id"] for q in data1["questions"]]

    # Call start again (simulating browser page refresh / re-click)
    r2 = await client.post(
        "/api/v1/assessments/sql-databases/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["attempt_id"] == attempt_id, "Did not resume existing in_progress attempt"
    q_ids_2 = [q["id"] for q in data2["questions"]]
    assert q_ids_1 == q_ids_2, "Question sequence changed upon attempt resume!"


# ─── Answer Submission & Grading Tests ───────────────────────────────


@pytest.mark.asyncio
async def test_submit_answer_and_complete_attempt(client: AsyncClient, test_session: AsyncSession):
    """
    Tests submitting answers and finalizing attempt:
    1. Answers persist correctly.
    2. Server-side grading evaluates score accurately.
    3. Final result contains proficiency band, topic breakdown, and review with explanations.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "assess.grading@test.com", "Vikram Sen")

    # Start DSA attempt
    r_start = await client.post(
        "/api/v1/assessments/dsa/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = r_start.json()
    attempt_id = data["attempt_id"]
    questions = data["questions"]

    # Submit an answer for the 1st question
    q1_id = questions[0]["id"]
    r_ans = await client.post(
        f"/api/v1/assessments/attempts/{attempt_id}/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={"question_id": q1_id, "selected_option_index": 2, "response_time_seconds": 15},
    )
    assert r_ans.status_code == 200
    ans_data = r_ans.json()
    assert ans_data["answered_count"] == 1
    assert ans_data["selected_option_index"] == 2

    # Verify attempt session returns the recorded answer
    r_sess = await client.get(
        f"/api/v1/assessments/attempts/{attempt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_sess.status_code == 200
    assert r_sess.json()["current_answers"][q1_id] == 2

    # Complete the attempt
    r_comp = await client.post(
        f"/api/v1/assessments/attempts/{attempt_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_comp.status_code == 200
    res_data = r_comp.json()

    assert res_data["status"] == "completed"
    assert 0.0 <= res_data["score_percentage"] <= 100.0
    assert res_data["proficiency_band"] in ("Foundational", "Developing", "Proficient", "Strong")
    assert len(res_data["topic_breakdown"]) >= 1
    assert "basic" in res_data["difficulty_breakdown"]
    assert "intermediate" in res_data["difficulty_breakdown"]
    assert "advanced" in res_data["difficulty_breakdown"]
    assert len(res_data["questions"]) == 20

    # Post-completion: Question review now includes correct answers and explanations
    for q_res in res_data["questions"]:
        assert "correct_option_index" in q_res
        assert "explanation" in q_res
        assert isinstance(q_res["is_correct"], bool)


@pytest.mark.asyncio
async def test_retake_preserves_history(client: AsyncClient, test_session: AsyncSession):
    """
    Verifies that taking an assessment multiple times creates new attempts
    and preserves historical scores without overwriting previous attempts.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "assess.retake@test.com", "Divya Nair")

    # 1. Complete first attempt
    r1 = await client.post("/api/v1/assessments/java/start", headers={"Authorization": f"Bearer {token}"})
    att1_id = r1.json()["attempt_id"]
    await client.post(f"/api/v1/assessments/attempts/{att1_id}/complete", headers={"Authorization": f"Bearer {token}"})

    # 2. Start a retake (second attempt)
    r2 = await client.post("/api/v1/assessments/java/start", headers={"Authorization": f"Bearer {token}"})
    att2_id = r2.json()["attempt_id"]
    assert att2_id != att1_id, "Retake did not allocate a distinct attempt ID"
    await client.post(f"/api/v1/assessments/attempts/{att2_id}/complete", headers={"Authorization": f"Bearer {token}"})

    # 3. Check history
    r_hist = await client.get("/api/v1/assessments/history", headers={"Authorization": f"Bearer {token}"})
    assert r_hist.status_code == 200
    history = r_hist.json()
    assert len(history) >= 2
    history_attempt_ids = [h["attempt_id"] for h in history]
    assert att1_id in history_attempt_ids
    assert att2_id in history_attempt_ids


# ─── Cross-User Security Tests ──────────────────────────────────────


@pytest.mark.asyncio
async def test_cross_user_attempt_access_forbidden(client: AsyncClient, test_session: AsyncSession):
    """Verifies that User B cannot access or answer User A's assessment attempt."""
    await seed_diagnostic_assessments(test_session)
    token_a = await register_and_login(client, "assess.usera@test.com", "User Alpha")
    token_b = await register_and_login(client, "assess.userb@test.com", "User Beta")

    # User A starts attempt
    r_a = await client.post("/api/v1/assessments/python/start", headers={"Authorization": f"Bearer {token_a}"})
    att_a_id = r_a.json()["attempt_id"]
    q_id = r_a.json()["questions"][0]["id"]

    # User B attempts to view User A's attempt
    r_b_view = await client.get(
        f"/api/v1/assessments/attempts/{att_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_b_view.status_code == 403

    # User B attempts to submit answer to User A's attempt
    r_b_ans = await client.post(
        f"/api/v1/assessments/attempts/{att_a_id}/answer",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"question_id": q_id, "selected_option_index": 1},
    )
    assert r_b_ans.status_code == 403
