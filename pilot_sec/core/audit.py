"""Audit trail — append-only event log per run."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AuditLog:
    def __init__(self, run_dir: Path, run_id: str, enabled: bool = True):
        self.run_dir = run_dir
        self.run_id = run_id
        self.enabled = enabled
        self._events: list[dict[str, Any]] = []
        if enabled:
            run_dir.mkdir(parents=True, exist_ok=True)

    def record(self, event_type: str, payload: Optional[dict[str, Any]] = None) -> None:
        if not self.enabled:
            return
        event = {
            "run_id": self.run_id,
            "event": event_type,
            "timestamp": _now(),
            **(payload or {}),
        }
        self._events.append(event)
        self._append(event)

    def _append(self, event: dict[str, Any]) -> None:
        log_file = self.run_dir / "event.json"
        existing: list[dict[str, Any]] = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text())
            except Exception:
                existing = []
        existing.append(event)
        log_file.write_text(json.dumps(existing, indent=2))

    def finalize(self, status: str, decision: str, extra: Optional[dict[str, Any]] = None) -> None:
        self.record("finalize", {"status": status, "decision": decision, **(extra or {})})

    @property
    def log_path(self) -> Path:
        return self.run_dir / "event.json"
