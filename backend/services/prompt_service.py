from uuid import UUID
from .exceptions import NotFoundError

class PromptService:
    async def get_active_prompt(self, agent_name: str) -> str:
        return f"Active prompt for {agent_name}"

    async def update_prompt(self, agent_name: str, content: str, user_id: UUID):
        return {"agent_name": agent_name, "version": 2}

    async def list_versions(self, agent_name: str):
        return []

    async def rollback(self, agent_name: str, version: int):
        return {"agent_name": agent_name, "version": version}
