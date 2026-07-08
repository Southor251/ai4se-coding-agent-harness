from pathlib import Path
from agent_harness.tools.base import ToolBase
from agent_harness.models import ToolResult


class WriteFileTool(ToolBase):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to file",
            args_schema={
                "path": "File path to write",
                "content": "UTF-8 text content to write",
            },
        )
    def run(self, path: str = "", content: str = "") -> ToolResult:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content, encoding="utf-8")
            return ToolResult(success=True, output=f"Written {len(content)} bytes to {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
