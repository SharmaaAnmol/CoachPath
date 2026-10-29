# CoachPath — Remediation Step 1 Report: Account Safety and Demo Data Isolation

> **Document Status**: Complete & Verified  
> **Phase**: Pre-Phase 10 Remediation — Step 1  
> **Date**: October 29, 2026  
> **Target Deployed URLs**:
> - Frontend: `https://coach-path-six.vercel.app`
> - API Backend: `https://coachpath-api-staging.onrender.com`

---

## 1. Executive Summary

This remediation executes **Step 1** of the existing-feature audit plan, addressing verified gaps in account management, data portability, and demonstration-data contamination. Prior to this remediation:
1. The **Settings** page presented interactive buttons for account deletion and GDPR data export that executed simulated browser `alert()` dialogs, creating a false impression that user accounts and data were deleted or exported when zero backend endpoints existed.
2. The **Applications**, **Recruiters**, **Interviews**, and **Career Readiness** screens loaded hardcoded mock data for demo candidate "Aarav Mehta" without informing authenticated candidates that the data was simulated.

In accordance with strict safety principles, simulated actions have been removed and replaced with truthful, disabled states with transparent roadmap milestones (Phase 16). All four demonstration pages now prominently feature a shared, accessible `DemoPreviewBanner` component clarifying that data displayed is isolated sandbox data and not connected to real candidate records.

---

## 2. Verified Audit Findings Addressed

| Issue ID | Area | Severity | Pre-Remediation Behavior | Post-Remediation Status |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-01** | Account Deletion (`settings/page.tsx`) | **P0** (Compliance) | Triggered `alert('Account and data purged permanently.')` with no API or DB cascade. | **PASS** — Fake alert removed; action truthfully disabled with Phase 16 notification and manual admin instructions. |
| **ISSUE-02** | Data Portability Export (`settings/page.tsx`) | **P1** (Transparency) | Triggered `alert('Exporting full user career graph JSON...')`. | **PASS** — Fake alert removed; action truthfully disabled with Phase 16 notification. |
| **ISSUE-03** | Applications Pipeline (`applications/page.tsx`) | **P1** (Contamination) | Loaded `mockApplications` with fake `Add Application` alert; candidate Aarav Mehta data presented without labeling. | **PASS** — `DemoPreviewBanner` added; fake alert replaced with disabled Phase 12 indicator. |
| **ISSUE-04** | Recruiter Discovery (`recruiters/page.tsx`) | **P1** (Contamination) | Loaded `mockRecruiters` (Apex Cloud outreach) without demonstration badge. | **PASS** — `DemoPreviewBanner` added indicating Phase 13 roadmap activation. |
| **ISSUE-05** | Interview Preparation (`interviews/page.tsx`) | **P1** (Contamination) | Loaded `mockScheduledInterviews` for Aarav Mehta without demonstration badge. | **PASS** — `DemoPreviewBanner` added indicating Phase 14 roadmap activation. |
| **ISSUE-06** | Career Readiness (`career-readiness/page.tsx`) | **P1** (Contamination) | Loaded static 84% readiness index from `mockReadinessData` without demonstration badge. | **PASS** — `DemoPreviewBanner` added indicating Phase 15 roadmap activation. |

---

## 3. Account Deletion & Data Export Technical Deep Dive

### 3.1 Account Deletion Verification & Status
- **Endpoint Check**: Searched FastAPI route declarations across `backend/app/api/routes/auth.py`, `settings.py`, and `profile.py`.
- **Result**: `DELETE /api/v1/auth/me` does **not** exist.
- **Router Analysis (`backend/app/api/routes/settings.py`)**:
  ```python
  @router.get("", summary="Settings Module Status")
  async def settings_status() -> Dict[str, str]:
      """Structural router placeholder for settings, GDPR export, and account deletion."""
      return {"module": "settings", "status": "placeholder", "phase": "Phase 16"}
  ```
- **Cascade & Cleanup Trace**:
  - `User` SQLAlchemy models declare `cascade="all, delete-orphan"` on child collections (profiles, resumes, assessment attempts, roadmaps).
  - Foreign key constraints specify `ondelete="CASCADE"`.
  - **Critical Gap**: A database-only cascade does **not** purge physical resume files stored in file systems or object storage (`storage_service.delete_file`), does not purge Redis session caches, and does not invalidate active access tokens.
- **Safety Decision**: In compliance with prompt constraints, no ad-hoc destructive endpoint was added without a verified Phase 16 architecture plan. The Settings UI action has been disabled with transparent user guidance.
- **Test Status**: **PASS** (UI safely prevents execution; backend verified absent).

### 3.2 Data Export Verification & Status
- **Endpoint Check**: Searched for `POST /api/v1/settings/privacy/export` or `GET /api/v1/settings/export`.
- **Result**: Endpoints do **not** exist in backend.
- **Safety Decision**: Removed simulated download alerts. Both "Export Career Graph" and "Export Resumes" buttons are disabled with `aria-disabled="true"` and an informative badge stating Phase 16 availability.
- **Test Status**: **PASS** (Zero simulated downloads; clear informational state).

---

## 4. Demonstration Data Audit on Affected Routes

