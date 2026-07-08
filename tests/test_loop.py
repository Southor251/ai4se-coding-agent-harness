from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.llm.mock import MockLLM
from agent_harness.llm.interface import LLMResponse
from agent_harness.models import AgentAction
from agent_harness.tools.builtin.write_file import WriteFileTool
from agent_harness.tools.registry import ToolRegistry


class SpyLLM(MockLLM):
    def __init__(self):
        super().__init__([LLMResponse(text="done", action=AgentAction(type="done"))])
        self.last_menu = None

    def call(self, context, menu):
        self.last_menu = menu
        return super().call(context, menu)


def test_harness_holds_llm():
    mock = MockLLM(responses=[])
    H = Harness(llm=mock)
    assert H.llm is mock


def test_harness_tracks_context_and_halt_reason():
    mock = MockLLM(responses=[])
    H = Harness(llm=mock)
    assert H.context == []
    assert H.halt_reason is None
    assert H.scope is None
    assert H.hitl is None


def test_agent_loop_immediate_done():
    mock = MockLLM(responses=[LLMResponse(text="ok", action=AgentAction(type="done"))])
    H = Harness(llm=mock, max_steps=10)
    answer = agent_loop("test", H)
    assert answer == "ok"
    assert H.step == 1
    assert H.halt_reason == "done"
    assert H.context[-1]["content"] == "ok"


def test_agent_loop_returns_done_answer_field_when_present():
    raw = '{"type": "done", "answer": "finished"}'
    mock = MockLLM(responses=[LLMResponse(text=raw, action=AgentAction(type="done", answer="finished"))])
    H = Harness(llm=mock, max_steps=10)

    answer = agent_loop("test", H)

    assert answer == "finished"
    assert H.context[-1]["content"] == raw


def test_agent_loop_multiple_steps():
    r1 = LLMResponse(text="first", action=AgentAction(type="call_tool", tool="read_file"))
    r2 = LLMResponse(text="done", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    H = Harness(llm=mock, max_steps=10)
    agent_loop("test", H)
    assert H.step == 2


def test_agent_loop_max_steps():
    mock = MockLLM(responses=[])
    H = Harness(llm=mock, max_steps=3)
    agent_loop("test", H)
    assert H.step <= 3


def test_agent_loop_resets_step_between_runs():
    mock = MockLLM(
        responses=[
            LLMResponse(text="first", action=AgentAction(type="done")),
            LLMResponse(text="second", action=AgentAction(type="done")),
        ]
    )
    H = Harness(llm=mock, max_steps=3)

    assert agent_loop("first goal", H) == "first"
    assert agent_loop("second goal", H) == "second"
    assert H.step == 1


def test_agent_loop_tool_menu_includes_arg_schema():
    registry = ToolRegistry()
    registry.register(WriteFileTool())
    llm = SpyLLM()
    H = Harness(llm=llm, tools=registry)

    agent_loop("inspect menu", H)

    assert llm.last_menu == [
        {
            "name": "write_file",
            "description": "Write content to file",
            "args_schema": {
                "path": "File path to write",
                "content": "UTF-8 text content to write",
            },
        }
    ]
