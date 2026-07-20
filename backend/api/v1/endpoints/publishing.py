from fastapi import APIRouter, Depends
from uuid import UUID
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_publishing_service
from services.publishing_service import PublishingService
from schemas.schedule import ScheduleCreate

router = APIRouter()

@router.post("/publish")
async def publish_now(data: ScheduleCreate, current_user: UUID = Depends(get_current_user), publishing_service: PublishingService = Depends(get_publishing_service)):
    return await publishing_service.publish_now(data.draft_id, data.social_account_id, current_user)

@router.post("/schedule")
async def schedule_post(data: ScheduleCreate, current_user: UUID = Depends(get_current_user), publishing_service: PublishingService = Depends(get_publishing_service)):
    return await publishing_service.schedule_post(data.draft_id, data.social_account_id, data.scheduled_at, current_user)

@router.delete("/schedule/{id}")
async def cancel_schedule(id: UUID, current_user: UUID = Depends(get_current_user), publishing_service: PublishingService = Depends(get_publishing_service)):
    return await publishing_service.cancel_schedule(id, current_user)

@router.get("/published")
async def list_published(current_user: UUID = Depends(get_current_user)):
    return []
