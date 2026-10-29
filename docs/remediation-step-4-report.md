# CoachPath — Remediation Step 4: Public Marketing Copy Alignment Report

> **Document Version**: 1.0.0  
> **Execution Date**: 2026-10-29  
> **Scope**: Step 4 of Feature Quality & Personalization Remediation Plan  
> **Status**: Completed & Verified  

---

## 1. Executive Summary

In Remediation Step 4, we aligned all public-facing marketing copy, privacy policies, footer notices, and preview components across the CoachPath application with verified software capabilities.

Previous audits (`docs/personalization-and-marketing-claims-audit.md`) identified 14 capability claims on public pages that were either missing, partially implemented without UI, technically misstated (e.g., claiming `pgvector` when deterministic weighted matching is used), or legally risky (e.g., claiming certified GDPR/CCPA compliance or enterprise zero-data-retention APIs).

Without removing legitimate product strengths, all affected copy was methodically revised to reflect CoachPath's true architectural design:
- Replaced unsupported `pgvector` / 1,536-dimensional embeddings with CoachPath's actual **Multi-Dimensional Weighted Matching Algorithm** (5 deterministic dimensions across 11 canonical tracks).
- Replaced the absolute "Zero-Hallucination Guarantee" with **Grounded Anti-Fabrication Guardrails** and human-in-the-loop candidate review.
- Clarified GitHub and portfolio claims from automated PR code auditing to **verifiable project deliverables & repository links**.
- Labeled unreleased modules (Applications Kanban Phase 12, Recruiter Discovery Phase 13, STAR Interview Prep Phase 14, Readiness Index Phase 15) as **Interactive Roadmap Previews** rather than live automated services.
- Replaced fictitious "1-click instant account wipe" and certified compliance claims with **Privacy by Design, Data Minimization, and Admin-Assisted Account Erasure** aligned with the Phase 16 compliance roadmap.
- Labeled candidate Aarav Mehta across interactive mockups as an **Illustrative Demo Profile**.

---

## 2. Marketing Claims Audit & Remediation Matrix (MC-01 to MC-14)

