from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import get_settings
from database.base import Base

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession]:
    """Dependency for providing database sessions to FastAPI endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database tables."""
    import models  # noqa: F401 - ensure all models are registered on Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_task_engine_and_factory():
    """Fresh engine + session factory for background tasks.

    Dramatiq actors bridge into asyncio with asyncio.run(), which creates a
    new event loop per task; the API's pooled engine cannot be shared across
    loops, so tasks build (and must dispose) their own NullPool engine.
    """
    from sqlalchemy.pool import NullPool

    task_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    factory = async_sessionmaker(
        bind=task_engine, class_=AsyncSession, expire_on_commit=False
    )
    return task_engine, factory
