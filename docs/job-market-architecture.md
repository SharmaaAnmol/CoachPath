# CoachPath — Job Market Intelligence and Job Ingestion Architecture

**Document Status**: Official Architecture Specification (Phase 8A)  
**Author**: CoachPath Core Engineering  
**Version**: 1.0.0  
**Last Updated**: October 2026  

---

## 1. Executive Summary

Phase 8A introduces the **Job Market Intelligence and Permitted Job Ingestion Engine** into CoachPath. This subsystem acts as the real-world data foundation powering candidate job discovery, role-market alignment, skill-demand insights, and future multi-factor job matching (Phase 8B).

CoachPath strictly enforces permitted, ethical data collection protocols. It does not perform unauthorized web scraping, bypass anti-bot defenses, or synthesize fabricated job postings. The system supports multi-source ingestion across curated benchmark seed datasets, candidate manual submissions, permitted public developer APIs (e.g. Arbeitnow), and isolated test harness adapters.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          PERMITTED INGESTION PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────────────┘
 [Curated Seed Data]    [Candidate Manual Import]    [Permitted Developer APIs]
         │                          │                            │
         └──────────────────────────┼────────────────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Source Adapter     │
                         │(BaseJobSourceAdapter)│
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Validation Stage   │
                         │ (Completeness Check) │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Normalization Engine │
                         │ • Clean Markup/HTML  │
                         │ • 9 Benchmark Roles  │
                         │ • Remote & Seniority │
                         │ • Salary Standardization
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Deduplication Match  │
                         │  • External ID / Hash│
                         │  • Safe Upsert       │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Description Parser   │
                         │ • 48 Canonical Skills│
                         │ • Mandatory vs Pref  │
                         │ • Section Extraction │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  PostgreSQL Catalog  │
                         │ • jobs & job_skills  │
                         │ • job_ingestion_runs │
                         │ • job_sources        │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Market Intelligence  │
                         │ • Skill Demand Freq  │
                         │ • Remote Breakdown   │
                         │ • Salary Benchmarks  │
                         └──────────────────────┘
```

---

## 2. Core Architectural Pillars

### 2.1 Permitted Data Source Abstraction (`BaseJobSourceAdapter`)
All sources implement a uniform asynchronous interface:
- `fetch_jobs(batch_size: int, page: int, **kwargs) -> List[RawJobListing]`
- Implementations:
  1. `SeedJobAdapter`: Curated benchmark tech opportunities covering all 9 CoachPath benchmark roles (Stripe, Datadog, Twilio, Figma, Notion, Vercel, Netflix, Spotify, Scale AI, Anthropic, Cloudflare, etc.).
  2. `ManualImportAdapter`: Enables candidates to paste job listings directly via `POST /api/v1/jobs/import` for automated parsing, normalization, and immediate catalog inclusion.
  3. `ArbeitnowJobAdapter`: Permitted open public API (`https://www.arbeitnow.com/api/job-board-api`) with rate limiting and timeout safeguards.
  4. `MockJobSourceAdapter`: Deterministic in-memory adapter for test suite execution without network dependencies.

### 2.2 Canonical Role & Skill Normalization
- **9 Benchmark Roles**:
  - `backend-developer`
  - `frontend-developer`
  - `fullstack-developer`
  - `data-scientist`
  - `machine-learning-engineer`
  - `ai-engineer`
  - `devops-cloud-engineer`
  - `software-engineer`
  - `data-analyst`
- **48 Canonical Skills Taxonomy**:
  - Reuses the canonical skill definitions established in Phase 6A (`backend/app/db/seeds/skill_taxonomy.py`).
  - Word-boundary regex tokenization with alias matching (e.g. `c++` -> `c-cpp`, `k8s` -> `kubernetes`, `aws` -> `aws`, `fastapi` -> `fastapi`).
  - Contextual classification distinguishing mandatory requirements from preferred/nice-to-have qualifications.
- **Workplace Flexibility**: Standardized to `remote`, `hybrid`, or `onsite`.
- **Seniority Tiers**: Standardized to `internship`, `entry_level`, `junior`, or `mid`.
- **Deduplication Fingerprinting**: Deterministic SHA-256 fingerprint generated from normalized company, title, and location.

