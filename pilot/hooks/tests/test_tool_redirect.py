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


class TestDangerousGitBlock:
    """Dangerous-git pattern check on Bash commands.

    The hook denies only TRULY irreversible variants (force push, mirror, colon-delete,
    hard reset, force clean, force-delete branch, destructive checkout/restore).
    Plain `git push` and `git commit` are NOT denied — pilot's social rule already
    requires explicit user authorization.
    """

    @staticmethod
    def _bash(command: str) -> tuple[int, str]:
        return _run_with_input("Bash", {"command": command})

    # ---- Block (deny) cases — irreversible variants ----

    def test_blocks_git_push_force_long(self):
        code, output = self._bash("git push --force origin main")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_push_force_short(self):
        code, output = self._bash("git push -f origin main")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_push_force_with_lease(self):
        code, output = self._bash("git push --force-with-lease origin main")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_push_mirror(self):
        code, output = self._bash("git push --mirror origin")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_push_remote_branch_delete(self):
        code, output = self._bash("git push origin :old-feature")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_reset_hard(self):
        code, output = self._bash("git reset --hard HEAD~1")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_clean_f(self):
        code, output = self._bash("git clean -f")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_clean_fd(self):
        code, output = self._bash("git clean -fd")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_branch_force_delete(self):
        code, output = self._bash("git branch -D feature")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_checkout_dot(self):
        code, output = self._bash("git checkout .")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_checkout_dashdash_file(self):
        code, output = self._bash("git checkout -- file.py")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_checkout_head_dashdash_file(self):
        code, output = self._bash("git checkout HEAD -- file.py")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_restore_dot(self):
        code, output = self._bash("git restore .")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_restore_worktree_combined(self):
        code, output = self._bash("git restore --staged --worktree .")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_dash_C_push_force(self):
        """`git -C path push --force` must normalize and deny."""
        code, output = self._bash("git -C /repo push --force origin main")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_dash_c_push_force(self):
        """`git -c key=val push --force` must normalize and deny."""
        code, output = self._bash("git -c core.sshCommand=foo push --force origin main")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_bash_wrapped_force_push(self):
        """`bash -c '...'` wrapping does not bypass — pattern matches the substring."""
        code, output = self._bash('bash -c "git push --force origin main"')
        assert code == 2
        assert _is_denied(output)

    # ---- Pass-through (safe) cases ----

    def test_passes_git_status(self):
        code, _ = self._bash("git status")
        assert code == 0

    def test_passes_git_diff(self):
        code, _ = self._bash("git diff HEAD")
        assert code == 0

    def test_passes_git_log(self):
        code, _ = self._bash("git log --oneline -10")
        assert code == 0

    def test_passes_git_pull(self):
        code, _ = self._bash("git pull origin main")
        assert code == 0

    def test_passes_git_fetch(self):
        code, _ = self._bash("git fetch origin")
        assert code == 0

    def test_passes_git_commit(self):
        code, _ = self._bash('git commit -m "fix: foo"')
        assert code == 0

    def test_passes_git_push_plain(self):
        """Plain `git push` is NOT denied — pilot's social rule covers authorization."""
        code, _ = self._bash("git push")
        assert code == 0

    def test_passes_git_push_origin_main(self):
        code, _ = self._bash("git push origin main")
        assert code == 0

    def test_passes_git_push_upstream(self):
        code, _ = self._bash("git push -u origin feature")
        assert code == 0

    def test_passes_git_push_tags(self):
        """`--tags` is additive, not destructive."""
        code, _ = self._bash("git push --tags origin")
        assert code == 0

    def test_passes_git_push_dry_run(self):
        """`--dry-run` is read-only across all git commands."""
        code, _ = self._bash("git push --dry-run origin main")
        assert code == 0

    def test_passes_git_push_force_dry_run(self):
        """`--dry-run` makes even force-push non-destructive — preview only."""
        code, _ = self._bash("git push --force --dry-run origin main")
        assert code == 0

    def test_passes_git_checkout_branch_name(self):
        code, _ = self._bash("git checkout main")
        assert code == 0

    def test_passes_git_restore_staged(self):
        """`--staged` only unstages; working tree untouched."""
        code, _ = self._bash("git restore --staged .")
        assert code == 0

    def test_passes_git_restore_file(self):
        """File-scoped restore — explicit path, not the destructive `.` form."""
        code, _ = self._bash("git restore src/config.py")
        assert code == 0

    def test_passes_git_restore_patch(self):
        code, _ = self._bash("git restore --patch README.md")
        assert code == 0

    def test_passes_git_branch_lowercase_d(self):
        """Soft delete; git refuses if branch is unmerged."""
        code, _ = self._bash("git branch -d feature")
        assert code == 0

    def test_passes_npm_install_force(self):
        """Non-git `--force` must pass through."""
        code, _ = self._bash("npm install --force")
        assert code == 0

    def test_passes_docker_build_force_rm(self):
        code, _ = self._bash("docker build --force-rm .")
        assert code == 0

    def test_passes_pip_install_force_reinstall(self):
        code, _ = self._bash("pip install --force-reinstall package")
        assert code == 0

    def test_passes_pilot_worktree_cleanup_force(self):
        """Pilot's `/spec` verify chain runs `pilot worktree cleanup --force` — must pass."""
        code, _ = self._bash("~/.pilot/bin/pilot worktree cleanup --force --json my-slug")
        assert code == 0

    def test_passes_cp_force(self):
        code, _ = self._bash("cp --force src dst")
        assert code == 0

    # ---- Codex adversarial review: bypass cases ----

    def test_blocks_chained_dryrun_then_force_push(self):
        """A `--dry-run` token in one segment must NOT mask a destructive command in the next."""
        code, output = self._bash("echo --dry-run; git push --force origin main")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_dryrun_push_then_hard_reset(self):
        """Same shape: dry-run push followed by hard reset — the reset must still deny."""
        code, output = self._bash("git push --force --dry-run origin main; git reset --hard HEAD~1")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_checkout_with_arbitrary_ref(self):
        """`git checkout HEAD~1 -- file.py` is destructive — overwrites working tree."""
        code, output = self._bash("git checkout HEAD~1 -- file.py")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_checkout_with_branch_ref(self):
        """`git checkout main -- file.py` is destructive too."""
        code, output = self._bash("git checkout main -- file.py")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_clean_long_force(self):
        """`git clean --force -d` is destructive — long form was missed by short-only regex."""
        code, output = self._bash("git clean --force -d")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_push_long_delete(self):
        """`git push origin --delete branch` is the long form of `:branch` colon-delete."""
        code, output = self._bash("git push origin --delete old-feature")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_branch_long_force_delete(self):
        """`git branch --delete --force feature` is the long form of `-D`."""
        code, output = self._bash("git branch --delete --force feature")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_branch_force_delete_reversed(self):
        """`git branch --force --delete feature` (option order swapped)."""
        code, output = self._bash("git branch --force --delete feature")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_restore_with_source_dot(self):
        """`git restore --source=HEAD~1 .` is working-tree destructive even without --worktree."""
        code, output = self._bash("git restore --source=HEAD~1 .")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_restore_worktree_reversed(self):
        """`git restore --worktree --staged .` (option order swapped) — still working-tree destructive."""
        code, output = self._bash("git restore --worktree --staged .")
        assert code == 2
        assert _is_denied(output)

    def test_blocks_git_push_force_with_lease_with_ref(self):
        """`git push --force-with-lease=ref origin main` — explicit ref form."""
        code, output = self._bash("git push --force-with-lease=feature origin main")
        assert code == 2
        assert _is_denied(output)

    def test_passes_cd_then_safe_git(self):
        """`cd /tmp && git status` — chained safe commands must pass."""
        code, _ = self._bash("cd /tmp && git status")
        assert code == 0

    def test_passes_dryrun_segment_alone(self):
        """`git push --dry-run origin main` in a single segment still passes."""
        code, _ = self._bash("git push --dry-run origin main")
        assert code == 0


