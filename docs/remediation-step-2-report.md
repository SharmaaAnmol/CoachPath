# CoachPath — Remediation Step 2 Report: Target Role Personalization Reconciler

> **Document Status**: Complete & Verified  
> **Phase**: Pre-Phase 10 Remediation — Step 2  
> **Date**: October 29, 2026  
> **Target Deployed URLs**:
> - Frontend: `https://coach-path-six.vercel.app`
> - API Backend: `https://coachpath-api-staging.onrender.com`
> - Staging Database: Neon Cloud PostgreSQL

---

## 1. Executive Summary

This remediation executes **Step 2** of the existing-feature audit remediation plan. Prior to this remediation:
1. The CoachPath role catalog contained 9 benchmark roles, omitting major industry tracks: **Data Engineer** and **Mobile Engineer**.
2. When users entered alternative titles (e.g., `"Data Engineer"`, `"iOS Developer"`, `"Mobile Engineer"`, `"ETL Engineer"`), or when unrecognized roles were passed across onboarding, career profile configuration, learning roadmaps, and skill gap analyses, the platform frequently suffered from silent fallback to `backend-developer` or triggered unhandled errors.
3. Frontend interfaces contained hardcoded fallbacks and filter lists that lacked support for modern data and mobile engineering careers.

In accordance with strict personalization and deterministic architecture principles:
- Extended the canonical benchmark role catalog to **11 roles**, adding full benchmark specifications and weighted requirements for `data-engineer` (11 skills) and `mobile-engineer` (10 skills).
- Added **9 new canonical skills** to the skills taxonomy with diagnostic assessment domain mappings.
- Created a centralized, deterministic role normalization and alias resolution service (`role_resolution.py`).
- Completely eliminated silent fallbacks to `backend-developer` across onboarding, career goals, roadmap engines, skill-gap analysis, and frontend components.
- Implemented explicit HTTP validation errors listing all supported roles when an unrecognized or unsupported role is supplied.
- Added seed job intelligence postings for both new roles.
- Created a dedicated automated test suite (`test_role_personalization_reconciler.py`) with 14 comprehensive tests, and verified that all 260 backend unit/integration tests and frontend production builds pass.

---

## 2. Verified Audit Findings Addressed

| Issue ID | Area | Severity | Pre-Remediation Behavior | Post-Remediation Status |
| :--- | :--- | :--- | :--- | :--- |
| **ROLE-01** | Canonical Role Catalog (`role_catalog.py`) | **P1** (Coverage) | Missing benchmarks for Data Engineer and Mobile Engineer. Only 9 roles defined. | **PASS** — Added complete benchmark definitions and requirements for `data-engineer` and `mobile-engineer`. |
| **ROLE-02** | Skill Taxonomy (`skill_taxonomy.py`) | **P1** (Coverage) | Missing key skills: ETL pipelines, data warehousing, orchestration, stream processing, mobile architecture, Kotlin, Swift, React Native, Flutter. | **PASS** — Added 9 new canonical skills and mapped to assessment diagnostic domains. |
| **ROLE-03** | Silent Fallback in Onboarding (`onboarding.py`) | **P0** (Personalization) | User input role fell back to `'backend-developer'` if not directly matching raw slugs. | **PASS** — Canonical alias resolver resolves titles; raises validation error if unsupported without silent substitution. |
| **ROLE-04** | Profile Career Goals (`profile.py`) | **P0** (Personalization) | Updating primary or secondary role allowed arbitrary unvalidated strings or retained stale relationship objects. | **PASS** — Strict validation against canonical roles and aliases; updates relationship cache in memory immediately. |
| **ROLE-05** | Roadmap Engine (`roadmap_engine.py`) | **P1** (Correctness) | Failed or gave generic roadmaps when passed new or alias roles. | **PASS** — Integrated `validate_and_resolve_role_id`; generates tailored milestones for `data-engineer` and `mobile-engineer`. |
| **ROLE-06** | Skill Gap Engine (`skill_gap_engine.py`) | **P0** (Personalization) | Evaluated unrecognized roles inconsistently; lacked structured error messages listing supported roles. | **PASS** — Normalized role resolution; explicit 404/422 error detailing supported roles; no silent fallback to backend-developer. |
| **ROLE-07** | Job Ingestion & Market Data (`job_normalization.py`, `job_seed_data.py`) | **P1** (Intelligence) | Job matcher had no keywords or seed postings for Data Platform or Mobile Engineering. | **PASS** — Added keywords to `CANONICAL_ROLE_KEYWORDS` and seeded Databricks & DoorDash job postings. |
| **ROLE-08** | Frontend Selectors & Types (`types/index.ts`, UI components) | **P1** (Consistency) | `TargetRole` type excluded new roles; job filters, manual import modals, and profile pages had hardcoded `'Backend Developer'` strings. | **PASS** — Updated TypeScript types, onboarding suggestions, job filter panels, manual import modal, and dynamic profile displays. |

