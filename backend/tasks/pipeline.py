"""Async implementations of the background tasks.

Each entrypoint owns its engine/session lifecycle because Dramatiq actors
run them via asyncio.run() on a fresh event loop.
"""
import asyncio
import logging
import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select

from agents.analytics_agent import AnalyticsAgent
from agents.base import AgentContext
from agents.editor_agent import EditorAgent
from agents.llm_provider import build_llm_provider
from agents.planning_agent import PlanningAgent
from agents.publishing_agent import PublishingAgent
from agents.quality_agent import QualityAgent
from agents.research_agent import ResearchAgent
from agents.social_provider import build_provider_registry
from agents.writer_agent import WriterAgent
from config.settings import get_settings
from database.session import create_task_engine_and_factory
from memory.memory_service import MemoryService
from models.brand_memory import BrandMemory
from models.content_idea import ContentIdea, IdeaStatusEnum
from models.draft import Draft, DraftStatusEnum
from models.posting_schedule import PostingSchedule, ScheduleStatusEnum
from models.published_post import PublishedPost, PublishStatusEnum
from models.quality_score import QualityScore
from models.research_result import ResearchResult, SourceEnum
from models.social_account import SocialAccount
from repositories.memory_repository import MemoryRepository
from research.registry import build_default_registry
from services.prompt_service import PromptService

logger = logging.getLogger(__name__)

_SOURCE_MAP = {
    "hackernews": SourceEnum.hackernews,
    "reddit": SourceEnum.reddit,
    "rss": SourceEnum.rss,
    "github": SourceEnum.github,
}


def _context(user_id: str, platform: str) -> AgentContext:
    return AgentContext(request_id=str(uuid.uuid4()), user_id=str(user_id), platform=platform)


async def _gather_research(session, llm, settings, idea: ContentIdea, user_id: str) -> dict:
    """Fetch raw material from plugins, synthesize with the research agent,
    persist ResearchResult rows, and stamp research_context on the idea."""
    registry = build_default_registry()
    raw_items = []
    results = await asyncio.gather(
        *(plugin.fetch(idea.title, 5) for plugin in registry.get_all_enabled()),
        return_exceptions=True,
    )
    for plugin_result in results:
        if isinstance(plugin_result, BaseException):
            logger.warning("Research plugin failed: %s", plugin_result)
            continue
        raw_items.extend(plugin_result)

    for item in raw_items:
        source = _SOURCE_MAP.get(item.source)
        if source is None:
            continue
        session.add(
            ResearchResult(
                idea_id=idea.id,
                source=source,
                title=item.title[:512],
                content=item.content,
                url=item.url or None,
            )
        )

    trending_context = "\n".join(f"- {i.title}: {i.content[:200]}" for i in raw_items[:20]) or "N/A"
    prompt_service = PromptService(session)
    agent = ResearchAgent(
        llm,
        settings,
        await prompt_service.get_active_prompt("research"),
        model=settings.MODEL_RESEARCH,
    )
    result = await agent.run(
        _context(user_id, idea.platform.value),
        topic=idea.title,
        trending_context=trending_context,
    )
    if not result.success:
        raise RuntimeError(result.error or "Research agent failed")

    idea.research_context = result.data
    await session.commit()
    return result.data


async def run_research(idea_id: str, user_id: str) -> None:
    settings = get_settings()
    engine, factory = create_task_engine_and_factory()
    llm = build_llm_provider(settings)
    try:
        async with factory() as session:
            idea = await session.get(ContentIdea, UUID(idea_id))
            if idea is None:
                logger.error("Idea %s not found for research", idea_id)
                return
            try:
                await _gather_research(session, llm, settings, idea, user_id)
                idea.status = IdeaStatusEnum.pending
                await session.commit()
            except Exception:
                idea.status = IdeaStatusEnum.failed
                await session.commit()
                raise
    finally:
        await llm.aclose()
        await engine.dispose()


