import logging

import httpx

from .base import RawResearchItem, ResearchPlugin

logger = logging.getLogger(__name__)


class RedditResearchPlugin(ResearchPlugin):
    """Searches Reddit via the public JSON API (no auth required for search)."""

    name = "reddit"

    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    "https://www.reddit.com/search.json",
                    params={"q": query, "limit": limit, "sort": "relevance", "t": "week"},
                    headers={"User-Agent": "social-engine/1.0 research"},
                )
                response.raise_for_status()
                children = response.json().get("data", {}).get("children", [])
        except httpx.HTTPError as exc:
            logger.warning("Reddit fetch failed: %s", exc)
            return []

        items = []
        for child in children[:limit]:
            post = child.get("data", {})
            title = post.get("title") or ""
            if not title:
                continue
            items.append(
                RawResearchItem(
                    title=title[:512],
                    content=(post.get("selftext") or title)[:2000],
                    url=f"https://www.reddit.com{post.get('permalink', '')}",
                    source="reddit",
                    metadata={
                        "subreddit": post.get("subreddit"),
                        "score": post.get("score"),
                        "num_comments": post.get("num_comments"),
                    },
                )
            )
        return items
