# Mathematical Scoring Specifications

## 1. Job Match Algorithm (Transparent 7-Factor Weighted Formula)
The overall match score $S_{\text{match}} \in [0, 100]$ is computed as the sum of 7 distinct factors:

$$S_{\text{match}} = S_{\text{skills}} + S_{\text{semantic}} + S_{\text{experience}} + S_{\text{projects}} + S_{\text{location}} + S_{\text{salary}} + S_{\text{education}}$$

| Factor | Weight | Maximum Points | Calculation Method |
|---|---|---|---|
| **Skills Fit** | 40% | 40 pts | Ratio of job required skills verified in candidate profile. Verified skills count 1.0; self-reported count 0.6. |
| **Semantic Alignment** | 15% | 15 pts | Cosine similarity between candidate profile embedding and job description embedding. |
| **Experience Level** | 15% | 15 pts | Match between candidate experience bracket (Fresher / 0-2 yrs) and role expectations. |
| **Projects Relevance** | 10% | 10 pts | Direct keyword and tech stack overlap between candidate projects and JD requirements. |
| **Location & Work Mode** | 10% | 10 pts | Alignment between preferred city (e.g., Bengaluru, Hyderabad, Remote) and job mode. |
| **Salary Alignment** | 5% | 5 pts | Evaluates whether minimum offering meets candidate's ₹ LPA expectation. |
| **Education & Preferences** | 5% | 5 pts | Degree type, graduation year, and preferred companies list match. |

---

## 2. Career Readiness Index (7-Component Weighted Formula)
The Readiness Index $R_{\text{career}} \in [0, 100]$ reflects a holistic evaluation across all candidate assets:

$$R_{\text{career}} = 0.25 \cdot T + 0.15 \cdot D + 0.15 \cdot P + 0.10 \cdot R + 0.15 \cdot I_v + 0.10 \cdot I_n + 0.10 \cdot J$$

Where:
- $T$: **Technical Skills** (25%) – Mean verified assessment score across core role skills.
- $D$: **DSA & Algorithms** (15%) – Algorithmic problem-solving assessment or progress.
- $P$: **Production Projects** (15%) – Portfolio count, complexity, and deployment status.
- $R$: **Resume ATS Alignment** (10%) – Latest ATS keyword and structure score.
- $I_v$: **Interview Prep** (15%) – Completed checklist items and mock practice answers.
- $I_n$: **Industry Relevance** (10%) – Overlap with trending technologies from market data.
- $J$: **Job Readiness Activity** (10%) – Active application funnel progress and tracker engagements.

---

## 3. "Biggest Lever" Sensitivity Analysis
To identify the single highest-impact action for the candidate, CoachPath computes the potential marginal return:

$$\Delta_{\text{impact}}(C) = W_C \cdot (100 - S_C)$$

The component maximizing $\Delta_{\text{impact}}$ is surfaced to the candidate with an exact projection (e.g., *"Raising your verified SQL assessment score from 38% to 75% increases your overall Career Readiness from 70% to 75%"*).
