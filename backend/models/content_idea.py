import enum
import uuid
from typing import Any

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from models.social_account import PlatformEnum


class IdeaStatusEnum(str, enum.Enum):
    pending = "pending"
    researching = "researching"
    generating = "generating"
    completed = "completed"
    failed = "failed"

class ContentIdea(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "content_ideas"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    research_context: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    platform: Mapped[PlatformEnum] = mapped_column(Enum(PlatformEnum), nullable=False)
    status: Mapped[IdeaStatusEnum] = mapped_column(Enum(IdeaStatusEnum), default=IdeaStatusEnum.pending, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    user = relationship("User", back_populates="content_ideas")
    drafts = relationship("Draft", back_populates="idea", cascade="all, delete-orphan")
    research_results = relationship("ResearchResult", back_populates="idea", cascade="all, delete-orphan")
