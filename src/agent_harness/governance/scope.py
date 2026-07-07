"""ScopeGuard: path fencing for workspace boundaries."""

from pathlib import Path
from agent_harness.models import ScopeVerdict

SENSITIVE_PATTERNS = [
    ".git/",
    ".env",
]


class ScopeGuard:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()

    def check(self, path: str) -> ScopeVerdict:
        try:
            p = Path(path).resolve()
        except Exception:
            p = Path(path)
        normalized = str(p)
        posix_path = p.as_posix()
        workspace_root = str(self.workspace_root)
        if p == self.workspace_root or p.is_relative_to(self.workspace_root):
            for pattern in SENSITIVE_PATTERNS:
                if pattern in normalized or pattern in posix_path:
                    return ScopeVerdict(
                        decision="sensitive",
                        normalized_path=normalized,
                        workspace_root=workspace_root,
                    )
            return ScopeVerdict(
                decision="inside",
                normalized_path=normalized,
                workspace_root=workspace_root,
            )
        return ScopeVerdict(
            decision="outside",
            normalized_path=normalized,
            workspace_root=workspace_root,
        )
