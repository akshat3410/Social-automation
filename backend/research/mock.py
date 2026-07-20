from .base import RawResearchItem, ResearchPlugin


class MockResearchPlugin(ResearchPlugin):
    name = "mock"
    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        return [RawResearchItem(title="Mock", content="Mock", url="http://mock.com", source="mock")]
