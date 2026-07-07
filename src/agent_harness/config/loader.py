from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class HarnessConfig(BaseModel):
    max_steps: int = 50
    workspace_root: str = "."
    llm: dict[str, Any] = Field(default_factory=lambda: {"provider": "mock"})
    permission: dict[str, Any] = Field(default_factory=dict)
    feedback: dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3})
    memory: dict[str, Any] = Field(default_factory=lambda: {"enabled": False})


def load_config(path: str | Path) -> HarnessConfig:
    config_path = Path(path)
    if not config_path.exists():
        return HarnessConfig()
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return HarnessConfig.model_validate(data)


def load_config_with_profile(path: str | Path, profile_path: str | Path | None = None) -> HarnessConfig:
    config = load_config(path)
    if not profile_path:
        return config
    profile = load_config(profile_path)
    merged = _deep_merge(config.model_dump(), profile.model_dump(exclude_unset=True))
    return HarnessConfig.model_validate(merged)


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
