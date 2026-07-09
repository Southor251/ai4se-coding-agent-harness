# Award-Level UI Iteration Implementation Plan

> **For agentic workers:** If task-execution workflow skills are available, you may use them to implement this plan task-by-task. Otherwise, execute the plan inline or manually. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current usable harness into a polished, competition-ready local application with a clear visual identity, strong task workflow, trace auditability, HITL ergonomics, and browser-verified presentation quality.

**Architecture:** Keep the already-verified Python harness/runtime as the source of truth. First harden the Streamlit console into a polished demo surface because it is running, tested, and low-risk. Then add a static HTML/CSS/JS “Showcase Console” served from the same repo if Streamlit’s layout limits prevent a competition-grade presentation; the static console will call testable service endpoints only after those contracts are implemented. Do not replace the self-implemented harness core with an agent framework.

**Tech Stack:** Python 3.12, Streamlit, pytest, ruff, existing harness modules, browser screenshot verification. Optional later stage: FastAPI + static HTML/CSS/JS, no React until the API contract is stable.

## Execution Status - 2026-07-09

All six planned tasks were implemented in the sandbox copy with TDD-style red/green checks, browser verification for visible UI changes, and per-slice commits.

| Task | Status | Commit |
| --- | --- | --- |
| Task 1: UI view models | Complete | `3b827ea feat: add ui trace view models` |
| Task 2: governance rail layout | Complete | `a7249d6 feat: add governance rail UI` |
| Task 3: HITL queue ergonomics | Complete | `99da14b feat: improve hitl queue ergonomics` |
| Task 4: demo walkthrough | Complete | `17fe8f8 feat: add judge demo walkthrough` |
| Task 5: Web UI smoke verifier | Complete | `6c39741 test: add web ui smoke verifier` |
| Task 6: static HTML spike | Complete | `df91ba9 feat: add static console spike` |

Latest full verification after Task 6 implementation:

- `.venv\Scripts\python.exe -m pytest -q ...` focused UI/server set -> `21 passed`
- `.venv\Scripts\python.exe -m ruff check ...` -> `All checks passed!`
- `.venv\Scripts\python.exe scripts\verify_delivery.py` -> `180 passed`, ruff passed, CLI run/list smoke passed, high-confidence secret scan passed
- `.venv\Scripts\python.exe -m pip wheel --no-deps --no-cache-dir . -w .harness\wheels` -> wheel built successfully
- Wheel content check confirmed `agent_harness/server/static/index.html`, `styles.css`, and `app.js` are included

Decision after Task 6: Streamlit remains the official runnable competition demo UI. The static HTML console is a packaged visual prototype and future API-contract target, not a replacement for the working governed Web console.

## Global Constraints

- Work in `C:\Users\hp\Documents\Codex\2026-07-07\https-opncd-ai-share-1wbl482n\work\ai4se-coding-agent-harness`.
- Keep `run_shell` outside the default governed runtime.
- Never commit API keys, `.env`, keyring data, screenshots containing secrets, or `.harness` runtime cache.
- Delivery verification must not call the real API; `scripts/verify_delivery.py` must stay mock-config based.
- Real API smoke may be run manually only with user-approved keyring access.
- Every implementation slice must include tests, `python scripts/verify_delivery.py`, browser verification for UI-visible changes, and a commit.
- Update `AGENT_LOG.md`, `PLAN.md`, and the external project record after each completed slice.

---

## Skill And Community Research

### Installed Skills

- Installed OpenAI curated `playwright` skill for browser-level UI validation.
- Installed OpenAI curated `screenshot` skill for screenshot-based visual QA.
- Existing useful skills in this environment:
  - `frontend-design`
  - `webapp-testing`
  - `web-artifacts-builder`
  - `browser:control-in-app-browser`

Restart Codex after this session to expose the newly installed `playwright` and `screenshot` skills in the normal skill list.

### Community Search Result

GitHub searches were run on 2026-07-09 with star count and recent update as the primary criteria:

