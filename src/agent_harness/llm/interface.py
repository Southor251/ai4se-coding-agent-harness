from abc import ABC, abstractmethod
from agent_harness.models import AgentAction


class LLMResponse:
    def __init__(self, text: str, action: AgentAction):
        self.text = text
        self.action = action


class LLMInterface(ABC):
    @abstractmethod
    def call(self, context: list[dict], menu: list[dict]) -> LLMResponse:
        ...