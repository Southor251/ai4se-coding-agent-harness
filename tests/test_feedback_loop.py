from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.feedback.sensor import FeedbackSensor
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction, ToolResult
from agent_harness.tools.base import ToolBase
from agent_harness.tools.registry import ToolRegistry


class FailingTool(ToolBase):
    def __init__(self):
        super().__init__(name="run_test", description="return a deterministic failure")

    def run(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, output="AssertionError: expected value")


def test_tool_failure_feedback_enters_next_context():
    registry = ToolRegistry()
    registry.register(FailingTool())
    mock = MockLLM(
        responses=[
            LLMResponse(
                text="run check",
                action=AgentAction(type="call_tool", tool="run_test", args={}),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(llm=mock, tools=registry, feedback=FeedbackSensor(), max_steps=5)

    agent_loop("test", harness)

    assert harness.feedback_events[0].category == "assertion"
    assert any("Feedback[assertion]" in message["content"] for message in harness.context)
