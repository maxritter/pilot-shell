"""PostToolUse hook — audit logger for all tool executions.

Every tool use becomes a structured event in the security audit trail:
  ~/.pilot/security/audit.jsonl

This is the "Audit Plane" — everything becomes a replayable, traceable record.
Runs as async=true so it never adds latency to the execution path.

Events captured:
  - Bash commands (with risk metadata from env, if pre-hook ran)
  - File writes (Write, Edit, MultiEdit)
  - Web access (WebFetch — if not blocked by tool_redirect)
  - Agent spawns
  - All other tool types get a minimal record
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from security.audit.logger import _write_event

_TOOL_CATEGORIES = {
    "Bash": "exec",
    "Write": "file_write",
    "Edit": "file_write",
    "MultiEdit": "file_write",
    "Read": "file_read",
    "Glob": "file_read",
    "Grep": "file_read",
    "WebFetch": "network",
    "WebSearch": "network",
    "Agent": "agent_spawn",
    "TodoWrite": "state_mutation",
    "AskUserQuestion": "user_interaction",
}


def _extract_summary(tool_name: str, tool_input: dict) -> str:
    """Extract a one-line summary of what the tool did."""
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        return cmd[:120]
    if tool_name in ("Write", "Edit", "MultiEdit"):
        return tool_input.get("file_path", "")
    if tool_name in ("Read", "Glob", "Grep"):
        return tool_input.get("file_path") or tool_input.get("pattern") or ""
    if tool_name == "WebFetch":
        return tool_input.get("url", "")
    if tool_name == "Agent":
        return tool_input.get("description", "")[:80]
    return ""


def run() -> int:
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})
    tool_response = hook_data.get("tool_response", {})

    category = _TOOL_CATEGORIES.get(tool_name, "other")
    summary = _extract_summary(tool_name, tool_input)

    # Was the tool result an error?
    is_error = False
    if isinstance(tool_response, dict):
        is_error = tool_response.get("is_error", False)
    elif isinstance(tool_response, str):
        is_error = "error" in tool_response.lower()[:50]

    _write_event(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_id": os.environ.get("PILOT_SESSION_ID"),
            "event_type": "tool_use",
            "tool_name": tool_name,
            "tool_category": category,
            "summary": summary,
            "is_error": is_error,
            "command": summary if tool_name == "Bash" else None,
            "risk": None,
            "policy": None,
            "secrets": [],
            "metadata": {
                "async_write": True,
            },
        }
    )

    return 0


if __name__ == "__main__":
    sys.exit(run())
