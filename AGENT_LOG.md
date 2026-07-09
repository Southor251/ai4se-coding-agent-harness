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

- current permission-profile slice
  - Runtime factory now loads permission rules from config.
  - Runtime factory now creates a `HITLManager`.
  - Ask-mode write actions create pending HITL requests and do not execute by default.

- current run-record slice
  - `agent-harness run` now writes trace JSONL through `TraceStore`.
  - `RunResult.trace_path` is populated.
  - CLI accepts `--trace <path>` and defaults to `.harness/runs/latest.jsonl`.

- current theater-summary slice
  - Added `summarize_trace(records)`.
  - Theater now reports step, tool-call, denial, and feedback-event counts.

- current project-memory slice
  - Added `ProjectMemory` append-only markdown store.
  - Runtime config can enable project memory with `memory.enabled`.

- current personal-profile slice
  - Added config/profile deep merge.
  - Added `agent-harness run --profile <path>`.
  - Added `config/personal-harness.yaml` as a safe starter profile.

- current HITL-resume slice
  - Added `approve_and_execute(harness, request_id)`.
  - Added public `HITLManager.find`.
  - Approved pending requests can execute their stored tool action.

- current HITL CLI slice
  - Added persistent `HITLStore`.
  - `HITLManager` now loads and saves requests when a store is configured.
  - Added `agent-harness hitl list|approve|deny`.
  - `approve_and_execute` now checks scope before executing approved actions.

- current Web task/HITL slice
  - Added `agent_harness.web.services` as a testable service layer for task runs, trace summary, and HITL list/approve/deny.
  - Extended the Streamlit theater with goal/config/profile/trace inputs, run result display, trace summary, step inspection, and HITL approval controls.
  - Kept Web logic on the same governed runtime and shared HITL store used by the CLI.

- current tool-schema slice
  - Added argument schemas to the tool base and built-in tools.
  - Agent loop menus now pass tool argument schemas to the LLM layer.
  - OpenAI-compatible prompts now include argument names and descriptions for structured JSON actions.

- current done-answer slice
  - Structured `done` actions now support an optional `answer` field.
  - The agent loop returns the `answer` field as user-facing output when present, while preserving old raw-text behavior for legacy mock responses.

- current API e2e slice
  - Added a fake OpenAI client end-to-end runtime test for read, write, run_test, trace, feedback, and structured final answer.
  - Added strict fenced JSON action compatibility for complete JSON code-fence responses.

- current HITL-continue slice
  - HITL requests now persist resume context and step.
  - Added `approve_execute_and_continue` to execute an approved action, inject the tool result into context, and continue the agent loop.
  - Added `agent-harness hitl approve --continue`.

- current read-only-tools slice
  - Added `list_files` and `search_text` as safe default runtime tools.
  - Both tools expose argument schemas for API-backed action generation.
  - `run_shell` remains excluded from the default governed runtime.

- current multi-read/diff tools slice
  - Added `read_many` for bounded batch file reads.
  - Added `git_diff` as a non-shell subprocess wrapper for read-only diff inspection.
  - Registered both tools in the default governed runtime.

- current precise-edit slice
  - Added `replace_once` for safer exact single-match edits.
  - Registered `replace_once` in the default governed runtime.

- current Web HITL-continue slice
  - Added `approve_and_continue_hitl_request` to the Web service layer.
  - Streamlit theater now exposes an `Approve + Continue` HITL action.

- current Web trace-history slice
  - Added `list_trace_runs` to the Web service layer.
  - Streamlit theater can select existing JSONL traces from `.harness/runs`.

- current delivery-setup slice
  - Added `scripts/verify_delivery.py` for repeatable local verification.
  - Added `docs/personal_setup.md` for personal API profile setup, HITL, Web, and safety defaults.

- current high-confidence-scan slice
  - Added `scripts.secret_scan` for automated high-confidence private-key, secret-token, and marker checks.
  - `scripts/verify_delivery.py` now uses `sys.executable` and the Python scanner for reproducible local validation.

- current final-status slice
  - Added `docs/final_status.md` summarizing implemented capabilities, latest verification, remaining user-specific setup, and safety boundaries.

## Verification

Latest verification in the sandbox:

```bash
python -m pytest -q
python -m ruff check src/ tests/ demo/
```

Observed result:

- `161 passed`
- `All checks passed!`
- CLI smoke: `agent-harness run "say done" --profile config/personal-harness.yaml --trace .harness/runs/latest.jsonl`
- CLI smoke: `agent-harness hitl list --store .harness/hitl/requests.json`
- Secret and marker scan found only documentation/test mentions of API key handling and fake test credentials; no real secret was identified.

## Remaining Product Work

- Implement real API-backed provider execution behind the working CLI runtime.
- Improve the Streamlit theater styling and replay ergonomics.
- Add real provider configuration and model selection once target provider/version requirements are fixed.
- Expand personal-harness features such as persistent project memory, patch planning, and richer tool permissions.

## 2026-07-08 Completion Gap Closure

- Added `agent_harness.cli.doctor` and registered `agent-harness doctor`.
  - Reports config/profile, workspace, provider, model, base URL, credential status, tool count, `run_shell` status, permission rule count, memory, and max steps.
  - Does not print credential values.
- Added `agent_harness.cli.smoke` and registered `agent-harness smoke hitl-write`.
  - Creates a deterministic pending `write_file` request under a controlled smoke workspace.
  - Confirms the target file is not written before approval.
  - Prints a copy-paste `agent-harness hitl approve <id> --continue --store <path>` command.
- Updated `README.md`, `docs/personal_setup.md`, and `docs/final_status.md`.
  - Added `doctor`, HITL smoke, real API read-only smoke, and reliable Windows Streamlit startup commands.
- Added implementation plan `docs/superpowers/plans/2026-07-08-completion-gap-closure.md`.
- Verification:
  - `python -m pytest -q tests/test_cli_doctor.py tests/test_cli_smoke.py` -> `4 passed`
  - `agent-harness doctor --profile config/personal-harness.yaml` -> reports `run_shell: disabled`
  - `agent-harness smoke hitl-write ...` -> creates pending request and does not write the target file
  - `python -m ruff check src/ tests/ demo/` -> `All checks passed!`
  - `python scripts/verify_delivery.py` -> `165 passed`, ruff passed, CLI run/list smoke passed, high-confidence secret scan passed
- Remaining boundary:
  - User still needs to configure their real provider/key locally and run the read-only smoke plus HITL write smoke against that provider.
  - Streamlit remains the current usable theater; full React/FastAPI GUI is deferred until the core workflow has real-provider validation.

## 2026-07-08 Real API Read-Only Smoke

- Configured `config/personal-harness.yaml` for the user's OpenAI-compatible endpoint:
  - provider: `openai`
  - model: `DeepSeek-R1`
  - base_url: `https://njusehub.info/v1`
- User stored the API key through `agent-harness credentials update --prompt`; the key was not printed or committed.
- Initial `doctor` in normal sandbox could not read keyring, but escalated `doctor` reported `credential: configured`.
- First real API run timed out because DeepSeek-R1 returned `<think>...</think>` reasoning before the JSON action, and the strict parser rejected the response as invalid.
- Added action protocol support for extracting the first valid JSON object from reasoning-wrapped responses while preserving invalid-action handling when no JSON exists.
- The first real run also showed that the old `ask before writes` path rule matched read tools. Added optional `PermissionRule.tools` filtering and updated the personal profile so only `write_file`, `replace_once`, and `edit_file` require approval.
- Updated `scripts/verify_delivery.py` so delivery verification uses the default mock config and does not accidentally call the user's real API profile.
- Real read-only smoke succeeded:
  - command: `agent-harness run "Read README.md and summarize it in one sentence." --profile config/personal-harness.yaml --trace .harness/runs/real-readonly-smoke.jsonl`
  - result: `halt_reason=done steps=2`
  - step 1: `read_file` on `README.md`
  - step 2: one-sentence `done.answer`
- Verification after fixes:
  - targeted tests: `23 passed`
  - full delivery: `168 passed`, ruff passed, CLI run/list smoke passed, high-confidence secret scan passed.

## 2026-07-09 Streamlit Console UI Pass

- Reworked `agent_harness.web.theater` from a linear debug page into a clearer console layout:
  - dark left sidebar for run configuration
  - top metric strip for steps, tool calls, denials, feedback, and pending HITL
  - tabs for Run, Trace, and HITL
  - trace inspector with LLM output, action JSON, tool result, and final answer sections