---

## 3. Canonical Role Catalog Extension

### 3.1 Data Engineer (`data-engineer`)
- **Title**: Data Engineer
- **Category**: `data`
- **Description**: Robust data pipelines, scalable storage, ETL processing, data modeling, and distributed analytics architectures.
- **Benchmark Requirements (11 skills)**:
  1. `python` (mandatory, level 3, weight 1.2): Core pipeline development and scripting.
  2. `sql-databases` (mandatory, level 4, weight 1.3): Complex analytical queries, indexing, and data warehousing.
  3. `etl-pipelines` (mandatory, level 4, weight 1.3): Reliable batch and micro-batch data transformation workflows.
  4. `data-warehousing` (mandatory, level 3, weight 1.2): Columnar storage, dimension modeling, and data marts.
  5. `data-orchestration` (mandatory, level 3, weight 1.1): Workflow orchestration via DAGs, retries, and dependency tracking.
  6. `stream-processing` (preferred, level 2, weight 1.0): Real-time event streams and pub/sub message brokers.
  7. `distributed-systems` (preferred, level 3, weight 1.1): Distributed compute and partition tolerance concepts.
  8. `docker-containers` (preferred, level 2, weight 0.8): Containerized processing tasks and reproducibility.
  9. `git-version-control` (mandatory, level 2, weight 0.8): Collaborative schema migrations and pipeline versioning.
  10. `rest-apis` (preferred, level 2, weight 0.8): Consuming external APIs and surfacing data endpoints.
  11. `system-design` (preferred, level 3, weight 1.0): Scalable, fault-tolerant analytics infrastructure architecture.

### 3.2 Mobile Engineer (`mobile-engineer`)
- **Title**: Mobile Engineer
- **Category**: `mobile`
- **Description**: Native and cross-platform mobile apps, mobile architectures, offline synchronization, and responsive mobile interfaces.
- **Benchmark Requirements (10 skills)**:
  1. `mobile-architecture` (mandatory, level 4, weight 1.3): Clean mobile architecture patterns (MVVM/MVI/VIPER), lifecycle, and offline storage.
  2. `kotlin` (preferred, level 3, weight 1.1): Modern native Android client engineering with Coroutines and Compose.
  3. `swift` (preferred, level 3, weight 1.1): Native iOS application development with Swift, SwiftUI, and Combine.
  4. `react-native` (preferred, level 3, weight 1.0): Cross-platform JavaScript/TypeScript mobile application development.
  5. `flutter` (bonus, level 2, weight 0.8): Cross-platform multi-target UI engineering using Dart.
  6. `rest-apis` (mandatory, level 3, weight 1.1): Resilient mobile client networking, token refreshes, and serialization.
  7. `git-version-control` (mandatory, level 2, weight 0.8): Branching strategies and mobile release management.
  8. `ci-cd-pipelines` (preferred, level 2, weight 0.9): Automated mobile test execution, Fastlane, and app store delivery.
  9. `clean-architecture` (preferred, level 3, weight 1.0): Separation of concerns, domain repositories, and testability.
  10. `testing-automation` (mandatory, level 3, weight 1.1): Mobile unit testing, mocking, and UI instrumentation suites.

