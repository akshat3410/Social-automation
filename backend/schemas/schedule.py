from pydantic import BaseModel, ConfigDict
from .common import UUIDStr
from datetime import datetime

class ScheduleCreate(BaseModel):
    draft_id: UUIDStr
    social_account_id: UUIDStr
    scheduled_at: datetime

class ScheduleUpdate(BaseModel):
    scheduled_at: datetime | None = None
    status: str | None = None

class ScheduleResponse(BaseModel):
    id: UUIDStr
    user_id: UUIDStr
    draft_id: UUIDStr
    social_account_id: UUIDStr
    scheduled_at: datetime
    status: str
    job_id: str | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
