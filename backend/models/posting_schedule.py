import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDMixin


class ScheduleTypeEnum(str, enum.Enum):
    immediate = "immediate"
    scheduled = "scheduled"
    recurring = "recurring"

class ScheduleStatusEnum(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class PostingSchedule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "posting_schedules"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    social_account_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=True, index=True)
    draft_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("drafts.id", ondelete="SET NULL"), nullable=True, index=True)
    schedule_type: Mapped[ScheduleTypeEnum] = mapped_column(Enum(ScheduleTypeEnum), nullable=False)
    cron_expression: Mapped[str | None] = mapped_column(String, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ScheduleStatusEnum] = mapped_column(Enum(ScheduleStatusEnum), default=ScheduleStatusEnum.pending, nullable=False)
    retries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(String, nullable=True)
    job_id: Mapped[str | None] = mapped_column(String, nullable=True)

    social_account = relationship("SocialAccount", back_populates="schedules")
    draft = relationship("Draft", back_populates="schedules")