# ---------------------------------------------------------------------------
# Search-nudge classifier tests (added 2026-04-29 for codegraph-probe-enforcement)
# ---------------------------------------------------------------------------


def _has_nudge(output: str) -> bool:
    """Check whether the hook stdout contains an additionalContext nudge."""
    if not output.strip():
        return False
    try:
        data = json.loads(output.strip())
    except (json.JSONDecodeError, ValueError):
        return False
    hook_output = data.get("hookSpecificOutput", {})
    return bool(hook_output.get("additionalContext"))


def _nudge_text(output: str) -> str:
    """Extract additionalContext string (or empty)."""
    try:
        data = json.loads(output.strip())
    except (json.JSONDecodeError, ValueError):
        return ""
    return data.get("hookSpecificOutput", {}).get("additionalContext", "")


import pytest  # noqa: E402  — added at end-of-file to avoid touching original imports


@pytest.fixture
def fresh_throttle(tmp_path, monkeypatch):
    """Redirect the throttle sentinel to a per-test file so each test starts fresh.

    The implementation exposes `_throttle_sentinel_path()` returning the sentinel
    Path; tests monkeypatch it to point at tmp_path.
    """
    import tool_redirect as tr

    sentinel = tmp_path / "search_nudge_sent.json"
    monkeypatch.setattr(tr, "_throttle_sentinel_path", lambda: sentinel)
    return sentinel


