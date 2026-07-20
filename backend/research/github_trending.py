import logging
from datetime import UTC, datetime, timedelta

import httpx

from .base import RawResearchItem, ResearchPlugin

logger = logging.getLogger(__name__)


class GitHubTrendingPlugin(ResearchPlugin):
    """Finds recently-popular repositories via the GitHub search API."""

    name = "github_trending"

    async def fetch(self, query: str, limit: int) -> list[RawResearchItem]:
        since = (datetime.now(UTC) - timedelta(days=14)).date().isoformat()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    "https://api.github.com/search/repositories",
                    params={
                        "q": f"{query} created:>{since}",
                        "sort": "stars",
                        "order": "desc",
                        "per_page": limit,
                    },
                    headers={"Accept": "application/vnd.github+json"},
                )
                response.raise_for_status()
                repos = response.json().get("items", [])
        except httpx.HTTPError as exc:
            logger.warning("GitHub trending fetch failed: %s", exc)
            return []

        return [
            RawResearchItem(
                title=repo.get("full_name", "")[:512],
                content=(repo.get("description") or repo.get("full_name", ""))[:2000]
                + f" (⭐ {repo.get('stargazers_count', 0)})",
                url=repo.get("html_url", ""),
                source="github",
            )
            for repo in repos[:limit]
            if repo.get("full_name")
        ]
