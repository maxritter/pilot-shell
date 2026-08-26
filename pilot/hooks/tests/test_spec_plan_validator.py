"""Tests for spec_plan_validator hook."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))
from spec_plan_validator import main

VALID_FEATURE_HEADER = """# Test Plan

Created: 2026-02-18
Status: PENDING
Approved: No
Iterations: 0
Worktree: No
Type: Feature
"""

VALID_BUILD_HEADER = """# Test Buildout

Created: 2026-02-18
Status: PENDING
Approved: No
Rounds: 0
Worktree: No
Type: Build
"""


class TestSpecPlanValidator:
    @patch("spec_plan_validator.is_waiting_for_user_input", return_value=False)
    @patch("sys.stdin")
    def test_blocks_when_no_plans_dir(self, mock_stdin, mock_waiting, tmp_path, capsys):
        with patch(
            "spec_plan_validator.json.load",
            return_value={
                "transcript_path": "/t.jsonl",
                "stop_hook_active": False,
                "project_root": str(tmp_path),
            },
        ):
            with patch("spec_plan_validator.os.environ", {"CLAUDE_PROJECT_ROOT": str(tmp_path)}):
                result = main()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["decision"] == "block"
        assert "not created yet" in data["reason"]

    @patch("spec_plan_validator.is_waiting_for_user_input", return_value=False)
    @patch("sys.stdin")
    def test_blocks_when_no_today_plans(self, mock_stdin, mock_waiting, tmp_path, capsys):
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)
        (plans_dir / "2020-01-01-old-plan.md").touch()

        with patch(
            "spec_plan_validator.json.load",
            return_value={
                "transcript_path": "/t.jsonl",
                "stop_hook_active": False,
                "project_root": str(tmp_path),
            },
        ):
            with patch("spec_plan_validator.os.environ", {"CLAUDE_PROJECT_ROOT": str(tmp_path)}):
                result = main()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["decision"] == "block"

    @patch("spec_plan_validator.is_waiting_for_user_input", return_value=False)
    @patch("spec_plan_validator.datetime")
    @patch("sys.stdin")
    def test_allows_when_today_plan_exists(self, mock_stdin, mock_dt, mock_waiting, tmp_path, capsys):
        import datetime

        mock_dt.date.today.return_value = datetime.date(2026, 2, 18)

        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)
        (plans_dir / "2026-02-18-test-plan.md").write_text(VALID_FEATURE_HEADER)

        with patch(
            "spec_plan_validator.json.load",
            return_value={
                "transcript_path": "/t.jsonl",
                "stop_hook_active": False,
                "project_root": str(tmp_path),
            },
        ):
            with patch("spec_plan_validator.os.environ", {"CLAUDE_PROJECT_ROOT": str(tmp_path)}):
                result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    @patch("spec_plan_validator.is_waiting_for_user_input", return_value=False)
    @patch("sys.stdin")
    def test_blocks_when_registered_plan_is_malformed(self, mock_stdin, mock_waiting, tmp_path, capsys):
        plan = tmp_path / "docs" / "plans" / "malformed.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("# This is Markdown, but not a Pilot plan.\n")

        with (
            patch("spec_plan_validator.json.load", return_value={"project_root": str(tmp_path)}),
            patch("spec_plan_validator._own_registered_plan", return_value=plan),
        ):
            assert main() == 0

        data = json.loads(capsys.readouterr().out)
        assert data["decision"] == "block"
        assert "not renderable" in data["reason"]
        assert "plan header" in data["reason"]

    def test_hook_local_fallback_rejects_unrenderable_plan(self, tmp_path):
        from spec_plan_validator import _validation_errors

        plan = tmp_path / "malformed.md"
        plan.write_text("# Not a plan\n")
        with patch("spec_plan_validator._canonical_validation_errors", return_value=None):
            errors = _validation_errors(plan)

        assert errors
        assert "plan header" in errors[0]

    def test_valid_unfinished_plan_has_no_blocking_errors(self, tmp_path):
        """No tasks is a canonical warning and must not hold the planning turn open."""
        from spec_plan_validator import _validation_errors

        plan = tmp_path / "unfinished.md"
        plan.write_text(VALID_FEATURE_HEADER)
        assert _validation_errors(plan) == []

    @patch("sys.stdin")
    def test_allows_when_waiting_for_user(self, mock_stdin):
        with patch(
            "spec_plan_validator.json.load",
            return_value={
                "transcript_path": "/t.jsonl",
                "stop_hook_active": False,
            },
        ):
            with patch("spec_plan_validator.is_waiting_for_user_input", return_value=True):
                result = main()

        assert result == 0


class TestBuildoutDirectory:
    """`/build` registers this hook against docs/builds/, not docs/plans/."""

    @patch("spec_plan_validator.is_waiting_for_user_input", return_value=False)
    @patch("sys.stdin")
    def test_blocks_when_buildout_missing_despite_a_plan_existing(self, mock_stdin, mock_waiting, tmp_path, capsys):
        # A /spec plan created today must NOT satisfy /build's guard: the two
        # workflows write to different directories and each must produce its own.
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)
        (plans_dir / "2026-02-18-some-spec.md").touch()

        with patch(
            "spec_plan_validator.json.load",
            return_value={
                "transcript_path": "/t.jsonl",
                "stop_hook_active": False,
                "project_root": str(tmp_path),
            },
        ):
            with patch("spec_plan_validator.os.environ", {"CLAUDE_PROJECT_ROOT": str(tmp_path)}):
                result = main("docs/builds", "Buildout")

        assert result == 0
        data = json.loads(capsys.readouterr().out)
        assert data["decision"] == "block"
        assert "Buildout" in data["reason"]
        assert "docs/builds" in data["reason"]

    @patch("spec_plan_validator.is_waiting_for_user_input", return_value=False)
    @patch("spec_plan_validator.datetime")
    @patch("sys.stdin")
    def test_allows_when_today_buildout_exists(self, mock_stdin, mock_dt, mock_waiting, tmp_path, capsys):
        import datetime

        mock_dt.date.today.return_value = datetime.date(2026, 2, 18)

        builds_dir = tmp_path / "docs" / "builds"
        builds_dir.mkdir(parents=True)
        (builds_dir / "2026-02-18-running-brand.md").write_text(VALID_BUILD_HEADER)

        with patch(
            "spec_plan_validator.json.load",
            return_value={
                "transcript_path": "/t.jsonl",
                "stop_hook_active": False,
                "project_root": str(tmp_path),
            },
        ):
            with patch("spec_plan_validator.os.environ", {"CLAUDE_PROJECT_ROOT": str(tmp_path)}):
                result = main("docs/builds", "Buildout")

        assert result == 0
        assert capsys.readouterr().out == ""


class TestSessionScoping:
    """The guard must be satisfied by THIS session's plan, not a sibling's.

    The original report (community thread, Aug 11) was that Pilot hooks fired in
    every session running in one repo directory. Every plan READER is now
    session-scoped through `resolve_session_id`, but this guard still globbed
    `docs/plans/{today}-*.md` repo-wide, so a plan created by another session
    silently satisfied it and a planning run could end with no file of its own.
    """

    def _payload(self, tmp_path: Path) -> dict:
        return {"stop_hook_active": False, "transcript_path": "", "project_root": str(tmp_path)}

    def _run(self, tmp_path: Path, payload: dict, capsys) -> bool:
        """Run the hook; return True when it blocked the stop."""
        with (
            patch("spec_plan_validator.is_waiting_for_user_input", return_value=False),
            patch("sys.stdin"),
            patch("spec_plan_validator.json.load", return_value=payload),
        ):
            main()
        return "decision" in capsys.readouterr().out

    def _plan_file(self, tmp_path: Path, name: str) -> Path:
        plans = tmp_path / "docs" / "plans"
        plans.mkdir(parents=True, exist_ok=True)
        path = plans / name
        path.write_text(VALID_FEATURE_HEADER)
        return path

    def _register(self, home: Path, session_id: str, plan: Path) -> None:
        session_dir = home / ".pilot" / "sessions" / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "active_plan.json").write_text(json.dumps({"plan_path": str(plan), "status": "PENDING"}))

    def test_sibling_sessions_plan_does_not_satisfy_this_session(self, tmp_path, capsys, monkeypatch):
        import datetime

        today = datetime.date.today().strftime("%Y-%m-%d")
        home = tmp_path / "home"
        plan = self._plan_file(tmp_path, f"{today}-session-a-plan.md")
        self._register(home, "session-a", plan)

        monkeypatch.setenv("PILOT_SESSION_ID", "session-b")
        monkeypatch.setattr(Path, "home", classmethod(lambda _cls: home))

        assert self._run(tmp_path, self._payload(tmp_path), capsys), (
            "session B was let go because session A had created a plan today"
        )

    def test_own_registration_satisfies_the_guard(self, tmp_path, capsys, monkeypatch):
        """Registered under a name today's glob would never match."""
        home = tmp_path / "home"
        plan = self._plan_file(tmp_path, "1999-01-01-old-name.md")
        self._register(home, "session-b", plan)

        monkeypatch.setenv("PILOT_SESSION_ID", "session-b")
        monkeypatch.setattr(Path, "home", classmethod(lambda _cls: home))

        assert not self._run(tmp_path, self._payload(tmp_path), capsys)

    def test_blocks_with_no_registration_and_no_file(self, tmp_path, capsys, monkeypatch):
        home = tmp_path / "home"
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        monkeypatch.setenv("PILOT_SESSION_ID", "session-b")
        monkeypatch.setattr(Path, "home", classmethod(lambda _cls: home))

        assert self._run(tmp_path, self._payload(tmp_path), capsys)

    def test_documented_residual_two_unregistered_sessions_collide(self, tmp_path, capsys, monkeypatch):
        """KNOWN LIMITATION, asserted deliberately so it cannot change silently.

        With NEITHER session registered there is no signal that attributes a plan
        file to a session, so the today-glob fallback accepts a sibling's file.
        Closing this would mean inferring ownership from mtime versus session
        start, which is guesswork that misfires on a plan edited across a session
        boundary. `pilot spec` documents `pilot register-plan` as the step that
        earns session-scoped guarding.
        """
        import datetime

        today = datetime.date.today().strftime("%Y-%m-%d")
        home = tmp_path / "home"
        self._plan_file(tmp_path, f"{today}-someone-elses.md")

        monkeypatch.setenv("PILOT_SESSION_ID", "session-b")
        monkeypatch.setattr(Path, "home", classmethod(lambda _cls: home))

        assert not self._run(tmp_path, self._payload(tmp_path), capsys), (
            "documented residual changed -- update the docs and the plan before changing this"
        )
