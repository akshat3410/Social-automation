from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TimestampMixin, UUIDMixin


class SubredditProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subreddit_profiles"

    subreddit_name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    rules: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    best_post_times: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    avg_upvotes: Mapped[float | None] = mapped_column(Float, nullable=True)
    posting_karma_required: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
