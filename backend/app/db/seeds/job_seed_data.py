"""
Curated Benchmark Job Postings Dataset for CoachPath.
Supplies verified, realistic tech job opportunities across the canonical benchmark roles.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

SEED_JOB_DATA: List[Dict[str, Any]] = [
    # ─── 1. Backend Developer Roles ────────────────────────────────────
    {
        "external_id": "seed-job-001",
        "title": "Junior Backend Engineer",
        "company_name": "Stripe",
        "location": "Seattle, WA",
        "remote_type": "hybrid",
        "role_id": "backend-developer",
        "experience_level": "entry_level",
        "min_salary": 115000,
        "max_salary": 135000,
        "currency": "USD",
        "application_url": "https://stripe.com/jobs/junior-backend-engineer",
        "source_url": "https://stripe.com/jobs/junior-backend-engineer",
        "description_text": """
## About the Role
As a Junior Backend Engineer at Stripe, you will help build scalable payment APIs, transactional ledger services, and asynchronous processing workers.

## Responsibilities
- Design, implement, and maintain RESTful backend APIs in Python and Go.
- Model relational database schemas in PostgreSQL with transaction isolation and performance in mind.
- Write unit, integration, and load tests to safeguard high-throughput payment rails.
- Collaborate with frontend engineers, product managers, and infrastructure teams.

## Requirements
- Demonstrated proficiency in Python or Go.
- Strong understanding of relational databases and SQL, particularly PostgreSQL.
- Knowledge of REST API principles and asynchronous programming.
- Familiarity with version control using Git and CI/CD pipelines.

## Preferred Qualifications
- Experience with Docker or containerized development environments.
- Understanding of distributed systems and message brokers like Redis or Kafka.
- Bachelor's degree in Computer Science, software engineering, or equivalent practical experience.
        """.strip(),
    },
    {
        "external_id": "seed-job-002",
        "title": "Backend Software Engineer, Core Services",
        "company_name": "Datadog",
        "location": "New York, NY",
        "remote_type": "remote",
        "role_id": "backend-developer",
        "experience_level": "junior",
        "min_salary": 120000,
        "max_salary": 145000,
        "currency": "USD",
        "application_url": "https://datadoghq.com/careers/backend-core",
        "source_url": "https://datadoghq.com/careers/backend-core",
        "description_text": """
## Role Overview
Datadog is looking for a Backend Engineer to build telemetry ingestion pipelines and microservice architectures.

## Responsibilities
- Architect high-performance backend microservices using Python and FastAPI.
- Optimize database queries, caching strategies with Redis, and data storage patterns.
- Troubleshoot production issues and participate in site reliability practices.
- Develop comprehensive automated test suites and maintain zero-downtime deployments.

## Requirements
- 1-3 years of server-side engineering experience with Python or Java.
- Proven experience with FastAPI or Django and relational databases (PostgreSQL, MySQL).
- Solid grasp of data structures, algorithms, and system design fundamentals.
- Comfort with Linux environments, Docker, and Git workflows.

## Preferred Qualifications
- Exposure to cloud platforms like AWS or GCP.
- Familiarity with Kubernetes orchestration and Prometheus monitoring.
        """.strip(),
    },
    {
        "external_id": "seed-job-003",
        "title": "API Backend Developer",
        "company_name": "Twilio",
        "location": "San Francisco, CA",
        "remote_type": "remote",
        "role_id": "backend-developer",
        "experience_level": "entry_level",
        "min_salary": 110000,
        "max_salary": 130000,
        "currency": "USD",
        "application_url": "https://twilio.com/careers/api-dev",
        "source_url": "https://twilio.com/careers/api-dev",
        "description_text": """
## Opportunity
Join Twilio's Developer Platform team building communication APIs relied upon by millions of developers worldwide.

## Responsibilities
- Build and maintain resilient RESTful APIs in Python and Node.js.
- Partner with security and compliance teams to ensure data privacy and authentication standards (OAuth2, JWT).
- Participate in agile sprints, daily standups, and code review processes.

## Requirements
- Solid programming skills in Python, JavaScript, or TypeScript.
- Understanding of web fundamentals, HTTP protocols, status codes, and JSON serialization.
- Familiarity with SQL databases and relational modeling.
- Enthusiasm for writing clean, readable, self-documenting code.

