"""Tests for native_plan_capture - filing an approved native plan under docs/plans/."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parent.parent / "native_plan_capture.py"
SESSION = "test-session"

PLAN = """# Rate-limit the webhook receiver

## Context

Bursty senders currently melt the queue.

## Steps

- [ ] Task 1: add a token bucket per sender
- [ ] Task 2: shed load past the bucket
"""


def _run(
    tmp_path: Path,
    payload: dict | None = None,
    *,
    project_root_env: bool = True,
) -> tuple[int, str]:
    """Run the hook hermetically and return (exit code, stdout)."""
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir(exist_ok=True)
    project.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["PILOT_SESSION_ID"] = SESSION
    if project_root_env:
        env["CLAUDE_PROJECT_ROOT"] = str(project)
    else:
        env.pop("CLAUDE_PROJECT_ROOT", None)
    env.pop("CLAUDE_CODE_SESSION_ID", None)
    env.pop("CODEX_THREAD_ID", None)
    env.pop("PYTHONPATH", None)
    if payload is None:
        payload = {
            "tool_name": "ExitPlanMode",
            "tool_input": {"plan": PLAN, "planFilePath": "/tmp/scratch.md"},
            "tool_response": {"is_error": False},
        }
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(project),
        input=json.dumps(payload),
    )
    return result.returncode, result.stdout.strip()


def _register_run(tmp_path: Path, *, status: str = "PENDING", in_project: bool = True) -> Path:
    """Write the active_plan.json a live /spec or /build run leaves behind."""
    session_dir = tmp_path / "home" / ".pilot" / "sessions" / SESSION
    session_dir.mkdir(parents=True, exist_ok=True)
    parent = tmp_path / "project" if in_project else tmp_path / "elsewhere"
    plans_dir = parent / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    plan_path = plans_dir / "2026-09-02-registered-run.md"
    plan_path.write_text(f"# Registered\n\nStatus: {status}\nApproved: Yes\nType: Feature\n")
    (session_dir / "active_plan.json").write_text(json.dumps({"plan_path": str(plan_path), "status": status}))
    return plan_path


def _captured(tmp_path: Path) -> list[Path]:
    plans = tmp_path / "project" / "docs" / "plans"
    if not plans.is_dir():
        return []
    return sorted(p for p in plans.iterdir() if p.suffix == ".md")


class TestNativePlanCapture:
    def test_captures_an_approved_native_plan(self, tmp_path):
        code, out = _run(tmp_path)
        assert code == 0
        files = _captured(tmp_path)
        assert len(files) == 1
        assert files[0].name.endswith("-rate-limit-the-webhook-receiver.md")
        content = files[0].read_text()
        assert content.startswith("# Rate-limit the webhook receiver\n")
        # The body survives verbatim below the header, headings and tasks intact.
        assert "## Context" in content
        assert "- [ ] Task 1: add a token bucket per sender" in content
        # Exactly one H1: the lifted title, never a duplicate from the body.
        assert content.count("\n# ") == 0
        # A plan that already opens with a section keeps it: no empty Summary
        # card wrapped above the real first heading.
        assert "## Summary" not in content
        assert out, "the agent must be told where the plan was filed"
        assert "docs/plans" in out

    def test_prose_only_plan_is_wrapped_in_a_summary_section(self, tmp_path):
        """Body text outside any `## ` section renders nowhere - give it one."""
        _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"plan": "# Small change\n\nSwap the constant and move on.\n"},
            },
        )
        content = _captured(tmp_path)[0].read_text()
        assert "## Summary\n\nSwap the constant and move on." in content

    def test_captured_plan_is_never_an_in_flight_run(self, tmp_path):
        """The staleness contract: a captured plan carries a terminal status.

        Nothing advances a native plan - there is no implement or verify phase
        to hook - so writing it PENDING would put a spec in the Console's active
        surfaces that no workflow can ever close. Every active-run surface keys
        on PENDING/COMPLETE, so the status must be neither.
        """
        _run(tmp_path)
        content = _captured(tmp_path)[0].read_text()
        assert "Status: SAVED" in content
        assert "Status: PENDING" not in content
        assert "Status: COMPLETE" not in content
        # Type keeps it off the Feature/Bugfix/Build workflow surfaces.
        assert "Type: Plan" in content
        # Header fields the plan format declares required, so every reader agrees.
        for field in ("Created:", "Agent:", "Approved:", "Worktree:", "Iterations:"):
            assert field in content, field

    def test_skips_while_a_pilot_run_owns_the_plan_mode_leg(self, tmp_path):
        """`/spec` and `/build` maintain their own plan file - never duplicate it.

        Regression guard: capturing here would drop a second file into
        docs/plans/ that competes with the registered run in the Console list.
        """
        registered = _register_run(tmp_path)
        code, out = _run(tmp_path)
        assert code == 0
        assert out == ""
        assert _captured(tmp_path) == [registered]

    def test_captures_when_the_registered_run_is_finished(self, tmp_path):
        """A VERIFIED plan from an earlier /spec in the same session is not a live run."""
        registered = _register_run(tmp_path, status="VERIFIED")
        _run(tmp_path)
        assert len(_captured(tmp_path)) == 2
        assert registered.read_text().startswith("# Registered")

    def test_captures_when_the_registered_run_belongs_to_another_project(self, tmp_path):
        """Cross-project bleed: a PENDING plan from another repo must not mute capture."""
        _register_run(tmp_path, in_project=False)
        _run(tmp_path)
        assert len(_captured(tmp_path)) == 1

    def test_skips_a_failed_or_rejected_exit(self, tmp_path):
        code, out = _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"plan": PLAN},
                "tool_response": {"is_error": True},
            },
        )
        assert code == 0
        assert out == ""
        assert _captured(tmp_path) == []

    def test_skips_other_tools_and_empty_plans(self, tmp_path):
        for payload in (
            {"tool_name": "EnterPlanMode", "tool_input": {"plan": PLAN}},
            {"tool_name": "ExitPlanMode", "tool_input": {"plan": "   "}},
            {"tool_name": "ExitPlanMode", "tool_input": {}},
            {"tool_name": "ExitPlanMode"},
        ):
            code, out = _run(tmp_path, payload=payload)
            assert code == 0, payload
            assert out == "", payload
            assert _captured(tmp_path) == [], payload

    def test_falls_back_to_the_scratch_file_claude_code_wrote(self, tmp_path):
        scratch = tmp_path / "home" / ".claude" / "plans" / "scratch.md"
        scratch.parent.mkdir(parents=True)
        scratch.write_text(PLAN)
        code, _ = _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"planFilePath": str(scratch)},
            },
        )
        assert code == 0
        assert len(_captured(tmp_path)) == 1

    def test_never_reads_a_scratch_file_outside_claudes_plan_directory(self, tmp_path):
        """A tool payload must not turn plan capture into an arbitrary-file copy."""
        outside = tmp_path / "private.md"
        outside.write_text("# Private\n\nA secret that is not a Claude plan.\n")

        code, out = _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"planFilePath": str(outside)},
            },
        )

        assert code == 0
        assert out == ""
        assert _captured(tmp_path) == []

    def test_honors_a_project_relative_custom_plans_directory(self, tmp_path):
        config_dir = tmp_path / "home" / ".claude"
        config_dir.mkdir(parents=True)
        (config_dir / "settings.json").write_text(json.dumps({"plansDirectory": ".plans"}))
        scratch = tmp_path / "project" / ".plans" / "scratch.md"
        scratch.parent.mkdir(parents=True)
        scratch.write_text(PLAN)

        code, _ = _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"planFilePath": str(scratch)},
            },
        )

        assert code == 0
        assert len(_captured(tmp_path)) == 1

    def test_rejects_a_scratch_symlink_that_escapes_the_plan_directory(self, tmp_path):
        outside = tmp_path / "private.md"
        outside.write_text("# Private\n\nA secret that is not a Claude plan.\n")
        scratch = tmp_path / "home" / ".claude" / "plans" / "scratch.md"
        scratch.parent.mkdir(parents=True)
        scratch.symlink_to(outside)

        code, out = _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"planFilePath": str(scratch)},
            },
        )

        assert code == 0
        assert out == ""
        assert _captured(tmp_path) == []

    def test_never_overwrites_an_existing_capture(self, tmp_path):
        """A second plan the same day keeps its own file - and so does a hand edit."""
        _run(tmp_path)
        first = _captured(tmp_path)[0]
        first.write_text(first.read_text() + "\n<!-- hand-edited -->\n")
        _run(tmp_path)
        files = _captured(tmp_path)
        assert len(files) == 2
        assert "hand-edited" in first.read_text()

    def test_untitled_plan_still_gets_a_file(self, tmp_path):
        code, _ = _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"plan": "Just do the thing, carefully.\n"},
            },
        )
        assert code == 0
        files = _captured(tmp_path)
        assert len(files) == 1
        content = files[0].read_text()
        assert content.startswith("# Plan\n")
        assert "Just do the thing, carefully." in content

    def test_says_so_when_there_is_no_project_root_to_file_into(self, tmp_path):
        """No project root = nowhere to write - but never fail silently.

        The plan exists only in Claude Code's throwaway scratch file at this
        point, so swallowing the failure loses it with no way for the user to
        know. Tell them instead of guessing with cwd.
        """
        code, out = _run(tmp_path, project_root_env=False)
        assert code == 0
        assert "not" in out.lower() and "saved" in out.lower(), out
        assert _captured(tmp_path) == []

    def test_prefers_the_approved_plan_from_the_tool_response(self, tmp_path):
        """The user can edit a plan during native review; the response is truth.

        Capturing `tool_input.plan` files what was PROPOSED, so any edit made in
        the approval dialog leaves the saved document silently out of date.
        """
        _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"plan": "# Proposed\n\nThe original idea.\n"},
                "tool_response": {"plan": "# Approved\n\nWhat they actually agreed to.\n"},
            },
        )
        files = _captured(tmp_path)
        assert len(files) == 1
        content = files[0].read_text()
        assert files[0].name.endswith("-approved.md")
        assert "What they actually agreed to." in content
        assert "The original idea." not in content

    def test_falls_back_to_the_request_when_the_response_carries_no_plan(self, tmp_path):
        """Not every build returns a plan in the response; the proposal still counts."""
        _run(
            tmp_path,
            payload={
                "tool_name": "ExitPlanMode",
                "tool_input": {"plan": "# Proposed\n\nThe original idea.\n"},
                "tool_response": {"is_error": False},
            },
        )
        assert "The original idea." in _captured(tmp_path)[0].read_text()

    def test_skips_when_an_orchestration_lane_owns_a_run(self, tmp_path):
        """A lane's /spec registers under lanes/<id>/, not the session slot.

        Reading only the session slot made a lane-owned run look like no run at
        all, so the capture filed a duplicate competing with the real plan.
        """
        lane_dir = tmp_path / "home" / ".pilot" / "sessions" / SESSION / "lanes" / "lane-a"
        lane_dir.mkdir(parents=True)
        plans_dir = tmp_path / "project" / "docs" / "plans"
        plans_dir.mkdir(parents=True)
        lane_plan = plans_dir / "2026-09-02-lane-run.md"
        lane_plan.write_text("# Lane\n\nStatus: PENDING\nApproved: Yes\nType: Feature\n")
        (lane_dir / "active_plan.json").write_text(json.dumps({"plan_path": str(lane_plan), "status": "PENDING"}))

        code, out = _run(tmp_path)
        assert code == 0
        assert out == ""
        assert _captured(tmp_path) == [lane_plan]

    def test_skips_when_workflow_ownership_cannot_be_determined(self, tmp_path):
        """A corrupt active_plan.json is ambiguous - never write a competing file.

        `_read_active_plan` swallows the parse error and returns None, which read
        as "no workflow is running" and produced exactly the duplicate this skip
        exists to prevent. Ambiguity must fail CLOSED.
        """
        session_dir = tmp_path / "home" / ".pilot" / "sessions" / SESSION
        session_dir.mkdir(parents=True)
        (session_dir / "active_plan.json").write_text("{ this is not json")

        code, out = _run(tmp_path)
        assert code == 0
        assert out == ""
        assert _captured(tmp_path) == []
