# CoachPath — Frontend Architecture & Design System Specification

**Document Version**: 1.0.0  
**Phase**: Phase 1 (Frontend Foundation + Design System + Product Shell)  
**Status**: Authoritative Reference  
**Last Updated**: October 2026  

---

## 1. Executive Summary & Objective

CoachPath is an AI-powered career intelligence platform designed to guide software engineers through a continuous, closed-loop growth and hiring journey:

$$\text{Central Career Profile} \longrightarrow \text{Diagnostic Assessments} \longrightarrow \text{Skill Gap Matrix} \longrightarrow \text{Personalized Roadmap} \longrightarrow \text{Semantic Job Matching} \longrightarrow \text{Truthful Resume Diff} \longrightarrow \text{Application Pipeline} \longrightarrow \text{Recruiter Gate} \longrightarrow \text{STAR Interview Prep} \longrightarrow \text{Career Readiness Index}$$

The primary objective of **Phase 1** is to establish the production-grade frontend foundation, atomic design system, and product shell for all 12 platform domains, completely decoupled from backend persistence or generative AI providers. The entire application is built using Next.js 14 (App Router), TypeScript, Tailwind CSS, and Lucide React icons, grounded in a typed mock data layer modeling benchmark candidate **Aarav Mehta**.

---

## 2. Technology Stack & Architectural Decisions

| Layer | Selection | Version | Decision Rationale |
| :--- | :--- | :--- | :--- |
| **Framework** | Next.js (App Router) | 14.2.15 | Zero-config server-side rendering, streaming suspense, nested route layouts (`(public)` vs `(app)`), and edge caching. |
| **Language** | TypeScript | 5.6.3 | Strict type contracts between UI components, mock data stores, and future FastAPI backend endpoints. |
| **Styling** | Tailwind CSS | 3.4.14 | Atomic utility classes, semantic CSS variable tokens, fast compile times, and design consistency. |
| **Icons** | Lucide React | 0.453.0 | Modern, lightweight, accessible SVG icon library with consistent 24x24 stroke grids. |
| **State & Data Fetching** | TanStack Query | 5.59.16 | Declarative caching, background re-validation, optimistic UI updates, and seamless future REST hook binding. |
| **Utilities** | `clsx` + `tailwind-merge` | 2.1.1 / 2.5.4 | Conflict-free dynamic className generation via custom `cn()` helper. |

---

## 3. Directory Topology & Workspace Layout

The frontend codebase is contained entirely under `/frontend`, adhering to the standard Next.js App Router workspace layout:

