# CoachPath — Personalized Job Matching Frontend Architecture (Phase 9B)

## 1. Executive Overview

Phase 9B connects the Next.js frontend to the authoritative **Intelligent Job Matching Engine (Phase 9A)**. 

The frontend implements a high-integrity, server-authoritative experience where **no match score is ever calculated on the client side**. Every score, evidence coverage rating, skill match classification, strength, gap, and next-step recommendation is derived directly from the backend deterministic scoring engine (`v1.0`).

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CoachPath Next.js Frontend                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   /jobs (JobsPage)                                                              │
│     ├── Tab 1: "Recommended For You"                                            │
│     │     ├── Filter Controls (Fit threshold, workplace type, provisional toggle)│
│     │     ├── JobMatchCard List (Score badge, coverage, skill chips, actions)   │
│     │     └── JobMatchDrawer (4-tab deep explainability slide-over)             │
│     │           ├── Factor Breakdown (5 weighted progress bars)                 │
│     │           ├── Skill Alignment Matrix (Provenance & factual rationale)     │
│     │           ├── Strengths & Gaps (Verified advantages vs critical gaps)     │
│     │           └── Action Plan (Deep-links to Assessments, Roadmap, Skills)    │
│     │                                                                           │
│     └── Tab 2: "All Opportunities"                                              │
│           ├── Full Catalog Explore & Multi-Facet Search                         │
│           ├── Market Intelligence Card (Live wage & role aggregates)            │
│           └── JobDetailModal (Embedded Personalized Match Fit Analysis)         │
│                                                                                 │
│   /jobs/[id] (JobDetailPage)                                                    │
│     └── Full Job Page with Embedded Personalized Fit Card & Explainability CTA   │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │ HTTP / REST API
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     FastAPI Intelligent Job Matching Engine                      │
│                           (Phase 9A Authoritative API)                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  • GET  /api/v1/jobs/recommendations                                            │
│  • GET  /api/v1/jobs/{job_id}/match                                             │
│  • GET  /api/v1/jobs/{job_id}/match-explanation                                 │
│  • POST /api/v1/jobs/{job_id}/match/recalculate                                 │
│  • POST /api/v1/jobs/matches/refresh                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Server-Authoritative Design Principles

1. **Authoritative Backend Scoring**: The frontend never computes or estimates match percentages. Match percentages, evidence coverage, and factor weights are strictly rendered as supplied by the FastAPI backend.
2. **Clear Separation of Fit vs. Evidence Coverage**:
   - **Match Score ($0 - 100\%$)**: How well documented and verified profile data aligns with stated role requirements.
   - **Evidence Coverage ($0 - 100\%$)**: The completeness of evaluated candidate data (skills verified through diagnostic assessments, approved resume extractions, hands-on projects, and documented tenure).
3. **Provisional Fit Flagging**: When evidence coverage is $< 40\%$, the UI prominently renders an amber **Provisional** badge and disclaimer alerting the candidate that confidence is limited due to sparse profile data.
4. **Anti-Hallucination & Provenance Transparency**: Every skill in the Skill Matrix displays its exact evidence provenance:
   - **Diagnostic Assessment**: Objective quiz attempt score % and proficiency tier.
   - **Project Artifact**: Practical projectdeliverable tagged with the canonical skill.
   - **Approved Resume**: Formally approved by candidate during resume review.
   - **Self-Reported**: Candidate profile statement without third-party verification.
5. **Ethical Disclaimers**: All match badges and breakdown views include a prominent disclaimer clarifying that the score is an algorithmic calibration tool and **not a guarantee of interview or employment**.

---

## 3. Component Architecture & Hierarchy

### 3.1. `MatchScoreBadge` (`frontend/src/components/jobs/match-score-badge.tsx`)
Displays the composite match percentage color-coded across four distinct fit tiers:
- **Exceptional Fit ($\ge 80\%$)**: Emerald badge (`#059669`) with `Sparkles` icon.
- **Strong Fit ($70 - 79\%$)**: Sky blue badge (`#0284c7`) with `CheckCircle2` icon.
- **Moderate Fit ($50 - 69\%$)**: Amber badge (`#d97706`) with `AlertCircle` icon.
- **Low Fit ($< 50\%$)**: Slate badge (`#64748b`) with `HelpCircle` icon.

Supports `sm`, `md`, and `lg` sizing with built-in accessibility tooltips and provisional indicators.

