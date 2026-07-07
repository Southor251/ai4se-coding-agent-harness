# Personal API Harness Master Implementation Plan

> **For agentic workers:** If task-execution workflow skills are available, you may use them to implement this plan task-by-task. Otherwise, execute the plan inline or manually. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local coding-agent harness application that can connect to the user's API, execute tasks under explicit safety controls, preserve trace/feedback evidence, and gradually become a personal project assistant.

**Architecture:** Keep the recovered deterministic kernel as the trusted core. Add application layers in this order: CLI runtime, provider abstraction, structured action protocol, safety/HITL execution, trace UI, then personal profile and memory. Each layer must be independently testable with MockLLM or fake clients before real API execution is enabled.

**Tech Stack:** Python 3.12, pytest, ruff, argparse, PyYAML, keyring, OpenAI-compatible chat API, Streamlit, JSONL, dataclasses.

## Global Constraints

- Work in the sandbox copy unless explicitly syncing to the desktop original.
- Use TDD for behavior changes: failing test first, implementation second.
- Never store or print real API keys.
- Shell execution defaults to deny or ask unless an explicit policy permits it.
- All path-like tool arguments must pass scope checks.
- Real API execution must have a dry-run or mock path for tests.
- Run `python -m pytest -q` and `python -m ruff check src/ tests/ demo/` after each task group.

---

## Target Milestones

### Milestone A: Local Application Entry

Make the package usable as a local application without relying on real API calls.

- `agent-harness run "goal"` returns a structured result.
- `agent-harness demo` runs deterministic demos.
- `agent-harness web` exposes a safe trace-theater entrypoint.
- Runtime factory creates a governed harness from config.

### Milestone B: Real API Provider

Make API connection explicit, configurable, and testable.

- Support provider config: `provider`, `model`, `base_url`, `temperature`.
- Load credentials from keyring, `.env`, or environment without printing secrets.
- Use fake clients in tests.
- Parse model responses through a structured action protocol.

### Milestone C: Robust Task Execution

Make tool execution useful while still governed.

- Add structured action validation errors.
- Feed invalid action errors back into context for retry.
- Add policy for `path`, `pattern`, and `cwd`.
- Add HITL approve/deny path for ask decisions.

### Milestone D: Personal UX

Make the harness practical for daily use.

- Streamlit task input.
- Trace replay with summary counts.
- Project memory and personal profile.
- Clear run records under `.harness/runs/`.

### Milestone E: Personalization

Make it adapt to the user's projects.

- Per-project profile.
- Preferred tools and command templates.
- Coding/review preferences.
- Exportable run reports.

## Immediate Execution Slice

The first execution slice is Milestone A. It is the right next step because the current repo already has a tested kernel but lacks a real application entry. This slice gives every later API/provider feature a stable place to plug in.

## File Structure for Milestone A

- `src/agent_harness/runtime/__init__.py`: runtime package export.
- `src/agent_harness/runtime/result.py`: `RunResult` dataclass.
- `src/agent_harness/runtime/factory.py`: config-to-harness builder.
- `src/agent_harness/cli/run.py`: run command implementation.
- `src/agent_harness/cli/demo.py`: deterministic demo command implementation.
- `src/agent_harness/cli/web.py`: safe web/theater command implementation.
- `src/agent_harness/cli/main.py`: argparse wiring.
- `tests/test_runtime_factory.py`: factory behavior.
- `tests/test_cli_run.py`: run command behavior.
- `tests/test_cli_demo.py`: demo command behavior.
- `tests/test_cli_web.py`: web command behavior.
- `README.md`, `AGENT_LOG.md`, `PLAN.md`: status updates.

## Task A1: Runtime Factory and Run Result

**Files:**
- Create: `src/agent_harness/runtime/__init__.py`
- Create: `src/agent_harness/runtime/result.py`
- Create: `src/agent_harness/runtime/factory.py`
- Create: `tests/test_runtime_factory.py`

**Interfaces:**
- Consumes: `HarnessConfig`, `Harness`, `MockLLM`, `LLMResponse`, `AgentAction`
- Produces: `RunResult(answer: str, halt_reason: str | None, steps: int, trace_path: str | None = None)`, `build_harness(config: HarnessConfig) -> Harness`

- [ ] Write failing tests for result and factory.
- [ ] Run targeted tests and confirm failure.
- [ ] Implement result and factory using MockLLM as safe default.
- [ ] Run targeted tests and confirm pass.
- [ ] Commit: `feat: add runtime factory`

## Task A2: Real CLI Run Command

**Files:**
- Modify: `src/agent_harness/cli/run.py`
- Modify: `src/agent_harness/cli/main.py`
- Create: `tests/test_cli_run.py`

**Interfaces:**
- Consumes: `build_harness(config)`, `agent_loop(goal, harness)`, `load_config(path)`
- Produces: `run_goal(goal: str, config_path: str | None = None) -> RunResult`, `add_run_parser(subparsers) -> None`

- [ ] Write failing tests for `run_goal` and parser execution.
- [ ] Run targeted tests and confirm failure.
- [ ] Implement `run_goal` and parser handler.
- [ ] Wire `agent-harness run "goal" --config config/agent-harness.yaml`.
- [ ] Run targeted tests and CLI smoke test.
- [ ] Commit: `feat: implement cli run command`

## Task A3: Demo and Web Commands

**Files:**
- Create: `src/agent_harness/cli/demo.py`
- Create: `src/agent_harness/cli/web.py`
- Modify: `src/agent_harness/cli/main.py`
- Create: `tests/test_cli_demo.py`
- Create: `tests/test_cli_web.py`

**Interfaces:**
- Produces: `run_all_demos() -> dict[str, dict]`, `theater_command(trace_path: str | None = None) -> str`

- [ ] Write failing tests for demo and web helpers.
- [ ] Implement helpers using existing demo modules and a safe theater message.
- [ ] Wire `agent-harness demo` and `agent-harness web`.
- [ ] Run targeted tests and CLI smoke tests.
- [ ] Commit: `feat: implement cli demo and web commands`

## Task A4: Documentation and Review Gate

**Files:**
- Modify: `README.md`
- Modify: `AGENT_LOG.md`
- Modify: `PLAN.md`

**Interfaces:**
- Produces: accurate application-entry documentation.

- [ ] Update docs with real CLI commands and current test count.
- [ ] Run full tests.
- [ ] Run ruff.
- [ ] Run CLI smoke tests.
- [ ] Run secret/TODO scan.
- [ ] Request code review.
- [ ] Fix Critical and Important findings.
- [ ] Commit: `docs: update application entry status`

## Self-Review

1. **Clarity:** The final target is now explicit: a local API-backed coding-agent application, not only a course harness.
2. **Feasibility:** The immediate slice avoids real API complexity and first creates stable application entrypoints. This matches the current codebase and my ability to deliver with low rework.
3. **Low rework:** Provider/API work is intentionally delayed until CLI runtime and result surfaces exist. This prevents redesigning provider code around an unstable app interface.
4. **Safety:** Real API and shell execution remain gated by credentials, config, scope, permission, and later HITL improvements.
5. **Quality:** Every task has a testable deliverable and commit boundary. The plan does not require speculative large refactors.
