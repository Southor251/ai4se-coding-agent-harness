from pathlib import Path

from agent_harness.web.services import list_hitl_requests, trace_summary, trace_timeline


STATIC_DIR = Path(__file__).with_name("static")


def load_console_payload(trace_path: str, store_path: str) -> dict:
    return {
        "summary": trace_summary(trace_path),
        "timeline": trace_timeline(trace_path),
        "hitl": list_hitl_requests(store_path),
    }


def static_app_available(static_dir: Path = STATIC_DIR) -> dict:
    required = {"index.html", "styles.css", "app.js"}
    files = {path.name for path in static_dir.glob("*") if path.is_file()} if static_dir.exists() else set()
    return {"available": required.issubset(files), "files": sorted(files)}
