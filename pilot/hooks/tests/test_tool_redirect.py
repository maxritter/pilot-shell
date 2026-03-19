"""Tests for tool_redirect hook — blocks WebSearch/WebFetch/Explore/PlanMode, warns on general Agent calls."""

from __future__ import annotations

import json
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tool_redirect import run_tool_redirect

HOOK_PATH = Path(__file__).resolve().parent.parent / "tool_redirect.py"


def _run_with_input(tool_name: str, tool_input: dict | None = None) -> tuple[int, str]:
    """Simulate hook invocation via direct import. Returns (exit_code, stdout_output)."""
    hook_data: dict = {"tool_name": tool_name}
    if tool_input is not None:
        hook_data["tool_input"] = tool_input
    stdin = StringIO(json.dumps(hook_data))
    with patch("sys.stdin", stdin), patch("sys.stdout", new_callable=StringIO) as stdout:
        code = run_tool_redirect()
        return code, stdout.getvalue()


def _run_subprocess(tool_name: str, tool_input: dict | None = None) -> tuple[int, str, str]:
    """Run the hook as a subprocess. Returns (exit_code, stdout, stderr)."""
    hook_data: dict[str, object] = {"tool_name": tool_name}
    if tool_input:
        hook_data["tool_input"] = tool_input
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(hook_data),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def _is_denied(stdout: str) -> bool:
    """Check if the hook output contains a deny decision."""
    try:
        data = json.loads(stdout.strip())
        return data.get("permissionDecision") == "deny"
    except (json.JSONDecodeError, ValueError):
        return False


def _has_warning_context(stdout: str) -> bool:
    """Check if the hook output contains additionalContext (warning, not block)."""
    try:
        data = json.loads(stdout.strip())
        hook_output = data.get("hookSpecificOutput", {})
        return bool(hook_output.get("additionalContext"))
    except (json.JSONDecodeError, ValueError):
        return False


class TestBlockedTools:
    """Tests for tools that should be hard-blocked (exit code 2)."""

    def test_blocks_web_search(self):
        code, _ = _run_with_input("WebSearch", {"query": "python tutorial"})
        assert code == 2

    def test_blocks_web_fetch(self):
        code, _ = _run_with_input("WebFetch", {"url": "https://example.com"})
        assert code == 2

    def test_blocks_enter_plan_mode(self):
        """EnterPlanMode is blocked — conflicts with /spec workflow."""
        code, output = _run_with_input("EnterPlanMode")
        assert code == 2
        result = json.loads(output)
        assert result["permissionDecision"] == "deny"
        assert "/spec" in result["reason"]

    def test_blocks_exit_plan_mode(self):
        code, output = _run_with_input("ExitPlanMode")
        assert code == 2
        result = json.loads(output)
        assert result["permissionDecision"] == "deny"


class TestBlockedAgentTypes:
    """Agent types that should be hard-blocked (exit code 2)."""

    def test_blocks_explore_agent(self):
        code, output = _run_with_input("Agent", {"subagent_type": "Explore", "prompt": "find files"})
        assert code == 2
        assert "Probe CLI" in output
        assert "codebase-memory-mcp" in output

    def test_blocks_plan_agent(self):
        code, output = _run_with_input("Agent", {"subagent_type": "Plan", "prompt": "plan impl"})
        assert code == 2
        assert "/spec" in output


class TestAgentWarning:
    """General Agent calls are warned (not blocked) — exit code 0 with context."""

    def test_warns_agent_general_purpose(self):
        code, output = _run_with_input("Agent", {"subagent_type": "general-purpose", "prompt": "research"})
        assert code == 0
        assert "additionalContext" in output

    def test_warns_agent_without_subagent_type(self):
        code, output = _run_with_input("Agent", {"prompt": "do something"})
        assert code == 0
        assert "additionalContext" in output


class TestAllowedSpecReviewerAgents:
    """/spec reviewer agents pass through silently — no warning."""

    def test_allows_plan_reviewer(self):
        code, output = _run_with_input("Agent", {"subagent_type": "pilot:plan-reviewer", "prompt": "review plan"})
        assert code == 0
        assert output == ""

    def test_allows_spec_reviewer(self):
        code, output = _run_with_input("Agent", {"subagent_type": "pilot:spec-reviewer", "prompt": "review code"})
        assert code == 0
        assert output == ""


