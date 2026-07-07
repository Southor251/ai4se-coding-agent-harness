from agent_harness.agent.harness import Harness
from agent_harness.governance.hitl import HITLManager
from agent_harness.hitl.resume import approve_and_execute
from agent_harness.models import AgentAction, ToolResult
from agent_harness.tools.base import ToolBase
from agent_harness.tools.registry import ToolRegistry


class RecordingTool(ToolBase):
    def __init__(self):
        super().__init__(name="write_file", description="record")
        self.calls = []

    def run(self, **kwargs) -> ToolResult:
        self.calls.append(kwargs)
        return ToolResult(success=True, output="executed")


def test_approve_and_execute_runs_pending_action():
    tool = RecordingTool()
    registry = ToolRegistry()
    registry.register(tool)
    hitl = HITLManager()
    request = hitl.create_request(
        AgentAction(type="call_tool", tool="write_file", args={"path": "note.txt"}),
        "review",
    )
    harness = Harness(llm=None, tools=registry, hitl=hitl)

    result = approve_and_execute(harness, request.id)

    assert result.success is True
    assert tool.calls == [{"path": "note.txt"}]
    assert request.status == "approved"


def test_approve_and_execute_rejects_unknown_request():
    harness = Harness(llm=None, tools=ToolRegistry(), hitl=HITLManager())

    result = approve_and_execute(harness, "missing")

    assert result.success is False
    assert "not found" in result.error
