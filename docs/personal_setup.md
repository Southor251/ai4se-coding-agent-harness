# Personal Harness Setup

This guide describes how to run the harness as a local, governed coding-agent application.

## 1. Install

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## 2. Verify The Local Build

```bash
python scripts/verify_delivery.py
```

For a command preview only:

```bash
python scripts/verify_delivery.py --dry-run
```

## 3. Configure Your API

The safe default uses `mock`. To use an OpenAI-compatible API, create or edit a profile based on `config/personal-harness.yaml`:

```yaml
workspace_root: "."
llm:
  provider: openai
  model: your-model
  temperature: 0.2
  base_url: https://your-api.example/v1
permission:
  rules:
    - name: ask before writes
      pattern: .*
      verdict: ask
      rule_type: path
memory:
  enabled: true
```

Store the API key through the credential manager or an environment variable. Do not put secrets in YAML files.

```bash
agent-harness credentials update <secret>
agent-harness credentials show
```

Check the active runtime before running a real task:

```bash
agent-harness doctor --profile config/personal-harness.yaml
```

The doctor output should show your provider, model, base URL, `credential: configured`, and `run_shell: disabled`. It never prints the key value.

## 4. Run A Task

```bash
agent-harness run "say done" --profile config/personal-harness.yaml --trace .harness/runs/latest.jsonl
```

For the first real API smoke, use a read-only goal against a small workspace:

```bash
agent-harness run "Read README.md and summarize it in one sentence." --profile config/personal-harness.yaml --trace .harness/runs/real-readonly-smoke.jsonl
```

The model must return one JSON action at a time:

```json
{"type":"call_tool","tool":"read_file","args":{"path":"README.md"}}
```

```json
{"type":"done","answer":"finished"}
```

## 5. Handle HITL Requests

List pending requests:

```bash
agent-harness hitl list --store .harness/hitl/requests.json
```

Approve and execute one pending action:

```bash
agent-harness hitl approve <request_id> --profile config/personal-harness.yaml --store .harness/hitl/requests.json
```

Approve and continue a saved-context task:

```bash
agent-harness hitl approve <request_id> --continue --profile config/personal-harness.yaml --store .harness/hitl/requests.json
```

Deny without executing:

```bash
agent-harness hitl deny <request_id> --store .harness/hitl/requests.json
```

You can create a deterministic pending write request without using a real API:

```bash
agent-harness smoke hitl-write --workspace .harness/smoke-workspace --store .harness/hitl/smoke-requests.json --trace .harness/runs/hitl-write-smoke.jsonl
```

The command prints a `pending_request` id and a copy-paste `approve_command`. The target file should not exist until you approve the request.

## 6. Use The Web Console

```bash
streamlit run src/agent_harness/web/theater.py
```

The Web console can run goals, select trace history from `.harness/runs`, inspect trace steps, and approve or deny HITL requests.

On Windows, prefer this explicit startup command:

```powershell
.\.venv\Scripts\python.exe -m streamlit run src\agent_harness\web\theater.py --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --global.developmentMode false
```

For a server that stays alive after the launching command returns, open a visible PowerShell window:

```powershell
Start-Process -FilePath powershell.exe -ArgumentList @(
  '-NoExit','-ExecutionPolicy','Bypass','-Command',
  'cd "<repo>"; .\.venv\Scripts\python.exe -m streamlit run src\agent_harness\web\theater.py --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --global.developmentMode false'
) -WindowStyle Normal
```

Then open `http://127.0.0.1:8501`.

## Safety Defaults

- `run_shell` is not registered in the default governed runtime.
- File actions are checked by `ScopeGuard`.
- The starter personal profile asks before writes.
- API secrets should stay in the credential manager, environment variables, or an ignored local `.env` file.
