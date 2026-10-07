# CoachPath — Phase 2 Final Audit Report
> **Backend Foundation & PostgreSQL Data Layer (Phase 2A + Phase 2B + Phase 2C)**

---

## Executive Summary

This document certifies the comprehensive engineering audit of **Phase 2 (Backend Foundation & PostgreSQL Data Layer)** for the CoachPath platform.

The architectural foundation connecting:
$$\text{Next.js 14 Frontend} \longrightarrow \text{FastAPI Async Backend} \longrightarrow \text{SQLAlchemy 2.0 ORM} \longrightarrow \text{PostgreSQL 16 + pgvector}$$

has been inspected across architectural boundaries, relational and vector schema compliance, API contract compatibility, security safeguards, automated test suites, and documentation integrity.

**Audit Verdict**: **PHASE 2 COMPLETE**  
The backend foundation and database layer are verified, fully functional, and internally consistent.

---

## 1. What Was Implemented

### Phase 2A — Backend Foundation & Infrastructure
- **FastAPI Application Shell (`backend/app/main.py`)**: Factory-pattern application bootstrap with lifespan shutdown, CORS policies, Correlation ID tracing (`X-Request-ID`, `X-Process-Time-Ms`), and centralized RFC 7807 Problem Details exception handlers.
- **Centralized Settings (`backend/app/core/config.py`)**: Type-coerced Pydantic `BaseSettings` reading `.env` with dynamic CORS parsing and cached configuration.
- **Async Database Session Lifecycle (`backend/app/db/session.py`)**: Asynchronous SQLAlchemy 2.0 connection pool using `asyncpg` (`pool_pre_ping=True`, `pool_recycle=1800s`, `expire_on_commit=False`).
- **Data Access Abstractions (`backend/app/repositories/base.py`, `backend/app/services/base.py`)**: Generic async `BaseRepository[Model]` and `BaseService[Model]` decoupling HTTP endpoints from direct database queries.
- **Health Probes (`backend/app/api/routes/health.py`)**: `GET /api/v1/health` (process liveness) and `GET /api/v1/ready` (async `SELECT 1` database readiness probe with 503 fallback).
- **14 Structural Domain Routers (`backend/app/api/routes/`)**: Clean, non-faked placeholders matching `/docs/api-specification.md`.

### Phase 2B — PostgreSQL Relational & Vector Data Layer
- **37 SQLAlchemy 2.x Declarative Models (`backend/app/models/`)**: Complete entity graph matching `/docs/database-schema.md`:
  - `auth.py`: `User`, `UserProfile`, `UserSession`
  - `career.py`: `Role`, `CareerProfile`, `Education`, `Experience`, `Project`, `Certification`
  - `skills.py`: `Skill`, `RoleRequirement`, `UserSkill`, `SkillGap`
  - `assessments.py`: `Assessment`, `AssessmentQuestion`, `AssessmentAttempt`, `AssessmentAnswer`, `AssessmentResult`
  - `roadmap.py`: `Roadmap`, `RoadmapPhase`, `RoadmapTask`
  - `jobs.py`: `Job`, `JobSkill`, `JobMatch`
  - `resume.py`: `Resume`, `ResumeVersion`
  - `applications.py`: `Application`, `ApplicationStatusHistory`, `Recruiter`, `RecruiterContact`, `RecruiterMessage`, `Interview`, `InterviewQuestion`, `InterviewPreparation`
  - `readiness.py`: `CareerReadinessScore`
  - `audit.py`: `ActivityLog`, `AuditLog`
- **Dialect Helpers & Shared Mixins (`backend/app/models/base.py`)**:
  - `UUIDMixin`: Native UUIDv4 primary keys.
  - `TimestampMixin`: Automatic UTC `created_at` and `updated_at`.
  - Dialect-agnostic type wrappers: `StringArray()`, `TextArray()`, `JsonB()`, `Inet()`, and `VectorType(1536)` (native on PostgreSQL, JSON fallback on SQLite test runners).