## Preferred Qualifications
- Hands-on experience with unit testing frameworks such as pytest or Jest.
- Understanding of Docker containerization.
        """.strip(),
    },

    # ─── 2. Frontend Developer Roles ───────────────────────────────────
    {
        "external_id": "seed-job-004",
        "title": "Junior Frontend Engineer",
        "company_name": "Vercel",
        "location": "San Francisco, CA",
        "remote_type": "remote",
        "role_id": "frontend-developer",
        "experience_level": "entry_level",
        "min_salary": 110000,
        "max_salary": 135000,
        "currency": "USD",
        "application_url": "https://vercel.com/careers/junior-frontend",
        "source_url": "https://vercel.com/careers/junior-frontend",
        "description_text": """
## What You'll Do
Build responsive, accessible, lightning-fast web applications using Next.js, React, and TypeScript.

## Responsibilities
- Develop rich user interfaces with React, Next.js, TypeScript, and Tailwind CSS.
- Ensure cross-browser compatibility, web performance (Core Web Vitals), and WCAG accessibility.
- Integrate frontend client components with backend REST and GraphQL endpoints.
- Maintain comprehensive unit and component tests using Vitest and React Testing Library.

## Requirements
- Proficiency in modern JavaScript (ES6+), TypeScript, HTML5, and CSS3.
- Hands-on experience building user interfaces with React.
- Understanding of state management, hooks, and responsive design patterns.
- Experience with Git and version control.

## Preferred Qualifications
- Familiarity with Next.js App Router and server components.
- Experience with Tailwind CSS and modern CSS modules.
        """.strip(),
    },
    {
        "external_id": "seed-job-005",
        "title": "Frontend UI Developer",
        "company_name": "Figma",
        "location": "San Francisco, CA",
        "remote_type": "hybrid",
        "role_id": "frontend-developer",
        "experience_level": "junior",
        "min_salary": 125000,
        "max_salary": 150000,
        "currency": "USD",
        "application_url": "https://figma.com/careers/frontend-ui",
        "source_url": "https://figma.com/careers/frontend-ui",
        "description_text": """
## Role Description
Help create the world's leading collaborative design platform, crafting fluid web interfaces.

## Responsibilities
- Implement high-performance UI components in React and TypeScript.
- Translate complex design mockups and Figma designs into pixel-perfect web experiences.
- Optimize client-side rendering, canvas interactions, and DOM operations.
- Contribute to our shared design system and component library.

## Requirements
- 1-3 years of professional frontend engineering experience.
- Deep expertise in TypeScript and React.
- Solid understanding of web performance, browser rendering pipelines, and DOM APIs.
- Experience with modern frontend toolchains (Vite, Webpack, npm/pnpm).

## Preferred Qualifications
- Familiarity with WebAssembly, WebGL, or Canvas APIs.
- Experience working closely with product designers and UX researchers.
        """.strip(),
    },

    # ─── 3. Fullstack Developer Roles ──────────────────────────────────
    {
        "external_id": "seed-job-006",
        "title": "Full Stack Engineer, Product",
        "company_name": "Notion",
        "location": "San Francisco, CA",
        "remote_type": "hybrid",
        "role_id": "fullstack-developer",
        "experience_level": "junior",
        "min_salary": 125000,
        "max_salary": 155000,
        "currency": "USD",
        "application_url": "https://notion.so/careers/fullstack-product",
        "source_url": "https://notion.so/careers/fullstack-product",
        "description_text": """
## Role Summary
Notion is looking for a versatile Full Stack Engineer to ship user-facing features across our web app, collaboration backend, and database engine.

## Responsibilities
- Deliver end-to-end features spanning React/Next.js frontend to Node.js/Python backend services.
- Design database migrations and schemas in PostgreSQL.
- Build intuitive user interfaces while keeping server-side APIs performant and secure.
- Champion code quality through automated testing and code reviews.

## Requirements
- Proficiency with TypeScript across both frontend (React) and backend (Node.js or Python).
- Practical experience with relational databases (PostgreSQL, SQL).
- Understanding of asynchronous programming, HTTP/REST protocols, and client-server sync.
- Track record of shipping functional web projects or products.