async def run_generation_pipeline(
    idea_id: str, user_id: str, num_variations: int | None = None
) -> None:
    settings = get_settings()
    engine, factory = create_task_engine_and_factory()
    llm = build_llm_provider(settings)
    try:
        async with factory() as session:
            idea = await session.get(ContentIdea, UUID(idea_id))
            if idea is None:
                logger.error("Idea %s not found for generation", idea_id)
                return
            try:
                await _run_pipeline_steps(session, llm, settings, idea, user_id, num_variations)
                idea.status = IdeaStatusEnum.completed
                await session.commit()
            except Exception:
                idea.status = IdeaStatusEnum.failed
                await session.commit()
                raise
    finally:
        await llm.aclose()
        await engine.dispose()


async def _run_pipeline_steps(
    session, llm, settings, idea: ContentIdea, user_id: str, num_variations: int | None
) -> None:
    context = _context(user_id, idea.platform.value)
    prompt_service = PromptService(session)
    memory = MemoryService(llm, MemoryRepository(model=BrandMemory, session=session))

    research_data = idea.research_context or await _gather_research(
        session, llm, settings, idea, user_id
    )

    planner = PlanningAgent(
        llm,
        settings,
        await prompt_service.get_active_prompt("planning"),
        model=settings.MODEL_RESEARCH,
    )
    plan_result = await planner.run(context, research_data=research_data)
    if not plan_result.success:
        raise RuntimeError(plan_result.error or "Planning agent failed")

    writer = WriterAgent(
        llm,
        settings,
        await prompt_service.get_active_prompt("writer"),
        model=settings.MODEL_WRITING,
    )
    write_result = await writer.run(
        context,
        plan=plan_result.data,
        num_variations=num_variations or settings.NUM_DRAFT_VARIATIONS,
    )
    if not write_result.success:
        raise RuntimeError(write_result.error or "Writer agent failed")

    editor = EditorAgent(
        llm,
        settings,
        await prompt_service.get_active_prompt("editor"),
        model=settings.MODEL_EDITING,
    )
    quality = QualityAgent(
        llm,
        settings,
        await prompt_service.get_active_prompt("quality"),
        model=settings.MODEL_EDITING,
    )

    for index, variation in enumerate(write_result.data["variations"], start=1):
        edit_result = await editor.run(context, draft_content=variation["content"])
        content = edit_result.data["content"]

        similarity = await memory.max_similarity(content, user_id)
        quality_result = await quality.run(
            context, content=content, duplicate_similarity=similarity
        )
        scores = quality_result.data

        passed = bool(scores.get("passed"))
        status = DraftStatusEnum.pending
        if passed and not settings.ENABLE_HUMAN_APPROVAL:
            status = DraftStatusEnum.approved
        elif not passed:
            status = DraftStatusEnum.rejected

        draft = Draft(
            idea_id=idea.id,
            user_id=UUID(str(user_id)),
            platform=idea.platform,
            content=content,
            hook=variation.get("hook"),
            variation_index=index,
            quality_score_data=scores,
            status=status,
            ai_model=settings.MODEL_WRITING,
            tokens_used=write_result.tokens_used + edit_result.tokens_used
            + quality_result.tokens_used,
            generation_time_ms=write_result.duration_ms + edit_result.duration_ms
            + quality_result.duration_ms,
        )
        session.add(draft)
        await session.flush()
        session.add(
            QualityScore(
                draft_id=draft.id,
                originality=scores.get("originality", 0.0),
                hook_strength=scores.get("hook_strength", 0.0),
                engagement_predicted=scores.get("engagement_predicted", 0.0),
                spam_probability=scores.get("spam_probability", 1.0),
                readability_score=scores.get("readability_score", 0.0),
                brand_consistency=scores.get("brand_consistency", 0.0),
                human_score=scores.get("human_score"),
                grammar_issues=[{"issue": g} for g in scores.get("grammar_issues", [])] or None,
                duplicate_similarity=scores.get("duplicate_similarity"),
                passed=passed,
                rejection_reason=scores.get("rejection_reason"),
            )
        )
    await session.commit()


