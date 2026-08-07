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
    _read_plan_approved_and_type,
    _sessions_base,
    build_objective_reinjection,
    get_session_plan_path,
    is_waiting_for_user_input,
    plan_in_current_project,
    resolve_session_id,
    stop_block,
)

COOLDOWN_SECONDS = 60
MAX_BLOCKS = 30
# Sentinel files older than this are treated as stale (PID reuse, crashed
# session, etc.) and unlinked without being honored. One hour is generous
# enough for any realistic approval-wait interaction.
SENTINEL_MAX_AGE_SECONDS = 3600


def get_stop_guard_path() -> Path:
    """Get session-scoped stop guard state path."""
    guard_dir = _sessions_base() / resolve_session_id()
    guard_dir.mkdir(parents=True, exist_ok=True)
    return guard_dir / "spec-stop-guard"


def get_approval_sentinel_path() -> Path:
    """Session-scoped path to the plan-approval-pending sentinel.

    Codex converts AskUserQuestion to a plain-text numbered prompt, so
    `is_waiting_for_user_input` (AskUserQuestion-only) never recognizes its
    approval-wait turn. Without a signal the stop guard would block the
    approval-wait stop and inject "IMMEDIATELY continue working", which a literal
    agent obeyed by editing `Approved: No -> Yes` itself and bypassing the user.

    The Codex approval step writes this sentinel before ending its turn; the stop
    guard honors it ONLY while the plan is still unapproved (Approved: No), so the
    implement-phase block (Approved: Yes) is preserved. Stale sentinels (older than
    SENTINEL_MAX_AGE_SECONDS — e.g. PID reuse / crashed session) are
    discarded, not honored.
    """
    guard_dir = _sessions_base() / resolve_session_id()
    guard_dir.mkdir(parents=True, exist_ok=True)
    return guard_dir / "spec-approval-pending"


def get_manual_switch_sentinel_path() -> Path:
    """Session-scoped path to the manual-switch-pending sentinel.

    Manual Model Switching pauses ONCE after plan approval so the user can run
    ``/model`` for the implementation leg. That pause cannot be an
    AskUserQuestion -- slash commands cannot be typed while a question prompt is
    open -- so the skill prints a normal finish message, touches this sentinel,
    and ends its turn. The stop guard honors the sentinel ONE time (deleting it
    on honor) and only for an APPROVED plan, so the pre-approval flow and the
    implement-phase block are both preserved. Stale sentinels are discarded.
    """
    guard_dir = _sessions_base() / resolve_session_id()
    guard_dir.mkdir(parents=True, exist_ok=True)
    return guard_dir / "manual-switch-pending"


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

    # Cross-session bleed guard: ignore an active plan that isn't part of this
    # project (e.g. a COMPLETE plan from another repo's /spec session leaking in
    # through the shared "default" active_plan.json when PILOT_SESSION_ID unset).
    if not plan_in_current_project(plan_file):
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


