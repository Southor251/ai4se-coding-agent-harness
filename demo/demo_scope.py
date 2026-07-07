import tempfile
from pathlib import Path

from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.governance.scope import ScopeGuard
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction, ToolResult
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
    with tempfile.TemporaryDirectory() as parent:
        workspace = Path(parent) / "workspace"
        outside = Path(parent) / "outside"
        workspace.mkdir()
        outside.mkdir()
        target = outside / "file.txt"
        tool = DemoTool()
        registry = ToolRegistry()
        registry.register(tool)
        llm = MockLLM(
            [
                LLMResponse(
                    "outside",
                    AgentAction(
                        type="call_tool",
                        tool="write_file",
                        args={"path": str(target), "content": "content"},
                    ),
                ),
                LLMResponse("done", AgentAction(type="done")),
            ]
        )
        harness = Harness(
            llm=llm,
            tools=registry,
            scope=ScopeGuard(workspace_root=str(workspace)),
            max_steps=5,
        )
        agent_loop("demo", harness)
        return {"status": "scope_denied", "tool_executed": tool.executed}


if __name__ == "__main__":
    print(run_demo())
