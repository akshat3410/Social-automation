from datetime import datetime

from sqlalchemy import select

from models.posting_schedule import ScheduleStatusEnum

from .base import BaseRepository


class ScheduleRepository(BaseRepository):
    async def get_pending_due(self, now: datetime):
        query = select(self.model).where(
            self.model.status == ScheduleStatusEnum.pending,
            self.model.scheduled_at.isnot(None),
            self.model.scheduled_at <= now,
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
