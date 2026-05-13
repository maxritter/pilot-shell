#!/usr/bin/env python3
"""Stop guard for /spec workflow - prevents early finishing when plan is active.

Only allows stopping when:
1. Asking user for plan approval (AskUserQuestion tool)
2. Asking user for an important decision (AskUserQuestion tool)
3. No active plan exists (not in /spec mode)
4. User stops again within 60s cooldown (escape hatch)
5. Runaway cap: after MAX_BLOCKS consecutive blocks for the same plan with no
   user-question turn in between, emit one escalation block instructing the
   agent to AskUserQuestion. The next block-attempt after escalation is
   allowed through, breaking pathological infinite verify→implement loops.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import (
    _sessions_base,
    build_objective_reinjection,
    get_session_plan_path,
    is_waiting_for_user_input,
    stop_block,
)

COOLDOWN_SECONDS = 60
MAX_BLOCKS = 30


def get_stop_guard_path() -> Path:
    """Get session-scoped stop guard state path."""
    session_id = os.environ.get("PILOT_SESSION_ID", "").strip() or "default"
    guard_dir = _sessions_base() / session_id
    guard_dir.mkdir(parents=True, exist_ok=True)
    return guard_dir / "spec-stop-guard"


def find_active_plan() -> tuple[Path | None, str | None]:
    """Find the active plan for THIS session via session-scoped active_plan.json."""
    plan_json = get_session_plan_path()
    if not plan_json.exists():
        return None, None

    try:
        data = json.loads(plan_json.read_text())
        plan_path_str = data.get("plan_path", "")
    except (json.JSONDecodeError, OSError):
        return None, None

    if not plan_path_str:
        return None, None

    plan_file = Path(plan_path_str)
    if not plan_file.is_absolute():
        project_root = os.environ.get("CLAUDE_PROJECT_ROOT", str(Path.cwd()))
        plan_file = Path(project_root) / plan_file
    if not plan_file.exists():
        return None, None

    try:
        content = plan_file.read_text()
        status_match = re.search(r"^Status:\s*(\w+)", content, re.MULTILINE)
        if not status_match:
            return None, None
        status = status_match.group(1).upper()
        if status not in ("PENDING", "COMPLETE"):
            return None, None
        return plan_file, status
    except OSError:
        return None, None


def _load_state(state_file: Path) -> dict:
    """Load stop-guard state. Returns {} on any error or missing file.

    Tolerates the legacy plain-float format from earlier versions.
    """
    if not state_file.exists():
        return {}
    try:
        raw = state_file.read_text().strip()
    except OSError:
        return {}
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        return {"ts": float(raw), "count": 1, "plan": ""}
    except ValueError:
        return {}


def _save_state(state_file: Path, state: dict) -> None:
    try:
        state_file.write_text(json.dumps(state))
    except OSError:
        pass


def main() -> int:
    """Check if stopping is allowed based on /spec workflow state."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if input_data.get("stop_hook_active", False):
        return 0

    plan_path, status = find_active_plan()
    if plan_path is None or status is None:
        return 0

    state_file = get_stop_guard_path()
    state = _load_state(state_file)

    plan_key = str(plan_path)
    if state.get("plan") != plan_key:
        state = {"ts": 0.0, "count": 0, "plan": plan_key}

    transcript_path = input_data.get("transcript_path", "")
    if transcript_path and is_waiting_for_user_input(transcript_path):
        state["count"] = 0
        state["ts"] = 0.0
        _save_state(state_file, state)
        return 0

    now = time.time()
    last_ts = float(state.get("ts") or 0.0)
    if last_ts and (now - last_ts) < COOLDOWN_SECONDS:
        state_file.unlink(missing_ok=True)
        return 0

    count = int(state.get("count") or 0)

    if count > MAX_BLOCKS:
        state_file.unlink(missing_ok=True)
        return 0

    state["count"] = count + 1
    state["ts"] = now
    _save_state(state_file, state)

    if count + 1 > MAX_BLOCKS:
        reason = (
            f"RUNAWAY GUARD TRIPPED — {MAX_BLOCKS} consecutive stop-block attempts on plan "
            f"{plan_path} (Status: {status}) without a user-question turn in between. "
            f"This pattern indicates the agent is stuck in a verify→implement loop and "
            f"burning tokens unsupervised. STOP. Your VERY NEXT action MUST be "
            f"AskUserQuestion summarising what you were doing, what's blocking, and asking "
            f"the user how to proceed (Continue / Pivot / Abandon). Do NOT continue working. "
            f"Do NOT make further tool calls before asking. The next stop attempt after this "
            f"one will be allowed through to end the runaway."
        )
        print(stop_block(reason))
        return 0

    objective_block = build_objective_reinjection(plan_path)
    base_reason = (
        f"/spec workflow active — cannot stop without user interaction. "
        f"Active plan: {plan_path} (Status: {status}). "
        f"Stop again within 60s to force exit.\n\n"
        f"CRITICAL INSTRUCTION TO CLAUDE: Do NOT acknowledge this stop attempt. "
        f"Do NOT output resume instructions or say goodbye. "
        f"IMMEDIATELY continue working on the next pending task in the plan. "
        f"Your VERY NEXT action must be a tool call — read the plan file, "
        f"check TaskList, or make a code change. Do NOT produce a text-only response."
    )
    reason = f"{objective_block}{base_reason}" if objective_block else base_reason
    print(stop_block(reason))
    return 0


if __name__ == "__main__":
    sys.exit(main())
