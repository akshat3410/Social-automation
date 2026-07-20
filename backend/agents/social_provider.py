from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel
import httpx

class SocialAccountDTO(BaseModel):
    id: str
    platform: str
    credentials: dict[str, Any]

class PublishResult(BaseModel):
    success: bool
    platform_post_id: str | None = None
    published_at: str | None = None
    error: str | None = None

class MetricsResult(BaseModel):
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0

class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = []

class SocialProvider(ABC):
    platform: str

    @abstractmethod
    async def publish(self, content: str, media: list | None, account: SocialAccountDTO) -> PublishResult:
        pass

    @abstractmethod
    async def fetch_metrics(self, post_id: str, account: SocialAccountDTO) -> MetricsResult:
        pass

    @abstractmethod
    async def validate_content(self, content: str) -> ValidationResult:
        pass

class TwitterProvider(SocialProvider):
    platform = "twitter"

    async def publish(self, content: str, media: list | None, account: SocialAccountDTO) -> PublishResult:
        return PublishResult(success=True, platform_post_id="tw_123")
        
    async def fetch_metrics(self, post_id: str, account: SocialAccountDTO) -> MetricsResult:
        return MetricsResult(likes=10)

    async def validate_content(self, content: str) -> ValidationResult:
        return ValidationResult(is_valid=len(content) <= 280)

class RedditProvider(SocialProvider):
    platform = "reddit"

    async def publish(self, content: str, media: list | None, account: SocialAccountDTO) -> PublishResult:
        return PublishResult(success=True, platform_post_id="rd_123")
        
    async def fetch_metrics(self, post_id: str, account: SocialAccountDTO) -> MetricsResult:
        return MetricsResult(likes=5)

    async def validate_content(self, content: str) -> ValidationResult:
        return ValidationResult(is_valid=True)

class MockSocialProvider(SocialProvider):
    platform = "mock"

    def __init__(self, platform: str = "mock"):
        self.platform = platform
        self.calls = []

    async def publish(self, content: str, media: list | None, account: SocialAccountDTO) -> PublishResult:
        self.calls.append({"action": "publish", "content": content})
        return PublishResult(success=True, platform_post_id=f"{self.platform}_123")
        
    async def fetch_metrics(self, post_id: str, account: SocialAccountDTO) -> MetricsResult:
        self.calls.append({"action": "fetch_metrics", "post_id": post_id})
        return MetricsResult(likes=42)

    async def validate_content(self, content: str) -> ValidationResult:
        return ValidationResult(is_valid=True)
