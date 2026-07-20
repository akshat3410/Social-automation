from .base import ResearchPlugin, RawResearchItem

class GitHubTrendingPlugin(ResearchPlugin):
    name = "github_trending"
    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        return []
