# Static HTML Spike

Task 6 created a controlled static console prototype without adding a new runtime dependency.

## Files

- `src/agent_harness/server/api.py`
- `src/agent_harness/server/static/index.html`
- `src/agent_harness/server/static/styles.css`
- `src/agent_harness/server/static/app.js`

## Decision

Streamlit remains the official runnable Web console for the current delivery. It already runs governed tasks, loads traces, manages HITL requests, and supports the deterministic demo walkthrough.

The static HTML prototype is useful as a visual and structural reference for a future FastAPI or desktop-style frontend, but it is not yet connected to live task execution or HITL mutation endpoints.

## Rationale

- Avoid adding FastAPI and browser-state complexity before the core demo is stable.
- Keep the competition demo easy to start with the existing Streamlit command.
- Preserve a higher-polish visual target for a later frontend rewrite.

## Next Backend Shape

If the static frontend is promoted later, expose small JSON endpoints around the existing service helpers:

- `GET /api/trace?path=...`
- `GET /api/hitl?store=...`
- `POST /api/run`
- `POST /api/hitl/{id}/approve`
- `POST /api/hitl/{id}/deny`

The endpoint layer should call the same governed runtime and HITL store helpers already used by CLI and Streamlit.
