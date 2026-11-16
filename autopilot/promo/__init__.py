"""Kawaii app promos: Godot gameplay capture -> assembled 9:16 reel -> publish."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REGISTRY = Path(__file__).resolve().parent / "apps.yaml"


def load_registry(path: Path = REGISTRY) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def app_config(app_id: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    reg = registry or load_registry()
    apps = reg.get("apps", {})
    if app_id not in apps:
        raise KeyError(f"unknown app {app_id!r}; known: {', '.join(apps)}")
    app = dict(apps[app_id])
    if app.get("status") != "ready":
        raise NotImplementedError(f"{app_id}: template {app.get('template')!r} is not built yet")
    app["id"] = app_id
    app["path"] = str(Path(reg["games_dir"]) / app["repo"])
    return app
