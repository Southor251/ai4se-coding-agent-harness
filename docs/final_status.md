# Final Project Status

## Status

The sandbox project is a usable local coding-agent harness foundation. It can run with a safe mock provider by default and can be configured for an OpenAI-compatible API through profile YAML plus the credential manager.

Latest verified command:

```bash
python scripts/verify_delivery.py
```

Latest observed result:

- `161 passed`
- ruff passed
- CLI run smoke passed
- HITL list smoke passed
- high-confidence secret scan passed

## Implemented Capabilities

- Strict JSON action protocol with `call_tool`, `take_note`, and `done.answer`.
- OpenAI-compatible provider configuration for `model`, `base_url`, and `temperature`.
- Credential manager with keyring first and ignored `.env` fallback.
- Governed runtime with `ScopeGuard`, permission policy, HITL, feedback, trace, and project memory.
- Default tools:
  - `read_file`
  - `read_many`
  - `list_files`
  - `search_text`
  - `git_diff`
  - `write_file`
  - `replace_once`
  - `edit_file`
  - `run_test`
- `run_shell` is not registered in the default governed runtime.
- Persistent HITL store at `.harness/hitl/requests.json`.
- CLI HITL list, approve, deny, and approve-and-continue.
- Streamlit theater with task input, trace selection, trace summary, step inspection, HITL approve, deny, and approve-and-continue.
- Delivery verification script and high-confidence secret/marker scan.

## User-Specific Setup Still Required

- Configure the real API endpoint and model in a personal profile.
- Store the real API key through `agent-harness credentials update <secret>` or an environment variable.
- Choose the actual workspace root for personal projects.
- Review and adjust permission rules before allowing write-heavy tasks.

## Safety Boundary

This project provides harness-level governance, not an operating-system sandbox. It should be run against a chosen workspace directory with conservative permission rules. The default runtime intentionally omits shell execution.
