import asyncio
import logging

import dramatiq

import workers.broker  # noqa: F401 - registers the Redis broker before actors

from . import pipeline

logger = logging.getLogger(__name__)


@dramatiq.actor(max_retries=3, time_limit=300000)
def run_research_task(idea_id: str, user_id: str) -> None:
    logger.info("Running research for idea %s", idea_id)
    asyncio.run(pipeline.run_research(idea_id, user_id))


@dramatiq.actor(max_retries=3, time_limit=600000)
def generate_drafts_task(idea_id: str, user_id: str, num_variations: int | None = None) -> None:
    logger.info("Generating drafts for idea %s", idea_id)
    asyncio.run(pipeline.run_generation_pipeline(idea_id, user_id, num_variations))


@dramatiq.actor(max_retries=3, time_limit=300000)
def publish_task(schedule_id: str) -> None:
    logger.info("Publishing schedule %s", schedule_id)
    asyncio.run(pipeline.publish_schedule(schedule_id))


@dramatiq.actor(max_retries=3, time_limit=300000)
def sync_analytics_task(published_post_id: str) -> None:
    logger.info("Syncing analytics for post %s", published_post_id)
    asyncio.run(pipeline.sync_analytics(published_post_id))
