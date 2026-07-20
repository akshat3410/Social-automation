from uuid import UUID
from sqlalchemy import select
from .base import BaseRepository

class MemoryRepository(BaseRepository):
    async def search_by_embedding(self, embedding: list[float], user_id: UUID, limit: int, threshold: float):
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.embedding.cosine_distance(embedding) < (1 - threshold)
        ).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
