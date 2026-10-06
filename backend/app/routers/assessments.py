from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import uuid
import json
import sqlite3
from app.core.config import settings
from app.core.db import get_connection
from app.services.recompute import recompute_everything

router = APIRouter(prefix="/assessments", tags=["Assessments"])

SAMPLE_QUESTION_BANKS = {
    "python": [
        {
            "id": "py-q1",
            "qtype": "mcq",
            "dimension": "Knowledge",
            "prompt": "What is the key difference between Python's list 'append()' and 'extend()' methods?",
            "options": [
                "A) append() adds its argument as a single element; extend() iterates over its argument adding each item",
                "B) append() works only with strings; extend() works with integers",
                "C) extend() mutates the list in-place; append() returns a new copy",
                "D) Both do the exact same operation"
            ],
            "answer_key": "A",
            "explanation": "append(x) adds x as an individual item, while extend(iterable) unpacks and appends each element of iterable."
        },
        {
            "id": "py-q2",
            "qtype": "code",
            "dimension": "Problem Solving",
            "prompt": "Find the bug in this Python function meant to remove duplicate numbers while preserving order:\n\ndef dedup(nums):\n    seen = set()\n    res = []\n    for n in nums:\n        if n not in seen:\n            res.append(n)\n            # BUG: missing seen.add(n)\n    return res",
            "options": [
                "A) 'seen' is never updated with seen.add(n), causing duplicates to never be filtered",
                "B) 'res.append(n)' throws an IndexError",
                "C) Sets cannot store numbers in Python",
                "D) The return statement should be outside the function"
            ],
            "answer_key": "A",
            "explanation": "Without adding visited elements to 'seen', the check 'n not in seen' is always True."
        },
        {
            "id": "py-q3",
            "qtype": "code",
            "dimension": "Practical Skills",
            "prompt": "In Scikit-Learn or Pandas, why should Data Normalization/StandardScaler be fitted ONLY on the training split rather than the whole dataset?",
            "options": [
                "A) To prevent Data Leakage from test/validation distributions into model training",
                "B) Because StandardScaler does not accept test datasets",
                "C) It makes the code run 10x slower on GPU",
                "D) Test split features have different column names"
            ],
            "answer_key": "A",
            "explanation": "Fitting scalers or imputers on test data introduces data leakage, giving overly optimistic validation metrics that degrade in production."
        },
        {
            "id": "py-q4",
            "qtype": "mcq",
            "dimension": "Industry Readiness",
            "prompt": "When deploying a FastAPI ML inference service in production, why should synchronous, CPU-bound model predictions (e.g., model.predict()) be offloaded to a threadpool / worker rather than blocking the main async event loop?",
            "options": [
                "A) Heavy synchronous CPU computation blocks the single async event loop thread, starving other concurrent HTTP requests",
                "B) FastAPI automatically disables CPU models",
                "C) Async functions cannot return JSON objects",
                "D) Python GIL crashes on async endpoints"
            ],
            "answer_key": "A",
            "explanation": "Blocking the asyncio event loop with CPU-heavy computation freezes the entire server process for other incoming requests."
        }
    ],
    "sql": [
        {
            "id": "sql-q1",
            "qtype": "mcq",
            "dimension": "Knowledge",
            "prompt": "What is the difference between WHERE and HAVING in SQL?",
            "options": [
                "A) WHERE filters rows before aggregation; HAVING filters groups after aggregation",
                "B) HAVING can only be used with PostgreSQL",
                "C) WHERE requires an ORDER BY clause",
                "D) There is no functional difference"
            ],
            "answer_key": "A",
            "explanation": "WHERE filters individual records prior to GROUP BY. HAVING evaluates conditions on aggregated results (e.g., HAVING COUNT(*) > 5)."
        },
        {
            "id": "sql-q2",
            "qtype": "sql",
            "dimension": "Practical Skills",
            "prompt": "Given a table 'employees (id INT, name TEXT, salary INT, department_id INT)', write a query to find the 2nd highest salary.",
            "options": [
                "A) SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1",
                "B) SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees)",
                "C) Both A and B are valid solutions",
                "D) SELECT salary[2] FROM employees"
            ],
            "answer_key": "C",
            "explanation": "Both LIMIT 1 OFFSET 1 with descending order and subqueries finding MAX strictly less than the top MAX accurately retrieve the 2nd highest salary."
        },
        {
            "id": "sql-q3",
            "qtype": "mcq",
            "dimension": "Problem Solving",
            "prompt": "Which JOIN type returns all records from Table A, along with matching rows from Table B, and fills NULL where Table B has no match?",
            "options": [
                "A) LEFT OUTER JOIN",
                "B) INNER JOIN",
                "C) CROSS JOIN",
                "D) FULL JOIN"
            ],
            "answer_key": "A",
            "explanation": "LEFT JOIN keeps all left table rows and injects NULLs for unmatched right table keys."
        },
        {
            "id": "sql-q4",
            "qtype": "mcq",
            "dimension": "Industry Readiness",
            "prompt": "In an e-commerce database with 10M orders, why does adding a B-Tree index on 'customer_id' dramatically accelerate 'SELECT * FROM orders WHERE customer_id = ?'?",
            "options": [
                "A) Reduces lookup complexity from O(N) full table scan to O(log N) tree traversal",
                "B) Compresses database files to 1% size",
                "C) Caches the full table into RAM",
                "D) Replaces the relational engine with Redis"
            ],
            "answer_key": "A",
            "explanation": "B-Tree indexes allow logarithmic search and rapid range scans without reading every single block on disk."
        }
    ]
}

