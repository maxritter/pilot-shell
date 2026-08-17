"""Tests for context_monitor hook — behavior at thresholds, throttling, caching, and standalone execution."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

from context_monitor import (
    _is_throttled,
    _read_codex_token_count_context,
    _resolve_context,
    run_context_monitor,
)


class TestContextMonitorAutocompact:
    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_autocompact_returns_0_with_additional_context(
        self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys
    ):
        mock_resolve.return_value = (91.0, 182000, False)

        result = run_context_monitor()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "hookSpecificOutput" in data
        assert data["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        assert "Auto-compact approaching" in data["hookSpecificOutput"]["additionalContext"]
        assert "Do NOT" not in data["hookSpecificOutput"]["additionalContext"]
        assert "sub-agents" not in data["hookSpecificOutput"]["additionalContext"]
        assert captured.err == ""

    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_autocompact_does_not_use_decision_block(self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys):
        mock_resolve.return_value = (91.0, 182000, False)

        run_context_monitor()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "decision" not in data


class TestContextMonitor80Warn:
    @patch("context_monitor.save_cache")
    @patch("context_monitor._get_pilot_session_id", return_value="test-sess")
    @patch("context_monitor._is_throttled", return_value=False)
    @patch("context_monitor._resolve_context")
    def test_warn_threshold_no_output_below_90_percent(self, mock_resolve, mock_throttle, mock_sid, mock_save, capsys):
        mock_resolve.return_value = (70.0, 140000, False)

        result = run_context_monitor()

        assert result == 0
        captured = capsys.readouterr()
        assert captured.out == ""


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
                    "tokens": 190000,
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

    def test_90_percent_shows_autocompact_warning(self, tmp_path: Path) -> None:
        import io

        session_id = "test-sess-42"
        session_base = tmp_path / "sessions" / session_id
        session_base.mkdir(parents=True)

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch("context_monitor._read_statusline_context_pct", return_value=91.0),
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
            assert "work can continue normally" in output
            assert exit_code == 0

    def test_autocompact_warning_is_not_repeated(self, tmp_path: Path) -> None:
        import io

        session_id = "test-sess-44"
        session_base = tmp_path / "sessions" / session_id
        session_base.mkdir(parents=True)
        cache_file = session_base / "context-cache.json"
        cache_file.write_text(
            json.dumps(
                {
                    "tokens": 160_000,
                    "timestamp": time.time() - 60,
                    "session_id": session_id,
                    "shown_autocompact_warn": True,
                }
            )
        )

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch("context_monitor._read_statusline_context_pct", return_value=91.0),
            patch("context_monitor.get_session_cache_path", return_value=cache_file),
        ):
            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                exit_code = run_context_monitor()
            finally:
                sys.stdout = old_stdout

        assert captured.getvalue() == ""
        assert exit_code == 0

    def test_89_percent_has_no_informational_message(self, tmp_path: Path) -> None:
        import io

        session_id = "test-sess-43"
        session_base = tmp_path / "sessions" / session_id
        session_base.mkdir(parents=True)
        cache_file = session_base / "context-cache.json"

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch("context_monitor._read_statusline_context_pct", return_value=89.0),
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
            assert output == ""
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


class TestRunContextMonitorOrchestrator:
    """Orchestrator-aware pct scaling has been removed (config schema v12).

    With per-skill model selection gone, the context monitor relies on the
    live statusline `context_window_size` alone — there is no separate
    orchestrator window to scale against. The remaining behavior in this
    class documents the post-v12 contract.
    """

    def test_run_context_monitor_does_not_scale_pct_post_v12(self, tmp_path: Path) -> None:
        """Even when a /spec plan is registered as PENDING, the hook reads the
        cached pct verbatim — there is no per-skill window scaling anymore."""
        import io

        session_id = "orch-test-no-scaling"
        session_dir = tmp_path / ".pilot" / "sessions" / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "context-pct.json").write_text(
            json.dumps({"pct": 30.0, "ts": time.time(), "context_window_size": 1_000_000})
        )

        plan_path = tmp_path / "docs" / "plans" / "2026-05-15-orch-fixture.md"
        plan_path.parent.mkdir(parents=True)
        plan_path.write_text(
            "# Orch Fixture Plan\n\nStatus: PENDING\nApproved: Yes\nType: Feature\n\n"
            "## Summary\n\nFixture for post-v12 contract.\n"
        )
        (session_dir / "active_plan.json").write_text(json.dumps({"plan_path": str(plan_path), "status": "PENDING"}))

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch.object(Path, "home", return_value=tmp_path),
            patch(
                "context_monitor.get_session_cache_path",
                return_value=session_dir / "context-cache.json",
            ),
        ):
            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                exit_code = run_context_monitor()
            finally:
                sys.stdout = old_stdout

            output = captured.getvalue()

        assert exit_code == 0
        # 30% on a 1M window is far below the AUTOCOMPACT threshold (75%) — no warning.
        assert "Auto-compact approaching" not in output


class TestPlanningLegModelWarning:
    """Per-turn detection of a silently downgraded /spec planning leg.

    Claude Code resolves `opusplan` to Opus only while `permissionMode == "plan"`
    AND the last assistant turn's usage is under 200K; past that it silently keeps
    serving Sonnet (anthropics/claude-code#74325, #65512). That crossover happens
    mid-planning, while the model is exploring - long after the plan file was last
    written - so the plan-doc-write anchor in plan_mode_tracker never observes it.
    Every tool call must re-check, which is why this hook (already registered on a
    broad PostToolUse matcher) carries the check.
    """

    @staticmethod
    def _downgraded_leg(tmp_path: Path, session_id: str, model_id: str, pct: float = 27.0) -> Path:
        """Planning leg whose statusline render post-dates EnterPlanMode."""
        session_dir = tmp_path / ".pilot" / "sessions" / session_id
        session_dir.mkdir(parents=True)
        sentinel = session_dir / "plan-mode-active"
        sentinel.write_text("")
        os.utime(sentinel, (1_000_000, 1_000_000))
        cache = session_dir / "context-pct.json"
        cache.write_text(
            json.dumps({"pct": pct, "ts": time.time(), "context_window_size": 1_000_000, "model_id": model_id})
        )
        os.utime(cache, (1_000_100, 1_000_100))
        return session_dir

    def _run(self, tmp_path: Path, session_dir: Path, session_id: str, throttled: bool = True) -> str:
        import io

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": session_id}),
            patch.object(Path, "home", return_value=tmp_path),
            patch("context_monitor.get_session_cache_path", return_value=session_dir / "context-cache.json"),
            patch("context_monitor._is_throttled", return_value=throttled),
            patch("plan_mode_tracker.read_model_switch_mode", return_value="automated"),
        ):
            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                assert run_context_monitor() == 0
            finally:
                sys.stdout = old_stdout
            return captured.getvalue()

    def test_warns_on_an_ordinary_tool_call_when_the_planning_leg_is_on_sonnet(self, tmp_path: Path) -> None:
        """The downgrade must surface without waiting for the next plan-doc write."""
        session_dir = self._downgraded_leg(tmp_path, "leg-sonnet", "claude-sonnet-5")

        output = self._run(tmp_path, session_dir, "leg-sonnet")

        context = json.loads(output)["hookSpecificOutput"]["additionalContext"]
        assert "NOT running on Opus" in context
        assert "claude-sonnet-5" in context
        assert (session_dir / "plan-model-warned").exists()

    def test_confirms_on_an_ordinary_tool_call_when_the_planning_leg_is_on_opus(self, tmp_path: Path) -> None:
        """A working switch must surface too - Claude Code announces nothing itself."""
        session_dir = self._downgraded_leg(tmp_path, "leg-opus", "claude-opus-5")

        context = json.loads(self._run(tmp_path, session_dir, "leg-opus"))["hookSpecificOutput"]["additionalContext"]
        assert "claude-opus-5" in context
        assert "NOT running on Opus" not in context
        assert (session_dir / "plan-model-confirmed").exists()

    def test_silent_outside_a_planning_leg(self, tmp_path: Path) -> None:
        """No plan-mode sentinel: nothing to verify, whatever the model is."""
        session_dir = self._downgraded_leg(tmp_path, "leg-none", "claude-sonnet-5")
        (session_dir / "plan-mode-active").unlink()

        assert self._run(tmp_path, session_dir, "leg-none") == ""

    def test_emits_one_json_object_when_autocompact_also_fires(self, tmp_path: Path) -> None:
        """Two `print`s would produce two concatenated objects and break the hook."""
        session_dir = self._downgraded_leg(tmp_path, "leg-both", "claude-sonnet-5", pct=93.0)

        output = self._run(tmp_path, session_dir, "leg-both", throttled=False)

        context = json.loads(output)["hookSpecificOutput"]["additionalContext"]
        assert "NOT running on Opus" in context
        assert "Auto-compact approaching" in context


class TestPlanningLegHookRegistration:
    """The per-turn guarantee is only as good as the matcher that fires the hook.

    The planning-leg check lives in this hook because it is registered on a broad
    PostToolUse matcher - so the matcher IS the guarantee. A named-tool list silently
    excludes whatever it forgot, and the tools it forgot last time were the MCP ones
    (`mcp__codegraph__*`, `mcp__semble__*`) that Pilot's own rules push the model
    toward during exactly the exploration phase where the 200K downgrade happens.
    """

    @staticmethod
    def _post_tool_use_matchers(registry: str) -> list[str]:
        config = json.loads((Path(__file__).resolve().parent.parent / registry).read_text())
        return [
            group.get("matcher", "")
            for group in config["hooks"]["PostToolUse"]
            if any("context_monitor.py" in hook["command"] for hook in group["hooks"])
        ]

    def test_claude_registry_fires_the_detector_on_every_tool(self) -> None:
        matchers = self._post_tool_use_matchers("hooks.json")

        assert matchers == ["*"], (
            f"context_monitor must match every PostToolUse tool, got {matchers!r}. "
            "A named list cannot express the guarantee: MCP tools, Agent and "
            "AskUserQuestion are all absent from one, and a planning leg can run "
            "many turns on those alone."
        )

    def test_codex_registry_does_not_spawn_context_monitor_per_tool(self) -> None:
        """Native Codex compaction makes the per-tool monitor redundant noise."""
        matchers = self._post_tool_use_matchers("codex_hooks.json")

        assert matchers == []


class TestCodexTranscriptTokenCount:
    """Context resolution from Codex token-count transcript events."""

    def test_reads_percentage_from_latest_token_count_event(self, tmp_path: Path) -> None:
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            json.dumps(
                {
                    "type": "event_msg",
                    "payload": {
                        "type": "token_count",
                        "info": {
                            "last_token_usage": {"input_tokens": 130_000, "output_tokens": 1_000},
                            "total_token_usage": {"input_tokens": 1_500_000},
                            "model_context_window": 258_400,
                        },
                    },
                }
            )
            + "\n"
        )

        result = _read_codex_token_count_context(str(transcript))

        assert result is not None
        pct, tokens = result
        assert 50 < pct < 51
        assert tokens == 131_000

    def test_ignores_transcript_size_when_token_count_is_low(self, tmp_path: Path) -> None:
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            "x" * 400_000
            + "\n"
            + json.dumps(
                {
                    "type": "event_msg",
                    "payload": {
                        "type": "token_count",
                        "info": {
                            "last_token_usage": {"input_tokens": 100_000, "output_tokens": 0},
                            "total_token_usage": {"input_tokens": 2_000_000},
                            "model_context_window": 258_400,
                        },
                    },
                }
            )
            + "\n"
        )

        result = _read_codex_token_count_context(str(transcript))

        assert result is not None
        pct, tokens = result
        assert 38 < pct < 39
        assert tokens == 100_000

    def test_returns_none_when_no_token_count_event_exists(self, tmp_path: Path) -> None:
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text("x" * 600_000)

        assert _read_codex_token_count_context(str(transcript)) is None

    def test_returns_none_for_missing_file(self) -> None:
        assert _read_codex_token_count_context("/nonexistent/path.jsonl") is None

    def test_returns_none_for_empty_path(self) -> None:
        assert _read_codex_token_count_context("") is None

    def test_resolve_context_falls_back_to_codex_token_count(self, tmp_path: Path) -> None:
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            json.dumps(
                {
                    "type": "event_msg",
                    "payload": {
                        "type": "token_count",
                        "info": {
                            "last_token_usage": {"input_tokens": 120_000, "output_tokens": 2_000},
                            "model_context_window": 258_400,
                        },
                    },
                }
            )
            + "\n"
        )
        session_id = "codex-test-sess"

        with patch("context_monitor._read_statusline_context_pct", return_value=None):
            result = _resolve_context(
                session_id,
                transcript_path=str(transcript),
                model="unknown-model",
            )

        assert result is not None
        pct, tokens, shown_80 = result
        assert 47 < pct < 48
        assert tokens == 122_000
        assert shown_80 is False
