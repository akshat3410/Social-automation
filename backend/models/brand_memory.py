import enum
import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TimestampMixin, UUIDMixin
from models.social_account import PlatformEnum


class MemoryTypeEnum(str, enum.Enum):
    tweet = "tweet"
    reddit_post = "reddit_post"
    hook = "hook"
    style = "style"
    product_info = "product_info"
    feature = "feature"

class BrandMemory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "brand_memories"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[MemoryTypeEnum] = mapped_column(Enum(MemoryTypeEnum), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[Any | None] = mapped_column(Vector(1536), nullable=True)
    performance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    platform: Mapped[PlatformEnum | None] = mapped_column(Enum(PlatformEnum), nullable=True)
