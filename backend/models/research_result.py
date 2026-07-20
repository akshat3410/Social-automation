import enum
import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDMixin


class SourceEnum(str, enum.Enum):
    github = "github"
    rss = "rss"
    news = "news"
    producthunt = "producthunt"
    hackernews = "hackernews"
    reddit = "reddit"

class ResearchResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_results"

    idea_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("content_ideas.id", ondelete="SET NULL"), nullable=True, index=True)
    source: Mapped[SourceEnum] = mapped_column(Enum(SourceEnum), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    embedding: Mapped[Any | None] = mapped_column(Vector(1536), nullable=True)

    idea = relationship("ContentIdea", back_populates="research_results")