- `claude code frontend design skill`
  - `LeeorNahum/claude-code-frontend-design-skill`: 1 star, updated 2026-06-08
  - `rohithgoud30/claude-code-frontend-design-skills`: 0 stars, updated 2025-12-27
  - `taksimlagirio-sudo/frontend-design-skill`: 0 stars, updated 2026-02-13
- `claude code skills frontend`
  - `samCrock/ccss`: 1 star, updated 2026-06-19
  - `orgershoni/orgersh-skills`: 1 star, updated 2026-07-03
  - `haonL-7/frontend-workflow`: 0 stars, updated 2026-06-04
  - `haonL-7/frontend-patterns`: 0 stars, updated 2026-06-04
- `codex skills frontend`
  - `Sunwood-ai-labs/frontend-design-skill`: 0 stars, updated 2026-05-05

Decision: do not install these community repos automatically. Their recency is acceptable, but stars are too low to treat them as reliable. Use their names only as weak signals that “frontend workflow”, “frontend patterns”, and “design skill” are useful categories; rely on installed curated skills and local verification instead.

---

## Capability Estimate

What I can realistically deliver well in this repo:

- A polished Streamlit console with coherent visual identity, better layout, stronger trace/HITL workflows, and screenshot-tested responsiveness.
- A robust service/view-model layer for UI data, so future React/FastAPI work does not duplicate harness logic.
- A demo script that proves real API, trace, and HITL workflows without exposing secrets.
- Browser-verified screenshots and regression tests after each visual slice.

What I should not promise in one pass:

- A full Codex/OpenCode-grade IDE with terminal, editor, project explorer, diff merge, multi-file patch authoring, and collaboration.
- A secure OS-level sandbox. This harness remains application-level governance.
- A large React/FastAPI rewrite without first locking API contracts and tests.

Competition strategy: produce a refined, credible, defensible demo that highlights governance, trace audit, HITL approval, and real API integration. A smaller polished system beats a half-finished IDE clone.

---

## Design Direction

Subject: a university-level governed coding-agent workbench.

Audience: course judges, instructors, and technically literate students.

Single job: show that this is not just a chatbot wrapper, but a controlled, inspectable software engineering harness.

Design tokens:

- `Ink`: `#17201B` for primary text.
- `Lab green`: `#0F2A23` for sidebar and governance surfaces.
- `Trace blue`: `#2B6CB0` for tool and trace records.
- `Review amber`: `#B7791F` for pending HITL.
- `Paper`: `#F7F8F5` for background.
- `Panel`: `#FFFFFF` for cards and work areas.

Typography:

- Display: system UI with heavier weight, restrained and workbench-like.
- Body: system UI, normal weight, dense but readable.
- Data/codes: monospace in trace, action JSON, and command blocks.

Signature element:

- A “governance rail” that visually ties each task to four states: model decision, permission verdict, tool result, feedback/HITL. This is the distinctive project-specific feature, not a decorative motif.

---

### Task 1: UI View Models For Trace And HITL

**Files:**
- Modify: `src/agent_harness/web/services.py`
- Modify: `src/agent_harness/web/theater.py`
- Test: `tests/test_web_services.py`
- Test: `tests/test_theater.py`

**Interfaces:**
- Consumes: `TraceStore.load(path) -> list[dict]`
- Produces: `trace_timeline(trace_path: str) -> list[dict]`
- Produces: `hitl_overview(store_path: str) -> dict[str, int]`

- [ ] **Step 1: Write failing trace timeline test**

Add this to `tests/test_web_services.py`:

```python
def test_trace_timeline_marks_governance_states(tmp_path):
    trace_path = tmp_path / "trace.jsonl"
    run_task("say done", trace_path=str(trace_path))

    rows = trace_timeline(str(trace_path))

    assert rows[0]["step"] == 1
    assert rows[0]["state"] in {"done", "tool", "blocked", "pending"}
    assert "permission" in rows[0]
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_services.py::test_trace_timeline_marks_governance_states
```

