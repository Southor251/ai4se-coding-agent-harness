# Demo Walkthrough

This walkthrough is a deterministic judge-facing path for the Streamlit console. It does not call a real API and does not require an API key.

## Start

```powershell
.\.venv\Scripts\python.exe -m streamlit run src\agent_harness\web\theater.py --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --global.developmentMode false
```

Open `http://127.0.0.1:8501`.

## Load The Demo

Click `Load demo walkthrough` in the sidebar.

The button creates:

- `.harness/runs/demo-walkthrough.jsonl`
- `.harness/hitl/demo-requests.json`

## What To Inspect

- `Trace` tab: the governance rail shows a successful read, a pending write approval, and a final done action.
- `HITL` tab: the pending request is selectable, the action arguments are visible, and approval controls are available.
- `Run` tab: normal governed task execution remains available for mock or configured OpenAI-compatible providers.

## Safety Boundary

The demo request is a stored `write_file` action under `.harness/demo-note.txt`. It remains pending until a human explicitly approves it.