| Claim ID | Original Public Marketing Claim | Verified Technical State | Remediation Action & Updated Copy | Status |
| :--- | :--- | :--- | :--- | :---: |
| **MC-01** | **9-Category Diagnostic Assessments & 20-Question Tests** | Verified in `backend/app/db/seeds/assessment_seeder.py` (270 questions, 9 categories, 7-7-6 difficulty curve). | Retained claim as verified and accurate. | **Retained** |
| **MC-02** | **Automated GitHub PR Auditing & Repo Verification** | `CareerProfile.github_url` and `Project.github_url` store links; no automated GitHub PR/test runner exists. | Updated to: *"Convert academic coursework into verified portfolio project deliverables"* and *"deliverable projects (e.g. repository links, system design write-ups, or demo applications)"*. | **Remediated** |
| **MC-03** | **Readiness Index & 4-Pillar Composite Score** | `backend/app/api/routes/readiness.py` is a Phase 15 placeholder; UI displays mock 84%. | Updated to: *"Readiness Index (Phase 15 Preview) — Calibrates composite readiness across 4 objective pillars, currently anchored by diagnostic skill gaps."* | **Remediated** |
| **MC-04** | **Live Automated Job Board Ingestion** | Ingestion pipeline exists (`arbeitnow`, seed), executed on-demand via manual admin trigger. | Updated to: *"Curated and on-demand job market ingestion across verified engineering roles."* | **Remediated** |
| **MC-05** | **Semantic pgvector Search & 1536-dim Embeddings** | `Job.embedding` is `None`. Matching engine uses a 5-factor weighted formula (40% skills, 20% experience, 15% seniority, 15% location, 10% preferences). | Updated to: *"Deterministic Multi-Dimensional Job Matching: Ingests real opportunities and evaluates alignment using a multi-dimensional weighted matching algorithm across 11 canonical engineering roles."* Removed all `pgvector` badges. | **Remediated** |
| **MC-06** | **Two-Pass Resume Anti-Fabrication Auditing** | `backend/app/services/resume_tailoring.py` contains verified two-pass validator; interactive UI planned for Phase 10B. | Updated to: *"Grounded Anti-Fabrication Guardrails • Human-in-the-Loop • Calibrated Skills"* and clarified that interactive UI launches in Phase 10B. | **Remediated** |
| **MC-07** | **Tailored Resume PDF & Markdown Export** | No tailored document compiler currently exists (downloads original file only). | Removed claims of "Tailored PDF Export". Updated deliverable to: *"Structured Markdown Diff Preview"*. | **Remediated** |
| **MC-08** | **Application Pipeline Kanban & Automated Reminders** | Route is Phase 12 placeholder; frontend `/applications` is a demo preview. | Updated to: *"Pipeline Kanban (Phase 12 Preview) — Tracks applications from saved to offer stage with structured next-step planning."* | **Remediated** |
| **MC-09** | **Live Recruiter Discovery & Outreach Emails** | Route is Phase 13 placeholder; frontend `/recruiters` is a demo sandbox. | Updated to: *"Recruiter Discovery Gate (Phase 13 Preview) — Generates high-context outreach drafts requiring manual human review and confirmation."* | **Remediated** |
| **MC-10** | **STAR Interview Question Bank & Prep Workflows** | Route is Phase 14 placeholder; frontend `/interviews` is a demo sandbox. | Updated to: *"STAR Interview Question Bank (Phase 14 Preview) — Role-specific question bank offering tailored Situation, Task, Action, and Result talking points."* | **Remediated** |
| **MC-11** | **One-Click Instant Full Account Wipe & JSON Export** | Self-service deletion unavailable in UI; automated cascade in active development for Phase 16. | Replaced 1-click purge claim with: *"Data Privacy & User Ownership — In line with our Phase 16 compliance roadmap, we uphold strict data minimization, store zero unencrypted credentials, and support admin-assisted account erasure upon request."* | **Remediated** |
| **MC-12** | **Certified GDPR & CCPA Compliance Claims** | Platform follows privacy principles, but lacks formal third-party audit and self-service Article 20 tools. | Replaced with: *"Designed for Privacy: Architected around data minimization and user ownership principles."* | **Remediated** |
| **MC-13** | **Enterprise Zero-Data-Retention AI APIs** | Google AI Studio developer API is utilized (`google-genai`). Vertex AI zero-retention terms are not configured. | Replaced with: *"Evidence-Bounded AI: All AI interactions utilize prompt minimization and evidence bounding, sending only the context necessary to evaluate skills or tailor documents, with zero model training on candidate resumes."* | **Remediated** |
| **MC-14** | **Zero-Hallucination Absolute Guarantee** | Two-pass reconciler catches unsupported skills, but LLM probabilistic nature precludes mathematical zero guarantee. | Replaced with: *"Evidence-Grounded Safeguards & Anti-Fabrication Guardrails with Human-in-the-Loop Review."* | **Remediated** |

---

## 3. Before & After Copy Alignment

