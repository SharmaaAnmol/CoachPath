# CoachPath — Intelligent Job Matching Engine Architecture (Phase 9A)

## 1. Executive Overview

The CoachPath Job Matching Engine connects a candidate's verified career profile and objective diagnostic assessment evidence to actual persisted job listings. 

Unlike conventional ATS systems that perform simplistic keyword counting, or opaque LLM wrappers that produce shifting numerical percentages, CoachPath implements a **deterministic, versioned, transparent, and explainable multi-factor calibration engine**.

```
Candidate Career Profile               Persisted Job Opportunity
  ├── Target Career Role                 ├── Canonical Benchmark Role
  ├── Verified Skill Evidence            ├── Mandatory / Preferred Skills
  │     (Diagnostic Assessments)         ├── Seniority / Experience Level
  │     (Approved Resume Extractions)    ├── Workplace Modality (Remote/Hybrid/Onsite)
  │     (Self-Reported Baseline)         ├── Target Metropolitan Market
  ├── Technical Projects & Artifacts     └── Freshness Lifecycle ('active', 'needs_refresh')
  ├── Cumulative Verified Experience
  └── Workplace & Location Preferences
                     │                                   │
                     └─────────────────┬─────────────────┘
                                       │
                      ┌────────────────▼────────────────┐
                      │    JobMatchingEngine (v1.0)     │
                      │  ─────────────────────────────  │
                      │  1. Skill Alignment (50%)       │
                      │  2. Experience Fit (15%)        │
                      │  3. Project Relevance (15%)     │
                      │  4. Workplace/Location (10%)    │
                      │  5. Role & Preference (10%)     │
                      └────────────────┬────────────────┘
                                       │
                      ┌────────────────▼────────────────┐
                      │       Authoritative Output      │
                      │  ─────────────────────────────  │
                      │  • Composite Score (0-100)      │
                      │  • Evidence Coverage (0-100)    │
                      │  • Provisional Flag (< 40%)     │
                      │  • Skills Classification Matrix │
                      │  • Grounded Strengths & Gaps    │
                      │  • Actionable Next Steps        │
                      └─────────────────────────────────┘
```

---

## 2. Evidence Provenance & Calibration Hierarchy

CoachPath treats data sources according to a strict evidentiary hierarchy. No self-reported claim is granted parity with an independently verified assessment or code artifact:

| Evidence Tier | Source | Multiplier | Verification Rule |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Highest)** | Diagnostic Assessment | **1.00** | Score $\ge 70.0\%$ on objective diagnostic assessment attempt (`AssessmentAttempt.passed == True`). |
| **Tier 2** | Project Evidence | **0.85** | Hands-on project artifacts in candidate portfolio containing verifiable GitHub or live production URLs. |
| **Tier 3** | Approved Resume | **0.80** | Extracted from uploaded document and explicitly approved by candidate during review (`UserSkill.primary_source == 'extracted'`). Drafts are excluded. |
| **Tier 4 (Lowest)** | Self-Reported | **0.60** | Claimed in profile without objective verification (`UserSkill.primary_source == 'self_reported'`). |

### Anti-Fabrication Safeguards
1. **Unapproved Resume Drafts Excluded**: Intermediate extractions in unapproved resumes (`Resume.status == 'needs_review'`) are strictly excluded until confirmed by the user.
2. **Distinct Technology Boundaries**: Competency in one technology does not imply proficiency in another (e.g., scoring $95\%$ in Python does not grant Java credit).
3. **Synergistic Skill Cross-Validation**: Canonical ontological parent skills validate recognized subsets (e.g., completing the `sql-databases` diagnostic validates `sql` and `postgresql` competencies).

---

## 3. Canonical Skill Matching & Classification

For each requirement in `job.skills` (`JobSkill`), the engine resolves canonical taxonomy IDs (`Skill.id`) and aliases via `normalize_skill_name()`.

Each requirement is evaluated and assigned one of five standard classifications:

1. **`MATCHED`**: Candidate demonstrates verified proficiency ($\ge 70\%$ calibrated alignment).
2. **`PARTIALLY_MATCHED`**: Candidate demonstrates developing competency ($40\% - 69\%$ calibrated alignment).
3. **`MISSING`**: Mandatory requirement with zero supporting evidence in candidate profile.
4. **`UNKNOWN`**: Preferred requirement with unrecorded evidence.
5. **`INSUFFICIENT_EVIDENCE`**: Unverified self-reported claim with low calibrated confidence score.

