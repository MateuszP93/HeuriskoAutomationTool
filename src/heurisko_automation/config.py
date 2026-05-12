from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from heurisko_automation.errors import ConfigError


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RuntimeConfig:
    root: Path
    app: dict[str, Any]
    windows: dict[str, Any]
    locators: dict[str, Any]
    workflows_dir: Path
    status_monitor: dict[str, Any] = field(default_factory=dict)


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config file does not exist: {path}")

    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}

    if not isinstance(data, dict):
        raise ConfigError(f"Config file must contain a mapping: {path}")

    return data


def load_config(root: Path | str | None = None) -> RuntimeConfig:
    project_root = Path(root).resolve() if root else PROJECT_ROOT
    configs = project_root / "configs"

    app_config = read_yaml(configs / "app.yaml")
    windows_config = read_yaml(configs / "windows.yaml")
    locators_config = read_yaml(configs / "locators.yaml")

    return RuntimeConfig(
        root=project_root,
        app=app_config.get("app", {}),
        status_monitor=app_config.get("status_monitor", {}),
        windows=windows_config.get("windows", {}),
        locators=locators_config.get("locators", {}),
        workflows_dir=configs / "workflows",
    )
