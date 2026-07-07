# Task 3.2-3.7: 5 built-in tools

**Files:**
- Create: `src/agent_harness/tools/builtin/__init__.py`
- Create: `src/agent_harness/tools/builtin/read_file.py`
- Create: `src/agent_harness/tools/builtin/write_file.py`
- Create: `src/agent_harness/tools/builtin/edit_file.py`
- Create: `src/agent_harness/tools/builtin/run_shell.py`
- Create: `src/agent_harness/tools/builtin/run_test.py`
- Update: `tests/test_tools.py`

**Goal:** 5 core coding tools, each with ToolBase subclass.

**Dependencies:** T3.1 (ToolBase, ToolRegistry)

## Tool implementations

Each tool extends `ToolBase` and implements `run(**kwargs) -> ToolResult`.

### read_file
```python
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
```

### write_file
```python
class WriteFileTool(ToolBase):
    def __init__(self):
        super().__init__(name="write_file", description="Write content to file")
    def run(self, path: str = "", content: str = "") -> ToolResult:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content, encoding="utf-8")
            return ToolResult(success=True, output=f"Written {len(content)} bytes to {path}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

### edit_file
```python
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
```

### run_shell
```python
import subprocess
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
```

### run_test
```python
class RunTestTool(ToolBase):
    def __init__(self):
        super().__init__(name="run_test", description="Run tests with pytest")
    def run(self, pattern: str = "tests/") -> ToolResult:
        try:
            result = subprocess.run(
                ["pytest", pattern, "-v", "--tb=short"],
                capture_output=True, text=True, timeout=60
            )
            output = result.stdout + result.stderr
            passed = "passed" in result.stdout and "failed" not in result.stdout
            return ToolResult(success=passed, output=output)
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Test timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

## Tests

Add to `tests/test_tools.py`:

```python
import tempfile
from pathlib import Path
from agent_harness.tools.builtin.read_file import ReadFileTool
from agent_harness.tools.builtin.write_file import WriteFileTool
from agent_harness.tools.builtin.edit_file import EditFileTool
from agent_harness.tools.builtin.run_shell import RunShellTool
from agent_harness.tools.builtin.run_test import RunTestTool

def test_read_file_success():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("hello")
        path = f.name
    tool = ReadFileTool()
    result = tool.run(path=path)
    assert result.success
    assert "hello" in result.output

def test_read_file_not_found():
    tool = ReadFileTool()
    result = tool.run(path="/nonexistent/file.txt")
    assert not result.success

def test_write_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "test.txt")
        tool = WriteFileTool()
        result = tool.run(path=path, content="hello world")
        assert result.success
        assert Path(path).read_text() == "hello world"

def test_edit_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "test.txt")
        Path(path).write_text("old content")
        tool = EditFileTool()
        result = tool.run(path=path, old="old", new="new")
        assert result.success
        assert "new content" in Path(path).read_text()

def test_edit_file_not_found():
    tool = EditFileTool()
    result = tool.run(path="/nonexistent", old="x", new="y")
    assert not result.success

def test_run_shell_echo():
    tool = RunShellTool()
    result = tool.run(command="echo hello")
    assert result.success
    assert "hello" in result.output

def test_run_shell_fail():
    tool = RunShellTool()
    result = tool.run(command="exit 1")
    assert not result.success

def test_run_test():
    tool = RunTestTool()
    result = tool.run(pattern="tests/test_import.py")
    assert result.success
```