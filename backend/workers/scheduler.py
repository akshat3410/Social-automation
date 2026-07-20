import time
import logging
from datetime import datetime, timezone
# In real code, import ScheduleRepository and session maker
from tasks.content_tasks import publish_task

logger = logging.getLogger(__name__)

def poll_schedules():
    """Polls posting_schedule for due jobs every 60 seconds."""
    logger.info("Starting scheduler loop")
    while True:
        try:
            now = datetime.now(timezone.utc)
            # pseudo-code:
            # session = get_session()
            # repo = ScheduleRepository(model=Schedule, session=session)
            # due_jobs = await repo.get_pending_due(now)
            # for job in due_jobs:
            #     publish_task.send(str(job.id))
            #     await repo.update(job.id, {"status": "processing"})
            logger.info(f"Polled schedules at {now}")
        except Exception as e:
            logger.error(f"Error polling schedules: {e}")
        time.sleep(60)

if __name__ == "__main__":
    poll_schedules()
