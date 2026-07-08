from abc import ABC, abstractmethod
from agent_harness.models import ToolResult


class ToolBase(ABC):
    def __init__(self, name: str, description: str = "", args_schema: dict[str, str] | None = None):
        self.name = name
        self.description = description
        self.args_schema = args_schema or {}

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        ...
