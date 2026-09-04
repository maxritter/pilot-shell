"""Installed-command E2E replay for Claude Code and Codex agent-asset hooks."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SOURCE_HOOKS = ROOT / "pilot" / "hooks"
SOURCE_CHECKER = ROOT / "pilot" / "skills" / "setup-rules" / "scripts" / "sync-agent-assets.mjs"


def _install_runtime(home: Path) -> tuple[Path, Path]:
    pilot = home / ".pilot"
    hooks = pilot / "hooks"
    hooks.mkdir(parents=True)
    run_if = hooks / "run_if_licensed.py"
    sync_hook = hooks / "repo_agent_sync.py"
    shutil.copy2(SOURCE_HOOKS / run_if.name, run_if)
    shutil.copy2(SOURCE_HOOKS / sync_hook.name, sync_hook)
    checker = pilot / "skills" / "setup-rules" / "scripts" / SOURCE_CHECKER.name
    checker.parent.mkdir(parents=True)
    shutil.copy2(SOURCE_CHECKER, checker)
    (pilot / ".license").write_text("e2e-test-license\n")
    return run_if, sync_hook


def _run_hook(run_if: Path, sync_hook: Path, repo: Path, platform: str, payload: dict) -> dict:
    env = os.environ.copy()
    env["HOME"] = str(run_if.parents[2])
    env["CLAUDE_PROJECT_PLATFORM"] = platform
    if platform == "codex":
        env["CODEX_THREAD_ID"] = "e2e-codex-thread"
        env.pop("CLAUDE_CODE_SESSION_ID", None)
    else:
        env["CLAUDE_CODE_SESSION_ID"] = "e2e-claude-session"
        env.pop("CODEX_THREAD_ID", None)
    completed = subprocess.run(
        [sys.executable, str(run_if), str(sync_hook)],
        cwd=repo,
        env=env,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    return json.loads(completed.stdout)


def _edit_payload(repo: Path, platform: str, event: str, relative_path: str) -> dict:
    if platform == "codex":
        tool_name = "apply_patch"
        tool_input = {"command": f"*** Begin Patch\n*** Update File: {relative_path}\n@@\n-old\n+new\n*** End Patch"}
    else:
        tool_name = "Write"
        tool_input = {"file_path": str(repo / relative_path), "content": "new\n"}
    return {
        "hook_event_name": event,
        "platform": platform,
        "cwd": str(repo),
        "session_id": f"e2e-{platform}",
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


@pytest.mark.skipif(shutil.which("node") is None or shutil.which("git") is None, reason="requires node and git")
@pytest.mark.parametrize("platform", ["claude", "codex"])
@pytest.mark.parametrize("scenario", ["incomplete_skill", "missing_rule_route"])
def test_installed_hook_chain_defers_transient_asset_errors_without_user_visible_blocks(
    tmp_path: Path,
    platform: str,
    scenario: str,
) -> None:
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    (repo / "AGENTS.md").write_text("# Shared instructions\n")
    (repo / "CLAUDE.md").write_text("@AGENTS.md\n")
    run_if, sync_hook = _install_runtime(home)

    if scenario == "incomplete_skill":
        relative_path = ".agents/skills/gws/notes.md"
        target = repo / relative_path
        expected = ".agents/skills/gws: SKILL.md is required"
    else:
        relative_path = ".claude/rules/assistant-project.md"
        target = repo / relative_path
        expected = "AGENTS.md is missing exact rule reference: .claude/rules/assistant-project.md"
    target.parent.mkdir(parents=True)
    target.write_text("# In-progress asset\n")

    pre = _run_hook(run_if, sync_hook, repo, platform, _edit_payload(repo, platform, "PreToolUse", relative_path))
    assert pre == ({"continue": True} if platform == "claude" else {})

    post = _run_hook(run_if, sync_hook, repo, platform, _edit_payload(repo, platform, "PostToolUse", relative_path))
    assert "decision" not in post
    assert "systemMessage" not in post
    assert expected in post["hookSpecificOutput"]["additionalContext"]
    if platform == "claude":
        assert post["continue"] is True
        assert post["suppressOutput"] is True
    else:
        assert "continue" not in post
        assert "suppressOutput" not in post

    stop = _run_hook(
        run_if,
        sync_hook,
        repo,
        platform,
        {
            "hook_event_name": "Stop",
            "platform": platform,
            "cwd": str(repo),
            "session_id": f"e2e-{platform}",
            "stop_hook_active": False,
        },
    )
    assert stop == {"continue": True}
