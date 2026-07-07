from agent_harness.config.loader import HarnessConfig, load_config, load_config_with_profile


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


def test_load_openai_config_from_yaml(tmp_path):
    config_path = tmp_path / "agent-harness.yaml"
    config_path.write_text(
        "\n".join(
            [
                "llm:",
                "  provider: openai",
                "  model: custom-model",
                "  base_url: https://example.test/v1",
                "  temperature: 0.2",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.llm["provider"] == "openai"
    assert config.llm["model"] == "custom-model"
    assert config.llm["base_url"] == "https://example.test/v1"
    assert config.llm["temperature"] == 0.2


def test_load_permission_rules_from_yaml(tmp_path):
    config_path = tmp_path / "agent-harness.yaml"
    config_path.write_text(
        "\n".join(
            [
                "permission:",
                "  rules:",
                "    - name: ask writes",
                "      pattern: .*",
                "      verdict: ask",
                "      rule_type: path",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.permission["rules"][0]["name"] == "ask writes"


def test_load_config_with_profile_overrides_base(tmp_path):
    base_path = tmp_path / "base.yaml"
    profile_path = tmp_path / "profile.yaml"
    base_path.write_text(
        "\n".join(
            [
                "max_steps: 7",
                "workspace_root: ./base",
                "llm:",
                "  provider: mock",
                "  model: base-model",
                "memory:",
                "  enabled: false",
            ]
        ),
        encoding="utf-8",
    )
    profile_path.write_text(
        "\n".join(
            [
                "workspace_root: ./profile",
                "llm:",
                "  provider: openai",
                "memory:",
                "  enabled: true",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config_with_profile(base_path, profile_path)

    assert config.max_steps == 7
    assert config.workspace_root == "./profile"
    assert config.llm["provider"] == "openai"
    assert config.llm["model"] == "base-model"
    assert config.memory["enabled"] is True
