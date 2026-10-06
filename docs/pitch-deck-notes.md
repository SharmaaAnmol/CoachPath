# CoachPath: Hackathon Pitch & Judge Alignment Notes

## Key Differentiators to Emphasize to Judges

### 1. The Bharat Hackathon 2.0 Edge
- **Target Audience**: 1.5M Indian engineering undergraduates, specifically focusing on Tier-2 and Tier-3 colleges navigating campus placement seasons and off-campus drives.
- **Native Ecosystem**: Default INR ₹ LPA salary figures, Indian tech tech-hubs (Bengaluru, Hyderabad, Pune, Gurugram), and India's trusted free learning platforms (NPTEL, SWAYAM, Physics Wallah, Krish Naik, CodeWithHarry, Striver SDE Sheet).
- **Accessibility**: English + हिन्दी (Hindi/Hinglish) bilingual UI toggle, lightweight zero-bloat pages, and mobile responsiveness.

### 2. "Automate the Busywork. Never the Decision."
- Many failed AI products attempt full automation that spams recruiters and fills out false applications.
- CoachPath enforces **Human Approval Gates** on both application submission and cold recruiter outreach.
- Every approval is cryptographically logged in an immutable `audit_log` with user approval status.

### 3. Truthfulness Checker (Zero Resume Hallucination)
- LLMs often hallucinate metrics or skills on resumes.
- CoachPath uses a rigorous dual-pass verification pass: every skill, metric, employer, and degree in the tailored resume must exist in the master record.
- Unverified items are stripped and flagged; candidate is given a transparent diff view.

### 4. Mathematical Explainability
- **Job Match**: A 7-factor transparent weighted score (40% skills, 15% semantic, 15% experience, 10% projects, 10% mode, 5% salary, 5% edu) with explicit checkmark/triangle/cross indicators.
- **Biggest Lever**: Sensitivity analysis ($W \cdot (100 - S)$) showing candidates the exact mathematical action to maximize their placement readiness.

### 5. Slide 18 (Future Vision Architecture)
- Do not build Slide 18, but articulate that the unified database schema (`profiles`, `user_skills`, `audit_log`) is already architected to plug in:
  - AI Voice Mock Interviews (WebRTC + TTS)
  - GitHub Portfolio Code Analyzers
  - College Placement Cell (TPO) enterprise dashboards
  - Predictive offer salary calculators.
