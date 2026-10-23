# CoachPath Diagnostic Skill Assessments Overhaul: Final Audit & Report

> **Document Version**: 1.0.0  
> **Status**: Completed, Fully Tested, and Operational  
> **Audit Date**: October 22, 2026  
> **Target Audience**: Engineering Leadership, Product Management, Quality Assurance  

---

## 1. Executive Summary

The Diagnostic Skill Assessments feature overhaul has been completed. The system has transitioned from a superficial, single-question static modal prototype into an end-to-end, multi-question technical evaluation platform backed by a **270-question expert question bank**, server-side deterministic scoring, granular topic and difficulty breakdowns, persistent resume capabilities, and a Next.js test-taking interface.

All acceptance criteria across database migrations, seeding, schemas, service orchestration, API routing, frontend integration, and automated testing are satisfied.

| Assessment Area | Target Requirement | Implemented Status | Verification Result |
|---|---|---|---|
| **Categories Supported** | Exactly 9 specified technical domains | 9 canonical domains active in DB | **PASS** |
| **Question Bank Volume** | $\ge 30$ questions per category ($\ge 270$ total) | 270 total questions (30 per category) | **PASS** |
| **Difficulty Distribution** | $\ge 10$ Basic, $\ge 10$ Intermediate, $\ge 10$ Advanced | Exactly 10 Basic, 10 Intermediate, 10 Advanced per domain | **PASS** |
| **Attempt Sizing** | Exactly 20 questions per attempt | 20 questions (7 Basic, 7 Intermediate, 6 Advanced) | **PASS** |
| **Answer Key Protection** | Sealed on server during test execution | Zero answer keys or explanations exposed in active sessions | **PASS** |
| **State Persistence** | Resumes identical attempt on refresh | Attempt question sequence & answers persisted in PostgreSQL | **PASS** |
| **Retake Support** | Retakes generate fresh attempts while preserving history | Historical attempts permanently retained without overwrite | **PASS** |
| **Automated Tests** | Full test coverage of bank, logic, and APIs | 123/123 tests passing in backend (0 failures) | **PASS** |
| **Frontend Production Build** | Zero TypeScript errors, clean production build | Next.js 14 compiles 25/25 static pages cleanly | **PASS** |

---

## 2. Root Cause of Original One-Question Limitation

Inspection of the codebase revealed that the original single-question limitation stemmed from the following factors:

1. **Frontend Static Mockup**:
   - Location: `frontend/src/app/(app)/assessments/page.tsx` (lines 131–195).
   - The page rendered static mock data (`mockAssessments`) and triggered a hardcoded modal dialog containing a single hardcoded question regarding Redis distributed caching (`When scaling a high-throughput API with distributed caching in Redis...`).
   - Clicking "Submit Answer" simply toggled a local boolean state (`hasSubmittedAnswer = true`), and clicking "Complete Assessment" displayed a browser `alert()` dialog before closing the modal without sending any network request.

2. **Backend Route Placeholder**:
   - Location: `backend/app/api/routes/assessments.py`.
   - The assessments route was an unmounted placeholder returning `{"module": "assessments", "status": "placeholder", "phase": "Phase 6"}`.
   - There was zero backend logic for question sampling, session management, or grading.

3. **Empty Database Tables**:
   - Although the baseline PostgreSQL migration defined `assessments`, `assessment_questions`, `assessment_attempts`, `assessment_answers`, and `assessment_results`, the tables contained **0 rows**.
   - No question bank existed in the codebase, and no seeding script had been authored.

---

## 3. Files Created and Modified

### 3.1 Backend Files Created & Modified

