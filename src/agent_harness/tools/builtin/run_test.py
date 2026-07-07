import subprocess
import sys

from agent_harness.tools.base import ToolBase
from agent_harness.models import ToolResult


class RunTestTool(ToolBase):
    def __init__(self):
        super().__init__(name="run_test", description="Run tests with pytest")

    def run(self, pattern: str = "tests/") -> ToolResult:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", pattern, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout + result.stderr
            passed = result.returncode == 0
            return ToolResult(success=passed, output=output)
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Test timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