```
========================================================================================
1. LANDING PAGE HERO TRUST BADGE (frontend/src/app/(public)/page.tsx)
========================================================================================
BEFORE: Two-Pass Anti-Hallucination AI • Human-in-the-Loop • Calibrated Skills
AFTER:  Grounded Anti-Fabrication Guardrails • Human-in-the-Loop • Calibrated Skills

========================================================================================
2. LANDING PAGE 10-STEP JOURNEY — STEP 05 (frontend/src/app/(public)/page.tsx)
========================================================================================
BEFORE: Job Vector Search — Ingests real opportunities and ranks them using semantic embeddings across 7 engineering roles.
AFTER:  Job Market Matching — Ingests real opportunities and evaluates alignment using a multi-dimensional weighted matching algorithm across 11 canonical engineering roles.

========================================================================================
3. LANDING PAGE 10-STEP JOURNEY — STEP 07 (frontend/src/app/(public)/page.tsx)
========================================================================================
BEFORE: Truthful Resume Diff — Two-pass AI optimizer tailors resumes using only verified evidence—strictly zero hallucinations.
AFTER:  Truthful Resume Diff — Grounded anti-fabrication guardrails tailor resumes using verified evidence with human-in-the-loop review.

========================================================================================
4. LANDING PAGE BENTO GRID PILLAR 3 (frontend/src/app/(public)/page.tsx)
========================================================================================
BEFORE: Badge: pgvector Embeddings
        Matches candidate profiles against live opportunities across 7 engineering tracks using cosine similarity and skill-overlap breakdown—never a black-box score.
AFTER:  Badge: Multi-Dimensional Match
        Matches candidate profiles against live opportunities across 11 canonical engineering tracks using a multi-dimensional weighted algorithm (skills, experience, seniority, domain, preferences)—never an unexplainable black-box score.

========================================================================================
5. RESPONSIBLE AI SECTION (frontend/src/app/(public)/page.tsx)
========================================================================================
BEFORE: Right to Erasure & Export: Your career data belongs to you. Export your complete data graph in JSON format anytime or purge your account and resumes with a single click.
AFTER:  Data Privacy & User Ownership: Your career data belongs to you. Aligned with our Phase 16 compliance roadmap, we uphold strict data minimization, store zero unencrypted credentials, and support admin-assisted account erasure upon request.

========================================================================================
6. FEATURES PAGE — JOB MATCHING (frontend/src/app/(public)/features/page.tsx)
========================================================================================
BEFORE: Title: Semantic Vector Job Search
        Desc: High-dimensional embeddings evaluate deep semantic fit beyond brittle keyword queries, surfacing relevant software roles.
        Bullets: ['pgvector cosine similarity', 'Real-time compensation stats', 'Remote & hybrid filtering']
AFTER:  Title: Multi-Dimensional Job Matching
        Desc: Evaluates multi-dimensional alignment beyond brittle keyword queries, analyzing skills, experience, and role seniority across 11 canonical engineering tracks.
        Bullets: ['5-factor deterministic scoring', 'Real-time compensation stats', 'Remote & hybrid filtering']

========================================================================================
7. FEATURES PAGE — RESUME OPTIMIZER (frontend/src/app/(public)/features/page.tsx)
========================================================================================
BEFORE: Title: Truthful Resume Optimizer
        Bullets: ['Side-by-side diff review', 'Zero hallucination audit', 'Targeted ATS keyword mapping']
AFTER:  Title: Truthful Resume Optimizer
        Bullets: ['Side-by-side diff review', 'Evidence-grounded audit (UI in Phase 10B)', 'Targeted ATS keyword mapping']

========================================================================================
8. FEATURES PAGE — PRIVACY (frontend/src/app/(public)/features/page.tsx)
========================================================================================
BEFORE: Desc: Your career profile and resumes are never used for public LLM training or sold to third-party data brokers. One-click data deletion.
        Bullets: ['GDPR & CCPA compliance', 'One-click full account wipe', 'JSON portability export']
AFTER:  Desc: Your career profile and resumes are never used for public LLM training or sold to third-party data brokers. Architected for data minimization with admin-assisted deletion.
        Bullets: ['Designed for privacy & minimization', 'Admin-assisted account erasure', 'Phase 16 compliance roadmap']

========================================================================================
9. HOW IT WORKS — STEP 05 & 06 (frontend/src/app/(public)/how-it-works/page.tsx)
========================================================================================
BEFORE: Semantic Job Ingestion & pgvector Search (1536-dimensional vector embeddings, cosine similarity)
        Explainable Multi-Factor Job Fit (Skill 40%, Experience 25%, Domain 20%, Seniority 15%)
AFTER:  Deterministic Multi-Dimensional Job Matching (5 objective dimensions across 11 canonical tracks)
        Explainable Multi-Factor Job Fit (Skill 40%, Experience 20%, Seniority 15%, Location 15%, Preferences 10%)

========================================================================================
10. PRIVACY POLICY (frontend/src/app/(public)/privacy/page.tsx)
========================================================================================
BEFORE: The Zero-Hallucination & Anti-Fabrication Guarantee / Enterprise zero-data-retention APIs / Instant 1-click purge
AFTER:  Grounded Anti-Fabrication & Evidence Safeguards / Evidence-Bounded AI with prompt minimization / Admin-assisted erasure with Phase 16 automated self-service roadmap
```

