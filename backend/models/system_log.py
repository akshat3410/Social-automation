import uuid
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from backend.database.base import Base, UUIDMixin, TimestampMixin

import enum

class LogLevelEnum(str, enum.Enum):
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"
    debug = "debug"

class ComponentEnum(str, enum.Enum):
    api = "api"
    agent = "agent"
    worker = "worker"
    research = "research"
    publishing = "publishing"

class SystemLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "system_logs"

    level: Mapped[LogLevelEnum] = mapped_column(Enum(LogLevelEnum), nullable=False)
    component: Mapped[ComponentEnum] = mapped_column(Enum(ComponentEnum), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String, nullable=False)
    request_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
