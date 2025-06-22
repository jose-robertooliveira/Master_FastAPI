#!/bin/sh

set -e

echo ">>> Wait for database..."

until uv run python -c "import asyncio; import asyncpg; asyncio.run(asyncpg.connect(dsn='${DATABASE_URL}'))"; do
  echo "Database is not ready yet, run again in 2 seconds..."
  sleep 2
done

echo ">>> Database is ready!"

echo ">>> Alembic migrations..."
uv run alembic upgrade head

echo ">>> Run FastAPI on Uvicorn..."
uv run uvicorn --host 0.0.0.0 --port 8000 fastapi_lesson.app:app
