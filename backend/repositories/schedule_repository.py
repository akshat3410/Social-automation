from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from .base import BaseRepository

class ScheduleRepository(BaseRepository):
    async def get_pending_due(self, now: datetime):
        query = select(self.model).where(
            self.model.status == "pending",
            self.model.scheduled_at <= now
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_job_id(self, job_id: str):
        result = await self.session.execute(select(self.model).where(self.model.job_id == job_id))
        return result.scalar_one_or_none()
