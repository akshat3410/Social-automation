from uuid import UUID
from sqlalchemy import select
from .base import BaseRepository

class DraftRepository(BaseRepository):
    async def get_by_status(self, status: str, user_id: UUID, idea_model: type):
        query = select(self.model).join(idea_model).where(
            idea_model.user_id == user_id,
            self.model.status == status
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_with_quality_score(self, draft_id: UUID):
        result = await self.session.execute(select(self.model).where(self.model.id == draft_id))
        return result.scalar_one_or_none()
