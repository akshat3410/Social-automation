from uuid import UUID

from sqlalchemy import func, select

from models.draft import Draft
from models.published_post import PublishedPost

from .base import BaseRepository


class AnalyticsRepository(BaseRepository):
    async def get_by_published_post(self, published_post_id: UUID):
        result = await self.session.execute(
            select(self.model).where(self.model.published_post_id == published_post_id)
        )
        return result.scalar_one_or_none()

    async def get_user_summary(self, user_id: UUID):
        query = (
            select(
                func.count(self.model.id).label("posts"),
                func.sum(self.model.views).label("views"),
                func.sum(self.model.likes).label("likes"),
                func.sum(self.model.replies).label("replies"),
                func.sum(self.model.reposts).label("reposts"),
            )
            .join(PublishedPost, self.model.published_post_id == PublishedPost.id)
            .join(Draft, PublishedPost.draft_id == Draft.id)
            .where(Draft.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.one()

    async def get_user_post_analytics(self, user_id: UUID, limit: int = 50):
        query = (
            select(self.model, PublishedPost)
            .join(PublishedPost, self.model.published_post_id == PublishedPost.id)
            .join(Draft, PublishedPost.draft_id == Draft.id)
            .where(Draft.user_id == user_id)
            .order_by(PublishedPost.published_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [(analytics, post) for analytics, post in result.all()]
