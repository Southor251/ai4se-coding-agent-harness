import subprocess
from pathlib import Path

from agent_harness.models import ToolResult
from agent_harness.tools.base import ToolBase


class GitDiffTool(ToolBase):
    def __init__(self):
        super().__init__(
            name="git_diff",
            description="Show git diff for a repository or target path",
            args_schema={
                "path": "Repository path",
                "target": "Optional file or directory path to diff",
            },
        )

    def run(self, path: str = ".", target: str = "") -> ToolResult:
        try:
            repo = Path(path)
            command = ["git", "-C", str(repo), "diff"]
            if target:
                command.extend(["--", target])
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            return ToolResult(success=result.returncode == 0, output=output, error=None if result.returncode == 0 else output)
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="git diff timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
