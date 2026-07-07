import json
from dataclasses import asdict
from pathlib import Path

from agent_harness.models import AgentAction, HITLRequest


class HITLStore:
    def __init__(self, path: str | Path = ".harness/hitl/requests.json"):
        self.path = Path(path)

    def load(self) -> list[HITLRequest]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        requests = []
        for item in payload:
            action_payload = item["action"]
            action = AgentAction(**action_payload)
            requests.append(
                HITLRequest(
                    id=item["id"],
                    action=action,
                    reason=item["reason"],
                    status=item["status"],
                    created_at=item["created_at"],
                    decided_by=item.get("decided_by"),
                    resolved_at=item.get("resolved_at"),
                )
            )
        return requests

    def save(self, requests: list[HITLRequest]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(request) for request in requests]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
