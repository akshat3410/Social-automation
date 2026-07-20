from .base import BaseAgent, AgentContext, AgentResult
from .social_provider import SocialAccountDTO

class PublishingAgent(BaseAgent):
    name = "PublishingAgent"
    description = "Publishes content to social platforms."

    def __init__(self, llm_provider, settings, provider_registry):
        super().__init__(llm_provider, settings)
        self.provider_registry = provider_registry

    async def run(self, context: AgentContext, content: str, account_data: dict) -> AgentResult:
        account = SocialAccountDTO(**account_data)
        provider = self.provider_registry.get(account.platform)
        if not provider:
            return AgentResult(success=False, data={}, error=f"Provider {account.platform} not found")
            
        result = await provider.publish(content, None, account)
        return AgentResult(
            success=result.success,
            data={"platform_post_id": result.platform_post_id, "published_at": result.published_at},
            error=result.error
        )