```
frontend/
├── package.json                   # Dependencies, build scripts, and linting rules
├── tsconfig.json                  # Strict TypeScript configuration with @/* path alias
├── tailwind.config.ts             # Semantic palette tokens, animations, and custom shadows
├── postcss.config.mjs             # PostCSS Tailwind and Autoprefixer integration
├── next.config.mjs                # Next.js App Router config and legacy route redirects
├── .eslintrc.json                 # Next.js Core Web Vitals ESLint rules
└── src/
    ├── app/                       # App Router file-system routes
    │   ├── layout.tsx             # Root HTML layout with fonts and TanStack Query Provider
    │   ├── globals.css            # CSS variables, typography, and scrollbar styles
    │   ├── (public)/              # Public unauthenticated routes
    │   │   ├── layout.tsx         # Header + Footer marketing layout
    │   │   ├── page.tsx           # High-converting Landing Page with Interactive Preview
    │   │   ├── about/page.tsx     # Mission, values, and candidate story
    │   │   ├── how-it-works/page.tsx # 10-step connected career journey walkthrough
    │   │   ├── features/page.tsx  # Breakdown of 12 platform capabilities
    │   │   ├── privacy/page.tsx   # Responsible AI, GDPR rights, and anti-hallucination policy
    │   │   ├── login/page.tsx     # Sign In with one-click Aarav Mehta demo fill
    │   │   └── signup/page.tsx    # Sign Up with persona and role selection
    │   └── (app)/                 # Authenticated application shells
    │       ├── layout.tsx         # AppShell with persistent Sidebar & Topbar
    │       ├── dashboard/page.tsx # Executive candidate dashboard
    │       ├── career-profile/page.tsx # Profile editor, experience, and verified projects
    │       ├── profile/page.tsx   # Canonical route alias -> /career-profile
    │       ├── skills/page.tsx    # Tri-state skill taxonomy & market gap matrix
    │       ├── assessments/page.tsx # Diagnostic test suite & interactive question runner
    │       ├── roadmap/page.tsx   # 3-phase dynamic milestone roadmap & deliverable proof
    │       ├── jobs/page.tsx      # Semantic pgvector job discovery & score explanations
    │       ├── resume/page.tsx    # Two-pass anti-hallucination diff review & export
    │       ├── applications/page.tsx # 4-stage Kanban pipeline tracker
    │       ├── recruiters/page.tsx# Recruiter discovery & manual copy outreach gate
    │       ├── interviews/page.tsx# Scheduled interview drill & STAR question bank
    │       ├── career-readiness/page.tsx # Composite 0-100% index across 4 pillars
    │       ├── readiness/page.tsx # Canonical route alias -> /career-readiness
    │       └── settings/page.tsx  # AI guardrails, notifications, and data deletion
    ├── components/
    │   ├── layout/                # Shell layout navigation components
    │   │   ├── sidebar.tsx        # Collapsible desktop sidebar & mobile drawer
    │   │   ├── topbar.tsx         # Breadcrumbs, search, notifications, and user avatar
    │   │   ├── app-shell.tsx      # Authenticated shell layout coordinator
    │   │   ├── public-header.tsx  # Marketing navigation header
    │   │   └── public-footer.tsx  # Marketing footer and compliance disclosures
    │   ├── landing/               # Specialized landing page interactive components
    │   │   └── interactive-preview.tsx # Live interactive preview with tab switching
    │   └── ui/                    # Atomic & domain design system components
    │       ├── button.tsx         # Primary, secondary, outline, ghost, destructive, intelligence
    │       ├── badge.tsx          # Semantic status chips (verified, action, gap, intelligence)
    │       ├── card.tsx           # Card, CardHeader, CardTitle, CardContent, CardFooter
    │       ├── input.tsx          # Form inputs with validation error states
    │       ├── textarea.tsx       # Multi-line inputs with helper text
    │       ├── progress-bar.tsx   # Animated progress bars with semantic color variants
    │       ├── stat-card.tsx      # Metrics card with icons and trends
    │       ├── modal.tsx          # Accessible modal dialog with backdrop dismiss
    │       ├── tabs.tsx           # Accessible tab navigation bar with counters
    │       ├── alert.tsx          # Banner notifications (success, warning, info, danger)
    │       ├── skeleton.tsx       # Pulse loading placeholders
    │       ├── empty-state.tsx    # Null state illustration and action button
    │       ├── skill-badge.tsx    # Interactive skill chip with confidence indicator
    │       ├── job-card.tsx       # Semantic job posting with explainable score factors
    │       ├── assessment-card.tsx# Diagnostic test card with difficulty and duration
    │       └── diff-viewer.tsx    # Two-pass resume diff comparison with accept/reject controls
    ├── lib/
    │   ├── utils.ts               # Class merging (cn) and formatting helpers
    │   └── mock/
    │       └── data.ts            # Typed mock store for candidate Aarav Mehta
    ├── providers/
    │   └── query-provider.tsx     # React Query client provider with stale-time policies
    └── types/
        └── index.ts               # Authoritative TypeScript domain interfaces
```

---

## 4. Design System Tokens & Semantic Color Palette

CoachPath avoids childish gradients or flashy AI gimmicks in favor of a calm, institutional SaaS aesthetic. The palette communicates state with scientific precision:

| Token Name | Hex Values | Functional Role | UI Usage |
| :--- | :--- | :--- | :--- |
| **Brand Primary** | `#4F46E5` / `#6366F1` | Primary platform identity | Primary CTA buttons, active sidebar links, key action focus states. |
| **Intelligence (AI)** | `#7C3AED` / `#8B5CF6` | AI analysis & recommendations | Vector match pills, AI diff suggestions, diagnostic test runners, readiness scores. |
| **Verified (Strengths)** | `#059669` / `#10B981` | Calibrated skills & passing grades | Verified skill chips, passed test badges, accepted resume bullet diffs. |
| **Action (Goals)** | `#D97706` / `#F59E0B` | In-progress milestones & warnings | Roadmap sprint tasks, developing skills, active interview preparation reminders. |
| **Gap (Deficits / Danger)**| `#E11D48` / `#EF4444` | Missing market skills & alerts | Missing skill tags, ungrounded resume claims, account deletion danger zone. |
| **Surfaces (Neutral)** | `#F8FAFC` to `#0F172A` | Backgrounds, cards, and borders | Card backgrounds (`#FFFFFF` light, `#111827` dark), subtle borders (`#E2E8F0`). |

---

## 5. Domain Shells & User Journeys

Each of the 12 platform domains delivers a complete interactive shell:

### 1. Executive Dashboard (`/dashboard`)
- Welcomes candidate Aarav Mehta with calibrated 78% Career Readiness Index.
- High-priority banner alerting to upcoming Stripe System Design interview.
- Active sprint card featuring Phase 1 Task 103 (Redis Architecture Diagnostic).
- Top semantic job matches with inline score factor toggles.