### 3.3 New Canonical Skills Added (9 Total)
| Skill ID | Skill Name | Category | Diagnostic Assessment Domain Mapping |
| :--- | :--- | :--- | :--- |
| `etl-pipelines` | ETL & Data Pipelines | `data` | `sql-databases` |
| `data-warehousing` | Data Warehousing & Modeling | `data` | `sql-databases` |
| `data-orchestration` | Workflow & Data Orchestration | `tools` | `python` |
| `stream-processing` | Stream Processing & Event Streaming | `architecture` | `python` |
| `mobile-architecture` | Mobile Architecture & State Management | `architecture` | `web-development` |
| `kotlin` | Kotlin & Android SDK | `languages` | `java` |
| `swift` | Swift & iOS SDK | `languages` | `c-cpp` |
| `react-native` | React Native | `frameworks` | `javascript-typescript` |
| `flutter` | Flutter & Dart | `frameworks` | `web-development` |

---

## 4. Canonical Role Resolution & Alias Engine

A centralized, pure service was created in `backend/app/services/role_resolution.py`:

### Supported Canonical IDs (11 total)
`ai-engineer`, `backend-developer`, `data-analyst`, `data-engineer`, `data-scientist`, `devops-cloud-engineer`, `frontend-developer`, `fullstack-developer`, `machine-learning-engineer`, `mobile-engineer`, `software-engineer`.

### Key Functions
- `normalize_role_identifier(raw: Optional[str]) -> Optional[str]`:
  - Trims whitespace, lowercases, and strips surrounding punctuation.
  - Checks if the input is already a canonical role ID.
  - Matches against the alias dictionary covering:
    - `"Data Engineer"`, `"data-engineer"`, `"Big Data Engineer"`, `"ETL Developer"`, `"Data Platform Engineer"`, `"Analytics Engineer"` -> `data-engineer`
    - `"Mobile Engineer"`, `"mobile-engineer"`, `"iOS Developer"`, `"Android Developer"`, `"React Native Developer"`, `"Flutter Developer"` -> `mobile-engineer`
    - All existing aliases for Software Engineer, Backend, Frontend, Full Stack, ML, AI, Data Science, and DevOps.
- `validate_and_resolve_role_id(raw: Optional[str], field_name: str = "role_id") -> str`:
  - Rejects missing, empty, or whitespace-only role strings with `ValidationException(422)`.
  - Rejects unrecognized roles with `ValidationException(422)` providing an informative error message that enumerates all supported canonical roles.
- `get_supported_role_ids() -> List[str]`:
  - Returns a sorted list of all active canonical role identifiers for API error messages and UI dropdowns.

---

## 5. Elimination of Silent Fallbacks Across Modules

### 5.1 Onboarding (`backend/app/services/onboarding.py`)
- Removed hardcoded fallback: Previously, if a user provided a custom title, it defaulted to `"backend-developer"`.
- Now, user answers to career questions pass through `normalize_role_identifier`. If the role resolves to a supported benchmark, it is saved accurately. If unrecognized, it raises an explicit validation error rather than defaulting to Backend Developer.

### 5.2 Career Profile Goals (`backend/app/services/profile.py`)
- In `update_career_goals`:
  - Validates `primary_role_id` and `secondary_role_id` against `validate_and_resolve_role_id`.
  - Rejects unrecognized inputs with HTTP 422 listing valid roles.
  - Directly refreshes cached SQLAlchemy relationship instances (`career_profile.primary_role = primary_role`) before committing, preventing in-memory stale role retention.

### 5.3 Roadmap Generation (`backend/app/services/roadmap_engine.py`)
- `generate_roadmap` and `get_active_roadmap` use `validate_and_resolve_role_id` on the requested or configured role ID.
- Rejects unsupported roles with HTTP 422 instead of generating generic or mismatched milestone objectives.

