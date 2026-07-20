from uuid import UUID
from datetime import datetime
from .exceptions import PublishingError

class PublishingService:
    def __init__(self, schedule_repo, draft_repo):
        self.schedule_repo = schedule_repo
        self.draft_repo = draft_repo

    async def publish_now(self, draft_id: UUID, social_account_id: UUID, user_id: UUID):
        pass

    async def schedule_post(self, draft_id: UUID, social_account_id: UUID, scheduled_at: datetime, user_id: UUID):
        data = {
            "draft_id": draft_id,
            "social_account_id": social_account_id,
            "scheduled_at": scheduled_at,
            "user_id": user_id,
            "status": "pending"
        }
        return await self.schedule_repo.create(data)

    async def cancel_schedule(self, schedule_id: UUID, user_id: UUID) -> bool:
        schedule = await self.schedule_repo.get(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return False
        await self.schedule_repo.update(schedule_id, {"status": "cancelled"})
        return True
