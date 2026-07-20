from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
from services.auth_service import AuthService
from services.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_auth_service() -> AuthService:
    return AuthService()

async def get_current_user(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)) -> UUID:
    try:
        user_id = auth_service.verify_token(token)
        return user_id
    except UnauthorizedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_superuser(current_user: UUID = Depends(get_current_user)):
    # logic to verify if user is superuser
    return current_user
