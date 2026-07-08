from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.governance.permission import PermissionPolicy
from agent_harness.governance.hitl import HITLManager
from agent_harness.hitl.resume import approve_and_execute, approve_execute_and_continue
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction, PermissionRule, ToolResult
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


def test_approve_and_execute_rejects_outside_scope(tmp_path):
    tool = RecordingTool()
    registry = ToolRegistry()
    registry.register(tool)
    hitl = HITLManager()
    outside = tmp_path / "outside.txt"
    request = hitl.create_request(
        AgentAction(type="call_tool", tool="write_file", args={"path": str(outside)}),
        "review",
    )
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    from agent_harness.governance.scope import ScopeGuard

    harness = Harness(llm=None, tools=registry, hitl=hitl, scope=ScopeGuard(str(workspace)))

    result = approve_and_execute(harness, request.id)

    assert result.success is False
    assert "scope" in result.error
    assert request.status == "pending"
    assert tool.calls == []


def test_approve_execute_and_continue_resumes_agent_context():
    tool = RecordingTool()
    registry = ToolRegistry()
    registry.register(tool)
    hitl = HITLManager()
    permission = PermissionPolicy()
    permission.add_rule(PermissionRule("ask writes", ".*", "ask", "path"))
    llm = MockLLM(
        [
            LLMResponse(
                "write",
                AgentAction(type="call_tool", tool="write_file", args={"path": "note.txt"}),
            ),
            LLMResponse(
                '{"type":"done","answer":"continued"}',
                AgentAction(type="done", answer="continued"),
            ),
        ]
    )
    harness = Harness(
        llm=llm,
        tools=registry,
        permission=permission,
        hitl=hitl,
        max_steps=1,
    )

    agent_loop("write note", harness)
    request = hitl.requests[0]
    harness.max_steps = 3

    result = approve_execute_and_continue(harness, request.id)

    assert result.answer == "continued"
    assert request.status == "approved"
    assert tool.calls == [{"path": "note.txt"}]
    assert any(message["content"] == "executed" for message in harness.context)
