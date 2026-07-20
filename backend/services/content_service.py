from datetime import datetime
from uuid import UUID

from models.content_idea import IdeaStatusEnum
from models.draft import DraftStatusEnum
from models.posting_schedule import ScheduleStatusEnum, ScheduleTypeEnum

from .exceptions import NotFoundError, ValidationError


class ContentService:
    def __init__(self, idea_repo, draft_repo, schedule_repo=None):
        self.idea_repo = idea_repo
        self.draft_repo = draft_repo
        self.schedule_repo = schedule_repo

    async def create_idea(self, user_id: UUID, data: dict):
        data["user_id"] = user_id
        return await self.idea_repo.create(data)

    async def list_ideas(
        self, user_id: UUID, status: str | None = None, skip: int = 0, limit: int = 100
    ):
        filters: dict = {"user_id": user_id}
        if status:
            filters["status"] = status
        return await self.idea_repo.get_multi(skip=skip, limit=limit, filters=filters)

    async def get_idea(self, idea_id: UUID, user_id: UUID):
        idea = await self.idea_repo.get(idea_id)
        if not idea or idea.user_id != user_id:
            raise NotFoundError("Idea not found")
        return idea

    async def run_research(self, idea_id: UUID, user_id: UUID) -> str:
        idea = await self.get_idea(idea_id, user_id)
        await self.idea_repo.update(idea.id, {"status": IdeaStatusEnum.researching})
        from tasks.content_tasks import run_research_task

        message = run_research_task.send(str(idea_id), str(user_id))
        return message.message_id

    async def generate_drafts(
        self, idea_id: UUID, user_id: UUID, num_variations: int | None = None
    ) -> str:
        idea = await self.get_idea(idea_id, user_id)
        await self.idea_repo.update(idea.id, {"status": IdeaStatusEnum.generating})
        from tasks.content_tasks import generate_drafts_task

        message = generate_drafts_task.send(str(idea_id), str(user_id), num_variations)
        return message.message_id

    async def list_drafts(
        self, user_id: UUID, status: str | None = None, skip: int = 0, limit: int = 100
    ):
        filters: dict = {"user_id": user_id}
        if status:
            filters["status"] = status
        return await self.draft_repo.get_multi(skip=skip, limit=limit, filters=filters)

    async def get_draft(self, draft_id: UUID, user_id: UUID):
        draft = await self.draft_repo.get(draft_id)
        if not draft or draft.user_id != user_id:
            raise NotFoundError("Draft not found")
        return draft

    async def approve_draft(
        self, draft_id: UUID, user_id: UUID, scheduled_for: datetime | None = None
    ):
        draft = await self.get_draft(draft_id, user_id)
        updated = await self.draft_repo.update(draft.id, {"status": DraftStatusEnum.approved})
        if scheduled_for is not None:
            if self.schedule_repo is None:
                raise ValidationError("Scheduling is not available")
            await self.schedule_repo.create(
                {
                    "user_id": user_id,
                    "draft_id": draft.id,
                    "schedule_type": ScheduleTypeEnum.scheduled,
                    "scheduled_at": scheduled_for,
                    "status": ScheduleStatusEnum.pending,
                }
            )
        return updated, scheduled_for

    async def reject_draft(self, draft_id: UUID, user_id: UUID, reason: str):
        draft = await self.get_draft(draft_id, user_id)
        quality = dict(draft.quality_score_data or {})
        quality["rejection_reason"] = reason
        return await self.draft_repo.update(
            draft.id, {"status": DraftStatusEnum.rejected, "quality_score_data": quality}
        )