class TestAllowedTools:
    """Tests for tools that should pass through."""

    def test_allows_read(self):
        code, _ = _run_with_input("Read", {"file_path": "/foo.py"})
        assert code == 0

    def test_allows_write(self):
        code, _ = _run_with_input("Write", {"file_path": "/foo.py"})
        assert code == 0

    def test_allows_edit(self):
        code, _ = _run_with_input("Edit", {"file_path": "/foo.py"})
        assert code == 0

    def test_allows_bash(self):
        code, _ = _run_with_input("Bash", {"command": "ls"})
        assert code == 0

    def test_allows_grep(self):
        code, _ = _run_with_input("Grep", {"pattern": "where is config loaded"})
        assert code == 0

    def test_allows_task_create(self):
        code, _ = _run_with_input("TaskCreate", {"subject": "test"})
        assert code == 0

    def test_allows_bash_background(self):
        code, _ = _run_with_input("Bash", {"command": "npm run dev", "run_in_background": True})
        assert code == 0


class TestGrepPatterns:
    """Grep with both semantic and literal patterns passes through."""

    def test_grep_semantic_patterns_allowed(self):
        semantic_patterns = [
            "where is authentication handled",
            "how does the config loader work",
            "find the error handler",
            "locate the user validation",
            "what is the main entry point",
            "search for config files",
            "looking for authentication",
        ]
        for pattern in semantic_patterns:
            code, _ = _run_with_input("Grep", {"pattern": pattern})
            assert code == 0, f"Grep with pattern '{pattern}' should be allowed"

    def test_grep_literal_patterns_allowed(self):
        literal_patterns = [
            "def process_order",
            "class UserService",
            "import json",
            "TODO:",
            "FIXME",
            "config",
            "handler",
            "= None",
            "function handleClick",
            "const foo",
            "interface User",
        ]
        for pattern in literal_patterns:
            code, _ = _run_with_input("Grep", {"pattern": pattern})
            assert code == 0, f"Grep with literal pattern '{pattern}' should be allowed"


class TestEdgeCases:
    """Tests for malformed input and edge cases."""

    def test_handles_invalid_json(self):
        stdin = StringIO("not json")
        with patch("sys.stdin", stdin):
            assert run_tool_redirect() == 0

    def test_handles_empty_stdin(self):
        stdin = StringIO("")
        with patch("sys.stdin", stdin):
            assert run_tool_redirect() == 0

    def test_handles_missing_tool_name(self):
        stdin = StringIO(json.dumps({"tool_input": {}}))
        with patch("sys.stdin", stdin):
            assert run_tool_redirect() == 0


class TestSubprocessIntegration:
    """Subprocess-level tests — verify the hook works as a standalone process."""

    def test_websearch_blocked(self):
        exit_code, stdout, _ = _run_subprocess("WebSearch")
        assert exit_code == 2
        assert _is_denied(stdout)
        assert "WebSearch is blocked" in stdout

    def test_webfetch_blocked(self):
        exit_code, stdout, _ = _run_subprocess("WebFetch")
        assert exit_code == 2
        assert _is_denied(stdout)
        assert "WebFetch is blocked" in stdout

    def test_enter_plan_mode_blocked(self):
        exit_code, stdout, _ = _run_subprocess("EnterPlanMode")
        assert exit_code == 2
        assert _is_denied(stdout)
        assert "/spec" in stdout

    def test_exit_plan_mode_blocked(self):
        exit_code, stdout, _ = _run_subprocess("ExitPlanMode")
        assert exit_code == 2
        assert _is_denied(stdout)

    def test_other_tools_allowed(self):
        for tool in ["Read", "Write", "Bash", "Glob", "Edit"]:
            exit_code, stdout, _ = _run_subprocess(tool)
            assert exit_code == 0, f"{tool} should be allowed"
            assert not _is_denied(stdout)

    def test_agent_warned_not_blocked(self):
        exit_code, stdout, _ = _run_subprocess("Agent")
        assert exit_code == 0
        assert _has_warning_context(stdout)

    def test_spec_reviewers_silent(self):
        for subagent in ["pilot:spec-reviewer", "pilot:plan-reviewer"]:
            exit_code, stdout, _ = _run_subprocess("Agent", {"subagent_type": subagent})
            assert exit_code == 0
            assert not _is_denied(stdout)
            assert not _has_warning_context(stdout)

    def test_explore_agent_blocked(self):
        exit_code, stdout, _ = _run_subprocess("Agent", {"subagent_type": "Explore"})
        assert exit_code == 2
        assert "Probe CLI" in stdout
        assert "codebase-memory-mcp" in stdout

    def test_plan_agent_blocked(self):
        exit_code, stdout, _ = _run_subprocess("Agent", {"subagent_type": "Plan"})
        assert exit_code == 2
        assert "/spec" in stdout
