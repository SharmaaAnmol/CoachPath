# AI Architecture & Intelligence Pipeline

> **Document Status**: Placeholder / Phase 0 Initialization  
> **Owner**: Lead Software Architect & AI Engineering  
> **Last Updated**: Phase 0 Kickoff

---

## 1. AI System Overview
The AI subsystem in CoachPath powers evidence-based skill evaluation, transparent gap analysis, semantic job matching, explainable career roadmaps, and truthful resume tailoring.

## 2. Core Pillars of the AI Architecture

### 2.1 Central Continuous Profile Loop
- Architecture for ingesting signals (assessments, course completions, new projects, application outcomes).
- Dynamic re-computation of skill confidence scores and readiness indicators.

### 2.2 Structured Output Enforcement & Guardrails
- Strict schema adherence using Instructor / Pydantic with LLM function calling / json_schema mode.
- Complete ban on speculative generation or hallucination of user experience, credentials, and achievements.
- Grounded resume tailoring: Only restructure, polish, and emphasize factual user background against target requirements.

### 2.3 RAG & Embedding Architecture
- Embedding generation for job listings, taxonomy skills, and user profile segments.
- pgvector-based retrieval for semantic search and hybrid keyword-vector matching.
- Chunking strategies for lengthy resumes and detailed job descriptions.

### 2.4 Explainability & Confidence Scoring
- Generation of human-interpretable rationale for match scores and skill gaps.
- Confidence intervals for extracted skills and assessments.

### 2.5 Provider Abstraction & Model Routing
- Loose coupling from specific LLM vendors (OpenAI, Anthropic, Gemini, local models).
- Cost and latency optimization: routing simple classification/extraction to fast models and complex evaluation/reasoning to frontier models.

### 2.6 Human-in-the-Loop Gateway
- Interceptor pattern for any automated or consequential recommendations.
- Mandatory approval envelope before committing external actions or major profile modifications.