- Expanded `load_trace_for_display` to expose tool name, HITL status, tool success/output/error, and final answer fields for UI rendering.
- Added regression coverage in `tests/test_theater.py` for tool detail rows.
- Browser verification:
  - opened `http://127.0.0.1:8501`
  - confirmed title `Agent Harness Console`
  - confirmed Run Control, metrics, Trace, and HITL sections render
  - captured screenshots before and after contrast adjustment
- Visual fix:
  - first screenshot showed metric cards with low-contrast text
  - updated CSS so metric labels and values render dark and readable
- Verification:
  - `python -m pytest -q tests/test_theater.py tests/test_web_services.py` -> `10 passed`
  - `python -m ruff check src/agent_harness/web/theater.py tests/test_theater.py` -> `All checks passed!`
  - `python scripts/verify_delivery.py` -> `169 passed`, ruff passed, CLI run/list smoke passed, high-confidence secret scan passed.

## 2026-07-09 Award UI Iteration Tasks 1-2

- Task 1 added testable UI view models in `agent_harness.web.services`:
  - `trace_timeline(path)` converts JSONL trace records into compact step/state/tool/permission/HITL rows.
  - `hitl_overview(store_path)` summarizes pending, approved, denied, and timed-out approval requests.
- Task 1 commit: `3b827ea feat: add ui trace view models`.
- Task 2 added a governance rail to the Streamlit Trace tab and a small `status_tone()` mapping for stable visual states.
- Browser verification at `http://127.0.0.1:8501` confirmed `Agent Harness Console`, `Trace inspector`, `Governance rail`, and 28 rendered rail rows.
- Task 2 verification:
  - `.venv\Scripts\python.exe -m pytest -q tests/test_theater.py tests/test_web_services.py` -> `13 passed`
  - `.venv\Scripts\python.exe -m ruff check src\agent_harness\web tests\test_web_services.py tests\test_theater.py` -> `All checks passed!`
  - `.venv\Scripts\python.exe scripts\verify_delivery.py` -> `172 passed`, ruff passed, CLI run/list smoke passed, high-confidence secret scan passed.

## 2026-07-09 Award UI Iteration Task 3

- Added `request_detail(store_path, request_id)` to expose a single HITL request with action args, resume step, context item count, timestamps, and decision fields.
- Streamlit HITL tab now sorts pending requests first, offers a request selector, keeps an advanced request-id input for copied ids, and renders the selected request JSON before approval.
- Browser verification at `http://127.0.0.1:8501` confirmed `Pending request`, `Request id (advanced)`, request detail JSON, and `Approve + Continue` are visible after Streamlit rerun.
- Task 3 verification:
  - `.venv\Scripts\python.exe -m pytest -q tests/test_web_services.py tests/test_theater.py` -> `15 passed`
  - `.venv\Scripts\python.exe -m ruff check src\agent_harness\web tests\test_web_services.py tests\test_theater.py` -> `All checks passed!`
  - `.venv\Scripts\python.exe scripts\verify_delivery.py` -> `174 passed`, ruff passed, CLI run/list smoke passed, high-confidence secret scan passed.

## 2026-07-09 Award UI Iteration Task 4

- Added deterministic demo data generation in `agent_harness.web.demo_data.ensure_demo_trace`.
- The demo writes `.harness/runs/demo-walkthrough.jsonl` and `.harness/hitl/demo-requests.json`, with a successful read step, a pending write approval step, and a final done step.
- Streamlit sidebar now includes `Load demo walkthrough`, which creates the demo artifacts, stores the active trace/HITL paths in session state, and reruns the app.
- Added `docs/demo_walkthrough.md` and linked it from `README.md`.
- Browser verification confirmed the demo trace path, demo HITL store value, governance rail, pending state, and demo answer are visible after clicking the button.
- Task 4 verification:
  - `.venv\Scripts\python.exe -m pytest -q tests/test_web_demo_data.py tests/test_web_services.py tests/test_theater.py` -> `16 passed`
  - `.venv\Scripts\python.exe -m ruff check src\agent_harness\web tests\test_web_demo_data.py tests\test_web_services.py tests\test_theater.py` -> `All checks passed!`
  - `.venv\Scripts\python.exe scripts\verify_delivery.py` -> `175 passed`, ruff passed, CLI run/list smoke passed, high-confidence secret scan passed.
