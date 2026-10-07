# CoachPath — Backend Architecture Specification

**Document Version**: 1.1.0  
**Phase**: Phase 2B (PostgreSQL Data Layer Implementation)  
**Status**: Authoritative Reference  
**Last Updated**: October 2026  

---

## 1. Executive Summary & Objective

CoachPath's backend service provides high-throughput, asynchronous career intelligence APIs supporting deterministic skill assessment, milestone roadmap execution, semantic vector search, and resume optimization. 

The primary objective of **Phase 2A** is to establish the production-grade **FastAPI backend foundation**, decoupled from specific domain business logic (Phases 3–16). The architecture implements strict hexagonal separation between routes, validation schemas, business services, and database repositories, configured for asynchronous PostgreSQL access via SQLAlchemy 2.0 and Alembic.

---

## 2. Technology Stack & Architectural Decisions

| Layer | Selection | Version | Decision Rationale |
| :--- | :--- | :--- | :--- |
| **API Runtime** | Python / FastAPI | 3.13+ / 0.115+ | Native async I/O, OpenAPI 3.1 generation, and high RPS throughput. |
| **Data Validation** | Pydantic v2 | 2.13+ | High-speed C-core (`pydantic-core`) validation and schema serialization. |
| **ORM / Data Access** | SQLAlchemy 2.0 (Async) | 2.1+ | Declarative typed mapping, Unit of Work pattern, connection pooling. |
| **Database Driver** | `asyncpg` | 0.32+ | High-performance asynchronous binary PostgreSQL protocol driver. |
| **Schema Migrations** | Alembic | 1.20+ | Version-controlled, reproducible database DDL schema evolution. |
| **Testing Suite** | Pytest + `pytest-asyncio` | 9.1+ / 1.4+ | Asynchronous fixtures, isolated in-memory testing via `aiosqlite`. |
| **HTTP Client** | `httpx` | 0.28+ | Async HTTP transport for integration testing and external API interactions. |

---

## 3. Layered Architecture & Request Lifecycle

CoachPath enforces a strict vertical separation of concerns. Business logic is strictly prohibited from living inside route handlers:

$$\text{Incoming Request} \longrightarrow \text{Correlation Middleware} \longrightarrow \text{FastAPI Route} \longrightarrow \text{Pydantic Schema Validation} \longrightarrow \text{Domain Service} \longrightarrow \text{Repository} \longrightarrow \text{PostgreSQL Session}$$

```
+-----------------------------------------------------------------------------------+
| 1. HTTP Ingestion & Middleware Layer                                              |
| - Correlation ID injection (X-Request-ID, X-Process-Time-Ms)                      |
| - CORS Middleware (Strict origin whitelist)                                       |
| - Centralized RFC 7807 Error Interception                                         |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| 2. API Route Controllers (/api/v1/*)                                              |
| - Route definition, path parameters, query parsing, HTTP status codes             |
| - Zero business logic; orchestrates Service layer calls                           |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| 3. Domain Services (app/services/*)                                               |
| - Core business logic, domain validation, multi-entity orchestration             |
| - Pure Python logic independent of transport protocols                            |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| 4. Data Repositories (app/repositories/*)                                         |
| - Raw SQLAlchemy queries, transactions, pagination, indexing filters              |
| - Generic BaseRepository[Model] abstraction                                       |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| 5. Database Layer (PostgreSQL / asyncpg)                                          |
| - Async connection pool (pool_size=10, max_overflow=20, recycle=1800s)           |
| - DeclarativeBase models with UUID and UTC timestamp mixins                       |
+-----------------------------------------------------------------------------------+
```

---

