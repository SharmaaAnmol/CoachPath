# CoachPath — Full Project Report

_Reviewed 2026-11-05 · local repo `~/Desktop/Coach_Path` · GitHub `SharmaaAnmol/CoachPath` (public) · live at https://coach-path-six.vercel.app_

---

## 1. What CoachPath is

An AI-assisted **career intelligence platform** for students, recent grads and early-career engineers (built for **Bharat Hackathon 2.0**, per the GitHub description). It keeps one central career profile and runs a loop on top of it:

```
Profile → AI onboarding chat → Resume upload & parse → Diagnostic assessments
  → Skill-gap analysis → Learning roadmap → Job discovery → Job matching (explained)
  → Resume tailoring (no fabrication) → Application package + recruiter outreach → (tracker / interviews / readiness — not built yet)
```

Its central design rules, enforced in code, not just in docs:

1. **Deterministic scoring.** Skill gap, job match and roadmap logic is plain math. No LLM is used in any score.
2. **Evidence provenance.** Self-reported or resume-claimed skills can never reach level 3/4. Only an assessment score ≥ 70% (or verified evidence) can.
3. **Human approval gates.** Resume parses, tailored resumes, application packages and outreach drafts all stay `draft` until the user approves them. Nothing is auto-sent or auto-submitted.
4. **No fabrication.** AI output is checked against the candidate's real evidence, and unsupported claims are removed or flagged.

---

## 2. Size & history

| Item | Value |
|---|---|
| Commits | 43 on `main`, from 2026-10-06 to 2026-10-29 |
| Source | ~75k lines of Python + TS/TSX (≈1.8 MB Python, ≈1.1 MB TS) |
| Docs | 70 markdown specs/audits in `docs/` (PRD, architecture, ADRs, a report for each phase) |
| Backend tests | **318 collected** (pytest, async, SQLite/aiosqlite) |
| Method | Phased: each feature gets A (backend) → B (frontend) → C (E2E audit), each with a report |

The first ~8 commits are all design docs (PRD, UX flows, 37-entity schema, API spec, AI architecture, security spec, roadmap). Implementation starts at Phase 1.

---

## 3. Architecture & deployment

```
Browser ──► Vercel (Next.js 14)  coach-path-six.vercel.app
              │  rewrite /api/v1/*  ──►  Render (FastAPI, Docker)  coachpath-api-staging.onrender.com
              │                              │
              │                              ├─► Neon Postgres (asyncpg, pgbouncer pooler, SSL)
              │                              ├─► Google Gemini (gemini-3.5-flash-lite)
              │                              └─► Local disk storage (R2/S3 adapter exists, not enabled)
```

- **The Vercel proxy is the key trick.** `next.config.mjs` rewrites `/api/v1/:path*` to `BACKEND_INTERNAL_URL`, so auth cookies are first-party (no third-party cookie blocking), and the edge `middleware.ts` can see them.
- **Render** (`render.yaml`): free-tier web service. Migrations run in `start.sh` with retries, because free tier has no pre-deploy hook. GitHub records a Render deployment per push; the latest is `566fb20` (2026-10-29).
- **Startup seeding** runs in a background task so the port binds fast: 48 canonical skills plus aliases, 11 roles with requirements, and 270 assessment questions.
- **Docker Compose** exists for local Postgres+pgvector and the API.

### Live check (done today)

| Probe | Result |
|---|---|
| `GET /` (Vercel) | 200, landing page renders |
| `GET /api/v1/health` via Vercel | 200 `{"status":"healthy","environment":"staging"}` |
| `GET /api/v1/ready` | 200 `database: connected` |
| `GET /api/v1/auth/me` (no cookie) | 401 RFC-7807 error, ~0.4 s |
| `GET /api/v1/roles` | Works on Render directly. One batch of requests through the proxy **timed out at 60 s** (likely Render free-tier cold start or slow Neon wake), then recovered. |

I didn't log in or create an account on the live site, so authenticated flows weren't exercised live.

---

## 4. Backend (FastAPI · Python 3.13 · SQLAlchemy 2 async · Alembic)

```
backend/app/
  main.py          app factory, CORS, correlation-ID middleware, RFC 7807 handlers, lifespan seeding
  core/            config (pydantic-settings), security (Argon2id, JWT), exceptions, in-memory rate limiter
  ai/              LLMProvider interface + adapters: gemini, groq, openai, anthropic, mock; prompts/ (versioned)
  api/routes/      17 routers (below)
  models/          ~40 tables
  schemas/         Pydantic v2 contracts
  services/        all business logic ("engines")
  db/seeds/        skill taxonomy, role catalog, 9×30-question assessment bank, seed jobs
```

