from .base import ResearchPlugin, RawResearchItem

class RSSPlugin(ResearchPlugin):
    name = "rss"
    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        return []
