from pathlib import Path
from dataclasses import asdict, is_dataclass
from typing import Any

from agent_harness.trace.store import TraceStore


def load_trace_for_display(path: str | Path) -> list[dict]:
    rows = []
    for record in TraceStore.load(path):
        action = record.get("llm_action") or {}
        feedback = record.get("feedback") or {}
        rows.append(
            {
                "step": record.get("step"),
                "llm": record.get("llm_text", ""),
                "action": action.get("type", ""),
                "permission": record.get("permission_verdict", ""),
                "feedback": feedback.get("category", "") if isinstance(feedback, dict) else "",
            }
        )
    return rows


def summarize_trace(records: list[Any]) -> dict:
    normalized = [_to_dict(record) for record in records]
    return {
        "steps": len(normalized),
        "tool_calls": sum(
            1 for record in normalized if (record.get("llm_action") or {}).get("type") == "call_tool"
        ),
        "denials": sum(1 for record in normalized if record.get("permission_verdict") == "deny"),
        "feedback_events": sum(1 for record in normalized if record.get("feedback")),
    }


def _to_dict(record: Any) -> dict:
    if is_dataclass(record):
        return asdict(record)
    return record


def main(path: str = ".harness/trace/session.jsonl"):
    import streamlit as st

    st.title("Agent Loop Theater")
    rows = load_trace_for_display(path)
    if not rows:
        st.info("No trace records found.")
        return
    summary = summarize_trace(TraceStore.load(path))
    st.write(summary)
    selected = st.slider("Step", 1, len(rows), 1)
    row = rows[selected - 1]
    st.subheader(f"Step {row['step']}")
    st.markdown(f"**LLM decision:** {row['llm']}")
    st.markdown(f"**Action:** {row['action']}")
    st.markdown(f"**Permission:** {row['permission']}")
    if row["feedback"]:
        st.markdown(f"**Feedback:** {row['feedback']}")


if __name__ == "__main__":
    main()
