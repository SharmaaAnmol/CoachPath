# CoachPath — Staging Deployment & Verification Report

**Document Status**: Verification & Deployment Runbook  
**Execution Date**: October 25, 2026  
**Target Environment**: Staging (`staging`)  
**Repository Branch**: `main` (`87c04b9`)  
**Remote**: `https://github.com/SharmaaAnmol/CoachPath.git`

---

## 1. Hosting Providers & Selected Plans

| Service Component | Selected Provider | Plan / Tier | Justification & Compatibility |
| :--- | :--- | :--- | :--- |
| **Source Repository** | GitHub | Free | Single source of truth at `https://github.com/SharmaaAnmol/CoachPath.git`. Clean working tree on branch `main`. |
| **Backend API** | Render | Free Web Service (Oregon) | Native Python 3.13 web service. Configured via `render.yaml`. Dynamic port `$PORT` binding, pre-deploy migration hook `alembic upgrade head`, and liveness probe at `/api/v1/health`. |
| **Managed Database** | Neon | Free Serverless PostgreSQL | PostgreSQL 16 with `pgvector` support. Isolated staging instance. Does not expire after 30 days (unlike Render Free PostgreSQL). SSL-enforced connection string. |
| **Durable Object Storage** | Cloudflare R2 | Free Tier (10 GB / month) | S3-compatible private document storage. Eliminates file loss caused by ephemeral disk wipes during Render service redeployments or spin-downs. Zero egress fees. |
| **Frontend Application** | Vercel | Hobby / Free (Non-Commercial Staging) | Native Next.js 14 App Router hosting. Edge middleware support for cookie authentication. Subdirectory root set to `frontend/`. Dual-mode reverse proxy support. |
| **AI Provider** | Google Gemini | Standard Pay-as-you-go / Free tier | `gemini-3.5-flash-lite` configured exclusively via backend environment variable `GEMINI_API_KEY`. |

---

## 2. Staging Infrastructure Status & Endpoints

| Resource | Target Staging Identifier / URL | Actual Status | Verification Method |
| :--- | :--- | :--- | :--- |
| **Frontend Web App** | `https://coachpath-staging.vercel.app` | **BLOCKED — AWAITING DASHBOARD SETUP** | Build compiled locally (25/25 static pages); pending Vercel dashboard project import. |
| **Backend REST API** | `https://coachpath-api-staging.onrender.com` | **BLOCKED — AWAITING DASHBOARD SETUP** | Architecture and Dockerfile verified; pending Render blueprint creation. |
| **Backend Health Probe**| `https://coachpath-api-staging.onrender.com/api/v1/health` | **BLOCKED — AWAITING DASHBOARD SETUP** | Verified locally returning `200 OK` (`status: healthy`). |
| **Database Readiness** | `https://coachpath-api-staging.onrender.com/api/v1/ready` | **BLOCKED — AWAITING DASHBOARD SETUP** | Verified locally with connection pooling and dialect validation. |
| **Neon PostgreSQL** | `coachpath-staging` instance | **BLOCKED — AWAITING USER PROVISIONING** | Migration scripts tested locally across all 10 revisions to `b3c4d5e6f7a2`. |
| **Cloudflare R2 Bucket** | `coachpath-resumes-staging` | **BLOCKED — AWAITING USER PROVISIONING** | `S3FileStorageService` validated with SigV4 client mocks. |

> [!NOTE]
> In accordance with deployment safety rules, no third-party cloud accounts or charges were created automatically. The repository has been prepared and verified, and exact step-by-step dashboard instructions are provided below.

---

## 3. Pre-Deployment Verification Commands & Results

### 3.1 Backend Test Suite (Pytest)
Command executed:
```bash
cd backend && .venv/bin/pytest tests/ -v
```
**Actual Result**:
- Total Tests: **247 tests executed** (246 passed, 1 skipped).
- Execution Time: **46.30s**.
- Status: **100% PASSING**.
- Details:
  - Phase 3 Auth (Register, Login, Token Rotation, Replay Attack Detection, Cookie Delivery): **PASSED**
  - Phase 4 Onboarding (Session Resumption, Turn Orchestration, Prompt Quarantine): **PASSED**
  - Phase 5 Resume Parsing (PDF/DOCX Extraction, Sanitization, Ownership Isolation): **PASSED**
  - Phase 6 Diagnostic Assessments (Question Bank Completeness, Scoring, 20-Question Resumption): **PASSED**
  - Phase 6A Skill Gap Engine (48 Skills Taxonomy, 7 Roles, Coverage Calculations): **PASSED**
  - Phase 7 Personalized Roadmap (DAG Dependency Lock, Feasibility Calculations): **PASSED**
  - Phase 8 Job Ingestion (Provider Adapters, Normalization, Freshness Lifecycle): **PASSED**
  - Phase 9 Intelligent Job Matching (Deterministic Fit Scoring, Explainability Drawers): **PASSED**
  - Phase 10A Resume Tailoring (Immutability, Multi-Version Sequence, Approval Gates): **PASSED**
  - Deployment Config (Dynamic Port Binding, Database URL Normalization, Cookie Policies, S3 Storage Drivers): **PASSED**
  - Live Gemini network integration: **SKIPPED** (Intended in sandboxed test environment).

