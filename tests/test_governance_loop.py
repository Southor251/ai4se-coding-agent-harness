from agent_harness.agent.harness import Harness
from agent_harness.agent.loop import agent_loop
from agent_harness.governance.hitl import HITLManager
from agent_harness.governance.permission import PermissionPolicy
from agent_harness.governance.scope import ScopeGuard
from agent_harness.llm.interface import LLMResponse
from agent_harness.llm.mock import MockLLM
from agent_harness.models import AgentAction, PermissionRule, ToolResult
from agent_harness.tools.base import ToolBase
from agent_harness.tools.registry import ToolRegistry


class RecordingTool(ToolBase):
    def __init__(self):
        super().__init__(name="write_file", description="record calls")
        self.calls = []

    def run(self, **kwargs) -> ToolResult:
        self.calls.append(kwargs)
        return ToolResult(success=True, output="executed")


class ShellLikeTool(ToolBase):
    def __init__(self):
        super().__init__(name="run_shell", description="shell-like test tool")
        self.calls = []

    def run(self, **kwargs) -> ToolResult:
        self.calls.append(kwargs)
        return ToolResult(success=True, output="executed")


class RunTestLikeTool(ToolBase):
    def __init__(self):
        super().__init__(name="run_test", description="test-like tool")
        self.calls = []

    def run(self, **kwargs) -> ToolResult:
        self.calls.append(kwargs)
        return ToolResult(success=True, output="executed")


def registry_with(tool: ToolBase) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(tool)
    return registry


def test_permission_deny_blocks_tool_execution():
    tool = RecordingTool()
    permission = PermissionPolicy()
    permission.add_rule(
        PermissionRule(
            name="deny blocked fixture",
            pattern="blocked-command",
            verdict="deny",
            rule_type="command",
        )
    )
    mock = MockLLM(
        responses=[
            LLMResponse(
                text="try blocked action",
                action=AgentAction(
                    type="call_tool",
                    tool="write_file",
                    args={"command": "blocked-command --target workspace", "path": "safe.txt"},
                ),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(llm=mock, tools=registry_with(tool), permission=permission, max_steps=5)

    agent_loop("test", harness)

    assert tool.calls == []
    assert any("blocked by permission" in message["content"] for message in harness.context)


def test_scope_outside_blocks_tool_execution(tmp_path):
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    outside_file = outside / "file.txt"
    tool = RecordingTool()
    mock = MockLLM(
        responses=[
            LLMResponse(
                text="try outside write",
                action=AgentAction(
                    type="call_tool",
                    tool="write_file",
                    args={"path": str(outside_file), "content": "content"},
                ),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(
        llm=mock,
        tools=registry_with(tool),
        scope=ScopeGuard(workspace_root=str(workspace)),
        max_steps=5,
    )

    agent_loop("test", harness)

    assert tool.calls == []
    assert any("blocked by scope" in message["content"] for message in harness.context)


def test_permission_ask_creates_hitl_request_and_blocks_by_default(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "file.txt"
    tool = RecordingTool()
    permission = PermissionPolicy()
    permission.add_rule(
        PermissionRule(
            name="ask review fixture",
            pattern="review-command",
            verdict="ask",
            rule_type="command",
        )
    )
    hitl = HITLManager()
    mock = MockLLM(
        responses=[
            LLMResponse(
                text="try reviewed action",
                action=AgentAction(
                    type="call_tool",
                    tool="write_file",
                    args={"command": "review-command file", "path": str(target), "content": "content"},
                ),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(
        llm=mock,
        tools=registry_with(tool),
        permission=permission,
        scope=ScopeGuard(workspace_root=str(workspace)),
        hitl=hitl,
        max_steps=5,
    )

    agent_loop("test", harness)

    assert tool.calls == []
    assert len(hitl.requests) == 1
    assert hitl.requests[0].status == "pending"
    assert any("requires human approval" in message["content"] for message in harness.context)


def test_scope_allows_workspace_path_to_execute(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "file.txt"
    tool = RecordingTool()
    mock = MockLLM(
        responses=[
            LLMResponse(
                text="try inside write",
                action=AgentAction(
                    type="call_tool",
                    tool="write_file",
                    args={"path": str(target), "content": "content"},
                ),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(
        llm=mock,
        tools=registry_with(tool),
        scope=ScopeGuard(workspace_root=str(workspace)),
        max_steps=5,
    )

    agent_loop("test", harness)

    assert tool.calls == [{"path": str(target), "content": "content"}]


def test_unknown_tool_records_feedback_and_trace(tmp_path):
    from agent_harness.trace.store import TraceStore

    trace_path = tmp_path / "trace.jsonl"
    mock = MockLLM(
        responses=[
            LLMResponse(
                text="unknown",
                action=AgentAction(type="call_tool", tool="missing_tool", args={}),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(llm=mock, tools=ToolRegistry(), trace=TraceStore(trace_path), max_steps=5)

    agent_loop("test", harness)

    assert any("Tool not found" in message["content"] for message in harness.context)
    assert len(TraceStore.load(trace_path)) == 2


def test_shell_tool_is_blocked_by_default_when_scope_is_enabled(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    tool = ShellLikeTool()
    mock = MockLLM(
        responses=[
            LLMResponse(
                text="shell",
                action=AgentAction(type="call_tool", tool="run_shell", args={"command": "safe-list"}),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(
        llm=mock,
        tools=registry_with(tool),
        scope=ScopeGuard(workspace_root=str(workspace)),
        max_steps=5,
    )

    agent_loop("test", harness)

    assert tool.calls == []
    assert any("blocked by shell policy" in message["content"] for message in harness.context)


def test_run_test_pattern_outside_scope_is_blocked(tmp_path):
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    tool = RunTestLikeTool()
    mock = MockLLM(
        responses=[
            LLMResponse(
                text="run outside tests",
                action=AgentAction(
                    type="call_tool",
                    tool="run_test",
                    args={"pattern": str(outside)},
                ),
            ),
            LLMResponse(text="done", action=AgentAction(type="done")),
        ]
    )
    harness = Harness(
        llm=mock,
        tools=registry_with(tool),
        scope=ScopeGuard(workspace_root=str(workspace)),
        max_steps=5,
    )

    agent_loop("test", harness)

    assert tool.calls == []
    assert any("blocked by scope" in message["content"] for message in harness.context)
