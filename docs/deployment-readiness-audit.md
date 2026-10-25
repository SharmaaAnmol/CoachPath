# CoachPath — Staging Deployment Readiness Audit

**Document Status**: Finalized & Audited  
**Audit Date**: October 25, 2026  
**Auditor**: CoachPath Architecture & Deployment Engineering  
**Deployment Target**: Staging Environment (`staging`)

---

## 1. Executive Summary

This readiness audit establishes the complete operational architecture, security posture, configuration matrix, and staging deployment blueprint for the CoachPath platform. CoachPath is an AI-powered career intelligence platform integrating FastAPI (Python 3.13), Next.js 14 App Router, PostgreSQL with pgvector, and Google Gemini AI.

All feature development has been paused at the completion of Phase 10A (backend foundation verified with 246 passing integration tests and zero frontend build warnings across all 25 Next.js static pages).

---

## 2. Verified System Architecture

```
                                  STAGING ENVIRONMENT TOPOLOGY
                                  ============================

 [ Candidate Web Browser ]
            │
            ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ Frontend Host: Vercel (Next.js 14 App Router)                          │
 │ - URL: https://coachpath-staging.vercel.app                            │
 │ - Build Command: `npm run build`                                       │
 │ - Edge Middleware: Authenticates session cookies (/dashboard, etc.)   │
 │ - Next.js Reverse Proxy: Rewrites `/api/v1/:path*` to Backend Target   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ (Same-Origin Cookie Forwarding)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ Backend Host: Render Web Service (FastAPI / Python 3.13)               │
 │ - URL: https://coachpath-api-staging.onrender.com                      │
 │ - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`   │
 │ - Pre-Deploy: `alembic upgrade head`                                   │
 │ - Health Check: `/api/v1/health` (Liveness) & `/api/v1/ready` (DB)    │
 │ - Auto-Seeding: 48 skills taxonomy, 7 roles, 270 diagnostic questions  │
 └───────────────────┬───────────────────────────────┬────────────────────┘
                     │                               │
                     ▼                               ▼
 ┌──────────────────────────────────────┐   ┌─────────────────────────────┐
 │ Managed Database: Neon PostgreSQL     │   │ Durable Storage:            │
 │ - Engine: PostgreSQL 16 + pgvector   │   │ Cloudflare R2 (S3-Compat)   │
 │ - Connectivity: SSL mode require     │   │ - Bucket: coachpath-resumes │
 │ - Schema: 10 Alembic revisions to    │   │ - Server-side AES256        │
 │   Phase 10A (b3c4d5e6f7a2)           │   │ - Private ACL only          │
 └──────────────────────────────────────┘   └─────────────────────────────┘
                     │
                     ▼
 ┌──────────────────────────────────────┐
 │ AI Provider: Google Gemini           │
 │ - Model: gemini-3.5-flash-lite       │
 │ - Transport: Backend secrets only    │
 └──────────────────────────────────────┘
```

---

## 3. Component Configuration & Entry Points

### 3.1 Frontend (`frontend/`)
- **Framework**: Next.js 14.2.15 (React 18.3.1, TypeScript 5.6.3, Tailwind CSS).
- **Package Manager**: npm.
- **Build Command**: `npm run build`.
- **Static Pages Generated**: 25/25 verified.
- **Middleware**: Edge authentication middleware (`src/middleware.ts`) enforcing session cookies on 15 protected route hierarchies.
- **API Integration**: Dual-mode reverse proxy via `next.config.mjs` (`BACKEND_INTERNAL_URL`) ensuring cookie same-origin delivery, eliminating third-party browser cookie blocking across distinct domains.

### 3.2 Backend (`backend/`)
- **Framework**: FastAPI 0.115.0 / Starlette with Uvicorn.
- **Runtime**: Python 3.13.6.
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.
- **Port Binding**: Dynamic port injection respecting Render/PaaS `$PORT`.
- **Database Driver**: SQLAlchemy 2.0.36 + `asyncpg` 0.30.0.
- **URL Normalizer**: Automatic scheme converter in `Settings` converting `postgres://` and `postgresql://` connection strings to `postgresql+asyncpg://`.
- **CORS Configuration**: Explicit origin whitelist with credential support (`allow_credentials=True`).
- **Cookie Security**: Configurable `COOKIE_SAMESITE` (`lax` for proxy topology, `none` for direct cross-origin) and `COOKIE_SECURE` (`True` in staging/production).

---

## 4. Staging Environment Variable Matrix

