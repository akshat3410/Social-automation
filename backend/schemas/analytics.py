from datetime import datetime

from pydantic import BaseModel

from .common import UUIDStr


class AnalyticsSummary(BaseModel):
    total_posts: int
    total_views: int
    total_likes: int
    total_replies: int
    total_reposts: int
    avg_engagement_rate: float


class PostAnalyticsItem(BaseModel):
    post_id: UUIDStr
    content_preview: str
    platform: str
    views: int
    likes: int
    replies: int
    reposts: int
    engagement_rate: float
    published_at: datetime | None
