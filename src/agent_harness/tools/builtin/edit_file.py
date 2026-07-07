from pathlib import Path
from agent_harness.tools.base import ToolBase
from agent_harness.models import ToolResult


class EditFileTool(ToolBase):
    def __init__(self):
        super().__init__(name="edit_file", description="Replace text in a file")
    def run(self, path: str = "", old: str = "", new: str = "") -> ToolResult:
        try:
            content = Path(path).read_text(encoding="utf-8")
            if old not in content:
                return ToolResult(success=False, error=f"Could not find: {old}")
            new_content = content.replace(old, new)
            Path(path).write_text(new_content, encoding="utf-8")
            return ToolResult(success=True, output=f"Replaced 1 occurrence in {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))