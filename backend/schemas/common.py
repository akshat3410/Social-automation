import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

UUIDStr = str | uuid.UUID

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
    
    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict | None = None

class SuccessResponse(BaseModel):
    success: bool = True
    message: str | None = None