## Preferred Qualifications
- Experience with full-stack frameworks such as Next.js or Remix.
- Familiarity with Docker and cloud hosting environments (AWS, Vercel).
        """.strip(),
    },
    {
        "external_id": "seed-job-007",
        "title": "Junior Full Stack Developer",
        "company_name": "Shopify",
        "location": "Toronto, ON",
        "remote_type": "remote",
        "role_id": "fullstack-developer",
        "experience_level": "entry_level",
        "min_salary": 105000,
        "max_salary": 125000,
        "currency": "USD",
        "application_url": "https://shopify.com/careers/junior-fullstack",
        "source_url": "https://shopify.com/careers/junior-fullstack",
        "description_text": """
## Impact
Empower millions of merchants around the world by building e-commerce web applications and merchant tools.

## Responsibilities
- Develop merchant dashboard features using React, TypeScript, and GraphQL.
- Write backend services and background workers in Ruby, Python, or Go.
- Write robust unit and end-to-end tests for all customer flows.

## Requirements
- Solid foundation in JavaScript, TypeScript, and Python or Ruby.
- Experience building full-stack web applications with relational databases.
- Strong problem-solving skills and curiosity to learn new technologies.

## Preferred Qualifications
- Experience with GraphQL or REST API design.
- Active GitHub portfolio or open source contributions.
        """.strip(),
    },

    # ─── 4. Data Scientist Roles ───────────────────────────────────────
    {
        "external_id": "seed-job-008",
        "title": "Associate Data Scientist",
        "company_name": "Spotify",
        "location": "Boston, MA",
        "remote_type": "hybrid",
        "role_id": "data-scientist",
        "experience_level": "entry_level",
        "min_salary": 110000,
        "max_salary": 130000,
        "currency": "USD",
        "application_url": "https://spotify.com/jobs/assoc-data-scientist",
        "source_url": "https://spotify.com/jobs/assoc-data-scientist",
        "description_text": """
## About the Team
Spotify's Data Science team leverages billions of daily interactions to understand listener behavior and personalize music discovery.

## Responsibilities
- Analyze large-scale user interaction datasets using SQL and Python.
- Build predictive statistical models, regression analyses, and customer segmentation algorithms.
- Design, evaluate, and interpret A/B experiments and hypothesis tests.
- Communicate findings and actionable recommendations to product and engineering partners.

## Requirements
- Proficiency in Python, Pandas, NumPy, and Scikit-Learn.
- Strong SQL skills for querying distributed data warehouses (BigQuery, Snowflake).
- Solid understanding of statistical concepts: hypothesis testing, confidence intervals, regression.
- Bachelor's or Master's degree in Data Science, Statistics, Mathematics, or Computer Science.

## Preferred Qualifications
- Experience with data visualization libraries (Seaborn, Matplotlib, Plotly).
- Familiarity with A/B testing methodologies and causal inference.
        """.strip(),
    },
    {
        "external_id": "seed-job-009",
        "title": "Data Scientist, Product Analytics",
        "company_name": "Airbnb",
        "location": "San Francisco, CA",
        "remote_type": "remote",
        "role_id": "data-scientist",
        "experience_level": "junior",
        "min_salary": 130000,
        "max_salary": 160000,
        "currency": "USD",
        "application_url": "https://airbnb.com/careers/data-scientist-product",
        "source_url": "https://airbnb.com/careers/data-scientist-product",
        "description_text": """
## Overview
Drive product strategy for Airbnb's host and guest marketplace through data-driven experimentation and statistical modeling.

## Responsibilities
- Define key product health metrics and build executive dashboards.
- Design end-to-end A/B tests to evaluate feature launches.
- Develop predictive churn, retention, and pricing models using Python.
- Translate data into strategic insights for product leaders.

## Requirements
- 1-3 years of data science or product analytics experience.
- Expert-level SQL querying complex relational and column-oriented databases.
- Strong Python modeling skills (Pandas, Scikit-Learn, Statsmodels).
- Deep knowledge of experimental design and power analysis.

