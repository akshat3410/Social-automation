import uuid
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, ForeignKey, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from backend.database.base import Base, UUIDMixin, TimestampMixin
from backend.models.social_account import PlatformEnum

class Analytics(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analytics"

    published_post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("published_posts.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    platform: Mapped[PlatformEnum] = mapped_column(Enum(PlatformEnum), nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    replies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bookmarks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reposts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ctr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    follower_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    post = relationship("PublishedPost", back_populates="analytics")
