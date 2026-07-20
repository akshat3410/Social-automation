from .base import ResearchPlugin, RawResearchItem

class RedditResearchPlugin(ResearchPlugin):
    name = "reddit"
    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        return []