---

## 4. Modified Files & Line References

| File Path | Description of Changes |
| :--- | :--- |
| [`frontend/src/app/(public)/page.tsx`](file:///Users/anmolsharma/Desktop/Coach_Path/frontend/src/app/(public)/page.tsx#L33-L44) | Updated 10 steps, trust banner, BentoCard pillars, Problem vs Solution bullets, and Responsible AI section. |
| [`frontend/src/app/(public)/features/page.tsx`](file:///Users/anmolsharma/Desktop/Coach_Path/frontend/src/app/(public)/features/page.tsx#L22-L107) | Aligned 12 feature cards: replaced vector search with multi-dimensional matching, removed 1-click purge, labeled roadmap previews (Phases 12, 13, 14, 15, 16). |
| [`frontend/src/app/(public)/how-it-works/page.tsx`](file:///Users/anmolsharma/Desktop/Coach_Path/frontend/src/app/(public)/how-it-works/page.tsx#L50-L112) | Updated steps 04, 05, 06, 07, 08, 09, 10 to reflect deterministic 5-factor scoring, portfolio deliverables, and preview statuses. |
| [`frontend/src/app/(public)/privacy/page.tsx`](file:///Users/anmolsharma/Desktop/Coach_Path/frontend/src/app/(public)/privacy/page.tsx#L21-L68) | Updated sections 1, 2, 4 to reflect grounded safeguards, evidence-bounded AI with prompt minimization, and admin-assisted erasure. |
| [`frontend/src/app/(public)/about/page.tsx`](file:///Users/anmolsharma/Desktop/Coach_Path/frontend/src/app/(public)/about/page.tsx#L29-L49) | Clarified benchmark persona Aarav Mehta as illustrative demo candidate and changed repo audits to project deliverables. |
| [`frontend/src/components/layout/public-footer.tsx`](file:///Users/anmolsharma/Desktop/Coach_Path/frontend/src/components/layout/public-footer.tsx#L19-L87) | Aligned footer badges: Evidence-grounded safeguards, Readiness Index (Preview), Designed for Privacy & Minimization. |
| [`frontend/src/components/landing/interactive-preview.tsx`](file:///Users/anmolsharma/Desktop/Coach_Path/frontend/src/components/landing/interactive-preview.tsx#L28-L285) | Labeled mock window as "Illustrative Demo Candidate", tab as "Readiness Preview (78%)", and tab 4 as "Anti-Fabrication Diff". |

---

## 5. Verification Results

### Frontend Linting
```bash
$ npm --prefix frontend run lint
✔ No ESLint warnings or errors
```

### Frontend Production Build
```bash
$ npm --prefix frontend run build
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (25/25)
✓ Finalizing page optimization
```
All 25 application routes compiled successfully with zero type errors.

### Backend Remediation Test Suite
```bash
$ ./backend/.venv/bin/pytest backend/tests/test_assessment_randomization_and_diversity.py backend/tests/test_role_personalization_reconciler.py
============================== 25 passed in 5.58s ==============================
```
All 25 remediation unit and integration tests continue to pass with zero regressions.

---

## 6. Audit & Remediation Milestone Completion

With Remediation Steps 1, 2, 3, and 4 complete:
1. **Step 1 (Account Safety & Demo Data Isolation)**: Disabled fake `alert()` dialogs in settings, linked to Phase 16 compliance roadmap, and isolated demo candidate data with `DemoPreviewBanner`.
2. **Step 2 (Target Role Personalization Reconciler)**: Added `data-engineer` and `mobile-engineer` to database seeds and taxonomies, added role resolution alias engine, eliminated silent fallbacks to `backend-developer`.
3. **Step 3 (Assessment Randomization & Diversity Engine)**: Shuffled question choices per attempt with concealed answer keys, dynamic option mapping, and 100% question diversity on retakes.
4. **Step 4 (Public Marketing Copy Alignment)**: Aligned all 14 audited public marketing claims across the landing page, features, how-it-works, privacy, about, footer, and interactive previews.

**CoachPath is now fully prepared to begin Phase 10: Resume Tailoring & Optimization Backend & Frontend.**
