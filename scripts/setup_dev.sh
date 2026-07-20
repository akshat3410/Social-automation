#!/bin/bash
# Local development setup: Postgres/Redis in Docker, backend in a venv.
# For the full stack in Docker, just run: docker compose up -d
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Setting up Social Engine development environment..."

if ! command -v docker &> /dev/null; then
    echo "Error: docker not found. Please install Docker." >&2
    exit 1
fi
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running." >&2
    exit 1
fi

# --- .env ------------------------------------------------------------------
if [ ! -f .env ]; then
    cp .env.example .env
    # Generate a real secret instead of shipping the placeholder.
    if command -v openssl &> /dev/null; then
        SECRET=$(openssl rand -hex 32)
        sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=${SECRET}/" .env && rm -f .env.bak
        echo "Created .env with a generated SECRET_KEY"
    else
        echo "Created .env — replace SECRET_KEY manually (openssl not found)"
    fi
    echo ">>> Edit .env and set AI_API_KEY before generating content."
else
    echo ".env already exists, leaving it untouched"
fi

# --- Infrastructure --------------------------------------------------------
echo "Starting PostgreSQL and Redis..."
docker compose up -d postgres redis

# --- Python environment ----------------------------------------------------
cd backend
if [ ! -d .venv ]; then
    echo "Creating virtualenv..."
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
echo "Installing backend dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements-dev.txt

echo "Waiting for PostgreSQL to accept connections..."
for _ in $(seq 1 30); do
    if docker compose -f ../docker-compose.yml exec -T postgres pg_isready -q 2>/dev/null; then
        break
    fi
    sleep 1
done

echo "Running database migrations..."
alembic upgrade head
cd ..

echo ""
echo "✨ Ready!"
echo "  Backend:   cd backend && source .venv/bin/activate && uvicorn main:app --reload"
echo "  Worker:    cd backend && source .venv/bin/activate && python -m dramatiq tasks.content_tasks"
echo "  Scheduler: cd backend && source .venv/bin/activate && python -m workers.scheduler"
echo "  Frontend:  cd frontend && npm install && npm run dev"
echo "  Seed data: cd backend && source .venv/bin/activate && python ../scripts/seed_data.py"
