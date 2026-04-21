"""Tests for session_end hook — worker stop and session completion behavior.

The hook is fully non-blocking: both side-effects (worker-stop and Console POST)
are handed to detached subprocesses so the harness cannot race cancellation with
synchronous I/O. Tests assert the detachment contract (``start_new_session=True``)
rather than the underlying network / process behaviour.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import session_end


def _find_call(mock: MagicMock, needle: str) -> tuple[tuple, dict] | None:
    """Return the first Popen call whose argv contains ``needle``, or None."""
    for call in mock.call_args_list:
        args, kwargs = call
        argv = args[0] if args else kwargs.get("args", [])
        if any(needle in str(token) for token in argv):
            return (args, kwargs)
    return None


def test_returns_early_without_plugin_root():
    """Should return 0 when CLAUDE_PLUGIN_ROOT is not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
        result = session_end.main()

    assert result == 0


def test_skips_stop_when_other_sessions_active(tmp_path: Path):
    """Should skip worker stop when other Pilot sessions are running."""
    base = tmp_path / "sessions"
    (base / "1001").mkdir(parents=True)
    (base / "2002").mkdir(parents=True)

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.os.kill", return_value=None),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    # No CLAUDE_SESSION_ID → no Console POST either; Popen should never fire.
    assert _find_call(mock_popen, "worker-service.cjs") is None


def test_stops_worker_when_no_other_sessions(tmp_path: Path):
    """Should spawn a detached worker-stop when this is the only active session."""
    base = tmp_path / "sessions"
    (base / "1001").mkdir(parents=True)

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    call = _find_call(mock_popen, "worker-service.cjs")
    assert call is not None, "worker-stop Popen never invoked"
    args, kwargs = call
    assert args[0][0] == "bun"
    assert args[0][-1] == "stop"
    assert kwargs["start_new_session"] is True
    assert kwargs["close_fds"] is True


def test_stops_worker_when_zero_sessions(tmp_path: Path):
    """Should spawn detached worker-stop even when no session dirs exist."""
    base = tmp_path / "sessions"
    base.mkdir(parents=True)

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    assert _find_call(mock_popen, "worker-service.cjs") is not None


def test_safe_default_on_directory_error():
    """Should NOT stop worker when sessions dir is unreadable (safe default)."""
    mock_dir = MagicMock()
    mock_dir.exists.side_effect = OSError("permission denied")

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", mock_dir),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    assert _find_call(mock_popen, "worker-service.cjs") is None


def test_skips_dead_pid_sessions(tmp_path: Path):
    """Should not count dead PID directories as active sessions."""
    base = tmp_path / "sessions"
    (base / "1001").mkdir(parents=True)
    (base / "9999").mkdir(parents=True)

    def kill_side_effect(pid: int, _sig: int) -> None:
        if pid == 9999:
            raise OSError("No such process")

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.os.kill", side_effect=kill_side_effect),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    assert _find_call(mock_popen, "worker-service.cjs") is not None


def test_worker_stop_swallows_exec_errors(tmp_path: Path):
    """Should not raise when bun is unavailable (OSError from Popen)."""
    base = tmp_path / "sessions"
    base.mkdir(parents=True)

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.subprocess.Popen", side_effect=OSError("bun not found")),
    ):
        # Should not raise
        assert session_end.main() == 0


# --- Session completion tests ---


def test_complete_session_spawns_detached_worker():
    """Should spawn a detached Python worker with URL and session id as argv."""
    with (
        patch.dict(os.environ, {"CLAUDE_SESSION_ID": "abc-123-def"}),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        session_end._complete_session()

    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    argv = args[0]
    assert argv[1] == "-c"
    assert argv[2] == session_end._COMPLETE_SESSION_WORKER
    assert argv[-2] == f"{session_end.CONSOLE_URL}/api/sessions/complete"
    assert argv[-1] == "abc-123-def"
    assert kwargs["start_new_session"] is True
    assert kwargs["close_fds"] is True


def test_complete_session_skips_without_session_id():
    """Should do nothing when CLAUDE_SESSION_ID is not set."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        os.environ.pop("CLAUDE_SESSION_ID", None)
        session_end._complete_session()

    mock_popen.assert_not_called()


def test_complete_session_ignores_exec_errors():
    """Should not raise when spawning the worker fails."""
    with (
        patch.dict(os.environ, {"CLAUDE_SESSION_ID": "abc-123"}),
        patch("session_end.subprocess.Popen", side_effect=OSError("no python")),
    ):
        # Should not raise
        session_end._complete_session()


def test_main_invokes_worker_stop_before_complete_session(tmp_path: Path):
    """Worker-stop must be spawned before _complete_session (leak > cosmetic).

    The critical resource release (port 41777, DB file descriptors) must happen
    first so that even a pathological failure of the Console POST spawn can't
    leave leaked workers.
    """
    base = tmp_path / "sessions"
    base.mkdir(parents=True)

    call_order: list[str] = []

    def popen_side_effect(argv, *_args, **_kwargs):
        if any("worker-service.cjs" in str(token) for token in argv):
            call_order.append("worker_stop")
        else:
            call_order.append("console_post")
        return MagicMock()

    with (
        patch.dict(
            os.environ,
            {
                "CLAUDE_PLUGIN_ROOT": "/fake/plugin",
                "PILOT_SESSION_ID": "1001",
                "CLAUDE_SESSION_ID": "session-xyz",
            },
        ),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.subprocess.Popen", side_effect=popen_side_effect),
    ):
        result = session_end.main()

    assert result == 0
    assert call_order == ["worker_stop", "console_post"]
