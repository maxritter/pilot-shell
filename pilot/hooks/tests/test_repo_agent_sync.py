"""Tests for automatic repository rule and skill synchronization hooks."""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, call

import pytest

_HOOKS_DIR = Path(__file__).resolve().parent.parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

import repo_agent_sync  # noqa: E402
from repo_agent_sync import CheckerResult, handle, main  # noqa: E402


def _enroll(repo: Path) -> Path:
    (repo / ".git").mkdir(parents=True, exist_ok=True)
    checker = repo / "scripts" / "sync-agent-assets.mjs"
    checker.parent.mkdir(parents=True)
    checker.write_text("// installed checker\n")
    return checker


def _session_payload(repo: Path) -> dict:
    return {"hook_event_name": "SessionStart", "source": "startup", "cwd": str(repo)}


def _post_payload(repo: Path, tool_name: str, tool_input: dict) -> dict:
    return {
        "hook_event_name": "PostToolUse",
        "cwd": str(repo),
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


def _pre_payload(repo: Path, tool_name: str, tool_input: dict) -> dict:
    payload = _post_payload(repo, tool_name, tool_input)
    payload["hook_event_name"] = "PreToolUse"
    return payload


def _make_skill(repo: Path, name: str = "example") -> Path:
    skill = repo / ".agents" / "skills" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Example project skill.\n---\n\n# Example\n"
    )
    return skill


