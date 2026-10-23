"""
Canonical Skill Taxonomy for CoachPath.
Defines standardized master technical skills, categories, descriptions,
and alias dictionaries for deterministic evidence normalization.
"""

from __future__ import annotations

from typing import Any, Dict, List

SKILL_TAXONOMY: List[Dict[str, Any]] = [
    # ─── Programming Languages ──────────────────────────────────────────
    {
        "id": "python",
        "name": "Python",
        "category": "language",
        "description": "Python programming language, syntax, OOP, dunder protocols, concurrency, and memory management.",
        "synonyms": ["python3", "py", "cpython"],
    },
    {
        "id": "javascript",
        "name": "JavaScript",
        "category": "language",
        "description": "ECMAScript specification, asynchronous event loop, prototype inheritance, and DOM/browser runtime.",
        "synonyms": ["js", "es6", "ecmascript"],
    },
    {
        "id": "typescript",
        "name": "TypeScript",
        "category": "language",
        "description": "Statically typed JavaScript superset, type inference, generics, mapped types, and TS compiler.",
        "synonyms": ["ts"],
    },
    {
        "id": "javascript-typescript",
        "name": "JavaScript & TypeScript",
        "category": "language",
        "description": "Combined frontend and backend ECMAScript & TypeScript language ecosystem.",
        "synonyms": ["js/ts", "javascript/typescript"],
    },
    {
        "id": "java",
        "name": "Java",
        "category": "language",
        "description": "Java enterprise platform, JVM architecture, memory model, multithreading, collections, and streams.",
        "synonyms": ["java8", "java11", "java17", "java21", "jvm"],
    },
    {
        "id": "c-cpp",
        "name": "C & C++",
        "category": "language",
        "description": "Low-level systems programming in C and C++, pointer arithmetic, dynamic memory, RAII, and templates.",
        "synonyms": ["c", "c++", "cpp", "c/c++"],
    },
    {
        "id": "go",
        "name": "Go (Golang)",
        "category": "language",
        "description": "Go programming language, goroutines, channels, interfaces, and concurrent systems programming.",
        "synonyms": ["golang"],
    },
    {
        "id": "sql",
        "name": "SQL",
        "category": "language",
        "description": "Structured Query Language, relational algebra, DDL, DML, window functions, and indexing.",
        "synonyms": ["structured query language", "ansi sql"],
    },
    {
        "id": "bash",
        "name": "Bash & Shell Scripting",
        "category": "tool",
        "description": "POSIX shell scripting, standard streams, pipe chains, text processing (grep/sed/awk), and automation.",
        "synonyms": ["sh", "shell", "zsh", "bash script"],
    },
    {
        "id": "html",
        "name": "HTML5",
        "category": "language",
        "description": "Semantic HTML, document structure, accessibility standards (ARIA), and DOM tree APIs.",
        "synonyms": ["html", "html5"],
    },
    {
        "id": "css",
        "name": "CSS3",
        "category": "language",
        "description": "Cascading style sheets, flexbox, CSS grid, responsive media queries, animations, and typography.",
        "synonyms": ["css", "css3", "styles"],
    },

    # ─── Frameworks & Libraries ─────────────────────────────────────────
    {
        "id": "fastapi",
        "name": "FastAPI",
        "category": "framework",
        "description": "Modern high-performance Python ASGI web framework built on Pydantic and Starlette.",
        "synonyms": ["fast-api"],
    },
    {
        "id": "django",
        "name": "Django",
        "category": "framework",
        "description": "Batteries-included Python web framework, ORM, authentication, and template system.",
        "synonyms": ["django orm", "django rest framework", "drf"],
    },
    {
        "id": "flask",
        "name": "Flask",
        "category": "framework",
        "description": "Lightweight Python WSGI microframework for web APIs and rapid microservices.",
        "synonyms": [],
    },
    {
        "id": "react",
        "name": "React",
        "category": "framework",
        "description": "Declarative component-based UI library, hooks lifecycle, virtual DOM, and client-state management.",
        "synonyms": ["reactjs", "react.js"],
    },
    {
        "id": "nextjs",
        "name": "Next.js",
        "category": "framework",
        "description": "React framework for production with SSR, static generation, server components, and API routes.",
        "synonyms": ["next.js", "next"],
    },
    {
        "id": "nodejs",
        "name": "Node.js",
        "category": "framework",
        "description": "V8 JavaScript runtime environment for scalable asynchronous network applications.",
        "synonyms": ["node", "node.js"],
    },
    {
        "id": "express",
        "name": "Express.js",
        "category": "framework",
        "description": "Fast, unopinionated, minimalist web framework for Node.js.",
        "synonyms": ["express"],
    },
    {
        "id": "tailwind-css",
        "name": "Tailwind CSS",
        "category": "framework",
        "description": "Utility-first CSS framework for rapid responsive UI styling and design systems.",
        "synonyms": ["tailwindcss", "tailwind"],
    },
    {
        "id": "pytorch",
        "name": "PyTorch",
        "category": "framework",
        "description": "Open source tensor and dynamic neural network deep learning framework.",
        "synonyms": ["torch"],
    },
    {
        "id": "tensorflow",
        "name": "TensorFlow & Keras",
        "category": "framework",
        "description": "End-to-end open source platform for machine learning and computational graph operations.",
        "synonyms": ["tf", "keras"],
    },
    {
        "id": "spring-boot",
        "name": "Spring Boot",
        "category": "framework",
        "description": "Enterprise Java application framework for microservices and enterprise APIs.",
        "synonyms": ["spring", "springboot"],
    },

    # ─── Databases & Storage ────────────────────────────────────────────
    {
        "id": "sql-databases",
        "name": "SQL & Relational Databases",
        "category": "database",
        "description": "Relational database schema modeling, SQL query authoring, window functions, indexing, and ACID transaction concurrency.",
        "synonyms": ["rdbms", "relational databases"],
    },
    {
        "id": "postgresql",
        "name": "PostgreSQL",
        "category": "database",
        "description": "Advanced open source object-relational database system with JSONB, MVCC, and indexing.",
        "synonyms": ["postgres", "pgsql", "psql"],
    },
    {
        "id": "redis",
        "name": "Redis",
        "category": "database",
        "description": "In-memory data structure store used as a database, cache, message broker, and streaming engine.",
        "synonyms": ["redis cache"],
    },
    {
        "id": "mongodb",
        "name": "MongoDB",
        "category": "database",
        "description": "Document-oriented NoSQL database supporting flexible schema, aggregation pipelines, and sharding.",
        "synonyms": ["mongo", "nosql"],
    },
    {
        "id": "elasticsearch",
        "name": "Elasticsearch",
        "category": "database",
        "description": "Distributed, RESTful search and analytics engine for text search and log indexing.",
        "synonyms": ["elastic", "opensearch"],
    },

    # ─── Tools, DevOps & Infrastructure ─────────────────────────────────
    {
        "id": "git",
        "name": "Git & Version Control",
        "category": "tool",
        "description": "Distributed version control system, branching strategies (Gitflow, trunk-based), and commit history.",
        "synonyms": ["github", "gitlab", "vcs"],
    },
    {
        "id": "docker",
        "name": "Docker & Containerization",
        "category": "tool",
        "description": "Container virtualization, Dockerfile optimization, multi-stage builds, and container runtimes.",
        "synonyms": ["containers", "dockerfile", "containerization"],
    },
    {
        "id": "kubernetes",
        "name": "Kubernetes",
        "category": "tool",
        "description": "Container orchestration, pods, deployments, services, ingress, and cluster scaling.",
        "synonyms": ["k8s", "k8s cluster"],
    },
    {
        "id": "ci-cd",
        "name": "CI/CD Pipelines",
        "category": "tool",
        "description": "Continuous Integration and Continuous Delivery automation (GitHub Actions, GitLab CI).",
        "synonyms": ["github actions", "continuous integration", "cicd", "jenkins"],
    },
    {
        "id": "linux",
        "name": "Linux Systems Administration",
        "category": "tool",
        "description": "Operating system fundamentals, processes, file permissions, networking (systemd, sockets), and security.",
        "synonyms": ["linux os", "unix", "ubuntu"],
    },
    {
        "id": "terraform",
        "name": "Terraform (IaC)",
        "category": "tool",
        "description": "Infrastructure as Code tool for building, changing, and versioning cloud infrastructure safely.",
        "synonyms": ["iac", "infrastructure as code"],
    },

    # ─── Cloud Providers ────────────────────────────────────────────────
    {
        "id": "aws",
        "name": "Amazon Web Services (AWS)",
        "category": "cloud",
        "description": "AWS cloud computing platform including EC2, S3, RDS, Lambda, ECS, IAM, and VPC networking.",
        "synonyms": ["amazon web services", "amazon aws"],
    },
    {
        "id": "gcp",
        "name": "Google Cloud Platform (GCP)",
        "category": "cloud",
        "description": "Google Cloud Platform including Compute Engine, Cloud Run, GKE, BigQuery, and Vertex AI.",
        "synonyms": ["google cloud", "google cloud platform"],
    },
    {
        "id": "azure",
        "name": "Microsoft Azure",
        "category": "cloud",
        "description": "Microsoft cloud computing services for building, testing, deploying, and managing applications.",
        "synonyms": ["microsoft azure", "azure cloud"],
    },

    # ─── Architecture & Concepts ────────────────────────────────────────
    {
        "id": "dsa",
        "name": "Data Structures & Algorithms",
        "category": "concept",
        "description": "Algorithmic complexity, tree and graph structures, dynamic programming, sorting, and algorithmic design patterns.",
        "synonyms": ["algorithms", "data structures", "leetcode", "algo"],
    },
    {
        "id": "web-development",
        "name": "Full-Stack Web Development",
        "category": "architecture",
        "description": "Full-stack client-server architecture, HTTP/2/3 protocols, browser rendering pipeline, web security (CORS/CSRF/XSS), and caching.",
        "synonyms": ["web dev", "frontend", "full stack"],
    },
    {
        "id": "rest-apis",
        "name": "RESTful API Design",
        "category": "architecture",
        "description": "REST architectural constraints, HTTP status codes, pagination, idempotency, versioning, and OpenAPI specs.",
        "synonyms": ["rest", "rest api", "restful", "api design"],
    },
    {
        "id": "microservices",
        "name": "Microservices Architecture",
        "category": "architecture",
        "description": "Service decomposition, event-driven architecture, API gateways, message queues, and distributed tracing.",
        "synonyms": ["distributed services", "event-driven architecture"],
    },
    {
        "id": "system-design",
        "name": "System Design & Distributed Systems",
        "category": "architecture",
        "description": "High-availability, load balancing, horizontal scalability, CAP theorem, replication, and fault tolerance.",
        "synonyms": ["distributed systems", "high availability", "scalability"],
    },
    {
        "id": "data-modeling",
        "name": "Data Modeling & Architecture",
        "category": "architecture",
        "description": "Entity-relationship modeling, 3NF normalization, dimensional data warehousing, and query optimization.",
        "synonyms": ["schema design", "database design"],
    },
    {
        "id": "machine-learning",
        "name": "Machine Learning",
        "category": "concept",
        "description": "Statistical learning, feature engineering, loss optimization, ensemble trees, classification metrics, and regularization.",
        "synonyms": ["ml", "supervised learning", "unsupervised learning"],
    },
    {
        "id": "deep-learning",
        "name": "Deep Learning",
        "category": "concept",
        "description": "Multi-layer neural networks, backpropagation, CNNs, RNNs, attention mechanisms, and optimization techniques.",
        "synonyms": ["dl", "neural networks"],
    },
    {
        "id": "ai-llm",
        "name": "AI & Large Language Models",
        "category": "concept",
        "description": "Transformer self-attention mechanics, subword tokenization, prompting strategies, PEFT/LoRA, RAG architectures, and agentic workflows.",
        "synonyms": ["llm", "large language models", "generative ai", "genai", "ai"],
    },
    {
        "id": "rag",
        "name": "Retrieval-Augmented Generation (RAG)",
        "category": "concept",
        "description": "Vector indexing, semantic chunking, dense embeddings, re-ranking, and retrieval pipelines for grounded LLM inference.",
        "synonyms": ["retrieval augmented generation", "vector search"],
    },
    {
        "id": "nlp",
        "name": "Natural Language Processing (NLP)",
        "category": "concept",
        "description": "Text tokenization, sentiment analysis, named entity recognition (NER), language modeling, and embeddings.",
        "synonyms": ["natural language processing"],
    },
    {
        "id": "security-best-practices",
        "name": "Application Security & OWASP",
        "category": "concept",
        "description": "Authentication (OAuth2/JWT), RBAC, encryption at rest/in transit, OWASP Top 10 mitigation, and input validation.",
        "synonyms": ["security", "appsec", "owasp", "cybersecurity"],
    },
]

# Normalized synonym lookup map (alias -> canonical skill_id)
SKILL_ALIAS_MAP: Dict[str, str] = {}
for skill in SKILL_TAXONOMY:
    SKILL_ALIAS_MAP[skill["id"].lower()] = skill["id"]
    SKILL_ALIAS_MAP[skill["name"].lower()] = skill["id"]
    for alias in skill.get("synonyms", []):
        SKILL_ALIAS_MAP[alias.lower()] = skill["id"]


def normalize_skill_name(raw_name: str) -> str | None:
    """
    Deterministically normalizes a freeform skill string into a canonical skill ID.
    Returns canonical skill_id or None if unmapped.
    """
    if not raw_name:
        return None
    cleaned = raw_name.strip().lower()
    return SKILL_ALIAS_MAP.get(cleaned)
