from .base import AgentContext, AgentResult
from .social_provider import MockSocialProvider, SocialAccountDTO, SocialProviderRegistry


class PublishingAgent:
    """Publishes content via the configured social provider for the platform.

    Falls back to the mock (dry-run) provider when the platform is not
    configured, so the pipeline works without real API credentials.
    """

    name = "publishing"

    def __init__(self, provider_registry: SocialProviderRegistry):
        self.provider_registry = provider_registry

    async def run(self, context: AgentContext, content: str, account_data: dict) -> AgentResult:
        account = SocialAccountDTO(**account_data)
        provider = self.provider_registry.get(account.platform) or MockSocialProvider(
            account.platform
        )
        validation = await provider.validate_content(content)
        if not validation.is_valid:
            return AgentResult(
                success=False, data={}, error="; ".join(validation.errors) or "Invalid content"
            )
        result = await provider.publish(content, None, account)
        return AgentResult(
            success=result.success,
            data={
                "platform_post_id": result.platform_post_id,
                "published_at": result.published_at,
                "dry_run": isinstance(provider, MockSocialProvider),
            },
            error=result.error,
        )
