import subprocess
from agent_harness.tools.base import ToolBase
from agent_harness.models import ToolResult


class RunShellTool(ToolBase):
    def __init__(self):
        super().__init__(name="run_shell", description="Execute a shell command")
    def run(self, command: str = "") -> ToolResult:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
            return ToolResult(success=result.returncode == 0, output=output)
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Command timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))