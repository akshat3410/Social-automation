from uuid import UUID

from schemas.analytics import AnalyticsSummary, PostAnalyticsItem


class AnalyticsService:
    def __init__(self, analytics_repo):
        self.analytics_repo = analytics_repo

    async def sync_analytics(self, published_post_id: UUID, user_id: UUID) -> str:
        from tasks.content_tasks import sync_analytics_task

        message = sync_analytics_task.send(str(published_post_id))
        return message.message_id

    async def get_summary(self, user_id: UUID) -> AnalyticsSummary:
        row = await self.analytics_repo.get_user_summary(user_id)
        total_views = int(row.views or 0)
        interactions = int(row.likes or 0) + int(row.replies or 0) + int(row.reposts or 0)
        return AnalyticsSummary(
            total_posts=int(row.posts or 0),
            total_views=total_views,
            total_likes=int(row.likes or 0),
            total_replies=int(row.replies or 0),
            total_reposts=int(row.reposts or 0),
            avg_engagement_rate=round(interactions / total_views, 4) if total_views else 0.0,
        )

    async def get_posts(self, user_id: UUID, limit: int = 50) -> list[PostAnalyticsItem]:
        rows = await self.analytics_repo.get_user_post_analytics(user_id, limit)
        items = []
        for analytics, post in rows:
            views = analytics.views or 0
            interactions = (
                (analytics.likes or 0) + (analytics.replies or 0) + (analytics.reposts or 0)
            )
            items.append(
                PostAnalyticsItem(
                    post_id=post.id,
                    content_preview=post.content[:120],
                    platform=post.platform.value,
                    views=views,
                    likes=analytics.likes or 0,
                    replies=analytics.replies or 0,
                    reposts=analytics.reposts or 0,
                    engagement_rate=round(interactions / views, 4) if views else 0.0,
                    published_at=post.published_at,
                )
            )
        return items
