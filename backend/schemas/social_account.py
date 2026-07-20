from pydantic import BaseModel, ConfigDict
from .common import UUIDStr
from datetime import datetime

class SocialAccountCreate(BaseModel):
    platform: str
    account_name: str
    access_token: str
    refresh_token: str | None = None
    metadata_json: dict | None = None

class SocialAccountResponse(BaseModel):
    id: UUIDStr
    user_id: UUIDStr
    platform: str
    account_name: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
