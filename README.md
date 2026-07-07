# AI4SE Coding Agent Harness

This repository contains a small, testable coding-agent harness kernel. It is designed as a course-facing project first and as a foundation for a later personal harness second.

The current implementation focuses on deterministic orchestration around an injected LLM, tool registry, scope guard, permission policy, human-in-the-loop request manager, feedback sensor, and JSONL trace store. Tests use `MockLLM` and neutral policy fixtures so the core behavior is reproducible without network access or real credentials.

## What Works

- Package import and editable install through `pyproject.toml`.
- Deterministic agent loop with `done`, `call_tool`, and `take_note` actions.
- Built-in tools for reading, writing, editing files, running shell commands, and running tests.
- Runtime factory registers safe default tools: `read_file`, `write_file`, `edit_file`, and `run_test`. `run_shell` is not registered by default.
- Governance checks for workspace scope, sensitive paths, permission deny, and permission ask.
- Human-in-the-loop request objects for ask-mode decisions.
- Runtime config can load permission rules and create HITL requests for ask-mode tool actions.
- Feedback classification from tool results and feedback injection into the next loop context.
- JSONL trace recording and loading.
- Deterministic mechanism demos for guardrails, feedback recovery, and scope blocking.
- YAML config loading, credential status/update/clear skeleton, plugin interfaces, and trace theater loader.

## Known Limits

- `agent-harness run`, `agent-harness demo`, and `agent-harness web` are minimal working local commands in this milestone. `run` uses the safe MockLLM runtime by default and can construct an OpenAI-compatible provider from config and credentials.
- Real API-backed task execution now uses a strict JSON action protocol. The next milestone is richer governed tool execution and HITL approval flow for real task work.
- The shell tool is intentionally conservative in governed loop execution. With scope enabled and no explicit permission policy, `run_shell` is blocked by default.
- This is not a complete OS sandbox. Scope and permission checks are harness-level guardrails.
- Reflection content is scaffolded only; the student should complete `REFLECTION.md` personally.

## Install

Use Python 3.12 or newer.

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

On Linux or macOS, activate the environment with:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Verify

```bash
python -m pytest -q
python -m ruff check src/ tests/ demo/
```

The final sandbox verification for this recovery pass was:

- `114 passed`
- `All checks passed!`

## Run Demos

```bash
python -m demo.demo_guardrail
python -m demo.demo_feedback
python -m demo.demo_scope
```

The demos use `MockLLM`; they do not require an API key.

## CLI

```bash
agent-harness --help
agent-harness run "say done"
agent-harness demo
agent-harness web --trace trace.jsonl
agent-harness credentials show
agent-harness credentials update <secret>
agent-harness credentials clear
```

Credential values are never printed. The manager tries keyring first and falls back to a local `.env` file. Do not commit `.env`; it is ignored by `.gitignore`.

## API Provider Config

The default config is safe and uses `mock`:

```yaml
llm:
  provider: mock
  model: gpt-4
  temperature: 0.7
  base_url:
```

For OpenAI-compatible APIs, use:

```yaml
llm:
  provider: openai
  model: your-model
  temperature: 0.2
  base_url: https://api.openai.com/v1
```

If no key is configured, `agent-harness run --config <file>` exits safely with `API key not configured`.

Model responses must be exactly one JSON object:

```json
{"type":"done"}
```

```json
{"type":"take_note","note":"remember this"}
```

```json
{"type":"call_tool","tool":"read_file","args":{"path":"README.md"}}
```

Invalid JSON or malformed actions are fed back into the loop as an invalid-action observation.

## Trace Theater

Trace loading is implemented in `agent_harness.web.theater.load_trace_for_display`. The Streamlit UI is intentionally minimal in this milestone:

```bash
streamlit run src/agent_harness/web/theater.py
```

## Docker

Build and test in a container:

```bash
docker build -t ai4se-agent-harness .
docker run --rm ai4se-agent-harness
```

## Project Structure

```text
src/agent_harness/agent/       Agent loop and harness dependency container
src/agent_harness/governance/  Scope, permission, and HITL modules
src/agent_harness/feedback/    Feedback classifier, sensor, and healing state
src/agent_harness/trace/       JSONL trace store
src/agent_harness/tools/       Tool base classes, registry, and built-ins
src/agent_harness/config/      YAML config loader
src/agent_harness/credentials/ Credential manager
src/agent_harness/plugins/     Minimal plugin extension surface
src/agent_harness/web/         Trace theater helpers
demo/                          Deterministic mechanism demos
tests/                         Unit and integration tests
docs/superpowers/              Recovery design and implementation plan
```

## Distribution Command

For a source distribution and wheel:

```bash
python -m pip install build
python -m build
```

## Safety Boundaries

- Tests and demos avoid real destructive command examples.
- Sensitive path checks use neutral fixtures such as `.git` and `.env`.
- Shell execution should be governed by explicit permission policy in any real integration.
- API secrets should be stored through the credential manager or environment variables, never in source files.
