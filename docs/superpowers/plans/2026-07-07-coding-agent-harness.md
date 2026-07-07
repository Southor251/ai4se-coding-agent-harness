# Coding Agent Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a teaching-demo Coding Agent Harness with PermissionPolicy, FeedbackSensor, TraceStore, and Agent Loop Theater.

**Architecture:** Python 3.12 monorepo with clear module boundaries. Core loop in `agent/loop.py`, governance in `governance/`, feedback in `feedback/`, trace in `trace/`, plugins in `plugins/`, WebUI in `web/theater.py`. TDD from the start — each task writes failing test first.

**Tech Stack:** Python 3.12, pytest, Streamlit, keyring, PyYAML, Pydantic, OpenAI SDK

## Global Constraints

- All code must be synchronous (no async/await) — dsv4flash async reliability is low
- All core mechanisms must be testable with MockLLM, without real network/LLM
- No enterprise agent frameworks (LangChain, AutoGen, CrewAI, etc.)
- Credentials never hardcoded or committed to Git
- `src/agent_harness/` is the Python package root
- Config files in `config/`, traces in `.harness/trace/`, demos in `demo/`

---

## File Structure

```
src/agent_harness/
├── __init__.py
├── models.py                    # All dataclasses
├── llm/
│   ├── interface.py             # LLMInterface abstract base
│   ├── mock.py                  # MockLLM (preset response queue)
│   └── openai.py                # OpenAILLM (real API)
├── agent/
│   ├── harness.py               # Harness dataclass (holds all components)
│   └── loop.py                  # agent_loop() main loop
├── tools/
│   ├── base.py                  # ToolBase abstract base
│   ├── registry.py              # ToolRegistry
│   └── builtin/
│       ├── read_file.py
│       ├── write_file.py
│       ├── edit_file.py
│       ├── run_shell.py
│       └── run_test.py
├── governance/
│   ├── permission.py            # PermissionPolicy (allow/ask/deny)
│   ├── scope.py                 # ScopeGuard (path fencing)
│   └── hitl.py                  # HITL state machine
├── feedback/
│   ├── classifier.py            # Failure classifier
│   ├── sensor.py                # FeedbackSensor
│   └── heal.py                  # Heal counter
├── trace/
│   └── store.py                 # TraceStore (JSONL)
├── memory/
│   └── scratchpad.py            # Session-level notes
├── config/
│   └── loader.py                # YAML → Pydantic config loader
├── credentials/
│   └── manager.py               # keyring + .env
├── plugins/
│   ├── base.py                  # 5 plugin base classes
│   ├── registry.py              # PluginRegistry
│   ├── hooks.py                 # HookRegistry
│   └── discovery.py             # entry_points discovery (optional)
├── cli/
│   ├── main.py                  # argparse entry point
│   ├── run.py                   # run subcommand
│   └── credentials.py           # credentials subcommand
└── web/
    └── theater.py               # Agent Loop Theater (Streamlit)

tests/
├── __init__.py
├── test_models.py
├── test_llm.py
├── test_loop.py
├── test_tools.py
├── test_permission.py
├── test_scope.py
├── test_hitl.py
├── test_feedback.py
├── test_trace.py
├── test_plugins.py
├── test_config.py
└── test_demo.py

demo/
├── demo_guardrail.py
├── demo_feedback.py
└── demo_scope.py

config/
└── agent-harness.yaml

.harness/trace/          # Runtime trace output (gitignored)
```

---

## Task List

### Task 0.1: Create project skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/agent_harness/__init__.py`
- Create: `tests/__init__.py`
- Create: `Makefile`
- Create: `.gitignore`

**Interfaces:**
- Produces: Installable package `agent_harness` with `pip install -e .`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "agent-harness"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "openai>=1.0",
    "keyring>=24.0",
    "streamlit>=1.28",
    "pyyaml>=6.0",
    "pydantic>=2.0",
]

[project.scripts]
agent-harness = "agent_harness.cli.main:main"

[tool.setuptools.packages.find]
where = ["src"]
```

- [ ] **Step 2: Create package init**

```python
# src/agent_harness/__init__.py
"""A teaching-demo Coding Agent Harness."""
```

- [ ] **Step 3: Create tests init**

```python
# tests/__init__.py
```

- [ ] **Step 4: Create Makefile**

```makefile
.PHONY: test lint clean web demo

test:
	pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/

clean:
	rm -rf .harness/trace/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/

