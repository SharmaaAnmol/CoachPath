#!/usr/bin/env bash
set -e

echo "=== CoachPath Backend Startup ==="
echo "Running database migrations with Alembic..."
alembic upgrade head

PORT="${PORT:-8000}"
echo "Starting Uvicorn server on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
