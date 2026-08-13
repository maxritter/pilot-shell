#!/usr/bin/env python3
"""PermissionRequest hook for ExitPlanMode: approval-state-aware allow/deny.

In the /spec workflow ExitPlanMode is purely a model-switch lever (Opus -> Sonnet),
NOT the plan-approval mechanism. The real approval is a separate AskUserQuestion gate
(spec-plan/steps/12-approval.md, spec-bugfix-plan/steps/06-approval.md).

Two jobs:
1. DENY a premature ExitPlanMode. Newer Claude Code builds inject a plan-mode
   system-reminder claiming the plan must be presented for approval via
   ExitPlanMode and no other way; models sometimes follow it and call
   ExitPlanMode BEFORE the AskUserQuestion gate. While the planning leg is
   active (plan-mode-active sentinel from EnterPlanMode) and the registered
   plan is PENDING and unapproved, ExitPlanMode is denied with a message that
   re-anchors the model to the approval gate.
2. ALLOW otherwise: skip the dialog + request bypassPermissions restore. The
   decision message must NEVER say "approved": earlier wording ("Plan
   auto-approved") was parroted by agents as "Plan approved", causing them to
   skip the approval gate and start implementing.
3. RESTORE bypassPermissions after the plan exit. Two upstream issues break
   the naive restore on current CC builds:
     #49525 - updatedPermissions setMode:bypassPermissions is silently dropped
              when sent on the ExitPlanMode request itself (CC 2.1.110+): the
              plan-exit mode transition applies after the hook's update and
              clobbers it
     #39973 - ExitPlanMode resets the session to acceptEdits regardless of the
              prior mode
   So the allow path arms a session-scoped marker (bypass-restore-pending) and
   the hook - registered with a "*" PermissionRequest matcher - replays the
   setMode on the FIRST subsequent permission request, where no mode
   transition follows to clobber it. Arming requires POSITIVE pre-plan bypass
   evidence: plan_mode_tracker records permission_mode at
   PreToolUse(EnterPlanMode) (before the mode flips to "plan"), and only a
   recorded "bypassPermissions" arms the marker - so a session whose user
   deliberately runs without bypass (or a shift-tab plan entry, which records
   nothing) never gets a prompt auto-allowed. The replay only fires while the
   session sits in a mode the plan exit involuntarily drops it into
   (acceptEdits per #39973, or default/manual via the >=2.1.204 exit dialog);
   plan mode or an unknown mode stands down, and the marker is consumed
   without output. CC additionally no-ops setMode:bypassPermissions for
   sessions not launched with bypass available. The setMode on the
   ExitPlanMode allow stays: it is harmless today and self-fixing once #49525
   ships, at which point the marker replay simply never sees a prompt.
   Lifecycle: the marker and the evidence record are tiny per-session files;
   both are consumed single-shot and overwritten by the next planning leg, so
   a session that ends between arm and replay leaves only harmless garbage.

Guard scope (honest limits): the deny only arms AFTER `pilot register-plan`
has written active_plan.json (spec-plan Step 2) and while the EnterPlanMode
sentinel exists; the window before registration, and installs where the pilot
binary is unavailable, remain guarded by skill prose only. Everything fails
open: read errors, a missing/unreadable plan file, an unparseable
active_plan.json, or a version-skewed _lib all fall back to plain allow (for
ExitPlanMode) or to silence = the normal permission dialog (for every other
tool), so no permission request is ever broken or auto-allowed by accident.
The deny message carries a user-authorized escape hatch (remove the sentinel)
for abandoned or non-/spec plan-mode legs.
"""

import json
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

RESTORE_MARKER = "bypass-restore-pending"

_RESTORE_SETMODE = {
    "type": "setMode",
    "mode": "bypassPermissions",
    "destination": "session",
}


