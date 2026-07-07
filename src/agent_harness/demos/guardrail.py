from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.governance.permission import PermissionPolicy
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction, PermissionRule, ToolResult
from agent_harness.tools.base import ToolBase
from agent_harness.tools.registry import ToolRegistry


class DemoTool(ToolBase):
    def __init__(self):
        super().__init__(name="write_file", description="demo tool")
        self.executed = False

    def run(self, **kwargs) -> ToolResult:
        self.executed = True
        return ToolResult(success=True, output="executed")


def run_demo() -> dict:
    tool = DemoTool()
    registry = ToolRegistry()
    registry.register(tool)
    permission = PermissionPolicy()
    permission.add_rule(
        PermissionRule("deny blocked fixture", "blocked-command", "deny", "command")
    )
    llm = MockLLM(
        [
            LLMResponse(
                "blocked",
                AgentAction(
                    type="call_tool",
                    tool="write_file",
                    args={"command": "blocked-command --target workspace", "path": "demo.txt"},
                ),
            ),
            LLMResponse("done", AgentAction(type="done")),
        ]
    )
    harness = Harness(llm=llm, tools=registry, permission=permission, max_steps=5)
    agent_loop("demo", harness)
    return {"status": "denied", "tool_executed": tool.executed}
