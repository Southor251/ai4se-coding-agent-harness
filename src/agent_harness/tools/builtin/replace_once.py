from pathlib import Path

from agent_harness.models import ToolResult
from agent_harness.tools.base import ToolBase


class ReplaceOnceTool(ToolBase):
    def __init__(self):
        super().__init__(
            name="replace_once",
            description="Replace text only when it appears exactly once",
            args_schema={
                "path": "File path to edit",
                "old": "Exact text expected once",
                "new": "Replacement text",
            },
        )

    def run(self, path: str = "", old: str = "", new: str = "") -> ToolResult:
        if not path:
            return ToolResult(success=False, error="path is required")
        if not old:
            return ToolResult(success=False, error="old is required")
        try:
            target = Path(path)
            content = target.read_text(encoding="utf-8")
            count = content.count(old)
            if count != 1:
                return ToolResult(success=False, error=f"Expected exactly one match, found {count}")
            target.write_text(content.replace(old, new, 1), encoding="utf-8")
            return ToolResult(success=True, output=f"Replaced 1 occurrence in {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