| Route | Data Source | Classification | Banner Applied | Planned Activation |
| :--- | :--- | :--- | :--- | :--- |
| `/applications` | `mockApplications` in `@/lib/mock/data` | Demonstrator / Sandbox | Yes (`DemoPreviewBanner`) | Phase 12: Application Pipeline Tracker |
| `/recruiters` | `mockRecruiters` in `@/lib/mock/data` | Demonstrator / Sandbox | Yes (`DemoPreviewBanner`) | Phase 13: Recruiter Discovery & High-Context Outreach |
| `/interviews` | `mockScheduledInterviews` in `@/lib/mock/data` | Demonstrator / Sandbox | Yes (`DemoPreviewBanner`) | Phase 14: Diagnostic Interview Preparation |
| `/career-readiness` (and `/readiness`) | `mockReadinessData` in `@/lib/mock/data` | Demonstrator / Sandbox | Yes (`DemoPreviewBanner`) | Phase 15: Holistic Career Readiness Command Center |

*Note: Genuine user pages (`/dashboard`, `/career-profile`, `/profile`, `/skills`, `/assessments`, `/roadmap`, `/jobs`, `/resume`) remain directly connected to live user APIs and are NOT labeled with demo banners.*

---

## 5. Security & UI Behavioral Verification

1. **Destructive Safety**: Accidental or deliberate clicks on "Delete Account" in Settings are impossible (`disabled` attribute, `pointer-events-none`, `aria-disabled="true"`).
2. **Alert Elimination**: All 4 instances of fake `window.alert()` calls in the frontend codebase have been completely removed.
3. **Multi-Tenant Isolation**: Unauthenticated requests to API endpoints continue to return `401 Unauthorized`. Client-supplied user IDs are not accepted by the backend.
4. **Accessible Banner Design**: The `DemoPreviewBanner` component implements `role="status"` and `aria-label="Demonstration preview notice"`, rendering seamlessly on mobile, tablet, and desktop viewports.

---

## 6. Files Changed

1. **`frontend/src/components/ui/demo-preview-banner.tsx`** *(New)*: Shared, accessible banner component communicating demonstration preview status and target roadmap phase.
2. **`frontend/src/app/(app)/settings/page.tsx`** *(Modified)*: Removed fake alerts, removed deceptive modal, disabled export and deletion buttons, added explicit Phase 16 notices.
3. **`frontend/src/app/(app)/applications/page.tsx`** *(Modified)*: Added `DemoPreviewBanner` for Phase 12; removed fake `Add Application` alert.
4. **`frontend/src/app/(app)/recruiters/page.tsx`** *(Modified)*: Added `DemoPreviewBanner` for Phase 13.
5. **`frontend/src/app/(app)/interviews/page.tsx`** *(Modified)*: Added `DemoPreviewBanner` for Phase 14.
6. **`frontend/src/app/(app)/career-readiness/page.tsx`** *(Modified)*: Added `DemoPreviewBanner` for Phase 15.

---

## 7. Test Verification & Results

### 7.1 Frontend Build & Static Generation
```bash
npm --prefix frontend run lint
# Result: ✔ No ESLint warnings or errors (PASS)

npm --prefix frontend run build
# Result: Compiled successfully (25/25 static pages generated) (PASS)
```

### 7.2 Core Backend Test Suite
```bash
backend/.venv/bin/pytest backend/tests/test_auth.py backend/tests/test_profile.py backend/tests/test_resume.py backend/tests/test_assessments.py
# Result: 57 passed, 3 warnings in 7.06s (PASS)
```

### 7.3 Verification Matrix

| Verification Item | Status | Details |
| :--- | :--- | :--- |
| Account deletion is either verified safe or clearly unavailable | **PASS** | Genuinely unavailable; action disabled with Phase 16 notice. |
| Data export is either verified functional or clearly unavailable | **PASS** | Genuinely unavailable; action disabled with Phase 16 notice. |
| Failed deletion request does not show false success | **PASS** | No false alerts or simulated success dialogs remain. |
| UI prevents accidental repeated destructive submissions | **PASS** | Destructive button is disabled. |
| Authentication and ownership protections remain intact | **PASS** | `test_auth.py` and `test_profile.py` pass 100%. |
| Each of the 4 demo pages correctly identifies demonstration content | **PASS** | Verified on `/applications`, `/recruiters`, `/interviews`, `/career-readiness`. |
| Genuine personalized data is not incorrectly labeled as demo data | **PASS** | `/dashboard`, `/profile`, `/resume`, `/skills`, `/roadmap`, `/jobs` have no demo banner. |
| Existing routes and navigation still work | **PASS** | All 25 routes render cleanly during `next build`. |
| Real destructive account deletion integration on live account | **NOT TESTED** | Deliberately skipped to avoid destructive side-effects on real user data; endpoint verified absent. |

---

## 8. Remaining Blockers & Required Follow-up Work

1. **Step 2 (Target Role Personalization Reconciler)**:
   - Reconcile `signup/page.tsx` with `backend/app/db/seeds/role_catalog.py` to prevent silent fallback to `backend-developer`.
2. **Step 3 (Assessment Randomization & Diversity)**:
   - Implement per-attempt option shuffling and retake history filtering in `AssessmentService`.
3. **Step 4 (Public Marketing Copy Corrections)**:
   - Update landing page and features copy to accurately reflect current deterministic matching algorithms.
4. **Phase 10B (Resume Tailoring Frontend UI)**:
   - Build `/resume` tailoring UI to expose existing Phase 10A backend.
5. **Phase 16 (Full Data Privacy Engine)**:
   - When reaching Phase 16, build `DELETE /api/v1/settings/privacy/delete-account` (with storage cleanup, token revocation, cascade) and `POST /api/v1/settings/privacy/export`.