## Preferred Qualifications
- Experience with Spark or distributed data processing.
- Familiarity with Tableau or Superset visualization tools.
        """.strip(),
    },

    # ─── 5. Machine Learning Engineer Roles ────────────────────────────
    {
        "external_id": "seed-job-010",
        "title": "Junior Machine Learning Engineer",
        "company_name": "Pinterest",
        "location": "San Francisco, CA",
        "remote_type": "hybrid",
        "role_id": "machine-learning-engineer",
        "experience_level": "entry_level",
        "min_salary": 125000,
        "max_salary": 150000,
        "currency": "USD",
        "application_url": "https://pinterest.com/careers/junior-mle",
        "source_url": "https://pinterest.com/careers/junior-mle",
        "description_text": """
## About the Team
Pinterest's Machine Learning team builds recommendation engines, visual search models, and content classification systems.

## Responsibilities
- Train, evaluate, and fine-tune deep learning and machine learning models using PyTorch.
- Build scalable feature engineering pipelines and offline evaluation benchmarks.
- Deploy models to low-latency serving infrastructure with Docker and Triton.
- Monitor model drift and production performance metrics.

## Requirements
- Strong Python programming skills and software engineering practices.
- Hands-on experience with PyTorch or TensorFlow, NumPy, and Scikit-Learn.
- Solid understanding of machine learning algorithms (gradient boosted trees, neural networks, embeddings).
- Degree in Computer Science, Machine Learning, or related quantitative field.

## Preferred Qualifications
- Experience with MLflow, Weights & Biases, or similar MLOps tooling.
- Knowledge of distributed training and GPU acceleration (CUDA).
        """.strip(),
    },
    {
        "external_id": "seed-job-011",
        "title": "ML Engineer, Recommendations",
        "company_name": "Netflix",
        "location": "Los Gatos, CA",
        "remote_type": "hybrid",
        "role_id": "machine-learning-engineer",
        "experience_level": "junior",
        "min_salary": 135000,
        "max_salary": 165000,
        "currency": "USD",
        "application_url": "https://netflix.com/jobs/ml-recs",
        "source_url": "https://netflix.com/jobs/ml-recs",
        "description_text": """
## Role Description
Join the team behind the iconic Netflix personalized recommendation system, processing millions of requests per second.

## Responsibilities
- Develop collaborative filtering, sequence modeling, and deep learning algorithms in PyTorch.
- Scale training pipelines across cloud GPU clusters in AWS.
- Implement real-time inference microservices in Python and C++.
- Conduct online A/B testing to measure engagement and retention lifts.

## Requirements
- 1-3 years experience developing and deploying machine learning models in production.
- Advanced proficiency in Python and PyTorch.
- Strong software design skills: algorithms, concurrency, and performance profiling.
- Experience with containerization (Docker) and cloud infrastructure (AWS or GCP).

## Preferred Qualifications
- Publications or projects in recommender systems or information retrieval.
- Experience with vector search databases (Faiss, Milvus, pgvector).
        """.strip(),
    },

    # ─── 6. AI Engineer Roles ──────────────────────────────────────────
    {
        "external_id": "seed-job-012",
        "title": "AI Application Engineer",
        "company_name": "Scale AI",
        "location": "San Francisco, CA",
        "remote_type": "onsite",
        "role_id": "ai-engineer",
        "experience_level": "junior",
        "min_salary": 130000,
        "max_salary": 160000,
        "currency": "USD",
        "application_url": "https://scale.com/careers/ai-app-eng",
        "source_url": "https://scale.com/careers/ai-app-eng",
        "description_text": """
## What You'll Do
Build generative AI applications, retrieval-augmented generation (RAG) pipelines, and evaluation harnesses.

## Responsibilities
- Architect RAG systems combining vector embeddings, semantic search, and LLM reasoning.
- Implement LLM orchestration with LangChain, LlamaIndex, and OpenAI/Anthropic APIs.
- Design rigorous evaluation benchmarks for hallucination prevention, latency, and factual recall.
- Build production APIs with FastAPI and PostgreSQL with pgvector.

## Requirements
- Strong Python programming and asynchronous API development experience.
- Experience integrating commercial LLMs (OpenAI, Anthropic) and open-source models (Llama, Mistral).
- Hands-on knowledge of vector databases (Pinecone, Chroma, pgvector, Qdrant).
- Understanding of prompt engineering, few-shot prompting, and structured output extraction.

