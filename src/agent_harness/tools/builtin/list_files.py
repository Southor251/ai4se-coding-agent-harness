from pathlib import Path

from agent_harness.models import ToolResult
from agent_harness.tools.base import ToolBase


class ListFilesTool(ToolBase):
    def __init__(self):
        super().__init__(
            name="list_files",
            description="List files under a directory",
            args_schema={
                "path": "Directory path to list",
                "max_files": "Maximum number of files to return",
            },
        )

    def run(self, path: str = ".", max_files: int = 200) -> ToolResult:
        try:
            root = Path(path)
            if not root.exists():
                return ToolResult(success=False, error=f"Path not found: {path}")
            if root.is_file():
                return ToolResult(success=True, output=root.name)
            files = []
            for item in sorted(root.rglob("*")):
                if item.is_file():
                    files.append(item.relative_to(root).as_posix())
                if len(files) >= max_files:
                    break
            return ToolResult(success=True, output="\n".join(files))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
