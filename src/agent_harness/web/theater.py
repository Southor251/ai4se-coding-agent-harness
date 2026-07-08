from pathlib import Path
from dataclasses import asdict, is_dataclass
from typing import Any

from agent_harness.trace.store import TraceStore


def load_trace_for_display(path: str | Path) -> list[dict]:
    rows = []
    for record in TraceStore.load(path):
        action = record.get("llm_action") or {}
        feedback = record.get("feedback") or {}
        tool_result = record.get("tool_result") or {}
        rows.append(
            {
                "step": record.get("step"),
                "llm": record.get("llm_text", ""),
                "action": action.get("type", ""),
                "tool": action.get("tool") or "",
                "permission": record.get("permission_verdict", ""),
                "hitl": record.get("hitl_status") or "",
                "tool_success": tool_result.get("success", "") if isinstance(tool_result, dict) else "",
                "tool_output": tool_result.get("output", "") if isinstance(tool_result, dict) else "",
                "tool_error": tool_result.get("error", "") if isinstance(tool_result, dict) else "",
                "feedback": feedback.get("category", "") if isinstance(feedback, dict) else "",
                "answer": action.get("answer") or "",
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


def main(path: str = ".harness/runs/latest.jsonl"):
    import streamlit as st

    from agent_harness.web.services import (
        DEFAULT_CONFIG_PATH,
        DEFAULT_HITL_STORE_PATH,
        DEFAULT_PROFILE_PATH,
        DEFAULT_TRACE_DIR,
        approve_and_continue_hitl_request,
        approve_hitl_request,
        deny_hitl_request,
        list_hitl_requests,
        list_trace_runs,
        run_task,
    )

    st.set_page_config(page_title="Agent Harness Console", layout="wide")
    _apply_console_style(st)

    st.title("Agent Harness Console")
    st.caption("Run governed tasks, inspect trace records, and resolve human approval requests.")

    with st.sidebar:
        st.header("Run Control")
        goal = st.text_area("Goal", value="say done")
        config_path = st.text_input("Config path", value=DEFAULT_CONFIG_PATH)
        profile_path = st.text_input("Profile path", value=DEFAULT_PROFILE_PATH)
        trace_path = st.text_input("Trace path", value=path)
        hitl_store_path = st.text_input("HITL store", value=DEFAULT_HITL_STORE_PATH)
        trace_runs = list_trace_runs(DEFAULT_TRACE_DIR)
        if trace_runs:
            selected_trace = st.selectbox("Trace history", trace_runs, format_func=lambda row: row["name"])
            if selected_trace:
                trace_path = selected_trace["path"]
        if st.button("Run task", use_container_width=True):
            result = run_task(
                goal,
                config_path=config_path,
                profile_path=profile_path or None,
                trace_path=trace_path,
            )
            st.session_state["run_result"] = result

    rows = load_trace_for_display(trace_path)
    summary = summarize_trace(TraceStore.load(trace_path)) if rows else {}
    requests = list_hitl_requests(hitl_store_path)
    pending_requests = [request for request in requests if request["status"] == "pending"]

    metric_cols = st.columns(5)
    metric_cols[0].metric("Steps", summary.get("steps", 0))
    metric_cols[1].metric("Tool calls", summary.get("tool_calls", 0))
    metric_cols[2].metric("Denials", summary.get("denials", 0))
    metric_cols[3].metric("Feedback", summary.get("feedback_events", 0))
    metric_cols[4].metric("Pending HITL", len(pending_requests))

    result = st.session_state.get("run_result")
    run_tab, trace_tab, hitl_tab = st.tabs(["Run", "Trace", "HITL"])

    with run_tab:
        st.subheader("Latest run")
        if result:
            st.success(f"halt_reason={result.halt_reason} steps={result.steps}")
            st.text_area("Answer", value=result.answer, height=160)
            st.code(result.trace_path or trace_path)
        else:
            st.info("Run a task from the sidebar to populate this panel.")

    with trace_tab:
        st.subheader("Trace inspector")
        st.caption(trace_path)
        if not rows:
            st.info("No trace records found.")
        else:
            selected = st.slider("Step", 1, len(rows), len(rows))
            row = rows[selected - 1]
            left, right = st.columns([2, 1])
            with left:
                st.markdown("**LLM output**")
                st.text_area("LLM output", value=row["llm"], height=260, label_visibility="collapsed")
            with right:
                st.markdown("**Action**")
                st.json(
                    {
                        "step": row["step"],
                        "action": row["action"],
                        "tool": row["tool"],
                        "permission": row["permission"],
                        "hitl": row["hitl"],
                        "feedback": row["feedback"],
                    }
                )
            if row["tool_output"] or row["tool_error"]:
                st.markdown("**Tool result**")
                st.text_area(
                    "Tool result",
                    value=row["tool_output"] or row["tool_error"],
                    height=220,
                    label_visibility="collapsed",
                )
            if row["answer"]:
                st.markdown("**Final answer**")
                st.info(row["answer"])

    with hitl_tab:
        st.subheader("Human approval queue")
        if requests:
            st.dataframe(requests, use_container_width=True)
        else:
            st.info("No HITL requests found.")
        request_id = st.text_input("Request id")
        approve_col, continue_col, deny_col = st.columns(3)
        with approve_col:
            if st.button("Approve", use_container_width=True) and request_id:
                approval = approve_hitl_request(
                    request_id,
                    config_path=config_path,
                    profile_path=profile_path or None,
                    store_path=hitl_store_path,
                )
                st.write({"success": approval.success, "output": approval.output, "error": approval.error})
        with continue_col:
            if st.button("Approve + Continue", use_container_width=True) and request_id:
                continued = approve_and_continue_hitl_request(
                    request_id,
                    config_path=config_path,
                    profile_path=profile_path or None,
                    store_path=hitl_store_path,
                )
                st.session_state["run_result"] = continued
                st.write(
                    {
                        "answer": continued.answer,
                        "halt_reason": continued.halt_reason,
                        "steps": continued.steps,
                    }
                )
        with deny_col:
            if st.button("Deny", use_container_width=True) and request_id:
                denied = deny_hitl_request(request_id, hitl_store_path)
                st.write({"id": denied.id, "status": denied.status})


def _apply_console_style(st) -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #f7f8f5;
            color: #17201b;
        }
        [data-testid="stSidebar"] {
            background: #101915;
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #e7ece6;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #dbe3dc;
            border-radius: 8px;
            padding: 12px;
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] p,
        div[data-testid="stMetric"] span,
        div[data-testid="stMetricValue"] {
            color: #17201b !important;
        }
        div[data-testid="stMetricValue"] {
            font-weight: 700;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background: #ffffff;
            border: 1px solid #dbe3dc;
            border-radius: 8px 8px 0 0;
            padding: 10px 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
