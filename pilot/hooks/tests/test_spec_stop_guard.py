"""Tests for spec_stop_guard hook — blocks session stop during active /spec workflows.

Notifications were removed from the stop guard — spec skills now handle
all notifications via `pilot notify`. The stop guard only blocks/allows stops.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from spec_stop_guard import main

HOOK_PATH = Path(__file__).resolve().parent.parent / "spec_stop_guard.py"
TEST_SESSION_ID = "test-spec-stop-guard"


def _test_session_dir() -> Path:
    """Get the session directory for the test session."""
    return Path.home() / ".pilot" / "sessions" / TEST_SESSION_ID


def _register_plan_for_session(plan_path: Path, status: str = "PENDING") -> None:
    """Register a plan in active_plan.json for the test session."""
    session_dir = _test_session_dir()
    session_dir.mkdir(parents=True, exist_ok=True)
    active_plan_json = session_dir / "active_plan.json"
    active_plan_json.write_text(json.dumps({"plan_path": str(plan_path), "status": status}))


@pytest.fixture(autouse=True)
def clear_session_state():
    """Clear session state before and after each test."""
    session_dir = _test_session_dir()
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
    yield
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)


def _run_subprocess(input_data: dict, plans_dir: Path | None = None) -> tuple[int, str, str]:
    """Run the hook as a subprocess. Returns (exit_code, stdout, stderr)."""
    cwd = str(plans_dir.parent.parent) if plans_dir else None
    env = {**os.environ, "PILOT_SESSION_ID": TEST_SESSION_ID}
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def _is_blocked(stdout: str) -> bool:
    """Check if the hook output contains a stop_block decision."""
    try:
        data = json.loads(stdout.strip())
        return data.get("decision") == "block"
    except (json.JSONDecodeError, ValueError):
        return False


class TestUnitMain:
    """Unit tests with mocked dependencies."""

    @patch("spec_stop_guard.find_active_plan")
    @patch("spec_stop_guard.is_waiting_for_user_input")
    @patch("sys.stdin")
    def test_allows_stop_when_waiting_for_input(self, mock_stdin, mock_waiting, mock_find_plan):
        mock_find_plan.return_value = (Path("/plan.md"), "PENDING")
        mock_waiting.return_value = True
        mock_stdin.read.return_value = json.dumps({"transcript_path": "/transcript.jsonl", "stop_hook_active": False})

        assert main() == 0

    @patch("spec_stop_guard.find_active_plan")
    @patch("spec_stop_guard.is_waiting_for_user_input")
    @patch("spec_stop_guard.get_stop_guard_path")
    @patch("spec_stop_guard.time.time")
    @patch("sys.stdin")
    def test_allows_stop_on_cooldown_escape(self, mock_stdin, mock_time, mock_guard_path, mock_waiting, mock_find_plan):
        mock_find_plan.return_value = (Path("/plan.md"), "PENDING")
        mock_waiting.return_value = False
        mock_time.return_value = 100.0

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".state") as f:
            f.write("50.0")
            state_path = Path(f.name)

        mock_guard_path.return_value = state_path
        mock_stdin.read.return_value = json.dumps({"transcript_path": "/transcript.jsonl", "stop_hook_active": False})

        try:
            assert main() == 0
        finally:
            state_path.unlink(missing_ok=True)

    @patch("spec_stop_guard.find_active_plan")
    @patch("sys.stdin")
    def test_allows_stop_when_no_active_plan(self, mock_stdin, mock_find_plan):
        mock_find_plan.return_value = (None, None)
        mock_stdin.read.return_value = json.dumps({"transcript_path": "/transcript.jsonl", "stop_hook_active": False})

        assert main() == 0

    @patch("spec_stop_guard.find_active_plan")
    @patch("spec_stop_guard.is_waiting_for_user_input")
    @patch("spec_stop_guard.get_stop_guard_path")
    @patch("spec_stop_guard.time.time")
    @patch("sys.stdin")
    def test_blocks_stop_when_outside_cooldown(
        self, mock_stdin, mock_time, mock_guard_path, mock_waiting, mock_find_plan, capsys
    ):
        mock_find_plan.return_value = (Path("/plan.md"), "PENDING")
        mock_waiting.return_value = False
        mock_time.return_value = 200.0

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".state") as f:
            f.write("100.0")
            state_path = Path(f.name)

        mock_guard_path.return_value = state_path
        mock_stdin.read.return_value = json.dumps({"transcript_path": "/transcript.jsonl", "stop_hook_active": False})

        try:
            result = main()
            assert result == 0
            captured = capsys.readouterr()
            data = json.loads(captured.out)
            assert data["decision"] == "block"
            assert "/plan.md" in data["reason"]
        finally:
            state_path.unlink(missing_ok=True)


class TestGetStopGuardPath:
    """Test get_stop_guard_path() session scoping."""

    def test_returns_session_scoped_path(self, tmp_path: Path) -> None:
        from spec_stop_guard import get_stop_guard_path

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": "12345"}),
            patch("spec_stop_guard._sessions_base", return_value=tmp_path / "sessions"),
        ):
            result = get_stop_guard_path()
            assert result == tmp_path / "sessions" / "12345" / "spec-stop-guard"

    def test_falls_back_to_default(self, tmp_path: Path) -> None:
        from spec_stop_guard import get_stop_guard_path

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("spec_stop_guard._sessions_base", return_value=tmp_path / "sessions"),
        ):
            result = get_stop_guard_path()
            assert result == tmp_path / "sessions" / "default" / "spec-stop-guard"

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        from spec_stop_guard import get_stop_guard_path

        base = tmp_path / "sessions"
        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": "777"}),
            patch("spec_stop_guard._sessions_base", return_value=base),
        ):
            result = get_stop_guard_path()
            assert result.parent.is_dir()


class TestSubprocessIntegration:
    """Subprocess-level tests with real file I/O."""

    def test_allows_stop_when_no_active_plan(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert not _is_blocked(stdout)

    def test_allows_stop_when_plan_is_verified(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-01-27-test-feature.md"
        plan_file.write_text("# Test Plan\n\nStatus: VERIFIED\nApproved: Yes\n")

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert not _is_blocked(stdout)

    def test_blocks_stop_when_plan_is_pending(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-01-27-test-feature.md"
        plan_file.write_text("# Test Plan\n\nStatus: PENDING\nApproved: No\n")
        _register_plan_for_session(plan_file, "PENDING")

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert _is_blocked(stdout)
        assert "cannot stop" in stdout.lower()

    def test_blocks_stop_when_plan_is_complete(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-01-27-test-feature.md"
        plan_file.write_text("# Test Plan\n\nStatus: COMPLETE\nApproved: Yes\n")
        _register_plan_for_session(plan_file, "COMPLETE")

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert _is_blocked(stdout)
        assert "cannot stop" in stdout.lower()

    def test_allows_stop_when_stop_hook_already_active(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-01-27-test-feature.md"
        plan_file.write_text("# Test Plan\n\nStatus: PENDING\nApproved: No\n")
        _register_plan_for_session(plan_file, "PENDING")

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": True}, plans_dir)
        assert exit_code == 0
        assert not _is_blocked(stdout)

    def test_allows_stop_when_asking_user_question(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-01-27-test-feature.md"
        plan_file.write_text("# Test Plan\n\nStatus: PENDING\nApproved: No\n")
        _register_plan_for_session(plan_file, "PENDING")

        transcript_file = tmp_path / "session.jsonl"
        assistant_msg = {
            "type": "assistant",
            "message": {
                "content": [{"type": "tool_use", "name": "AskUserQuestion", "input": {"question": "Approve?"}}]
            },
        }
        transcript_file.write_text(json.dumps(assistant_msg) + "\n")

        exit_code, stdout, _ = _run_subprocess(
            {"stop_hook_active": False, "transcript_path": str(transcript_file)},
            plans_dir,
        )
        assert exit_code == 0
        assert not _is_blocked(stdout)

    def test_blocks_stop_when_last_action_not_question(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-01-27-test-feature.md"
        plan_file.write_text("# Test Plan\n\nStatus: PENDING\nApproved: No\n")
        _register_plan_for_session(plan_file, "PENDING")

        transcript_file = tmp_path / "session.jsonl"
        assistant_msg = {
            "type": "assistant",
            "message": {"content": [{"type": "tool_use", "name": "Write", "input": {"file_path": "/tmp/test.py"}}]},
        }
        transcript_file.write_text(json.dumps(assistant_msg) + "\n")

        exit_code, stdout, _ = _run_subprocess(
            {"stop_hook_active": False, "transcript_path": str(transcript_file)},
            plans_dir,
        )
        assert exit_code == 0
        assert _is_blocked(stdout)
        assert "cannot stop" in stdout.lower()

    def test_handles_invalid_json_input(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input="not valid json",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_uses_registered_plan_not_other_plans_in_dir(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        unregistered_plan = plans_dir / "2026-01-01-other-feature.md"
        unregistered_plan.write_text("# Other Plan\n\nStatus: PENDING\nApproved: No\n")

        registered_plan = plans_dir / "2026-01-27-my-feature.md"
        registered_plan.write_text("# My Plan\n\nStatus: PENDING\nApproved: No\n")
        _register_plan_for_session(registered_plan, "PENDING")

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert _is_blocked(stdout)
        assert str(registered_plan) in stdout


class TestCooldownEscape:
    """Tests for the double-stop cooldown escape hatch."""

    def test_allows_escape_on_second_stop(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-01-27-test-feature.md"
        plan_file.write_text("# Test Plan\n\nStatus: PENDING\nApproved: No\n")
        _register_plan_for_session(plan_file, "PENDING")

        exit_code1, stdout1, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code1 == 0
        assert _is_blocked(stdout1)
        assert "60s to force exit" in stdout1

        exit_code2, stdout2, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code2 == 0
        assert not _is_blocked(stdout2)

    def test_cooldown_resets_after_escape(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-01-27-test-feature.md"
        plan_file.write_text("# Test Plan\n\nStatus: PENDING\nApproved: No\n")
        _register_plan_for_session(plan_file, "PENDING")

        exit_code1, stdout1, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert _is_blocked(stdout1)

        exit_code2, stdout2, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert not _is_blocked(stdout2)

        exit_code3, stdout3, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert _is_blocked(stdout3)


class TestSessionScopedPlanDetection:
    """Tests that find_active_plan() uses session-scoped active_plan.json."""

    def test_ignores_plan_from_other_session(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-02-06-other-session-plan.md"
        plan_file.write_text("# Other Plan\n\nStatus: PENDING\nApproved: Yes\n")

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert not _is_blocked(stdout)

    def test_blocks_when_plan_registered_for_session(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-02-06-my-plan.md"
        plan_file.write_text("# My Plan\n\nStatus: PENDING\nApproved: No\n")
        _register_plan_for_session(plan_file, "PENDING")

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert _is_blocked(stdout)
        assert "cannot stop" in stdout.lower()

    def test_allows_stop_when_registered_plan_is_verified(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-02-06-done-plan.md"
        plan_file.write_text("# Done Plan\n\nStatus: VERIFIED\nApproved: Yes\n")
        _register_plan_for_session(plan_file, "PENDING")

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert not _is_blocked(stdout)

    def test_allows_stop_when_registered_plan_file_deleted(self, tmp_path: Path) -> None:
        _register_plan_for_session(Path("/nonexistent/plan.md"), "PENDING")
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)
        assert exit_code == 0
        assert not _is_blocked(stdout)

    def test_resolves_relative_plan_path_against_project_root(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "2026-02-06-relative.md"
        plan_file.write_text("# Relative\n\nStatus: PENDING\nApproved: Yes\n")

        session_dir = _test_session_dir()
        session_dir.mkdir(parents=True, exist_ok=True)
        active_plan_json = session_dir / "active_plan.json"
        active_plan_json.write_text(json.dumps({"plan_path": "docs/plans/2026-02-06-relative.md", "status": "PENDING"}))

        with patch.dict(os.environ, {"CLAUDE_PROJECT_ROOT": str(tmp_path)}):
            exit_code, stdout, _ = _run_subprocess({"stop_hook_active": False}, plans_dir)

        assert exit_code == 0
        assert _is_blocked(stdout)
        assert "cannot stop" in stdout.lower()
