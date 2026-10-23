"""
Diagnostic Skill Assessments Question Bank Seeder.
Seeds canonical skills, assessment examinations, and 270+ diagnostic questions
across all 9 core engineering domains with deterministic stable IDs.
"""

from __future__ import annotations

import decimal
import logging
import uuid
from typing import Any, Dict, List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skills import Skill
from app.models.assessments import Assessment, AssessmentQuestion
from app.db.seeds.assessment_bank import (
    PYTHON_QUESTIONS,
    JAVASCRIPT_TYPESCRIPT_QUESTIONS,
    JAVA_QUESTIONS,
    C_CPP_QUESTIONS,
    SQL_DATABASES_QUESTIONS,
    DSA_QUESTIONS,
    WEB_DEVELOPMENT_QUESTIONS,
    MACHINE_LEARNING_QUESTIONS,
    AI_LLM_QUESTIONS,
)

logger = logging.getLogger(__name__)

# Canonical namespace for deterministic UUIDv5 generation
COACHPATH_DNS_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "coachpath.dev")

CATEGORIES_SPEC: List[Dict[str, Any]] = [
    {
        "skill_id": "python",
        "skill_name": "Python",
        "skill_category": "language",
        "skill_description": "Python programming language, syntax, OOP, dunder protocols, concurrency, and memory management.",
        "assessment_title": "Python Programming Diagnostic",
        "assessment_description": "Comprehensive evaluation covering variables, syntax, functional paradigms, OOP, memory architecture, decorators, asyncio, and concurrency in Python.",
        "time_limit_minutes": 40,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": PYTHON_QUESTIONS,
    },
    {
        "skill_id": "javascript-typescript",
        "skill_name": "JavaScript & TypeScript",
        "skill_category": "language",
        "skill_description": "Modern ECMAScript, closures, prototypes, TypeScript type system, generics, and event loop concurrency.",
        "assessment_title": "JavaScript & TypeScript Diagnostic",
        "assessment_description": "In-depth diagnostic measuring lexical scoping, closures, prototype chains, microtask event loop timing, and advanced TypeScript type-level programming.",
        "time_limit_minutes": 40,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": JAVASCRIPT_TYPESCRIPT_QUESTIONS,
    },
    {
        "skill_id": "java",
        "skill_name": "Java",
        "skill_category": "language",
        "skill_description": "Java enterprise development, JVM architecture, memory model, multithreading, collections, and streams.",
        "assessment_title": "Java Programming Diagnostic",
        "assessment_description": "Rigorous diagnostic evaluating object-oriented architecture, collections framework internals, memory layout, GC mechanics, and concurrent Java programming.",
        "time_limit_minutes": 40,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": JAVA_QUESTIONS,
    },
    {
        "skill_id": "c-cpp",
        "skill_name": "C & C++",
        "skill_category": "language",
        "skill_description": "Low-level systems programming in C and C++, pointer arithmetic, dynamic memory, RAII, templates, and move semantics.",
        "assessment_title": "C & C++ Systems Programming Diagnostic",
        "assessment_description": "Evaluation of low-level systems mechanics, pointer arithmetic, manual heap management, virtual dispatch (vtables), RAII, smart pointers, and modern C++ move semantics.",
        "time_limit_minutes": 40,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": C_CPP_QUESTIONS,
    },
    {
        "skill_id": "sql-databases",
        "skill_name": "SQL & Relational Databases",
        "skill_category": "database",
        "skill_description": "Relational database schema modeling, SQL query authoring, window functions, indexing, and ACID transaction concurrency.",
        "assessment_title": "SQL & Relational Databases Diagnostic",
        "assessment_description": "Covers schema constraints, complex joins, CTEs, window functions, B-tree indexes, query plan evaluation (EXPLAIN), MVCC, and transaction isolation levels.",
        "time_limit_minutes": 40,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": SQL_DATABASES_QUESTIONS,
    },
    {
        "skill_id": "dsa",
        "skill_name": "Data Structures & Algorithms",
        "skill_category": "concept",
        "skill_description": "Algorithmic complexity, tree and graph structures, dynamic programming, sorting, and algorithmic design patterns.",
        "assessment_title": "Data Structures & Algorithms Diagnostic",
        "assessment_description": "Rigorous technical diagnosis of asymptotic analysis (Big-O), linear and non-linear data structures, graph traversals, and dynamic programming.",
        "time_limit_minutes": 45,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": DSA_QUESTIONS,
    },
    {
        "skill_id": "web-development",
        "skill_name": "Full-Stack Web Development",
        "skill_category": "architecture",
        "skill_description": "Full-stack client-server architecture, HTTP/2/3 protocols, browser rendering pipeline, web security (CORS/CSRF/XSS), and caching.",
        "assessment_title": "Full-Stack Web Development Diagnostic",
        "assessment_description": "Broad assessment examining HTTP specifications, responsive layouts, web security vulnerabilities, authentication architectures, performance metrics (CWV), and caching.",
        "time_limit_minutes": 40,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": WEB_DEVELOPMENT_QUESTIONS,
    },
    {
        "skill_id": "machine-learning",
        "skill_name": "Machine Learning",
        "skill_category": "concept",
        "skill_description": "Statistical learning, feature engineering, loss optimization, ensemble trees, classification metrics, and regularization.",
        "assessment_title": "Machine Learning Diagnostic",
        "assessment_description": "Comprehensive evaluation spanning supervised/unsupervised algorithms, regularization math, bias-variance trade-offs, dimensionality reduction, and evaluation metrics.",
        "time_limit_minutes": 40,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": MACHINE_LEARNING_QUESTIONS,
    },
    {
        "skill_id": "ai-llm",
        "skill_name": "AI & Large Language Models",
        "skill_category": "concept",
        "skill_description": "Transformer self-attention mechanics, subword tokenization, prompting strategies, PEFT/LoRA, RAG architectures, and agentic workflows.",
        "assessment_title": "Artificial Intelligence & LLMs Diagnostic",
        "assessment_description": "Advanced evaluation analyzing self-attention math, positional encodings, sampling algorithms, KV caching, PEFT/LoRA, RAG systems, and AI agent frameworks.",
        "time_limit_minutes": 45,
        "passing_threshold": decimal.Decimal("70.0"),
        "questions": AI_LLM_QUESTIONS,
    },
]