async def _account_dto(account: SocialAccount | None, platform: str) -> dict:
    if account is None:
        return {"id": "dry-run", "platform": platform, "credentials": {}}
    credentials = {"access_token": account.access_token}
    if account.refresh_token:
        credentials["refresh_token"] = account.refresh_token
    credentials.update(account.metadata_ or {})
    return {"id": str(account.id), "platform": platform, "credentials": credentials}


async def publish_schedule(schedule_id: str) -> None:
    settings = get_settings()
    engine, factory = create_task_engine_and_factory()
    try:
        async with factory() as session:
            schedule = await session.get(PostingSchedule, UUID(schedule_id))
            if schedule is None:
                logger.error("Schedule %s not found", schedule_id)
                return
            if schedule.status in (ScheduleStatusEnum.completed, ScheduleStatusEnum.cancelled):
                return
            schedule.status = ScheduleStatusEnum.processing
            await session.commit()

            draft = await session.get(Draft, schedule.draft_id) if schedule.draft_id else None
            if draft is None:
                schedule.status = ScheduleStatusEnum.failed
                schedule.last_error = "Draft not found"
                await session.commit()
                return

            account = None
            if schedule.social_account_id:
                account = await session.get(SocialAccount, schedule.social_account_id)
            else:
                result = await session.execute(
                    select(SocialAccount).where(
                        SocialAccount.user_id == draft.user_id,
                        SocialAccount.platform == draft.platform,
                        SocialAccount.is_active.is_(True),
                    )
                )
                account = result.scalars().first()

            agent = PublishingAgent(build_provider_registry(settings))
            context = _context(str(draft.user_id), draft.platform.value)
            result = await agent.run(
                context, draft.content, await _account_dto(account, draft.platform.value)
            )

            if result.success:
                session.add(
                    PublishedPost(
                        draft_id=draft.id,
                        social_account_id=account.id if account else None,
                        platform=draft.platform,
                        platform_post_id=result.data.get("platform_post_id"),
                        content=draft.content,
                        published_at=datetime.now(UTC),
                        status=PublishStatusEnum.success,
                    )
                )
                draft.status = DraftStatusEnum.published
                schedule.status = ScheduleStatusEnum.completed
                await session.commit()
                if result.data.get("dry_run"):
                    logger.info(
                        "Draft %s published via dry-run provider (no real %s account configured)",
                        draft.id,
                        draft.platform.value,
                    )
            else:
                schedule.status = ScheduleStatusEnum.failed
                schedule.retries += 1
                schedule.last_error = result.error
                await session.commit()
                raise RuntimeError(f"Publish failed: {result.error}")
    finally:
        await engine.dispose()


async def sync_analytics(published_post_id: str) -> None:
    settings = get_settings()
    engine, factory = create_task_engine_and_factory()
    try:
        async with factory() as session:
            post = await session.get(PublishedPost, UUID(published_post_id))
            if post is None or not post.platform_post_id:
                logger.error("Published post %s not found or has no platform id", published_post_id)
                return
            account = None
            if post.social_account_id:
                account = await session.get(SocialAccount, post.social_account_id)

            draft = await session.get(Draft, post.draft_id)
            agent = AnalyticsAgent(build_provider_registry(settings))
            context = _context(str(draft.user_id) if draft else "unknown", post.platform.value)
            result = await agent.run(
                context, post.platform_post_id, await _account_dto(account, post.platform.value)
            )

            from models.analytics import Analytics

            existing = await session.execute(
                select(Analytics).where(Analytics.published_post_id == post.id)
            )
            row = existing.scalar_one_or_none()
            metrics = result.data
            if row is None:
                row = Analytics(published_post_id=post.id, platform=post.platform)
                session.add(row)
            row.likes = metrics.get("likes", 0)
            row.reposts = metrics.get("reposts", 0)
            row.replies = metrics.get("replies", 0)
            row.views = metrics.get("views", 0)
            row.fetched_at = datetime.now(UTC)
            row.raw_data = metrics
            await session.commit()
    finally:
        await engine.dispose()
