from agent_harness.config.loader import HarnessConfig, load_config


def test_default_config_values():
    config = HarnessConfig()

    assert config.max_steps == 50
    assert config.workspace_root == "."
    assert config.llm["provider"] == "mock"


def test_load_config_from_yaml(tmp_path):
    config_path = tmp_path / "agent-harness.yaml"
    config_path.write_text(
        "max_steps: 7\nworkspace_root: ./workspace\nllm:\n  provider: mock\n",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.max_steps == 7
    assert config.workspace_root == "./workspace"
    assert config.llm["provider"] == "mock"
