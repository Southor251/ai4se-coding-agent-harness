from pathlib import Path

from agent_harness.models import ToolResult
from agent_harness.tools.base import ToolBase


class ReadManyTool(ToolBase):
    def __init__(self):
        super().__init__(
            name="read_many",
            description="Read multiple UTF-8 text files",
            args_schema={
                "paths": "List of file paths to read",
                "max_bytes": "Maximum bytes per file",
            },
        )

    def run(self, paths: list[str] | None = None, max_bytes: int = 20000) -> ToolResult:
        if not paths:
            return ToolResult(success=False, error="paths is required")
        chunks = []
        try:
            for raw_path in paths:
                path = Path(raw_path)
                if not path.exists():
                    chunks.append(f"## {raw_path}\nERROR: path not found")
                    continue
                if not path.is_file():
                    chunks.append(f"## {raw_path}\nERROR: not a file")
                    continue
                data = path.read_bytes()[:max_bytes]
                text = data.decode("utf-8", errors="replace")
                chunks.append(f"## {raw_path}\n{text}")
            return ToolResult(success=True, output="\n\n".join(chunks))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