def generate_assessment_id(skill_id: str) -> uuid.UUID:
    """Generates a stable deterministic UUID for an assessment."""
    return uuid.uuid5(COACHPATH_DNS_NAMESPACE, f"assessment.{skill_id}")


def generate_question_id(skill_id: str, question_idx: int) -> uuid.UUID:
    """Generates a stable deterministic UUID for an assessment question."""
    return uuid.uuid5(COACHPATH_DNS_NAMESPACE, f"assessment.{skill_id}.question.{question_idx}")


async def seed_diagnostic_assessments(db: AsyncSession) -> Dict[str, Any]:
    """
    Idempotently seeds all 9 canonical skills, assessments, and their question banks.
    Returns audit counts of processed entities.
    """
    total_skills_seeded = 0
    total_assessments_seeded = 0
    total_questions_seeded = 0
    category_counts: Dict[str, Dict[str, int]] = {}

    for spec in CATEGORIES_SPEC:
        skill_id = spec["skill_id"]
        # 1. Upsert Skill
        skill = await db.get(Skill, skill_id)
        if not skill:
            skill = Skill(
                id=skill_id,
                name=spec["skill_name"],
                category=spec["skill_category"],
                description=spec["skill_description"],
                synonyms=[spec["skill_name"].lower()],
            )
            db.add(skill)
            total_skills_seeded += 1
        else:
            skill.name = spec["skill_name"]
            skill.category = spec["skill_category"]
            skill.description = spec["skill_description"]

        await db.flush()

        # 2. Upsert Assessment
        assessment_id = generate_assessment_id(skill_id)
        assessment = await db.get(Assessment, assessment_id)
        if not assessment:
            assessment = Assessment(
                id=assessment_id,
                skill_id=skill_id,
                title=spec["assessment_title"],
                description=spec["assessment_description"],
                time_limit_minutes=spec["time_limit_minutes"],
                passing_threshold=spec["passing_threshold"],
                is_active=True,
            )
            db.add(assessment)
            total_assessments_seeded += 1
        else:
            assessment.title = spec["assessment_title"]
            assessment.description = spec["assessment_description"]
            assessment.time_limit_minutes = spec["time_limit_minutes"]
            assessment.passing_threshold = spec["passing_threshold"]
            assessment.is_active = True

        await db.flush()

        # 3. Upsert Questions
        questions_list = spec["questions"]
        diff_counts = {"basic": 0, "intermediate": 0, "advanced": 0}

        for idx, q_data in enumerate(questions_list):
            q_id = generate_question_id(skill_id, idx + 1)
            diff = q_data["difficulty"]
            diff_counts[diff] = diff_counts.get(diff, 0) + 1

            question = await db.get(AssessmentQuestion, q_id)
            if not question:
                question = AssessmentQuestion(
                    id=q_id,
                    assessment_id=assessment_id,
                    prompt_text=q_data["prompt_text"],
                    code_snippet=q_data.get("code_snippet"),
                    options=q_data["options"],
                    correct_option_index=q_data["correct_option_index"],
                    explanation=q_data["explanation"],
                    difficulty=diff,
                    topic=q_data["topic"],
                )
                db.add(question)
                total_questions_seeded += 1
            else:
                question.prompt_text = q_data["prompt_text"]
                question.code_snippet = q_data.get("code_snippet")
                question.options = q_data["options"]
                question.correct_option_index = q_data["correct_option_index"]
                question.explanation = q_data["explanation"]
                question.difficulty = diff
                question.topic = q_data["topic"]
                total_questions_seeded += 1

        category_counts[skill_id] = {
            "total": len(questions_list),
            **diff_counts,
        }

    await db.commit()
    logger.info("Successfully seeded diagnostic assessments: %d questions across 9 categories.", total_questions_seeded)

    return {
        "skills_count": len(CATEGORIES_SPEC),
        "assessments_count": len(CATEGORIES_SPEC),
        "total_questions": total_questions_seeded,
        "categories": category_counts,
    }
