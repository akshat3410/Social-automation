from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select

from api.dependencies.auth import get_auth_service, get_current_user, get_user_repository
from api.dependencies.rate_limit import auth_rate_limit
from models.user import User
from repositories.user_repository import UserRepository
from schemas.user import TokenResponse, UserCreate, UserResponse
from services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_rate_limit())],
)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository),
):
    if await user_repo.get_by_email(user_in.email):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    if await user_repo.get_by_username(user_in.username):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Username already taken")

    # The first registered user becomes the admin of this self-hosted instance.
    result = await user_repo.session.execute(select(func.count(User.id)))
    is_first_user = int(result.scalar_one()) == 0

    return await user_repo.create(
        {
            "email": user_in.email,
            "username": user_in.username,
            "hashed_password": auth_service.hash_password(user_in.password),
            "is_active": True,
            "is_superuser": is_first_user,
        }
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(auth_rate_limit())],
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository),
):
    user = await user_repo.get_by_email(form_data.username) or await user_repo.get_by_username(
        form_data.username
    )
    if (
        user is None
        or not user.is_active
        or not auth_service.verify_password(form_data.password, user.hashed_password)
    ):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=auth_service.create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
