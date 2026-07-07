from agent_harness.llm.interface import LLMInterface, LLMResponse
from agent_harness.models import AgentAction


class MockLLM(LLMInterface):
    def __init__(self, responses: list[LLMResponse]):
        self.responses = responses
        self.call_count = 0

    def call(self, context: list[dict], menu: list[dict]) -> LLMResponse:
        if self.call_count >= len(self.responses):
            return LLMResponse(text="", action=AgentAction(type="done"))
        response = self.responses[self.call_count]
        self.call_count += 1
        return response