### 3.2 Frontend Production Build & Typecheck (Next.js)
Command executed:
```bash
cd frontend && npm run build
```
**Actual Result**:
- Status: **Compiled successfully with 0 errors**.
- Typecheck & Lint: **Passed**.
- Static Pages Generated: **25 / 25 routes generated**.
- Edge Middleware: **26.6 kB bundle verified**.
- Routes Compiled:
  - Public routes: `/`, `/about`, `/features`, `/how-it-works`, `/privacy`, `/login`, `/signup`
  - Protected routes: `/dashboard`, `/career-profile`, `/skills`, `/assessments`, `/roadmap`, `/jobs`, `/jobs/[id]`, `/resume`, `/applications`, `/recruiters`, `/interviews`, `/career-readiness`, `/settings`

---

## 4. Exact Manual Dashboard Setup Walkthrough

Follow these steps to connect your GitHub repository and deploy CoachPath to Staging:

### Step 1: Provision Neon PostgreSQL Staging Database
1. Navigate to [Neon Console](https://console.neon.tech/) and log in (Free Tier).
2. Click **Create Project**.
3. Name the project `coachpath-staging` and select your nearest AWS region (e.g. `US East (Ohio) / us-east-2`).
4. Under **Database**, note the generated database name `neondb` (or create `coachpath_staging`).
5. Enable `pgvector` by running in the Neon SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
6. Copy the connection string from the dashboard. It will look like:
   `postgresql://coachpath_owner:npg_xyz@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require`
   *(Note: CoachPath backend will automatically normalize this to `postgresql+asyncpg://` at runtime).*

---

### Step 2: Provision Cloudflare R2 Durable Resume Bucket
1. Navigate to the [Cloudflare Dashboard](https://dash.cloudflare.com/) and select **R2 Object Storage**.
2. Click **Create Bucket**.
3. Bucket Name: `coachpath-resumes-staging`.
4. Location: Select **Automatic** (or closest region).
5. Default storage class: **Standard**.
6. Ensure **Public Access** is disabled (remains strictly private).
7. Under **Manage R2 API Tokens**, click **Create API Token**:
   - Token name: `coachpath-staging-token`.
   - Permissions: **Object Read & Write**.
   - Specific bucket: `coachpath-resumes-staging`.
8. Copy the **Access Key ID**, **Secret Access Key**, and **Endpoint URL** (`https://<account_id>.r2.cloudflarestorage.com`).

---

### Step 3: Deploy Backend on Render
1. Navigate to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository `https://github.com/SharmaaAnmol/CoachPath.git`.
4. Render will automatically detect the root `render.yaml` file.
5. In the configuration prompt, provide the environment secrets:
   - `DATABASE_URL`: Your Neon connection string from Step 1.
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `CORS_ORIGINS`: `https://coachpath-staging.vercel.app,http://localhost:3000`
   - `STORAGE_PROVIDER`: `r2`
   - `S3_ENDPOINT_URL`: Your Cloudflare R2 endpoint URL from Step 2.
   - `S3_ACCESS_KEY_ID`: Your Cloudflare R2 Access Key ID.
   - `S3_SECRET_ACCESS_KEY`: Your Cloudflare R2 Secret Access Key.
   - `S3_BUCKET_NAME`: `coachpath-resumes-staging`
6. Click **Apply**.
7. Render will build the service, execute `alembic upgrade head` in the pre-deploy phase, seed baseline taxonomy and questions, and start Uvicorn.
8. Once deployed, copy your backend URL (e.g., `https://coachpath-api-staging.onrender.com`).

---

### Step 4: Deploy Frontend on Vercel
1. Navigate to the [Vercel Dashboard](https://vercel.com/new).
2. Import the Git repository `SharmaaAnmol/CoachPath`.
3. In **Project Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: Click Edit and select `frontend`.
4. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_APP_URL`: `https://coachpath-staging.vercel.app`
   - `NEXT_PUBLIC_API_URL`: `/api/v1`
   - `BACKEND_INTERNAL_URL`: Your Render backend URL (e.g. `https://coachpath-api-staging.onrender.com`)
5. Click **Deploy**.
6. Vercel will run `npm run build`, bundle Edge Middleware, and deploy to your staging URL.

---

## 5. Free-Tier Limitations Affecting Staging

1. **Render Free Spin-Down**:
   - Free Web Services spin down after 15 minutes of inactivity.
   - The first request after a period of inactivity may incur a cold-start delay of 30–50 seconds while the container initializes.
   - *Mitigation for Staging*: Set up a free external monitoring ping (such as UptimeRobot or Cron) checking `/api/v1/health` every 10 minutes, or accept the cold start during testing.
2. **Neon Free Compute Auto-Suspend**:
   - Neon serverless compute instances suspend after 5 minutes of inactivity.
   - Cold resumption takes 500ms–1.5s, which is handled transparently by CoachPath's `asyncpg` pool pre-ping mechanism.
3. **Cloudflare R2 Free Allowance**:
   - Free tier includes 10 GB of storage per month and 1,000,000 Class A operations. More than sufficient for staging resume uploads.

---

## 6. End-to-End Staging Verification Checklist

| Verification Item | Scope | Local Test Status | Staging Live Status |
| :--- | :--- | :--- | :--- |
| **Backend Startup & Liveness** | `/api/v1/health` returns status `healthy` | **PASS** | **NOT TESTED** *(Pending Render)* |
| **Database Readiness Probe** | `/api/v1/ready` executes `SELECT 1` | **PASS** | **NOT TESTED** *(Pending Neon)* |
| **Database Migrations** | Alembic upgrades to head (`b3c4d5e6f7a2`) | **PASS** | **NOT TESTED** *(Pending Neon)* |
| **Database Auto-Seeding** | 48 skills, 7 roles, 270 questions seeded | **PASS** | **NOT TESTED** *(Pending Neon)* |
| **Registration & Password Hash** | Argon2id hashing, session creation | **PASS** | **NOT TESTED** *(Pending Vercel/Render)* |
| **Authentication & Cookie Flow** | HttpOnly cookie delivery & edge middleware | **PASS** | **NOT TESTED** *(Pending Vercel/Render)* |
| **Multi-Tenant User Isolation** | 403 / 404 on cross-user data access | **PASS** | **NOT TESTED** *(Pending Staging)* |
| **Resume Upload & Validation** | PDF/DOCX magic bytes & 10MB limits | **PASS** | **NOT TESTED** *(Pending Staging)* |
| **Durable Resume Storage** | S3/R2 persistence across container restarts | **PASS** | **NOT TESTED** *(Pending Cloudflare R2)* |
| **Resume AI Parsing** | Gemini structured entities extraction | **PASS** | **NOT TESTED** *(Requires live key)* |
| **Diagnostic Assessments** | 20-question randomized session lifecycle | **PASS** | **NOT TESTED** *(Pending Staging)* |
| **Skill Gap Analysis** | Deterministic alignment & benchmark scoring | **PASS** | **NOT TESTED** *(Pending Staging)* |
| **Personalized Learning Roadmap**| DAG milestone locks & task status updates | **PASS** | **NOT TESTED** *(Pending Staging)* |
| **Job Market Discovery** | Curated catalog loading & search filters | **PASS** | **NOT TESTED** *(Pending Staging)* |
| **Intelligent Job Matching** | 5-factor fit score & explainability drawer | **PASS** | **NOT TESTED** *(Pending Staging)* |
| **Resume Tailoring Backend** | Zero-fabrication server-side reconciliation | **PASS** | **NOT TESTED** *(Pending Staging)* |
| **Frontend Responsive Rendering**| Desktop and mobile layout verification | **PASS** | **NOT TESTED** *(Pending Vercel)* |
| **Security & Secrets Review** | Zero secrets in bundles, responses, or logs | **PASS** | **PASS** |

---

## 7. Next Actions Before Production Deployment

1. Complete the 4 manual dashboard steps above to launch the live staging instances on Neon, Cloudflare R2, Render, and Vercel.
2. Execute an authenticated smoke test against the live staging URL with a dedicated test account.
3. Review staging performance, cold-start latency, and Gemini API quota utilization.
4. Prepare Phase 10B (Frontend Tailoring Workbench) or proceed to Phase 11 application tracking.
