from abc import ABC, abstractmethod
from pydantic import BaseModel
from datetime import datetime

class RawResearchItem(BaseModel):
    title: str
    content: str
    url: str
    source: str
    published_at: datetime | None = None
    metadata: dict = {}

class ResearchPlugin(ABC):
    name: str
    
    @abstractmethod
    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        pass
