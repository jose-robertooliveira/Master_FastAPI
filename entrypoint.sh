#!/bin/sh

set -e

echo ">>> Executando migrações Alembic..."
uv run alembic upgrade head

echo ">>> Subindo FastAPI no Uvicorn..."
uv run uvicorn --host 0.0.0.0 --port 8000 fastapi_lesson.app:app