@pytest.mark.usefixtures("fresh_throttle")
class TestSearchNudgeBashGrep:
    """Bash(grep ...) recursive search → nudge."""

    def test_nudges_grep_short_recursive(self):
        code, output = _run_with_input("Bash", {"command": "grep -rn 'foo' ./src"})
        assert code == 0
        assert _has_nudge(output)
        text = _nudge_text(output)
        assert "codegraph_search" in text or "codegraph" in text
        assert "probe search" in text or "probe" in text

    def test_nudges_grep_capital_R(self):
        code, output = _run_with_input("Bash", {"command": "grep -R pattern ."})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_grep_long_recursive(self):
        code, output = _run_with_input("Bash", {"command": "grep --recursive 'x' ."})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_grep_recursive_listfiles(self):
        code, output = _run_with_input("Bash", {"command": "grep -rl pattern ."})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_grep_with_include(self):
        code, output = _run_with_input("Bash", {"command": "grep --include='*.py' -r pattern ."})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_grep_with_time_prefix(self):
        code, output = _run_with_input("Bash", {"command": "time grep -r foo ."})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_grep_with_sudo_prefix(self):
        code, output = _run_with_input("Bash", {"command": "sudo grep -r foo ."})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_grep_with_nice_prefix(self):
        code, output = _run_with_input("Bash", {"command": "nice grep -r foo ."})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_compound_segment(self):
        code, output = _run_with_input("Bash", {"command": "cd src && grep -r foo ."})
        assert code == 0
        assert _has_nudge(output)


@pytest.mark.usefixtures("fresh_throttle")
class TestSearchNudgeBashRg:
    def test_nudges_rg_default_recursive(self):
        code, output = _run_with_input("Bash", {"command": "rg 'pattern' ."})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_rg_no_path(self):
        code, output = _run_with_input("Bash", {"command": "rg pattern"})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_rg_files_mode(self):
        code, output = _run_with_input("Bash", {"command": "rg --files"})
        assert code == 0
        assert _has_nudge(output)
        assert "codegraph_files" in _nudge_text(output)


@pytest.mark.usefixtures("fresh_throttle")
class TestSearchNudgeBashFind:
    def test_nudges_find_with_name(self):
        code, output = _run_with_input("Bash", {"command": "find . -name '*.py'"})
        assert code == 0
        assert _has_nudge(output)
        assert "codegraph_files" in _nudge_text(output)

    def test_nudges_find_with_iname(self):
        code, output = _run_with_input("Bash", {"command": "find . -iname '*.PY'"})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_find_with_type_only(self):
        code, output = _run_with_input("Bash", {"command": "find . -type f"})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_find_with_type_and_delete(self):
        code, output = _run_with_input("Bash", {"command": "find . -type f -delete"})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_find_subdir_with_name(self):
        code, output = _run_with_input("Bash", {"command": "find ./src -name '*.ts'"})
        assert code == 0
        assert _has_nudge(output)


@pytest.mark.usefixtures("fresh_throttle")
class TestSearchNudgeBashFdAg:
    def test_nudges_fd_with_pattern(self):
        code, output = _run_with_input("Bash", {"command": "fd config"})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_fd_no_args(self):
        code, output = _run_with_input("Bash", {"command": "fd"})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_ag_basic(self):
        code, output = _run_with_input("Bash", {"command": "ag 'TODO'"})
        assert code == 0
        assert _has_nudge(output)


@pytest.mark.usefixtures("fresh_throttle")
class TestSearchNudgeBuiltinTools:
    """Built-in Grep / Glob tools."""

    def test_nudges_grep_tool_call(self):
        code, output = _run_with_input("Grep", {"pattern": "foo", "path": "./src"})
        assert code == 0
        assert _has_nudge(output)
        text = _nudge_text(output)
        assert "codegraph_search" in text

    def test_nudges_grep_no_path(self):
        code, output = _run_with_input("Grep", {"pattern": "foo"})
        assert code == 0
        assert _has_nudge(output)

    def test_nudges_glob_tool_call(self):
        code, output = _run_with_input("Glob", {"pattern": "**/*.py"})
        assert code == 0
        assert _has_nudge(output)
        assert "codegraph_files" in _nudge_text(output)


