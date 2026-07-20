from uuid import UUID

from .base import BaseRepository


class DraftRepository(BaseRepository):
    async def get_by_status(self, status: str, user_id: UUID):
        return await self.get_multi(filters={"user_id": user_id, "status": status})