Expected: FAIL because `trace_timeline` does not exist.

- [ ] **Step 2: Implement `trace_timeline`**

Add to `src/agent_harness/web/services.py`:

```python
def trace_timeline(trace_path: str = DEFAULT_TRACE_PATH) -> list[dict]:
    rows = []
    for record in TraceStore.load(trace_path):
        action = record.get("llm_action") or {}
        permission = record.get("permission_verdict", "")
        hitl = record.get("hitl_status") or ""
        action_type = action.get("type", "")
        if hitl == "pending":
            state = "pending"
        elif permission == "deny":
            state = "blocked"
        elif action_type == "call_tool":
            state = "tool"
        elif action_type == "done":
            state = "done"
        else:
            state = action_type or "unknown"
        rows.append(
            {
                "step": record.get("step"),
                "state": state,
                "action": action_type,
                "tool": action.get("tool") or "",
                "permission": permission,
                "hitl": hitl,
            }
        )
    return rows
```

- [ ] **Step 3: Implement `hitl_overview`**

Add test:

```python
def test_hitl_overview_counts_statuses(tmp_path):
    store_path = tmp_path / "requests.json"
    manager = HITLManager(store=HITLStore(store_path))
    manager.create_request(AgentAction(type="call_tool", tool="write_file"), "review")

    overview = hitl_overview(str(store_path))

    assert overview["pending"] == 1
    assert overview["approved"] == 0
    assert overview["denied"] == 0
```

Implementation:

```python
def hitl_overview(store_path: str = DEFAULT_HITL_STORE_PATH) -> dict[str, int]:
    counts = {"pending": 0, "approved": 0, "denied": 0, "timed_out": 0}
    for request in HITLStore(store_path).load():
        counts[request.status] = counts.get(request.status, 0) + 1
    return counts
```

- [ ] **Step 4: Verify**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_services.py tests\test_theater.py
.\.venv\Scripts\python.exe -m ruff check src\agent_harness\web tests\test_web_services.py tests\test_theater.py
```

- [ ] **Step 5: Commit**

```powershell
git add src/agent_harness/web/services.py tests/test_web_services.py tests/test_theater.py
git commit -m "feat: add ui trace view models"
```

---

### Task 2: Competition-Grade Streamlit Layout

**Files:**
- Modify: `src/agent_harness/web/theater.py`
- Test: `tests/test_theater.py`

**Interfaces:**
- Consumes: `trace_timeline(trace_path: str) -> list[dict]`
- Consumes: `hitl_overview(store_path: str) -> dict[str, int]`

- [ ] **Step 1: Add UI helper tests**

Add pure helper functions in `theater.py` and tests first:

```python
def test_status_tone_maps_states():
    assert status_tone("pending") == "review"
    assert status_tone("blocked") == "blocked"
    assert status_tone("done") == "done"
    assert status_tone("tool") == "tool"
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_theater.py::test_status_tone_maps_states
```

Expected: FAIL because `status_tone` does not exist.

- [ ] **Step 2: Implement tone helper**

```python
def status_tone(state: str) -> str:
    return {
        "pending": "review",
        "blocked": "blocked",
        "done": "done",
        "tool": "tool",
    }.get(state, "neutral")
