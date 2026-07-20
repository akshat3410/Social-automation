from services.content_service import ContentService
from services.publishing_service import PublishingService
from services.analytics_service import AnalyticsService
from services.prompt_service import PromptService
from services.auth_service import AuthService
from repositories.content_repository import ContentIdeaRepository
from repositories.draft_repository import DraftRepository
from repositories.schedule_repository import ScheduleRepository
from repositories.analytics_repository import AnalyticsRepository

# Factory functions for dependency injection

def get_content_service() -> ContentService:
    # Dummy session and models for now
    idea_repo = ContentIdeaRepository(model=None, session=None)
    draft_repo = DraftRepository(model=None, session=None)
    return ContentService(idea_repo, draft_repo)

def get_publishing_service() -> PublishingService:
    schedule_repo = ScheduleRepository(model=None, session=None)
    draft_repo = DraftRepository(model=None, session=None)
    return PublishingService(schedule_repo, draft_repo)

def get_analytics_service() -> AnalyticsService:
    analytics_repo = AnalyticsRepository(model=None, session=None)
    return AnalyticsService(analytics_repo)

def get_prompt_service() -> PromptService:
    return PromptService()
