import uuid
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, Boolean, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from backend.database.base import Base, UUIDMixin, TimestampMixin

class QualityScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quality_scores"

    draft_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, unique=True)
    originality: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    hook_strength: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    engagement_predicted: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    spam_probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    readability_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    brand_consistency: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    human_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    grammar_issues: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    duplicate_similarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String, nullable=True)

    draft = relationship("Draft", back_populates="quality_score_obj")