## Preferred Qualifications
- Experience fine-tuning LLMs with LoRA / PEFT.
- Full-stack familiarity with Next.js or React for prototyping interactive AI UIs.
        """.strip(),
    },
    {
        "external_id": "seed-job-013",
        "title": "Generative AI Solutions Engineer",
        "company_name": "Anthropic",
        "location": "San Francisco, CA",
        "remote_type": "hybrid",
        "role_id": "ai-engineer",
        "experience_level": "entry_level",
        "min_salary": 135000,
        "max_salary": 165000,
        "currency": "USD",
        "application_url": "https://anthropic.com/careers/ai-solutions",
        "source_url": "https://anthropic.com/careers/ai-solutions",
        "description_text": """
## Mission
Deploy safe, reliable Claude AI integrations to solve complex industry workflows.

## Responsibilities
- Design and implement AI agent architectures, tool use (function calling), and multi-turn workflows.
- Build automated testing pipelines to benchmark output accuracy and adherence to safety guidelines.
- Partner with customers to debug complex prompt behavior and latency bottlenecks.
- Write technical documentation, code samples, and SDK examples in Python and TypeScript.

## Requirements
- Proficiency in Python and modern software engineering practices.
- Strong conceptual understanding of large language models, context windows, and tokenization.
- Experience with API design and asynchronous web frameworks (FastAPI, aiohttp).
- Excellent written and verbal communication skills.

## Preferred Qualifications
- Experience with autonomous agent frameworks and eval platforms.
- Background in safety evaluation, red-teaming, or model interpretability.
        """.strip(),
    },

    # ─── 7. DevOps & Cloud Engineer Roles ──────────────────────────────
    {
        "external_id": "seed-job-014",
        "title": "Junior DevOps Engineer",
        "company_name": "Cloudflare",
        "location": "Austin, TX",
        "remote_type": "hybrid",
        "role_id": "devops-cloud-engineer",
        "experience_level": "entry_level",
        "min_salary": 105000,
        "max_salary": 125000,
        "currency": "USD",
        "application_url": "https://cloudflare.com/careers/junior-devops",
        "source_url": "https://cloudflare.com/careers/junior-devops",
        "description_text": """
## Role Overview
Help operate Cloudflare's global edge network through automated infrastructure-as-code and CI/CD pipelines.

## Responsibilities
- Manage cloud infrastructure using Terraform and Ansible.
- Build and maintain continuous integration and automated deployment pipelines in GitHub Actions.
- Configure monitoring, alerting, and log aggregation with Prometheus and Grafana.
- Assist software engineers in debugging container runtime issues in Linux and Docker.

## Requirements
- Practical experience with Linux system administration, shell scripting (Bash), and networking basics.
- Familiarity with Docker containerization and Dockerfiles.
- Knowledge of cloud platforms (AWS, GCP, or Azure).
- Version control proficiency with Git.

## Preferred Qualifications
- Hands-on experience with Terraform or Kubernetes.
- Basic coding proficiency in Python or Go for infrastructure automation.
        """.strip(),
    },
    {
        "external_id": "seed-job-015",
        "title": "Cloud Infrastructure Engineer",
        "company_name": "HashiCorp",
        "location": "San Francisco, CA",
        "remote_type": "remote",
        "role_id": "devops-cloud-engineer",
        "experience_level": "junior",
        "min_salary": 120000,
        "max_salary": 145000,
        "currency": "USD",
        "application_url": "https://hashicorp.com/careers/cloud-infra",
        "source_url": "https://hashicorp.com/careers/cloud-infra",
        "description_text": """
## Role Details
Build cloud infrastructure platforms for developers using Terraform, Vault, and Kubernetes.

## Responsibilities
- Architect repeatable multi-cloud infrastructure in AWS using Terraform.
- Maintain production Kubernetes clusters, Helm charts, and ingress controllers.
- Implement security best practices: secrets management, least-privilege IAM, and audit trails.
- Collaborate on incident response and infrastructure reliability improvements.

