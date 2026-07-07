from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.llm.mock import MockLLM
from agent_harness.llm.interface import LLMResponse
from agent_harness.models import AgentAction, ToolResult
from agent_harness.tools.registry import ToolRegistry
from agent_harness.tools.base import ToolBase


class FakeTool(ToolBase):
    def __init__(self):
        super().__init__(name="echo", description="echo test")
    def run(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=str(kwargs.get("msg", "")))


class FakeMemory:
    def __init__(self):
        self.notes = []
    def write(self, note):
        self.notes.append(note)


def test_call_tool_dispatch():
    reg = ToolRegistry()
    reg.register(FakeTool())
    r1 = LLMResponse(text="calling", action=AgentAction(type="call_tool", tool="echo", args={"msg": "hi"}))
    r2 = LLMResponse(text="done", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    H = Harness(llm=mock, tools=reg, max_steps=10)
    answer = agent_loop("test", H)
    assert answer == "done"


def test_take_note():
    mem = FakeMemory()
    r1 = LLMResponse(text="note", action=AgentAction(type="take_note", note="remember this"))
    r2 = LLMResponse(text="done", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    H = Harness(llm=mock, memory=mem, max_steps=10)
    agent_loop("test", H)
    assert "remember this" in mem.notes


def test_max_steps_enforced():
    mock = MockLLM(responses=[])
    H = Harness(llm=mock, max_steps=3)
    agent_loop("test", H)
    assert H.step == 3