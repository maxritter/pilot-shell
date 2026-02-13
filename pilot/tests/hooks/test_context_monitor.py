"""Tests for context_monitor throttling and context resolution."""

import json
import time

from context_monitor import _is_throttled, _resolve_context


def test_throttle_skips_when_recent_and_low_context(tmp_path, monkeypatch):
    """Throttle returns True when last check was < 30s ago and context < 80%."""
    cache_file = tmp_path / "context_cache.json"
    monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

    session_id = "test-session-123"
    cache_file.write_text(json.dumps({
        "session_id": session_id,
        "tokens": 100000,
        "timestamp": time.time() - 5,
    }))

    assert _is_throttled(session_id) is True


def test_throttle_allows_when_high_context(tmp_path, monkeypatch):
    """Throttle returns False when context >= 80% (never skip high context)."""
    cache_file = tmp_path / "context_cache.json"
    monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

    session_id = "test-session-123"
    cache_file.write_text(json.dumps({
        "session_id": session_id,
        "tokens": 170000,
        "timestamp": time.time() - 5,
    }))

    assert _is_throttled(session_id) is False


def test_throttle_allows_when_stale_timestamp(tmp_path, monkeypatch):
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


def test_throttle_allows_when_no_cache(tmp_path, monkeypatch):
    """Throttle returns False when no cache file exists."""
    cache_file = tmp_path / "context_cache.json"
    monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

    assert _is_throttled("test-session-123") is False


def test_throttle_allows_when_different_session(tmp_path, monkeypatch):
    """Throttle returns False when cache is for a different session."""
    cache_file = tmp_path / "context_cache.json"
    monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)

    cache_file.write_text(json.dumps({
        "session_id": "other-session-456",
        "tokens": 100000,
        "timestamp": time.time() - 5,
    }))

    assert _is_throttled("test-session-123") is False




def test_resolve_context_returns_none_when_statusline_cache_missing(tmp_path, monkeypatch):
    """Returns None when no statusline cache exists (no racy fallback)."""
    cache_file = tmp_path / "context_cache.json"
    monkeypatch.setattr("context_monitor.get_session_cache_path", lambda: cache_file)
    monkeypatch.setattr("context_monitor._read_statusline_context_pct", lambda: None)

    result = _resolve_context("test-session-123")

    assert result is None


def test_resolve_context_returns_statusline_percentage(tmp_path, monkeypatch):
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


def test_resolve_context_includes_session_flags(tmp_path, monkeypatch):
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