class TestSessionStart:
    def test_repository_without_checker_is_quiet_noop(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        repo = tmp_path / "repo"
        (repo / ".git").mkdir(parents=True)
        run = Mock()
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        assert handle(_session_payload(repo)) == {"continue": True}
        run.assert_not_called()

    def test_bundled_checker_refreshes_enrolled_repo(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        repo = tmp_path / "repo"
        local = _enroll(repo)
        bundled = tmp_path / "bundled" / "sync-agent-assets.mjs"
        bundled.parent.mkdir()
        bundled.write_text("// current bundled checker\n")
        run = Mock(return_value=CheckerResult(True))
        monkeypatch.setattr(repo_agent_sync, "_bundled_checker", lambda: bundled)
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        result = handle(_session_payload(repo))

        run.assert_called_once_with(bundled, "install", repo)
        assert result["continue"] is True
        assert "refreshed and synchronized" in result["systemMessage"]
        assert result["hookSpecificOutput"]["hookEventName"] == "SessionStart"
        assert local.is_file()

    def test_local_checker_is_fallback_when_bundle_is_unavailable(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        repo = tmp_path / "repo"
        checker = _enroll(repo)
        run = Mock(side_effect=[CheckerResult(False, "drift"), CheckerResult(True)])
        monkeypatch.setattr(repo_agent_sync, "_bundled_checker", lambda: None)
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        result = handle(_session_payload(repo))

        assert run.call_args_list == [
            call(checker, "check", repo),
            call(checker, "write", repo),
        ]
        assert "synchronized" in result["systemMessage"]

    def test_current_synchronized_repo_is_silent(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        repo = tmp_path / "repo"
        checker = _enroll(repo)
        bundled = tmp_path / "bundled.mjs"
        bundled.write_bytes(checker.read_bytes())
        run = Mock(return_value=CheckerResult(True))
        monkeypatch.setattr(repo_agent_sync, "_bundled_checker", lambda: bundled)
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        result = handle(_session_payload(repo))

        assert result == {"continue": True}
        run.assert_called_once_with(bundled, "check", repo)

    def test_checker_failure_warns_but_does_not_block_session(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)
        monkeypatch.setattr(repo_agent_sync, "_bundled_checker", lambda: None)
        monkeypatch.setattr(
            repo_agent_sync,
            "_run_checker",
            Mock(return_value=CheckerResult(False, "refusing to overwrite nontrivial CLAUDE.md")),
        )

        result = handle(_session_payload(repo))

        assert result["continue"] is True
        assert "nontrivial CLAUDE.md" in result["systemMessage"]
        assert "decision" not in result


class TestPostToolUse:
    @pytest.mark.parametrize("tool_name", ["Write", "Edit", "MultiEdit"])
    def test_claude_canonical_rule_edit_syncs_immediately(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tool_name: str
    ) -> None:
        repo = tmp_path / "repo"
        checker = _enroll(repo)
        run = Mock(return_value=CheckerResult(True))
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        result = handle(_post_payload(repo, tool_name, {"file_path": str(repo / "AGENTS.md")}))

        run.assert_called_once_with(checker, "write", repo)
        assert result["continue"] is True
        assert "synchronized" in result["systemMessage"]
        assert result["hookSpecificOutput"]["hookEventName"] == "PostToolUse"

    def test_claude_canonical_skill_edit_syncs_immediately(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        repo = tmp_path / "repo"
        checker = _enroll(repo)
        run = Mock(return_value=CheckerResult(True))
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        result = handle(
            _post_payload(repo, "Edit", {"file_path": ".agents/skills/my-skill/references/example.md"})
        )

        run.assert_called_once_with(checker, "write", repo)
        assert result["continue"] is True

    def test_codex_apply_patch_extracts_every_canonical_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        repo = tmp_path / "repo"
        checker = _enroll(repo)
        run = Mock(return_value=CheckerResult(True))
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)
        patch = """*** Begin Patch
*** Update File: AGENTS.md
@@
-old
+new
*** Add File: .agents/skills/new-skill/SKILL.md
+content
*** Move to: .agents/skills/new-skill/references/note.md
*** End Patch"""

        result = handle(_post_payload(repo, "functions.apply_patch", {"command": patch}))

        run.assert_called_once_with(checker, "write", repo)
        assert result["continue"] is True

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("CLAUDE.md", "CLAUDE.md -> AGENTS.md"),
            (
                ".claude/skills/project-skill/SKILL.md",
                ".claude/skills/project-skill/SKILL.md -> .agents/skills/project-skill/SKILL.md",
            ),
        ],
    )
    def test_generated_edits_are_restored_with_canonical_mapping(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        path: str,
        expected: str,
    ) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)
        if path.startswith(".claude/skills/"):
            _make_skill(repo, "project-skill")
        run = Mock(return_value=CheckerResult(True))
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        result = handle(_post_payload(repo, "Edit", {"file_path": path}))

        run.assert_called_once_with(repo / "scripts" / "sync-agent-assets.mjs", "write", repo)
        assert result["decision"] == "block"
        assert expected in result["reason"]
        assert "restored" in result["systemMessage"]

    def test_generated_edit_wins_over_same_patch_canonical_edit(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)
        _make_skill(repo, "demo")
        run = Mock(return_value=CheckerResult(True))
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)
        patch = """*** Begin Patch
*** Update File: .agents/skills/demo/SKILL.md
@@
-old
+canonical
*** Update File: .claude/skills/demo/SKILL.md
@@
-old
+generated
*** End Patch"""

        result = handle(_post_payload(repo, "apply_patch", {"command": patch}))

        run.assert_called_once_with(repo / "scripts" / "sync-agent-assets.mjs", "write", repo)
        assert result["decision"] == "block"

    @pytest.mark.parametrize("path", ["app/main.ts", ".claude/rules/project.md", "docs/AGENTS.md"])
    def test_unrelated_edit_is_quiet_and_does_not_run_node(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, path: str
    ) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)
        run = Mock()
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        assert handle(_post_payload(repo, "Edit", {"file_path": path})) == {"continue": True}
        run.assert_not_called()

    def test_checker_failure_blocks_canonical_edit_with_recovery_command(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)
        monkeypatch.setattr(
            repo_agent_sync,
            "_run_checker",
            Mock(return_value=CheckerResult(False, "skill frontmatter is invalid")),
        )

        result = handle(_post_payload(repo, "Edit", {"file_path": "AGENTS.md"}))

        assert result["decision"] == "block"
        assert "skill frontmatter is invalid" in result["reason"]
        assert "node scripts/sync-agent-assets.mjs --write" in result["reason"]

    def test_repo_without_checker_never_runs_or_warns(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        repo = tmp_path / "repo"
        (repo / ".git").mkdir(parents=True)
        run = Mock()
        monkeypatch.setattr(repo_agent_sync, "_run_checker", run)

        assert handle(_post_payload(repo, "Edit", {"file_path": "AGENTS.md"})) == {"continue": True}
        run.assert_not_called()


class TestInputSafety:
    @pytest.mark.parametrize("payload", [None, [], "broken", {}, {"hook_event_name": "Unknown"}])
    def test_malformed_or_unknown_payload_is_fail_open(self, payload: object) -> None:
        assert handle(payload) == {"continue": True}

    def test_main_handles_invalid_json(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(sys, "stdin", io.StringIO("{invalid"))

        assert main() == 0
        assert json.loads(capsys.readouterr().out) == {"continue": True}

    def test_checker_timeout_is_bounded(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        checker = tmp_path / "checker.mjs"
        checker.write_text("// checker\n")
        monkeypatch.setattr(repo_agent_sync.shutil, "which", lambda _name: "/usr/bin/node")
        monkeypatch.setattr(
            repo_agent_sync.subprocess,
            "run",
            Mock(side_effect=subprocess.TimeoutExpired(["node"], repo_agent_sync._RUN_TIMEOUT_SECONDS)),
        )

        result = repo_agent_sync._run_checker(checker, "write", tmp_path)

        assert result == CheckerResult(False, "checker timed out after 8 seconds")


class TestPreToolUse:
    @pytest.mark.parametrize("tool_name", ["Write", "Edit", "MultiEdit"])
    def test_claude_mirror_edit_redirects_to_canonical_path(
        self, tmp_path: Path, tool_name: str
    ) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)
        _make_skill(repo, "demo")
        original = repo / ".claude" / "skills" / "demo" / "SKILL.md"

        result = handle(_pre_payload(repo, tool_name, {"file_path": str(original), "content": "new"}))

        output = result["hookSpecificOutput"]
        assert output["hookEventName"] == "PreToolUse"
        assert output["permissionDecision"] == "allow"
        assert output["updatedInput"]["file_path"] == str(repo / ".agents" / "skills" / "demo" / "SKILL.md")
        assert output["updatedInput"]["content"] == "new"
        assert "redirected" in output["additionalContext"]

    def test_codex_apply_patch_redirects_only_mirror_markers(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)
        _make_skill(repo, "demo")
        patch = """*** Begin Patch
*** Update File: .claude/skills/demo/SKILL.md
@@
-old
+new
*** Update File: app/main.ts
@@
-before
+after
*** Move to: .claude/skills/demo/references/note.md
*** End Patch"""

        result = handle(_pre_payload(repo, "apply_patch", {"command": patch, "timeout": 10}))

        output = result["hookSpecificOutput"]
        rewritten = output["updatedInput"]["command"]
        assert output["permissionDecision"] == "allow"
        assert "*** Update File: .agents/skills/demo/SKILL.md" in rewritten
        assert "*** Move to: .agents/skills/demo/references/note.md" in rewritten
        assert "*** Update File: app/main.ts" in rewritten
        assert output["updatedInput"]["timeout"] == 10

    @pytest.mark.parametrize("tool_name", ["Write", "Edit", "MultiEdit", "apply_patch"])
    def test_claude_md_edit_is_denied_before_mutation(self, tmp_path: Path, tool_name: str) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)
        if tool_name == "apply_patch":
            tool_input = {"command": "*** Begin Patch\n*** Update File: CLAUDE.md\n*** End Patch"}
        else:
            tool_input = {"file_path": "CLAUDE.md"}

        result = handle(_pre_payload(repo, tool_name, tool_input))

        output = result["hookSpecificOutput"]
        assert output == {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "CLAUDE.md is generated and must remain exactly @AGENTS.md. "
                "Apply the rule change to AGENTS.md instead."
            ),
        }

    def test_unrelated_pre_tool_edit_is_quiet(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)

        assert handle(_pre_payload(repo, "Edit", {"file_path": "app/main.ts"})) == {"continue": True}

    def test_untracked_claude_only_skill_is_not_redirected(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        _enroll(repo)

        result = handle(_pre_payload(repo, "Edit", {"file_path": ".claude/skills/local-only/SKILL.md"}))

        assert result == {"continue": True}


@pytest.mark.skipif(shutil.which("node") is None or shutil.which("git") is None, reason="requires node and git")
class TestBundledCheckerIntegration:
    def test_session_start_upgrades_converges_and_preserves_untracked_local_skill(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
        local_checker = _enroll(repo)
        (repo / "AGENTS.md").write_text("# Shared instructions\n")
        canonical = _make_skill(repo)
        local_skill = repo / ".claude" / "skills" / "local-only"
        local_skill.mkdir(parents=True)
        (local_skill / "SKILL.md").write_text("local agent state\n")

        result = handle(_session_payload(repo))

        bundled = repo_agent_sync._bundled_checker()
        assert bundled is not None
        assert result["continue"] is True
        assert "refreshed and synchronized" in result["systemMessage"]
        assert local_checker.read_bytes() == bundled.read_bytes()
        assert (repo / "CLAUDE.md").read_text() == "@AGENTS.md\n"
        assert (repo / ".claude" / "skills" / "example" / "SKILL.md").read_bytes() == (
            canonical / "SKILL.md"
        ).read_bytes()
        assert (local_skill / "SKILL.md").read_text() == "local agent state\n"

    def test_session_start_never_overwrites_nontrivial_claude(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
        _enroll(repo)
        (repo / "AGENTS.md").write_text("# Shared instructions\n")
        _make_skill(repo)
        claude = repo / "CLAUDE.md"
        original = "# Unique Claude instructions\n\nKeep this content.\n"
        claude.write_text(original)

        result = handle(_session_payload(repo))

        assert result["continue"] is True
        assert "refusing to overwrite nontrivial CLAUDE.md" in result["systemMessage"]
        assert claude.read_text() == original

    def test_post_tool_fallback_restores_generated_skill_from_canonical(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
        checker = _enroll(repo)
        bundled = repo_agent_sync._bundled_checker()
        assert bundled is not None
        checker.write_bytes(bundled.read_bytes())
        (repo / "AGENTS.md").write_text("# Shared instructions\n")
        canonical = _make_skill(repo)
        assert handle(_session_payload(repo))["continue"] is True
        mirror = repo / ".claude" / "skills" / "example" / "SKILL.md"
        mirror.write_text("direct generated edit\n")

        result = handle(_post_payload(repo, "Edit", {"file_path": str(mirror)}))

        assert result["decision"] == "block"
        assert mirror.read_bytes() == (canonical / "SKILL.md").read_bytes()


def _commands(manifest: dict, event: str) -> list[tuple[str, dict]]:
    return [
        (entry.get("matcher", ""), hook)
        for entry in manifest["hooks"][event]
        for hook in entry.get("hooks", [])
    ]


def test_claude_and_codex_manifests_register_sync_lifecycle() -> None:
    hooks_dir = Path(__file__).resolve().parent.parent
    claude = json.loads((hooks_dir / "hooks.json").read_text())
    codex = json.loads((hooks_dir / "codex_hooks.json").read_text())

    claude_start = [item for item in _commands(claude, "SessionStart") if "repo_agent_sync.py" in item[1]["command"]]
    codex_start = [item for item in _commands(codex, "SessionStart") if "repo_agent_sync.py" in item[1]["command"]]
    claude_pre = [item for item in _commands(claude, "PreToolUse") if "repo_agent_sync.py" in item[1]["command"]]
    codex_pre = [item for item in _commands(codex, "PreToolUse") if "repo_agent_sync.py" in item[1]["command"]]
    claude_post = [item for item in _commands(claude, "PostToolUse") if "repo_agent_sync.py" in item[1]["command"]]
    codex_post = [item for item in _commands(codex, "PostToolUse") if "repo_agent_sync.py" in item[1]["command"]]

    assert [matcher for matcher, _hook in claude_start] == ["startup|resume|clear|compact"]
    assert [matcher for matcher, _hook in codex_start] == ["startup|resume|clear|compact"]
    assert [matcher for matcher, _hook in claude_pre] == ["Write|Edit|MultiEdit"]
    assert [matcher for matcher, _hook in codex_pre] == ["apply_patch"]
    assert [matcher for matcher, _hook in claude_post] == ["Write|Edit|MultiEdit"]
    assert [matcher for matcher, _hook in codex_post] == ["apply_patch"]
    for _matcher, hook in [*claude_start, *codex_start, *claude_pre, *codex_pre, *claude_post, *codex_post]:
        assert "codex_background.py" not in hook["command"]
        assert hook["timeout"] <= 20
