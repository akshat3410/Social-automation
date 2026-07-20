from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.dependencies.auth import get_auth_service, get_current_user
from schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from services.auth_service import AuthService
from uuid import UUID

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    # logic to create user
    return {}

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    # check user
    # for dummy:
    access_token = auth_service.create_access_token(UUID("00000000-0000-0000-0000-000000000000"))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=dict)
async def get_me(current_user: UUID = Depends(get_current_user)):
    return {"id": str(current_user)}
