#!/usr/bin/env python3
"""PermissionRequest hook for ExitPlanMode: approval-state-aware allow/deny.

⛔ SCOPE: this hook acts ONLY on a `/spec` planning leg. In that workflow
ExitPlanMode is purely a model-switch lever (Opus -> Sonnet), NOT the
plan-approval mechanism - the real approval is a separate AskUserQuestion gate
(spec-plan/steps/12-approval.md, spec-bugfix-plan/steps/06-approval.md), so the
redundant native plan dialog is suppressed there. Claude Code's OWN plan mode -
the user pressing shift-tab, or the model entering plan mode for ordinary work -
is a completely different thing: there ExitPlanMode *is* the approval, and the
dialog is the only place the user gets to read the plan and accept or reject it.
Suppressing it silently approved every native plan, which is why every allow
path below is gated on `spec_plan_leg_active`. Without a live Pilot run the hook
emits NOTHING for ExitPlanMode and Claude Code prompts exactly as it normally
would.

Three jobs:
1. DENY a premature ExitPlanMode. Newer Claude Code builds inject a plan-mode
   system-reminder claiming the plan must be presented for approval via
   ExitPlanMode and no other way; models sometimes follow it and call
   ExitPlanMode BEFORE the AskUserQuestion gate. While the planning leg is
   active (plan-mode-active sentinel from EnterPlanMode) and the registered
   plan is PENDING and unapproved, ExitPlanMode is denied with a message that
   re-anchors the model to the approval gate.
2. ALLOW an approved /spec plan exit: skip the (already-answered) dialog +
   request bypassPermissions restore. The decision message must NEVER say
   "approved": earlier wording ("Plan auto-approved") was parroted by agents as
   "Plan approved", causing them to skip the approval gate and start
   implementing.
3. RESTORE bypassPermissions after a /spec plan exit - and ONLY a /spec one.
   In native plan mode the exit dialog's "auto-accept edits" / "manually
   approve edits" choice IS the user selecting a permission mode, so replaying
   a restore over it would override a deliberate decision and auto-allow their
   next prompt; the marker is therefore never armed outside a /spec leg. Within
   /spec the same transition is an involuntary drop, from two upstream issues:
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

Ownership is decided at ENTRY, not at exit. `spec_plan_leg_active` reads the
record `plan_mode_tracker` writes at PreToolUse(EnterPlanMode), because at exit
a /spec plan (PENDING + Approved: Yes at Step 12.3) is indistinguishable from an
approved plan the model opened native plan mode on top of mid-implementation, or
from a /build Buildout, which sets Approved: Yes when its contract locks and
never enters plan mode at all. Gating on "a run is registered" alone therefore
handed native plan mode straight back to the /spec code path inside any live
run - the same silent-approval bug, in a narrower window.

Guard scope (honest limits): both the deny AND the allow additionally require
`pilot register-plan` to have written active_plan.json (spec-plan Step 2) while
the EnterPlanMode sentinel exists; the window before registration, and installs
where the pilot binary is unavailable, remain guarded by skill prose only. An
ExitPlanMode in that window falls through to the native dialog rather than being
suppressed - a visible extra confirmation inside `/spec` is the cost of never
silently approving a plan outside it. Everything fails toward the native dialog:
read errors, a missing/unreadable plan file, an unparseable active_plan.json, a
missing owner record (a shift-tab plan entry writes none), or a version-skewed
_lib all end in silence, so no permission request is ever broken or auto-allowed
by accident. The deny message carries a user-authorized escape hatch (remove the
sentinel) for abandoned or non-/spec plan-mode legs.
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


def _is_spec_plan_leg(fallback_sid: str = "") -> bool:
    """True when this ExitPlanMode belongs to a registered Pilot planning leg.

    The gate on every allow path. Fail-closed for THIS consumer (False on any
    error, including a version-skewed _lib predating the predicate): "not a
    Pilot leg" hands the decision back to Claude Code's own plan dialog, which
    is always safe. The opposite default is what silently approved native
    plans.
    """
    try:
        from _lib.util import resolve_session_id, spec_plan_leg_active

        return spec_plan_leg_active(resolve_session_id(fallback_sid))
    except Exception:
        return False


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


def _exit_plan_mode_decision(data: dict) -> dict | None:
    """Decision for an ExitPlanMode permission request, or None for "stay out".

    None means the hook prints nothing and Claude Code shows its normal plan
    dialog - the correct outcome for native plan mode, where that dialog IS the
    approval.
    """
    fallback_sid = str(data.get("session_id") or "")
    sentinel = _pending_denial_sentinel(fallback_sid)
    if sentinel is not None:
        return {"behavior": "deny", "message": _deny_message(sentinel)}
    if not _is_spec_plan_leg(fallback_sid):
        # Claude Code's own plan mode. Two things must NOT happen here.
        #
        # The plan itself: ExitPlanMode IS the approval, so the dialog must
        # reach the user. Allowing it - let alone echoing updatedInput, which
        # tells CC the required interaction was already collected - approves
        # the plan on their behalf.
        #
        # The permission mode: the exit dialog's "auto-accept edits" vs
        # "manually approve edits" is the user CHOOSING a mode, not Claude Code
        # dropping one. Arming the bypass restore here would auto-allow their
        # next permission request and force bypassPermissions over the choice
        # they just made - a worse outcome than the plan approval this hook was
        # fixing. So the marker stays unarmed and the evidence record is left
        # for the next planning leg, which overwrites it at EnterPlanMode.
        return None
    # Arm the post-exit replay: CC drops the setMode below on the exit request
    # itself (#49525) and lands the session in acceptEdits (#39973). Only arm
    # for a real plan exit (missing field = older CC without permission_mode)
    # AND with positive evidence the session ran bypassPermissions before the
    # planning leg - never escalate a session that was not in bypass. /spec legs
    # only: there the mode change is an involuntary drop, not a user choice.
    restore_bypass = data.get("permission_mode", "plan") == "plan" and _pre_plan_bypass_evidence(fallback_sid)
    if restore_bypass:
        _arm_restore_marker(fallback_sid)
    decision = {
        "behavior": "allow",
        "message": "ExitPlanMode allowed (model switch) - permission action only, NOT plan approval",
    }
    if restore_bypass:
        # Positive evidence only. Asking for bypass without it would escalate a
        # session the user deliberately kept in manual/acceptEdits if Claude
        # Code starts honoring setMode on ExitPlanMode in a future release.
        decision["updatedPermissions"] = [dict(_RESTORE_SETMODE)]
        decision["message"] = (
            "ExitPlanMode allowed (model switch); restoring bypassPermissions - "
            "permission action only, NOT plan approval"
        )
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
        exit_decision = _exit_plan_mode_decision(data)
        if exit_decision is not None:
            _print_decision(exit_decision)
        return 0
    if tool_name == "EnterPlanMode":
        return 0  # never interfere with entering plan mode
    decision = _restore_decision(data)
    if decision is not None:
        _print_decision(decision)
    return 0


if __name__ == "__main__":
    sys.exit(main())
