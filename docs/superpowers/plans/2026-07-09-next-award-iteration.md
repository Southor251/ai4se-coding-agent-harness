# Next Award Iteration Implementation Plan

> **For agentic workers:** If task-execution workflow skills are available, you may use them to implement this plan task-by-task. Otherwise, execute the plan inline or manually. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the harness from a polished demo console toward a competition-grade governed coding-agent workbench with better project awareness, safer HITL review, stronger replay, and judge-ready export evidence.

**Architecture:** Keep the existing Python harness, CLI, Streamlit console, trace store, and HITL store as the source of truth. Add small tested service/view-model modules before UI changes, and keep Streamlit as the official runnable UI until a replacement frontend has live API parity. Avoid new framework dependencies in this round unless a task explicitly proves the value.

**Tech Stack:** Python 3.12, Streamlit, pytest, ruff, existing `agent_harness.web.services`, `TraceStore`, `HITLStore`, safe built-in tools, browser smoke verification.

## Global Constraints

- Work in `C:\Users\hp\Documents\Codex\2026-07-07\https-opncd-ai-share-1wbl482n\work\ai4se-coding-agent-harness`.
- Keep `run_shell` outside the default governed runtime.
- Do not commit API keys, `.env`, keyring data, screenshots containing secrets, or `.harness` runtime cache.
- `scripts/verify_delivery.py` must stay mock-config based and must not call the real API.
- Every implementation task must use TDD: failing test, implementation, focused verification, full delivery verification, browser verification for visible UI work, then commit.
- Update `AGENT_LOG.md`, `PLAN.md` or this plan file, `README.md` where user-facing behavior changes, and the external project record.

---

## Multi-Round Final Vision

### Final Product Shape

The final application should be a local governed coding-agent workbench:

- A user chooses a project workspace, provider profile, and task goal.
- The agent can inspect files, search text, read batches, propose edits, run tests, and record every step.
- All writes are governed by scope, permission rules, and HITL approval.
- The UI shows project context, trace replay, tool results, pending approvals, provider status, and exportable evidence.
- A judge or instructor can run a deterministic demo without a key, then optionally run a real read-only API smoke with a configured key.

### Round 1: Application Credibility

Focus: make the current Streamlit app feel like a real workbench.

- Project workspace browser.
- Trace replay improvements.
- HITL diff/impact preview.
- Provider and safety status panel.
- Exportable judge report.

### Round 2: Real Task Ergonomics

Focus: reduce friction for actual personal use.

- Task templates for read-only review, small edit, test repair, and documentation update.
- Run history with named sessions.
- Checkpoint metadata before writes.
- Better approval resume flow with explicit final result display.
- More provider profile diagnostics.

### Round 3: Stronger Engineering Loop

Focus: improve coding-agent quality without expanding unsafe authority.

- Patch planning action before write execution.
- Test selection helper backed by safe project scanning.
- Failure-classified trace filters.
- Exportable diff/test evidence.
- Optional real API smoke suite with explicit user approval.

### Round 4: Productization

Focus: package and presentation.

- Stable desktop/local launch command.
- Static or FastAPI frontend only if it reaches parity with Streamlit task run, trace, HITL, and demo.
- Installation validation with `doctor`.
- Release checklist and final competition walkthrough.

---

## This Round Scope

This round should complete six independently testable tasks:

1. App state and session view models.
2. Read-only project workspace explorer.
3. Richer trace replay and filtering.
4. HITL action impact preview.
5. Provider/safety status panel.
6. Judge report export and final QA.

The round should not build a full IDE, terminal, multi-file editor, or a new React app.

---

### Task 1: App State And Session View Models

**Files:**
- Create: `src/agent_harness/web/session_models.py`
- Modify: `src/agent_harness/web/theater.py`
- Test: `tests/test_web_session_models.py`

**Interfaces:**
- Produces: `active_paths(default_trace: str, default_store: str, session: dict) -> dict[str, str]`
- Produces: `run_badges(summary: dict, hitl_counts: dict) -> list[dict[str, str]]`

- [ ] **Step 1: Write failing tests**

