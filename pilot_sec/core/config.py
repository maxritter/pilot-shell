"""Config file management for pilot-sec."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "project": {
        "name": "",
    },
    "policy": {
        "level": "standard",  # relaxed|standard|strict
        "packs": [],
    },
    "logging": {
        "audit": True,
        "redaction": True,
    },
    "scanners": {
        "enabled": [],  # empty = all available
        "timeout": 300,
    },
    "integrations": {
        "github": {
            "enabled": False,
        },
    },
    "risk": {
        "defaults": {
            "fail_on": "high",
            "threshold": 70,
        },
    },
    "env": {
        "defaults": {
            "network": "on",
            "write": "workspace",
            "secrets": "prompt",
        },
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


class PilotSecConfig:
    """Loaded and validated configuration."""

    def __init__(self, data: dict[str, Any], path: Optional[Path] = None):
        self._data = data
        self.path = path

    @classmethod
    def load(cls, pilot_sec_dir: Path, extra_path: Optional[str] = None) -> "PilotSecConfig":
        data = dict(DEFAULT_CONFIG)
        config_path = pilot_sec_dir / "config.yaml"
        if config_path.exists():
            loaded = yaml.safe_load(config_path.read_text()) or {}
            data = _deep_merge(data, loaded)
        if extra_path:
            extra = yaml.safe_load(Path(extra_path).read_text()) or {}
            data = _deep_merge(data, extra)
        return cls(data, config_path)

    @classmethod
    def defaults(cls) -> "PilotSecConfig":
        return cls(dict(DEFAULT_CONFIG))

    def get(self, key: str, default: Any = None) -> Any:
        """Dot-notation key lookup: 'policy.level'."""
        parts = key.split(".")
        val: Any = self._data
        for p in parts:
            if not isinstance(val, dict):
                return default
            val = val.get(p, default)
        return val

    def set(self, key: str, value: Any) -> None:
        parts = key.split(".")
        d = self._data
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        # Attempt type coercion if existing value has a type
        existing = d.get(parts[-1])
        if existing is not None:
            if isinstance(existing, bool):
                value = str(value).lower() in ("true", "1", "yes")
            elif isinstance(existing, int):
                value = int(value)
            elif isinstance(existing, float):
                value = float(value)
        d[parts[-1]] = value

    def save(self) -> None:
        if self.path is None:
            raise RuntimeError("No config path set")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(yaml.dump(self._data, default_flow_style=False))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def validate(self) -> list[str]:
        """Return list of validation errors (empty = valid)."""
        errors: list[str] = []
        level = self.get("policy.level")
        if level not in ("relaxed", "standard", "strict"):
            errors.append(f"policy.level must be relaxed|standard|strict, got: {level!r}")
        timeout = self.get("scanners.timeout")
        if not isinstance(timeout, int) or timeout < 1:
            errors.append(f"scanners.timeout must be a positive integer, got: {timeout!r}")
        return errors
