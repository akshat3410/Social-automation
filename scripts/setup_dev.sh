#!/bin/bash
set -e

echo "Setting up Social Engine development environment..."

# Check docker
if ! command -v docker &> /dev/null; then
    echo "Error: docker could not be found. Please install Docker."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running."
    exit 1
fi

# Copy env file
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
    else
        echo "Warning: .env.example not found. Creating blank .env"
        touch .env
    fi
fi

# Start services
echo "Starting PostgreSQL and Redis..."
docker compose up -d postgres redis

# Setup python
if [ -d "backend" ]; then
    echo "Installing backend dependencies..."
    cd backend
    if command -v uv &> /dev/null; then
        uv pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    
    echo "Running migrations..."
    # alembic upgrade head
    cd ..
fi

echo ""
echo "✨ Ready! Run: docker compose up"
