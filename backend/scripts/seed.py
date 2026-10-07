"""
CoachPath Database Seed Script (Phase 2B).
Populates canonical benchmark roles, master technology skills taxonomy,
and role benchmark requirements.
Marked clearly as development / baseline taxonomy seed data.
"""

import asyncio
import decimal
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.career import Role
from app.models.skills import RoleRequirement, Skill

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CANONICAL_ROLES = [
    {
        "id": "backend-developer",
        "title": "Backend Developer",
        "description": "Architects, builds, and maintains server-side web applications, robust APIs, and scalable distributed data storage systems.",
        "category": "engineering",
    },
    {
        "id": "frontend-developer",
        "title": "Frontend Developer",
        "description": "Engineers responsive, accessible, high-performance user interfaces and client-side applications.",
        "category": "engineering",
    },
    {
        "id": "fullstack-developer",
        "title": "Full Stack Developer",
        "description": "Builds end-to-end features spanning modern client-side architectures, RESTful APIs, and relational persistence layers.",
        "category": "engineering",
    },
    {
        "id": "ai-engineer",
        "title": "AI Engineer",
        "description": "Develops production-grade AI systems, LLM agent workflows, RAG pipelines, and model evaluation harnesses.",
        "category": "ai",
    },
    {
        "id": "devops-cloud-engineer",
        "title": "DevOps & Cloud Engineer",
        "description": "Automates CI/CD delivery pipelines, manages cloud infrastructure as code, and maintains container orchestration.",
        "category": "infrastructure",
    },
    {
        "id": "mobile-developer",
        "title": "Mobile Developer",
        "description": "Engineers performant native and cross-platform mobile experiences for iOS and Android devices.",
        "category": "mobile",
    },
    {
        "id": "data-engineer",
        "title": "Data Engineer",
        "description": "Designs and orchestrates large-scale data ingestion pipelines, analytical warehouses, and transformation workflows.",
        "category": "data",
    },
]

CANONICAL_SKILLS = [
    {
        "id": "python",
        "name": "Python",
        "category": "language",
        "description": "Interpreted high-level programming language emphasizing code readability and vast ecosystem for backend and AI.",
        "synonyms": ["py", "python3"],
    },
    {
        "id": "typescript",
        "name": "TypeScript",
        "category": "language",
        "description": "Typed superset of JavaScript providing static types, interfaces, and compile-time correctness.",
        "synonyms": ["ts"],
    },
    {
        "id": "javascript",
        "name": "JavaScript",
        "category": "language",
        "description": "Core dynamic language of modern web browsers and Node.js server runtimes.",
        "synonyms": ["js", "es6"],
    },
    {
        "id": "fastapi",
        "name": "FastAPI",
        "category": "framework",
        "description": "Modern, high-performance Python web framework based on standard type hints and OpenAPI.",
        "synonyms": ["fast-api"],
    },
    {
        "id": "react",
        "name": "React",
        "category": "framework",
        "description": "Component-driven declarative frontend library for constructing modern single-page applications.",
        "synonyms": ["reactjs", "react.js"],
    },
    {
        "id": "nextjs",
        "name": "Next.js",
        "category": "framework",
        "description": "The React framework for the web supporting server components, SSR, and production optimization.",
        "synonyms": ["next.js", "next"],
    },
    {
        "id": "postgresql",
        "name": "PostgreSQL",
        "category": "database",
        "description": "Advanced open-source relational database supporting ACID transactions, JSONB, and vector search.",
        "synonyms": ["postgres", "pgsql"],
    },
    {
        "id": "redis",
        "name": "Redis",
        "category": "database",
        "description": "In-memory data store used as a distributed cache, message broker, and real-time session store.",
        "synonyms": ["redis-server"],
    },
    {
        "id": "docker",
        "name": "Docker",
        "category": "tool",
        "description": "Industry-standard platform for containerizing applications into portable, reproducible runtime units.",
        "synonyms": ["containers", "docker-compose"],
    },
    {
        "id": "kubernetes",
        "name": "Kubernetes",
        "category": "cloud",
        "description": "Automated deployment, scaling, and management platform for containerized application workloads.",
        "synonyms": ["k8s"],
    },
    {
        "id": "aws",
        "name": "AWS",
        "category": "cloud",
        "description": "Amazon Web Services comprehensive suite of cloud computing, storage, and networking services.",
        "synonyms": ["amazon-web-services", "amazon-cloud"],
    },
    {
        "id": "git",
        "name": "Git",
        "category": "tool",
        "description": "Distributed version control system for tracking changes in source code during software development.",
        "synonyms": ["github", "version-control"],
    },
    {
        "id": "sql",
        "name": "SQL",
        "category": "concept",
        "description": "Structured Query Language for querying, aggregating, and manipulating relational databases.",
        "synonyms": ["ansi-sql", "relational-queries"],
    },
    {
        "id": "rest-api",
        "name": "REST API Architecture",
        "category": "architecture",
        "description": "Architectural principles for stateless, resource-oriented HTTP web services and client contracts.",
        "synonyms": ["rest", "restful-services"],
    },
    {
        "id": "system-design",
        "name": "System Design",
        "category": "architecture",
        "description": "Design of scalable, fault-tolerant distributed systems including caching, load balancing, and sharding.",
        "synonyms": ["distributed-systems", "software-architecture"],
    },
]

