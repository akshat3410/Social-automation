from fastapi import APIRouter, Depends
from uuid import UUID
from api.dependencies.auth import get_current_user, require_superuser
from api.dependencies.services import get_prompt_service
from services.prompt_service import PromptService

router = APIRouter()

@router.get("/")
async def list_prompts(current_user: UUID = Depends(require_superuser), prompt_service: PromptService = Depends(get_prompt_service)):
    return []

@router.get("/{agent_name}")
async def get_prompt(agent_name: str, current_user: UUID = Depends(require_superuser), prompt_service: PromptService = Depends(get_prompt_service)):
    return await prompt_service.get_active_prompt(agent_name)

@router.put("/{agent_name}")
async def update_prompt(agent_name: str, content: str, current_user: UUID = Depends(require_superuser), prompt_service: PromptService = Depends(get_prompt_service)):
    return await prompt_service.update_prompt(agent_name, content, current_user)

@router.get("/{agent_name}/versions")
async def list_versions(agent_name: str, current_user: UUID = Depends(require_superuser), prompt_service: PromptService = Depends(get_prompt_service)):
    return await prompt_service.list_versions(agent_name)

@router.post("/{agent_name}/rollback/{version}")
async def rollback_prompt(agent_name: str, version: int, current_user: UUID = Depends(require_superuser), prompt_service: PromptService = Depends(get_prompt_service)):
    return await prompt_service.rollback(agent_name, version)
