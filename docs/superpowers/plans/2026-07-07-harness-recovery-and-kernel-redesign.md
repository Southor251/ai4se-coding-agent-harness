# Harness Recovery and Kernel Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover the partial AI4SE Coding Agent Harness into a stable, deterministic, course-deliverable kernel that can later become a personal harness.

**Architecture:** Keep the existing Python package and evolve it in place. The core loop becomes a deterministic pipeline around injected LLM, policy, tools, feedback, and trace components. Security tests use neutral blocked-action fixtures instead of high-risk command literals.

**Tech Stack:** Python 3.12, pytest, ruff, dataclasses, argparse, keyring, PyYAML, Pydantic, Streamlit, JSONL traces.

## Global Constraints

- Work only in the sandbox copy unless the user explicitly asks to sync changes back.
- Use TDD for behavior changes: failing test first, then minimal implementation.
- Do not use real API keys in tests.
- Do not execute or document real destructive commands as examples; use neutral blocked-action fixtures.
- Keep the v1 implementation synchronous.
- Required course CI includes `.gitlab-ci.yml` with a `unit-test` job.
- README must explain project intro, install, run, distribution command, directory structure, and safety boundaries.

---

## File Structure

- `pyproject.toml`: package metadata, runtime dependencies, dev dependencies.
- `.gitlab-ci.yml`, `.github/workflows/test.yml`: CI setup.
- `src/agent_harness/models.py`: shared dataclasses.
- `src/agent_harness/agent/loop.py`: orchestration pipeline.
- `src/agent_harness/agent/harness.py`: dependency container.
- `src/agent_harness/governance/*`: policy, scope, HITL.
- `src/agent_harness/feedback/*`: classifier, sensor, healing state.
- `src/agent_harness/trace/store.py`: JSONL trace store.
- `src/agent_harness/config/loader.py`: YAML profile config.
- `src/agent_harness/credentials/manager.py`: keyring and `.env` credentials.
- `src/agent_harness/cli/*`: CLI entrypoints.
- `src/agent_harness/web/theater.py`: trace replay WebUI.
- `src/agent_harness/plugins/*`: minimal extension interfaces.
- `demo/*`: deterministic MockLLM demos.
- `tests/*`: module and integration tests.
- `README.md`, `AGENT_LOG.md`, `SPEC_PROCESS.md`, `Dockerfile`: delivery artifacts.

## Task 1: Baseline Recovery

**Files:**
- Modify: `pyproject.toml`
- Modify: `.gitlab-ci.yml`
- Modify: `.github/workflows/test.yml`
- Modify: `src/agent_harness/tools/builtin/run_test.py`
- Modify: `src/agent_harness/agent/loop.py`
- Modify: `tests/test_import.py`
- Modify: `tests/test_loop.py`
- Modify: `tests/test_permission.py`
- Modify: `tests/test_scope.py`
- Modify: `tests/test_models.py`
- Modify: `tests/test_hitl.py`

**Interfaces:**
- Produces: reliable `python -m pytest`, reliable `python -m ruff`, neutral policy fixtures.

- [ ] Add dev dependencies for `pytest` and `ruff`.
- [ ] Update CI to install `.[dev]`.
- [ ] Change RunTestTool to call `sys.executable -m pytest`.
- [ ] Fix current ruff errors.
- [ ] Replace high-risk command/path literals with neutral fixtures.
- [ ] Verify `python -m pip install -e ".[dev]"`.
- [ ] Verify `python -m pytest -q`.
- [ ] Verify `python -m ruff check src/ tests/`.

## Task 2: Governance Integrated Loop

**Files:**
- Modify: `src/agent_harness/agent/harness.py`
- Modify: `src/agent_harness/agent/loop.py`
- Modify: `tests/test_loop_extended.py`
- Create or modify: `tests/test_governance_loop.py`

**Interfaces:**
- Consumes: `PermissionPolicy.check(action) -> str`, `ScopeGuard.check(path) -> ScopeVerdict`, `HITLManager.create_request(action, reason)`.
- Produces: loop behavior where denied actions do not execute tools and ask actions create HITL requests.

- [ ] Write failing test: denied tool action is not executed.
- [ ] Write failing test: out-of-scope path is blocked before tool execution.
- [ ] Write failing test: ask verdict creates HITL request and does not execute by default.
- [ ] Implement minimal governance pipeline in `agent_loop`.
- [ ] Verify targeted governance-loop tests pass.
- [ ] Verify full tests and lint.

## Task 3: Feedback Loop

**Files:**
- Create: `src/agent_harness/feedback/__init__.py`
- Create: `src/agent_harness/feedback/classifier.py`
- Create: `src/agent_harness/feedback/sensor.py`
- Create: `src/agent_harness/feedback/heal.py`
- Modify: `src/agent_harness/agent/loop.py`
- Create: `tests/test_feedback.py`
- Create or modify: `tests/test_feedback_loop.py`

