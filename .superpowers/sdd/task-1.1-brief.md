# Task 1.1: Define core data models

**Files:**
- Create: `src/agent_harness/models.py`
- Create: `tests/test_models.py`

**Goal:** All core dataclasses for the harness.

**Dependencies:** T0.1 (package skeleton)

**Verification:** 9 tests pass

## Data Models to Implement

See `SPEC.md §6` for full definitions. Implement these dataclasses:

- `AgentAction` — type, tool, args, note, changed_code
- `ToolResult` — success, output, error, files_changed
- `Feedback` — category (syntax/assertion/timeout/tool_error/success), message, raw
- `TraceRecord` — step, llm_text, llm_action, permission_verdict, hitl_status, tool_result, feedback, context_size, timestamp
- `HITLRequest` — id, action, reason, status, created_at, decided_by, resolved_at
- `PermissionRule` — name, pattern, verdict, rule_type
- `ScopeVerdict` — decision, normalized_path, workspace_root

All use `from dataclasses import dataclass, field` and `from typing import Literal`.

## Tests

```python
# tests/test_models.py
from agent_harness.models import AgentAction, ToolResult, TraceRecord, Feedback, HITLRequest, PermissionRule, ScopeVerdict

def test_agent_action_call_tool():
    action = AgentAction(type="call_tool", tool="read_file", args={"path": "test.py"})
    assert action.type == "call_tool"
    assert action.tool == "read_file"

def test_agent_action_done():
    action = AgentAction(type="done")
    assert action.type == "done"

def test_tool_result_success():
    result = ToolResult(success=True, output="file content")
    assert result.success
    assert result.output == "file content"

def test_tool_result_error():
    result = ToolResult(success=False, error="file not found")
    assert not result.success

def test_trace_record():
    record = TraceRecord(step=1, llm_text="hello", llm_action=AgentAction(type="done"), permission_verdict="allow")
    assert record.step == 1
    assert record.permission_verdict == "allow"

def test_feedback():
    fb = Feedback(category="assertion", message="expected 5 but got 3", raw="AssertionError: ...")
    assert fb.category == "assertion"

def test_hitl_request():
    req = HITLRequest(id="1", action=AgentAction(type="call_tool", tool="rm"), reason="dangerous", status="pending", created_at=100.0)
    assert req.status == "pending"

def test_permission_rule():
    rule = PermissionRule(name="deny rm", pattern="rm -rf", verdict="deny", rule_type="command")
    assert rule.verdict == "deny"

def test_scope_verdict():
    v = ScopeVerdict(decision="outside", normalized_path="/etc/passwd", workspace_root="/workspace")
    assert v.decision == "outside"
```