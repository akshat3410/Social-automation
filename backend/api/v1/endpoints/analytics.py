from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.dependencies.auth import get_current_user
from api.dependencies.services import get_analytics_service
from models.user import User
from schemas.analytics import AnalyticsSummary, PostAnalyticsItem
from schemas.content import TaskQueuedResponse
from services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.get_summary(current_user.id)


@router.get("/posts", response_model=list[PostAnalyticsItem])
async def post_analytics(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.get_posts(current_user.id, limit)


@router.post(
    "/sync/{post_id}", response_model=TaskQueuedResponse, status_code=status.HTTP_202_ACCEPTED
)
async def sync_analytics(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    task_id = await analytics_service.sync_analytics(post_id, current_user.id)
    return TaskQueuedResponse(task_id=task_id)
