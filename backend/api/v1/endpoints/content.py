from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.dependencies.auth import get_current_user
from api.dependencies.rate_limit import generate_rate_limit
from api.dependencies.services import get_content_service
from models.user import User
from schemas.content import (
    ContentIdeaCreate,
    ContentIdeaResponse,
    DraftApprovalRequest,
    DraftRejectionRequest,
    DraftResponse,
    GenerateContentRequest,
    TaskQueuedResponse,
)
from services.content_service import ContentService

router = APIRouter()


@router.post("/ideas", response_model=ContentIdeaResponse, status_code=status.HTTP_201_CREATED)
async def create_idea(
    data: ContentIdeaCreate,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    return await content_service.create_idea(current_user.id, data.model_dump())


@router.get("/ideas", response_model=list[ContentIdeaResponse])
async def list_ideas(
    status_filter: str | None = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    return await content_service.list_ideas(
        current_user.id, status=status_filter, skip=offset, limit=limit
    )


@router.get("/ideas/{idea_id}", response_model=ContentIdeaResponse)
async def get_idea(
    idea_id: UUID,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    return await content_service.get_idea(idea_id, current_user.id)


@router.post(
    "/ideas/{idea_id}/research",
    response_model=TaskQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(generate_rate_limit())],
)
async def trigger_research(
    idea_id: UUID,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    task_id = await content_service.run_research(idea_id, current_user.id)
    return TaskQueuedResponse(task_id=task_id)


@router.post(
    "/ideas/{idea_id}/generate",
    response_model=TaskQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(generate_rate_limit())],
)
async def generate_drafts(
    idea_id: UUID,
    req: GenerateContentRequest | None = None,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    num_variations = req.num_variations if req else None
    task_id = await content_service.generate_drafts(idea_id, current_user.id, num_variations)
    return TaskQueuedResponse(task_id=task_id)


@router.get("/drafts", response_model=list[DraftResponse])
async def list_drafts(
    status_filter: str | None = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    drafts = await content_service.list_drafts(
        current_user.id, status=status_filter, skip=offset, limit=limit
    )
    return [DraftResponse.from_model(d) for d in drafts]


@router.get("/drafts/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: UUID,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    draft = await content_service.get_draft(draft_id, current_user.id)
    return DraftResponse.from_model(draft)


@router.post("/drafts/{draft_id}/approve", response_model=DraftResponse)
async def approve_draft(
    draft_id: UUID,
    data: DraftApprovalRequest | None = None,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    scheduled_for = data.scheduled_for if data else None
    draft, scheduled = await content_service.approve_draft(
        draft_id, current_user.id, scheduled_for
    )
    return DraftResponse.from_model(draft, scheduled_for=scheduled)


@router.post("/drafts/{draft_id}/reject", response_model=DraftResponse)
async def reject_draft(
    draft_id: UUID,
    data: DraftRejectionRequest,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    draft = await content_service.reject_draft(draft_id, current_user.id, data.reason)
    return DraftResponse.from_model(draft)
