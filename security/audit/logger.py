"""Audit logger — structured, append-only event log for every governed action.

Every command that passes through the security control plane becomes a
structured JSON event written to:
  ~/.pilot/security/audit.jsonl   (primary, append-only)

Each event is a newline-delimited JSON object (NDJSON) so the log is
streamable, grep-friendly, and importable into any SIEM.

Schema (all fields present, nullable fields marked with ?):
{
  "ts":         "ISO-8601 UTC timestamp",
  "session_id": "PILOT_SESSION_ID env var or null",
  "event_type": "command_evaluated | secret_found | policy_blocked | scan_result | session_start | session_end",
  "command":    "raw command string or null",
  "risk": {
    "level":    "INFO|LOW|MEDIUM|HIGH|CRITICAL",
    "level_int": 0-4,
    "reason":   "...",
    "tags":     ["..."]
  },
  "policy": {
    "action":   "allow|warn|block|require",
    "matched_rules": ["..."],
    "warnings": ["..."],
    "block_reason": "...|null"
  },
  "secrets": [
    {"pattern_name": "...", "severity": "HIGH|MEDIUM|LOW", "line_number": N, "redacted": "..."}
  ],
  "metadata": {}   // arbitrary extension dict
}
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LOG_DIR = Path.home() / ".pilot" / "security"
_LOG_FILE = _LOG_DIR / "audit.jsonl"

_lock = threading.Lock()


def _get_log_path() -> Path:
    """Allow override via PILOT_SEC_AUDIT_LOG env var."""
    override = os.environ.get("PILOT_SEC_AUDIT_LOG", "").strip()
    return Path(override) if override else _LOG_FILE


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_id() -> str | None:
    return os.environ.get("PILOT_SESSION_ID") or None


def _ensure_log_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_event(event: dict[str, Any]) -> None:
    """Thread-safe append of a single JSON event to the audit log."""
    log_path = _get_log_path()
    _ensure_log_dir(log_path)
    line = json.dumps(event, default=str, separators=(",", ":"))
    with _lock:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_command_evaluated(
    command: str,
    risk: dict[str, Any],
    policy: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log a command that was evaluated by the risk + policy pipeline."""
    _write_event(
        {
            "ts": _now_iso(),
            "session_id": _session_id(),
            "event_type": "command_evaluated",
            "command": command,
            "risk": risk,
            "policy": policy,
            "secrets": [],
            "metadata": metadata or {},
        }
    )


def log_secret_found(
    source: str,
    findings: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log secret detection findings from a file or text scan."""
    _write_event(
        {
            "ts": _now_iso(),
            "session_id": _session_id(),
            "event_type": "secret_found",
            "command": None,
            "risk": None,
            "policy": None,
            "secrets": findings,
            "metadata": {"source": source, **(metadata or {})},
        }
    )


def log_policy_blocked(
    command: str,
    risk: dict[str, Any],
    policy: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log a command that was explicitly blocked by policy."""
    _write_event(
        {
            "ts": _now_iso(),
            "session_id": _session_id(),
            "event_type": "policy_blocked",
            "command": command,
            "risk": risk,
            "policy": policy,
            "secrets": [],
            "metadata": metadata or {},
        }
    )


def log_scan_result(
    scan_type: str,
    target: str,
    findings: list[dict[str, Any]],
    tool: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log output from an external scanner (SAST, deps, container, IaC)."""
    _write_event(
        {
            "ts": _now_iso(),
            "session_id": _session_id(),
            "event_type": "scan_result",
            "command": None,
            "risk": None,
            "policy": None,
            "secrets": [],
            "metadata": {
                "scan_type": scan_type,
                "target": target,
                "tool": tool,
                "finding_count": len(findings),
                "findings": findings,
                **(metadata or {}),
            },
        }
    )


def log_session_event(
    event_type: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log session lifecycle events (start, end, compact, clear)."""
    _write_event(
        {
            "ts": _now_iso(),
            "session_id": _session_id(),
            "event_type": event_type,
            "command": None,
            "risk": None,
            "policy": None,
            "secrets": [],
            "metadata": metadata or {},
        }
    )


def tail_log(n: int = 20) -> list[dict[str, Any]]:
    """Return the last `n` audit events as parsed dicts."""
    log_path = _get_log_path()
    if not log_path.exists():
        return []
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
        recent = lines[-n:]
        return [json.loads(line) for line in recent if line.strip()]
    except (OSError, json.JSONDecodeError):
        return []


def get_log_path() -> Path:
    """Return the path to the active audit log."""
    return _get_log_path()
