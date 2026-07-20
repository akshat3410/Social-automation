from uuid import UUID

from sqlalchemy import select

from .base import BaseRepository


class MemoryRepository(BaseRepository):
    async def search_by_embedding(
        self, embedding: list[float], user_id: UUID, limit: int, threshold: float
    ) -> list[tuple]:
        """Return (memory, similarity) tuples above the similarity threshold."""
        distance = self.model.embedding.cosine_distance(embedding).label("distance")
        query = (
            select(self.model, distance)
            .where(
                self.model.user_id == user_id,
                self.model.embedding.isnot(None),
                distance < (1 - threshold),
            )
            .order_by(distance)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [(row, 1.0 - float(dist)) for row, dist in result.all()]