### Required vs. Preferred Weighting
- **Mandatory Requirements ($R$)**: Carry **$80\%$** of the overall skill alignment dimension.
- **Preferred Requirements ($P$)**: Carry **$20\%$** of the overall skill alignment dimension.

$$\text{SkillScore} = \left( 0.80 \times \frac{\sum_{r \in R} S_r}{|R|} + 0.20 \times \frac{\sum_{p \in P} S_p}{|P|} \right) \times 100$$

If a posting contains only required skills or only preferred skills, the dimension normalizes over $100\%$ of the present set.

---

## 4. Multi-Dimensional Scoring Formula

The matching engine calculates alignment across 5 independent dimensions:

| Dimension | Default Weight ($W_i$) | Evaluated Factors |
| :--- | :--- | :--- |
| **Skill Alignment** | **50%** ($0.50$) | Required vs preferred canonical skills, assessment scores, user skills. |
| **Relevant Experience** | **15%** ($0.15$) | Cumulative verified years of experience vs job seniority level (`internship`, `entry_level`, `junior`, `mid`, `senior`). |
| **Project Relevance** | **15%** ($0.15$) | Tech stack overlap across portfolio projects, GitHub repository verification bonus ($+15\%$). |
| **Location & Workplace** | **10%** ($0.10$) | Workplace modality compatibility (`remote`, `hybrid`, `onsite`) and target metropolitan market match. |
| **Career & Preferences** | **10%** ($0.10$) | Primary/secondary benchmark role alignment, employment modality (`full_time`, etc.). |

### Experience Fit Rules
- Years $\ge$ minimum expected: **$100.0\%$**
- Years within 1 year below minimum: **$75.0\%$**
- Years 2+ below minimum: **$45.0\%$**
- 0 years experience on `entry_level` or `internship`: **$100.0\%$**
- 0 years experience on `mid` or `senior`: **$25.0\%$**

### Workplace Compatibility Rules
- **Remote Job**:
  - Candidate preference `remote` or `flexible`: **$100.0\%$**
  - Candidate preference `hybrid`: **$95.0\%$**
  - Candidate preference `onsite`: **$75.0\%$**
- **Hybrid / Onsite Job**:
  - Candidate preference `remote`: **$25.0\%$** (Strict workplace conflict penalty)
  - Candidate preference `hybrid` / `onsite` / `flexible`:
    - Target city matches job location: **$100.0\%$**
    - Target locations unspecified (open): **$80.0\%$**
    - Target locations specified but do not match: **$40.0\%$**

---

## 5. Missing Data Policy & Factor Normalization

When a job listing or candidate profile lacks information for a specific dimension (e.g., job lists no experience requirement or candidate has no projects because they have extensive employment history):

1. The factor is classified as **`unevaluated`**.
2. The factor is **normalized out** of the denominator:

$$\text{OverallScore} = \text{round}\left( \frac{\sum_{e \in E} W_e \times Score_e}{\sum_{e \in E} W_e}, 1 \right)$$

where $E$ represents the set of successfully evaluated factors.

This ensures:
- Candidates are not falsely penalized with $0.0\%$ for unstated job criteria.
- Missing data does not artificially produce inflated $100\%$ scores.
- Overall score remains strictly within $[0.0, 100.0]$.

---

## 6. Evidence Coverage & Match Confidence

Independent of the match score, the engine computes **Evidence Coverage** ($0.0 - 100.0$) measuring the completeness of underlying evaluation data:

1. **Job Requirement Clarity ($25\%$ max)**: Quantity of structured job skills extracted ($\ge 5$ skills = $25$ pts, $3-4$ skills = $20$ pts).
2. **Assessment Verification ($30\%$ max)**: Quantity of completed diagnostic assessments ($\ge 3$ assessments = $30$ pts, $1-2$ = $20$ pts).
3. **Experience Completeness ($15\%$ max)**: Presence of explicit job level and candidate experience history.
4. **Project Artifacts ($15\%$ max)**: Presence of technical project repositories in candidate portfolio.
5. **Preference Completeness ($15\%$ max)**: Presence of documented role and workplace preferences.

