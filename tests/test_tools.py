from agent_harness.tools.base import ToolBase
from agent_harness.tools.registry import ToolRegistry
from agent_harness.models import ToolResult


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