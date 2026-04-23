"""Tests for context_monitor hook — behavior at thresholds, throttling, caching, and standalone execution."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

from context_monitor import _is_throttled, _resolve_context, run_context_monitor


class TestContextMonitorAutocompact:
    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_autocompact_returns_0_with_additional_context(
        self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys
    ):
        mock_resolve.return_value = (80.0, 160000, False)

        result = run_context_monitor()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "hookSpecificOutput" in data
        assert data["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        assert "Auto-compact approaching" in data["hookSpecificOutput"]["additionalContext"]
        assert captured.err == ""

    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_autocompact_does_not_use_decision_block(self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys):
        mock_resolve.return_value = (80.0, 160000, False)

        run_context_monitor()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "decision" not in data


class TestContextMonitor80Warn:
    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_80_warn_uses_additional_context(self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys):
        mock_resolve.return_value = (70.0, 140000, False)

        result = run_context_monitor()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "hookSpecificOutput" in data
        assert "Auto-compact will handle" in data["hookSpecificOutput"]["additionalContext"]


class TestContextMonitorBelowThreshold:
    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_below_threshold_no_output(self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys):
        mock_resolve.return_value = (20.0, 40000, False)

        result = run_context_monitor()

        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=True)
    def test_throttled_no_output(self, mock_throttle, mock_sid, capsys):
        result = run_context_monitor()

        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context", return_value=None)
    def test_no_context_data_no_output(self, mock_resolve, mock_throttle, mock_sid, capsys):
        result = run_context_monitor()

        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""


class TestIsThrottled:
    """Tests for throttle logic based on cache freshness and context level."""

    def test_throttle_skips_when_recent_and_low_context(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        session_id = "test-session-123"
        cache_file.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "tokens": 100000,
                    "timestamp": time.time() - 5,
                }
            )
        )

        assert _is_throttled(session_id) is True

    def test_throttle_allows_when_high_context(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)
        monkeypatch.setattr("context_monitor._get_max_context_tokens", lambda: 200_000)

        session_id = "test-session-123"
        cache_file.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "tokens": 170000,
                    "timestamp": time.time() - 5,
                }
            )
        )

        assert _is_throttled(session_id) is False

    def test_throttle_allows_when_stale_timestamp(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        session_id = "test-session-123"
        cache_file.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "tokens": 100000,
                    "timestamp": time.time() - 35,
                }
            )
        )

        assert _is_throttled(session_id) is False

    def test_throttle_allows_when_no_cache(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        assert _is_throttled("test-session-123") is False

    def test_throttle_allows_when_different_session(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        cache_file.write_text(
            json.dumps(
                {
                    "session_id": "other-session-456",
                    "tokens": 100000,
                    "timestamp": time.time() - 5,
                }
            )
        )

        assert _is_throttled("test-session-123") is False


class TestResolveContext:
    """Tests for context resolution from statusline cache."""

    def test_returns_none_when_statusline_cache_missing(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)
        monkeypatch.setattr("context_monitor._read_statusline_context_pct", lambda: None)

        result = _resolve_context("test-session-123")
        assert result is None

    def test_returns_statusline_percentage(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)
        monkeypatch.setattr("context_monitor._read_statusline_context_pct", lambda: 45.0)
        monkeypatch.setattr("context_monitor._get_max_context_tokens", lambda: 200_000)

        result = _resolve_context("test-session-123")

        assert result is not None
        pct, tokens, shown_80 = result
        assert pct == 45.0
        assert tokens == 90000
        assert shown_80 is False

    def test_includes_session_flags(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)
        monkeypatch.setattr("context_monitor._read_statusline_context_pct", lambda: 85.0)
        monkeypatch.setattr("context_monitor._get_max_context_tokens", lambda: 200_000)

        session_id = "test-session-123"
        cache_file.write_text(
            json.dumps(
                {
                    "session_id": session_id,
                    "tokens": 170000,
                    "timestamp": time.time() - 5,
                    "shown_80_warn": True,
                }
            )
        )

        result = _resolve_context(session_id)

        assert result is not None
        pct, tokens, shown_80 = result
        assert pct == 85.0
        assert tokens == 170000
        assert shown_80 is True


class TestResolveContextStatuslineIntegration:
    """Tests for statusline cache preference and staleness handling."""

    def test_uses_statusline_cache_when_available(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / ".pilot" / "sessions" / "12345"
        cache_dir.mkdir(parents=True)
        (cache_dir / "context-pct.json").write_text(json.dumps({"pct": 91.5, "ts": time.time()}))

        session_cache = cache_dir / "context-cache.json"

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": "12345"}),
            patch.object(Path, "home", return_value=tmp_path),
            patch("context_monitor.get_session_cache_path", return_value=session_cache),
        ):
            result = _resolve_context("cc-session-id")

        assert result is not None
        pct, _, _ = result
        assert pct == 91.5

    def test_ignores_stale_statusline_cache(self, tmp_path: Path) -> None:
        cache_dir = tmp_path / ".pilot" / "sessions" / "12345"
        cache_dir.mkdir(parents=True)
        (cache_dir / "context-pct.json").write_text(json.dumps({"pct": 91.5, "ts": time.time() - 120}))

        session_cache = cache_dir / "context-cache.json"

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": "12345"}),
            patch.object(Path, "home", return_value=tmp_path),
            patch("context_monitor.get_session_cache_path", return_value=session_cache),
            patch("context_monitor._read_statusline_context_pct", return_value=None),
        ):
            result = _resolve_context("cc-session-id")

        assert result is None

    def test_accepts_cache_regardless_of_claude_session_id(self, tmp_path: Path) -> None:
        """Cross-session validation was removed — PILOT_SESSION_ID scoping is sufficient."""
        cache_dir = tmp_path / ".pilot" / "sessions" / "12345"
        cache_dir.mkdir(parents=True)
        (cache_dir / "context-pct.json").write_text(
            json.dumps({"pct": 92.0, "ts": time.time(), "session_id": "old-cc-session"})
        )

        session_cache = cache_dir / "context-cache.json"

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": "12345"}),
            patch.object(Path, "home", return_value=tmp_path),
            patch("context_monitor.get_session_cache_path", return_value=session_cache),
        ):
            result = _resolve_context("12345")

        assert result is not None
        pct, _, _ = result
        assert pct == 92.0

    def test_accepts_cache_without_session_id_field(self, tmp_path: Path) -> None:
        """Backwards compat: cache without session_id field should still be accepted."""
        cache_dir = tmp_path / ".pilot" / "sessions" / "12345"
        cache_dir.mkdir(parents=True)
        (cache_dir / "context-pct.json").write_text(json.dumps({"pct": 75.0, "ts": time.time()}))

        session_cache = cache_dir / "context-cache.json"

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": "12345"}),
            patch.object(Path, "home", return_value=tmp_path),
            patch("context_monitor.get_session_cache_path", return_value=session_cache),
        ):
            result = _resolve_context("any-cc-session")

        assert result is not None
        pct, _, _ = result
        assert pct == 75.0

    def test_returns_none_when_no_cache_and_no_statusline(self, tmp_path: Path) -> None:
        session_cache = tmp_path / "context-cache.json"

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": ""}),
            patch.object(Path, "home", return_value=tmp_path),
            patch("context_monitor.get_session_cache_path", return_value=session_cache),
            patch("context_monitor._read_statusline_context_pct", return_value=None),
        ):
            result = _resolve_context("cc-session-id")

        assert result is None


class TestSessionCachePath:
    """Test get_session_cache_path() from _lib.util."""

    def test_returns_session_scoped_path(self, tmp_path: Path) -> None:
        import _lib.util as _util_mod
        from _lib.util import get_session_cache_path

        with patch.dict(os.environ, {"PILOT_SESSION_ID": "12345"}):
            original = _util_mod._sessions_base
            try:
                _util_mod._sessions_base = lambda: tmp_path / "sessions"
                result = get_session_cache_path()
                assert result == tmp_path / "sessions" / "12345" / "context-cache.json"
            finally:
                _util_mod._sessions_base = original

    def test_falls_back_to_default(self, tmp_path: Path) -> None:
        import _lib.util as _util_mod
        from _lib.util import get_session_cache_path

        with patch.dict(os.environ, {}, clear=True):
            original = _util_mod._sessions_base
            try:
                _util_mod._sessions_base = lambda: tmp_path / "sessions"
                result = get_session_cache_path()
                assert result == tmp_path / "sessions" / "default" / "context-cache.json"
            finally:
                _util_mod._sessions_base = original

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        import _lib.util as _util_mod
        from _lib.util import get_session_cache_path

        original = _util_mod._sessions_base
        try:
            _util_mod._sessions_base = lambda: tmp_path / "sessions"
            with patch.dict(os.environ, {"PILOT_SESSION_ID": "777"}):
                result = get_session_cache_path()
                assert result.parent.is_dir()
        finally:
            _util_mod._sessions_base = original


class TestAutoCompactWarningIntegration:
    """Integration tests for auto-compact warnings using run_context_monitor."""

    def test_75_percent_shows_autocompact_warning(self, tmp_path: Path) -> None:
        import io

        session_id = "test-sess-42"
        session_base = tmp_path / "sessions" / session_id
        session_base.mkdir(parents=True)

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch("context_monitor._read_statusline_context_pct", return_value=76.0),
            patch("context_monitor.get_session_cache_path", return_value=session_base / "context-cache.json"),
        ):
            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                exit_code = run_context_monitor()
            finally:
                sys.stdout = old_stdout

            output = captured.getvalue()
            assert "Auto-compact approaching" in output
            assert "no context is lost" in output
            assert exit_code == 0

    def test_65_percent_shows_informational_message(self, tmp_path: Path) -> None:
        import io

        session_id = "test-sess-43"
        session_base = tmp_path / "sessions" / session_id
        session_base.mkdir(parents=True)
        cache_file = session_base / "context-cache.json"

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch("context_monitor._read_statusline_context_pct", return_value=66.0),
            patch("context_monitor.get_session_cache_path", return_value=cache_file),
        ):
            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                exit_code = run_context_monitor()
            finally:
                sys.stdout = old_stdout

            output = captured.getvalue()
            assert "Auto-compact will handle context automatically" in output
            assert exit_code == 0


class TestCacheAlwaysSavedAfterResolve:
    """Cache must be saved after every resolve, not just at threshold crossings."""

    def test_cache_updated_between_thresholds(self, tmp_path: Path) -> None:
        import io

        session_id = "cache-test"
        session_base = tmp_path / "sessions" / session_id
        session_base.mkdir(parents=True)
        cache_file = session_base / "context-cache.json"

        cache_file.write_text(
            json.dumps(
                {
                    "tokens": 60000,
                    "timestamp": time.time() - 60,
                    "session_id": session_id,
                    "shown_80_warn": False,
                }
            )
        )

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch("context_monitor._read_statusline_context_pct", return_value=55.0),
            patch("context_monitor.get_session_cache_path", return_value=cache_file),
            patch("context_monitor._get_max_context_tokens", return_value=200_000),
        ):
            captured = io.StringIO()
            old_stderr = sys.stderr
            sys.stderr = captured
            try:
                run_context_monitor()
            finally:
                sys.stderr = old_stderr

        cache_data = json.loads(cache_file.read_text())
        assert cache_data["tokens"] == 110000

    def test_stale_cache_uses_fresh_statusline(self, tmp_path: Path) -> None:
        session_id = "stale-test"
        session_base = tmp_path / "sessions" / session_id
        session_base.mkdir(parents=True)
        cache_file = session_base / "context-cache.json"

        cache_file.write_text(
            json.dumps(
                {
                    "tokens": 100000,
                    "timestamp": time.time() - 10,
                    "session_id": session_id,
                    "shown_80_warn": False,
                }
            )
        )

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch("context_monitor._read_statusline_context_pct", return_value=90.0),
            patch("context_monitor.get_session_cache_path", return_value=cache_file),
        ):
            result = _resolve_context(session_id)

        assert result is not None
        pct, _, _ = result
        assert pct >= 89.0


class TestStandaloneExecution:
    """Test that context_monitor.py can be executed as a standalone script."""

    def test_no_import_errors_when_run_standalone(self) -> None:
        script = Path(__file__).resolve().parent.parent / "context_monitor.py"
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            env={**os.environ, "PILOT_SESSION_ID": ""},
            timeout=5,
        )
        assert "ImportError" not in result.stderr
        assert "ModuleNotFoundError" not in result.stderr