### 3.2. `MatchEvidenceCoverage` (`frontend/src/components/jobs/match-evidence-coverage.tsx`)
Visualizes data completeness on a progress bar with three confidence tiers:
- **High Confidence ($\ge 70\%$)**: Green bar and verified shield.
- **Moderate Data ($40 - 69\%$)**: Sky blue bar.
- **Sparse Evidence ($< 40\%$)**: Amber warning bar.

### 3.3. `JobMatchCard` (`frontend/src/components/jobs/job-match-card.tsx`)
Interactive recommendation card featuring:
- Role title, company name, location, workplace modality, compensation range, and posting freshness.
- Score pill (`MatchScoreBadge`) and data completeness (`MatchEvidenceCoverage`).
- Mandatory matched skills (green pills with checkmarks) and missing required skills (rose pills).
- Teaser snippets for key candidate strengths and identified deficits.
- Action triggers: "Match Breakdown" (opens `JobMatchDrawer`) and "View Details" (opens `JobDetailModal`).

### 3.4. `JobMatchDrawer` (`frontend/src/components/jobs/job-match-drawer.tsx`)
Accessible slide-over drawer conforming to API Spec Section 8.2:
- **Header**: Job metadata, composite score, coverage bar, stale result alert, and quick "Recalculate Fit" button.
- **Tab 1: Factor Breakdown**: 5 progress bars reflecting configured weights:
  1. *Skill Alignment* (50% weight)
  2. *Professional Experience* (15% weight)
  3. *Project Evidence* (15% weight)
  4. *Location & Work Mode* (10% weight)
  5. *Role & Compensation Preferences* (10% weight)
  - Evaluated vs. Normalized factor tags.
- **Tab 2: Skill Alignment Matrix**:
  - Filter pills: All, Matched, Partially Matched, Missing, Mandatory, Preferred.
  - Table rows with mandatory/preferred chips, classification badges, provenance indicators, and factual explanations.
- **Tab 3: Strengths & Gaps**:
  - Grounded hiring rationale summary paragraph.
  - Verified candidate strengths list.
  - Identified skill gaps and deficits list.
- **Tab 4: Action Plan**:
  - Grounded CoachPath recommendations to improve fit.
  - Deep-link ecosystem shortcuts: `/assessments` (take diagnostic assessments), `/roadmap` (add skill to learning roadmap), `/skills` (skill taxonomy & gap analysis), `/profile` (update preferences).
- **Footer**: Recalculate button, external application link ("Apply on Site"), and full job details shortcut.

### 3.5. `JobDetailModal` & `JobDetailPage` (`/jobs/[id]`)
Both the modal and standalone job detail route embed a dedicated **Personalized Match Fit Analysis** card displaying the candidate's real match score, evidence coverage, quick 5-factor preview, and drill-down CTAs.

---

## 4. State Management & API Integration

The `jobMatchingClient` (`frontend/src/lib/job-matching-client.ts`) interfaces with all 6 Phase 9A backend endpoints:

| Frontend Method | Backend Route | Purpose |
| :--- | :--- | :--- |
| `getRecommendations(query)` | `GET /api/v1/jobs/recommendations` | Fetches personalized matches ranked by score with pagination & filters |
| `getJobMatch(jobId)` | `GET /api/v1/jobs/{job_id}/match` | Retrieves or calculates match for a specific job |
| `getJobMatchExplanation(jobId)` | `GET /api/v1/jobs/{job_id}/match-explanation` | Retrieves explainability drawer data |
| `recalculateJobMatch(jobId)` | `POST /api/v1/jobs/{job_id}/match/recalculate` | Forces recalculation of match and resets stale status |
| `refreshRecommendations()` | `POST /api/v1/jobs/matches/refresh` | Batch recalculates recommendations across all active opportunities |
| `listMatches()` | `GET /api/v1/jobs/matches` | Lists all evaluated matches for profile |

### State Synchronization on Recalculation
When a match is recalculated in `JobMatchDrawer` or `JobDetailPage`, the updated match is propagated into the local recommendation item list immediately, updating the score badge, progress bar, and stale status without requiring a page refresh.

---

## 5. Verification & Testing Summary

1. **Frontend Production Build**: `npm run build` completed with zero TypeScript errors across all 25 routes.
2. **ESLint Audit**: `npm run lint` completed with zero errors and zero warnings.
3. **Automated Integration Tests**: `backend/tests/test_phase9b_frontend_integration.py` executed with 6 integration tests passing:
   - Recommendations contract and ranking descending validation.
   - Query filters (`min_score`, `remote_type`, `include_provisional`).
   - Explainability drawer schema and skill provenance.
   - Single match retrieval and forced recalculation.
   - Batch recommendation refresh.
   - Multi-tenant authentication enforcement.