## 4. Directory Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI factory, middleware, and lifespan
│   ├── core/
│   │   ├── config.py               # Pydantic BaseSettings environment loader
│   │   └── exceptions.py           # Custom domain exception classes
│   ├── api/
│   │   ├── router.py               # Master router mounting /api/v1 routes
│   │   ├── dependencies.py         # Reusable dependency injection (DB session, request ID)
│   │   └── routes/                 # Domain router controllers
│   │       ├── health.py           # /health and /ready diagnostic probes
│   │       ├── auth.py             # /auth placeholder
│   │       ├── profile.py          # /profile placeholder
│   │       ├── onboarding.py       # /onboarding placeholder
│   │       ├── resume.py           # /resume placeholder
│   │       ├── assessments.py      # /assessments placeholder
│   │       ├── skills.py           # /skills placeholder
│   │       ├── roadmap.py          # /roadmap placeholder
│   │       ├── jobs.py             # /jobs placeholder
│   │       ├── applications.py     # /applications placeholder
│   │       ├── recruiters.py       # /recruiters placeholder
│   │       ├── interviews.py       # /interviews placeholder
│   │       ├── readiness.py        # /career-readiness placeholder
│   │       ├── dashboard.py        # /dashboard placeholder
│   │       └── settings.py         # /settings placeholder
│   ├── db/
│   │   ├── base.py                 # Metadata export for Alembic detection
│   │   └── session.py              # Async engine pool, sessionmaker, and get_db()
│   ├── models/
│   │   ├── __init__.py             # Model registry hub
│   │   └── base.py                 # DeclarativeBase, UUIDMixin, TimestampMixin
│   ├── schemas/
│   │   └── error.py                # RFC 7807 Problem Details schemas
│   ├── services/
│   │   └── base.py                 # Generic BaseService abstraction
│   ├── repositories/
│   │   └── base.py                 # Generic BaseRepository abstraction
│   └── middleware/
│       ├── correlation.py          # Correlation ID injection and logging
│       └── error_handler.py        # Centralized exception handlers
├── alembic/
│   ├── env.py                      # Async migration runner bound to Base.metadata
│   ├── script.py.mako              # Migration script template
│   └── versions/                   # Migration revision scripts
├── tests/
│   ├── conftest.py                 # In-memory async SQLite fixtures and AsyncClient
│   ├── test_health.py              # Liveness and readiness test suite
│   ├── test_errors.py              # RFC 7807 problem details and correlation tests
│   ├── test_routers_structure.py   # Mounted router verification
│   └── test_db.py                  # Repository and service CRUD tests
├── Dockerfile                      # Production-ready Python 3.13 container
├── pytest.ini                      # Pytest discovery and asyncio configuration
├── requirements.txt                # Pinned production and test dependencies
└── README.md                       # Local development guide
```

---

## 5. Centralized Configuration System

The configuration subsystem (`app/core/config.py`) leverages Pydantic's `BaseSettings`:
- Reads from local `.env` or container environment variables with strict type coercion.
- Parses comma-delimited `CORS_ORIGINS` dynamically.
- Caches the settings instance via `@lru_cache()` to prevent redundant file I/O.

### Environment Variable Contract
```ini
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DATABASE_URL=postgresql+asyncpg://coachpath_user:coachpath_password@localhost:5432/coachpath_db
SECRET_KEY=insecure-default-change-in-production-secret-key-32-chars-min
```

---

## 6. Database Connection Lifecycle & Models

### Connection Pooling
- Built on SQLAlchemy 2.0 `create_async_engine()`.
- Uses `pool_pre_ping=True` to automatically recycle stale connections after network interruptions.
- Employs `async_sessionmaker(..., expire_on_commit=False)` to prevent premature attribute eviction during async operations.
- Application lifespan handler (`lifespan`) in `app/main.py` explicitly calls `engine.dispose()` on process SIGTERM/SIGINT.

### Declarative Model Standards
All domain entities inherit from `Base` (`app/models/base.py`) and are organized into 10 modular domain packages under `app/models/`:
1. `auth.py`: `User`, `UserProfile`, `UserSession`
2. `career.py`: `Role`, `CareerProfile`, `Education`, `Experience`, `Project`, `Certification`
3. `skills.py`: `Skill`, `RoleRequirement`, `UserSkill`, `SkillGap`
4. `assessments.py`: `Assessment`, `AssessmentQuestion`, `AssessmentAttempt`, `AssessmentAnswer`, `AssessmentResult`
5. `roadmap.py`: `Roadmap`, `RoadmapPhase`, `RoadmapTask`
6. `jobs.py`: `Job`, `JobSkill`, `JobMatch`
7. `resume.py`: `Resume`, `ResumeVersion`
8. `applications.py`: `Application`, `ApplicationStatusHistory`, `Recruiter`, `RecruiterContact`, `RecruiterMessage`, `Interview`, `InterviewQuestion`, `InterviewPreparation`
9. `readiness.py`: `CareerReadinessScore`
10. `audit.py`: `ActivityLog`, `AuditLog`

### Database Engine & Types
- **UUIDs**: Standard `sa.Uuid(as_uuid=True)` client-safe UUIDv4 primary keys.
- **Auditing**: `TimestampMixin` maintaining timezone-aware `created_at` and `updated_at` in UTC.
- **Arrays**: `StringArray(length)` and `TextArray()` compiling to native `VARCHAR[]` / `TEXT[]` on PostgreSQL with SQLite JSON fallbacks for testing.
- **JSON**: `JsonB()` compiling to PostgreSQL `JSONB` with SQLite JSON fallbacks.
- **Vectors**: `VectorType(1536)` mapping to `pgvector` HNSW representations on PostgreSQL.
- **Network**: `Inet()` compiling to PostgreSQL `INET` with `VARCHAR(45)` fallback on SQLite.

### Alembic Migration & Seeding
- **Baseline Revision**: `00b73b0a6635_initial_schema_baseline.py`
- **Phase 2B Revision**: `973e9bef3510_phase_2b_data_model.py` (executes PostgreSQL extensions `uuid-ossp` and `vector`, generates all 37 tables, composite indexes, and foreign keys with `ON DELETE CASCADE / RESTRICT / SET NULL`).
- **Seed Script**: `backend/scripts/seed.py` idempotently seeds canonical benchmark roles (7 roles), core skills ontology (15+ skills), and benchmark requirements.

---

## 7. Standardized Error Handling (RFC 7807)

CoachPath transforms all HTTP errors into the RFC 7807 Problem Details structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters provided.",
    "status": 422,
    "details": [
      {
        "field": "score",
        "issue": "Score must be a number between 0 and 100."
      }
    ],
    "request_id": "req_5a6cf3711f1d4d"
  }
}
```

