from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .common import UUIDStr


class ContentIdeaCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    platform: str


class ContentIdeaUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    platform: str | None = None
    status: str | None = None


class ContentIdeaResponse(BaseModel):
    id: UUIDStr
    title: str
    description: str | None
    platform: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DraftResponse(BaseModel):
    id: UUIDStr
    idea_id: UUIDStr
    content: str
    platform: str
    status: str
    hook: str | None = None
    quality_score: dict[str, Any] | None = None
    scheduled_for: datetime | None = None
    created_at: datetime

    @classmethod
    def from_model(cls, draft: Any, scheduled_for: datetime | None = None) -> "DraftResponse":
        return cls(
            id=draft.id,
            idea_id=draft.idea_id,
            content=draft.content,
            platform=draft.platform.value if hasattr(draft.platform, "value") else draft.platform,
            status=draft.status.value if hasattr(draft.status, "value") else draft.status,
            hook=draft.hook,
            quality_score=draft.quality_score_data,
            scheduled_for=scheduled_for,
            created_at=draft.created_at,
        )


class DraftApprovalRequest(BaseModel):
    scheduled_for: datetime | None = None


class DraftRejectionRequest(BaseModel):
    reason: str = Field(min_length=1)


class GenerateContentRequest(BaseModel):
    num_variations: int | None = Field(default=None, ge=1, le=5)


class TaskQueuedResponse(BaseModel):
    task_id: str
    status: str = "queued"
