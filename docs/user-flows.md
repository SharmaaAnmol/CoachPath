# User Flows Specification

> **Document Status**: Placeholder / Phase 0 Initialization  
> **Owner**: Lead Software Architect & Product Engineering  
> **Last Updated**: Phase 0 Kickoff

---

## 1. Overview
This document specifies the primary end-to-end user journeys through the CoachPath platform, detailing user interactions, system state transitions, AI interactions, and decision nodes.

## 2. Core User Flows to Detail in Phase 0

### 2.1 Onboarding & Career Profile Ingestion
- Account creation & authentication.
- Career objective definition (target roles, experience level, preferences).
- Resume upload, extraction verification, and user confirmation.

### 2.2 Skill Assessment & Evidence Gathering
- Adaptive skill assessment assignment.
- Question/project evaluation and feedback.
- Profile skill confidence calibration.

### 2.3 Skill-Gap Analysis & Roadmap Generation
- Target role requirements vs. current profile benchmark.
- Gap identification and explainable prioritization.
- Actionable, personalized roadmap generation and milestone tracking.

### 2.4 Job Matching & Market Discovery
- Ingestion of permitted job listings.
- Vector & semantic matching against user career profile.
- Match score breakdown, rationale, and missing skill callouts.

### 2.5 Truthful Resume Tailoring
- Job description selection.
- Contextual highlighting and rephrasing of authentic candidate experience.
- Strict anti-hallucination validation and user diff review.

### 2.6 Application Lifecycle & Tracker
- Job application state tracking (Saved, Applied, Interviewing, Offered, Rejected).
- Activity logging and career readiness metric recalculation.

### 2.7 Human-in-the-Loop Consequential Action Flow
- Pre-action preparation stage.
- Explicit user review and modification.
- Explicit user authorization trigger.
- Immutable audit trail recording.
