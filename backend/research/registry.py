from .base import ResearchPlugin


class ResearchPluginRegistry:
    def __init__(self):
        self._plugins: dict[str, ResearchPlugin] = {}

    def register(self, plugin: ResearchPlugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> ResearchPlugin | None:
        return self._plugins.get(name)

    def list_available(self) -> list[str]:
        return list(self._plugins.keys())

    def get_all_enabled(self) -> list[ResearchPlugin]:
        return list(self._plugins.values())


def build_default_registry() -> ResearchPluginRegistry:
    """Registry with all built-in research plugins enabled."""
    from .github_trending import GitHubTrendingPlugin
    from .hacker_news import HackerNewsPlugin
    from .reddit_research import RedditResearchPlugin
    from .rss import RSSPlugin

    registry = ResearchPluginRegistry()
    registry.register(HackerNewsPlugin())
    registry.register(RedditResearchPlugin())
    registry.register(RSSPlugin())
    registry.register(GitHubTrendingPlugin())
    return registry
