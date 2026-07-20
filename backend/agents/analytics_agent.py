from .base import BaseAgent, AgentContext, AgentResult
from .social_provider import SocialAccountDTO

class AnalyticsAgent(BaseAgent):
    name = "AnalyticsAgent"
    description = "Fetches analytics for published posts."

    def __init__(self, llm_provider, settings, provider_registry):
        super().__init__(llm_provider, settings)
        self.provider_registry = provider_registry

    async def run(self, context: AgentContext, post_id: str, account_data: dict) -> AgentResult:
        account = SocialAccountDTO(**account_data)
        provider = self.provider_registry.get(account.platform)
        if not provider:
            return AgentResult(success=False, data={}, error=f"Provider {account.platform} not found")
            
        metrics = await provider.fetch_metrics(post_id, account)
        return AgentResult(
            success=True,
            data=metrics.model_dump()
        )
