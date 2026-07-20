"""Scheduler: polls posting_schedules and enqueues due publish jobs.

Run with: python -m workers.scheduler
"""
import asyncio
import logging
from datetime import UTC, datetime

from config.logging_config import configure_logging
from config.settings import get_settings
from database.session import create_task_engine_and_factory
from models.posting_schedule import PostingSchedule, ScheduleStatusEnum
from repositories.schedule_repository import ScheduleRepository
from tasks.content_tasks import publish_task

logger = logging.getLogger(__name__)


async def poll_once(factory) -> int:
    async with factory() as session:
        repo = ScheduleRepository(model=PostingSchedule, session=session)
        due = await repo.get_pending_due(datetime.now(UTC))
        for schedule in due:
            schedule.status = ScheduleStatusEnum.processing
        await session.commit()
        for schedule in due:
            publish_task.send(str(schedule.id))
            logger.info("Enqueued publish for schedule %s", schedule.id)
        return len(due)


async def main() -> None:
    settings = get_settings()
    configure_logging(debug=settings.DEBUG)
    engine, factory = create_task_engine_and_factory()
    logger.info(
        "Scheduler started (interval %ss)", settings.SCHEDULER_POLL_INTERVAL_SECONDS
    )
    try:
        while True:
            try:
                count = await poll_once(factory)
                if count:
                    logger.info("Enqueued %s due schedule(s)", count)
            except Exception:
                logger.exception("Scheduler poll failed")
            await asyncio.sleep(settings.SCHEDULER_POLL_INTERVAL_SECONDS)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