def _next_action_for(status: str, plan_type: str = "Feature") -> str:
    """Return the outstanding-step instruction for a plan in ``status``.

    The instruction must name the step that is ACTUALLY outstanding. A COMPLETE
    plan has every task checked off, so the generic "next pending task" wording
    reads as "nothing left to do" and the agent stops -- skipping verification
    entirely, which is the one step COMPLETE exists to gate.

    ``/build`` rubrics (``Type: Build``) have no tasks and no verify skill to
    dispatch -- their outstanding step is the next loop round or the final blind
    judge pass, so they get their own wording rather than spec's.
    """
    if plan_type == "Build":
        if status == "COMPLETE":
            return (
                "Every criterion is ticked but the FINAL blind judge pass has not run. "
                "IMMEDIATELY re-obtain the bar using the rubric's re-obtain command, then rule "
                "every criterion again from the finished artifact alone. Do NOT set "
                "Status: VERIFIED without that pass, and do NOT summarise the work instead of "
                "judging it."
            )
        return (
            "The build loop is active. Your VERY NEXT action must be a tool call - re-read the "
            "rubric's Criteria and Round Log, close the single gap named there, then judge every "
            "criterion against the re-obtained bar. Do NOT stop while any criterion is unticked, "
            "do NOT tick one without evidence you can point at, and do NOT lower a criterion "
            "silently."
        )
    if status == "COMPLETE":
        return (
            "Implementation is done and verification has NOT run yet. "
            "IMMEDIATELY dispatch the verify phase: read the plan's `Type:` header, then invoke "
            "Skill(skill='spec-verify') for a feature plan or Skill(skill='spec-bugfix-verify') "
            "for a bugfix plan, passing the plan path. Do NOT re-implement, do NOT mark the plan "
            "VERIFIED yourself, and do NOT summarise the work instead of dispatching."
        )
    return (
        "IMMEDIATELY continue working on the next pending task in the plan. "
        "Your VERY NEXT action must be a tool call - read the plan file, "
        "check TaskList, or make a code change."
    )


def _block_reason(plan_path: Path, status: str) -> str:
    """Compose the stop-block message for an active plan or `/build` rubric."""
    _, plan_type = _read_plan_approved_and_type(str(plan_path))
    is_build = plan_type == "Build"
    workflow = "/build loop" if is_build else "/spec workflow"
    artifact = "Active rubric" if is_build else "Active plan"
    base_reason = (
        f"{workflow} active — cannot stop without user interaction. "
        f"{artifact}: {plan_path} (Status: {status}). "
        f"Stop again within 60s to force exit.\n\n"
        f"CRITICAL INSTRUCTION TO CLAUDE: Do NOT acknowledge this stop attempt. "
        f"Do NOT output resume instructions or say goodbye. "
        f"{_next_action_for(status, plan_type)} Do NOT produce a text-only response."
    )
    objective_block = build_objective_reinjection(plan_path)
    return f"{objective_block}{base_reason}" if objective_block else base_reason


def main() -> int:
    """Check if stopping is allowed based on /spec or /build workflow state."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if input_data.get("stop_hook_active", False):
        return 0

    plan_path, status = find_active_plan()
    if plan_path is None or status is None:
        return 0

    # Approval-wait pause for agents that cannot emit AskUserQuestion (Codex):
    # while the plan is still unapproved, a fresh approval-pending sentinel grants
    # permission to stop so the user can actually answer the approval question.
    # Honored ONLY for unapproved plans — once Approved: Yes flips, the
    # implement-phase block re-engages. Stale sentinels are discarded, not honored.
    approval_sentinel = get_approval_sentinel_path()
    if approval_sentinel.exists():
        try:
            age = time.time() - approval_sentinel.stat().st_mtime
        except OSError:
            age = 0.0
        if age > SENTINEL_MAX_AGE_SECONDS:
            approval_sentinel.unlink(missing_ok=True)
        else:
            approved, _ = _read_plan_approved_and_type(str(plan_path))
            if not approved:
                return 0

    # Manual-mode post-approval pause: the skill ends its turn so the user can
    # run /model (impossible inside an AskUserQuestion prompt). Honored ONE time
    # -- the sentinel is consumed on honor -- and only for an APPROVED plan, so
    # the implement-phase block re-engages on the very next stop attempt.
    manual_sentinel = get_manual_switch_sentinel_path()
    if manual_sentinel.exists():
        try:
            age = time.time() - manual_sentinel.stat().st_mtime
        except OSError:
            age = 0.0
        if age > SENTINEL_MAX_AGE_SECONDS:
            manual_sentinel.unlink(missing_ok=True)
        else:
            approved, _ = _read_plan_approved_and_type(str(plan_path))
            if approved:
                manual_sentinel.unlink(missing_ok=True)
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

    print(stop_block(_block_reason(plan_path, status)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
