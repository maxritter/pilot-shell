"""Claude SessionStart repair for display details lost to native auto-updates."""

from __future__ import annotations

import json
import signal
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from claude_display_patch_sync import repair_on_startup


def _manager(tmp_path: Path) -> Path:
    state = tmp_path / "state"
    state.mkdir()
    (state / "manager.py").write_text("# fixture")
    return state


def _completed(status: str, message: str = "result", returncode: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess([], returncode, json.dumps({"status": status, "message": message}), "")


def test_missing_manager_is_quiet(tmp_path: Path) -> None:
    assert repair_on_startup(tmp_path / "missing") == {}


def test_unchanged_and_unsupported_are_quiet(tmp_path: Path) -> None:
    state = _manager(tmp_path)
    for status in ("unchanged", "skipped"):
        with patch("claude_display_patch_sync._run_manager", return_value=_completed(status)):
            assert repair_on_startup(state) == {}


def test_repair_tells_current_claude_session_to_restart(tmp_path: Path) -> None:
    state = _manager(tmp_path)
    with patch("claude_display_patch_sync._run_manager", return_value=_completed("patched")):
        result = repair_on_startup(state)

    context = result["hookSpecificOutput"]["additionalContext"]
    assert "restart Claude Code once" in context
    assert "Ctrl+O" in context


def test_failure_warning_is_deduplicated_and_actionable(tmp_path: Path) -> None:
    state = _manager(tmp_path)
    completed = _completed("failed", "patch shape changed", returncode=1)
    with (
        patch("claude_display_patch_sync._repair_attempt_key", return_value="same-attempt"),
        patch("claude_display_patch_sync._run_manager", return_value=completed) as run,
    ):
        first = repair_on_startup(state)
        second = repair_on_startup(state)

    assert "pilot repair-display" in first["hookSpecificOutput"]["additionalContext"]
    assert second == {}
    assert run.call_count == 1


def test_invalid_manager_output_is_nonblocking(tmp_path: Path) -> None:
    state = _manager(tmp_path)
    completed = subprocess.CompletedProcess([], 1, "not-json", "trace")
    with patch("claude_display_patch_sync._run_manager", return_value=completed):
        result = repair_on_startup(state)

    assert "pilot repair-display" in result["hookSpecificOutput"]["additionalContext"]


def test_busy_repair_tells_second_session_to_restart(tmp_path: Path) -> None:
    state = _manager(tmp_path)
    with patch("claude_display_patch_sync._run_manager", return_value=_completed("busy")):
        result = repair_on_startup(state)

    assert "Another Claude Code session" in result["hookSpecificOutput"]["additionalContext"]


def test_manager_timeout_kills_process_group(monkeypatch) -> None:
    from claude_display_patch_sync import _run_manager

    class Process:
        pid = 42
        returncode = None

        def __init__(self):
            self.calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls == 1:
                assert timeout == 30
                raise subprocess.TimeoutExpired(["manager"], timeout)
            return "", ""

    process = Process()
    monkeypatch.setattr("claude_display_patch_sync.subprocess.Popen", lambda *args, **kwargs: process)
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr("claude_display_patch_sync.os.killpg", lambda pid, sig: killed.append((pid, sig)))

    with pytest.raises(subprocess.TimeoutExpired):
        _run_manager(["manager"])

    assert killed == [(42, signal.SIGKILL)]