### Provisional Match Flag
If $\text{EvidenceCoverage} < 40.0$, the result is flagged with `is_provisional = True`. This alerts candidates and advisors that the numerical score is provisional until further diagnostic assessments or profile details are recorded.

---

## 7. Deterministic Grounded Explainability

Every match response generates a structured explanation grounded in evaluated facts:

- **`strengths`**: Positive factors (e.g., `"Verified high proficiency in Python (95%) via diagnostic assessment."`, `"Matches 4 required skills: Python, PostgreSQL, FastAPI, Docker."`).
- **`gaps`**: Objective missing areas (e.g., `"Missing 1 required skill: Redis."`, `"Listing requires onsite presence in Seattle, which conflicts with your remote preference."`).
- **`recommended_actions`**: Actionable guidance to bridge gaps (e.g., `"Take the Redis Diagnostic Assessment to prove competency."`, `"Add technical projects demonstrating FastAPI experience."`).
- **`summary`**: Coherent 2-3 sentence overview describing overall fit and next steps.

---

## 8. Persistence, Staleness & Invalidation

Match computations are cached in the PostgreSQL `job_matches` table:
- Unique constraint on `(career_profile_id, job_id)`.
- Version identifier `scoring_version = 'v1.0'`.
- Staleness flag `is_stale: bool`:
  - Set to `True` when the candidate's profile, assessment attempts, or user skills are updated.
  - Automatically reset to `False` upon on-demand recalculation (`POST /jobs/{id}/match/recalculate`) or batch refresh (`POST /jobs/matches/refresh`).

---

## 9. API Specifications

All endpoints require active user authentication and enforce multi-tenant isolation.

### 9.1 Personalized Recommendations
- **`GET /api/v1/jobs/recommendations`**
- **Query Parameters**:
  - `min_score`: Filter by minimum match score ($0 - 100$).
  - `role_id`: Filter by canonical role.
  - `remote_type`: Filter by `remote`, `hybrid`, or `onsite`.
  - `include_provisional`: Include/exclude matches with coverage $< 40\%$.
  - `page`, `page_size`: Standard pagination.
- **Response**: `JobRecommendationResponse` (ranked descending by `overall_score`).

### 9.2 Single Job Match
- **`GET /api/v1/jobs/{job_id}/match`**
- **Response**: `JobMatchResponse` with detailed requirement-by-requirement `skills_detail`.

### 9.3 Match Explainability Drawer
- **`GET /api/v1/jobs/{job_id}/match-explanation`**
- Conforms to `docs/api-specification.md` Section 8.2: returns `overall_score`, `evidence_coverage`, component `breakdown`, `matched_skills`, `missing_skills`, and `hiring_rationale`.

### 9.4 Recalculate Single Match
- **`POST /api/v1/jobs/{job_id}/match/recalculate`**
- Forces recalculation with latest assessment evidence and updates `job_matches`.

### 9.5 Batch Refresh
- **`POST /api/v1/jobs/matches/refresh`**
- Flags existing matches stale and recalculates scores across active catalog listings.

### 9.6 List Evaluated Matches
- **`GET /api/v1/jobs/matches`**
- Lists previously computed matches for current user ordered by score descending.

---

## 10. Database Schema Extensions (Migration `a2b3c4d5e6f7`)

The `job_matches` table was enriched with the following columns:

```sql
ALTER TABLE job_matches
  ADD COLUMN project_score NUMERIC(4, 1) DEFAULT 0.0 NOT NULL,
  ADD COLUMN location_score NUMERIC(4, 1) DEFAULT 0.0 NOT NULL,
  ADD COLUMN preference_score NUMERIC(4, 1) DEFAULT 0.0 NOT NULL,
  ADD COLUMN evidence_coverage NUMERIC(4, 1) DEFAULT 0.0 NOT NULL,
  ADD COLUMN scoring_version VARCHAR(32) DEFAULT 'v1.0' NOT NULL,
  ADD COLUMN is_stale BOOLEAN DEFAULT FALSE NOT NULL,
  ADD COLUMN matched_preferred_skills VARCHAR(64)[] DEFAULT '{}' NOT NULL,
  ADD COLUMN unknown_skills VARCHAR(64)[] DEFAULT '{}' NOT NULL;

CREATE INDEX job_matches_is_stale_idx ON job_matches (is_stale);
```