| File Path | Nature | Purpose |
|---|---|---|
| `backend/app/models/assessments.py` | Modified | Added `topic` to `AssessmentQuestion`, `question_ids` to `AssessmentAttempt`, and `topic_breakdown` & `difficulty_breakdown` to `AssessmentResult`. |
| `backend/alembic/versions/c3d4e5f6a1b2_phase_6_diagnostic_assessments.py` | Created | Alembic migration adding the 4 enhancement columns to PostgreSQL. |
| `backend/app/db/seeds/assessment_bank/__init__.py` | Created | Module aggregator for the 9 domain question banks. |
| `backend/app/db/seeds/assessment_bank/python_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering Python syntax, OOP, dunder methods, and asyncio. |
| `backend/app/db/seeds/assessment_bank/javascript_typescript_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering scoping, closures, event loop, and advanced TypeScript. |
| `backend/app/db/seeds/assessment_bank/java_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering JMM, collections, GC generations, multithreading, and Loom. |
| `backend/app/db/seeds/assessment_bank/c_cpp_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering pointers, memory leaks, RAII, vtables, and move semantics (tagged C vs C++). |
| `backend/app/db/seeds/assessment_bank/sql_databases_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering constraints, CTEs, window functions, MVCC, and indexing. |
| `backend/app/db/seeds/assessment_bank/dsa_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering Big-O, heaps, trees, graph algorithms, and DP. |
| `backend/app/db/seeds/assessment_bank/web_development_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering HTTP/3, CORS/CSRF/XSS, rendering, caching, and Core Web Vitals. |
| `backend/app/db/seeds/assessment_bank/machine_learning_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering regularization, metrics, ensembles, PCA, and optimization. |
| `backend/app/db/seeds/assessment_bank/ai_llm_questions.py` | Created | 30 questions (10 basic, 10 intermediate, 10 advanced) covering attention math, RoPE, LoRA, FlashAttention, RAG, and agents. |
| `backend/app/db/seeds/assessment_seeder.py` | Created | Idempotent seeder creating 9 canonical skills, assessments, and 270 questions using deterministic UUIDv5s. |
| `backend/app/schemas/assessments.py` | Created | Pydantic contracts for categories, public attempts, answer submissions, and graded results. |
| `backend/app/services/assessments.py` | Created | Core service managing 20-question attempts, answer persistence, deterministic grading, and UserSkill profile updates. |
| `backend/app/api/routes/assessments.py` | Modified | Complete FastAPI router implementing all 8 assessment endpoints. |
| `backend/app/main.py` | Modified | Integrated auto-seeding of diagnostic assessments into application lifespan. |
| `backend/tests/test_assessments.py` | Created | 8 test suites verifying bank counts, 7/7/6 quotas, answer hiding, scoring math, retakes, and 403 security. |
| `backend/tests/test_routers_structure.py` | Modified | Updated router status checks for authenticated `/assessments` route. |

### 3.2 Frontend Files Created & Modified

| File Path | Nature | Purpose |
|---|---|---|
| `frontend/src/types/index.ts` | Modified | Added TypeScript interfaces for `AssessmentCategoryItem`, `AttemptQuestionPublic`, `AttemptSession`, `AssessmentResultResponse`, and breakdowns. |
| `frontend/src/lib/assessment-client.ts` | Created | API client handling assessment listing, attempt starts, live answer submissions, completion, and history queries. |
| `frontend/src/components/assessments/assessment-runner.tsx` | Created | 20-question test runner with jump palette, progress bar, countdown timer, code snippet viewer, and auto-syncing option choices. |
| `frontend/src/components/assessments/assessment-result-view.tsx` | Created | Graded results view with radial score, proficiency band, topic and difficulty breakdown bars, and 20-question review with explanations. |
| `frontend/src/app/(app)/assessments/page.tsx` | Modified | Replaced static modal with live 9-category grid, managing view transitions between catalog, runner, and result screens. |

---

## 4. Assessment Categories & Question Bank Audit

A live database audit was executed via `AsyncSessionLocal` against the PostgreSQL database:

```
Total Assessments: 9
  [python] "Python Programming Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
  [javascript-typescript] "JavaScript & TypeScript Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
  [java] "Java Programming Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
  [c-cpp] "C & C++ Systems Programming Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
  [sql-databases] "SQL & Relational Databases Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
  [dsa] "Data Structures & Algorithms Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
  [web-development] "Full-Stack Web Development Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
  [machine-learning] "Machine Learning Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
  [ai-llm] "Artificial Intelligence & LLMs Diagnostic": total=30 (basic=10, intermediate=10, advanced=10, unique_topics=30)
Total Questions across database: 270
```

Every category satisfies:
- $\ge 30$ questions
- $\ge 10$ basic questions
- $\ge 10$ intermediate questions
- $\ge 10$ advanced questions
- Exactly 4 options per question with zero duplicates
- Valid `correct_option_index` in range $[0, 3]$
- Detailed, pedagogical explanations

---

## 5. Attempt Management & Question Selection Logic

### 5.1 Quota Enforcement (20 Questions per Attempt)

When an attempt is initialized via `POST /api/v1/assessments/{category_id}/start`:
1. The engine retrieves all active questions for that category.
2. It samples without replacement:
   - Exactly **7 Basic** questions
   - Exactly **7 Intermediate** questions
   - Exactly **6 Advanced** questions
3. The questions are sequenced in ascending difficulty order (1–7 basic, 8–14 intermediate, 15–20 advanced).
4. The ordered UUID list is serialized to `assessment_attempts.question_ids`.

### 5.2 Resume Capability

When a candidate revisits `/assessments`:
- If an attempt is `in_progress`, the category card highlights a pulsing **"Resume Diagnostic"** badge.
- Clicking the badge or refreshing the runner queries the existing attempt.
- The server returns the exact same 20 questions in their original order along with previously saved answers (`current_answers`).

---

## 6. Server-Side Deterministic Grading & Scoring Engine

### 6.1 Formula

$$\text{Score Percentage} = \text{round}\left( \frac{\text{Correct Answers Count}}{20} \times 100.0, 1 \right)$$

Unanswered questions are scored as incorrect (0 points).

### 6.2 Proficiency Classifications

- $\ge 85.0\%$: **Strong**
- $\ge 70.0\%$: **Proficient**
- $\ge 50.0\%$: **Developing**
- $< 50.0\%$: **Foundational**