### 4.1 API surface (`/api/v1`)

| Router | Status | What it does |
|---|---|---|
| health | ✅ | `/health`, `/ready` (DB check) |
| auth | ✅ | register, login, refresh (rotation), logout, me. HttpOnly cookies, Argon2id, audit log, rate-limited login |
| profile | ✅ | CRUD for profile, career goals, education, experience, projects, certifications |
| onboarding | ✅ | AI interview: start/resume, answer, progress, history, summary, confirm → merge into profile |
| resume | ✅ | upload PDF/DOCX → extract → Gemini parse → **draft** → review → confirm/merge; retry, delete, file download; tailoring endpoints (tailor, list, get, edit, approve, diff, analysis) |
| assessments | ✅ | list categories, detail, start/resume attempt, submit answer, complete, result, history |
| roles / skills | ✅ | role catalog & requirements; gap analysis calculate/latest/history/evidence |
| roadmap | ✅ | generate, active, by id, history, progress, PATCH task status (with proof URL), adapt |
| jobs | ✅ | search/filter, detail, manual import, ingestion run, market intelligence, status/freshness |
| job_matching | ✅ | per-job match, recommendations, recalculate, explanation drawer |
| applications | 🟡 **uncommitted (11A)** | application packages: prepare (AI), get/list, edit, approve, handoff, confirm submitted |
| recruiters | 🟡 **uncommitted (11A)** | outreach drafts: create (AI), edit, approve, handoff, confirm sent, cancel, delete |
| interviews | ⛔ placeholder | returns `{"status":"placeholder","phase":"Phase 14"}` |
| career-readiness | ⛔ placeholder | Phase 15 |
| dashboard | ⛔ placeholder | Phase 15 (the frontend dashboard builds its own view from other clients) |
| settings | ⛔ placeholder | Phase 16 (GDPR export/delete not built) |

Swagger/OpenAPI is only exposed when `DEBUG=true`, and DEBUG is forced off when deployed.

### 4.2 Data model (main tables)

- **Identity:** `users`, `user_profiles`, `user_sessions` (hashed refresh tokens), `activity_logs`, `audit_logs`
- **Career graph:** `career_profiles`, `education`, `experience`, `projects`, `certifications`, `roles`
- **Skills:** `skills` (canonical), `role_requirements` (weight, required level, importance), `user_skills`, `skill_gaps`, `skill_gap_analyses` (snapshots)
- **Onboarding:** `onboarding_sessions`, `onboarding_turns`
- **Resume:** `resumes` (original is immutable, draft JSON attached), `resume_versions` (tailored variants)
- **Assessments:** `assessments`, `assessment_questions`, `assessment_attempts`, `assessment_answers`, `assessment_results`
- **Roadmap:** `roadmaps`, `roadmap_phases`, `roadmap_tasks`
- **Jobs:** `job_sources`, `job_ingestion_runs`, `jobs` (dedupe hash, quality score, freshness, `embedding` column), `job_skills`, `job_matches`
- **Pipeline:** `applications`, `application_status_history`, `recruiters`, `recruiter_contacts`, `recruiter_messages`, `interviews`, `interview_questions`, `interview_preparations`, `career_readiness_scores`
- **New in 11A (uncommitted migration `d5e6f7a2b3c4`):** `application_packages`, `recruiter_outreach_drafts`

### 4.3 The engines: how each one works

**Skill Gap Engine** (`services/skill_gap_engine.py`), no LLM
- Gathers evidence per canonical skill from assessments, user skills, projects and resume.
- Calibrates a level from 0 to 4:
  - assessment ≥ 85% → 4, ≥ 70% → 3, ≥ 50% → 2, otherwise 1
  - unverified evidence caps at 2 (with projects) or 1
- Per requirement: `coverage = min(current/required, 1)`. Status is one of STRENGTH, DEVELOPING, GAP, NOT_ASSESSED or NOT_IN_PROFILE.
- **Role Alignment** = weighted mean of coverage. **Evidence Coverage** = weighted share of skills with verified evidence (half credit for unverified).
- Outputs ranked gaps, recommended assessments, a templated narrative and a snapshot history.

