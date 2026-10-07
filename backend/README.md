# CoachPath Backend — Python / FastAPI Service

This is the FastAPI backend service for CoachPath, powering the AI-driven career intelligence platform.

---

## 🛠️ Technology Stack
- **Runtime**: Python 3.13+
- **API Framework**: FastAPI 0.115+
- **Data Validation**: Pydantic v2
- **ORM**: SQLAlchemy 2.0 (Async)
- **Database Driver**: `asyncpg` (PostgreSQL)
- **Database Migrations**: Alembic
- **Testing**: Pytest, `pytest-asyncio`, `httpx`, `aiosqlite`

---

## 🚀 Local Development Setup

### 1. Prerequisites
- Python 3.13+
- PostgreSQL 16 with `pgvector` (or Docker)

### 2. Virtual Environment & Dependencies
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` from project root to `.env` in the backend directory or project root:
```bash
cp ../.env.example .env
```

### 4. Running Database Migrations & Seeding
```bash
# Apply migrations to database
alembic upgrade head

# Seed initial canonical benchmark roles and skills taxonomy (development/demo data)
python scripts/seed.py

# Generate a new migration revision
alembic revision -m "add_table_name"
```

### 5. Starting the Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API docs are available at:
- Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- ReDoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
- OpenAPI Specification: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

---

## 🧪 Running Tests
```bash
pytest -v
```
Tests run with an in-memory asynchronous SQLite engine and do not require an active external PostgreSQL instance.

---

## 🐳 Running via Docker Compose
From the root workspace directory:
```bash
docker compose up -d
```
This boots both `db` (PostgreSQL + pgvector) and `backend` (FastAPI).
