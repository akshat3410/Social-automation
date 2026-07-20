import uuid
from typing import Any, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from backend.database.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from backend.models.social_account import PlatformEnum

import enum

class IdeaStatusEnum(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    rejected = "rejected"
    published = "published"

class ContentIdea(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "content_ideas"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    research_context: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    platform: Mapped[PlatformEnum] = mapped_column(Enum(PlatformEnum), nullable=False)
    status: Mapped[IdeaStatusEnum] = mapped_column(Enum(IdeaStatusEnum), default=IdeaStatusEnum.draft, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tags: Mapped[List[str] | None] = mapped_column(JSONB, nullable=True)

    user = relationship("User", back_populates="content_ideas")
    drafts = relationship("Draft", back_populates="idea", cascade="all, delete-orphan")
    research_results = relationship("ResearchResult", back_populates="idea", cascade="all, delete-orphan")