### 6.3 Atomicity & Career Profile Integration

Upon attempt completion in `AssessmentService.complete_attempt`:
1. An `AssessmentResult` is recorded with strengths, weaknesses, milestones, and JSONB breakdowns.
2. The attempt status transitions to `completed`.
3. The candidate's `CareerProfile.user_skills` entry for that domain is calibrated:
   - `confidence_score` updated based on score percentage
   - `is_verified = true` if score clears passing threshold ($70.0\%$)
   - `proficiency_tier` updated to `mastered`, `proficient`, or `demonstrated`
   - `primary_source = 'assessment'`

---

## 7. API Endpoints Implemented

| Endpoint | Method | Status Code | Summary |
|---|---|---|---|
| `/api/v1/assessments` | `GET` | 200 | List all 9 assessment categories with user status & scores. |
| `/api/v1/assessments/history` | `GET` | 200 | Retrieve historical attempts for the candidate. |
| `/api/v1/assessments/{category_id}` | `GET` | 200 | Category detail, syllabus, and question bank stats. |
| `/api/v1/assessments/{category_id}/start` | `POST` | 200 | Start a new 20-question attempt or resume active attempt. |
| `/api/v1/assessments/attempts/{id}` | `GET` | 200 | Get active attempt questions and recorded choices (answer key masked). |
| `/api/v1/assessments/attempts/{id}/answer` | `POST` | 200 | Record or update selected option index for a question. |
| `/api/v1/assessments/attempts/{id}/complete` | `POST` | 200 | Grade attempt, persist result, and reveal explanations. |
| `/api/v1/assessments/attempts/{id}/result` | `GET` | 200 | Get graded review for a completed attempt. |

---

## 8. Frontend Components Implemented

1. **`AssessmentRunner`** (`frontend/src/components/assessments/assessment-runner.tsx`):
   - Interactive 20-button jump palette showing answered (green) vs unanswered (slate) vs current (brand ring) states.
   - Live countdown timer based on assessment duration limit.
   - Code snippet box rendered in high-contrast dark terminal style.
   - Instant optimistic selection saving with background server synchronization.
   - Confirmation dialog preventing accidental early submission with unanswered questions.

2. **`AssessmentResultView`** (`frontend/src/components/assessments/assessment-result-view.tsx`):
   - Calibrated score radial display with proficiency badge.
   - Subtopic-level progress bars and difficulty-tier performance metrics.
   - Full 20-question review filterable by All, Correct, and Incorrect.
   - Color-coded choices (user choice in green or red, correct choice with badge).
   - Pedagogical explanation cards explaining technical rationale for every question.
   - Direct "Retake Diagnostic Test" button triggering a fresh attempt.

3. **`AssessmentsPage`** (`frontend/src/app/(app)/assessments/page.tsx`):
   - Replaced static modal mockup with dynamic 9-card category grid.
   - Filter tabs: All, Ready to Take, In Progress, Completed & Verified.
   - Seamless view state routing (`catalog` $\rightarrow$ `runner` $\rightarrow$ `result`).

---

## 9. Test Results & Verification

### 9.1 Backend Test Suite

The assessment test suite was run hermetically:

```
$ pytest tests/test_assessments.py -v
============================== 8 passed in 2.59s ===============================
```

Full backend test suite:
```
$ pytest tests/
======================= 123 passed, 5 warnings in 15.19s =======================
```

All 123 tests across authentication, career profile, AI onboarding, resume parsing, and diagnostic assessments pass with 0 errors.

### 9.2 Frontend Static Audits & Production Build

TypeScript typecheck:
```
$ npx tsc --noEmit
Exit code: 0 (Zero errors)
```

ESLint audit:
```
$ npm run lint
✔ No ESLint warnings or errors
```

Next.js Production Build:
```
$ npm run build
✓ Compiled successfully
✓ Generating static pages (25/25)
Route /assessments compiled cleanly (10.9 kB)
```

---

## 10. Security & Privacy Audit

1. **Sealed Answer Keys**: Verification confirmed that `AttemptQuestionPublic` omits `correct_option_index` and `explanation`. Candidates cannot inspect browser network responses to identify correct choices before submitting.
2. **Horizontal Privilege Enforcement**: Calling attempt endpoints with credentials belonging to another user returns `403 Forbidden` (`test_cross_user_attempt_access_forbidden`).
3. **Immutability After Grading**: Attempts marked `completed` reject further answers (`409 Conflict`).
4. **Deterministic autograding**: All grading is performed in Python code on the server, eliminating any risk of prompt manipulation or LLM inconsistencies.

---

## 11. Conclusion

The CoachPath Diagnostic Skill Assessments overhaul is fully operational. The one-question limitation has been eradicated. Users can select from 9 technical domains, complete authentic 20-question diagnostic assessments, resume progress upon refresh, receive immediate server-graded results with topic breakdowns, and review pedagogical explanations.