**Interfaces:**
- Produces: `classify_feedback(output: str, success: bool, error: str | None) -> str`, `FeedbackSensor.from_tool_result(result) -> Feedback`, `HealingState`.

- [ ] Write failing classifier tests for success, syntax, assertion, timeout, and tool error.
- [ ] Implement classifier.
- [ ] Write failing sensor tests.
- [ ] Implement sensor.
- [ ] Write failing healing-state tests.
- [ ] Implement healing state.
- [ ] Write failing loop test proving feedback enters next context.
- [ ] Integrate feedback into `agent_loop`.
- [ ] Verify full tests and lint.

## Task 4: Trace Store and Mechanism Demos

**Files:**
- Create: `src/agent_harness/trace/__init__.py`
- Create: `src/agent_harness/trace/store.py`
- Modify: `src/agent_harness/agent/loop.py`
- Create: `demo/__init__.py`
- Create: `demo/demo_guardrail.py`
- Create: `demo/demo_feedback.py`
- Create: `demo/demo_scope.py`
- Create: `tests/test_trace.py`
- Create: `tests/test_demo.py`

**Interfaces:**
- Produces: `TraceStore.record(record)`, `TraceStore.load(path)`, three deterministic demo `run_demo()` functions.

- [ ] Write failing TraceStore write/load tests.
- [ ] Implement TraceStore.
- [ ] Write failing loop trace integration test.
- [ ] Integrate trace recording into loop.
- [ ] Write failing demo tests.
- [ ] Implement demos with neutral fixtures.
- [ ] Verify `python -m pytest -q`, `python -m ruff check src/ tests/`.

## Task 5: Config, CLI, Credentials

**Files:**
- Create: `src/agent_harness/config/__init__.py`
- Create: `src/agent_harness/config/loader.py`
- Create: `src/agent_harness/credentials/__init__.py`
- Create: `src/agent_harness/credentials/manager.py`
- Create: `src/agent_harness/cli/main.py`
- Create: `src/agent_harness/cli/run.py`
- Create: `src/agent_harness/cli/credentials.py`
- Create: `config/agent-harness.yaml`
- Create: `tests/test_config.py`
- Create: `tests/test_credentials.py`
- Create: `tests/test_cli.py`

**Interfaces:**
- Produces: `load_config(path)`, `CredentialManager`, `agent-harness` CLI.

- [ ] Write failing config load tests.
- [ ] Implement config loader with defaults.
- [ ] Write failing credentials tests using a fake backend.
- [ ] Implement credentials manager without printing secrets.
- [ ] Write failing CLI help tests.
- [ ] Implement CLI commands.
- [ ] Verify full tests and lint.

## Task 6: Theater and Plugins

**Files:**
- Create: `src/agent_harness/web/__init__.py`
- Create: `src/agent_harness/web/theater.py`
- Create: `src/agent_harness/plugins/__init__.py`
- Create: `src/agent_harness/plugins/base.py`
- Create: `src/agent_harness/plugins/registry.py`
- Create: `tests/test_plugins.py`

**Interfaces:**
- Produces: trace-readable Streamlit app, `ToolPlugin`, `PolicyPlugin`, `FeedbackPlugin`, `PluginRegistry`.

- [ ] Write failing plugin interface tests.
- [ ] Implement minimal plugin base classes and registry.
- [ ] Implement Theater as a read-only trace display module.
- [ ] Verify import tests, full tests, and lint.

## Task 7: Delivery Artifacts

**Files:**
- Create: `README.md`
- Create: `AGENT_LOG.md`
- Create: `SPEC_PROCESS.md`
- Create: `Dockerfile`
- Create: `REFLECTION.md`
- Modify: `Makefile`
- Modify: `PLAN.md`

**Interfaces:**
- Produces: complete course-facing artifact set.

- [ ] Add README with required sections.
- [ ] Add AGENT_LOG with recovered task history and new task entries.
- [ ] Add SPEC_PROCESS summarizing process, cold-start requirement status, and revision rationale.
- [ ] Add Dockerfile.
- [ ] Add REFLECTION scaffold clearly marked for student completion.
- [ ] Update Makefile targets.
- [ ] Update PLAN status summary.
- [ ] Run final tests, lint, secret scan, and import checks.

## Self-Review

- Spec coverage: Baseline, governance, feedback, trace, CLI/config/credentials, theater/plugins, and course artifacts are covered.
- Placeholder scan: No task contains TBD/TODO placeholders.
- Type consistency: Task interfaces match existing names or introduce explicit names.
- Scope check: This is one cohesive recovery plan for the harness; later personal-harness customization remains future work.
