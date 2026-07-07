from agent_harness.tools.base import ToolBase


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolBase] = {}

    def register(self, tool: ToolBase):
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolBase | None:
        return self._tools.get(name)

    def list(self) -> list[ToolBase]:
        return list(self._tools.values())

    def unregister(self, name: str):
        self._tools.pop(name, None)