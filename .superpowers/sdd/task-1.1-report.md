# Task 1.1: Define Core Data Models — Report

## What Was Implemented

Created `src/agent_harness/models.py` with 7 dataclasses as specified in SPEC.md §6:

- **AgentAction** — `type` (call_tool/done/take_note), `tool`, `args`, `note`, `changed_code`
- **ToolResult** — `success`, `output`, `error`, `files_changed`
- **TraceRecord** — `step`, `llm_text`, `llm_action`, `permission_verdict`, `hitl_status`, `tool_result`, `feedback`, `context_size`, `timestamp`
- **Feedback** — `category` (syntax/assertion/timeout/tool_error/success), `message`, `raw`
- **HITLRequest** — `id`, `action`, `reason`, `status`, `created_at`, `decided_by`, `resolved_at`
- **PermissionRule** — `name`, `pattern`, `verdict`, `rule_type`
- **ScopeVerdict** — `decision` (inside/outside/sensitive), `normalized_path`, `workspace_root`

## TDD Evidence

### RED (before implementation)
```
ERROR tests/test_models.py
ModuleNotFoundError: No module named 'agent_harness.models'
```

### GREEN (after implementation)
```
tests/test_models.py::test_agent_action_call_tool PASSED  [11%]
tests/test_models.py::test_agent_action_done      PASSED  [22%]
tests/test_models.py::test_tool_result_success     PASSED  [33%]
tests/test_models.py::test_tool_result_error       PASSED  [44%]
tests/test_models.py::test_trace_record            PASSED  [55%]
tests/test_models.py::test_feedback                PASSED  [66%]
tests/test_models.py::test_hitl_request            PASSED  [77%]
tests/test_models.py::test_permission_rule         PASSED  [88%]
tests/test_models.py::test_scope_verdict           PASSED  [100%]
============================== 9 passed in 0.11s ==============================
```

## Files Changed

| File | Action |
|------|--------|
| `src/agent_harness/models.py` | Created (54 lines) |
| `tests/test_models.py` | Created (65 lines) |

## Self-Review Findings

- All fields match SPEC.md §6 exactly, including `Literal` types, `field(default_factory=list)` for mutable defaults, and forward reference for `TraceRecord.feedback`
- Tests cover all 7 models with 9 test functions as specified in the brief
- No unused imports; no comments added
- Test file uses `from agent_harness.models import ...` matching the package's `src` layout

## Concerns

None. The models are straightforward dataclasses with no business logic — pure data definition.