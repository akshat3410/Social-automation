from pydantic import BaseModel, ConfigDict
from .common import UUIDStr
from datetime import datetime

class AnalyticsResponse(BaseModel):
    id: UUIDStr
    post_id: UUIDStr
    likes: int
    shares: int
    comments: int
    impressions: int
    clicks: int
    synced_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AnalyticsSummary(BaseModel):
    total_likes: int
    total_shares: int
    total_comments: int
    total_impressions: int
    total_posts: int

class PerformanceComparison(BaseModel):
    current_period: AnalyticsSummary
    previous_period: AnalyticsSummary
    improvement_percentage: float
