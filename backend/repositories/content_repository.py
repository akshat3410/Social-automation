from uuid import UUID

from .base import BaseRepository


class ContentIdeaRepository(BaseRepository):
    async def get_ideas_by_user(
        self, user_id: UUID, status: str | None = None, platform: str | None = None
    ):
        query = self._base_query().where(self.model.user_id == user_id)
        if status:
            query = query.where(self.model.status == status)
        if platform:
            query = query.where(self.model.platform == platform)
        result = await self.session.execute(query)
        return list(result.scalars().all())
