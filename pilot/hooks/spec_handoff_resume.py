#!/usr/bin/env python3
"""UserPromptSubmit hook — auto-resume /spec implementation after model swap.

When `spec-plan` / `spec-bugfix-plan` end their turn after plan approval with
the Model Switching toggle ON, they write `~/.pilot/sessions/<sid>/spec-handoff-pending`.
`spec_stop_guard` allows the stop but leaves the sentinel intact so this hook can
consume it on the user's next prompt — whatever it is. The hook reads the active
plan path from `active_plan.json`, injects a system reminder instructing the agent
to invoke `Skill('spec-implement', '<plan-path>')` immediately, and deletes the
sentinel. This removes the need for `/clear` and `/spec <plan-path>` in the
model-switch resume flow.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import _sessions_base, get_session_plan_path

HANDOFF_SENTINEL_MAX_AGE_SECONDS = 3600


def get_handoff_sentinel_path() -> Path:
    session_id = os.environ.get("PILOT_SESSION_ID", "").strip() or "default"
    return _sessions_base() / session_id / "spec-handoff-pending"


def _resolve_plan_path() -> str | None:
    plan_json = get_session_plan_path()
    if not plan_json.exists():
        return None
    try:
        data = json.loads(plan_json.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    plan_path = data.get("plan_path")
    if not isinstance(plan_path, str) or not plan_path:
        return None
    p = Path(plan_path)
    if not p.is_absolute():
        project_root = os.environ.get("CLAUDE_PROJECT_ROOT", str(Path.cwd()))
        p = Path(project_root) / p
    return str(p) if p.exists() else None


def main() -> int:
    sentinel = get_handoff_sentinel_path()
    if not sentinel.exists():
        return 0

    try:
        age = time.time() - sentinel.stat().st_mtime
    except OSError:
        age = 0.0

    sentinel.unlink(missing_ok=True)

    if age > HANDOFF_SENTINEL_MAX_AGE_SECONDS:
        return 0

    plan_path = _resolve_plan_path()
    if not plan_path:
        return 0

    additional_context = (
        f"[Pilot model-switch resume] The plan at `{plan_path}` is approved and "
        f"awaiting implementation. The user may have switched models via `/model` "
        f"before sending this prompt. Your VERY NEXT action MUST be "
        f"`Skill(skill='spec-implement', args='{plan_path}')` — do not chat, "
        f"summarise, or re-interpret the user's prompt. Invoke the skill "
        f"immediately to resume the /spec workflow."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": additional_context,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