## Requirements
- 1-3 years of cloud engineering or site reliability experience.
- Expertise in AWS or GCP, Terraform, and Docker.
- Experience administering Kubernetes clusters in production environments.
- Proficiency in Python, Go, or Bash for automation scripting.

## Preferred Qualifications
- CKA (Certified Kubernetes Administrator) or AWS Solutions Architect certification.
- Experience with service meshes (Consul, Istio).
        """.strip(),
    },

    # ─── 8. Software Engineer (General SWE) Roles ─────────────────────
    {
        "external_id": "seed-job-016",
        "title": "Associate Software Engineer",
        "company_name": "GitHub",
        "location": "San Francisco, CA",
        "remote_type": "remote",
        "role_id": "software-engineer",
        "experience_level": "entry_level",
        "min_salary": 115000,
        "max_salary": 135000,
        "currency": "USD",
        "application_url": "https://github.com/careers/associate-swe",
        "source_url": "https://github.com/careers/associate-swe",
        "description_text": """
## Purpose
Build tools that empower over 100 million developers worldwide on GitHub.

## Responsibilities
- Write clean, maintainable, tested code across the GitHub software stack.
- Collaborate with product designers and senior engineers to deliver reliable developer features.
- Review peers' pull requests with constructive, pedagogical feedback.
- Participate in on-call rotations and production stability improvements.

## Requirements
- Solid understanding of computer science fundamentals: algorithms, data structures, and OOP.
- Proficiency in at least one modern language: Python, TypeScript, Ruby, Go, or Java.
- Familiarity with relational databases, SQL, and Git workflows.
- Strong problem solving and communication abilities.

## Preferred Qualifications
- Active open source contributions or published personal software projects.
- Familiarity with CI/CD automation and containerized services.
        """.strip(),
    },
    {
        "external_id": "seed-job-017",
        "title": "Software Engineer, Core Platform",
        "company_name": "Uber",
        "location": "Seattle, WA",
        "remote_type": "hybrid",
        "role_id": "software-engineer",
        "experience_level": "junior",
        "min_salary": 125000,
        "max_salary": 150000,
        "currency": "USD",
        "application_url": "https://uber.com/careers/swe-core",
        "source_url": "https://uber.com/careers/swe-core",
        "description_text": """
## About the Team
Uber's Core Platform team builds the foundational services powering global ridesharing and delivery logistics.

## Responsibilities
- Develop high-throughput microservices handling millions of geographic requests per minute.
- Optimize database performance and implement caching layers in Redis and Cassandra.
- Maintain high test coverage through automated unit and integration tests.
- Participate in design reviews, architecture discussions, and root cause analyses.

## Requirements
- 1-3 years of software engineering experience.
- Proficiency in Go, Java, or Python.
- Strong understanding of multithreading, concurrent programming, and distributed systems.
- Experience with relational and NoSQL database modeling.

## Preferred Qualifications
- Experience with Apache Kafka or gRPC communication protocols.
- Bachelor's or Master's degree in Computer Science or Software Engineering.
        """.strip(),
    },

    # ─── 9. Data Analyst Roles ─────────────────────────────────────────
    {
        "external_id": "seed-job-018",
        "title": "Junior Data Analyst",
        "company_name": "DoorDash",
        "location": "San Francisco, CA",
        "remote_type": "hybrid",
        "role_id": "data-analyst",
        "experience_level": "entry_level",
        "min_salary": 95000,
        "max_salary": 115000,
        "currency": "USD",
        "application_url": "https://doordash.com/careers/junior-analyst",
        "source_url": "https://doordash.com/careers/junior-analyst",
        "description_text": """
## What You'll Do
Uncover data-driven opportunities to optimize marketplace logistics and merchant growth at DoorDash.

## Responsibilities
- Write complex SQL queries across massive datasets to answer strategic business questions.
- Build and maintain interactive dashboards in Tableau and Mode Analytics.
- Collaborate with operations and marketing teams to evaluate campaigns and performance metrics.
- Automate recurring reporting pipelines using Python and SQL.

## Requirements
- Strong SQL proficiency (joins, window functions, aggregations, CTEs).
- Experience with business intelligence and visualization tools (Tableau, Power BI, Looker).
- Basic Python scripting skills for data analysis (Pandas).
- Strong analytical curiosity and attention to detail.