- **Alembic Database Migration (`backend/alembic/versions/973e9bef3510_phase_2b_data_model.py`)**:
  - Automatically executes `CREATE EXTENSION IF NOT EXISTS "uuid-ossp"` and `"vector"`.
  - Generates all 37 tables, composite foreign keys, unique constraints, and indexes.
  - Bidirectional verification: validated both `alembic upgrade head` and `alembic downgrade -1`.
- **Master Taxonomy Seeding (`backend/scripts/seed.py`)**:
  - Idempotent script populating initial 7 benchmark roles, 15 canonical skills, and role benchmark requirements clearly identified as development/demo data.

---

## 2. Architecture Verification

| Check | Status | Verification Detail |
| :--- | :--- | :--- |
| **Route handlers not overloaded** | **PASS** | Route handlers in `backend/app/api/routes/` are lightweight controllers. No raw SQL or heavy logic is placed inside route functions. |
| **Business logic separated** | **PASS** | Logic belongs strictly to domain services (`BaseService` pattern). Services communicate with repositories via dependency injection. |
| **Database access separated** | **PASS** | Handled through async sessions via `get_db` FastAPI dependency and `BaseRepository`. Direct database access outside the repository layer is prohibited. |
| **Schemas separated from models** | **PASS** | Pydantic response/error schemas reside in `app/schemas/`. SQLAlchemy declarative models reside in `app/models/`. |
| **Configuration centralized** | **PASS** | `app/core/config.py` provides the single source of truth for runtime environment variables with Pydantic validation. |
| **Dependencies clean** | **PASS** | `backend/requirements.txt` contains pinned production dependencies (`fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `alembic`, `asyncpg`, `pgvector`). |
| **No circular imports** | **PASS** | Evaluated via Python AST and full module imports. All relationship declarations use string class targets with `if TYPE_CHECKING:` typing guards. |
| **No unnecessary coupling** | **PASS** | Clean boundaries exist between routers, services, repositories, and models. Frontend interacts solely via HTTP REST endpoints. |

---

## 3. Database Verification against `/docs/database-schema.md`

Every entity, column, index, and constraint has been verified against the Phase 0 specification:

### Entity Count & Identification
- **Total Tables**: Exactly 37 tables registered in `Base.metadata` and generated in Alembic migration `973e9bef3510`.
- **ID Strategy**:
  - Master canonical reference tables use normalized string keys: `roles.id` (e.g., `'backend-developer'`) and `skills.id` (e.g., `'postgresql'`).
  - All 35 user-owned and transactional entities use UUIDv4 (`UUIDMixin`).

### Foreign Keys & Cascade Integrity
- **GDPR "Right to be Forgotten"**: Deleting a record from `users` cascades (`ON DELETE CASCADE`) to all candidate tables: `user_profiles`, `user_sessions`, `career_profiles`, `resumes`, `assessment_attempts`, `applications`, `career_readiness_scores`, `activity_logs`, and `audit_logs`.
- **Career Profile Cascade**: Deleting a `career_profiles` record cascades to `education`, `experience`, `projects`, `certifications`, `user_skills`, `skill_gaps`, `roadmaps`, and `job_matches`.
- **Restricted Canonical Deletions**: Deleting a canonical `Role` or `Skill` while linked to active user profiles is blocked via `ON DELETE RESTRICT`.
- **Graceful Nullification**:
  - `applications.tailored_resume_version_id` is set to `ON DELETE SET NULL` so pruning a tailored resume does not destroy application history.
  - `roadmap_tasks.skill_id` and `interview_questions.skill_id` are set to `ON DELETE SET NULL`.

### Constraints & Indexes
- **Check Constraints**: Enforced on `roles`, `career_stage`, `work_preference`, `confidence_score` (0.00–1.00), `readiness_percentage` (0.0–100.0), `gpa` (0.0–4.0), and `time_limit_minutes > 0`.
- **Composite Unique Constraints**:
  - `role_requirements`: `UNIQUE(role_id, skill_id)`
  - `user_skills`: `UNIQUE(career_profile_id, skill_id)`
  - `skill_gaps`: `UNIQUE(career_profile_id, role_id)`
  - `job_skills`: `UNIQUE(job_id, skill_id)`
  - `job_matches`: `UNIQUE(career_profile_id, job_id)`
  - `applications`: `UNIQUE(user_id, job_id)`
  - `career_readiness_scores`: `UNIQUE(user_id, recorded_date)` (prevents unbounded duplicate telemetry per user per day)
- **Vector Search Support**:
  - `skills.embedding` (`vector(1536)`) and `jobs.embedding` (`vector(1536)`).

---

## 4. API Compatibility Verification against `/docs/api-specification.md`

| Domain Router | Endpoint Prefix | Contract Verification Status |
| :--- | :--- | :--- |
| **Health & Readiness** | `/api/v1/health`, `/api/v1/ready` | **Implemented & Live** (200 / 503 probes verified). |
| **Authentication** | `/api/v1/auth` | **Structural Placeholder** (Scheduled for Phase 3). Zero fake auth tokens. |
| **Career Profile** | `/api/v1/profile` | **Structural Placeholder** (Scheduled for Phase 3). Compatible with models. |
| **Onboarding** | `/api/v1/onboarding` | **Structural Placeholder** (Scheduled for Phase 4). |
| **Resumes** | `/api/v1/resume` | **Structural Placeholder** (Scheduled for Phase 5 & 11). |
| **Assessments** | `/api/v1/assessments` | **Structural Placeholder** (Scheduled for Phase 6). |
| **Skills & Gaps** | `/api/v1/skills` | **Structural Placeholder** (Scheduled for Phase 7). |
| **Roadmaps** | `/api/v1/roadmap` | **Structural Placeholder** (Scheduled for Phase 8). |
| **Jobs & Matching** | `/api/v1/jobs` | **Structural Placeholder** (Scheduled for Phase 9 & 10). |
| **Applications** | `/api/v1/applications` | **Structural Placeholder** (Scheduled for Phase 12). |
| **Recruiters** | `/api/v1/recruiters` | **Structural Placeholder** (Scheduled for Phase 13). |
| **Interviews** | `/api/v1/interviews` | **Structural Placeholder** (Scheduled for Phase 14). |
| **Readiness** | `/api/v1/career-readiness` | **Structural Placeholder** (Scheduled for Phase 15). |
| **Dashboard** | `/api/v1/dashboard` | **Structural Placeholder** (Composite orchestration). |
| **Settings** | `/api/v1/settings` | **Structural Placeholder** (Scheduled for Phase 16). |

---

## 5. Security Verification

1. **No Secrets in Source Control**: Verified via `git grep` and repository scans.
2. **Environment Variable Sovereignty**: `.env` and `.env*.local` are explicitly ignored in `.gitignore`. A documented `.env.example` provides explicit configuration templates.
3. **CORS Hardening**: Configurable via `CORS_ORIGINS` with comma-delimited parsing, defaulting to frontend port `3000`.
4. **Information Leakage Prevention**:
   - `SQLAlchemyError` and unhandled `Exception` handlers in `app/middleware/error_handler.py` return sanitized static RFC 7807 problem details with an opaque `request_id`.
   - Internal stack traces and database schemas are logged server-side only.
5. **Production Safety Hardening (Implemented in Phase 2C)**:
   - Added a Pydantic `model_validator` in `app/core/config.py`: When `ENVIRONMENT=production`, `DEBUG` is automatically forced to `False`, and default insecure placeholder `SECRET_KEY` values are rejected at startup.
   - FastAPI interactive documentation (`/docs`, `/redoc`, `/openapi.json`) is automatically disabled when `DEBUG=False`.
6. **Object Storage Boundaries**: Private file paths stored in `resumes.storage_path` point to isolated UUID directories rather than public web assets.

---

## 6. Tests Executed & Results

```
============================= test session starts ==============================
platform darwin -- Python 3.13.6, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/anmolsharma/Desktop/Coach_Path/backend
configfile: pytest.ini
collected 34 items

backend/tests/test_db.py::test_repository_and_service_crud PASSED        [  2%]
backend/tests/test_errors.py::test_not_found_endpoint_rfc7807 PASSED     [  5%]
backend/tests/test_errors.py::test_correlation_id_preservation PASSED    [  8%]
backend/tests/test_errors.py::test_custom_app_exceptions PASSED          [ 11%]
backend/tests/test_health.py::test_root_endpoint PASSED                  [ 14%]
backend/tests/test_health.py::test_health_liveness PASSED                [ 17%]
backend/tests/test_health.py::test_ready_endpoint_healthy PASSED         [ 20%]
backend/tests/test_health.py::test_ready_endpoint_unhealthy PASSED       [ 23%]
backend/tests/test_health.py::test_production_environment_security PASSED [ 26%]
backend/tests/test_models.py::test_user_and_profile_creation_and_cascade PASSED [ 29%]
backend/tests/test_models.py::test_user_unique_constraint PASSED         [ 32%]
backend/tests/test_models.py::test_career_profile_and_evidence_graph PASSED [ 35%]
backend/tests/test_models.py::test_skills_taxonomy_and_user_skills PASSED [ 38%]
backend/tests/test_models.py::test_assessments_hierarchy_and_results PASSED [ 41%]
backend/tests/test_models.py::test_dynamic_roadmap_structure PASSED      [ 44%]
backend/tests/test_models.py::test_jobs_and_semantic_matching PASSED     [ 47%]
backend/tests/test_models.py::test_resumes_and_truthful_tailoring PASSED [ 50%]
backend/tests/test_models.py::test_applications_kanban_and_interviews PASSED [ 52%]
backend/tests/test_models.py::test_readiness_and_audit_logging PASSED    [ 55%]
backend/tests/test_models.py::test_canonical_taxonomy_seeding_idempotence PASSED [ 58%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/auth-auth] PASSED [ 61%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/profile-profile] PASSED [ 64%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/onboarding-onboarding] PASSED [ 67%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/resume-resume] PASSED [ 70%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/assessments-assessments] PASSED [ 73%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/skills-skills] PASSED [ 76%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/roadmap-roadmap] PASSED [ 79%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/jobs-jobs] PASSED [ 82%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/applications-applications] PASSED [ 85%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/recruiters-recruiters] PASSED [ 88%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/interviews-interviews] PASSED [ 91%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/career-readiness-career-readiness] PASSED [ 94%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/dashboard-dashboard] PASSED [ 97%]
backend/tests/test_routers_structure.py::test_domain_router_structural_placeholder[/api/v1/settings-settings] PASSED [100%]

============================== 34 passed in 1.58s ==============================
```

- **Frontend Verification**:
  - `npm run lint`: **0 ESLint errors or warnings**.
  - `npm run build`: **Compiled successfully; 24/24 static routes generated**.

---

## 7. Problems Discovered During Audit

1. **Alembic Autogenerate Missing Imports**: Autogenerated migration scripts omitted imports for `pgvector`, `String`, and `Text`, which would trigger `NameError` on execution.
2. **Missing PostgreSQL Extensions in Migrations**: The baseline migration lacked explicit `CREATE EXTENSION IF NOT EXISTS "uuid-ossp"` and `"vector"`.
3. **Async Lazy Loading MissingGreenlet Error**: Accessing model relationships in async tests without explicit loading strategy caused `MissingGreenlet` errors because SQLAlchemy defaults to synchronous lazy loading.
4. **SQLite PRAGMA Thread Context in aiosqlite**: Attempting to set SQLite pragmas inside connection listeners called into aiosqlite worker threads improperly, causing unawaited coroutine warnings.
5. **OpenAPI / Swagger Docs Always Enabled**: FastAPI documentation endpoints were enabled unconditionally in all environments.

---

## 8. Problems Fixed During Audit

1. **Fixed Migration Script Header**: Added explicit imports for `pgvector`, `pgvector.sqlalchemy`, `sa.String`, and `sa.Text` to `backend/alembic/versions/973e9bef3510_phase_2b_data_model.py`.
2. **Added PostgreSQL Extension Invocations**: Added dialect-aware `op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')` and `op.execute('CREATE EXTENSION IF NOT EXISTS "vector";')` inside migration upgrade.
3. **Standardized Eager Loading**: Updated model tests to use `selectinload` for asynchronous relationship traversal across all queries.
4. **Clean SQLite Foreign Key Pragma Execution**: Configured `test_engine` in `backend/tests/conftest.py` to execute `PRAGMA foreign_keys=ON;` within `async with engine.begin() as conn:`.
5. **Production Safety Hardening**:
   - Added Pydantic `model_validator` in `app/core/config.py` enforcing `DEBUG=False` in production and rejecting default insecure secret keys.
   - Configured `docs_url`, `redoc_url`, and `openapi_url` in `app/main.py` to evaluate to `None` when `DEBUG=False`.

---

## 9. Remaining Risks & Monitoring Notes

- **pgvector Extension Availability in Target Cloud Database**: When deploying to managed cloud PostgreSQL (e.g., AWS RDS, Supabase, Cloud SQL), the `vector` extension must be enabled by the database administrator if the database user lacks superuser privileges.
- **SQLite vs. PostgreSQL Vector Operator Semantics**: Unit tests run against `aiosqlite` with vector fallback to JSON arrays. In Phase 9/10, semantic cosine similarity searches (`<->` / `<=>` operators) must be executed against genuine PostgreSQL with `pgvector` enabled (via Docker in CI/CD).
- **HNSW Index Building on Empty Tables**: HNSW indexes in PostgreSQL are most efficient when constructed with data present; the migration creates standard indexes that will populate with ingested roles and jobs.

---

## 10. Exact Phase 3 Prerequisites

Before starting **Phase 3 (Authentication and User Profile Graph)**, verify the following are in place:

1. **Existing Models Ready**:
   - [`User`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/models/auth.py#L26), [`UserProfile`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/models/auth.py#L125), and [`UserSession`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/models/auth.py#L201) are already mapped and tested.
   - [`CareerProfile`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/models/career.py#L104), [`Education`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/models/career.py#L225), and [`Experience`](file:///Users/anmolsharma/Desktop/Coach_Path/backend/app/models/career.py#L297) are mapped and tested.
2. **Required Dependencies to Add in Phase 3**:
   - Password hashing: `argon2-cffi` or `passlib[argon2]`
   - Token creation & validation: `pyjwt` or `python-jose[cryptography]`
3. **Endpoints to Implement in Phase 3**:
   - Auth routes under `/api/v1/auth`: `POST /register`, `POST /login`, `POST /refresh`, `POST /logout`, `GET /me`.
   - Profile routes under `/api/v1/profile`: `GET /profile`, `PUT /profile`, `GET /career-profile`, `PUT /career-profile`.
4. **Security Enforcements Needed in Phase 3**:
   - Auth dependency `get_current_user` in `app/api/dependencies.py`.
   - Password strength validation (min 8 chars, mixed case, numbers, special characters).
   - Session revocation ledger validation in `user_sessions`.

---

## 11. Declaration

# PHASE 2 COMPLETE

The backend foundation and database layer are verified, fully functional, and internally consistent. Engineering work is cleared to proceed to **Phase 3: Authentication and User Profile**.
