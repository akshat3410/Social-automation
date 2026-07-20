from fastapi import APIRouter, Depends
from uuid import UUID
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_content_service
from services.content_service import ContentService
from schemas.content import (
    ContentIdeaCreate, ContentIdeaResponse, GenerateContentRequest,
    DraftApprovalRequest
)

router = APIRouter()

@router.post("/ideas", response_model=dict)
async def create_idea(data: ContentIdeaCreate, current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    return await content_service.create_idea(current_user, data.model_dump())

@router.get("/ideas", response_model=list)
async def list_ideas(current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    # Implementation using content_service
    return []

@router.get("/ideas/{id}", response_model=dict)
async def get_idea(id: UUID, current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    return {}

@router.post("/ideas/{id}/research")
async def trigger_research(id: UUID, current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    return await content_service.run_research(id, current_user)

@router.post("/ideas/{id}/generate")
async def generate_drafts(id: UUID, req: GenerateContentRequest, current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    return await content_service.generate_drafts(id, current_user)

@router.get("/drafts")
async def list_drafts(current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    return []

@router.get("/drafts/{id}")
async def get_draft(id: UUID, current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    return {}

@router.post("/drafts/{id}/approve")
async def approve_draft(id: UUID, data: DraftApprovalRequest, current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    return await content_service.approve_draft(id, current_user)

@router.post("/drafts/{id}/reject")
async def reject_draft(id: UUID, data: DraftApprovalRequest, current_user: UUID = Depends(get_current_user), content_service: ContentService = Depends(get_content_service)):
    return await content_service.reject_draft(id, current_user, data.reason or "No reason provided")