### Exception Mapping Matrix
| Status | Error Code String | Triggering Condition |
| :--- | :--- | :--- |
| **400** | `MALFORMED_REQUEST` | Syntax errors, bad payload format. |
| **401** | `AUTHENTICATION_REQUIRED` | Missing or invalid authentication token. |
| **403** | `INSUFFICIENT_PERMISSIONS` | Forbidden access to non-owned resources. |
| **404** | `RESOURCE_NOT_FOUND` | Unmapped route or missing entity ID. |
| **409** | `STATE_CONFLICT` | Duplicate unique constraint, conflicting state. |
| **422** | `VALIDATION_ERROR` | Pydantic request schema validation failure. |
| **500** | `DATABASE_ERROR` | Database execution or transaction failure. |
| **500** | `INTERNAL_SERVER_ERROR` | Unhandled server exception (internal traces sanitized). |
| **503** | `SERVICE_UNAVAILABLE` | Database readiness check failure. |

---

## 8. Diagnostic Health Probes

1. **`GET /api/v1/health` (Liveness)**
   - Returns 200 OK immediately if the web process is running.
   ```json
   {
     "status": "healthy",
     "service": "CoachPath API",
     "version": "0.1.0",
     "environment": "development"
   }
   ```

2. **`GET /api/v1/ready` (Readiness)**
   - Executes `SELECT 1` through an active async database session.
   - If connected: Returns `200 OK` `{"status": "ready", "database": "connected"}`.
   - If unreachable: Returns `503 Service Unavailable` `{"status": "unhealthy", "database": "disconnected"}`.

---

## 9. Frontend Integration Interface

The Next.js frontend integrates via [`frontend/src/lib/api-client.ts`](file:///Users/anmolsharma/Desktop/Coach_Path/frontend/src/lib/api-client.ts):
- Respects `process.env.NEXT_PUBLIC_API_URL` (default: `http://localhost:8000/api/v1`).
- Auto-attaches `X-Request-ID` correlation tracing headers.
- Parses RFC 7807 error envelopes into typed `ApiClientError` instances.
- Provides helper methods `checkHealth()` and `checkReadiness()`.

---

## 10. Test Execution & Verification

The backend test suite executes with 100% pass rates across 33 automated tests:

```bash
cd backend
.venv/bin/pytest -v
# ============================== 33 passed in 1.57s ==============================
```
- **Liveness & Readiness**: Root metadata, healthy DB readiness, and 503 fallback when DB fails.
- **RFC 7807 Errors**: Validation error formatting, 404 formatting, custom domain exceptions.
- **Middleware**: Tracing headers, execution timing, and correlation ID preservation.
- **Structural Routers**: Validates all 14 placeholder domain routes mount correctly.
- **Repository / Service Layer**: Validates CRUD abstraction and `NotFoundException` handling.
- **Model Tests (`test_models.py`)**: Validates model creation, relationships, foreign keys, unique constraints, cascade deletion, and seed script idempotency across all 37 database entities.
