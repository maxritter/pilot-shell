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


def test_skips_stop_when_other_sessions_active(tmp_path: Path):
    """Should skip worker stop when other Pilot sessions are running."""
    base = tmp_path / "sessions"
    (base / "1001").mkdir(parents=True)
    (base / "2002").mkdir(parents=True)

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.os.kill", return_value=None),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    # No --session-end flag -> no Console POST either; Popen should never fire.
    assert _find_call(mock_popen, "worker-service.cjs") is None


def test_stops_worker_when_no_other_sessions(tmp_path: Path):
    """Should spawn a detached worker-stop when this is the only active session."""
    base = tmp_path / "sessions"
    (base / "1001").mkdir(parents=True)

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    call = _find_call(mock_popen, "worker-service.cjs")
    assert call is not None, "worker-stop Popen never invoked"
    args, kwargs = call
    assert args[0][0] == "bun"
    # The worker script now lives under ~/.pilot/scripts/, no longer
    # ~/.claude/pilot/scripts/ — verify the new location explicitly.
    assert args[0][1].endswith("/.pilot/scripts/worker-service.cjs")
    assert args[0][-1] == "stop"
    assert kwargs["start_new_session"] is True
    assert kwargs["close_fds"] is True


def test_stops_worker_when_zero_sessions(tmp_path: Path):
    """Should spawn detached worker-stop even when no session dirs exist."""
    base = tmp_path / "sessions"
    base.mkdir(parents=True)

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
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
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
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
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
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
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch("session_end.subprocess.Popen", side_effect=OSError("bun not found")),
    ):
        # Should not raise
        assert session_end.main() == 0


# --- Session completion tests ---


def _posted_session_id(mock_popen: MagicMock) -> str:
    """Return the session id argv the detached Console-POST worker was given."""
    mock_popen.assert_called_once()
    args, _kwargs = mock_popen.call_args
    return args[0][-1]


def test_complete_session_uses_stdin_session_id():
    """Should POST the payload's session_id - the id session-init registered."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        session_end._complete_session({"session_id": "abc-123-def"})

    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    argv = args[0]
    assert argv[1] == "-c"
    assert argv[2] == session_end._COMPLETE_SESSION_WORKER
    assert argv[-2] == f"{session_end.get_console_url()}/api/sessions/complete"
    assert argv[-1] == "abc-123-def"
    assert kwargs["start_new_session"] is True
    assert kwargs["close_fds"] is True


def test_complete_session_falls_back_to_claude_code_session_id():
    """Claude Code exports CLAUDE_CODE_SESSION_ID, not CLAUDE_SESSION_ID."""
    with (
        patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "cc-session"}, clear=True),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        session_end._complete_session({})

    assert _posted_session_id(mock_popen) == "cc-session"


def test_complete_session_falls_back_to_codex_thread_id():
    """Last rung of the chain, kept for a future real Codex session-end event."""
    with (
        patch.dict(os.environ, {"CODEX_THREAD_ID": "codex-thread"}, clear=True),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        session_end._complete_session({})

    assert _posted_session_id(mock_popen) == "codex-thread"


def test_complete_session_prefers_stdin_over_env():
    """The payload is authoritative; env vars are only the fallback."""
    with (
        patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "from-env"}, clear=True),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        session_end._complete_session({"session_id": "from-stdin"})

    assert _posted_session_id(mock_popen) == "from-stdin"


def test_complete_session_ignores_pilot_session_id():
    """PILOT_SESSION_ID is the wrapper/PID id and never matches a contentSessionId.

    Posting it would look like it worked while the Console silently answered
    not_found - exactly the failure this hook already had.
    """
    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "51682"}, clear=True),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        session_end._complete_session({})

    mock_popen.assert_not_called()


def test_complete_session_skips_without_any_session_id():
    """Should do nothing when neither the payload nor the env chain yields an id."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        session_end._complete_session({})

    mock_popen.assert_not_called()


def test_complete_session_ignores_exec_errors():
    """Should not raise when spawning the worker fails."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("session_end.subprocess.Popen", side_effect=OSError("no python")),
    ):
        # Should not raise
        session_end._complete_session({"session_id": "abc-123"})


def test_main_skips_completion_without_session_end_flag(tmp_path: Path):
    """Codex runs this hook on every Stop; completing there aborts its SDK agent."""
    base = tmp_path / "sessions"
    base.mkdir(parents=True)

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001", "CODEX_THREAD_ID": "t-1"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch.object(session_end.sys, "argv", ["session_end.py"]),
        patch("session_end.read_hook_stdin", return_value={"session_id": "sid-1"}),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    assert _find_call(mock_popen, "/api/sessions/complete") is None
    # The worker-stop half is unconditional and must still fire.
    assert _find_call(mock_popen, "worker-service.cjs") is not None


def test_main_completes_session_with_session_end_flag(tmp_path: Path):
    """Claude Code's SessionEnd entry passes the flag, so completion runs."""
    base = tmp_path / "sessions"
    base.mkdir(parents=True)

    with (
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch.object(session_end.sys, "argv", ["session_end.py", "--session-end"]),
        patch("session_end.read_hook_stdin", return_value={"session_id": "sid-1"}),
        patch("session_end.subprocess.Popen") as mock_popen,
    ):
        result = session_end.main()

    assert result == 0
    call = _find_call(mock_popen, "/api/sessions/complete")
    assert call is not None, "Console POST never spawned"
    assert call[0][0][-1] == "sid-1"


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
        patch.dict(os.environ, {"PILOT_SESSION_ID": "1001"}),
        patch.object(session_end, "SESSIONS_DIR", base),
        patch.object(session_end.sys, "argv", ["session_end.py", "--session-end"]),
        patch("session_end.read_hook_stdin", return_value={"session_id": "session-xyz"}),
        patch("session_end.subprocess.Popen", side_effect=popen_side_effect),
    ):
        result = session_end.main()

    assert result == 0
    assert call_order == ["worker_stop", "console_post"]
