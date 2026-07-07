"""ScopeGuard: path fencing for workspace boundaries."""

from pathlib import Path
from agent_harness.models import ScopeVerdict

SENSITIVE_NAMES = {
    ".git",
    ".env",
}


class ScopeGuard:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()

    def check(self, path: str) -> ScopeVerdict:
        try:
            p = Path(path).resolve()
        except Exception:
            p = Path(path)
        normalized = str(p)
        workspace_root = str(self.workspace_root)
        if not self.workspace_root.exists():
            return ScopeVerdict(
                decision="outside",
                normalized_path=normalized,
                workspace_root=workspace_root,
            )
        if p == self.workspace_root or p.is_relative_to(self.workspace_root):
            relative_parts = p.relative_to(self.workspace_root).parts
            for part in relative_parts:
                if part in SENSITIVE_NAMES:
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