**Assessments** (`services/assessments.py`)
- 9 categories × 30 questions = 270: Python, JS/TS, Java, C/C++, SQL, DSA, Web, ML, AI/LLM.
- Each session is 20 randomized questions with diversity-ranked selection, and an attempt can be resumed.
- Grading happens server-side. Answers are never sent to the client before submission.
- Results are written back into `user_skills` as verified evidence through `assessment_skill_mapper`.

**Roadmap Engine** (`services/roadmap_engine.py` + `roadmap_catalog.py`)
- Builds a 4-phase plan from the latest gap snapshot.
- Prerequisites are validated as a DAG (topological order), and locked tasks can't be started.
- Checks schedule feasibility against weekly hours, and task completion accepts a deliverable proof URL.
- `adapt` rebuilds the plan after new evidence.
- The LLM only rewrites task descriptions, and there's a deterministic fallback.

**Job Ingestion** (`job_ingestion_pipeline.py`, `job_source_adapters.py`, `job_normalization.py`)
- Adapters: Seed, Manual, Arbeitnow, Mock. Production currently uses `JOB_API_PROVIDER=seed`.
- Pipeline: HTML clean → classify role, seniority and remote type → deterministic skill extraction → data-quality score → dedupe hash → idempotent upsert → run log.
- Includes freshness lifecycle (30 days active, 60 days stale) and SSRF protection on manual URL import.

**Job Matching Engine** (`job_matching_engine.py`), no LLM
- Score = **50% skills** (required vs preferred, weighted by evidence provenance) + **15% experience** + **15% projects** + **10% location** + **10% preferences**.
- Matches with evidence coverage < 40% are flagged **provisional**.
- Results are cached in `job_matches`, invalidated when the profile changes, and explained in a 4-tab drawer.

**AI Onboarding** (`services/onboarding.py`)
- The LLM proposes the next question and pulls out stated facts. The app owns state transitions and DB writes.
- Max 20 turns. Summary falls back to a deterministic builder if AI fails.
- The user confirms the summary before it merges into the career profile.

**Resume parsing** (`services/resume.py`, `document_extractor.py`)
- pypdf / python-docx text extraction with a timeout → Gemini structured parse → skill normalization → **draft only**.
- Never mutates the profile until `confirm_and_merge_profile`. The UI shows conflicts between resume and profile.

**Resume Tailoring** (`services/resume_tailoring.py`)
- Gemini tailors to a job using a serialized evidence profile.
- `_reconcile_and_verify_truthfulness` removes or flags any skill or claim that isn't in the evidence.
- Versioned drafts → approve. Also provides a diff API and keyword coverage/gap analysis. The original resume is immutable.

