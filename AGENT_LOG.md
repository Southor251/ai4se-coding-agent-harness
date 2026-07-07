# Agent Log

This log records the recovery work performed in the sandbox copy of the project.

## Context

- Original project source: `C:\Users\hp\Desktop\opencodem\ai4se-coding-agent-harness`
- Sandbox working copy: `C:\Users\hp\Documents\Codex\2026-07-07\https-opncd-ai-share-1wbl482n\work\ai4se-coding-agent-harness`
- Recovery objective: turn the partial harness into a stable, deterministic kernel suitable for course delivery and later personal customization.

## Commit History

- `424e71f chore: recover sandbox baseline`
  - Added dev dependencies and CI install path.
  - Made tests run through `sys.executable -m pytest`.
  - Replaced high-risk security literals with neutral fixtures.
  - Verified tests and ruff after baseline recovery.

- `543992c feat: add kernel observability contract`
  - Added `scope`, `hitl`, `context`, `feedback_events`, and `halt_reason` to the harness container.
  - Fixed path prefix scope handling.

- `1d41305 feat: enforce governance in agent loop`
  - Integrated scope, permission, and HITL checks before tool execution.
  - Added tests proving denied and ask actions do not execute tools by default.

- `147dff8 feat: add deterministic feedback loop`
  - Added feedback classifier, sensor, and healing state.
  - Fed structured feedback back into the agent context.

- `f9a4cf9 feat: add trace store and deterministic demos`
  - Added JSONL trace recording and deterministic mechanism demos.

- `8adb5e2 feat: add config credentials and cli skeleton`
  - Added YAML config loading, credential manager, and CLI command skeleton.

- `4cfae7f feat: add plugins and trace theater`
  - Added minimal plugin interfaces and trace theater loader.

- `9ad6bda fix: harden governance and feedback loop`
  - Addressed code-review findings around sensitive path detection, missing workspace roots, loop step reuse, unknown tools, shell default policy, pytest return code handling, trace timestamps, and feedback demo truthfulness.

- `70da24e docs: add delivery artifacts`
  - Added README, AGENT_LOG, SPEC_PROCESS, Dockerfile, REFLECTION, and delivery Makefile/PLAN updates.

- final review fix
  - Restored the credential manager package to tracked source by narrowing the credential ignore rule.
  - Added scope enforcement for `run_test(pattern=...)`.
  - Added parsing for simple OpenAI text tool actions with `tool:` and JSON `args:`.

- current application-entry slice
  - Added a master plan for the final API-backed personal harness target.
  - Added runtime factory and `RunResult`.
  - Implemented minimal working `agent-harness run`, `agent-harness demo`, and `agent-harness web` commands.
  - Moved reusable demo logic into the installable `agent_harness.demos` package.

- current provider slice
  - Added OpenAI-compatible provider construction through config and credential manager.
  - Added support for `model`, `base_url`, and `temperature`.
  - Verified no-key execution exits safely without network calls.

- current action-protocol slice
  - Added strict JSON action parsing in `agent_harness.llm.action_protocol`.
  - OpenAI-compatible provider now instructs the model to emit one JSON action object.
  - Invalid action output becomes an observable `invalid` action and is fed back into the loop for retry.

- current runtime-tooling slice
  - Runtime factory now registers safe default tools: `read_file`, `write_file`, `edit_file`, and `run_test`.
  - Runtime factory now adds `ScopeGuard` and `FeedbackSensor`.
  - `run_shell` remains excluded from default runtime registration.

## Verification

Latest verification in the sandbox:

```bash
python -m pytest -q
python -m ruff check src/ tests/ demo/
```

Observed result:

- `111 passed`
- `All checks passed!`

## Remaining Product Work

- Implement real API-backed provider execution behind the working CLI runtime.
- Replace the minimal Streamlit theater with a richer replay UI.
- Add real provider configuration and model selection once target provider/version requirements are fixed.
- Expand personal-harness features such as persistent project memory, patch planning, and richer tool permissions.
