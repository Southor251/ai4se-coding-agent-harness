from pathlib import Path
from agent_harness.tools.base import ToolBase
from agent_harness.models import ToolResult


class ReadFileTool(ToolBase):
    def __init__(self):
        super().__init__(name="read_file", description="Read file contents")
    def run(self, path: str = "") -> ToolResult:
        try:
            content = Path(path).read_text(encoding="utf-8")
            return ToolResult(success=True, output=content)
        except Exception as e:
            return ToolResult(success=False, error=str(e))