### 5.4 Skill Gap Analysis (`backend/app/services/skill_gap_engine.py`)
- `calculate_gap_analysis` resolves and validates `role_id` against the database role records.
- If a requested role does not exist in the database, returns an informative `NotFoundException(404)` with the full list of supported roles.
- If a requested role exists but has an incomplete benchmark profile, returns `ValidationException(422)`.
- If a user has not configured a role and requests gap analysis without a `role_id`, baseline profile initialization is safely isolated without cross-user contamination.

### 5.5 Frontend User Experience
- `frontend/src/types/index.ts`: Expanded `TargetRole` union type to include all 11 canonical roles.
- `frontend/src/components/onboarding/question-input.tsx`: Added `Data Engineer` and `Mobile Engineer` to role suggestion pills.
- `frontend/src/components/jobs/job-filter-panel.tsx`: Added filters for `Data Engineer` and `Mobile Engineer`.
- `frontend/src/components/jobs/market-intelligence-card.tsx`: Added intelligence tabs for both roles.
- `frontend/src/components/jobs/manual-job-import-modal.tsx`: Added options to select Data Engineer or Mobile Engineer.
- `frontend/src/app/(app)/skills/page.tsx`: Dynamically loads available roles from the catalog API instead of defaulting state to `'backend-developer'`.
- `frontend/src/app/(app)/career-profile/page.tsx`: Displays actual target role title or "No target role selected" instead of hardcoded `'Backend Developer'`.

---

## 6. Verification and Test Results Matrix

| Test ID | Area / Function | Expected Outcome | Execution Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TEST-01** | Canonical Roles Seeder | 11 roles with 100 requirements seeded into DB | Seeded 57 skills, 11 roles, 100 requirements | **PASS** |
| **TEST-02** | Role Normalizer (DE Aliases) | `"Data Engineer"`, `"data-engineer"`, `"ETL Developer"` -> `data-engineer` | Evaluated across 6 variants | **PASS** |
| **TEST-03** | Role Normalizer (Mobile Aliases) | `"Mobile Engineer"`, `"iOS Developer"`, `"Android Developer"` -> `mobile-engineer` | Evaluated across 7 variants | **PASS** |
| **TEST-04** | Role Normalizer (Unsupported) | `"quantum-computing"`, `"blockchain-dev"` -> returns `None` / raises 422 | Tested rejection | **PASS** |
| **TEST-05** | Profile Career Goals (DE) | Primary role saved as `data-engineer` | Stored & verified via API | **PASS** |
| **TEST-06** | Profile Career Goals (Mobile) | Primary role saved as `mobile-engineer` | Stored & verified via API | **PASS** |
| **TEST-07** | Profile Rejection on Invalid Role | `PUT /profile/career-goals` with unsupported role returns 422 with supported list | HTTP 422 returned with 11 roles | **PASS** |
| **TEST-08** | Data Engineer Skill Gap Analysis | Gap analysis computes using 11 DE benchmark requirements | Verified alignment score and skill details | **PASS** |
| **TEST-09** | Mobile Engineer Skill Gap Analysis | Gap analysis computes using 10 Mobile benchmark requirements | Verified alignment score and skill details | **PASS** |
| **TEST-10** | Unrecognized Role Gap Analysis | `POST /skills/gap-analysis` with unknown role returns explicit error listing supported roles | HTTP 404 returned with 11 roles | **PASS** |
| **TEST-11** | Dynamic Role Switching | Switching from `backend-developer` to `data-engineer` generates new snapshot | Verified separate IDs and roles | **PASS** |
| **TEST-12** | Data Engineer Roadmap Generation | `POST /roadmap/generate` with `data-engineer` produces tailored milestones | 201 Created with DE phases | **PASS** |
| **TEST-13** | Roadmap Unrecognized Role Rejection | `POST /roadmap/generate` with invalid role returns 422 with supported roles list | 422 Unprocessable Content | **PASS** |
| **TEST-14** | Multi-Tenant Authorization Isolation | Analyses and snapshots are strictly segregated between users | Verified isolation across candidates | **PASS** |
| **REG-01** | Phase 6b Frontend Integration | Full gap analysis API contract suite | 3/3 tests passed | **PASS** |
| **REG-02** | Phase 6c End-to-End Audit | Cross-user isolation and determinism | 9/9 tests passed | **PASS** |
| **REG-03** | Full Backend Test Suite | All modules (Phases 1-9c + Remediation 1-2) | 260 passed, 1 skipped, 0 failed | **PASS** |
| **REG-04** | Frontend Lint Check | `npm --prefix frontend run lint` | 0 warnings, 0 errors | **PASS** |
| **REG-05** | Frontend Static Generation | `npm --prefix frontend run build` | 25/25 static pages compiled | **PASS** |

