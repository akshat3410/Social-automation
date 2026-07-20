from fastapi import APIRouter, Depends
from uuid import UUID
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_analytics_service
from services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/summary")
async def get_summary(days: int = 30, current_user: UUID = Depends(get_current_user), analytics_service: AnalyticsService = Depends(get_analytics_service)):
    return await analytics_service.get_summary(current_user, days)

@router.get("/posts")
async def top_performing_posts(limit: int = 10, platform: str = "", current_user: UUID = Depends(get_current_user), analytics_service: AnalyticsService = Depends(get_analytics_service)):
    return await analytics_service.get_top_posts(current_user, limit, platform)

@router.post("/sync/{post_id}")
async def sync_analytics(post_id: UUID, current_user: UUID = Depends(get_current_user), analytics_service: AnalyticsService = Depends(get_analytics_service)):
    return await analytics_service.sync_analytics(post_id, current_user)
