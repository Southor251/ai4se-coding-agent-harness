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
