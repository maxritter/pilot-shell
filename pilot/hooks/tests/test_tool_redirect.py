"""Tests for tool_redirect hook — blocks WebSearch/WebFetch/Explore/PlanMode/research agents."""

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
        assert "CodeGraph" in output

    def test_blocks_plan_agent(self):
        code, output = _run_with_input("Agent", {"subagent_type": "Plan", "prompt": "plan impl"})
        assert code == 2
        assert "/spec" in output


class TestAgentPassthrough:
    """Non-blocked Agent calls pass through silently — no output."""

    def test_allows_agent_general_purpose(self):
        code, output = _run_with_input(
            "Agent", {"subagent_type": "general-purpose", "description": "Fix test failures", "prompt": "fix"}
        )
        assert code == 0
        assert output == ""

    def test_allows_agent_without_subagent_type(self):
        code, output = _run_with_input("Agent", {"description": "Run test suite", "prompt": "do something"})
        assert code == 0
        assert output == ""


class TestResearchAgentBlocked:
    """Agent with description starting with 'Research' is blocked."""

    def test_blocks_research_first_word(self):
        code, output = _run_with_input("Agent", {"description": "Research Extensions system", "prompt": "explore"})
        assert code == 2
        assert "codegraph_context" in output

    def test_blocks_research_case_insensitive(self):
        code, output = _run_with_input("Agent", {"description": "research codebase architecture", "prompt": "explore"})
        assert code == 2

    def test_allows_research_not_first_word(self):
        code, output = _run_with_input("Agent", {"description": "Find research papers", "prompt": "search"})
        assert code == 0
        assert output == ""

    def test_allows_research_midsentence(self):
        code, output = _run_with_input("Agent", {"description": "Do some research work", "prompt": "explore"})
        assert code == 0
        assert output == ""


class TestExploreDescriptionBlocked:
    """Agent with 'Explore' anywhere in description is blocked (regardless of subagent_type)."""

    def test_blocks_explore_first_word(self):
        code, output = _run_with_input(
            "Agent",
            {"subagent_type": "general-purpose", "description": "Explore console UI codebase", "prompt": "look around"},
        )
        assert code == 2
        assert "Probe" in output

    def test_blocks_explore_mid_sentence(self):
        code, output = _run_with_input("Agent", {"description": "Deep explore of auth module", "prompt": "search"})
        assert code == 2

    def test_blocks_explore_case_insensitive(self):
        code, output = _run_with_input("Agent", {"description": "EXPLORE the project structure", "prompt": "look"})
        assert code == 2

    def test_blocks_explore_no_subagent_type(self):
        code, output = _run_with_input(
            "Agent", {"description": "Explore and understand the codebase", "prompt": "look"}
        )
        assert code == 2

    def test_allows_non_explore_description(self):
        code, output = _run_with_input(
            "Agent", {"subagent_type": "general-purpose", "description": "Fix test failures", "prompt": "fix"}
        )
        assert code == 0
        assert output == ""


class TestAllowedSpecReviewerAgents:
    """/spec reviewer agents pass through silently — no warning."""

    def test_allows_spec_review(self):
        code, output = _run_with_input("Agent", {"subagent_type": "pilot:spec-review", "prompt": "review plan"})
        assert code == 0
        assert output == ""

    def test_allows_changes_review(self):
        code, output = _run_with_input("Agent", {"subagent_type": "pilot:changes-review", "prompt": "review code"})
        assert code == 0
        assert output == ""


class TestAllowedWebSearchAgents:
    """web-search-agent passes through silently — used by /prd deep research."""

    def test_allows_web_search_agent(self):
        code, output = _run_with_input(
            "Agent",
            {"subagent_type": "web-search-agent", "description": "Research competitor landscape", "prompt": "search"},
        )
        assert code == 0
        assert output == ""

    def test_allows_pilot_web_search_agent(self):
        code, output = _run_with_input(
            "Agent",
            {
                "subagent_type": "pilot:web-search-agent",
                "description": "Research technical approaches",
                "prompt": "search",
            },
        )
        assert code == 0
        assert output == ""

    def test_web_search_agent_bypasses_research_pattern(self):
        """web-search-agent with 'Research' description must NOT be blocked."""
        code, output = _run_with_input(
            "Agent",
            {
                "subagent_type": "web-search-agent",
                "description": "Research UX patterns for onboarding",
                "prompt": "search",
            },
        )
        assert code == 0
        assert output == ""

    def test_web_search_agent_bypasses_explore_pattern(self):
        """web-search-agent with 'Explore' description must NOT be blocked."""
        code, output = _run_with_input(
            "Agent",
            {"subagent_type": "web-search-agent", "description": "Explore competitor landscape", "prompt": "search"},
        )
        assert code == 0
        assert output == ""

    def test_spec_review_bypasses_explore_pattern(self):
        """spec-review with 'Explore' description must NOT be blocked."""
        code, output = _run_with_input(
            "Agent",
            {"subagent_type": "pilot:spec-review", "description": "Explore alignment with spec", "prompt": "review"},
        )
        assert code == 0
        assert output == ""

    def test_changes_review_bypasses_explore_pattern(self):
        """changes-review with 'Explore' description must NOT be blocked."""
        code, output = _run_with_input(
            "Agent",
            {"subagent_type": "pilot:changes-review", "description": "Explore code changes", "prompt": "review"},
        )
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

    def test_agent_passthrough_silent(self):
        exit_code, stdout, _ = _run_subprocess("Agent", {"description": "Fix test suite"})
        assert exit_code == 0
        assert stdout.strip() == ""

    def test_research_agent_blocked(self):
        exit_code, stdout, _ = _run_subprocess("Agent", {"description": "Research API design"})
        assert exit_code == 2
        assert _is_denied(stdout)

    def test_spec_reviewers_silent(self):
        for subagent in ["pilot:changes-review", "pilot:spec-review"]:
            exit_code, stdout, _ = _run_subprocess("Agent", {"subagent_type": subagent})
            assert exit_code == 0
            assert not _is_denied(stdout)
            assert not _has_warning_context(stdout)

    def test_explore_agent_blocked(self):
        exit_code, stdout, _ = _run_subprocess("Agent", {"subagent_type": "Explore"})
        assert exit_code == 2
        assert "Probe CLI" in stdout
        assert "CodeGraph" in stdout

    def test_plan_agent_blocked(self):
        exit_code, stdout, _ = _run_subprocess("Agent", {"subagent_type": "Plan"})
        assert exit_code == 2
        assert "/spec" in stdout

    def test_explore_description_blocked(self):
        exit_code, stdout, _ = _run_subprocess(
            "Agent", {"subagent_type": "general-purpose", "description": "Explore console UI codebase"}
        )
        assert exit_code == 2
        assert _is_denied(stdout)
        assert "Probe" in stdout

    def test_web_search_agent_allowed_with_research_description(self):
        exit_code, stdout, _ = _run_subprocess(
            "Agent", {"subagent_type": "web-search-agent", "description": "Research competitor landscape"}
        )
        assert exit_code == 0
        assert not _is_denied(stdout)

    def test_web_search_agent_allowed_with_explore_description(self):
        exit_code, stdout, _ = _run_subprocess(
            "Agent", {"subagent_type": "web-search-agent", "description": "Explore alternatives"}
        )
        assert exit_code == 0
        assert not _is_denied(stdout)
