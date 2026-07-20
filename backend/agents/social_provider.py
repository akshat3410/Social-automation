from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field

TIMEOUT = httpx.Timeout(30.0)


class SocialAccountDTO(BaseModel):
    id: str
    platform: str
    credentials: dict[str, Any] = Field(default_factory=dict)


class PublishResult(BaseModel):
    success: bool
    platform_post_id: str | None = None
    published_at: str | None = None
    error: str | None = None


class MetricsResult(BaseModel):
    likes: int = 0
    reposts: int = 0
    replies: int = 0
    views: int = 0


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)


class SocialProvider(ABC):
    platform: str

    @abstractmethod
    async def publish(
        self, content: str, media: list | None, account: SocialAccountDTO
    ) -> PublishResult:
        ...

    @abstractmethod
    async def fetch_metrics(self, post_id: str, account: SocialAccountDTO) -> MetricsResult:
        ...

    @abstractmethod
    async def validate_content(self, content: str) -> ValidationResult:
        ...


class TwitterProvider(SocialProvider):
    """Twitter/X API v2. Requires an OAuth2 user access token with tweet.write
    scope stored on the social account (credentials['access_token'])."""

    platform = "twitter"
    base_url = "https://api.twitter.com/2"

    async def publish(
        self, content: str, media: list | None, account: SocialAccountDTO
    ) -> PublishResult:
        token = account.credentials.get("access_token")
        if not token:
            return PublishResult(success=False, error="Twitter account has no access token")
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/tweets",
                    json={"text": content},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()
                data = response.json()
                return PublishResult(
                    success=True,
                    platform_post_id=data["data"]["id"],
                    published_at=datetime.now(UTC).isoformat(),
                )
        except httpx.HTTPError as exc:
            return PublishResult(success=False, error=f"Twitter publish failed: {exc}")

    async def fetch_metrics(self, post_id: str, account: SocialAccountDTO) -> MetricsResult:
        token = account.credentials.get("access_token")
        if not token:
            return MetricsResult()
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(
                    f"{self.base_url}/tweets/{post_id}",
                    params={"tweet.fields": "public_metrics"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()
                metrics = response.json()["data"].get("public_metrics", {})
                return MetricsResult(
                    likes=metrics.get("like_count", 0),
                    reposts=metrics.get("retweet_count", 0),
                    replies=metrics.get("reply_count", 0),
                    views=metrics.get("impression_count", 0),
                )
        except httpx.HTTPError:
            return MetricsResult()

    async def validate_content(self, content: str) -> ValidationResult:
        errors = []
        if len(content) > 280:
            errors.append(f"Content exceeds 280 characters ({len(content)})")
        return ValidationResult(is_valid=not errors, errors=errors)


class RedditProvider(SocialProvider):
    """Reddit API. Requires an OAuth token and a target subreddit in the
    account credentials ({'access_token': ..., 'subreddit': ...})."""

    platform = "reddit"
    base_url = "https://oauth.reddit.com"

    async def publish(
        self, content: str, media: list | None, account: SocialAccountDTO
    ) -> PublishResult:
        token = account.credentials.get("access_token")
        subreddit = account.credentials.get("subreddit")
        if not token or not subreddit:
            return PublishResult(
                success=False, error="Reddit account needs access_token and subreddit"
            )
        title = content.splitlines()[0][:250] if content else "Untitled"
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/api/submit",
                    data={
                        "sr": subreddit,
                        "kind": "self",
                        "title": title,
                        "text": content,
                        "api_type": "json",
                    },
                    headers={
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "social-engine/1.0",
                    },
                )
                response.raise_for_status()
                data = response.json()["json"]["data"]
                return PublishResult(
                    success=True,
                    platform_post_id=data.get("name") or data.get("id"),
                    published_at=datetime.now(UTC).isoformat(),
                )
        except (httpx.HTTPError, KeyError) as exc:
            return PublishResult(success=False, error=f"Reddit publish failed: {exc}")

    async def fetch_metrics(self, post_id: str, account: SocialAccountDTO) -> MetricsResult:
        token = account.credentials.get("access_token")
        if not token:
            return MetricsResult()
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(
                    f"{self.base_url}/api/info",
                    params={"id": post_id},
                    headers={
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "social-engine/1.0",
                    },
                )
                response.raise_for_status()
                children = response.json()["data"]["children"]
                if not children:
                    return MetricsResult()
                post = children[0]["data"]
                return MetricsResult(
                    likes=post.get("ups", 0),
                    replies=post.get("num_comments", 0),
                    views=post.get("view_count") or 0,
                )
        except (httpx.HTTPError, KeyError):
            return MetricsResult()

    async def validate_content(self, content: str) -> ValidationResult:
        return ValidationResult(is_valid=bool(content.strip()))


class MockSocialProvider(SocialProvider):
    """Dry-run provider used when no real platform account is configured."""

    platform = "mock"

    def __init__(self, platform: str = "mock"):
        self.platform = platform
        self.calls: list[dict] = []

    async def publish(
        self, content: str, media: list | None, account: SocialAccountDTO
    ) -> PublishResult:
        self.calls.append({"action": "publish", "content": content})
        return PublishResult(
            success=True,
            platform_post_id=f"{self.platform}_mock_{len(self.calls)}",
            published_at=datetime.now(UTC).isoformat(),
        )

    async def fetch_metrics(self, post_id: str, account: SocialAccountDTO) -> MetricsResult:
        self.calls.append({"action": "fetch_metrics", "post_id": post_id})
        return MetricsResult()

    async def validate_content(self, content: str) -> ValidationResult:
        return ValidationResult(is_valid=True)


class SocialProviderRegistry:
    def __init__(self):
        self._providers: dict[str, SocialProvider] = {}

    def register(self, provider: SocialProvider) -> None:
        self._providers[provider.platform] = provider

    def get(self, platform: str) -> SocialProvider | None:
        return self._providers.get(platform)


def build_provider_registry(settings) -> SocialProviderRegistry:
    registry = SocialProviderRegistry()
    if settings.ENABLE_TWITTER:
        registry.register(TwitterProvider())
    if settings.ENABLE_REDDIT:
        registry.register(RedditProvider())
    return registry
