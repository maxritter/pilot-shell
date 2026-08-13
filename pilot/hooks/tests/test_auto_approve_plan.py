"""Tests for auto_approve_plan hook - approval-state-aware ExitPlanMode gate."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parent.parent / "auto_approve_plan.py"
SESSION = "test-session"
RESTORE_MARKER = "bypass-restore-pending"


def _marker(tmp_path: Path) -> Path:
    return tmp_path / "home" / ".pilot" / "sessions" / SESSION / RESTORE_MARKER


def _arm_marker(tmp_path: Path) -> Path:
    marker = _marker(tmp_path)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("")
    return marker


def _record_pre_plan_mode(tmp_path: Path, mode: str) -> Path:
    record = tmp_path / "home" / ".pilot" / "sessions" / SESSION / "pre-plan-permission-mode"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(mode)
    return record


def _setup_spec_state(
    tmp_path: Path,
    *,
    approved: str = "No",
    status: str = "PENDING",
    sentinel: bool = True,
    plan_file: bool = True,
    plan_in_project: bool = True,
) -> Path:
    """Create the session + plan state the hook inspects. Returns the plan path."""
    session_dir = tmp_path / "home" / ".pilot" / "sessions" / SESSION
    session_dir.mkdir(parents=True, exist_ok=True)
    plan_parent = tmp_path / "project" if plan_in_project else tmp_path / "elsewhere"
    plans_dir = plan_parent / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    plan_path = plans_dir / "2026-07-02-test-feature.md"
    if plan_file:
        plan_path.write_text(f"# Test Feature\n\nStatus: {status}\nApproved: {approved}\nType: Feature\n")
    (session_dir / "active_plan.json").write_text(json.dumps({"plan_path": str(plan_path), "status": status}))
    if sentinel:
        (session_dir / "plan-mode-active").write_text("")
    return plan_path


def _run(
    tmp_path: Path,
    hook_path: Path = HOOK_PATH,
    project_root_env: bool = True,
    payload: dict | None = None,
    session_env: bool = True,
) -> tuple[int, dict | None]:
    """Run the hook hermetically (isolated HOME/session/project) and parse its output.

    payload is the PermissionRequest stdin JSON; the default simulates the
    classic ExitPlanMode request. Returns None for data when the hook printed
    nothing (passthrough to the normal permission dialog). session_env=False
    strips the whole session-id env chain, simulating a launch where neither
    the shell wrapper nor the agent exported a session id.
    """
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir(exist_ok=True)
    project.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["HOME"] = str(home)
    if session_env:
        env["PILOT_SESSION_ID"] = SESSION
    else:
        env.pop("PILOT_SESSION_ID", None)
    if project_root_env:
        env["CLAUDE_PROJECT_ROOT"] = str(project)
    else:
        env.pop("CLAUDE_PROJECT_ROOT", None)
    env.pop("CLAUDE_CODE_SESSION_ID", None)
    env.pop("CODEX_THREAD_ID", None)
    env.pop("PYTHONPATH", None)  # a leaked path to pilot/hooks would defeat the orphan-_lib isolation
    if payload is None:
        payload = {"tool_name": "ExitPlanMode", "permission_mode": "plan"}
    result = subprocess.run(
        [sys.executable, str(hook_path)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(project),
        input=json.dumps(payload),
    )
    stdout = result.stdout.strip()
    return result.returncode, json.loads(stdout) if stdout else None


def _decision(data: dict | None) -> dict:
    assert data is not None, "hook printed no decision"
    return data["hookSpecificOutput"]["decision"]


class TestAutoApprovePlan:
    def test_allows_without_spec_state(self, tmp_path):
        """No registered plan / no plan-mode sentinel -> plain allow (legacy behavior)."""
        code, data = _run(tmp_path)
        assert code == 0
        assert data is not None
        assert data["hookSpecificOutput"]["hookEventName"] == "PermissionRequest"
        decision = _decision(data)
        assert decision["behavior"] == "allow"
        perms = decision["updatedPermissions"]
        assert any(p.get("type") == "setMode" and p.get("mode") == "bypassPermissions" for p in perms)

    def test_allow_message_does_not_claim_plan_approval(self, tmp_path):
        """The allow message must NOT signal that the plan is approved.

        Regression guard: emitting "Plan auto-approved" made agents misread the
        auto-allowed ExitPlanMode (a model-switch/permission action) as the user
        approving the plan, so they skipped the real /spec approval gate
        (spec-plan/steps/12-approval.md). The message must perform the permission
        action while explicitly disclaiming plan approval.
        """
        _, data = _run(tmp_path)
        message = _decision(data)["message"].lower()
        assert "approved" not in message, f"misleading approval wording: {message!r}"
        assert "not plan approval" in message, f"missing disclaimer: {message!r}"

    def test_denies_while_plan_awaits_approval(self, tmp_path):
        """Premature ExitPlanMode during the /spec planning leg must be denied.

        Regression guard for the field report where the model followed the harness
        plan-mode reminder ("present the plan for approval via ExitPlanMode") and
        called ExitPlanMode BEFORE the AskUserQuestion approval gate. With an active
        plan-mode sentinel and a registered PENDING, unapproved plan, the hook must
        deny and re-anchor the model to the approval gate - including the escape
        hatch (sentinel path) for non-/spec or abandoned plan-mode legs.
        """
        _setup_spec_state(tmp_path, approved="No")
        code, data = _run(tmp_path)
        assert code == 0
        decision = _decision(data)
        assert decision["behavior"] == "deny"
        message = decision["message"]
        assert "askuserquestion" in message.lower()
        assert "plan-mode-active" in message  # escape hatch names the sentinel
        assert "updatedPermissions" not in decision  # allow-only field per hook schema
        assert not _marker(tmp_path).exists()  # a denied exit must not arm the restore

    def test_allows_after_plan_approved(self, tmp_path):
        _setup_spec_state(tmp_path, approved="Yes")
        _, data = _run(tmp_path)
        decision = _decision(data)
        assert decision["behavior"] == "allow"
        assert any(p.get("mode") == "bypassPermissions" for p in decision["updatedPermissions"])

    def test_allows_without_plan_mode_sentinel(self, tmp_path):
        """No EnterPlanMode sentinel = no plan-mode leg in flight -> never deny.

        A stale PENDING plan must not trap a user who entered plan mode manually
        (Shift+Tab does not call the EnterPlanMode tool, so no sentinel exists).
        """
        _setup_spec_state(tmp_path, approved="No", sentinel=False)
        _, data = _run(tmp_path)
        assert _decision(data)["behavior"] == "allow"

    def test_allows_when_plan_file_missing(self, tmp_path):
        """Registered plan path that no longer exists -> fail open (allow)."""
        _setup_spec_state(tmp_path, approved="No", plan_file=False)
        _, data = _run(tmp_path)
        assert _decision(data)["behavior"] == "allow"

    def test_allows_when_plan_file_undecodable(self, tmp_path):
        """Unreadable/undecodable plan file -> fail open (allow), never a deny trap.

        A deny here would be unrecoverable: 'set Approved: Yes' can never clear a
        decode error, so the session would be stuck in plan mode.
        """
        plan_path = _setup_spec_state(tmp_path, approved="No")
        plan_path.write_bytes(b"Status: PENDING\nApproved: No\n\xe9\xff")
        _, data = _run(tmp_path)
        assert _decision(data)["behavior"] == "allow"

    def test_allows_when_plan_outside_project(self, tmp_path):
        """Cross-session bleed guard: a plan from another repo never denies here."""
        _setup_spec_state(tmp_path, approved="No", plan_in_project=False)
        _, data = _run(tmp_path)
        assert _decision(data)["behavior"] == "allow"

    def test_allows_when_project_root_undetermined(self, tmp_path):
        """No CLAUDE_PROJECT_ROOT and a non-git cwd -> fail open (allow).

        plan_in_current_project returns True when the root cannot be
        determined; for the deny consumer that would be fail-closed, letting a
        stale plan deny ExitPlanMode in an unrelated non-git directory.
        """
        _setup_spec_state(tmp_path, approved="No")
        _, data = _run(tmp_path, project_root_env=False)
        assert _decision(data)["behavior"] == "allow"

    def test_sibling_default_bucket_state_does_not_deny_identified_session(self, tmp_path):
        """Same-repo sibling bleed: deny state another (env-less) session left in the
        shared 'default' bucket must not deny ExitPlanMode in a session whose hook
        payload carries its own session_id. The project guard passes here (same
        repo), so only session-scoped resolution prevents the cross-fire."""
        default_dir = tmp_path / "home" / ".pilot" / "sessions" / "default"
        default_dir.mkdir(parents=True)
        plans_dir = tmp_path / "project" / "docs" / "plans"
        plans_dir.mkdir(parents=True)
        plan_path = plans_dir / "2026-08-13-sibling-feature.md"
        plan_path.write_text("# Sibling\n\nStatus: PENDING\nApproved: No\nType: Feature\n")
        (default_dir / "active_plan.json").write_text(json.dumps({"plan_path": str(plan_path), "status": "PENDING"}))
        (default_dir / "plan-mode-active").write_text("")

        code, data = _run(
            tmp_path,
            payload={"tool_name": "ExitPlanMode", "permission_mode": "plan", "session_id": "session-b-uuid"},
            session_env=False,
        )
        assert code == 0
        assert _decision(data)["behavior"] == "allow", (
            "a sibling session's unapproved plan in the shared 'default' bucket must "
            "not deny this session's ExitPlanMode"
        )

    def test_sibling_default_bucket_restore_marker_not_consumed_by_identified_session(self, tmp_path):
        """Same-repo sibling bleed, restore branch: a bypass-restore marker another
        (env-less) session armed in the shared 'default' bucket must neither
        auto-allow this session's permission prompt nor be consumed by it -
        otherwise one session silently escalates another's permissions AND steals
        the owning session's pending restore."""
        default_dir = tmp_path / "home" / ".pilot" / "sessions" / "default"
        default_dir.mkdir(parents=True)
        marker = default_dir / RESTORE_MARKER
        marker.write_text("")

        code, data = _run(
            tmp_path,
            payload={"tool_name": "Bash", "permission_mode": "acceptEdits", "session_id": "session-b-uuid"},
            session_env=False,
        )
        assert code == 0
        assert data is None, "a sibling session's restore marker must not auto-allow this session's prompt"
        assert marker.exists(), "the owning session's pending restore marker must survive"

    def test_allows_when_lib_util_unavailable(self, tmp_path):
        """A version-skewed install (hook without _lib) degrades to plain allow.

        The hook must always print a decision and exit 0; an ImportError crash
        would drop Claude Code back to the interactive permission dialog.
        """
        orphan_hook = tmp_path / "orphan" / "auto_approve_plan.py"
        orphan_hook.parent.mkdir(parents=True)
        shutil.copy(HOOK_PATH, orphan_hook)
        _setup_spec_state(tmp_path, approved="No")  # deny state, but guard can't load
        code, data = _run(tmp_path, hook_path=orphan_hook)
        assert code == 0
        assert _decision(data)["behavior"] == "allow"
        # Restore branch under the same skew: never crash, never auto-allow -
        # a non-ExitPlanMode request degrades to the normal permission dialog.
        code, data = _run(
            tmp_path,
            hook_path=orphan_hook,
            payload={"tool_name": "Bash", "permission_mode": "acceptEdits"},
        )
        assert code == 0
        assert data is None

    def test_exit_allow_arms_restore_marker(self, tmp_path):
        """An allowed ExitPlanMode must arm the bypass-restore marker.

        Claude Code resets the session to acceptEdits on plan exit (upstream
        #39973) and silently drops the setMode sent on the exit request itself
        (#49525), so the restore must be replayed on the NEXT permission
        request. The marker is what arms that replay. Arming requires positive
        pre-plan bypass evidence (recorded by plan_mode_tracker at
        PreToolUse(EnterPlanMode)); the record is consumed per planning leg.
        """
        record = _record_pre_plan_mode(tmp_path, "bypassPermissions")
        code, data = _run(tmp_path, payload={"tool_name": "ExitPlanMode", "permission_mode": "plan"})
        assert code == 0
        assert _decision(data)["behavior"] == "allow"
        assert _marker(tmp_path).exists()
        assert not record.exists()  # evidence is per-leg, consumed on use

    def test_exit_allow_requires_bypass_evidence_to_arm(self, tmp_path):
        """No recorded pre-plan bypass mode -> allow, but NEVER arm the marker.

        Guards the permissions regression a reviewer flagged: without this
        gate, a session that was never in bypassPermissions (user deliberately
        in manual/acceptEdits, or a shift-tab plan entry that records nothing)
        would get its next permission prompt silently auto-allowed.
        """
        payload = {"tool_name": "ExitPlanMode", "permission_mode": "plan"}
        # (a) no evidence record at all
        code, data = _run(tmp_path, payload=payload)
        assert code == 0
        assert _decision(data)["behavior"] == "allow"
        assert not _marker(tmp_path).exists()
        # (b) evidence of a NON-bypass pre-plan mode
        _record_pre_plan_mode(tmp_path, "default")
        code, data = _run(tmp_path, payload=payload)
        assert code == 0
        assert _decision(data)["behavior"] == "allow"
        assert not _marker(tmp_path).exists()

    def test_enter_plan_mode_request_leaves_marker_untouched(self, tmp_path):
        """A PermissionRequest for EnterPlanMode is pure passthrough: no
        output, and an armed marker survives to fire on the next
        non-EnterPlanMode request."""
        marker = _arm_marker(tmp_path)
        code, data = _run(tmp_path, payload={"tool_name": "EnterPlanMode", "permission_mode": "acceptEdits"})
        assert code == 0
        assert data is None
        assert marker.exists()

    def test_restore_fires_on_first_prompt_after_plan_exit(self, tmp_path):
        """First permission request after a plan exit -> allow + setMode
        bypassPermissions, marker consumed (single-shot).

        The exit drops the session to acceptEdits (#39973) OR to manual
        (Claude Code >= 2.1.204's exit dialog, field report from the /spec
        smoke test) - the replay must cover every involuntary drop state,
        both 'default' and its 2.1.200+ alias 'manual'.
        """
        for dropped_mode in ("acceptEdits", "default", "manual"):
            marker = _arm_marker(tmp_path)
            code, data = _run(
                tmp_path,
                payload={
                    "tool_name": "Bash",
                    "permission_mode": dropped_mode,
                    "tool_input": {"command": "echo hi"},
                },
            )
            assert code == 0, dropped_mode
            decision = _decision(data)
            assert decision["behavior"] == "allow", dropped_mode
            assert any(
                p.get("type") == "setMode"
                and p.get("mode") == "bypassPermissions"
                and p.get("destination") == "session"
                for p in decision["updatedPermissions"]
            ), dropped_mode
            assert not marker.exists(), dropped_mode
            message = decision["message"].lower()
            assert "approved" not in message, f"misleading approval wording: {message!r}"
            assert "not plan approval" in message, f"missing disclaimer: {message!r}"

    def test_passthrough_for_other_tools_without_marker(self, tmp_path):
        """No armed marker -> a non-ExitPlanMode request produces NO output.

        Safety-critical with the '*' matcher: any output here would auto-allow
        arbitrary permission requests. Silence hands the request back to the
        normal Claude Code permission dialog.
        """
        code, data = _run(tmp_path, payload={"tool_name": "Bash", "permission_mode": "acceptEdits"})
        assert code == 0
        assert data is None

    def test_no_restore_in_plan_or_unknown_mode(self, tmp_path):
        """Marker armed but the session is back in plan mode (or the mode is
        missing/unrecognized) -> stand down: consume the marker, no output.

        Only the involuntary drop states (acceptEdits/default/manual) replay;
        anything else must never be auto-allowed.
        """
        for mode_payload in (
            {"permission_mode": "plan"},
            {"permission_mode": "bypassPermissions"},  # unreachable in practice; pinned defensively
            {},
        ):
            marker = _arm_marker(tmp_path)
            code, data = _run(tmp_path, payload={"tool_name": "Bash", **mode_payload})
            assert code == 0, mode_payload
            assert data is None, mode_payload
            assert not marker.exists(), mode_payload
