"""Tests for session_clear hook — stale session state cleanup on /clear."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import session_clear


def test_removes_stale_findings_files(tmp_path: Path):
    """Should delete reviewer findings from session directory."""
    session_dir = tmp_path / "sessions" / "1001"
    session_dir.mkdir(parents=True)
    (session_dir / "findings-plan-reviewer.json").write_text("{}")
    (session_dir / "findings-spec-reviewer.json").write_text("{}")

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_clear, "SESSIONS_DIR", tmp_path / "sessions"),
    ):
        result = session_clear.main()

    assert result == 0
    assert not (session_dir / "findings-plan-reviewer.json").exists()
    assert not (session_dir / "findings-spec-reviewer.json").exists()


def test_removes_all_stale_state(tmp_path: Path):
    """Should delete all stale session files."""
    session_dir = tmp_path / "sessions" / "1001"
    session_dir.mkdir(parents=True)
    for name in session_clear.STALE_FILES:
        (session_dir / name).write_text("stale")

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_clear, "SESSIONS_DIR", tmp_path / "sessions"),
    ):
        result = session_clear.main()

    assert result == 0
    for name in session_clear.STALE_FILES:
        assert not (session_dir / name).exists(), f"{name} should have been deleted"


def test_preserves_worktree_json(tmp_path: Path):
    """Should NOT delete worktree.json — it tracks a physical git resource."""
    session_dir = tmp_path / "sessions" / "1001"
    session_dir.mkdir(parents=True)
    (session_dir / "worktree.json").write_text('{"path": "/tmp/wt"}')

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_clear, "SESSIONS_DIR", tmp_path / "sessions"),
    ):
        session_clear.main()

    assert (session_dir / "worktree.json").exists()


def test_cleans_task_list(tmp_path: Path):
    """Should remove stale task files from ~/.claude/tasks/pilot-<PID>/."""
    task_dir = tmp_path / ".claude" / "tasks" / "pilot-1001"
    task_dir.mkdir(parents=True)
    (task_dir / "task-abc.json").write_text('{"subject": "Old task"}')
    (task_dir / "task-def.json").write_text('{"subject": "Another old task"}')

    session_dir = tmp_path / "sessions" / "1001"
    session_dir.mkdir(parents=True)

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_clear, "SESSIONS_DIR", tmp_path / "sessions"),
        patch("session_clear.Path.home", return_value=tmp_path),
    ):
        session_clear.main()

    json_files = list(task_dir.glob("*.json"))
    assert json_files == [], f"Expected no task files, found: {[f.name for f in json_files]}"


def test_task_cleanup_skips_missing_dir(tmp_path: Path):
    """Should not fail when task directory doesn't exist."""
    session_dir = tmp_path / "sessions" / "1001"
    session_dir.mkdir(parents=True)

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_clear, "SESSIONS_DIR", tmp_path / "sessions"),
        patch("session_clear.Path.home", return_value=tmp_path),
    ):
        result = session_clear.main()

    assert result == 0


def test_noop_when_no_session_id():
    """Should return 0 when PILOT_SESSION_ID is not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("PILOT_SESSION_ID", None)
        result = session_clear.main()

    assert result == 0


def test_noop_when_session_dir_missing(tmp_path: Path):
    """Should return 0 when session directory doesn't exist."""
    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "9999"}),
        patch.object(session_clear, "SESSIONS_DIR", tmp_path / "sessions"),
    ):
        result = session_clear.main()

    assert result == 0


def test_tolerates_already_missing_files(tmp_path: Path):
    """Should not fail when stale files don't exist."""
    session_dir = tmp_path / "sessions" / "1001"
    session_dir.mkdir(parents=True)
    (session_dir / "active_plan.json").write_text("{}")

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_clear, "SESSIONS_DIR", tmp_path / "sessions"),
    ):
        result = session_clear.main()

    assert result == 0
    assert not (session_dir / "active_plan.json").exists()