---

## 7. Files Changed

### Backend Files
1. **`backend/app/services/role_resolution.py`** *(New)*: Canonical registry, role alias normalization, and validation engine.
2. **`backend/app/db/seeds/skill_taxonomy.py`** *(Modified)*: Added 9 canonical skills for data and mobile engineering.
3. **`backend/app/db/seeds/role_catalog.py`** *(Modified)*: Added `data-engineer` and `mobile-engineer` benchmark specifications and requirements.
4. **`backend/app/services/assessment_skill_mapper.py`** *(Modified)*: Mapped 9 new skills to diagnostic assessment domains.
5. **`backend/app/services/job_normalization.py`** *(Modified)*: Added keywords for data and mobile engineer job matching.
6. **`backend/app/db/seeds/job_seed_data.py`** *(Modified)*: Added Databricks Data Platform Engineer and DoorDash Mobile Engineer job records.
7. **`backend/app/services/roadmap_engine.py`** *(Modified)*: Added target role validation using `validate_and_resolve_role_id`.
8. **`backend/app/services/profile.py`** *(Modified)*: Added canonical role validation in career goals update and refreshed relationship caches.
9. **`backend/app/services/onboarding.py`** *(Modified)*: Replaced fallback with canonical alias normalization.
10. **`backend/app/services/skill_gap_engine.py`** *(Modified)*: Added alias resolution, database role checks, and detailed error messages.
11. **`backend/tests/test_role_personalization_reconciler.py`** *(New)*: 14 automated unit/integration tests verifying all Step 2 requirements.

### Frontend Files
1. **`frontend/src/types/index.ts`** *(Modified)*: Updated `TargetRole` type definition to include all 11 canonical roles.
2. **`frontend/src/components/onboarding/question-input.tsx`** *(Modified)*: Added suggestions for Data Engineer and Mobile Engineer.
3. **`frontend/src/components/jobs/job-filter-panel.tsx`** *(Modified)*: Added Data Engineer and Mobile Engineer filter checkboxes.
4. **`frontend/src/components/jobs/market-intelligence-card.tsx`** *(Modified)*: Added market intelligence metrics for Data Engineer and Mobile Engineer.
5. **`frontend/src/components/jobs/manual-job-import-modal.tsx`** *(Modified)*: Added new roles to manual import selection dropdown.
6. **`frontend/src/app/(app)/skills/page.tsx`** *(Modified)*: Replaced hardcoded default role state with dynamic role selection.
7. **`frontend/src/app/(app)/career-profile/page.tsx`** *(Modified)*: Removed hardcoded `'Backend Developer'` fallback text.

---

## 8. Staging & Production Deployment Readiness

- **Database**: PostgreSQL schema remains unchanged because `roles` table stores role records dynamically and `career_profiles.primary_role_id` is `VARCHAR(64)` referencing `roles.id`. Seeder dynamically inserts new roles and requirements on startup.
- **Backwards Compatibility**: All legacy endpoints (`/api/v1/skills/gaps`, legacy gap responses) remain fully operational and verified through `test_skill_gap.py`.
- **Next Remediation Steps**:
  - **Step 3**: Diagnostic assessment question pool expansion and deterministic randomization.
  - **Step 4**: Public marketing copy alignment and truth-in-advertising reconciliation.
