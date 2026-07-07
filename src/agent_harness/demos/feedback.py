from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.feedback.sensor import FeedbackSensor
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction, ToolResult
from agent_harness.tools.base import ToolBase
from agent_harness.tools.registry import ToolRegistry


class DemoTestTool(ToolBase):
    def __init__(self):
        super().__init__(name="run_test", description="demo test tool")
        self.attempts = 0

    def run(self, **kwargs) -> ToolResult:
        self.attempts += 1
        if self.attempts == 1:
            return ToolResult(success=False, error="AssertionError: expected value")
        return ToolResult(success=True, output="tests passed")


def run_demo() -> dict:
    registry = ToolRegistry()
    tool = DemoTestTool()
    registry.register(tool)
    llm = MockLLM(
        [
            LLMResponse("check", AgentAction(type="call_tool", tool="run_test", args={})),
            LLMResponse("retry", AgentAction(type="call_tool", tool="run_test", args={})),
            LLMResponse("done", AgentAction(type="done")),
        ]
    )
    harness = Harness(llm=llm, tools=registry, feedback=FeedbackSensor(), max_steps=5)
    agent_loop("demo", harness)
    status = "healed" if tool.attempts == 2 and harness.feedback_events[-1].category == "success" else "failed"
    return {
        "status": status,
        "feedback_category": harness.feedback_events[0].category,
        "attempts": tool.attempts,
    }
