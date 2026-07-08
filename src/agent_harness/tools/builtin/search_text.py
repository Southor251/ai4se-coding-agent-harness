from pathlib import Path

from agent_harness.models import ToolResult
from agent_harness.tools.base import ToolBase


class SearchTextTool(ToolBase):
    def __init__(self):
        super().__init__(
            name="search_text",
            description="Search for literal text in UTF-8 files",
            args_schema={
                "path": "Directory or file path to search",
                "query": "Literal text to search for",
                "max_matches": "Maximum number of matches to return",
            },
        )

    def run(self, path: str = ".", query: str = "", max_matches: int = 100) -> ToolResult:
        if not query:
            return ToolResult(success=False, error="query is required")
        try:
            root = Path(path)
            if not root.exists():
                return ToolResult(success=False, error=f"Path not found: {path}")
            files = [root] if root.is_file() else sorted(item for item in root.rglob("*") if item.is_file())
            matches = []
            for file_path in files:
                self._collect_matches(root, file_path, query, matches, max_matches)
                if len(matches) >= max_matches:
                    break
            return ToolResult(success=True, output="\n".join(matches))
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _collect_matches(
        self,
        root: Path,
        file_path: Path,
        query: str,
        matches: list[str],
        max_matches: int,
    ) -> None:
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            return
        display_path = file_path.name if root.is_file() else file_path.relative_to(root).as_posix()
        for line_number, line in enumerate(lines, start=1):
            if query in line:
                matches.append(f"{display_path}:{line_number}:{line}")
            if len(matches) >= max_matches:
                return
