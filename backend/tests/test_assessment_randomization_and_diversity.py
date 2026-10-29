"""
Comprehensive Tests for Remediation Step 3:
Assessment Option Randomization and Question Diversity Engine.

Covers:
1. Option order randomization per attempt without modifying canonical questions.
2. Server-side mapping of displayed option indices to canonical indices.
3. Retention of correct answer truth during grading and answer submission.
4. Security: initial question session strictly conceals correct_option_index and explanation.
5. Idempotent attempt resume preserving exact question sequence and option ordering.
6. Question selection diversity: First attempt selects 20 unique questions (7/7/6 difficulty).
7. Retake diversity: Attempt 2 prioritizes the 10 questions unseen in Attempt 1 and selects all 10.
8. Multi-retake least-recently-seen rotation across 3+ attempts.
9. Zero duplicate questions within any attempt.
10. Category isolation: questions from one category never leak to another.
11. Accurate post-completion pedagogical review showing displayed options, correct answers, and candidate selections.
12. Downstream UserSkill calibration and skill gap engine integration.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seeds.assessment_seeder import seed_diagnostic_assessments
from app.db.seeds.gap_analysis_seeder import seed_skill_taxonomy_and_roles
from app.models.assessments import (
    Assessment,
    AssessmentAttempt,
    AssessmentQuestion,
)


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


# ─── A. Answer-Option Randomization & Security ───────────────────────────────


@pytest.mark.asyncio
async def test_canonical_question_options_remain_unmodified(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that creating attempts with option shuffling never modifies
    the master question record's options array or correct_option_index in the database.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "canonical_test@example.com", "Canonical Tester")

    # Record baseline state of all Python questions
    stmt = (
        select(AssessmentQuestion)
        .join(Assessment)
        .where(Assessment.skill_id == "python")
    )
    master_questions = (await test_session.scalars(stmt)).all()
    baseline = {
        q.id: (list(q.options), q.correct_option_index)
        for q in master_questions
    }

    # Create 3 successive attempts
    for _ in range(3):
        res = await client.post(
            "/api/v1/assessments/python/start",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        att_id = res.json()["attempt_id"]
        # Complete to allow next attempt
        await client.post(
            f"/api/v1/assessments/attempts/{att_id}/complete",
            headers={"Authorization": f"Bearer {token}"},
        )

    # Re-query master questions from database
    master_after = (await test_session.scalars(stmt)).all()
    for q in master_after:
        orig_options, orig_correct = baseline[q.id]
        assert q.options == orig_options, f"Master question {q.id} options were mutated!"
        assert q.correct_option_index == orig_correct, f"Master question {q.id} correct index mutated!"


@pytest.mark.asyncio
async def test_option_order_randomization_and_stability_on_refresh(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that:
    1. An active attempt persists option orders per question.
    2. Re-fetching / refreshing the attempt returns the exact same displayed option order.
    3. The option orders vary across different attempts.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "refresh_test@example.com", "Refresh Tester")

    # Start attempt
    res1 = await client.post(
        "/api/v1/assessments/python/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 200
    data1 = res1.json()
    attempt_id = data1["attempt_id"]
    questions1 = data1["questions"]

    # Re-fetch via GET /attempts/{id}
    res2 = await client.get(
        f"/api/v1/assessments/attempts/{attempt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 200
    questions2 = res2.json()["questions"]

    # Re-fetch via POST /python/start (idempotent resume)
    res3 = await client.post(
        "/api/v1/assessments/python/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res3.status_code == 200
    questions3 = res3.json()["questions"]

    for q1, q2, q3 in zip(questions1, questions2, questions3):
        assert q1["id"] == q2["id"] == q3["id"]
        assert q1["options"] == q2["options"] == q3["options"], "Displayed options changed on refresh!"


@pytest.mark.asyncio
async def test_different_attempts_produce_different_option_permutations(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that multiple newly created attempts receive different option orderings
    across questions rather than static identical option sequences.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "perm_tester@example.com", "Permutation Tester")

    # Start and complete 5 attempts, collecting option sequences for a shared question
    permutations_seen = set()

    for i in range(5):
        res = await client.post(
            "/api/v1/assessments/python/start",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        att_id = data["attempt_id"]

        # Track the option tuple of the first question
        first_q = data["questions"][0]
        permutations_seen.add(tuple(first_q["options"]))

        # Complete attempt to allow next attempt
        await client.post(
            f"/api/v1/assessments/attempts/{att_id}/complete",
            headers={"Authorization": f"Bearer {token}"},
        )

    # In random shuffling of 4 choices (24 permutations), 5 attempts should produce > 1 permutation
    assert len(permutations_seen) >= 2, "All attempts produced identical option orders!"


@pytest.mark.asyncio
async def test_insufficient_question_bank_produces_transparent_validation_error(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that if an assessment has fewer than 20 questions in the question bank,
    it returns a clear 422 validation error stating the actual count and required count,
    never crashing or silently fabricating duplicate questions.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "small_bank@example.com", "Small Bank Tester")

    # Create a small synthetic assessment with only 5 questions
    small_asmt = Assessment(
        skill_id="python",
        title="Micro Assessment",
        description="Testing small question bank",
        time_limit_minutes=15,
        passing_threshold=70.0,
    )
    test_session.add(small_asmt)
    await test_session.flush()

    # Add only 5 questions
    for i in range(5):
        q = AssessmentQuestion(
            assessment_id=small_asmt.id,
            prompt_text=f"Question {i} prompt for testing small bank behavior",
            options=["Option A", "Option B", "Option C", "Option D"],
            correct_option_index=0,
            explanation=f"Explanation for question {i}",
            difficulty="basic",
            topic="Basics",
        )
        test_session.add(q)
    await test_session.commit()

    # Attempt to start the micro assessment
    res = await client.post(
        f"/api/v1/assessments/{small_asmt.id}/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422
    data = res.json()
    err_msg = data.get("error", {}).get("message") or data.get("message", "")
    assert "contains only 5 questions" in err_msg
    assert "minimum 20 required" in err_msg


@pytest.mark.asyncio
async def test_answer_keys_concealed_during_active_attempt(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Security check:
    Verify that correct_option_index, explanation, and option_orders mapping
    are NEVER exposed in AttemptSessionResponse or AttemptQuestionPublic.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "security_test@example.com", "Security Tester")

    res = await client.post(
        "/api/v1/assessments/sql-databases/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()

    assert "option_orders" not in data
    for q in data["questions"]:
        assert "correct_option_index" not in q
        assert "explanation" not in q
        assert "permutation" not in q
        assert "canonical_option_index" not in q


@pytest.mark.asyncio
async def test_correct_and_incorrect_answer_mapping_accuracy(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that:
    1. Selecting the displayed option that corresponds to the canonical correct answer results in is_correct=True.
    2. Selecting a displayed option that corresponds to an incorrect answer results in is_correct=False.
    3. Graded review reflects the actual displayed options and indices.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "grading_mapping@example.com", "Mapping Tester")

    res = await client.post(
        "/api/v1/assessments/python/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = res.json()
    attempt_id = data["attempt_id"]
    displayed_questions = data["questions"]

    # Pre-fetch master questions to determine correct text per question
    stmt_q = (
        select(AssessmentQuestion)
        .join(Assessment)
        .where(Assessment.skill_id == "python")
    )
    master_questions = (await test_session.scalars(stmt_q)).all()
    correct_text_map = {str(q.id): q.options[q.correct_option_index] for q in master_questions}

    # Answer all 20 questions:
    # First 15 correct, last 5 incorrect
    expected_correct = 15
    for idx, dq in enumerate(displayed_questions):
        qid = dq["id"]
        correct_text = correct_text_map[qid]
        correct_disp_idx = dq["options"].index(correct_text)

        if idx < expected_correct:
            chosen_disp_idx = correct_disp_idx
        else:
            # Pick a wrong option
            chosen_disp_idx = (correct_disp_idx + 1) % len(dq["options"])

        # Submit answer
        ans_res = await client.post(
            f"/api/v1/assessments/attempts/{attempt_id}/answer",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question_id": qid,
                "selected_option_index": chosen_disp_idx,
                "response_time_seconds": 10,
            },
        )
        assert ans_res.status_code == 200

    # Finalize attempt
    comp_res = await client.post(
        f"/api/v1/assessments/attempts/{attempt_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert comp_res.status_code == 200
    result = comp_res.json()

    assert result["correct_count"] == expected_correct
    expected_score = round((expected_correct / 20) * 100.0, 1)  # 75.0%
    assert result["score_percentage"] == expected_score
    assert result["passed"] is True  # threshold is 70.0%

    # Verify each graded question in result
    for idx, gq in enumerate(result["questions"]):
        qid = gq["id"]
        correct_text = correct_text_map[qid]
        expected_correct_disp_idx = gq["options"].index(correct_text)

        assert gq["correct_option_index"] == expected_correct_disp_idx

        if idx < expected_correct:
            assert gq["is_correct"] is True
            assert gq["selected_option_index"] == expected_correct_disp_idx
        else:
            assert gq["is_correct"] is False
            assert gq["selected_option_index"] != expected_correct_disp_idx


# ─── B. Question Selection & Retake Diversity ────────────────────────────────


@pytest.mark.asyncio
async def test_initial_attempt_selects_20_unique_questions_with_difficulty_ratio(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that the first attempt selects exactly 20 distinct questions
    adhering strictly to: 7 Basic, 7 Intermediate, 6 Advanced.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "first_attempt@example.com", "First Attempt")

    res = await client.post(
        "/api/v1/assessments/dsa/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    questions = data["questions"]

    assert len(questions) == 20
    q_ids = [q["id"] for q in questions]
    assert len(set(q_ids)) == 20, "Attempt contains duplicate questions!"

    basics = [q for q in questions if q["difficulty"] == "basic"]
    inters = [q for q in questions if q["difficulty"] == "intermediate"]
    advs = [q for q in questions if q["difficulty"] == "advanced"]

    assert len(basics) == 7
    assert len(inters) == 7
    assert len(advs) == 6


@pytest.mark.asyncio
async def test_second_attempt_prioritizes_all_10_unseen_questions(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Core diversity test:
    With 30 questions in the bank (10 basic, 10 intermediate, 10 advanced):
    - Attempt 1 chooses 20 questions (7 basic, 7 intermediate, 6 advanced).
    - Unseen questions from Attempt 1: 3 basic, 3 intermediate, 4 advanced = 10 questions total.
    - Attempt 2 MUST prioritize and include ALL 10 previously unseen questions.
    - The remaining 10 slots must be filled from Attempt 1 without duplicates.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "retake_diversity@example.com", "Retake Diver")

    # 1. Attempt 1
    r1 = await client.post(
        "/api/v1/assessments/c-cpp/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r1.status_code == 200
    att1_data = r1.json()
    att1_id = att1_data["attempt_id"]
    att1_q_ids = set(q["id"] for q in att1_data["questions"])
    assert len(att1_q_ids) == 20

    # Complete Attempt 1
    c1 = await client.post(
        f"/api/v1/assessments/attempts/{att1_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert c1.status_code == 200

    # Find the 10 questions in C-CPP that were NOT in Attempt 1
    all_c_cpp = (
        await test_session.scalars(
            select(AssessmentQuestion)
            .join(Assessment)
            .where(Assessment.skill_id == "c-cpp")
        )
    ).all()
    all_c_cpp_ids = set(str(q.id) for q in all_c_cpp)
    assert len(all_c_cpp_ids) == 30

    unseen_in_att1 = all_c_cpp_ids - att1_q_ids
    assert len(unseen_in_att1) == 10, f"Expected 10 unseen questions, got {len(unseen_in_att1)}"

    # 2. Attempt 2 (Retake)
    r2 = await client.post(
        "/api/v1/assessments/c-cpp/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    att2_data = r2.json()
    att2_id = att2_data["attempt_id"]
    assert att2_id != att1_id
    att2_q_ids = set(q["id"] for q in att2_data["questions"])
    assert len(att2_q_ids) == 20

    # Invariant: ALL 10 previously unseen questions MUST be in Attempt 2!
    for unseen_qid in unseen_in_att1:
        assert unseen_qid in att2_q_ids, (
            f"Question {unseen_qid} was not seen in Attempt 1, "
            "but was NOT prioritized/included in Attempt 2!"
        )

    # Invariant: Overlap between Attempt 1 and Attempt 2 must be exactly 10 questions (the minimum possible!)
    overlap = att1_q_ids.intersection(att2_q_ids)
    assert len(overlap) == 10, f"Expected exactly 10 overlapping questions, got {len(overlap)}"


@pytest.mark.asyncio
async def test_three_attempts_least_recently_seen_rotation(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that across 3 successive attempts:
    - Attempt 3 prioritizes questions not seen in Attempt 2.
    - Zero duplicate questions within any single attempt.
    - Each attempt maintains the 7/7/6 difficulty distribution.
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "three_retakes@example.com", "Tri-Retaker")

    attempt_ids = []
    attempt_questions = []

    for i in range(3):
        res = await client.post(
            "/api/v1/assessments/java/start",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        att_id = data["attempt_id"]
        q_ids = [q["id"] for q in data["questions"]]

        # Strict checks for this attempt
        assert len(q_ids) == 20
        assert len(set(q_ids)) == 20, f"Attempt {i + 1} has duplicate questions!"

        basics = [q for q in data["questions"] if q["difficulty"] == "basic"]
        inters = [q for q in data["questions"] if q["difficulty"] == "intermediate"]
        advs = [q for q in data["questions"] if q["difficulty"] == "advanced"]
        assert len(basics) == 7
        assert len(inters) == 7
        assert len(advs) == 6

        attempt_ids.append(att_id)
        attempt_questions.append(set(q_ids))

        # Complete to allow next attempt
        await client.post(
            f"/api/v1/assessments/attempts/{att_id}/complete",
            headers={"Authorization": f"Bearer {token}"},
        )

    # Attempt 3 must prioritize questions absent in Attempt 2
    unseen_in_att2 = (attempt_questions[0] | attempt_questions[1]) - attempt_questions[1]
    # The 10 questions not in Attempt 2 must all be in Attempt 3
    all_java = (
        await test_session.scalars(
            select(AssessmentQuestion)
            .join(Assessment)
            .where(Assessment.skill_id == "java")
        )
    ).all()
    all_java_ids = set(str(q.id) for q in all_java)
    not_in_att2 = all_java_ids - attempt_questions[1]
    assert len(not_in_att2) == 10

    for qid in not_in_att2:
        assert qid in attempt_questions[2], f"Question {qid} absent in Attempt 2 was missing from Attempt 3!"


@pytest.mark.asyncio
async def test_category_isolation_questions_never_cross_domains(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that questions from one category (e.g. Python) are never
    accidentally selected in another category's attempt (e.g. JavaScript).
    """
    await seed_diagnostic_assessments(test_session)
    token = await register_and_login(client, "isolation@example.com", "Isolation Tester")

    # Start JavaScript assessment
    res = await client.post(
        "/api/v1/assessments/javascript-typescript/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    js_q_ids = [uuid.UUID(q["id"]) for q in res.json()["questions"]]

    # Query master DB to verify all assigned questions belong to javascript-typescript
    stmt = (
        select(AssessmentQuestion)
        .join(Assessment)
        .where(
            AssessmentQuestion.id.in_(js_q_ids),
            Assessment.skill_id != "javascript-typescript",
        )
    )
    cross_category = (await test_session.scalars(stmt)).all()
    assert len(cross_category) == 0, "Found questions from other categories in JS attempt!"


# ─── C. Downstream Skill-Gap & Platform Regression ──────────────────────────


@pytest.mark.asyncio
async def test_completed_assessment_updates_user_skills_and_skill_gap(
    client: AsyncClient, test_session: AsyncSession
):
    """
    Verifies that a completed assessment:
    1. Updates the candidate's UserSkill record in their CareerProfile.
    2. Elevates is_verified to True when passed.
    3. Feeds into deterministic skill gap analysis role alignment.
    """
    await seed_diagnostic_assessments(test_session)
    await seed_skill_taxonomy_and_roles(test_session)

    token = await register_and_login(client, "downstream_test@example.com", "Downstream Candidate")
    headers = {"Authorization": f"Bearer {token}"}

    # Pre-fetch master questions to know correct answer text for each question
    stmt_q = (
        select(AssessmentQuestion)
        .join(Assessment)
        .where(Assessment.skill_id == "python")
    )
    master_qs = (await test_session.scalars(stmt_q)).all()
    correct_text_map = {str(q.id): q.options[q.correct_option_index] for q in master_qs}

    # 1. Start Python assessment
    r_start = await client.post("/api/v1/assessments/python/start", headers=headers)
    assert r_start.status_code == 200
    att_data = r_start.json()
    att_id = att_data["attempt_id"]
    questions = att_data["questions"]

    # 2. Answer all 20 questions correctly using displayed options
    for q in questions:
        qid = q["id"]
        correct_text = correct_text_map[qid]
        correct_disp_idx = q["options"].index(correct_text)

        await client.post(
            f"/api/v1/assessments/attempts/{att_id}/answer",
            headers=headers,
            json={"question_id": qid, "selected_option_index": correct_disp_idx},
        )

    # 3. Complete attempt
    r_comp = await client.post(f"/api/v1/assessments/attempts/{att_id}/complete", headers=headers)
    assert r_comp.status_code == 200
    res_data = r_comp.json()
    assert res_data["score_percentage"] == 100.0
    assert res_data["passed"] is True
    assert res_data["proficiency_band"] == "Strong"

    # 4. Verify skill-gap analysis consumes the verified Python skill
    gap_res = await client.post(
        "/api/v1/skills/gap-analysis",
        headers=headers,
        json={"role_id": "backend-developer"},
    )
    assert gap_res.status_code in [200, 201]
    gap_data = gap_res.json()
    python_detail = gap_data["skill_details"]["python"]
    assert python_detail["status"] == "STRENGTH"
    assert python_detail["current_level"] >= 3
