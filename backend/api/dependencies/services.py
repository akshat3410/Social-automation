from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from models.analytics import Analytics
from models.content_idea import ContentIdea
from models.draft import Draft
from models.posting_schedule import PostingSchedule
from repositories.analytics_repository import AnalyticsRepository
from repositories.content_repository import ContentIdeaRepository
from repositories.draft_repository import DraftRepository
from repositories.schedule_repository import ScheduleRepository
from services.analytics_service import AnalyticsService
from services.content_service import ContentService
from services.prompt_service import PromptService
from services.publishing_service import PublishingService


def get_content_service(db: AsyncSession = Depends(get_db)) -> ContentService:
    idea_repo = ContentIdeaRepository(model=ContentIdea, session=db)
    draft_repo = DraftRepository(model=Draft, session=db)
    schedule_repo = ScheduleRepository(model=PostingSchedule, session=db)
    return ContentService(idea_repo, draft_repo, schedule_repo)


def get_publishing_service(db: AsyncSession = Depends(get_db)) -> PublishingService:
    schedule_repo = ScheduleRepository(model=PostingSchedule, session=db)
    draft_repo = DraftRepository(model=Draft, session=db)
    return PublishingService(schedule_repo, draft_repo, db)


def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    analytics_repo = AnalyticsRepository(model=Analytics, session=db)
    return AnalyticsService(analytics_repo)


def get_prompt_service(db: AsyncSession = Depends(get_db)) -> PromptService:
    return PromptService(db)
