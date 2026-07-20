import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum, DateTime, Index
from backend.database.base import Base, UUIDMixin, TimestampMixin
from backend.models.social_account import PlatformEnum

import enum

class PublishStatusEnum(str, enum.Enum):
    success = "success"
    failed = "failed"
    pending = "pending"

class PublishedPost(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "published_posts"

    draft_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, index=True)
    social_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_post_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    platform: Mapped[PlatformEnum] = mapped_column(Enum(PlatformEnum), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[PublishStatusEnum] = mapped_column(Enum(PublishStatusEnum), nullable=False)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    draft = relationship("Draft", back_populates="published_posts")
    social_account = relationship("SocialAccount", back_populates="published_posts")
    analytics = relationship("Analytics", back_populates="post", uselist=False)
    comments = relationship("Comment", back_populates="post")