```python
from agent_harness.web.session_models import active_paths, run_badges


def test_active_paths_prefers_session_values():
    session = {"active_trace_path": "runs/demo.jsonl", "active_hitl_store_path": "hitl/demo.json"}

    result = active_paths("runs/latest.jsonl", "hitl/requests.json", session)

    assert result["trace_path"] == "runs/demo.jsonl"
    assert result["hitl_store_path"] == "hitl/demo.json"


def test_run_badges_returns_display_values():
    badges = run_badges(
        {"steps": 3, "tool_calls": 2, "denials": 1, "feedback_events": 1},
        {"pending": 4},
    )

    assert badges[0] == {"label": "Steps", "value": "3"}
    assert {"label": "Pending HITL", "value": "4"} in badges
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_session_models.py
```

Expected: fail with `ModuleNotFoundError`.

- [ ] **Step 2: Implement the module**

```python
def active_paths(default_trace: str, default_store: str, session: dict) -> dict[str, str]:
    return {
        "trace_path": str(session.get("active_trace_path") or default_trace),
        "hitl_store_path": str(session.get("active_hitl_store_path") or default_store),
    }


def run_badges(summary: dict, hitl_counts: dict) -> list[dict[str, str]]:
    return [
        {"label": "Steps", "value": str(summary.get("steps", 0))},
        {"label": "Tool calls", "value": str(summary.get("tool_calls", 0))},
        {"label": "Denials", "value": str(summary.get("denials", 0))},
        {"label": "Feedback", "value": str(summary.get("feedback_events", 0))},
        {"label": "Pending HITL", "value": str(hitl_counts.get("pending", 0))},
    ]
```

- [ ] **Step 3: Wire `theater.py` to use these helpers**

Replace inline session-path selection and metric construction with `active_paths()` and `run_badges()`. Keep labels unchanged.

- [ ] **Step 4: Verify and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_session_models.py tests\test_theater.py tests\test_web_services.py
.\.venv\Scripts\python.exe -m ruff check src\agent_harness\web tests\test_web_session_models.py tests\test_theater.py tests\test_web_services.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
git add src/agent_harness/web/session_models.py src/agent_harness/web/theater.py tests/test_web_session_models.py AGENT_LOG.md
git commit -m "feat: add web session view models"
```

---

### Task 2: Read-Only Project Workspace Explorer

**Files:**
- Modify: `src/agent_harness/web/services.py`
- Modify: `src/agent_harness/web/theater.py`
- Test: `tests/test_web_services.py`

**Interfaces:**
- Produces: `workspace_tree(root: str, limit: int = 200) -> list[dict]`
- Produces: `file_preview(root: str, path: str, max_chars: int = 4000) -> dict`

- [ ] **Step 1: Write failing tests**

```python
from agent_harness.web.services import file_preview, workspace_tree