```

- [ ] **Step 3: Replace linear trace display with governance rail**

In `main`, inside Trace tab:

- Show timeline rows as compact markdown badges:
  - `pending` -> amber
  - `blocked` -> red
  - `tool` -> blue
  - `done` -> green
- Keep the existing text area for LLM output.
- Keep the JSON action panel.
- Keep the tool result panel.

Add CSS classes:

```css
.rail-row { border-left: 4px solid #2B6CB0; padding: 8px 10px; margin: 6px 0; background: #fff; border-radius: 8px; }
.rail-review { border-left-color: #B7791F; }
.rail-blocked { border-left-color: #C53030; }
.rail-done { border-left-color: #2F855A; }
```

- [ ] **Step 4: Browser verify**

Start Streamlit:

```powershell
.\.venv\Scripts\python.exe -m streamlit run src\agent_harness\web\theater.py --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --global.developmentMode false
```

Open `http://127.0.0.1:8501` and verify:

- title is visible
- metric cards are readable
- Run / Trace / HITL tabs are visible
- trace rail rows are visible when a trace exists
- no overlapping text at 1280px width

- [ ] **Step 5: Verify and commit**

```powershell
.\.venv\Scripts\python.exe scripts\verify_delivery.py
git add src/agent_harness/web/theater.py tests/test_theater.py
git commit -m "feat: add governance rail UI"
```

---

### Task 3: HITL Queue Ergonomics

**Files:**
- Modify: `src/agent_harness/web/services.py`
- Modify: `src/agent_harness/web/theater.py`
- Test: `tests/test_web_services.py`

**Interfaces:**
- Produces: `request_detail(store_path: str, request_id: str) -> dict`

- [ ] **Step 1: Test request detail**

```python
def test_request_detail_includes_action_args(tmp_path):
    store_path = tmp_path / "requests.json"
    manager = HITLManager(store=HITLStore(store_path))
    request = manager.create_request(
        AgentAction(type="call_tool", tool="write_file", args={"path": "note.txt", "content": "hello"}),
        "review",
    )

    detail = request_detail(str(store_path), request.id)

    assert detail["id"] == request.id
    assert detail["tool"] == "write_file"
    assert detail["args"]["path"] == "note.txt"
```

- [ ] **Step 2: Implement request detail**

```python
def request_detail(store_path: str, request_id: str) -> dict:
    for request in HITLStore(store_path).load():
        if request.id == request_id:
            return {
                "id": request.id,
                "status": request.status,
                "tool": request.action.tool or "",
                "args": request.action.args or {},
                "reason": request.reason,
                "step": request.step,
            }
    raise ValueError(f"HITL request not found: {request_id}")
```

- [ ] **Step 3: UI**

In the HITL tab:

- Put pending requests first.
- Let the user select a request from a dropdown instead of manually typing id.
- Show the action args as JSON before approval.
- Keep manual id input as an advanced fallback.

- [ ] **Step 4: Verify**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_services.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
```

- [ ] **Step 5: Commit**

```powershell
git add src/agent_harness/web/services.py src/agent_harness/web/theater.py tests/test_web_services.py
git commit -m "feat: improve hitl queue ergonomics"
```

---

### Task 4: Demo Mode And Judge Walkthrough

**Files:**
- Create: `src/agent_harness/web/demo_data.py`
- Modify: `src/agent_harness/web/theater.py`
- Create: `docs/demo_walkthrough.md`
- Test: `tests/test_web_demo_data.py`

**Interfaces:**
- Produces: `ensure_demo_trace(trace_path: str, store_path: str) -> dict[str, str]`

- [ ] **Step 1: Test demo data creation**

```python
from agent_harness.web.demo_data import ensure_demo_trace


def test_ensure_demo_trace_creates_trace_and_hitl(tmp_path):
    trace_path = tmp_path / "demo.jsonl"
    store_path = tmp_path / "requests.json"

    result = ensure_demo_trace(str(trace_path), str(store_path))

    assert result["trace_path"] == str(trace_path)
    assert trace_path.exists()
    assert store_path.exists()
```

- [ ] **Step 2: Implement demo data**

Use deterministic `TraceStore` and `HITLStore` to create:

- one read tool step
- one write action pending HITL step
- one done step

No real API call.

- [ ] **Step 3: UI button**

Add sidebar button `Load demo walkthrough`:

- creates demo trace/store
- sets session state trace path
- shows a success message

- [ ] **Step 4: Write judge walkthrough**

Create `docs/demo_walkthrough.md` with exact steps:

1. Run `python scripts/verify_delivery.py`.
2. Start Streamlit.
3. Click `Load demo walkthrough`.
4. Open Trace tab and explain governance rail.
5. Open HITL tab and explain approval.
6. Run real API read-only smoke only if network/keyring is available.

- [ ] **Step 5: Verify and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\test_web_demo_data.py
.\.venv\Scripts\python.exe scripts\verify_delivery.py
git add src/agent_harness/web/demo_data.py src/agent_harness/web/theater.py tests/test_web_demo_data.py docs/demo_walkthrough.md
git commit -m "feat: add judge demo walkthrough"
```

---

### Task 5: Browser Screenshot QA Gate

**Files:**
- Create: `scripts/verify_web_ui.py`
- Modify: `scripts/verify_delivery.py`
- Test: `tests/test_delivery_verify.py`

**Interfaces:**
- Produces: `scripts/verify_web_ui.py --url http://127.0.0.1:8501`

- [ ] **Step 1: Write test for optional web command**

Update `tests/test_delivery_verify.py` so `build_checks()` still excludes web UI by default, and add a dry-run assertion for a new optional helper if implemented as separate script.

- [ ] **Step 2: Implement script**

The script should:

- request a URL argument
- fetch it with `urllib.request.urlopen`
- print status code
- fail if the body does not contain `Agent Harness Console`

Use only Python standard library.

- [ ] **Step 3: Verify**

With Streamlit running:

```powershell
.\.venv\Scripts\python.exe scripts\verify_web_ui.py --url http://127.0.0.1:8501
```

Expected output:

```text
web_ui ok status=200
```

- [ ] **Step 4: Commit**

```powershell
git add scripts/verify_web_ui.py tests/test_delivery_verify.py
git commit -m "test: add web ui smoke verifier"
```

---

### Task 6: Optional FastAPI + Static HTML Spike

**Files:**
- Create: `src/agent_harness/server/api.py`
- Create: `src/agent_harness/server/models.py`
- Create: `src/agent_harness/server/static/index.html`
- Create: `src/agent_harness/server/static/styles.css`
- Create: `src/agent_harness/server/static/app.js`
- Test: `tests/test_server_api.py`

**Interfaces:**
- Produces: `GET /api/trace?path=...`
- Produces: `GET /api/hitl?store=...`
- Produces: `POST /api/runs`

This task is optional. Start it only after Tasks 1-5 are complete and verified. If time is limited, skip it and polish Streamlit instead.

- [ ] **Step 1: Test API contract**

Use FastAPI `TestClient` only if FastAPI is added to dependencies. If avoiding new dependencies, skip this task.

- [ ] **Step 2: Build static visual prototype**

Implement `index.html` with no build step:

- left run controls
- center trace rail
- right HITL queue

Use static sample data first. Do not duplicate harness logic.

- [ ] **Step 3: Decision gate**

Only continue if:

- static HTML is visibly better than Streamlit
- API contract tests are stable
- full verification still passes

Otherwise, stop and keep Streamlit as the official demo UI.

---

## Final Verification Checklist

Run after every completed task:

```powershell
.\.venv\Scripts\python.exe scripts\verify_delivery.py
.\.venv\Scripts\python.exe -m pip wheel --no-deps --no-cache-dir . -w .harness\wheels
git status --short
```

For UI tasks:

```powershell
.\.venv\Scripts\python.exe -m streamlit run src\agent_harness\web\theater.py --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --global.developmentMode false
```

Then verify in a browser:

- page loads with HTTP 200
- title and tabs visible
- metric text readable
- no overlapping controls at 1280px width
- screenshot reviewed before commit

## Self-Review

- **Spec coverage:** The plan covers backup, skill research/installation, objective capability estimate, UI polish, HITL ergonomics, demo walkthrough, web verification, and a controlled optional HTML/FastAPI path.
- **Placeholder scan:** No task uses TBD/TODO/fill-in placeholders. Optional FastAPI spike has explicit skip criteria.
- **Type consistency:** Function names and signatures are defined before use: `trace_timeline`, `hitl_overview`, `request_detail`, `ensure_demo_trace`.