| Variable Name | Required By | Environment | Description / Placeholder | Sensitive? |
| :--- | :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_APP_URL` | Frontend | Vercel | Public URL of the frontend (e.g. `https://coachpath-staging.vercel.app`) | No |
| `NEXT_PUBLIC_API_URL` | Frontend | Vercel | Set to `/api/v1` for reverse-proxy routing | No |
| `BACKEND_INTERNAL_URL` | Frontend | Vercel | Target backend URL for Next.js proxy (e.g. `https://coachpath-api-staging.onrender.com`) | No |
| `ENVIRONMENT` | Backend | Render | Set to `staging` | No |
| `DEBUG` | Backend | Render | Set to `false` in staging | No |
| `LOG_LEVEL` | Backend | Render | `info` | No |
| `PORT` | Backend | Render | Auto-injected by Render (default 10000) | No |
| `SECRET_KEY` | Backend | Render | 32+ character random secret (e.g. `openssl rand -hex 32`) | **YES** |
| `CORS_ORIGINS` | Backend | Render | Comma-separated frontend origins: `https://coachpath-staging.vercel.app` | No |
| `COOKIE_SAMESITE` | Backend | Render | `lax` (with Next.js reverse proxy) or `none` (direct) | No |
| `COOKIE_SECURE` | Backend | Render | `true` | No |
| `DATABASE_URL` | Backend | Render | Neon PostgreSQL async connection string with `?sslmode=require` | **YES** |
| `AI_PROVIDER` | Backend | Render | `gemini` | No |
| `GEMINI_API_KEY` | Backend | Render | Google Gemini API Key | **YES** |
| `GEMINI_MODEL` | Backend | Render | `gemini-3.5-flash-lite` | No |
| `STORAGE_PROVIDER` | Backend | Render | `r2` (or `local` for ephemeral staging evaluation) | No |
| `S3_ENDPOINT_URL` | Backend | Render | Cloudflare R2 endpoint URL (`https://<account_id>.r2.cloudflarestorage.com`) | No |
| `S3_ACCESS_KEY_ID` | Backend | Render | Cloudflare R2 Access Key ID | **YES** |
| `S3_SECRET_ACCESS_KEY`| Backend | Render | Cloudflare R2 Secret Access Key | **YES** |
| `S3_BUCKET_NAME` | Backend | Render | `coachpath-resumes-staging` | No |

> [!CAUTION]
> Under no circumstances must `GEMINI_API_KEY`, `DATABASE_URL`, `SECRET_KEY`, or S3 secrets be prefixed with `NEXT_PUBLIC_` or placed in frontend bundles.

---

## 5. Security & Isolation Review

1. **Secret Leakage Audit**:
   - `git grep` and history scans verified zero committed API keys, tokens, or plaintext passwords.
   - Root, health (`/api/v1/health`), and readiness (`/api/v1/ready`) endpoints return operational flags only and redact all database connection strings and passwords.
2. **Multi-Tenant Isolation**:
   - Every protected route enforces user ownership through `get_current_user` and `ensure_resource_ownership`.
   - Resume uploads, assessments, skill-gap snapshots, roadmaps, and tailored versions cannot be viewed or mutated across user accounts.
3. **Session Cookies & Transport**:
   - Auth tokens are delivered in `HttpOnly` cookies.
   - When deployed behind HTTPS, `Secure=True` is strictly enforced.
4. **Prompt Injection & AI Sanitization**:
   - User inputs and candidate documents are quarantined within triple-angle delimiter blocks (`<<<CANDIDATE_RESUME_TEXT>>>`).
   - The AI layer is strictly read-only and deterministic server-side reconcilers verify truthfulness before database commit.
5. **Private Resume Document Storage**:
   - Object storage driver enforces server-controlled paths (`{user_id}/{uuid}.{ext}`).
   - Bucket permissions remain strictly private. Resumes are only downloadable through authenticated endpoints (`/api/v1/resume/{id}/file`).

---

## 6. Durable Storage vs. Ephemeral Disk Strategy

| Storage Driver | Environment | Persistence | Cost | Evaluation |
| :--- | :--- | :--- | :--- | :--- |
| `LocalFileStorageService` | Local Dev (`uploads/`) | Survives local restarts; destroyed on container restart/redeploy on Render Free | Free | **Unsuitable for persistent staging resumes** |
| `S3FileStorageService` (Cloudflare R2) | Staging (`coachpath-resumes-staging`) | Durable; persists across all redeployments and container restarts | Free (10 GB/mo, $0 egress) | **Recommended for Staging** |
| `S3FileStorageService` (AWS S3) | Production / Staging alternative | Durable; standard 99.999999999% durability | Pay-as-you-go | Secondary alternative |

---

## 7. Outstanding Blockers & Prerequisites

To execute the live staging deployment, the following external accounts/resources must be provisioned:

1. **GitHub Repository**: Accessible at `https://github.com/SharmaaAnmol/CoachPath.git` on branch `main`. (Ready)
2. **Neon PostgreSQL Database**: Staging database `coachpath_staging` with connection string. (Requires user to provision free Neon account)
3. **Cloudflare R2 Bucket**: Private bucket `coachpath-resumes-staging` with R2 API token. (Requires user to provision free Cloudflare account)
4. **Google Gemini API Key**: Valid key with quota for `gemini-3.5-flash-lite`. (Requires user Gemini API key)
5. **Render Web Service**: Connected to GitHub repo using `render.yaml`. (Requires user Render account)
6. **Vercel Project**: Connected to GitHub repo pointing to `frontend/`. (Requires user Vercel account)