def test_workspace_tree_lists_relative_files(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('ok')", encoding="utf-8")

    rows = workspace_tree(str(tmp_path))

    assert rows == [{"path": "src/app.py", "kind": "file"}]


def test_file_preview_blocks_outside_path(tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    preview = file_preview(str(tmp_path), str(outside))

    assert preview["success"] is False
    assert "outside workspace" in preview["error"]
```

- [ ] **Step 2: Implement read-only helpers**

Use `Path(root).resolve()` and `Path(path).resolve()`. Only return content when `target.is_relative_to(root_path)` is true. Return UTF-8 text with replacement on decode errors.

- [ ] **Step 3: Add UI tab or section**

Add a `Project` tab in `theater.py`:

- Workspace root input.
- Dataframe of relative files.
- Text input for preview path.
- Preview text area.

- [ ] **Step 4: Browser verify**

Open `http://127.0.0.1:8501`, confirm the `Project` tab is visible and previewing `README.md` does not overlap controls.

- [ ] **Step 5: Verify and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_services.py tests\test_theater.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
git add src/agent_harness/web/services.py src/agent_harness/web/theater.py tests/test_web_services.py AGENT_LOG.md
git commit -m "feat: add read-only project explorer"
```

---

### Task 3: Richer Trace Replay And Filtering

**Files:**
- Modify: `src/agent_harness/web/services.py`
- Modify: `src/agent_harness/web/theater.py`
- Test: `tests/test_web_services.py`

**Interfaces:**
- Produces: `filter_timeline(rows: list[dict], state: str = "all") -> list[dict]`
- Produces: `trace_step_detail(trace_path: str, step: int) -> dict`

- [ ] **Step 1: Write failing tests**

```python
from agent_harness.web.services import filter_timeline, trace_step_detail


def test_filter_timeline_keeps_matching_state():
    rows = [{"step": 1, "state": "tool"}, {"step": 2, "state": "pending"}]

    assert filter_timeline(rows, "pending") == [{"step": 2, "state": "pending"}]
    assert filter_timeline(rows, "all") == rows


def test_trace_step_detail_returns_selected_step(tmp_path):
    trace_path = tmp_path / "trace.jsonl"
    run_task("say done", trace_path=str(trace_path))

    detail = trace_step_detail(str(trace_path), 1)

    assert detail["step"] == 1
    assert "llm_action" in detail
```

- [ ] **Step 2: Implement helpers**

`filter_timeline` returns all rows for `"all"` and exact state matches otherwise. `trace_step_detail` loads trace records and returns the first matching step or raises `ValueError(f"Trace step not found: {step}")`.

- [ ] **Step 3: Update Trace tab**

Add a state selectbox with values `all`, `tool`, `pending`, `blocked`, `done`. Use filtered rows for the governance rail, while keeping the step slider over full records.

- [ ] **Step 4: Verify and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_services.py tests\test_theater.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
git add src/agent_harness/web/services.py src/agent_harness/web/theater.py tests/test_web_services.py AGENT_LOG.md
git commit -m "feat: add trace replay filtering"
```

---

### Task 4: HITL Action Impact Preview

**Files:**
- Modify: `src/agent_harness/web/services.py`
- Modify: `src/agent_harness/web/theater.py`
- Test: `tests/test_web_services.py`

**Interfaces:**
- Produces: `hitl_impact_preview(store_path: str, request_id: str, workspace_root: str) -> dict`

- [ ] **Step 1: Write failing tests**

```python
from agent_harness.web.services import hitl_impact_preview


def test_hitl_impact_preview_for_write_file(tmp_path):
    store_path = tmp_path / "requests.json"
    manager = HITLManager(store=HITLStore(store_path))
    request = manager.create_request(
        AgentAction(type="call_tool", tool="write_file", args={"path": str(tmp_path / "note.txt"), "content": "hello"}),
        "review",
    )

    preview = hitl_impact_preview(str(store_path), request.id, str(tmp_path))

    assert preview["safe_to_preview"] is True
    assert preview["tool"] == "write_file"
    assert preview["target"] == str(tmp_path / "note.txt")
    assert preview["would_create"] is True
```

- [ ] **Step 2: Implement preview**

For `write_file`, report `would_create`, `existing_chars`, and `new_chars`. For `replace_once` and `edit_file`, report whether target exists and old/new text lengths. If target path is outside workspace, return `safe_to_preview: False` and error `outside workspace`.

- [ ] **Step 3: Update HITL tab**

Below request detail JSON, show an `Impact preview` JSON block. Do not execute tools in preview.

- [ ] **Step 4: Verify and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_services.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
git add src/agent_harness/web/services.py src/agent_harness/web/theater.py tests/test_web_services.py AGENT_LOG.md
git commit -m "feat: add hitl impact preview"
```

---

### Task 5: Provider And Safety Status Panel

**Files:**
- Modify: `src/agent_harness/web/services.py`
- Modify: `src/agent_harness/web/theater.py`
- Test: `tests/test_web_services.py`

**Interfaces:**
- Produces: `runtime_status(config_path: str, profile_path: str | None) -> dict`

- [ ] **Step 1: Write failing test**

```python
from agent_harness.web.services import runtime_status


def test_runtime_status_reports_mock_provider_and_shell_disabled(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("workspace_root: .\nllm:\n  provider: mock\n", encoding="utf-8")

    status = runtime_status(str(config_path), None)

    assert status["provider"] == "mock"
    assert status["run_shell"] == "disabled"
    assert status["tool_count"] >= 1
```

- [ ] **Step 2: Implement status helper**

Load config with `load_config_with_profile`, build harness, inspect provider, model, base URL, workspace root, tool names, permission rule count, memory enabled, and whether `run_shell` is registered.

- [ ] **Step 3: Add UI panel**

Add `Safety` tab or sidebar expander:

- Provider/model/base URL.
- Credential status only as configured/not configured.
- `run_shell` status.
- Permission rule count.
- Tool names.

- [ ] **Step 4: Verify and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_services.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
git add src/agent_harness/web/services.py src/agent_harness/web/theater.py tests/test_web_services.py AGENT_LOG.md
git commit -m "feat: add runtime safety status panel"
```

---

### Task 6: Judge Report Export And Final QA

**Files:**
- Create: `src/agent_harness/web/reporting.py`
- Modify: `src/agent_harness/web/theater.py`
- Create: `tests/test_web_reporting.py`
- Modify: `docs/demo_walkthrough.md`

**Interfaces:**
- Produces: `build_judge_report(trace_path: str, store_path: str) -> str`

- [ ] **Step 1: Write failing test**

```python
from agent_harness.web.demo_data import ensure_demo_trace
from agent_harness.web.reporting import build_judge_report


def test_build_judge_report_contains_summary_and_hitl(tmp_path):
    trace_path = tmp_path / "demo.jsonl"
    store_path = tmp_path / "requests.json"
    ensure_demo_trace(str(trace_path), str(store_path))

    report = build_judge_report(str(trace_path), str(store_path))

    assert "# Agent Harness Judge Report" in report
    assert "Steps: 3" in report
    assert "Pending HITL: 1" in report
    assert "run_shell default: disabled" in report
```

- [ ] **Step 2: Implement Markdown report**

The report should include:

- Trace path and HITL store path.
- Summary counts.
- Timeline rows.
- HITL overview.
- Safety boundary: `run_shell default: disabled`.
- Verification commands.

- [ ] **Step 3: Add UI download**

Add a `Download judge report` button using `st.download_button` with filename `agent-harness-judge-report.md`.

- [ ] **Step 4: Final browser QA**

With Streamlit running:

```powershell
.\.venv\Scripts\python.exe scripts\verify_web_ui.py --url http://127.0.0.1:8501
```

Use browser inspection to confirm:

- Project, Run, Trace, HITL, and Safety/report controls are visible.
- Text does not overlap at 1280px width.
- Demo walkthrough still loads.

- [ ] **Step 5: Full verification and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_web_reporting.py tests/test_web_services.py tests/test_theater.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
.\.venv\Scripts\python.exe scripts\verify_web_ui.py --url http://127.0.0.1:8501
git add src/agent_harness/web/reporting.py src/agent_harness/web/theater.py tests/test_web_reporting.py docs/demo_walkthrough.md AGENT_LOG.md README.md
git commit -m "feat: add judge report export"
```

---

## Final Verification Checklist

After all tasks:

```powershell
.\.venv\Scripts\python.exe scripts\verify_delivery.py
.\.venv\Scripts\python.exe scripts\verify_web_ui.py --url http://127.0.0.1:8501
.\.venv\Scripts\python.exe -m pip wheel --no-deps --no-cache-dir . -w .harness\wheels
git status --short
```

Expected:

- `verify_delivery.py` exits 0.
- `verify_web_ui.py` exits 0.
- Wheel builds successfully.
- Worktree is clean after commits.

## Self-Review

- **Spec coverage:** The plan covers the next practical gap after the completed UI pass: app state, project awareness, replay, safer HITL review, safety/provider status, and exportable judging evidence.
- **Placeholder scan:** No task contains placeholder-only steps. Each task names files, functions, tests, commands, expected outcomes, and commit messages.
- **Type consistency:** Function names used by later tasks match the interfaces declared in each task: `active_paths`, `run_badges`, `workspace_tree`, `file_preview`, `filter_timeline`, `trace_step_detail`, `hitl_impact_preview`, `runtime_status`, and `build_judge_report`.
