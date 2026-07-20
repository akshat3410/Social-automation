import uuid
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from backend.database.base import Base, UUIDMixin, TimestampMixin

import enum

class SentimentEnum(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class Comment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "comments"

    published_post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("published_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_comment_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    author: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    sentiment: Mapped[SentimentEnum | None] = mapped_column(Enum(SentimentEnum), nullable=True)
    replied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    post = relationship("PublishedPost", back_populates="comments")
