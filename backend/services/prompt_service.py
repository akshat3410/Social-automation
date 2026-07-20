from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from models.prompt_version import AgentNameEnum, PromptVersion

from .exceptions import NotFoundError, ValidationError


def _validate_agent(agent_name: str) -> AgentNameEnum:
    try:
        return AgentNameEnum(agent_name)
    except ValueError:
        valid = ", ".join(a.value for a in AgentNameEnum)
        raise ValidationError(f"Unknown agent '{agent_name}'. Valid agents: {valid}") from None


class PromptService:
    """Prompt storage: versioned rows in the DB, markdown files as the fallback."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _read_file_prompt(self, agent: AgentNameEnum) -> str:
        path = get_settings().PROMPTS_DIR / f"{agent.value}.md"
        if not path.is_file():
            raise NotFoundError(f"No prompt found for agent '{agent.value}'")
        return path.read_text()

    async def _active_version(self, agent: AgentNameEnum) -> PromptVersion | None:
        result = await self.session.execute(
            select(PromptVersion).where(
                PromptVersion.agent_name == agent, PromptVersion.is_active.is_(True)
            )
        )
        return result.scalar_one_or_none()

    async def get_active_prompt(self, agent_name: str) -> str:
        agent = _validate_agent(agent_name)
        active = await self._active_version(agent)
        if active is not None:
            return active.content
        return self._read_file_prompt(agent)

    async def get_prompt_info(self, agent_name: str) -> dict:
        agent = _validate_agent(agent_name)
        active = await self._active_version(agent)
        if active is not None:
            return {
                "agent_name": agent.value,
                "content": active.content,
                "version": active.version,
                "updated_at": active.updated_at,
            }
        return {
            "agent_name": agent.value,
            "content": self._read_file_prompt(agent),
            "version": 0,
            "updated_at": None,
        }

    async def list_prompts(self) -> list[dict]:
        infos = []
        for agent in AgentNameEnum:
            try:
                info = await self.get_prompt_info(agent.value)
            except NotFoundError:
                continue
            infos.append(
                {
                    "agent_name": info["agent_name"],
                    "version": info["version"],
                    "updated_at": info["updated_at"],
                }
            )
        return infos

    async def update_prompt(self, agent_name: str, content: str, user_id: UUID) -> dict:
        agent = _validate_agent(agent_name)
        if not content.strip():
            raise ValidationError("Prompt content cannot be empty")
        active = await self._active_version(agent)
        if active is not None:
            active.is_active = False
        result = await self.session.execute(
            select(func.coalesce(func.max(PromptVersion.version), 0)).where(
                PromptVersion.agent_name == agent
            )
        )
        next_version = int(result.scalar_one()) + 1
        row = PromptVersion(
            agent_name=agent,
            version=next_version,
            content=content,
            is_active=True,
            created_by=user_id,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return {
            "agent_name": agent.value,
            "content": row.content,
            "version": row.version,
            "updated_at": row.updated_at,
        }

    async def list_versions(self, agent_name: str) -> list[dict]:
        agent = _validate_agent(agent_name)
        result = await self.session.execute(
            select(PromptVersion)
            .where(PromptVersion.agent_name == agent)
            .order_by(PromptVersion.version.desc())
        )
        return [
            {"version": v.version, "created_at": v.created_at, "is_active": v.is_active}
            for v in result.scalars().all()
        ]

    async def rollback(self, agent_name: str, version: int) -> dict:
        agent = _validate_agent(agent_name)
        result = await self.session.execute(
            select(PromptVersion).where(
                PromptVersion.agent_name == agent, PromptVersion.version == version
            )
        )
        target = result.scalar_one_or_none()
        if target is None:
            raise NotFoundError(f"Version {version} not found for agent '{agent.value}'")
        active = await self._active_version(agent)
        if active is not None:
            active.is_active = False
        target.is_active = True
        await self.session.commit()
        return {
            "agent_name": agent.value,
            "content": target.content,
            "version": target.version,
            "updated_at": target.updated_at,
        }
