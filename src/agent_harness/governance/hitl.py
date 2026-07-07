"""HITL state machine for human-in-the-loop approval."""

import time
import uuid

from agent_harness.models import AgentAction, HITLRequest


class HITLManager:
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.requests: list[HITLRequest] = []

    def create_request(self, action: AgentAction, reason: str) -> HITLRequest:
        req = HITLRequest(
            id=str(uuid.uuid4())[:8],
            action=action,
            reason=reason,
            status="pending",
            created_at=time.time(),
        )
        self.requests.append(req)
        return req

    def approve(self, req_id: str) -> HITLRequest | None:
        req = self._find(req_id)
        if req and req.status == "pending":
            req.status = "approved"
            req.decided_by = "human"
            req.resolved_at = time.time()
        return req

    def deny(self, req_id: str) -> HITLRequest | None:
        req = self._find(req_id)
        if req and req.status == "pending":
            req.status = "denied"
            req.decided_by = "human"
            req.resolved_at = time.time()
        return req

    def find(self, req_id: str) -> HITLRequest | None:
        return self._find(req_id)

    def check_timeout(self, req: HITLRequest) -> bool:
        if req.status == "pending" and (time.time() - req.created_at) > self.timeout:
            req.status = "timed_out"
            req.decided_by = "timeout"
            req.resolved_at = time.time()
            return True
        return False

    def _find(self, req_id: str) -> HITLRequest | None:
        return next((r for r in self.requests if r.id == req_id), None)
