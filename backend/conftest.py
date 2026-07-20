"""Pytest configuration: provide required settings before any app import."""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost:65432/test_db"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:65379/0")
os.environ.setdefault("AI_API_KEY", "test-ai-key")
os.environ.setdefault("DEBUG", "False")
