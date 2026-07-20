from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from .common import UUIDStr

class ContentIdeaCreate(BaseModel):
    topic: str
    platform: str
    notes: str | None = None

class ContentIdeaUpdate(BaseModel):
    topic: str | None = None
    platform: str | None = None
    status: str | None = None
    notes: str | None = None

class ContentIdeaResponse(BaseModel):
    id: UUIDStr
    user_id: UUIDStr
    topic: str
    platform: str
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DraftResponse(BaseModel):
    id: UUIDStr
    idea_id: UUIDStr
    content: str
    status: str
    quality_score: float | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DraftApprovalRequest(BaseModel):
    reason: str | None = None

class ResearchRequest(BaseModel):
    topic: str
    platform: str

class ResearchResponse(BaseModel):
    idea_id: UUIDStr
    summary: str
    sources: list[str] = Field(default_factory=list)

class GenerateContentRequest(BaseModel):
    idea_id: UUIDStr

class GenerateContentResponse(BaseModel):
    drafts: list[DraftResponse]