## Preferred Qualifications
- Degree in Economics, Statistics, Mathematics, or Business Analytics.
- Experience with Snowflake or Google BigQuery.
        """.strip(),
    },
    {
        "external_id": "seed-job-019",
        "title": "Business Intelligence Analyst",
        "company_name": "Snowflake",
        "location": "San Mateo, CA",
        "remote_type": "remote",
        "role_id": "data-analyst",
        "experience_level": "junior",
        "min_salary": 105000,
        "max_salary": 125000,
        "currency": "USD",
        "application_url": "https://snowflake.com/careers/bi-analyst",
        "source_url": "https://snowflake.com/careers/bi-analyst",
        "description_text": """
## Role Summary
Join the BI team at Snowflake, building world-class analytical reports on top of Snowflake's own Data Cloud.

## Responsibilities
- Design data models and semantic layers for enterprise analytics.
- Build intuitive self-serve dashboards and KPI scorecards for executive leadership.
- Partner with data engineering to define data transformation pipelines and data quality tests.
- Perform exploratory analyses on customer usage, retention, and expansion patterns.

## Requirements
- 1-3 years of data analytics or BI experience.
- Expert-level SQL skills.
- Deep expertise in modern BI platforms (Tableau, PowerBI, or Sigma).
- Clear communication of statistical findings to non-technical stakeholders.

## Preferred Qualifications
- Experience with dbt (data build tool) for SQL modeling.
- Python or R programming experience for exploratory data visualization.
        """.strip(),
    },
    {
        "external_id": "seed-job-020",
        "title": "Backend Systems Software Engineer",
        "company_name": "MongoDB",
        "location": "New York, NY",
        "remote_type": "hybrid",
        "role_id": "backend-developer",
        "experience_level": "mid",
        "min_salary": 135000,
        "max_salary": 160000,
        "currency": "USD",
        "application_url": "https://mongodb.com/careers/backend-systems",
        "source_url": "https://mongodb.com/careers/backend-systems",
        "description_text": """
## Opportunity
Build distributed storage and replication features within MongoDB Atlas cloud database.

## Responsibilities
- Develop distributed storage and query processing engine features in Go, C++, or Python.
- Implement high-availability, fault tolerance, and consensus mechanisms.
- Troubleshoot performance regressions, memory leaks, and CPU bottlenecks.

## Requirements
- 3+ years experience with systems programming in Go, C++, or Python.
- Deep understanding of distributed databases, concurrency, and OS internals.
- Practical experience with Linux systems, networking protocols, and performance tuning.

## Preferred Qualifications
- Experience with Raft, Paxos, or distributed transaction protocols.
- Familiarity with cloud deployment on AWS, Azure, or GCP.
        """.strip(),
    },
    {
        "external_id": "seed-job-021",
        "title": "Frontend React Engineer",
        "company_name": "Linear",
        "location": "San Francisco, CA",
        "remote_type": "remote",
        "role_id": "frontend-developer",
        "experience_level": "junior",
        "min_salary": 120000,
        "max_salary": 145000,
        "currency": "USD",
        "application_url": "https://linear.app/careers/react-eng",
        "source_url": "https://linear.app/careers/react-eng",
        "description_text": """
## About Linear
We are building the issue tracker and project management tool that teams love using. Fast, keyboard-first, and sync-driven.

## Responsibilities
- Build highly responsive client-side interfaces in React and TypeScript.
- Implement local-first data synchronization and offline editing capabilities.
- Ensure 60fps animations and instant keyboard shortcut navigation.

## Requirements
- Exceptional proficiency in modern JavaScript, TypeScript, and React.
- Solid understanding of web performance, DOM rendering, and memory management.
- Passion for software craft, typography, and UX design details.

## Preferred Qualifications
- Experience with IndexedDB, SQLite in WASM, or client-side caching.
- Familiarity with Tailwind CSS and CSS animation libraries.
        """.strip(),
    },
    {
        "external_id": "seed-job-022",
        "title": "Machine Learning Engineer, NLP",
        "company_name": "Cohere",
        "location": "Toronto, ON",
        "remote_type": "remote",
        "role_id": "machine-learning-engineer",
        "experience_level": "junior",
        "min_salary": 130000,
        "max_salary": 160000,
        "currency": "USD",
        "application_url": "https://cohere.com/careers/mle-nlp",
        "source_url": "https://cohere.com/careers/mle-nlp",
        "description_text": """
