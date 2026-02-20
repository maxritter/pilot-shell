"""Tests for context_monitor hook — behavior at thresholds and internal helpers."""

from __future__ import annotations

import json
import time
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
        mock_resolve.return_value = (80.0, 160000, [], False)

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
        mock_resolve.return_value = (80.0, 160000, [], False)

        run_context_monitor()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "decision" not in data


class TestContextMonitorLearnReminder:
    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_learn_reminder_uses_additional_context(self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys):
        mock_resolve.return_value = (45.0, 90000, [], False)

        result = run_context_monitor()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "hookSpecificOutput" in data
        assert "Skill(learn)" in data["hookSpecificOutput"]["additionalContext"]


class TestContextMonitor80Warn:
    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_80_warn_uses_additional_context(self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys):
        mock_resolve.return_value = (70.0, 140000, [40, 55, 65], False)

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
        mock_resolve.return_value = (20.0, 40000, [], False)

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
        """Throttle returns True when last check was < 30s ago and context below warning threshold."""
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        session_id = "test-session-123"
        cache_file.write_text(json.dumps({
            "session_id": session_id,
            "tokens": 100000,
            "timestamp": time.time() - 5,
        }))

        assert _is_throttled(session_id) is True

    def test_throttle_allows_when_high_context(self, tmp_path, monkeypatch):
        """Throttle returns False when context is high (never skip near compaction)."""
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        session_id = "test-session-123"
        cache_file.write_text(json.dumps({
            "session_id": session_id,
            "tokens": 170000,
            "timestamp": time.time() - 5,
        }))

        assert _is_throttled(session_id) is False

    def test_throttle_allows_when_stale_timestamp(self, tmp_path, monkeypatch):
        """Throttle returns False when last check was > 30s ago."""
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        session_id = "test-session-123"
        cache_file.write_text(json.dumps({
            "session_id": session_id,
            "tokens": 100000,
            "timestamp": time.time() - 35,
        }))

        assert _is_throttled(session_id) is False

    def test_throttle_allows_when_no_cache(self, tmp_path, monkeypatch):
        """Throttle returns False when no cache file exists."""
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        assert _is_throttled("test-session-123") is False

    def test_throttle_allows_when_different_session(self, tmp_path, monkeypatch):
        """Throttle returns False when cache is for a different session."""
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

        cache_file.write_text(json.dumps({
            "session_id": "other-session-456",
            "tokens": 100000,
            "timestamp": time.time() - 5,
        }))

        assert _is_throttled("test-session-123") is False




class TestResolveContext:
    """Tests for context resolution from statusline cache."""

    def test_returns_none_when_statusline_cache_missing(self, tmp_path, monkeypatch):
        """Returns None when no statusline cache exists (no racy fallback)."""
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)
        monkeypatch.setattr("context_monitor._read_statusline_context_pct", lambda: None)

        result = _resolve_context("test-session-123")

        assert result is None

    def test_returns_statusline_percentage(self, tmp_path, monkeypatch):
        """Returns percentage from statusline cache when available."""
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)
        monkeypatch.setattr("context_monitor._read_statusline_context_pct", lambda: 45.0)

        result = _resolve_context("test-session-123")

        assert result is not None
        pct, tokens, shown_learn, shown_80 = result
        assert pct == 45.0
        assert tokens == 90000
        assert shown_learn == []
        assert shown_80 is False

    def test_includes_session_flags(self, tmp_path, monkeypatch):
        """Returns session flags (learn thresholds, 80% warning) from cache."""
        cache_file = tmp_path / "context_cache.json"
        monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)
        monkeypatch.setattr("context_monitor._read_statusline_context_pct", lambda: 85.0)

        session_id = "test-session-123"
        cache_file.write_text(json.dumps({
            "session_id": session_id,
            "tokens": 170000,
            "timestamp": time.time() - 5,
            "shown_learn": [40, 60],
            "shown_80_warn": True,
        }))

        result = _resolve_context(session_id)

        assert result is not None
        pct, tokens, shown_learn, shown_80 = result
        assert pct == 85.0
        assert tokens == 170000
        assert shown_learn == [40, 60]
        assert shown_80 is True