@router.post("/start")
def start_assessment(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Initiates a skill assessment session with questions across the 4 dimensions."""
    user_id = payload.get("user_id", settings.DEFAULT_USER_ID)
    skill = payload.get("skill", "python").lower()
    
    questions = SAMPLE_QUESTION_BANKS.get(skill, SAMPLE_QUESTION_BANKS["python"])
    assessment_id = str(uuid.uuid4())
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO assessments (id, user_id, skill, status)
        VALUES (?, ?, ?, 'in_progress')
        """,
        (assessment_id, user_id, skill)
    )
    
    for q in questions:
        cursor.execute(
            """
            INSERT INTO assessment_questions (id, assessment_id, qtype, prompt, options, answer_key, dimension)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                assessment_id,
                q["qtype"],
                q["prompt"],
                json.dumps(q.get("options", [])),
                json.dumps({"key": q.get("answer_key", "A"), "explanation": q.get("explanation", "")}),
                q["dimension"]
            )
        )
    conn.commit()
    conn.close()

    return {
        "assessment_id": assessment_id,
        "skill": skill,
        "total_questions": len(questions),
        "dimensions": ["Knowledge", "Problem Solving", "Practical Skills", "Industry Readiness"],
        "questions": questions
    }

@router.post("/{assessment_id}/submit")
def submit_assessment(assessment_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates candidate answers across the 4 scored dimensions,
    maps score -> level (0-39 Beginner, 40-69 Intermediate, 70+ Advanced),
    updates user_skills, and triggers recompute_everything!
    """
    user_id = payload.get("user_id", settings.DEFAULT_USER_ID)
    answers = payload.get("answers", {}) # {"py-q1": "A", "py-q2": "A", ...}
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT skill FROM assessments WHERE id = ?", (assessment_id,))
    row = cursor.fetchone()
    skill = row["skill"] if row else "python"
    conn.close()

    questions = SAMPLE_QUESTION_BANKS.get(skill, SAMPLE_QUESTION_BANKS["python"])
    
    dimension_scores = {
        "Knowledge": 0,
        "Problem Solving": 0,
        "Practical Skills": 0,
        "Industry Readiness": 0
    }
    dimension_counts = {k: 0 for k in dimension_scores}
    correct_count = 0

    for q in questions:
        dim = q["dimension"]
        dimension_counts[dim] = dimension_counts.get(dim, 0) + 1
        
        user_ans = answers.get(q["id"], "").strip()
        expected = q.get("answer_key", "A")
        
        # Check matching answer or selected letter
        is_correct = user_ans.upper().startswith(expected) or expected in user_ans.upper()
        if is_correct:
            correct_count += 1
            dimension_scores[dim] = dimension_scores.get(dim, 0) + 100

    # Calculate dimension averages
    for dim in dimension_scores:
        count = dimension_counts.get(dim, 1)
        dimension_scores[dim] = int(dimension_scores[dim] / count) if count > 0 else 70

    overall_score = int(sum(dimension_scores.values()) / len(dimension_scores))

    # Level mapping (Slide 8): 0-39 Beginner, 40-69 Intermediate, 70+ Advanced
    if overall_score >= 70:
        assessed_level = "advanced"
    elif overall_score >= 40:
        assessed_level = "intermediate"
    else:
        assessed_level = "beginner"

    # Update assessments table
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE assessments
        SET status = 'completed',
            knowledge = ?,
            problem_solving = ?,
            practical = ?,
            industry_readiness = ?,
            overall = ?
        WHERE id = ?
        """,
        (
            dimension_scores.get("Knowledge", 70),
            dimension_scores.get("Problem Solving", 70),
            dimension_scores.get("Practical Skills", 70),
            dimension_scores.get("Industry Readiness", 70),
            overall_score,
            assessment_id
        )
    )

    # Upsert user_skills table
    cursor.execute(
        """
        INSERT INTO user_skills (id, user_id, skill, assessed_level, assessed_score, last_assessed_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, skill) DO UPDATE SET
            assessed_level = excluded.assessed_level,
            assessed_score = excluded.assessed_score,
            last_assessed_at = CURRENT_TIMESTAMP
        """,
        (str(uuid.uuid4()), user_id, skill, assessed_level, overall_score)
    )
    conn.commit()
    conn.close()

    # Trigger central reactive recomputation
    recompute_result = recompute_everything(user_id, trigger_event=f"{skill}_assessment_graded")

    feedback = f"Assessment completed for {skill.title()}! Scored {overall_score}/100 ({assessed_level.title()} Level). Dimension scores: Knowledge {dimension_scores['Knowledge']}%, Problem Solving {dimension_scores['Problem Solving']}%, Practical {dimension_scores['Practical Skills']}%, Industry Readiness {dimension_scores['Industry Readiness']}%."

    return {
        "assessment_id": assessment_id,
        "skill": skill,
        "overall_score": overall_score,
        "assessed_level": assessed_level,
        "dimension_scores": dimension_scores,
        "feedback": feedback,
        "recomputed_readiness": recompute_result["readiness"]["overall"],
        "roadmap_updated": True
    }
