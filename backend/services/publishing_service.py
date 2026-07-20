from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.draft import Draft, DraftStatusEnum
from models.posting_schedule import ScheduleStatusEnum, ScheduleTypeEnum
from models.published_post import PublishedPost

from .exceptions import NotFoundError, ValidationError


class PublishingService:
    def __init__(self, schedule_repo, draft_repo, session: AsyncSession):
        self.schedule_repo = schedule_repo
        self.draft_repo = draft_repo
        self.session = session

    async def _get_owned_draft(self, draft_id: UUID, user_id: UUID) -> Draft:
        draft = await self.draft_repo.get(draft_id)
        if not draft or draft.user_id != user_id:
            raise NotFoundError("Draft not found")
        return draft

    async def publish_now(self, draft_id: UUID, user_id: UUID) -> str:
        draft = await self._get_owned_draft(draft_id, user_id)
        if draft.status not in (DraftStatusEnum.approved, DraftStatusEnum.pending):
            raise ValidationError(f"Draft in status '{draft.status.value}' cannot be published")
        schedule = await self.schedule_repo.create(
            {
                "user_id": user_id,
                "draft_id": draft.id,
                "schedule_type": ScheduleTypeEnum.immediate,
                "status": ScheduleStatusEnum.pending,
            }
        )
        from tasks.content_tasks import publish_task

        message = publish_task.send(str(schedule.id))
        return message.message_id

    async def schedule_post(self, draft_id: UUID, scheduled_for: datetime, user_id: UUID):
        draft = await self._get_owned_draft(draft_id, user_id)
        return await self.schedule_repo.create(
            {
                "user_id": user_id,
                "draft_id": draft.id,
                "schedule_type": ScheduleTypeEnum.scheduled,
                "scheduled_at": scheduled_for,
                "status": ScheduleStatusEnum.pending,
            }
        )

    async def list_scheduled(self, user_id: UUID):
        return await self.schedule_repo.get_multi(
            filters={"user_id": user_id, "status": ScheduleStatusEnum.pending}
        )

    async def cancel_schedule(self, schedule_id: UUID, user_id: UUID) -> bool:
        schedule = await self.schedule_repo.get(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return False
        await self.schedule_repo.update(schedule_id, {"status": ScheduleStatusEnum.cancelled})
        return True

    async def list_published(self, user_id: UUID, limit: int = 100):
        query = (
            select(PublishedPost)
            .join(Draft, PublishedPost.draft_id == Draft.id)
            .where(Draft.user_id == user_id)
            .order_by(PublishedPost.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
