from uuid import UUID
from .exceptions import NotFoundError, QualityGateFailedError

class ContentService:
    def __init__(self, idea_repo, draft_repo):
        self.idea_repo = idea_repo
        self.draft_repo = draft_repo

    async def create_idea(self, user_id: UUID, data: dict):
        data["user_id"] = user_id
        return await self.idea_repo.create(data)

    async def run_research(self, idea_id: UUID, user_id: UUID):
        from tasks.content_tasks import run_research_task
        run_research_task.send(str(idea_id), str(user_id))
        return {"idea_id": idea_id, "status": "research_started"}

    async def generate_drafts(self, idea_id: UUID, user_id: UUID):
        from tasks.content_tasks import generate_drafts_task
        generate_drafts_task.send(str(idea_id), str(user_id))
        return []

    async def approve_draft(self, draft_id: UUID, user_id: UUID):
        draft = await self.draft_repo.get(draft_id)
        if not draft:
            raise NotFoundError("Draft not found")
        return await self.draft_repo.update(draft_id, {"status": "approved"})

    async def reject_draft(self, draft_id: UUID, user_id: UUID, reason: str):
        draft = await self.draft_repo.get(draft_id)
        if not draft:
            raise NotFoundError("Draft not found")
        return await self.draft_repo.update(draft_id, {"status": "rejected", "rejection_reason": reason})

    async def get_pending_approvals(self, user_id: UUID):
        return await self.draft_repo.get_by_status("pending_approval", user_id, None)
