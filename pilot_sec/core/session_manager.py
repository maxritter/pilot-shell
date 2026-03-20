"""Session lifecycle management."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    rand = uuid.uuid4().hex[:6]
    return f"{prefix}_{ts}_{rand}"


class Session:
    def __init__(self, data: dict[str, Any], path: Path):
        self._data = data
        self.path = path

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def status(self) -> str:
        return self._data.get("status", "active")

    @property
    def started_at(self) -> str:
        return self._data.get("started_at", "")

    def record_command(self, cmd: str, result: dict[str, Any]) -> None:
        self._data.setdefault("commands", []).append({
            "command": cmd,
            "result": result,
            "timestamp": _now(),
        })
        self._save()

    def record_finding(self, finding: dict[str, Any]) -> None:
        self._data.setdefault("findings", []).append(finding)
        self._save()

    def stop(self) -> None:
        self._data["status"] = "stopped"
        self._data["stopped_at"] = _now()
        self._save()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2))


class SessionManager:
    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir

    def start(self, name: Optional[str] = None) -> Session:
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        sid = _new_id("sess")
        data: dict[str, Any] = {
            "id": sid,
            "name": name or sid,
            "status": "active",
            "started_at": _now(),
            "commands": [],
            "findings": [],
            "artifacts": [],
        }
        path = self.sessions_dir / f"{sid}.json"
        session = Session(data, path)
        session._save()
        # Write "current" pointer
        (self.sessions_dir / "current").write_text(sid)
        return session

    def stop(self, session_id: Optional[str] = None) -> Optional[Session]:
        sid = session_id or self._current_id()
        if not sid:
            return None
        session = self.load(sid)
        if session:
            session.stop()
            current_file = self.sessions_dir / "current"
            if current_file.exists() and current_file.read_text().strip() == sid:
                current_file.unlink()
        return session

    def current(self) -> Optional[Session]:
        sid = self._current_id()
        if sid:
            return self.load(sid)
        return None

    def load(self, session_id: str) -> Optional[Session]:
        path = self.sessions_dir / f"{session_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return Session(data, path)

    def list_sessions(self) -> list[dict[str, Any]]:
        if not self.sessions_dir.exists():
            return []
        sessions = []
        for f in sorted(self.sessions_dir.glob("sess_*.json"), reverse=True):
            try:
                data = json.loads(f.read_text())
                sessions.append({
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "status": data.get("status"),
                    "started_at": data.get("started_at"),
                    "stopped_at": data.get("stopped_at"),
                    "commands": len(data.get("commands", [])),
                    "findings": len(data.get("findings", [])),
                })
            except Exception:
                pass
        return sessions

    def _current_id(self) -> Optional[str]:
        current_file = self.sessions_dir / "current"
        if current_file.exists():
            return current_file.read_text().strip() or None
        return None


def new_run_id() -> str:
    return _new_id("run")
