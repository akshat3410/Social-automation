from typing import Literal
from pydantic import BaseModel
from uuid import UUID

class BrandMemory(BaseModel):
    id: str
    content: str
    type: str
    user_id: UUID
    metadata: dict

class MemorySearchResult(BaseModel):
    content: str
    similarity_score: float
    type: str
    metadata: dict

class MemoryService:
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider

    async def store(self, content: str, type: str, user_id: UUID, metadata: dict) -> BrandMemory:
        embedding = await self.llm_provider.embed(content, "text-embedding-ada-002")
        # In real code, save to pgvector here
        return BrandMemory(
            id="mem_123",
            content=content,
            type=type,
            user_id=user_id,
            metadata=metadata
        )

    async def search_similar(self, query: str, user_id: UUID, limit: int = 5, threshold: float = 0.85) -> list[MemorySearchResult]:
        embedding = await self.llm_provider.embed(query, "text-embedding-ada-002")
        # In real code, query pgvector here
        return []

    async def is_duplicate(self, content: str, user_id: UUID, threshold: float = 0.85) -> bool:
        results = await self.search_similar(content, user_id, limit=1, threshold=threshold)
        return len(results) > 0
