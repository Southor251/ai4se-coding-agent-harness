from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.llm.mock import MockLLM
from agent_harness.llm.interface import LLMResponse
from agent_harness.models import AgentAction


def test_harness_holds_llm():
    mock = MockLLM(responses=[])
    H = Harness(llm=mock)
    assert H.llm is mock


def test_agent_loop_immediate_done():
    mock = MockLLM(responses=[LLMResponse(text="ok", action=AgentAction(type="done"))])
    H = Harness(llm=mock, max_steps=10)
    answer = agent_loop("test", H)
    assert answer == "ok"
    assert H.step == 1


def test_agent_loop_multiple_steps():
    r1 = LLMResponse(text="first", action=AgentAction(type="call_tool", tool="read_file"))
    r2 = LLMResponse(text="done", action=AgentAction(type="done"))
    mock = MockLLM(responses=[r1, r2])
    H = Harness(llm=mock, max_steps=10)
    answer = agent_loop("test", H)
    assert H.step == 2


def test_agent_loop_max_steps():
    mock = MockLLM(responses=[])
    H = Harness(llm=mock, max_steps=3)
    answer = agent_loop("test", H)
    assert H.step <= 3