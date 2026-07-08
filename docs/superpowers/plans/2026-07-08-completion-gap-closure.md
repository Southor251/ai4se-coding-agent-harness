# Completion Gap Closure Implementation Plan

> **For agentic workers:** If task-execution workflow skills are available, you may use them to implement this plan task-by-task. Otherwise, execute the plan inline or manually. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the remaining practical gaps after the initial harness build: environment diagnosis, real API readiness, HITL write-loop demonstration, Web startup reliability, and final status documentation.

**Architecture:** Keep the existing self-implemented harness core. Add a small CLI `doctor` command for configuration/runtime diagnosis, a deterministic HITL demo command for write approval workflow, and documentation/scripts that make the current Streamlit theater and API setup repeatable. Avoid starting the React/FastAPI rewrite until the CLI/Web core loop is stable.

**Tech Stack:** Python 3.12, argparse CLI, pytest, ruff, existing `agent_harness` package, Streamlit theater.

## Global Constraints

- Continue development in the sandbox repository unless explicitly syncing to another location.
- No real API keys in source, docs examples, test fixtures, or Git.
- `run_shell` remains unregistered in the default governed runtime.
- Approval can bypass permission ask, but must not bypass `ScopeGuard`.
- Every implementation task must have tests before or alongside code and pass `python scripts/verify_delivery.py`.

---

### Task 1: Add `agent-harness doctor`

**Files:**
- Create: `src/agent_harness/cli/doctor.py`
- Modify: `src/agent_harness/cli/main.py`
- Test: `tests/test_cli_doctor.py`

**Interfaces:**
- Consumes: `load_config_with_profile(config_path, profile_path) -> HarnessConfig`
- Consumes: `build_harness(config, hitl_store_path=None) -> Harness`
- Produces: `run_doctor(config_path: str | None, profile_path: str | None, credential_manager: CredentialManager | None = None) -> list[str]`

- [ ] **Step 1: Write failing tests**

```python
from agent_harness.cli.doctor import run_doctor
from agent_harness.cli.main import main


class FakeCredentialManager:
    def show_status(self):
        return "configured"


def test_doctor_reports_runtime_without_secret(tmp_path):
    profile = tmp_path / "profile.yaml"
    profile.write_text(
        "\n".join(
            [
                f"workspace_root: {tmp_path.as_posix()}",
                "llm:",
                "  provider: openai",
                "  model: test-model",
                "  base_url: https://example.test/v1",
            ]
        ),
        encoding="utf-8",
    )

    lines = run_doctor(None, str(profile), credential_manager=FakeCredentialManager())

    text = "\n".join(lines)
    assert "provider: openai" in text
    assert "model: test-model" in text
    assert "credential: configured" in text
    assert "run_shell: disabled" in text
    assert "https://example.test/v1" in text


def test_doctor_cli_prints_summary(capsys):
    exit_code = main(["doctor", "--profile", "config/personal-harness.yaml"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "agent-harness doctor" in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli_doctor.py -q`  
Expected: FAIL with missing `agent_harness.cli.doctor`.

- [ ] **Step 3: Implement minimal code**

Create `doctor.py` that loads config/profile, builds the governed runtime without HITL store side effects, reports workspace, provider, model, base URL, credential status, tool count, `run_shell` disabled/enabled, memory status, and permission rule count. Do not print credential values.

- [ ] **Step 4: Wire parser**

Register `doctor` in `src/agent_harness/cli/main.py`.

- [ ] **Step 5: Verify**

Run:

```powershell
python -m pytest tests/test_cli_doctor.py -q
python scripts/verify_delivery.py
```

- [ ] **Step 6: Commit**

```powershell
git add src/agent_harness/cli/doctor.py src/agent_harness/cli/main.py tests/test_cli_doctor.py
git commit -m "feat: add runtime doctor command"
```

---

### Task 2: Add deterministic HITL write-loop demo

**Files:**
- Create: `src/agent_harness/cli/smoke.py`
- Modify: `src/agent_harness/cli/main.py`
- Test: `tests/test_cli_smoke.py`