### 2. Career Profile Graph (`/career-profile` & `/profile`)
- Authoritative profile view with tabs: Overview, Experience, Verified Projects, Education & Certs.
- Includes evidence verification tags linking claims to GitHub repositories (`distributed-metrics-broker`, `querylens-pg`).
- Modal for re-parsing PDF resumes without overriding verified test grades.

### 3. Skill Taxonomy & Competency Engine (`/skills`)
- Tri-state visualization: Verified Strengths (6), Developing Skills (3), Identified Market Gaps (3).
- Filterable by engineering categories: Languages, Frameworks, Cloud & DevOps, Databases, Architecture.
- Calibrated confidence bars (e.g. TypeScript 92%, PostgreSQL 84%, Kubernetes 15%).

### 4. Diagnostic Skill Assessments (`/assessments`)
- Standardized 15-minute diagnostic tests validating real code competency.
- Interactive Diagnostic Runner modal with code snippet inspection, multiple-choice questions, and deterministic scoring.

### 5. Dynamic Milestone Roadmap (`/roadmap`)
- 9-week curriculum divided into 3 progressive phases:
  - Phase 1: High-Performance Caching & Data Consistency (75% Complete).
  - Phase 2: Distributed Event Streaming & Observability (10% Complete).
  - Phase 3: Production Infrastructure & System Design (0% Complete).
- Each task includes an hour budget, curated resource URL, and deliverable submission modal.

### 6. Semantic Job Discovery (`/jobs`)
- Vector similarity search ranking opportunities across top employers (Stripe 94%, Linear 91%, Vercel 87%, Datadog 81%).
- Multi-factor score breakdown: Skills (40%), Experience (25%), Domain (20%), Role Seniority (15%).
- Matched skills badges (emerald) vs missing skill gap pills (rose).

### 7. Truthful Resume Optimization (`/resume`)
- Specialized two-pass anti-hallucination diff viewer.
- Side-by-side comparison of original vs suggested text with rationale and evidence grounding proof.
- Candidate approval controls: Accept (bakes change into resume) or Discard (rejects modification).

### 8. Application Pipeline Tracker (`/applications`)
- Visual Kanban board with 4 columns: Saved Opportunities, Submitted Applications, Active Interviewing, Offers Extended.
- Displays next action deadlines, salary bands, and interview dates.

### 9. Recruiter Discovery & Outreach Gate (`/recruiters`)
- Direct talent leads for target companies (Sarah Jenkins @ Stripe, Marcus Chen @ Linear).
- Personalized outreach drafts highlighting candidate accomplishments.
- Strict manual copy-to-clipboard gate to enforce candidate agency and prevent bot spam.

### 10. Interview Preparation & STAR Bank (`/interviews`)
- Scheduled round tracking for Stripe Connect Infrastructure.
- Role-specific question bank with comprehensive STAR story structures (Situation, Task, Action, Result) and key talking points.

### 11. Career Readiness Index (`/career-readiness` & `/readiness`)
- Comprehensive 0-100% composite index across 4 objective pillars:
  1. Skill Verification (Weight: 35%, Score: 82%)
  2. Demonstrated Projects (Weight: 25%, Score: 75%)
  3. Market Relevance (Weight: 25%, Score: 85%)
  4. Interview Fluency (Weight: 15%, Score: 70%)
- Tailored recommendations to reach the 85%+ readiness tier.

### 12. Settings & Privacy Controls (`/settings`)
- Account information and notification preferences.
- AI Guardrail enforcement toggles: Mandatory two-pass auditor, manual recruiter copy confirmation.
- GDPR Art. 20 JSON data export and permanent account deletion confirmation modal.

---

## 6. Route Aliasing & Canonical Paths

To honor both `docs/user-flows.md` and standard URL naming conventions, route aliases are supported at both Next.js configuration and page component levels:

- `/profile` $\longrightarrow$ Redirects / Aliases to `/career-profile`
- `/readiness` $\longrightarrow$ Redirects / Aliases to `/career-readiness`

---

## 7. Mock Data Layer & Future REST Integration Strategy

The mock data layer (`src/lib/mock/data.ts`) models candidate **Aarav Mehta** using strict TypeScript interfaces (`src/types/index.ts`). In Phase 2 and Phase 3:
1. React Query hooks (e.g. `useProfile()`, `useSkills()`, `useRoadmap()`, `useJobMatches()`) will be introduced.
2. The typed Fetch/Axios client configured in Phase 2 will query the FastAPI endpoints defined in `/docs/api-specification.md`.
3. Because UI components consume typed data interfaces rather than raw HTTP responses, switching from mock data to real API hooks requires zero UI component refactoring.

---

## 8. Build & Verification Status

The frontend application has been verified to build cleanly:
- `npm run lint`: **0 errors, 0 warnings**
- `tsc --noEmit`: **0 type errors**
- `npm run build`: **Compiled successfully with valid static routes**
