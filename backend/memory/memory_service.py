import logging
from uuid import UUID

from pydantic import BaseModel

from config.settings import get_settings
from models.brand_memory import BrandMemory, MemoryTypeEnum
from repositories.memory_repository import MemoryRepository

logger = logging.getLogger(__name__)


class MemorySearchResult(BaseModel):
    content: str
    similarity_score: float
    type: str


class MemoryService:
    """Semantic brand memory backed by pgvector.

    Degrades gracefully: when embeddings are not configured (no
    EMBEDDINGS_API_KEY), store/search become no-ops and duplicate
    detection reports no duplicates.
    """

    def __init__(self, llm_provider, memory_repo: MemoryRepository):
        self.llm_provider = llm_provider
        self.memory_repo = memory_repo
        self.settings = get_settings()

    async def _embed(self, text: str) -> list[float] | None:
        try:
            return await self.llm_provider.embed(text, self.settings.EMBEDDINGS_MODEL)
        except NotImplementedError:
            return None
        except Exception as exc:
            logger.warning("Embedding failed; memory feature degraded: %s", exc)
            return None

    async def store(
        self, content: str, type: str, user_id: UUID | str, metadata: dict | None = None
    ) -> BrandMemory | None:
        embedding = await self._embed(content)
        if embedding is None:
            return None
        memory = BrandMemory(
            user_id=UUID(str(user_id)),
            type=MemoryTypeEnum(type),
            content=content,
            embedding=embedding,
            tags=list((metadata or {}).values()) or None,
        )
        self.memory_repo.session.add(memory)
        await self.memory_repo.session.commit()
        return memory

    async def search_similar(
        self, query: str, user_id: UUID | str, limit: int = 5, threshold: float | None = None
    ) -> list[MemorySearchResult]:
        threshold = threshold if threshold is not None else self.settings.MEMORY_SIMILARITY_THRESHOLD
        embedding = await self._embed(query)
        if embedding is None:
            return []
        rows = await self.memory_repo.search_by_embedding(
            embedding, UUID(str(user_id)), limit, threshold
        )
        return [
            MemorySearchResult(
                content=row.content, similarity_score=similarity, type=row.type.value
            )
            for row, similarity in rows
        ]

    async def max_similarity(self, content: str, user_id: UUID | str) -> float:
        """Return an approximate max similarity of content vs stored memories."""
        results = await self.search_similar(content, user_id, limit=1)
        return results[0].similarity_score if results else 0.0
