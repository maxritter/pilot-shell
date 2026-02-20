"""Tests for session_end hook — worker stop behavior."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import session_end


def test_returns_early_without_plugin_root():
    """Should return 0 when CLAUDE_PLUGIN_ROOT is not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
        result = session_end.main()

    assert result == 0


def test_skips_stop_when_other_sessions_active():
    """Should skip worker stop when other Pilot sessions are running."""
    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin"}),
        patch("session_end._get_active_session_count", return_value=2),
        patch("session_end.subprocess.run") as mock_run,
    ):
        result = session_end.main()

    assert result == 0
    mock_run.assert_not_called()


def test_stops_worker_when_no_other_sessions():
    """Should stop worker when this is the only active session."""
    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin"}),
        patch("session_end._get_active_session_count", return_value=1),
        patch("session_end.subprocess.run", return_value=MagicMock(returncode=0)) as mock_run,
    ):
        result = session_end.main()

    assert result == 0
    mock_run.assert_called_once()
    assert "stop" in str(mock_run.call_args)


def test_stops_worker_when_zero_sessions():
    """Should stop worker and return 0 when no sessions active."""
    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin"}),
        patch("session_end._get_active_session_count", return_value=0),
        patch("session_end.subprocess.run", return_value=MagicMock(returncode=0)) as mock_run,
    ):
        result = session_end.main()

    assert result == 0
    mock_run.assert_called_once()
