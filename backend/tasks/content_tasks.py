import dramatiq
import logging
from workers.broker import get_broker

logger = logging.getLogger(__name__)

@dramatiq.actor(max_retries=3, time_limit=300000)
def run_research_task(idea_id: str, user_id: str):
    logger.info(f"Running research for idea {idea_id} by user {user_id}")
    # calls ResearchAgent
    pass

@dramatiq.actor(max_retries=3, time_limit=600000)
def generate_drafts_task(idea_id: str, user_id: str):
    logger.info(f"Generating drafts for idea {idea_id} by user {user_id}")
    # runs full pipeline
    pass

@dramatiq.actor(max_retries=3, time_limit=300000)
def publish_task(schedule_id: str):
    logger.info(f"Publishing schedule {schedule_id}")
    # publishes scheduled post
    pass

@dramatiq.actor(max_retries=3, time_limit=300000)
def sync_analytics_task(published_post_id: str):
    logger.info(f"Syncing analytics for post {published_post_id}")
    # syncs analytics
    pass