BENCHMARK_REQUIREMENTS = [
    # Backend Developer
    {"role_id": "backend-developer", "skill_id": "python", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.5")},
    {"role_id": "backend-developer", "skill_id": "fastapi", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.3")},
    {"role_id": "backend-developer", "skill_id": "postgresql", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.4")},
    {"role_id": "backend-developer", "skill_id": "redis", "importance": "preferred", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.1")},
    {"role_id": "backend-developer", "skill_id": "docker", "importance": "preferred", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.0")},
    {"role_id": "backend-developer", "skill_id": "git", "importance": "mandatory", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.0")},
    {"role_id": "backend-developer", "skill_id": "system-design", "importance": "preferred", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.2")},
    # Frontend Developer
    {"role_id": "frontend-developer", "skill_id": "typescript", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.5")},
    {"role_id": "frontend-developer", "skill_id": "react", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.5")},
    {"role_id": "frontend-developer", "skill_id": "nextjs", "importance": "preferred", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.2")},
    {"role_id": "frontend-developer", "skill_id": "javascript", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.3")},
    {"role_id": "frontend-developer", "skill_id": "git", "importance": "mandatory", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.0")},
    # Full Stack Developer
    {"role_id": "fullstack-developer", "skill_id": "typescript", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.3")},
    {"role_id": "fullstack-developer", "skill_id": "react", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.3")},
    {"role_id": "fullstack-developer", "skill_id": "python", "importance": "mandatory", "min_proficiency": "proficient", "weight": decimal.Decimal("1.3")},
    {"role_id": "fullstack-developer", "skill_id": "postgresql", "importance": "mandatory", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.2")},
    {"role_id": "fullstack-developer", "skill_id": "docker", "importance": "preferred", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.0")},
    # AI Engineer
    {"role_id": "ai-engineer", "skill_id": "python", "importance": "mandatory", "min_proficiency": "mastered", "weight": decimal.Decimal("1.6")},
    {"role_id": "ai-engineer", "skill_id": "fastapi", "importance": "mandatory", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.2")},
    {"role_id": "ai-engineer", "skill_id": "docker", "importance": "preferred", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.0")},
    {"role_id": "ai-engineer", "skill_id": "postgresql", "importance": "preferred", "min_proficiency": "demonstrated", "weight": decimal.Decimal("1.1")},
]


async def seed_canonical_data(session: AsyncSession) -> None:
    """Idempotently seeds canonical roles, skills, and benchmark requirements."""
    logger.info("Starting CoachPath canonical taxonomy seeding...")

    # 1. Seed Roles
    for role_data in CANONICAL_ROLES:
        existing = await session.scalar(select(Role).where(Role.id == role_data["id"]))
        if not existing:
            role = Role(**role_data)
            session.add(role)
            logger.info("Seeded canonical role: %s (%s)", role_data["title"], role_data["id"])
        else:
            existing.title = role_data["title"]
            existing.description = role_data["description"]
            existing.category = role_data["category"]

    await session.flush()

    # 2. Seed Skills
    for skill_data in CANONICAL_SKILLS:
        existing = await session.scalar(select(Skill).where(Skill.id == skill_data["id"]))
        if not existing:
            skill = Skill(
                id=skill_data["id"],
                name=skill_data["name"],
                category=skill_data["category"],
                description=skill_data["description"],
                synonyms=skill_data["synonyms"],
            )
            session.add(skill)
            logger.info("Seeded canonical skill: %s (%s)", skill_data["name"], skill_data["id"])
        else:
            existing.name = skill_data["name"]
            existing.category = skill_data["category"]
            existing.description = skill_data["description"]
            existing.synonyms = skill_data["synonyms"]

    await session.flush()

    # 3. Seed Role Requirements
    for req_data in BENCHMARK_REQUIREMENTS:
        existing = await session.scalar(
            select(RoleRequirement).where(
                RoleRequirement.role_id == req_data["role_id"],
                RoleRequirement.skill_id == req_data["skill_id"],
            )
        )
        if not existing:
            req = RoleRequirement(**req_data)
            session.add(req)
            logger.info("Seeded requirement: %s -> %s", req_data["role_id"], req_data["skill_id"])
        else:
            existing.importance = req_data["importance"]
            existing.min_proficiency = req_data["min_proficiency"]
            existing.weight = req_data["weight"]

    await session.commit()
    logger.info("Successfully seeded canonical roles, skills, and benchmark requirements!")


async def main() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        await seed_canonical_data(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
