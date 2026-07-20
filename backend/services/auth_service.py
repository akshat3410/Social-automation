from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from config.settings import get_settings

from .exceptions import UnauthorizedError

ALGORITHM = "HS256"


class AuthService:
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except ValueError:
            return False

    def create_access_token(self, user_id: UUID) -> str:
        settings = get_settings()
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"exp": expire, "sub": str(user_id)}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(token, get_settings().SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise UnauthorizedError("Invalid token")
            return UUID(user_id)
        except (JWTError, ValueError) as exc:
            raise UnauthorizedError("Invalid token") from exc
