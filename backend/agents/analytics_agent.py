from .base import AgentContext, AgentResult
from .social_provider import MockSocialProvider, SocialAccountDTO, SocialProviderRegistry


class AnalyticsAgent:
    """Fetches analytics for published posts via the platform provider."""

    name = "analytics"

    def __init__(self, provider_registry: SocialProviderRegistry):
        self.provider_registry = provider_registry

    async def run(self, context: AgentContext, post_id: str, account_data: dict) -> AgentResult:
        account = SocialAccountDTO(**account_data)
        provider = self.provider_registry.get(account.platform) or MockSocialProvider(
            account.platform
        )
        metrics = await provider.fetch_metrics(post_id, account)
        return AgentResult(success=True, data=metrics.model_dump())