**Interfaces:**
- Produces: `run_hitl_write_smoke(workspace: str, store: str, trace: str) -> list[str]`

- [ ] **Step 1: Write failing tests**

```python
from agent_harness.cli.smoke import run_hitl_write_smoke
from agent_harness.cli.main import main


def test_hitl_write_smoke_creates_pending_request(tmp_path):
    workspace = tmp_path / "workspace"
    store = tmp_path / "requests.json"
    trace = tmp_path / "trace.jsonl"

    lines = run_hitl_write_smoke(str(workspace), str(store), str(trace))

    assert workspace.exists()
    assert store.exists()
    assert any("pending_request:" in line for line in lines)
    assert any("approve_command:" in line for line in lines)


def test_smoke_cli_hitl_write(capsys, tmp_path):
    exit_code = main(
        [
            "smoke",
            "hitl-write",
            "--workspace",
            str(tmp_path / "workspace"),
            "--store",
            str(tmp_path / "requests.json"),
            "--trace",
            str(tmp_path / "trace.jsonl"),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "pending_request:" in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli_smoke.py -q`  
Expected: FAIL with missing module.

- [ ] **Step 3: Implement deterministic demo**

Use `MockLLM` with a `write_file` action against a temporary workspace and permission rule `ask`, then return the pending request id and exact CLI approve command. Do not execute the approval inside this smoke command.

- [ ] **Step 4: Verify**

Run:

```powershell
python -m pytest tests/test_cli_smoke.py -q
python scripts/verify_delivery.py
```

- [ ] **Step 5: Commit**

```powershell
git add src/agent_harness/cli/smoke.py src/agent_harness/cli/main.py tests/test_cli_smoke.py
git commit -m "feat: add hitl write smoke command"
```

---

### Task 3: Harden Web startup documentation

**Files:**
- Modify: `docs/personal_setup.md`
- Modify: `README.md`
- Modify: `docs/final_status.md`

**Interfaces:**
- Consumes: current Streamlit entrypoint `agent-harness web`
- Produces: copy-pasteable Windows commands for reliable startup

- [ ] **Step 1: Add docs**

Document the reliable Streamlit command:

```powershell
.\.venv\Scripts\python.exe -m streamlit run src\agent_harness\web\theater.py --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --global.developmentMode false
```

Also document the visible `PowerShell -NoExit` launcher for long-running local use.

- [ ] **Step 2: Verify docs contain exact command**

Run: `rg "browser.gatherUsageStats false|127.0.0.1:8501" README.md docs/personal_setup.md docs/final_status.md`

- [ ] **Step 3: Commit**

```powershell
git add README.md docs/personal_setup.md docs/final_status.md
git commit -m "docs: harden web startup instructions"
```

---

### Task 4: Final verification and GitHub sync

**Files:**
- Modify: `AGENT_LOG.md`
- Modify: `PLAN.md`

**Interfaces:**
- Consumes: all tasks above
- Produces: final verification record

- [ ] **Step 1: Run verification**

```powershell
python scripts/verify_delivery.py
python -m pytest -q tests/test_cli_doctor.py tests/test_cli_smoke.py
python -m pip wheel --no-deps --no-cache-dir . -w .harness\wheels
```

- [ ] **Step 2: Update logs**

Record completed tasks, commit hashes, verification output, and remaining known gaps.

- [ ] **Step 3: Commit docs**

```powershell
git add AGENT_LOG.md PLAN.md
git commit -m "docs: record completion gap closure"
```

- [ ] **Step 4: Push and verify**

```powershell
git push origin main
git fetch origin --prune
git rev-list --left-right --count origin/main...HEAD
```

Expected: `0 0`.

---

## Self-Review

- **Spec coverage:** This plan addresses the actual remaining practical gaps: GitHub is already synced, so it focuses on real API readiness, HITL write-loop usability, Web startup reliability, final verification, and logs.
- **Placeholder scan:** No task uses TBD/TODO/fill-in placeholders.
- **Type consistency:** `run_doctor(...)` and `run_hitl_write_smoke(...)` signatures are defined before use and referenced consistently.
