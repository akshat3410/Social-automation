from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.dependencies.auth import require_superuser
from api.dependencies.services import get_prompt_service
from models.user import User
from services.prompt_service import PromptService

router = APIRouter()


class PromptUpdateRequest(BaseModel):
    content: str


@router.get("")
async def list_prompts(
    current_user: User = Depends(require_superuser),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    return await prompt_service.list_prompts()


@router.get("/{agent_name}")
async def get_prompt(
    agent_name: str,
    current_user: User = Depends(require_superuser),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    return await prompt_service.get_prompt_info(agent_name)


@router.put("/{agent_name}")
async def update_prompt(
    agent_name: str,
    data: PromptUpdateRequest,
    current_user: User = Depends(require_superuser),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    return await prompt_service.update_prompt(agent_name, data.content, current_user.id)


@router.get("/{agent_name}/versions")
async def list_versions(
    agent_name: str,
    current_user: User = Depends(require_superuser),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    return await prompt_service.list_versions(agent_name)


@router.post("/{agent_name}/rollback/{version}")
async def rollback_prompt(
    agent_name: str,
    version: int,
    current_user: User = Depends(require_superuser),
    prompt_service: PromptService = Depends(get_prompt_service),
):
    return await prompt_service.rollback(agent_name, version)