web:
	streamlit run src/agent_harness/web/theater.py

demo:
	python -m demo.demo_guardrail
	python -m demo.demo_feedback
	python -m demo.demo_scope
```

- [ ] **Step 5: Create .gitignore**

```
.env
.harness/
__pycache__/
*.pyc
*.egg-info/
.pytest_cache/
```

- [ ] **Step 6: Verify**

```bash
pip install -e .
python -c "import agent_harness; print('OK')"
# Expected: OK
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: project skeleton"
```

---

### Task 1.1: Define core data models

**Files:**
- Create: `src/agent_harness/models.py`
- Create: `tests/test_models.py`

**Interfaces:**
- Produces: `AgentAction`, `ToolResult`, `TraceRecord`, `Feedback`, `HITLRequest`, `PermissionRule`, `ScopeVerdict` dataclasses

- [ ] **Step 1: Write the failing test**

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

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py -v
# Expected: FAIL - module not found
```

- [ ] **Step 3: Write minimal implementation**

```python
# src/agent_harness/models.py
from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class AgentAction:
    type: Literal["call_tool", "done", "take_note"]
    tool: str | None = None
    args: dict | None = None
    note: str | None = None
    changed_code: bool = False


@dataclass
class ToolResult:
    success: bool
    output: str = ""
    error: str | None = None
    files_changed: list[str] = field(default_factory=list)


@dataclass
class Feedback:
    category: Literal["syntax", "assertion", "timeout", "tool_error", "success"]
    message: str
    raw: str


@dataclass
class TraceRecord:
    step: int
    llm_text: str
    llm_action: AgentAction
    permission_verdict: Literal["allow", "ask", "deny"]
    hitl_status: Literal["pending", "approved", "denied", "timed_out"] | None = None
    tool_result: ToolResult | None = None
    feedback: Feedback | None = None
    context_size: int = 0
    timestamp: float = 0.0


@dataclass
class HITLRequest:
    id: str
    action: AgentAction
    reason: str
    status: Literal["pending", "approved", "denied", "timed_out"]
    created_at: float
    decided_by: Literal["human", "auto_deny", "timeout"] | None = None
    resolved_at: float | None = None


@dataclass
class PermissionRule:
    name: str
    pattern: str
    verdict: Literal["allow", "ask", "deny"]
    rule_type: Literal["path", "command", "regex"]


@dataclass
class ScopeVerdict:
    decision: Literal["inside", "outside", "sensitive"]
    normalized_path: str
    workspace_root: str
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
# Expected: 9 passed
```

- [ ] **Step 5: Commit**

```bash
git add src/agent_harness/models.py tests/test_models.py
git commit -m "feat: core data models"
```

---

### Task 1.2: Implement LLMInterface abstract base

**Files:**
- Create: `src/agent_harness/llm/interface.py`
- Update: `tests/test_llm.py`

**Interfaces:**
- Produces: `LLMInterface` ABC with `call(context, menu) -> LLMResponse`
- `LLMResponse = tuple[str, AgentAction]` or a small dataclass

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm.py
import pytest
from agent_harness.llm.interface import LLMInterface

def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        LLMInterface()  # Abstract class
```

- [ ] **Step 2: Run to verify it fails**

```bash
pytest tests/test_llm.py::test_cannot_instantiate_abstract -v
# Expected: FAIL
```

- [ ] **Step 3: Write minimal implementation**

```python
# src/agent_harness/llm/interface.py
from abc import ABC, abstractmethod
from typing import Any


class LLMResponse:
    """Response from an LLM call."""
    def __init__(self, text: str, action: Any):
        self.text = text
        self.action = action


class LLMInterface(ABC):
    @abstractmethod
    def call(self, context: list[dict], menu: list[dict]) -> LLMResponse:
        ...
```

- [ ] **Step 4: Run to verify it passes**

```bash
pytest tests/test_llm.py::test_cannot_instantiate_abstract -v
# Expected: PASS
```

- [ ] **Step 5: Commit**

```bash
git add src/agent_harness/llm/interface.py tests/test_llm.py
git commit -m "feat: LLMInterface abstract base"
```

---

[Remaining tasks T1.3 through T10.9 follow the same TDD pattern. See PLAN.md for the full task list — each task follows the same structure: write failing test → run (red) → implement → run (green) → commit.]

---

## Execution Handoff

**Plan complete. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for parallel worktrees (governance, feedback, trace can run in parallel after core loop).

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for review.

**Which approach?**