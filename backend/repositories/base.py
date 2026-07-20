from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import utc_now

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    def _base_query(self):
        query = select(self.model)
        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))  # type: ignore[attr-defined]
        return query

    async def get(self, id: UUID) -> T | None:
        result = await self.session.execute(
            self._base_query().where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[T]:
        query = self._base_query()
        if filters:
            for k, v in filters.items():
                query = query.where(getattr(self.model, k) == v)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: dict[str, Any]) -> T:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: UUID, obj_in: dict[str, Any]) -> T | None:
        db_obj = await self.get(id)
        if not db_obj:
            return None
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def soft_delete(self, id: UUID) -> bool:
        db_obj = await self.get(id)
        if not db_obj:
            return False
        if hasattr(db_obj, "deleted_at"):
            db_obj.deleted_at = utc_now()  # type: ignore[attr-defined]
            await self.session.commit()
            return True
        return False

    async def hard_delete(self, id: UUID) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        await self.session.commit()
        return result.rowcount > 0  # type: ignore[attr-defined]
