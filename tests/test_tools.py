from agent_harness.tools.base import ToolBase
from agent_harness.tools.registry import ToolRegistry
from agent_harness.models import ToolResult
import tempfile
from pathlib import Path
from agent_harness.tools.builtin.read_file import ReadFileTool
from agent_harness.tools.builtin.write_file import WriteFileTool
from agent_harness.tools.builtin.edit_file import EditFileTool
from agent_harness.tools.builtin.run_shell import RunShellTool
from agent_harness.tools.builtin.run_test import RunTestTool
from agent_harness.tools.builtin.list_files import ListFilesTool
from agent_harness.tools.builtin.search_text import SearchTextTool
from unittest.mock import patch


class EchoTool(ToolBase):
    def __init__(self):
        super().__init__(name="echo", description="echoes input")
    def run(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=str(kwargs.get("msg", "")))


def test_tool_base_abstract():
    import pytest
    with pytest.raises(TypeError):
        ToolBase(name="test")


def test_registry_register_list():
    t = EchoTool()
    reg = ToolRegistry()
    reg.register(t)
    assert len(reg.list()) == 1
    assert reg.list()[0].name == "echo"


def test_registry_get():
    t = EchoTool()
    reg = ToolRegistry()
    reg.register(t)
    assert reg.get("echo") is t
    assert reg.get("nonexistent") is None


def test_tool_run():
    t = EchoTool()
    result = t.run(msg="hello")
    assert result.success
    assert result.output == "hello"


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


def test_run_test_uses_return_code_for_success():
    class Completed:
        returncode = 1
        stdout = "1 passed"
        stderr = ""

    tool = RunTestTool()
    with patch("agent_harness.tools.builtin.run_test.subprocess.run", return_value=Completed()):
        result = tool.run(pattern="tests/test_import.py")

    assert not result.success


def test_list_files_tool_lists_relative_files(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "b.txt").write_text("b", encoding="utf-8")

    result = ListFilesTool().run(path=str(tmp_path))

    assert result.success
    assert "a.txt" in result.output
    assert "nested/b.txt" in result.output


def test_search_text_tool_finds_matches(tmp_path):
    (tmp_path / "a.txt").write_text("alpha\nbeta\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("gamma\n", encoding="utf-8")

    result = SearchTextTool().run(path=str(tmp_path), query="alpha")

    assert result.success
    assert "a.txt:1:alpha" in result.output


def test_builtin_tools_expose_argument_schemas():
    assert ReadFileTool().args_schema == {"path": "File path to read"}
    assert WriteFileTool().args_schema == {
        "path": "File path to write",
        "content": "UTF-8 text content to write",
    }
    assert EditFileTool().args_schema == {
        "path": "File path to edit",
        "old": "Text to replace",
        "new": "Replacement text",
    }
    assert RunTestTool().args_schema == {"pattern": "Pytest path or test pattern"}
    assert ListFilesTool().args_schema == {
        "path": "Directory path to list",
        "max_files": "Maximum number of files to return",
    }
    assert SearchTextTool().args_schema == {
        "path": "Directory or file path to search",
        "query": "Literal text to search for",
        "max_matches": "Maximum number of matches to return",
    }
