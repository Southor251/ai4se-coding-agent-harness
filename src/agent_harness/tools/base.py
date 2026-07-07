from abc import ABC, abstractmethod
from agent_harness.models import ToolResult


class ToolBase(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        ...