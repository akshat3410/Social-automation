"""Initial schema: all 14 tables + pgvector extension.

This initial migration creates the schema directly from the SQLAlchemy
metadata so it can never drift from the models. Subsequent migrations
should use autogenerate as usual.

Revision ID: 0001
Revises:
Create Date: 2026-07-20
"""
from alembic import op

import models  # noqa: F401 - registers all models on Base.metadata
from database.base import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=False)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
