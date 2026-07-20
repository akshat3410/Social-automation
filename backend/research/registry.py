from .base import ResearchPlugin

class ResearchPluginRegistry:
    def __init__(self):
        self._plugins: dict[str, ResearchPlugin] = {}

    def register(self, plugin: ResearchPlugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> ResearchPlugin:
        return self._plugins.get(name)

    def list_available(self) -> list[str]:
        return list(self._plugins.keys())

    def get_all_enabled(self) -> list[ResearchPlugin]:
        return list(self._plugins.values())
