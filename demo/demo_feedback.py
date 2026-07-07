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

    def run(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, output="AssertionError: expected value")


def run_demo() -> dict:
    registry = ToolRegistry()
    registry.register(DemoTestTool())
    llm = MockLLM(
        [
            LLMResponse("check", AgentAction(type="call_tool", tool="run_test", args={})),
            LLMResponse("done", AgentAction(type="done")),
        ]
    )
    harness = Harness(llm=llm, tools=registry, feedback=FeedbackSensor(), max_steps=5)
    agent_loop("demo", harness)
    return {
        "status": "healed",
        "feedback_category": harness.feedback_events[0].category,
    }


if __name__ == "__main__":
    print(run_demo())

