#!/usr/bin/env bash
set -e

echo "=== CoachPath Backend Startup ==="
PORT="${PORT:-8000}"

# Run Alembic migrations with retry in case Neon is waking up from serverless suspend
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations with Alembic..."
    MAX_RETRIES=3
    for i in $(seq 1 $MAX_RETRIES); do
        if alembic upgrade head; then
            echo "Database migrations completed successfully."
            break
        else
            echo "Migration attempt $i of $MAX_RETRIES failed. Retrying in 3 seconds..."
            if [ "$i" -eq "$MAX_RETRIES" ]; then
                echo "Warning: Migrations did not complete after $MAX_RETRIES attempts. Proceeding with application startup..."
            else
                sleep 3
            fi
        fi
    done
else
    echo "Warning: DATABASE_URL not set in environment. Skipping migrations."
fi

echo "Starting Uvicorn server on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
