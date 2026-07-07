# Harness Recovery and Kernel Redesign

## Goal

Recover the AI4SE Coding Agent Harness project from its current partial implementation into a stable, testable, course-deliverable harness that can later evolve into a personal coding harness.

## Context

The copied project already contains a useful core: data models, LLM abstraction, MockLLM, OpenAILLM, a basic loop, five tools, PermissionPolicy, ScopeGuard, HITL, and 47 passing tests in the original environment. It is not ready for final delivery because the loop does not yet integrate governance, feedback, trace, CLI, credentials, WebUI, demo scripts, or required documentation.

The previous development flow stalled with a service-side `sensitive_words_detected` error. The repository does not contain the request id, but the tests and task material contain full high-risk command and sensitive path examples. The recovery design keeps the security-governance behavior but replaces high-risk literals in prompts/tests/demos with neutral fixtures.

## Design Principles

- Keep the existing repository and commits; do not rebuild from scratch.
- Work in the sandbox copy only unless the user asks to sync changes back.
- Treat the LLM as a replaceable decision source, not the harness core.
- Make the kernel deterministic under MockLLM.
- Use neutral fixtures for policy tests to avoid model-side filtering while preserving behavior.
- Prefer small, typed data objects over ad hoc strings in the loop.
- Keep the first working version synchronous and simple.

## Target Kernel Shape

The agent loop should follow this pipeline:

1. Build context from system prompt, goal, memory, and prior observations.
2. Call an injected LLM implementation.
3. Validate the returned action shape.
4. Run scope and permission checks before tool execution.
5. Execute or block the action.
6. Convert tool output into structured feedback.
7. Record a trace entry.
8. Decide whether to halt.

Each stage should be independently testable. The loop should return a structured run result or, at minimum, leave structured evidence in trace/context fields.

## Recovery Scope

### Phase 1: Development Baseline

- Fix lint errors.
- Add dev dependencies for `pytest` and `ruff`.
- Make CI install dev dependencies.
- Make `RunTestTool` use `sys.executable -m pytest`.
- Replace high-risk security test literals with neutral fixtures.

### Phase 2: Governance Integration

- Integrate PermissionPolicy, ScopeGuard, and HITL into `agent_loop`.
- Ensure blocked actions do not execute tools.
- Ensure blocked/asked actions are fed back into context.
- Preserve deterministic tests.

### Phase 3: Feedback Loop

- Add FeedbackClassifier, FeedbackSensor, and HealingState.
- Convert ToolResult into structured Feedback.
- Feed feedback into the next LLM context.
- Use MockLLM response queues to prove behavior changes after feedback.

### Phase 4: Trace and Demo

- Add TraceStore using JSONL.
- Record per-step LLM decisions, policy decisions, tool results, feedback, and halt reason.
- Add deterministic demos for policy blocking, feedback recovery, and scope-policy cooperation using neutral fixtures.

### Phase 5: CLI, Config, Credentials

- Add YAML profile loading.
- Add CLI commands for run, demo, web, and credentials.
- Implement credentials with keyring first and `.env` fallback.
- Never print secret values.

### Phase 6: Theater and Plugin Surface

- Add a Streamlit Agent Loop Theater that reads trace JSONL only.
- Add minimal plugin interfaces for tools, policy, and feedback.

### Phase 7: Course Delivery

- Add README, AGENT_LOG, SPEC_PROCESS, Dockerfile, and final delivery checks.
- Provide a reflection scaffold only; the student must write the final reflection.

## Explicit Non-Goals

- No real dangerous command examples in prompts, demos, or reports.
- No async orchestration.
- No real shell sandbox beyond policy and scope checks in v1.
- No automatic remote push or public deployment without user confirmation.
- No use of real API keys during automated tests.

## Acceptance Criteria

- `pytest -q` passes in the sandbox copy after editable install.
- `python -m ruff check src/ tests/` passes.
- The full mechanism demo runs under MockLLM without network access.
- Governance, feedback, trace, and CLI have deterministic tests.
- README documents install, run, Docker, key setup, safety boundaries, and known limits.
- Required course artifacts exist or are explicitly scaffolded with user-owned sections marked clearly.