**Application Prep & Recruiter Outreach** (11A, uncommitted)
- Builds a package (cover note + answers to common application questions) grounded in evidence. Flow: approve → "handoff" (user applies on the employer's site) → user confirms it was submitted.
- Outreach drafts are capped at **90 words**, with at most **3 active drafts per job**. Nothing is ever sent automatically, and a draft is marked "sent" only when the user confirms.

### 4.4 AI layer
- One `LLMProvider` interface (`ai/base.py`), picked by `AI_PROVIDER`: gemini (default), groq, openai, anthropic, disabled. The factory never silently swaps in the mock adapter; a missing key → 503.
- Prompts are versioned modules in `ai/prompts/` with Pydantic output schemas (e.g. `application_prep_v1`, `recruiter_outreach_v1`).

### 4.5 Security posture
- Argon2id (tuned for container CPU), short-lived JWT access tokens in cookies (60 min), refresh rotation with hashed tokens in DB (7 days), session revocation.
- Cookies are HttpOnly, Secure when deployed, SameSite=lax. Deployed builds refuse to start with the default `SECRET_KEY`.
- Ownership checks are enforced in every service (`_enforce_ownership`). Errors use RFC 7807 bodies with request IDs.
- The rate limiter is **in-memory** (`core/rate_limit.py`): it only protects auth, resets on restart, and isn't shared across instances.

---

## 5. Frontend (Next.js 14 App Router · React 18 · TS · Tailwind · TanStack Query · Framer Motion)

```
src/app/(public)/   landing, about, features, how-it-works, privacy, login, signup
src/app/(app)/      protected app shell (sidebar + topbar)
src/components/     ui/ design system + feature folders (onboarding, resume, assessments, skills, roadmap, jobs, landing, layout)
src/lib/            typed API clients per domain (api-client.ts handles RFC 7807 → ApiClientError)
src/providers/      AuthProvider (session), QueryProvider
src/middleware.ts   edge gate: no access/refresh cookie → redirect to /login?redirect=…
src/types/index.ts  1.5k lines of domain types mirroring backend schemas
```

| Page | Data |
|---|---|
| /dashboard | **Real**: built from profile, onboarding, roadmap, matching, assessment and skill-gap clients |
| /onboarding | Real (AI chat, progress, summary review, completion) |
| /career-profile | Real (1.9k-line editor for all profile sections) |
| /resume | Real (upload, processing status, parsed review with conflict indicators, approval, history, tailoring wizard, workspace, diff viewer, versions) |
| /assessments | Real (runner + results review) |
| /skills | Real (role selector, gauges, comparison table, gap list, evidence modal, history) |
| /roadmap | Real (phase accordions, DAG locks, deliverable modal, schedule banner, regenerate) |
| /jobs, /jobs/[id] | Real (filters, market intel card, manual import, recommendations tab, match drawer) |
| /settings | Partly real (profile client) |
| /applications, /recruiters, /interviews, /career-readiness | **Mock data** (`lib/mock/data.ts`) with a "demo preview" banner |

The landing page shows an **illustrative** demo candidate ("Aarav Mehta", 78% readiness, 4 pillars). It's labelled as illustrative, but the readiness index, kanban and recruiter features it advertises are marked "Preview" because the backend isn't built yet.

---

## 6. Where the project stands

**Done and committed:** Phases 0 → 10C (foundations, auth, profile, onboarding, resume parsing, assessments, skill gap, roadmap, job market, job matching, resume tailoring frontend and audit), plus a remediation pass and a premium UI redesign.

**In progress (uncommitted on `main`):** Phase 11A, the application-preparation and recruiter-outreach backend. That's 7 modified files, 9 new files (+857 lines in modified files), a new Alembic migration, and a 1.5k-line test file.

**Not started:**
- application pipeline tracker (kanban, backed by the existing `applications` tables)
- interview prep (Phase 14)
- composite readiness and real dashboard API (Phase 15)
- settings, privacy and data deletion (Phase 16)
- observability and hardening (Phase 16/17)

---

## 7. Issues & risks I found

1. **README is out of date.**
   - It says Phase 10B/10C are unchecked (they're committed), quotes 246 tests (318 now) and lists 7 roles (the catalog has 11).
   - Its phase numbering differs from `docs/development-roadmap.md`: README Phase 12 = Recruiter, roadmap Phase 13 = Recruiter.
2. **Some claimed tech isn't used.**
   - **Redis** is listed in the stack, but there's no Redis client in requirements or code.
   - **pgvector / "semantic vector similarity"** is claimed, but the `embedding` column is always `None` and matching is entirely deterministic.
   - Either implement them or drop them from the README/landing copy, especially for a hackathon judge.
3. **Uncommitted 11A work sits directly on `main`.** One `git checkout .` would lose it. Commit it on a branch.
4. **The Render free tier sleeps.** First requests after idle can take 30–60 s+, and one of my proxied API requests timed out. That matters for a demo: warm it up beforehand or use a paid instance.
5. **Uploaded resumes go on local disk on Render** (`STORAGE_PROVIDER=local`), which is wiped on every redeploy or restart. Uploaded resumes will disappear. The R2/S3 adapter already exists; turn it on.
6. **In-memory rate limiter** resets on restart and only covers auth endpoints. AI endpoints (onboarding, parse, tailor, prep, outreach) have no per-user limit, so they're a cost/abuse risk on your Gemini key.
7. **Four app pages are mock-only** and four API routers are placeholders. That's fine if the demo says so, but they shouldn't be presented as live.
8. `uploads/` (161 local files, presumably test resumes) is correctly git-ignored, so it isn't leaking to GitHub.

---

## 8. How to run locally (from README, verified paths)

```bash
cd backend && source .venv/bin/activate && alembic upgrade head && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
cd backend && pytest tests/ -q
cd frontend && npx tsc --noEmit && npm run build
```

Env template: `.env.example` (Gemini key, Neon `DATABASE_URL`, `BACKEND_INTERNAL_URL` for the Vercel proxy, cookie settings, storage, job provider).
