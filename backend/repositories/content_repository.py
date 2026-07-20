from uuid import UUID
from sqlalchemy import select
from .base import BaseRepository

class ContentIdeaRepository(BaseRepository):
    async def get_ideas_by_user(self, user_id: UUID, status: str | None = None, platform: str | None = None):
        query = select(self.model).where(self.model.user_id == user_id)
        if status:
            query = query.where(self.model.status == status)
        if platform:
            query = query.where(self.model.platform == platform)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_drafts_by_idea(self, idea_id: UUID, draft_model: type):
        result = await self.session.execute(select(draft_model).where(draft_model.idea_id == idea_id))
        return list(result.scalars().all())

    async def get_pending_drafts(self, user_id: UUID, draft_model: type, idea_model: type):
        query = select(draft_model).join(idea_model).where(
            idea_model.user_id == user_id,
            draft_model.status == "pending_approval"
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