## Mission
Build natural language processing models and enterprise embedding architectures that understand human communication.

## Responsibilities
- Train and evaluate transformer-based models for text classification, embedding generation, and summarization.
- Build high-throughput inference serving pipelines using PyTorch and ONNX Runtime.
- Collaborate with software engineers to benchmark latency and token throughput.

## Requirements
- Proficiency in Python, PyTorch, and Hugging Face Transformers.
- Strong understanding of NLP architectures: attention mechanisms, tokenization, embeddings.
- Experience with Docker and cloud GPU compute.

## Preferred Qualifications
- Familiarity with quantization techniques (INT8, FP8) and vLLM / TensorRT-LLM.
- Research experience in computational linguistics or natural language understanding.
        """.strip(),
    },
    {
        "external_id": "seed-job-023",
        "title": "Data Platform Engineer",
        "company_name": "Databricks",
        "location": "San Francisco, CA",
        "remote_type": "hybrid",
        "role_id": "data-engineer",
        "experience_level": "junior",
        "min_salary": 125000,
        "max_salary": 150000,
        "currency": "USD",
        "application_url": "https://databricks.com/careers/data-platform-engineer",
        "source_url": "https://databricks.com/careers/data-platform-engineer",
        "description_text": """
## About the Role
As a Data Platform Engineer at Databricks, you will help design, build, and optimize scalable data ingestion pipelines, Lakehouse data modeling, and orchestration workflows.

## Responsibilities
- Design and maintain reliable batch and streaming ETL pipelines using Python and Apache Spark.
- Model dimensional schemas, data vault tables, and optimized SQL queries in cloud data warehouses.
- Build automated DAG orchestration workflows using Airflow and dbt.
- Ensure high data quality, schema validation, and pipeline observability.

## Requirements
- Demonstrated proficiency in Python and SQL (complex analytical queries, window functions).
- Strong data modeling fundamentals: star/snowflake schemas, dimensional design.
- Hands-on experience with ETL/ELT pipeline design and workflow orchestration.
- Solid understanding of data structures, algorithms, and Git version control.

## Preferred Qualifications
- Experience with Apache Spark, Kafka, or distributed streaming systems.
- Familiarity with cloud platforms (AWS, GCP) and containerization with Docker.
        """.strip(),
    },
    {
        "external_id": "seed-job-024",
        "title": "Mobile Software Engineer (iOS & Android)",
        "company_name": "DoorDash",
        "location": "Sunnyvale, CA",
        "remote_type": "remote",
        "role_id": "mobile-engineer",
        "experience_level": "junior",
        "min_salary": 120000,
        "max_salary": 145000,
        "currency": "USD",
        "application_url": "https://doordash.com/careers/mobile-engineer",
        "source_url": "https://doordash.com/careers/mobile-engineer",
        "description_text": """
## About the Role
Join our consumer engineering team to build world-class, responsive, and accessible mobile experiences across iOS and Android platforms.

## Responsibilities
- Architect, build, and maintain native and cross-platform mobile features using modern declarative frameworks (SwiftUI/Jetpack Compose or React Native).
- Integrate backend RESTful and streaming APIs with robust token authentication, offline data sync, and optimistic UI updates.
- Optimize app launch times, frame rates, memory footprints, and battery consumption.
- Write unit, integration, and UI automation tests to preserve mobile app reliability.

## Requirements
- Strong understanding of mobile application architecture (MVVM, Clean Architecture, state management, and lifecycle events).
- Proficiency in either Kotlin (Android) or Swift (iOS), or cross-platform mobile development (React Native / Flutter).
- Solid grasp of asynchronous networking, RESTful APIs, and offline caching.
- Good knowledge of data structures, algorithmic efficiency, and Git version control.

## Preferred Qualifications
- Experience with mobile CI/CD pipelines (Fastlane, GitHub Actions) and code signing.
- Understanding of mobile security best practices (Keychain/KeyStore, certificate pinning).
        """.strip(),
    },
]
