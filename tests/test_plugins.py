from agent_harness.plugins.base import FeedbackPlugin, PolicyPlugin, ToolPlugin
from agent_harness.plugins.registry import PluginRegistry


class ExampleToolPlugin(ToolPlugin):
    name = "example-tool"

    def register(self, harness):
        return "registered"


class ExamplePolicyPlugin(PolicyPlugin):
    name = "example-policy"

    def register(self, harness):
        return "registered"


class ExampleFeedbackPlugin(FeedbackPlugin):
    name = "example-feedback"

    def register(self, harness):
        return "registered"


def test_plugin_registry_registers_and_lists_plugins():
    registry = PluginRegistry()
    plugin = ExampleToolPlugin()

    registry.register(plugin)

    assert registry.list_names() == ["example-tool"]
    assert registry.get("example-tool") is plugin


def test_plugin_registry_rejects_duplicate_names():
    registry = PluginRegistry()
    registry.register(ExampleToolPlugin())

    try:
        registry.register(ExampleToolPlugin())
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("expected duplicate plugin registration to fail")


def test_policy_and_feedback_plugins_share_contract():
    registry = PluginRegistry()
    registry.register(ExamplePolicyPlugin())
    registry.register(ExampleFeedbackPlugin())

    assert registry.get("example-policy").register(None) == "registered"
    assert registry.get("example-feedback").register(None) == "registered"
