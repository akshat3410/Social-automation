from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .common import UUIDStr


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    id: UUIDStr
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
