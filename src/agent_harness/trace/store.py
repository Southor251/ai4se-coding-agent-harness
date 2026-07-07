import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


class TraceStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, record: Any):
        payload = asdict(record) if is_dataclass(record) else record
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def flush(self):
        return None

    @staticmethod
    def load(path: str | Path) -> list[dict]:
        records = []
        trace_path = Path(path)
        if not trace_path.exists():
            return records
        for line in trace_path.read_text(encoding="utf-8").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records

