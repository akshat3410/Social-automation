from uuid import UUID

class AnalyticsService:
    def __init__(self, analytics_repo):
        self.analytics_repo = analytics_repo

    async def sync_analytics(self, published_post_id: UUID, user_id: UUID):
        from tasks.content_tasks import sync_analytics_task
        sync_analytics_task.send(str(published_post_id))
        return {"status": "sync_queued"}

    async def get_summary(self, user_id: UUID, days: int):
        return await self.analytics_repo.get_user_analytics_summary(user_id, days, None)

    async def get_top_posts(self, user_id: UUID, limit: int, platform: str):
        return await self.analytics_repo.get_top_performing_posts(user_id, limit, platform, None)
