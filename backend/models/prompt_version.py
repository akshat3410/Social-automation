import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Enum
from backend.database.base import Base, UUIDMixin, TimestampMixin

import enum

class AgentNameEnum(str, enum.Enum):
    researcher = "researcher"
    writer = "writer"
    editor = "editor"
    reviewer = "reviewer"
    analyzer = "analyzer"

class PromptVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "prompt_versions"

    agent_name: Mapped[AgentNameEnum] = mapped_column(Enum(AgentNameEnum), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    performance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
