"""Codex hook manifest stays quiet, non-blocking, and lifecycle-correct."""

from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "codex_hooks.json"


def _commands(event: list[dict]) -> list[dict]:
    return [hook for entry in event for hook in entry.get("hooks", [])]


def test_codex_hooks_do_not_gate_sessions_or_initialize_repositories() -> None:
    hooks = json.loads(MANIFEST.read_text())["hooks"]
    startup = _commands(hooks["SessionStart"])
    commands = [hook["command"] for hook in startup]

    assert not any("license_check.py" in command for command in commands)
    assert not any("codegraph_init.py" in command for command in commands)


def test_codex_bookkeeping_uses_native_async_commands() -> None:
    hooks = json.loads(MANIFEST.read_text())["hooks"]

    startup_sync = next(hook for hook in _commands(hooks["SessionStart"]) if "codex_skill_sync.py" in hook["command"])
    session_init = next(hook for hook in _commands(hooks["UserPromptSubmit"]) if "session-init" in hook["command"])
    observation = next(hook for hook in _commands(hooks["PostToolUse"]) if "observation" in hook["command"])
    summary = next(hook for hook in _commands(hooks["Stop"]) if "summarize" in hook["command"])

    for hook in (startup_sync, session_init, observation, summary):
        assert hook["async"] is True
        assert "codex_background.py" not in hook["command"]


def test_codex_post_tool_hooks_do_not_inject_workflow_reminders() -> None:
    hooks = json.loads(MANIFEST.read_text())["hooks"]
    commands = [hook["command"] for hook in _commands(hooks["PostToolUse"])]

    assert not any("file_checker.py" in command for command in commands)
    assert not any("context_monitor.py" in command for command in commands)


def test_stop_hooks_cover_workflow_and_repository_invariants() -> None:
    hooks = json.loads(MANIFEST.read_text())["hooks"]
    stop_hooks = _commands(hooks["Stop"])
    stop_commands = [hook["command"] for hook in stop_hooks]

    assert stop_commands[0] == 'uv run --no-project --python python3 python "$HOME/.pilot/hooks/spec_stop_guard.py"'
    assert len(stop_commands) == 3
    repo_sync = next(hook for hook in stop_hooks if "repo_agent_sync.py" in hook["command"])
    assert "async" not in repo_sync
    assert repo_sync["timeout"] == 45
    summary = next(hook for hook in stop_hooks if "summarize" in hook["command"])
    assert summary["async"] is True
    assert "codex_background.py" not in summary["command"]
    assert not any("session_end.py" in command or "auto-export" in command for command in stop_commands)


def test_completion_runs_once_within_codex_session_end_timeout() -> None:
    hooks = json.loads(MANIFEST.read_text())["hooks"]
    session_end_hooks = _commands(hooks["SessionEnd"])
    session_end_commands = [hook["command"] for hook in session_end_hooks]

    assert session_end_commands == [
        'uv run --no-project --python python3 python "$HOME/.pilot/hooks/session_end.py" --session-end'
    ]
    assert session_end_hooks[0]["timeout"] == 3


def test_control_and_context_hooks_remain_synchronous() -> None:
    hooks = json.loads(MANIFEST.read_text())["hooks"]
    synchronous_commands = (
        "repo_agent_sync.py",
        "spec_stop_guard.py",
        "hook codex context",
        "session_clear.py",
        "post_compact_restore.py",
        "tool_token_saver.py",
        "session_end.py",
        "pre_compact.py",
    )

    selected = [
        hook
        for event in hooks.values()
        for hook in _commands(event)
        if any(command in hook["command"] for command in synchronous_commands)
    ]
    assert selected
    assert all("async" not in hook for hook in selected)
