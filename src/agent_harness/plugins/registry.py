from agent_harness.plugins.base import BasePlugin


class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin):
        if plugin.name in self._plugins:
            raise ValueError(f"plugin already registered: {plugin.name}")
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> BasePlugin | None:
        return self._plugins.get(name)

    def list_names(self) -> list[str]:
        return sorted(self._plugins)

