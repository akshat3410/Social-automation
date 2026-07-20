from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .common import UUIDStr


class PublishNowRequest(BaseModel):
    draft_id: UUIDStr


class ScheduleCreate(BaseModel):
    draft_id: UUIDStr
    scheduled_for: datetime


class ScheduleResponse(BaseModel):
    id: UUIDStr
    draft_id: UUIDStr | None
    scheduled_for: datetime | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class PublishedPostResponse(BaseModel):
    id: UUIDStr
    draft_id: UUIDStr
    platform: str
    platform_post_id: str | None
    url: str | None = None
    published_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
