from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import yaml


def load_yaml(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_configs(
    camera_path: str | Path = "config/camera_intrinsics.yaml",
    handeye_path: str | Path = "config/handeye_T_base_cam.yaml",
    task_path: str | Path = "config/task_params.yaml",
) -> Dict[str, Any]:
    return {
        "camera": load_yaml(camera_path),
        "handeye": load_yaml(handeye_path),
        "task": load_yaml(task_path),
    }
