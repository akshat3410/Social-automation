import asyncio
import logging

import feedparser

from .base import RawResearchItem, ResearchPlugin

logger = logging.getLogger(__name__)

DEFAULT_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://dev.to/feed",
]


class RSSPlugin(ResearchPlugin):
    """Parses configured RSS feeds and filters entries by the query terms."""

    name = "rss"

    def __init__(self, feeds: list[str] | None = None):
        self.feeds = feeds or DEFAULT_FEEDS

    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        terms = [t.lower() for t in query.split() if t]
        items: list[RawResearchItem] = []
        for feed_url in self.feeds:
            try:
                # feedparser is synchronous; run it off the event loop.
                parsed = await asyncio.to_thread(feedparser.parse, feed_url)
            except Exception as exc:
                logger.warning("RSS fetch failed for %s: %s", feed_url, exc)
                continue
            for entry in parsed.entries:
                title = getattr(entry, "title", "")
                summary = getattr(entry, "summary", "")
                haystack = f"{title} {summary}".lower()
                if terms and not any(term in haystack for term in terms):
                    continue
                items.append(
                    RawResearchItem(
                        title=title[:512],
                        content=summary[:2000] or title,
                        url=getattr(entry, "link", ""),
                        source="rss",
                    )
                )
                if len(items) >= limit:
                    return items
        return items
