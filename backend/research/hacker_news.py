import logging
from datetime import datetime

import httpx

from .base import RawResearchItem, ResearchPlugin

logger = logging.getLogger(__name__)


class HackerNewsPlugin(ResearchPlugin):
    """Searches Hacker News via the public Algolia API."""

    name = "hacker_news"

    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={"query": query, "tags": "story", "hitsPerPage": limit},
                )
                response.raise_for_status()
                hits = response.json().get("hits", [])
        except httpx.HTTPError as exc:
            logger.warning("HackerNews fetch failed: %s", exc)
            return []

        items = []
        for hit in hits[:limit]:
            title = hit.get("title") or ""
            if not title:
                continue
            created = hit.get("created_at")
            items.append(
                RawResearchItem(
                    title=title,
                    content=f"{title} ({hit.get('points', 0)} points, "
                    f"{hit.get('num_comments', 0)} comments)",
                    url=hit.get("url")
                    or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    source="hackernews",
                    published_at=datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if created
                    else None,
                )
            )
        return items
