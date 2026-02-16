"""SessionStart(compact) hook - restore Pilot context after compaction.

Fires after Claude Code compaction completes to re-inject Pilot-specific context
(active plan, task state) that may have been compressed during compaction.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _util import (
    get_session_plan_path,
    read_hook_stdin,
)


def _sessions_base() -> Path:
    """Get base sessions directory."""
    return Path.home() / ".pilot" / "sessions"


def _read_active_plan() -> dict | None:
    """Read active plan state from session data."""
    plan_path = get_session_plan_path()
    if not plan_path.exists():
        return None

    try:
        return json.loads(plan_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _read_fallback_state(session_id: str) -> dict | None:
    """Read pre-compact fallback state if available."""
    fallback_file = _sessions_base() / session_id / "pre-compact-state.json"
    if not fallback_file.exists():
        return None

    try:
        state = json.loads(fallback_file.read_text())
        fallback_file.unlink()
        return state
    except (json.JSONDecodeError, OSError):
        return None


def _format_context_message(plan_data: dict | None, fallback_state: dict | None) -> str:
    """Format structured context restoration message."""
    lines = ["[Pilot Context Restored After Compaction]"]

    if plan_data:
        plan_path = plan_data.get("plan_path", "Unknown")
        status = plan_data.get("status", "Unknown")
        current_task = plan_data.get("current_task")

        if current_task:
            lines.append(f"Active Plan: {plan_path} (Status: {status}, Task {current_task} in progress)")
        else:
            lines.append(f"Active Plan: {plan_path} (Status: {status})")

    elif fallback_state and fallback_state.get("active_plan"):
        plan = fallback_state["active_plan"]
        plan_path = plan.get("plan_path", "Unknown")
        status = plan.get("status", "Unknown")
        lines.append(f"Active Plan: {plan_path} (Status: {status}) [from pre-compact state]")

    else:
        lines.append("No active plan")

    if fallback_state and fallback_state.get("task_list"):
        task_count = fallback_state["task_list"].get("task_count")
        if task_count:
            lines.append(f"Tasks: {task_count} active")

    return "\n".join(lines)


def run_post_compact_restore() -> int:
    """Run SessionStart(compact) hook to restore context after compaction.

    Returns exit code: 0 (output to stdout visible in context).
    """
    hook_data = read_hook_stdin()
    session_id = hook_data.get("session_id", os.environ.get("PILOT_SESSION_ID", "default"))

    plan_data = _read_active_plan()

    fallback_state = _read_fallback_state(session_id)

    message = _format_context_message(plan_data, fallback_state)
    print(message)

    return 0


if __name__ == "__main__":
    sys.exit(run_post_compact_restore())