---

## 3. Database Schema Extensions

### 3.1 New Tables

#### `job_sources`
Tracks configured ingestion providers and operational health:
- `id`: UUID (Primary Key)
- `name`: String(64), Unique (`seed`, `manual`, `arbeitnow`, `mock`)
- `provider_type`: String(32) (`seed`, `manual`, `api`, `mock`)
- `base_url`: String(255), Nullable
- `is_active`: Boolean (Default: True)
- `rate_limit_per_minute`: Integer (Default: 30)
- `last_ingested_at`: DateTime with timezone, Nullable
- `config_metadata`: JSONB

#### `job_ingestion_runs`
Audit ledger of pipeline execution runs and ingestion statistics:
- `id`: UUID (Primary Key)
- `source_id`: UUID, FK `job_sources.id` (ON DELETE SET NULL)
- `source_name`: String(64)
- `status`: String(32) (`pending`, `running`, `completed`, `failed`, `partial`)
- `items_fetched`: Integer
- `items_inserted`: Integer
- `items_updated`: Integer
- `items_skipped`: Integer
- `items_errored`: Integer
- `error_log`: JSONB
- `started_at`: DateTime with timezone
- `finished_at`: DateTime with timezone

### 3.2 Enhanced Columns

#### `jobs`
- `source_url`: String(512), Nullable (Original job posting link)
- `normalized_title`: String(255), Nullable
- `normalized_location`: String(128), Nullable
- `employment_type`: String(32), Default `'full_time'`
- `freshness_status`: String(32), Default `'active'` (`active`, `needs_refresh`, `expired`, `closed`)
- `last_verified_at`: DateTime with timezone, Nullable
- `responsibilities`: JSONB (Array of extracted responsibility strings)
- `required_qualifications`: JSONB (Array of extracted mandatory requirements)
- `preferred_qualifications`: JSONB (Array of extracted nice-to-have qualifications)
- `raw_source_payload`: JSONB (Audit trail of original provider payload)
- `data_quality_score`: Numeric(4, 2) (Completeness score 0.00 to 1.00)
- `embedding`: VectorType(1536), Nullable (Semantic requirements vector)

#### `job_skills`
- `confidence_score`: Numeric(4, 2), Default `1.00`
- `source_phrase`: String(255), Nullable (Matched text snippet)

---

## 4. API Specification

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/jobs` | Search curated jobs with multi-facet filters (`role_id`, `remote_type`, `experience_level`, `keyword`, `min_salary`, pagination). | Yes |
| `GET` | `/api/v1/jobs/{job_id}` | Retrieve comprehensive job opportunity details, requirements, and tagged skills. | Yes |
| `POST` | `/api/v1/jobs/import` | Submit a target job description manually for real-time normalization, skill extraction, and persistence. | Yes |
| `POST` | `/api/v1/jobs/ingest` | Trigger an ingestion run for a specific permitted provider source (`seed`, `arbeitnow`, `mock`). | Yes |
| `GET` | `/api/v1/jobs/market-intelligence` | Calculate real-time market aggregates (skill frequency, role distribution, remote percentage, salary stats). | Yes |
| `GET` | `/api/v1/jobs/ingestion-runs` | Retrieve recent pipeline execution audit runs and throughput metrics. | Yes |

---

## 5. Idempotency & Upsert Semantics

The ingestion engine guarantees strict idempotency:
1. If an incoming job matches an existing record by `(source, external_id)` or SHA-256 fingerprint `(normalized_company, normalized_title, normalized_location)`:
   - The job is **not duplicated**.
   - `last_verified_at` and `freshness_status` are refreshed to active.
   - Responsibilities, qualifications, and salaries are synced.
   - Associated `job_skills` are atomically updated.
   - `items_updated` is incremented.
2. If the incoming job does not match an existing record:
   - A new `Job` record is inserted with `is_active=True`.
   - Extracted canonical skills are attached via `JobSkill`.
   - `items_inserted` is incremented.
