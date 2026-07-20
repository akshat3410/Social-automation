"""Seed the database with demo data.

Run from backend/ with its virtualenv active:
    python ../scripts/seed_data.py
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy import select  # noqa: E402

from database.session import create_task_engine_and_factory  # noqa: E402
from models.content_idea import ContentIdea, IdeaStatusEnum  # noqa: E402
from models.draft import Draft, DraftStatusEnum  # noqa: E402
from models.social_account import PlatformEnum  # noqa: E402
from models.user import User  # noqa: E402
from services.auth_service import AuthService  # noqa: E402

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo-password-123"

IDEAS = [
    ("Why AI agents fail in production", "twitter"),
    ("Postgres as a vector database", "twitter"),
    ("Lessons from self-hosting everything", "reddit"),
]

DRAFTS = [
    "Most AI agent demos die in production. The gap isn't the model — it's error "
    "handling, retries, and observability. Build the boring parts first.",
    "You probably don't need a dedicated vector DB. Postgres + pgvector handles "
    "millions of embeddings with one operational surface. Boring tech wins again.",
]


async def seed() -> None:
    engine, factory = create_task_engine_and_factory()
    try:
        async with factory() as session:
            existing = await session.execute(select(User).where(User.email == DEMO_EMAIL))
            if existing.scalar_one_or_none():
                print(f"Demo user {DEMO_EMAIL} already exists — nothing to do.")
                return

            auth = AuthService()
            user = User(
                email=DEMO_EMAIL,
                username="demo",
                hashed_password=auth.hash_password(DEMO_PASSWORD),
                is_active=True,
                is_superuser=True,
            )
            session.add(user)
            await session.flush()

            ideas = []
            for index, (title, platform) in enumerate(IDEAS):
                idea = ContentIdea(
                    user_id=user.id,
                    title=title,
                    description=f"Seeded demo idea #{index + 1}",
                    platform=PlatformEnum(platform),
                    status=IdeaStatusEnum.completed if index < 2 else IdeaStatusEnum.pending,
                )
                session.add(idea)
                ideas.append(idea)
            await session.flush()

            for index, content in enumerate(DRAFTS):
                session.add(
                    Draft(
                        idea_id=ideas[index].id,
                        user_id=user.id,
                        platform=ideas[index].platform,
                        content=content,
                        hook="Bold claim" if index == 0 else "Contrarian take",
                        variation_index=1,
                        status=DraftStatusEnum.pending,
                        quality_score_data={
                            "originality": 0.82,
                            "hook_strength": 0.78,
                            "engagement_predicted": 0.74,
                            "spam_probability": 0.05,
                            "readability_score": 0.9,
                            "brand_consistency": 0.85,
                            "human_score": 0.88,
                            "passed": True,
                        },
                        created_at=datetime.now(timezone.utc) - timedelta(hours=index),
                    )
                )
            await session.commit()

            print(f"Created user {DEMO_EMAIL} (password: {DEMO_PASSWORD}, superuser)")
            print(f"Created {len(IDEAS)} content ideas and {len(DRAFTS)} pending drafts")
            print("Log in to the dashboard with the demo credentials to explore.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
