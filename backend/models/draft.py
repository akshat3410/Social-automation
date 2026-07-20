import enum
import uuid
from typing import Any

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from models.social_account import PlatformEnum


class ToneEnum(str, enum.Enum):
    professional = "professional"
    casual = "casual"
    humorous = "humorous"
    provocative = "provocative"
    educational = "educational"

class DraftStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    published = "published"

class Draft(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "drafts"

    idea_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_ideas.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[PlatformEnum] = mapped_column(Enum(PlatformEnum), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    hook: Mapped[str | None] = mapped_column(String, nullable=True)
    tone: Mapped[ToneEnum | None] = mapped_column(Enum(ToneEnum), nullable=True)
    variation_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    quality_score_data: Mapped[dict[str, Any] | None] = mapped_column("quality_score", JSONB, nullable=True)
    status: Mapped[DraftStatusEnum] = mapped_column(Enum(DraftStatusEnum), default=DraftStatusEnum.pending, nullable=False)
    ai_model: Mapped[str | None] = mapped_column(String, nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    idea = relationship("ContentIdea", back_populates="drafts")
    published_posts = relationship("PublishedPost", back_populates="draft")
    quality_score_obj = relationship("QualityScore", back_populates="draft", uselist=False)
    schedules = relationship("PostingSchedule", back_populates="draft")
