from uuid import UUID
from sqlalchemy import select
from .base import BaseRepository

class UserRepository(BaseRepository):
    async def get_by_email(self, email: str):
        result = await self.session.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str):
        result = await self.session.execute(select(self.model).where(self.model.username == username))
        return result.scalar_one_or_none()
