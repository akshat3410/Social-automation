from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import get_current_user
from api.dependencies.services import get_publishing_service
from models.user import User
from schemas.content import TaskQueuedResponse
from schemas.schedule import (
    PublishedPostResponse,
    PublishNowRequest,
    ScheduleCreate,
    ScheduleResponse,
)
from services.publishing_service import PublishingService

router = APIRouter()


def _schedule_response(schedule) -> ScheduleResponse:
    return ScheduleResponse(
        id=schedule.id,
        draft_id=schedule.draft_id,
        scheduled_for=schedule.scheduled_at,
        status=schedule.status.value,
    )


@router.post("/publish", response_model=TaskQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
async def publish_now(
    data: PublishNowRequest,
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(get_publishing_service),
):
    task_id = await publishing_service.publish_now(UUID(str(data.draft_id)), current_user.id)
    return TaskQueuedResponse(task_id=task_id)


@router.post("/schedule", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def schedule_post(
    data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(get_publishing_service),
):
    schedule = await publishing_service.schedule_post(
        UUID(str(data.draft_id)), data.scheduled_for, current_user.id
    )
    return _schedule_response(schedule)


@router.get("/scheduled", response_model=list[ScheduleResponse])
async def list_scheduled(
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(get_publishing_service),
):
    schedules = await publishing_service.list_scheduled(current_user.id)
    return [_schedule_response(s) for s in schedules]


@router.delete("/schedule/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_schedule(
    schedule_id: UUID,
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(get_publishing_service),
):
    cancelled = await publishing_service.cancel_schedule(schedule_id, current_user.id)
    if not cancelled:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Schedule not found")


@router.get("/published", response_model=list[PublishedPostResponse])
async def list_published(
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(get_publishing_service),
):
    posts = await publishing_service.list_published(current_user.id)
    return [
        PublishedPostResponse(
            id=p.id,
            draft_id=p.draft_id,
            platform=p.platform.value,
            platform_post_id=p.platform_post_id,
            url=(p.raw_url if hasattr(p, "raw_url") else None),
            published_at=p.published_at,
        )
        for p in posts
    ]
