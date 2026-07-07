# Task 4.2 + 4.3: ScopeGuard + HITL

**Files:**
- Create: `src/agent_harness/governance/scope.py`
- Create: `src/agent_harness/governance/hitl.py`
- Create: `tests/test_scope.py`
- Create: `tests/test_hitl.py`

**Goal:** ScopeGuard path fencing + HITL state machine.

**Dependencies:** T4.1 (PermissionPolicy), T1.1 (models)

## ScopeGuard

```python
# src/agent_harness/governance/scope.py
import os
from pathlib import Path
from agent_harness.models import ScopeVerdict

SENSITIVE_PATTERNS = [
    "/etc/", "/var/lib/", "/boot/", "/sys/", "/proc/",
    "C:\\Windows\\", "C:\\Program Files\\",
    ".git/", ".env",
]

class ScopeGuard:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = str(Path(workspace_root).resolve())

    def check(self, path: str) -> ScopeVerdict:
        try:
            normalized = str(Path(path).resolve())
        except Exception:
            normalized = path
        for pattern in SENSITIVE_PATTERNS:
            if pattern in normalized:
                return ScopeVerdict(decision="sensitive", normalized_path=normalized, workspace_root=self.workspace_root)
        if normalized.startswith(self.workspace_root):
            return ScopeVerdict(decision="inside", normalized_path=normalized, workspace_root=self.workspace_root)
        return ScopeVerdict(decision="outside", normalized_path=normalized, workspace_root=self.workspace_root)
```

## HITL

```python
# src/agent_harness/governance/hitl.py
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

    def check_timeout(self, req: HITLRequest) -> bool:
        if req.status == "pending" and (time.time() - req.created_at) > self.timeout:
            req.status = "timed_out"
            req.decided_by = "timeout"
            req.resolved_at = time.time()
            return True
        return False

    def _find(self, req_id: str) -> HITLRequest | None:
        return next((r for r in self.requests if r.id == req_id), None)
```

## Tests

```python
# tests/test_scope.py
from agent_harness.governance.scope import ScopeGuard
import tempfile
from pathlib import Path

def test_inside_workspace():
    with tempfile.TemporaryDirectory() as tmp:
        guard = ScopeGuard(workspace_root=tmp)
        test_file = Path(tmp) / "test.txt"
        test_file.write_text("hello")
        verdict = guard.check(str(test_file))
        assert verdict.decision == "inside"

def test_outside_workspace():
    guard = ScopeGuard(workspace_root="/workspace")
    verdict = guard.check("/etc/passwd")
    assert verdict.decision == "outside"

def test_sensitive_path():
    guard = ScopeGuard(workspace_root="/workspace")
    verdict = guard.check("/workspace/.git/config")
    assert verdict.decision == "sensitive"

def test_sensitive_etc():
    guard = ScopeGuard(workspace_root="/workspace")
    verdict = guard.check("/workspace/../etc/passwd")
    assert verdict.decision in ("outside", "sensitive")
```

```python
# tests/test_hitl.py
from agent_harness.governance.hitl import HITLManager
from agent_harness.models import AgentAction

def test_create_request():
    h = HITLManager()
    req = h.create_request(AgentAction(type="call_tool", tool="rm"), "dangerous")
    assert req.status == "pending"
    assert req.id is not None

def test_approve():
    h = HITLManager()
    req = h.create_request(AgentAction(type="call_tool", tool="rm"), "dangerous")
    h.approve(req.id)
    assert req.status == "approved"

def test_deny():
    h = HITLManager()
    req = h.create_request(AgentAction(type="call_tool", tool="rm"), "dangerous")
    h.deny(req.id)
    assert req.status == "denied"

def test_timeout():
    h = HITLManager(timeout=0)
    import time
    time.sleep(0.01)
    req = h.create_request(AgentAction(type="call_tool", tool="rm"), "dangerous")
    assert h.check_timeout(req) == True
    assert req.status == "timed_out"
```

## TDD
1. Write test_scope.py + test_hitl.py
2. Run → FAIL
3. Create scope.py + hitl.py
4. Run → 8/8 PASS
5. Run full suite → all pass
6. Commit