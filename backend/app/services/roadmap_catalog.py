"""
Curated Milestone Task Templates & Skill Progression Library for CoachPath.
Defines deterministic task templates, official educational resources, deliverable requirements,
and prerequisite dependency graphs for all canonical role competencies.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ─── Skill Prerequisite Rules ─────────────────────────────────────────
# Maps a skill to the skills that should be studied BEFORE or concurrently with it.
SKILL_PREREQUISITES: Dict[str, List[str]] = {
    "fastapi": ["python", "rest-apis"],
    "postgresql": ["sql-databases"],
    "sql-databases": [],
    "python": [],
    "javascript": [],
    "typescript": ["javascript"],
    "javascript-typescript": [],
    "react": ["javascript", "html", "css"],
    "nextjs": ["react", "typescript"],
    "redis": ["python"],
    "docker": ["linux"],
    "kubernetes": ["docker", "linux"],
    "ci-cd": ["git", "docker"],
    "machine-learning": ["python"],
    "deep-learning": ["machine-learning", "python"],
    "pytorch": ["python", "machine-learning"],
    "ai-llm": ["python"],
    "rag": ["ai-llm", "python"],
    "system-design": ["sql-databases", "rest-apis", "docker"],
    "data-modeling": ["sql-databases"],
    "tailwind-css": ["css", "html"],
    "aws": ["linux", "docker"],
    "terraform": ["aws", "docker"],
    "security-best-practices": ["rest-apis"],
}


# ─── Curated Task Templates ───────────────────────────────────────────

CURATED_TASK_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    # ─── Python ───────────────────────────────────────────────────────
    "python": [
        {
            "level": 1,
            "title": "Master Core Async Python, Protocols & Type Annotations",
            "description": "Deep-dive into Python's data model, typing module, async/await event loops, generator coroutines, and context managers.",
            "learning_objective": "Write robust, fully type-annotated asynchronous Python code adhering to PEP 8, PEP 484, and modern idioms.",
            "task_type": "practice",
            "estimated_hours": 6,
            "resource_urls": [
                {"title": "Python Official Documentation: Data Model", "url": "https://docs.python.org/3/reference/datamodel.html", "type": "documentation"},
                {"title": "Real Python: Async IO in Python", "url": "https://realpython.com/async-io-python/", "type": "tutorial"},
            ],
            "deliverable_requirement": "GitHub repository with typed utility modules, asynchronous batch processor, and passing pytest suite.",
            "completion_criteria": "Code passes mypy --strict, flake8, and includes at least 10 unit tests achieving >90% coverage.",
        },
        {
            "level": 2,
            "title": "Build a Resilient CLI Tool with Structured Concurrency & Logging",
            "description": "Construct a production-ready command line interface using Click or Typer with structured JSON logging, exception hierarchies, and worker pools.",
            "learning_objective": "Demonstrate practical engineering craftsmanship in package structure, concurrency, and graceful error handling in Python.",
            "task_type": "project",
            "estimated_hours": 8,
            "resource_urls": [
                {"title": "Typer Official Documentation", "url": "https://typer.tiangolo.com/", "type": "documentation"},
                {"title": "Python Logging Cookbook", "url": "https://docs.python.org/3/howto/logging-cookbook.html", "type": "documentation"},
            ],
            "deliverable_requirement": "Published GitHub repository with pyproject.toml, CLI entry point, and automated test suite.",
            "completion_criteria": "CLI executes multiple parallel API queries with retry backoff, outputs structured logs, and passes all edge-case tests.",
        },
    ],

    # ─── FastAPI ──────────────────────────────────────────────────────
    "fastapi": [
        {
            "level": 2,
            "title": "Implement Async RESTful Microservice with FastAPI & Dependency Injection",
            "description": "Design and build an asynchronous CRUD microservice with Pydantic v2 schemas, hierarchical dependency injection, and middleware.",
            "learning_objective": "Master FastAPI routing, request validation, exception handling, and dependency injection patterns.",
            "task_type": "project",
            "estimated_hours": 8,
            "resource_urls": [
                {"title": "FastAPI Official Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "documentation"},
                {"title": "Pydantic v2 Documentation", "url": "https://docs.pydantic.dev/latest/", "type": "documentation"},
            ],
            "deliverable_requirement": "FastAPI service repo with OpenAPI schema, authentication middleware, and unit tests using AsyncClient.",
            "completion_criteria": "Endpoints validate incoming payloads with HTTP 422 for bad data, authenticate requests via Bearer JWT, and pass integration tests.",
        },
        {
            "level": 3,
            "title": "Production FastAPI Optimization: Background Tasks, Rate Limiting & Health Probes",
            "description": "Harden a FastAPI backend with Redis token-bucket rate limiting, background worker tasks, and Kubernetes-ready readiness/liveness probes.",
            "learning_objective": "Architect high-performance, fault-tolerant FastAPI applications ready for production workloads.",
            "task_type": "project",
            "estimated_hours": 10,
            "resource_urls": [
                {"title": "FastAPI Deployment Guide", "url": "https://fastapi.tiangolo.com/deployment/", "type": "documentation"},
                {"title": "Starlette Middleware Documentation", "url": "https://www.starlette.io/middleware/", "type": "documentation"},
            ],
            "deliverable_requirement": "GitHub repo with rate-limiting middleware, background worker queue, and Docker healthcheck endpoint.",
            "completion_criteria": "Load tested with Locust or wrk; verifies 429 Too Many Requests when rate threshold exceeded.",
        },
    ],

    # ─── SQL Databases & PostgreSQL ────────────────────────────────────
    "sql-databases": [
        {
            "level": 1,
            "title": "Relational Data Modeling & Complex Query Mastery",
            "description": "Learn relational normal forms (1NF-3NF), multi-table joins, subqueries, CTEs (WITH clauses), and window functions.",
            "learning_objective": "Write optimized SQL queries extracting multi-dimensional analytics from normalized schemas.",
            "task_type": "practice",
            "estimated_hours": 6,
            "resource_urls": [
                {"title": "PostgreSQL Window Functions Tutorial", "url": "https://www.postgresql.org/docs/current/tutorial-window.html", "type": "documentation"},
                {"title": "Use The Index, Luke!", "url": "https://use-the-index-luke.com/", "type": "reading"},
            ],
            "deliverable_requirement": "SQL script file containing schema definition, sample data seed, and 10 analytical queries using CTEs and window functions.",
            "completion_criteria": "All queries execute cleanly, correctly calculate moving averages, running totals, and partition rankings.",
        },
    ],
    "postgresql": [
        {
            "level": 2,
            "title": "PostgreSQL Performance Tuning: Indexes, EXPLAIN ANALYZE & Connection Pooling",
            "description": "Audit real query performance using EXPLAIN (ANALYZE, BUFFERS), design compound B-tree and GIN indexes, and configure asyncpg pooling.",
            "learning_objective": "Diagnose query bottlenecks, prevent full table scans, and manage high-concurrency database connection pools.",
            "task_type": "project",
            "estimated_hours": 8,
            "resource_urls": [
                {"title": "PostgreSQL Performance Optimization", "url": "https://wiki.postgresql.org/wiki/Performance_Optimization", "type": "documentation"},
                {"title": "AsyncPG Connection Pool Guide", "url": "https://magicstack.github.io/asyncpg/current/usage.html#connection-pools", "type": "documentation"},
            ],
            "deliverable_requirement": "Markdown performance audit report comparing query execution plans before and after indexing with reproducible SQL scripts.",
            "completion_criteria": "Demonstrated >5x query plan execution time reduction on dataset >100,000 rows.",
        },
    ],

    # ─── Redis ────────────────────────────────────────────────────────
    "redis": [
        {
            "level": 2,
            "title": "Distributed Caching & Session Management with Redis",
            "description": "Integrate Redis as a cache-aside layer and distributed session store with TTL policies, serialization, and invalidation strategies.",
            "learning_objective": "Implement sub-millisecond response caching while avoiding cache stampedes and stale data reads.",
            "task_type": "project",
            "estimated_hours": 6,
            "resource_urls": [
                {"title": "Redis Cache-Aside Pattern", "url": "https://redis.io/docs/manual/patterns/", "type": "documentation"},
            ],
            "deliverable_requirement": "Service implementation with Redis cache decorators, probabilistic early expiration, and docker-compose.yml.",
            "completion_criteria": "Integration test verifies cache hit returns data without hitting the primary database; cache invalidation works on write mutations.",
        },
    ],

    # ─── Docker ───────────────────────────────────────────────────────
    "docker": [
        {
            "level": 2,
            "title": "Containerize Full-Stack Services with Multi-Stage Dockerfiles",
            "description": "Construct minimal, secure multi-stage Docker images running non-root containers with Alpine or distroless base images.",
            "learning_objective": "Package applications into production-ready containers with minimal attack surface and sub-100MB footprint.",
            "task_type": "project",
            "estimated_hours": 6,
            "resource_urls": [
                {"title": "Docker Best Practices for Production", "url": "https://docs.docker.com/develop/develop-images/dockerfile_best-practices/", "type": "documentation"},
            ],
            "deliverable_requirement": "Dockerfile using multi-stage build, docker-compose.yml orchestrating API + PostgreSQL + Redis with healthchecks.",
            "completion_criteria": "docker-compose up -d starts all services with healthy status; final API container image size < 150MB.",
        },
    ],

    # ─── Kubernetes ───────────────────────────────────────────────────
    "kubernetes": [
        {
            "level": 2,
            "title": "Kubernetes Deployment, StatefulSets, Ingress & Secrets Configuration",
            "description": "Deploy a containerized microservice onto local Kubernetes (k3d/minikube) with rolling updates, ConfigMaps, and resource quotas.",
            "learning_objective": "Manage declarative Kubernetes manifests, horizontal pod autoscalers, and zero-downtime rolling deployments.",
            "task_type": "project",
            "estimated_hours": 10,
            "resource_urls": [
                {"title": "Kubernetes Official Tutorials", "url": "https://kubernetes.io/docs/tutorials/", "type": "documentation"},
            ],
            "deliverable_requirement": "Directory of k8s manifests (Deployment, Service, Ingress, HPA, ConfigMap) with deployment shell script.",
            "completion_criteria": "Pods scale automatically under load simulation; rolling deployment executes without dropped HTTP connections.",
        },
    ],

    # ─── CI/CD & Git ──────────────────────────────────────────────────
    "git": [
        {
            "level": 1,
            "title": "Professional Git Workflow: Rebase, Branching Strategies & Conventional Commits",
            "description": "Master interactive rebase, cherry-picking, stash workflows, and Git branching models (GitHub Flow / Trunk-Based).",
            "learning_objective": "Maintain clean, linear Git history with semantic conventional commits and resolved merge conflicts.",
            "task_type": "practice",
            "estimated_hours": 4,
            "resource_urls": [
                {"title": "Pro Git Book", "url": "https://git-scm.com/book/en/v2", "type": "book"},
            ],
            "deliverable_requirement": "GitHub repository featuring feature branches, pull requests with peer reviews, and interactive rebase history.",
            "completion_criteria": "Git log displays clean atomic commits adhering to 'feat:', 'fix:', 'test:' conventions without merge bubbles.",
        },
    ],
    "ci-cd": [
        {
            "level": 2,
            "title": "Build Automated GitHub Actions CI/CD Pipeline with Security Scanning",
            "description": "Construct an automated workflow that runs linters, unit tests, Docker container builds, and security scanning (Trivy) on PRs.",
            "learning_objective": "Automate continuous integration, test gatekeeping, and automated container image publishing.",
            "task_type": "project",
            "estimated_hours": 6,
            "resource_urls": [
                {"title": "GitHub Actions Documentation", "url": "https://docs.github.com/en/actions", "type": "documentation"},
            ],
            "deliverable_requirement": ".github/workflows/ci.yml configuration file with branch protection rules and automated test summary output.",
            "completion_criteria": "Pipeline automatically triggers on pull requests, blocks merge on test failure, and outputs test coverage badges.",
        },
    ],

    # ─── React & Frontend ─────────────────────────────────────────────
    "javascript": [
        {
            "level": 1,
            "title": "Modern JavaScript ES2024: Closures, Event Loop, Promises & Prototypes",
            "description": "Deepen mastery of JavaScript asynchronous runtime, microtask queues, scoping closures, and functional methods.",
            "learning_objective": "Write clean, bug-free modern JavaScript with thorough understanding of event loop mechanics.",
            "task_type": "practice",
            "estimated_hours": 6,
            "resource_urls": [
                {"title": "JavaScript.info Modern Tutorial", "url": "https://javascript.info/", "type": "tutorial"},
            ],
            "deliverable_requirement": "Repository of JavaScript utility implementations (debounce, throttle, deepClone, promiseAll) with Jest unit tests.",
            "completion_criteria": "All custom asynchronous utilities pass concurrency and timing edge-case tests with 100% test coverage.",
        },
    ],
    "typescript": [
        {
            "level": 2,
            "title": "Advanced TypeScript: Generics, Conditional Types & Mapped Types",
            "description": "Implement robust type-safe libraries using conditional types, template literal types, Discriminated Unions, and infer keyword.",
            "learning_objective": "Construct bulletproof type systems eliminating any runtime type errors in complex frontend applications.",
            "task_type": "practice",
            "estimated_hours": 6,
            "resource_urls": [
                {"title": "TypeScript Handbook: Advanced Types", "url": "https://www.typescriptlang.org/docs/handbook/2/types-from-types.html", "type": "documentation"},
            ],
            "deliverable_requirement": "TypeScript project demonstrating type-safe state machine or generic API client with zero 'any' casts.",
            "completion_criteria": "Compiler runs in strict mode (noImplicitAny, strictNullChecks); all types infer accurately across generic boundaries.",
        },
    ],
    "react": [
        {
            "level": 2,
            "title": "Build Interactive Component System with Custom Hooks & State Management",
            "description": "Architect a modular UI library with React hooks (useMemo, useCallback, useReducer), context providers, and optimistic updates.",
            "learning_objective": "Design scalable, high-performance React component trees with clean separation of presentation and state.",
            "task_type": "project",
            "estimated_hours": 8,
            "resource_urls": [
                {"title": "React.dev Official Documentation", "url": "https://react.dev/", "type": "documentation"},
            ],
            "deliverable_requirement": "Interactive web app or component library with custom hooks for data fetching, pagination, and accessibility (a11y).",
            "completion_criteria": "Zero unnecessary re-renders; passes React Testing Library suite; accessibility score > 95 on Lighthouse.",
        },
    ],
    "nextjs": [
        {
            "level": 2,
            "title": "Next.js App Router: Server Components, Server Actions & Streaming SSR",
            "description": "Build a modern full-stack web application using React Server Components, Suspense streaming, and Server Actions for mutations.",
            "learning_objective": "Master server-side rendering, client boundary isolation, and edge-rendered performance in Next.js.",
            "task_type": "project",
            "estimated_hours": 10,
            "resource_urls": [
                {"title": "Next.js App Router Documentation", "url": "https://nextjs.org/docs/app", "type": "documentation"},
            ],
            "deliverable_requirement": "Full-stack Next.js web application deployed on Vercel with dynamic routing, loading skeletons, and server actions.",
            "completion_criteria": "Initial server response renders instant HTML skeleton; mutations update UI optimistically; core web vitals green.",
        },
    ],

    # ─── Machine Learning & AI ────────────────────────────────────────
    "machine-learning": [
        {
            "level": 2,
            "title": "End-to-End Scikit-Learn Pipeline: Feature Engineering & Model Evaluation",
            "description": "Build reproducible machine learning pipelines featuring cross-validation, imputation, categorical encoding, and ROC-AUC / F1 analysis.",
            "learning_objective": "Implement mathematically sound feature pre-processing, hyperparameter search, and leak-free validation splits.",
            "task_type": "project",
            "estimated_hours": 8,
            "resource_urls": [
                {"title": "Scikit-Learn User Guide", "url": "https://scikit-learn.org/stable/user_guide.html", "type": "documentation"},
            ],
            "deliverable_requirement": "Jupyter Notebook or Python package with ColumnTransformer, Pipeline, and cross-validated benchmark comparisons.",
            "completion_criteria": "Pipeline prevents target leakage; demonstrates baseline vs tuned model metrics; produces confusion matrix visualizations.",
        },
    ],
    "deep-learning": [
        {
            "level": 2,
            "title": "Deep Neural Network Architecture: Backpropagation, Regularization & PyTorch",
            "description": "Construct neural network architectures from scratch and in PyTorch, exploring custom loss functions, learning rate schedules, and dropout.",
            "learning_objective": "Understand gradient flow, vanishing gradients, optimizer dynamics (AdamW), and tensor operations.",
            "task_type": "project",
            "estimated_hours": 10,
            "resource_urls": [
                {"title": "PyTorch Official Tutorials", "url": "https://pytorch.org/tutorials/", "type": "documentation"},
                {"title": "Deep Learning with PyTorch Book", "url": "https://pytorch.org/deep-learning-with-pytorch", "type": "book"},
            ],
            "deliverable_requirement": "PyTorch training module with validation loop, TensorBoard/W&B metric logging, and model checkpointing.",
            "completion_criteria": "Training demonstrates convergence without catastrophic overfitting; test accuracy beats standard baseline by >15%.",
        },
    ],
    "ai-llm": [
        {
            "level": 2,
            "title": "LLM Integration: Structured JSON Outputs, Prompt Engineering & Guardrails",
            "description": "Build an LLM client wrapper enforcing strict Pydantic schema validation, prompt injection defense, and retry handling.",
            "learning_objective": "Harden production LLM workflows against hallucination, format drift, and prompt injection vulnerabilities.",
            "task_type": "project",
            "estimated_hours": 8,
            "resource_urls": [
                {"title": "Google Gemini API Guide", "url": "https://ai.google.dev/docs", "type": "documentation"},
                {"title": "OWASP Top 10 for Large Language Model Applications", "url": "https://owasp.org/www-project-top-10-for-large-language-model-applications/", "type": "reading"},
            ],
            "deliverable_requirement": "Python module with schema-validated LLM generator, token tracking, and quarantine delimiters for untrusted input.",
            "completion_criteria": "Returns 100% valid Pydantic models across 50 test inputs; gracefully handles API rate limits with exponential backoff.",
        },
    ],
    "rag": [
        {
            "level": 3,
            "title": "Build Production Retrieval-Augmented Generation (RAG) with Vector Search",
            "description": "Construct a document Q&A engine with document chunking strategies, dense embeddings, vector indexing, and hybrid BM25 + vector reranking.",
            "learning_objective": "Implement production-grade semantic retrieval pipelines with contextual citation and hallucination checks.",
            "task_type": "project",
            "estimated_hours": 12,
            "resource_urls": [
                {"title": "Pinecone / Chroma Vector Search Guide", "url": "https://docs.trychroma.com/", "type": "documentation"},
                {"title": "LangChain / LlamaIndex Architecture", "url": "https://docs.llamaindex.ai/", "type": "documentation"},
            ],
            "deliverable_requirement": "Full RAG system with document ingestion pipeline, embedding store, retrieval engine, and evaluation benchmark.",
            "completion_criteria": "Answers include exact source page citations; evaluation shows >80% factual precision against Ground Truth test questions.",
        },
    ],

    # ─── System Design & DSA ──────────────────────────────────────────
    "dsa": [
        {
            "level": 2,
            "title": "Data Structures & Algorithmic Problem Solving Mastery",
            "description": "Solve and analyze intermediate algorithmic patterns: two pointers, sliding window, binary search, tree traversals, and graphs (BFS/DFS).",
            "learning_objective": "Analyze Big-O time and space complexity with precision and solve complex technical interview problems systematically.",
            "task_type": "practice",
            "estimated_hours": 8,
            "resource_urls": [
                {"title": "NeetCode Algorithmic Roadmap", "url": "https://neetcode.io/roadmap", "type": "tutorial"},
            ],
            "deliverable_requirement": "Documented solution repository containing at least 15 verified solutions across graphs, dynamic programming, and heaps.",
            "completion_criteria": "All solutions achieve optimal Big-O complexity; code includes unit test assertions verifying edge cases (empty inputs, large values).",
        },
    ],
    "system-design": [
        {
            "level": 3,
            "title": "High-Level Distributed System Design: Scaling to 10M DAU",
            "description": "Architect a distributed URL shortener or social media feed: database sharding, CAP theorem trade-offs, CDN caching, and message queues.",
            "learning_objective": "Design resilient, scalable distributed backends addressing single points of failure, latency, and data consistency.",
            "task_type": "project",
            "estimated_hours": 10,
            "resource_urls": [
                {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "type": "reading"},
            ],
            "deliverable_requirement": "Comprehensive architectural design document (Mermaid diagrams, capacity estimations, API contracts, failure modes analysis).",
            "completion_criteria": "Calculates queries per second (QPS), bandwidth, storage requirements; specifies failover strategies for database and cache outages.",
        },
    ],

    # ─── Security Best Practices ──────────────────────────────────────
    "security-best-practices": [
        {
            "level": 2,
            "title": "Web Application Security Audit: OWASP Top 10 Mitigation",
            "description": "Audit and protect APIs against SQL injection, XSS, CSRF, broken access controls, and insecure deserialization.",
            "learning_objective": "Implement defense-in-depth security principles across authentication, input sanitization, and HTTP security headers.",
            "task_type": "practice",
            "estimated_hours": 6,
            "resource_urls": [
                {"title": "OWASP API Security Top 10", "url": "https://owasp.org/www-project-api-security/", "type": "documentation"},
            ],
            "deliverable_requirement": "Security audit report and automated pytest suite testing authorization boundaries, payload tampering, and injection safety.",
            "completion_criteria": "Service scores A+ on Mozilla Observatory; unauthorized tenant data access attempts return 403 Forbidden.",
        },
    ],
}


def get_task_templates_for_skill(skill_id: str, current_level: int, target_level: int) -> List[Dict[str, Any]]:
    """
    Returns curated task templates appropriate for advancing a skill from current_level to target_level.
    If no explicit template is found, generates a deterministic structured template.
    """
    templates = CURATED_TASK_TEMPLATES.get(skill_id, [])
    matching = [t for t in templates if current_level < t["level"] <= target_level]

    if matching:
        return matching

    # Fallback to general template matching level or synthesized
    if templates:
        return [templates[0]]

    # Synthesize fallback task
    human_name = skill_id.replace("-", " ").title()
    return [
        {
            "level": max(1, current_level + 1),
            "title": f"Master Core Competencies in {human_name}",
            "description": f"Study foundational and applied principles of {human_name}. Implement hands-on exercises and build practical proof-of-concept projects.",
            "learning_objective": f"Attain verifiable Level {target_level} competence in {human_name} for target role requirements.",
            "task_type": "project" if target_level >= 2 else "practice",
            "estimated_hours": 8 if target_level >= 2 else 5,
            "resource_urls": [
                {"title": f"{human_name} Official Guide & Documentation", "url": f"https://devdocs.io/{skill_id.split('-')[0]}", "type": "documentation"}
            ],
            "deliverable_requirement": f"GitHub repository with documented {human_name} code implementation and test coverage.",
            "completion_criteria": "Code executes cleanly, demonstrates target competency, and passes peer review / automated test suite.",
        }
    ]