@pytest.mark.usefixtures("fresh_throttle")
class TestSearchNudgeNegatives:
    """Cases that must NOT produce a nudge."""

    def test_no_nudge_grep_single_file(self):
        code, output = _run_with_input("Bash", {"command": "grep ERROR /var/log/app.log"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_grep_n_single_file(self):
        code, output = _run_with_input("Bash", {"command": "grep -n pattern src/file.py"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_rg_single_file(self):
        code, output = _run_with_input("Bash", {"command": "rg pattern src/main.ts"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_git_grep(self):
        code, output = _run_with_input("Bash", {"command": "git grep 'foo'"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_git_grep_with_args(self):
        code, output = _run_with_input("Bash", {"command": "git grep -n pattern -- '*.py'"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_curl_pipe_grep(self):
        code, output = _run_with_input("Bash", {"command": "curl https://example.com | grep error"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_cat_pipe_grep(self):
        code, output = _run_with_input("Bash", {"command": "cat foo.log | grep WARN"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_echo_pipe_grep(self):
        code, output = _run_with_input("Bash", {"command": "echo $PATH | grep node"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_xargs_grep(self):
        # Composed command via xargs — pipeline filtering, lean conservative.
        code, output = _run_with_input("Bash", {"command": "ls *.py | xargs grep foo"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_npm_install(self):
        code, output = _run_with_input("Bash", {"command": "npm install"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_uv_pytest(self):
        code, output = _run_with_input("Bash", {"command": "uv run pytest -q"})
        assert code == 0
        assert not _has_nudge(output)

    def test_no_nudge_ls_grep_filter(self):
        code, output = _run_with_input("Bash", {"command": "ls -la | grep '\\.py$'"})
        assert code == 0
        assert not _has_nudge(output)


class TestSearchNudgeThrottle:
    @pytest.mark.usefixtures("fresh_throttle")
    def test_throttle_grep_only_first_call_nudges(self):
        code1, out1 = _run_with_input("Grep", {"pattern": "foo"})
        assert code1 == 0
        assert _has_nudge(out1)
        code2, out2 = _run_with_input("Grep", {"pattern": "bar"})
        assert code2 == 0
        assert not _has_nudge(out2)

    @pytest.mark.usefixtures("fresh_throttle")
    def test_throttle_separate_categories(self):
        _, out1 = _run_with_input("Bash", {"command": "grep -r foo ."})
        assert _has_nudge(out1)
        # Different category — must still nudge
        _, out2 = _run_with_input("Bash", {"command": "rg pattern ."})
        assert _has_nudge(out2)

    @pytest.mark.usefixtures("fresh_throttle")
    def test_throttle_glob_separate_from_grep(self):
        _, out1 = _run_with_input("Grep", {"pattern": "foo"})
        assert _has_nudge(out1)
        _, out2 = _run_with_input("Glob", {"pattern": "**/*.py"})
        assert _has_nudge(out2)

    def test_throttle_corrupt_sentinel_file(self, fresh_throttle):
        # Pre-write malformed JSON; throttle should treat as never-sent.
        fresh_throttle.parent.mkdir(parents=True, exist_ok=True)
        fresh_throttle.write_text("not json {{{")
        code, output = _run_with_input("Grep", {"pattern": "foo"})
        assert code == 0
        assert _has_nudge(output)

    @pytest.mark.usefixtures("fresh_throttle")
    def test_throttle_no_session_id(self, monkeypatch):
        monkeypatch.delenv("PILOT_SESSION_ID", raising=False)
        code, output = _run_with_input("Grep", {"pattern": "foo"})
        assert code == 0
        # With sentinel monkeypatched the env var isn't even read, but ensure no crash.
        assert _has_nudge(output)


@pytest.mark.usefixtures("fresh_throttle")
class TestSearchNudgeSafety:
    """Hook never denies, never crashes on bad input, preserves existing deny logic."""

    def test_search_nudge_never_denies_on_bash_grep(self):
        code, output = _run_with_input("Bash", {"command": "grep -r foo ."})
        assert code == 0
        try:
            data = json.loads(output.strip())
            assert data.get("permissionDecision") != "deny"
        except (json.JSONDecodeError, ValueError):
            pass  # additionalContext payload is fine

    def test_search_nudge_never_denies_on_grep_tool(self):
        code, output = _run_with_input("Grep", {"pattern": "foo"})
        assert code == 0
        assert not _is_denied(output)

    def test_search_nudge_never_denies_on_glob_tool(self):
        code, output = _run_with_input("Glob", {"pattern": "**/*.py"})
        assert code == 0
        assert not _is_denied(output)

    def test_existing_dangerous_git_still_denies(self):
        code, output = _run_with_input("Bash", {"command": "git push --force origin main"})
        assert code == 2
        assert _is_denied(output)

    def test_existing_websearch_still_denies(self):
        code, output = _run_with_input("WebSearch", {"query": "x"})
        assert code == 2
        assert _is_denied(output)

    def test_existing_explore_agent_still_denies(self):
        code, output = _run_with_input("Agent", {"subagent_type": "Explore", "prompt": "find files"})
        assert code == 2
        assert _is_denied(output)