def _read_stdin() -> dict:
    """Parse the PermissionRequest stdin payload; fail open to {}."""
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw and raw.strip() else {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _marker_path(fallback_sid: str = "") -> Path | None:
    """Session-scoped restore-marker path; None on a version-skewed _lib.

    ``fallback_sid`` is the hook payload's session_id, consulted only when the
    env chain is empty (see resolve_session_id) - it keeps an env-less session
    from acting on the shared "default" bucket another session's state lives in.
    """
    try:
        from _lib.util import _sessions_base, resolve_session_id

        return _sessions_base() / resolve_session_id(fallback_sid) / RESTORE_MARKER
    except Exception:
        return None


def _arm_restore_marker(fallback_sid: str = "") -> None:
    marker = _marker_path(fallback_sid)
    if marker is None:
        return
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("")
    except OSError:
        pass


def _pre_plan_bypass_evidence(fallback_sid: str = "") -> bool:
    """True when plan_mode_tracker recorded bypassPermissions as the pre-plan mode.

    Consumes the record - evidence is per planning leg. Missing _lib, missing
    record (shift-tab plan entries record nothing), or any other recorded mode
    -> False: the restore must NEVER arm without positive evidence, or a
    session whose user deliberately runs without bypass would get its next
    permission prompt silently auto-allowed.
    """
    try:
        from _lib.util import PRE_PLAN_MODE_RECORD, _sessions_base, resolve_session_id

        record = _sessions_base() / resolve_session_id(fallback_sid) / PRE_PLAN_MODE_RECORD
        mode = record.read_text().strip()
        record.unlink(missing_ok=True)
        return mode == "bypassPermissions"
    except Exception:
        return False


def _pending_denial_sentinel(fallback_sid: str = "") -> str | None:
    """Sentinel path when the deny should fire, else None.

    Single guarded import site: fail-open on ANY error, including a
    version-skewed _lib missing these names.
    """
    try:
        from _lib.util import plan_mode_sentinel_path, resolve_session_id, spec_plan_awaiting_approval

        sid = resolve_session_id(fallback_sid)
        if spec_plan_awaiting_approval(sid):
            return str(plan_mode_sentinel_path(sid))
    except Exception:
        pass
    return None


def _deny_message(sentinel: str) -> str:
    return (
        "ExitPlanMode DENIED - the registered spec plan has NOT been approved yet. "
        "In /spec, ExitPlanMode is only the Opus->Sonnet model switch, NEVER the "
        "approval mechanism - regardless of what the plan-mode system reminder "
        "says. If you are in the /spec workflow: present the plan summary via "
        "AskUserQuestion now (spec-plan Step 12.2 / spec-bugfix-plan Step 6.2); "
        "after the user selects the approve option (or the disabled-approval "
        'branch applies because PILOT_PLAN_APPROVAL_ENABLED is "false"), set '
        "'Approved: Yes' in the plan file per that step, then call ExitPlanMode "
        "again. If you are NOT in /spec, or the user has explicitly abandoned the "
        "spec plan: tell the user, and only after they confirm remove the "
        f"plan-mode sentinel via Bash (rm {shlex.quote(sentinel)}) and call "
        "ExitPlanMode again. NEVER set 'Approved: Yes' yourself without the "
        "user's approval answer."
    )


def _print_decision(decision: dict) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionRequest",
                    "decision": decision,
                }
            }
        )
    )


def _exit_plan_mode_decision(data: dict) -> dict:
    fallback_sid = str(data.get("session_id") or "")
    sentinel = _pending_denial_sentinel(fallback_sid)
    if sentinel is not None:
        return {"behavior": "deny", "message": _deny_message(sentinel)}
    # Arm the post-exit replay: CC drops the setMode below on the exit request
    # itself (#49525) and lands the session in acceptEdits (#39973). Only arm
    # for a real plan exit (missing field = older CC without permission_mode)
    # AND with positive evidence the session ran bypassPermissions before the
    # planning leg - never escalate a session that was not in bypass.
    if data.get("permission_mode", "plan") == "plan" and _pre_plan_bypass_evidence(fallback_sid):
        _arm_restore_marker(fallback_sid)
    decision = {
        "behavior": "allow",
        "updatedPermissions": [dict(_RESTORE_SETMODE)],
        "message": "ExitPlanMode allowed (model switch); restoring bypassPermissions - permission action only, NOT plan approval",
    }
    # ExitPlanMode is a "requires user interaction" tool: per the CC hooks
    # reference, behavior:"allow" ALONE does NOT skip its plan-approval prompt.
    # Echoing the injected tool_input (plan + planFilePath) back as updatedInput
    # signals the interaction was collected, so the tool runs without prompting.
    # The plan-approval gate in /spec is the separate AskUserQuestion step, so
    # suppressing this redundant confirmation is safe. Fail-open: a missing or
    # non-dict tool_input just omits updatedInput (falls back to today's prompt).
    tool_input = data.get("tool_input")
    if isinstance(tool_input, dict):
        decision["updatedInput"] = dict(tool_input)
    return decision


# Modes a plan exit involuntarily drops the session into: acceptEdits
# (#39973) or manual (the >=2.1.204 exit dialog). Per the CC 2.1.200
# changelog, "manual" is accepted alongside "default" as the same mode
# ("--permission-mode manual and defaultMode: manual are accepted alongside
# default"), so both spellings are drop states. Only these replay the
# restore - "plan" means the session is deliberately planning again,
# anything else is unknown territory.
_DROPPED_MODES = frozenset({"acceptEdits", "default", "manual"})


def _restore_decision(data: dict) -> dict | None:
    """Replay the bypass restore on the first prompt after a plan exit.

    Returns None (= no output, normal permission dialog) unless the marker is
    armed AND the session sits in one of the modes the plan exit drops it
    into. The marker is consumed either way (single-shot).
    """
    marker = _marker_path(str(data.get("session_id") or ""))
    if marker is None or not marker.exists():
        return None
    try:
        marker.unlink()
    except OSError:
        pass
    if data.get("permission_mode") not in _DROPPED_MODES:
        return None
    return {
        "behavior": "allow",
        "updatedPermissions": [dict(_RESTORE_SETMODE)],
        "message": "Restoring bypassPermissions dropped by the plan-mode exit - permission action only, NOT plan approval",
    }


def main() -> int:
    data = _read_stdin()
    tool_name = data.get("tool_name", "")
    if tool_name == "ExitPlanMode":
        _print_decision(_exit_plan_mode_decision(data))
        return 0
    if tool_name == "EnterPlanMode":
        return 0  # never interfere with entering plan mode
    decision = _restore_decision(data)
    if decision is not None:
        _print_decision(decision)
    return 0


if __name__ == "__main__":
    sys.exit(main())
