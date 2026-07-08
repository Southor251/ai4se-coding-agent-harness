from pathlib import Path
from typing import Protocol

from agent_harness.config.loader import load_config_with_profile
from agent_harness.credentials.manager import CredentialManager
from agent_harness.runtime.factory import build_harness


class CredentialStatus(Protocol):
    def show_status(self) -> str:
        ...


def run_doctor(
    config_path: str | None = None,
    profile_path: str | None = None,
    credential_manager: CredentialStatus | None = None,
) -> list[str]:
    config_source = config_path or "config/agent-harness.yaml"
    config = load_config_with_profile(config_source, profile_path)
    harness = build_harness(config, hitl_store_path=None)
    tool_names = sorted(tool.name for tool in harness.tools.list())
    llm = config.llm
    manager = credential_manager or CredentialManager()
    workspace = Path(config.workspace_root)
    permission_rules = len(config.permission.get("rules", []))

    return [
        "agent-harness doctor",
        f"config: {config_source}",
        f"profile: {profile_path or '(none)'}",
        f"workspace_root: {workspace}",
        f"workspace_exists: {'yes' if workspace.exists() else 'no'}",
        f"provider: {llm.get('provider', 'mock')}",
        f"model: {llm.get('model', '(default)')}",
        f"base_url: {llm.get('base_url') or '(default)'}",
        f"temperature: {llm.get('temperature', '(default)')}",
        f"credential: {manager.show_status()}",
        f"tools: {len(tool_names)}",
        f"run_shell: {'enabled' if 'run_shell' in tool_names else 'disabled'}",
        f"permission_rules: {permission_rules}",
        f"memory: {'enabled' if config.memory.get('enabled', False) else 'disabled'}",
        f"max_steps: {config.max_steps}",
    ]


def add_doctor_parser(subparsers):
    parser = subparsers.add_parser("doctor", help="diagnose runtime configuration")
    parser.add_argument("--config", default=None)
    parser.add_argument("--profile", default=None)
    parser.set_defaults(handler=_doctor)


def _doctor(args) -> int:
    for line in run_doctor(args.config, args.profile):
        print(line)
    return 0
