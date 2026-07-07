from pathlib import Path

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


def main(path: str = ".harness/trace/session.jsonl"):
    import streamlit as st

    st.title("Agent Loop Theater")
    rows = load_trace_for_display(path)
    if not rows:
        st.info("No trace records found.")
        return
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
