"""Tests for installer.steps.codex_files — Codex-specific file installation."""

from __future__ import annotations

import json
import re
import shutil
import tomllib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from installer.steps.codex_files import (
    CodexFilesStep,
    _TomlStructureError,
    _ensure_section_keys,
    _validate_toml_structure,
    build_codex_review_agent_toml,
)


class TestCodexFilesStepCheck:
    def test_check_returns_false_always(self) -> None:
        step = CodexFilesStep()
        ctx = MagicMock()
        assert step.check(ctx) is False


class TestCodexFilesStepSkipsWhenNoCodex:
    def test_run_is_noop_when_codex_not_installed(self, tmp_path: Path) -> None:
        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        with patch(
            "installer.steps.codex_files.is_codex_installed",
            return_value=False,
        ):
            step.run(ctx)

    def test_run_warns_and_returns_when_codex_home_is_relative(self) -> None:
        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = MagicMock()

        with (
            patch("installer.steps.codex_files.is_codex_installed", return_value=True),
            patch(
                "installer.steps.codex_files._get_codex_config_dir",
                side_effect=ValueError("CODEX_HOME must be an absolute path, got: relative"),
            ),
            patch.object(step, "_install_codex_skills") as mock_install_skills,
        ):
            step.run(ctx)

        ctx.ui.warning.assert_called_once_with(
            "Skipping Codex file installation: CODEX_HOME must be an absolute path, got: relative"
        )
        mock_install_skills.assert_not_called()

    def test_run_warns_and_returns_when_codex_home_is_relative_during_rules_install(self, tmp_path: Path) -> None:
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.md").write_text("# Test Rule\n")

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = MagicMock()
        ctx.local_mode = False

        codex_dir = tmp_path / ".codex"
        with (
            patch("installer.steps.codex_files.is_codex_installed", return_value=True),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
            patch(
                "installer.steps.codex_files._get_codex_config_dir",
                side_effect=[
                    codex_dir,
                    codex_dir,
                    ValueError("CODEX_HOME must be an absolute path, got: relative"),
                ],
            ),
        ):
            step.run(ctx)

        ctx.ui.warning.assert_called_with(
            "Skipping Codex file installation: CODEX_HOME must be an absolute path, got: relative"
        )


class TestCodexHooksInstallation:
    def test_installs_hooks_json_to_codex_dir(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        pilot_home = tmp_path / ".pilot"
        hooks_src = pilot_home / "hooks"
        hooks_src.mkdir(parents=True)

        codex_hooks_template = tmp_path / "source" / "pilot" / "hooks" / "codex_hooks.json"
        codex_hooks_template.parent.mkdir(parents=True)
        codex_hooks_template.write_text(
            json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo test"}]}]}})
        )

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        ctx.local_mode = True
        ctx.local_repo_dir = tmp_path / "source"
        ctx.project_dir = tmp_path / "project"

        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_hooks(ctx)

        hooks_file = codex_dir / "hooks.json"
        assert hooks_file.exists()
        data = json.loads(hooks_file.read_text())
        assert "hooks" in data
        assert "SessionStart" in data["hooks"]

    def test_real_template_injects_memory_context_on_codex_startup(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        ctx.local_mode = True
        ctx.local_repo_dir = repo_root

        with patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir):
            step._install_codex_hooks(ctx)

        data = json.loads((codex_dir / "hooks.json").read_text())
        context_commands = [
            hook["command"] for entry in data["hooks"]["SessionStart"] for hook in entry.get("hooks", [])
        ]
        assert any('worker-service.cjs" hook codex context' in command for command in context_commands)

    def test_real_template_has_all_hook_events(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        ctx.local_mode = True
        ctx.local_repo_dir = repo_root

        with patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir):
            step._install_codex_hooks(ctx)

        data = json.loads((codex_dir / "hooks.json").read_text())
        hooks = data["hooks"]
        assert "SessionStart" in hooks
        assert "UserPromptSubmit" in hooks
        assert "PreToolUse" in hooks
        assert "PostToolUse" in hooks
        assert "Stop" in hooks
        assert "PreCompact" in hooks

    def test_merge_preserves_user_posttooluse_hooks(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent

        user_hooks = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "*",
                        "hooks": [{"type": "command", "command": "my-custom-hook.sh"}],
                    }
                ]
            }
        }
        (codex_dir / "hooks.json").write_text(json.dumps(user_hooks))

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        ctx.local_mode = True
        ctx.local_repo_dir = repo_root

        with patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir):
            step._install_codex_hooks(ctx)

        data = json.loads((codex_dir / "hooks.json").read_text())
        all_commands = [hook["command"] for entry in data["hooks"]["PostToolUse"] for hook in entry.get("hooks", [])]
        assert any("my-custom-hook.sh" in cmd for cmd in all_commands)
        assert any("observation" in cmd for cmd in all_commands)


class TestCodexSkillsInstallation:
    def test_builds_codex_skill_with_frontmatter(self, tmp_path: Path) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        skill_dir = tmp_path / "skills" / "fix"
        skill_dir.mkdir(parents=True)
        (skill_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "orchestrator": "orchestrator.md",
                    "steps": [{"id": "step-1", "file": "steps/01-impl.md"}],
                }
            )
        )
        (skill_dir / "orchestrator.md").write_text(
            "---\nname: fix\ndescription: Bugfix workflow\nuser-invocable: true\n---\n\n# /fix\n\nFix bugs fast."
        )
        steps_dir = skill_dir / "steps"
        steps_dir.mkdir()
        (steps_dir / "01-impl.md").write_text("## Step 1\n\nImplement the fix.")

        result = build_codex_skill_md(skill_dir)
        assert result.startswith("---\n")
        assert "name: fix" in result
        assert "description: Bugfix workflow" in result
        assert "# /fix" in result or "# $fix" in result
        assert "Implement the fix." in result

    def test_codex_skill_adapts_invocation_syntax(self, tmp_path: Path) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        skill_dir = tmp_path / "skills" / "spec"
        skill_dir.mkdir(parents=True)
        (skill_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "orchestrator": "orchestrator.md",
                    "steps": [],
                }
            )
        )
        (skill_dir / "orchestrator.md").write_text(
            "---\nname: spec\ndescription: Spec workflow\n---\n\nRun /spec to plan. Also /fix for bugs."
        )

        result = build_codex_skill_md(skill_dir)
        assert "$spec" in result
        assert "$fix" in result

    def test_ask_codex_skill_is_never_shipped_to_codex(self, tmp_path: Path) -> None:
        """ask-codex is deliberately CC-only (Codex driving Codex is redundant).

        The mechanism is allowlist omission; this pins it so a future allowlist
        edit or auto-discovery refactor cannot silently ship $ask-codex.
        """
        agents_skills_dir = tmp_path / ".agents" / "skills"
        pilot_skills_dir = tmp_path / ".claude" / "skills"

        for name in ("fix", "ask-codex"):
            skill_dir = pilot_skills_dir / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "manifest.json").write_text(
                json.dumps({"version": 1, "orchestrator": "orchestrator.md", "steps": []})
            )
            (skill_dir / "orchestrator.md").write_text(f"---\nname: {name}\ndescription: d\n---\n\n# {name}\n\nBody.")

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None

        with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
            step._install_codex_skills(ctx)

        assert (agents_skills_dir / "fix" / "SKILL.md").exists()  # allowlisted sibling proves the run
        assert not (agents_skills_dir / "ask-codex").exists()

    def test_installs_skills_to_agents_dir(self, tmp_path: Path) -> None:
        agents_skills_dir = tmp_path / ".agents" / "skills"
        pilot_skills_dir = tmp_path / ".claude" / "skills"

        skill_dir = pilot_skills_dir / "fix"
        skill_dir.mkdir(parents=True)
        (skill_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "orchestrator": "orchestrator.md",
                    "steps": [],
                }
            )
        )
        (skill_dir / "orchestrator.md").write_text("---\nname: fix\ndescription: Bugfix\n---\n\n# Fix\n\nContent.")

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None

        with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
            step._install_codex_skills(ctx)

        skill_md = agents_skills_dir / "fix" / "SKILL.md"
        assert skill_md.exists()
        content = skill_md.read_text()
        assert content.startswith("---\n")
        assert "name: fix" in content

    def test_builds_codex_review_agent_toml_without_output_path_contract(self) -> None:
        result = build_codex_review_agent_toml(Path("pilot/agents/spec-review.md"))
        data = tomllib.loads(result)

        assert data["name"] == "spec-review"
        assert data["model"] == "codex-auto-review"
        assert "requirements" in data["description"]
        assert "developer_instructions" in data
        instructions = data["developer_instructions"]
        assert "Output ONLY valid JSON" in instructions
        assert '"issues"' in instructions
        assert "output_path" not in instructions
        assert "MANDATORY: Write output" not in instructions
        assert "Your LAST action MUST be `Write`" not in instructions

    def test_builds_changes_review_agent_with_final_status_guidance(self) -> None:
        result = build_codex_review_agent_toml(Path("pilot/agents/changes-review.md"))
        data = tomllib.loads(result)

        assert data["name"] == "changes-review"
        instructions = data["developer_instructions"]
        assert "Status: VERIFIED" in instructions
        assert "orchestrator after the user review gate" in instructions
        assert "do not emit a finding during changes review" in instructions

    def test_installs_review_agents_to_codex_agents_dir(self, tmp_path: Path) -> None:
        claude_agents_dir = tmp_path / ".claude" / "agents"
        claude_agents_dir.mkdir(parents=True)
        shutil.copyfile(Path("pilot/agents/spec-review.md"), claude_agents_dir / "spec-review.md")
        shutil.copyfile(Path("pilot/agents/changes-review.md"), claude_agents_dir / "changes-review.md")
        codex_agents_dir = tmp_path / ".codex" / "agents"
        codex_agents_dir.mkdir(parents=True)
        (codex_agents_dir / "user-agent.toml").write_text('name = "user-agent"\n')

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None

        with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
            step._install_codex_agents(ctx)

        spec_agent = codex_agents_dir / "spec-review.toml"
        changes_agent = codex_agents_dir / "changes-review.toml"
        assert spec_agent.exists()
        assert changes_agent.exists()
        assert (codex_agents_dir / "user-agent.toml").exists()
        spec_data = tomllib.loads(spec_agent.read_text())
        changes_data = tomllib.loads(changes_agent.read_text())
        assert spec_data["name"] == "spec-review"
        assert spec_data["model"] == "codex-auto-review"
        assert changes_data["name"] == "changes-review"
        assert changes_data["model"] == "codex-auto-review"

    def test_preserves_user_created_same_name_codex_agent(self, tmp_path: Path) -> None:
        claude_agents_dir = tmp_path / ".claude" / "agents"
        claude_agents_dir.mkdir(parents=True)
        shutil.copyfile(Path("pilot/agents/spec-review.md"), claude_agents_dir / "spec-review.md")
        codex_agents_dir = tmp_path / ".codex" / "agents"
        codex_agents_dir.mkdir(parents=True)
        user_content = 'name = "spec-review"\ndescription = "user agent"\n'
        (codex_agents_dir / "spec-review.toml").write_text(user_content)

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = MagicMock()

        with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
            step._install_codex_agents(ctx)

        assert (codex_agents_dir / "spec-review.toml").read_text() == user_content
        ctx.ui.warning.assert_called_once()

    def test_removes_stale_bot_skills_from_agents_dir(self, tmp_path: Path) -> None:
        agents_skills_dir = tmp_path / ".agents" / "skills"
        pilot_skills_dir = tmp_path / ".claude" / "skills"

        # Create a supported skill (fix) and stale bot-* skills
        for name in ["fix", "bot-boot", "bot-channel-task", "bot-defaults"]:
            skill_dir = pilot_skills_dir / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "manifest.json").write_text(
                json.dumps({"version": 1, "orchestrator": "orchestrator.md", "steps": []})
            )
            (skill_dir / "orchestrator.md").write_text(
                f"---\nname: {name}\ndescription: {name}\n---\n\n# {name}\n\nContent."
            )

        # Pre-populate stale bot-* skills in agents dir (from older installer)
        for name in ["bot-boot", "bot-channel-task", "bot-defaults"]:
            stale_dir = agents_skills_dir / name
            stale_dir.mkdir(parents=True)
            (stale_dir / "SKILL.md").write_text(f"# stale {name}")

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None

        with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
            step._install_codex_skills(ctx)

        # bot-* should be removed
        assert not (agents_skills_dir / "bot-boot").exists()
        assert not (agents_skills_dir / "bot-channel-task").exists()
        assert not (agents_skills_dir / "bot-defaults").exists()
        # fix should still be installed
        assert (agents_skills_dir / "fix" / "SKILL.md").exists()

    def test_setup_rules_codex_skill_creates_project_agents_md(self) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills/setup-rules"))

        assert "Codex reads project instructions from repo-root `AGENTS.md`" in result
        assert "If `AGENTS.md` does not exist, create it" in result
        assert "Never create AGENTS.md if it doesn't exist" not in result

    def test_create_skill_codex_skill_uses_agents_skill_paths(self) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills/create-skill"))

        assert ".agents/skills/{slug}-{name}/SKILL.md" in result
        assert "~/.agents/skills/{slug}-{name}/SKILL.md" in result
        assert (
            "Skills in `.agents/skills/` (project) or `~/.agents/skills/` (global) are available to Codex"
        ) in result
        assert (
            "Skills in `.claude/skills/` (project) or `~/.claude/skills/` "
            "(global) are automatically available to Claude"
        ) not in result

    def test_benchmark_codex_skill_describes_codex_materialization(self) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills/benchmark"))

        assert ".agents/skills/<name>/" in result
        assert "root `AGENTS.md`" in result
        assert "--agent codex" in result
        assert "with/.claude/skills/<name>/" not in result

    def test_fix_codex_skill_uses_selective_codegraph_guidance(self) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills/fix"))

        assert 'Start with `codegraph_context(task="<bug description>")`' not in result
        assert "Use `codegraph_explore` only when the bug is structural" in result
        assert "For docs, rules, markdown, config, UI copy, or a named local file/function" in result

    def test_fix_skill_env_blocker_protocol_diverges_per_agent(self) -> None:
        """Run-the-repro-first + blocker protocol: shared content in both builds,
        the inline `!` login hint is CC-only, the separate-terminal hint Codex-only."""
        from installer.skill_builder import build_skill_md
        from installer.steps.codex_files import build_codex_skill_md

        codex_result = build_codex_skill_md(Path("pilot/skills/fix"))
        assert "Read the COMPLETE output" in codex_result
        assert "Environment blocker protocol" in codex_result
        assert "separate terminal" in codex_result
        assert "! <command>" not in codex_result

        cc_result = build_skill_md(Path("pilot/skills/fix"))
        assert "Read the COMPLETE output" in cc_result
        assert "Environment blocker protocol" in cc_result
        assert "! <command>" in cc_result

    def test_spec_plan_codex_skill_strips_model_switch_mode(self) -> None:
        """Model Switching is CC-ONLY (Codex has no model switching).

        The three-way mode read in the planning skills must survive the CC
        build and be stripped from the Codex build (skill-sync parity rule).
        """
        from installer.skill_builder import build_skill_md
        from installer.steps.codex_files import build_codex_skill_md

        for skill in ("spec-plan", "spec-bugfix-plan"):
            codex_result = build_codex_skill_md(Path("pilot/skills") / skill)
            assert "read_model_switch_mode" not in codex_result, skill
            assert "EnterPlanMode" not in codex_result, skill
            assert "ExitPlanMode" not in codex_result, skill

            cc_result = build_skill_md(Path("pilot/skills") / skill)
            assert "read_model_switch_mode" in cc_result, skill


class TestCodexRulesInstallation:
    def test_creates_agents_md_with_markers(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "testing.md").write_text("## Testing\n\nTest rules here.")
        (rules_dir / "verification.md").write_text("## Verification\n\nVerify rules.")

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        ctx.local_mode = False

        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_rules(ctx)

        agents_md = codex_dir / "AGENTS.md"
        assert agents_md.exists()
        content = agents_md.read_text()
        assert "<!-- PILOT:START -->" in content
        assert "<!-- PILOT:END -->" in content
        assert "## Testing" in content
        assert "## Verification" in content

    def test_preserves_user_content_outside_markers(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        (codex_dir / "AGENTS.md").write_text(
            "# My Project\n\nCustom instructions.\n\n<!-- PILOT:START -->\nold pilot content\n<!-- PILOT:END -->\n\nMore user content."
        )
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "testing.md").write_text("## Testing\n\nNew rules.")

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        ctx.local_mode = False

        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_rules(ctx)

        content = (codex_dir / "AGENTS.md").read_text()
        assert "# My Project" in content
        assert "Custom instructions." in content
        assert "More user content." in content
        assert "New rules." in content
        assert "old pilot content" not in content

    def test_adapts_invocation_syntax(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "workflow.md").write_text("## Workflow\n\nRun /spec to start. Use /fix for bugs.")

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        ctx.local_mode = False

        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_rules(ctx)

        content = (codex_dir / "AGENTS.md").read_text()
        assert "$spec" in content
        assert "$fix" in content

    def test_real_rules_generate_codex_safe_agents_md(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        rules_dir = tmp_path / ".claude" / "rules"
        shutil.copytree(Path("pilot/rules"), rules_dir, dirs_exist_ok=True)

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        ctx.local_mode = False

        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_rules(ctx)

        content = (codex_dir / "AGENTS.md").read_text()
        assert "## Codex Compatibility" in content
        assert "update_plan" in content
        assert "verify the generated artifacts directly" in content
        assert "persist returned agent/job ids to a session file" in content
        assert "| Start any new task | `codegraph_context(task=...)` — ALWAYS FIRST |" not in content
        assert "| Task orientation (FIRST on every task) | `codegraph_context` |" not in content
        # The CODEX-START variant of the CodeGraph guidance must survive unwrapping, and the
        # CC-ONLY variant must be stripped. Assert the load-bearing phrases rather than whole
        # sentences - the rules get reworded regularly, and a full-sentence match turns every
        # copy-edit into a red test without catching anything a phrase match misses.
        assert "Codex budget:" in content
        assert "Skip the graph entirely for docs, rules, config, UI copy, named paths" in content
        preamble_end = "Skill invocation: use `$skill-name` (not `/skill-name`)."
        assert preamble_end in content
        rules_body = content.split(preamble_end, 1)[1]
        for forbidden in (
            "<!-- CC-ONLY -->",
            "<!-- CODEX-START",
            "AskUserQuestion",
            "TaskCreate",
            "TaskList",
            "TaskOutput",
            "Skill()",
            "Skill(",
            "Skill(skill=",
            "Skill('",
            "Agent(",
            "Task(",
            "suppressOutput",
            "hookSpecificOutput",
            "CLAUDE_CODE_TASK_LIST_ID",
            "CLAUDE_PROJECT_ROOT",
            "WebFetch",
            "WebSearch",
            "Bash(",
            "Read(",
            "Write(",
            "Edit(",
            "plain-text numbered options(",
            "plain-text numbered options tool",
            "/fix",
            "/prd",
            "SendMessage",
            "codex-companion.mjs",
            "codex:codex-rescue",
        ):
            assert forbidden not in rules_body
        assert re.search(r"(^|[^A-Za-z0-9_`])/(spec|fix|prd)([^A-Za-z0-9_/]|$)", rules_body) is None
        for forbidden in ("Run /spec", "Use /spec", "invoke /spec"):
            assert forbidden not in content


class TestCodexMcpConfiguration:
    def test_generates_toml_for_stdio_server(self) -> None:
        from installer.steps.codex_files import _mcp_json_to_toml

        mcp = {"mcpServers": {"context7": {"command": "npx", "args": ["-y", "@upstash/context7-mcp@2.2.4"]}}}
        toml = _mcp_json_to_toml(mcp)
        assert "[mcp_servers.context7]" in toml
        assert 'command = "npx"' in toml
        assert 'args = ["-y", "@upstash/context7-mcp@2.2.4"]' in toml

    def test_generates_toml_for_http_server(self) -> None:
        from installer.steps.codex_files import _mcp_json_to_toml

        mcp = {"mcpServers": {"grep-mcp": {"type": "http", "url": "https://mcp.grep.app"}}}
        toml = _mcp_json_to_toml(mcp)
        assert "[mcp_servers.grep-mcp]" in toml
        assert 'url = "https://mcp.grep.app"' in toml

    def test_generates_toml_with_env_vars(self) -> None:
        from installer.steps.codex_files import _mcp_json_to_toml

        mcp = {
            "mcpServers": {
                "web-search": {
                    "command": "npx",
                    "args": ["-y", "open-websearch"],
                    "env": {"MODE": "stdio", "ENGINE": "duckduckgo"},
                }
            }
        }
        toml = _mcp_json_to_toml(mcp)
        assert "[mcp_servers.web-search.env]" in toml
        assert 'MODE = "stdio"' in toml
        assert 'ENGINE = "duckduckgo"' in toml

    @staticmethod
    def _run_mcp_install(tmp_path: Path, existing_toml: str | None, mcp_servers: dict) -> tuple[str, MagicMock]:
        """Run _install_codex_mcp against a fixture config; return (final content, ctx)."""
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True, exist_ok=True)
        if existing_toml is not None:
            (codex_dir / "config.toml").write_text(existing_toml)

        mcp_json = tmp_path / ".pilot" / ".mcp.json"
        mcp_json.parent.mkdir(parents=True, exist_ok=True)
        mcp_json.write_text(json.dumps({"mcpServers": mcp_servers}))

        step = CodexFilesStep()
        ctx = MagicMock()

        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_mcp(ctx)

        return (codex_dir / "config.toml").read_text(), ctx

    _CONTEXT7 = {"context7": {"command": "npx", "args": ["-y", "@upstash/context7-mcp@3.2.1"]}}

    def test_installs_mcp_to_codex_config_toml(self, tmp_path: Path) -> None:
        config, _ = self._run_mcp_install(tmp_path, None, {"test-server": {"command": "echo", "args": ["hello"]}})
        assert "[mcp_servers.test-server]" in config

    def test_preserves_user_mcp_entries(self, tmp_path: Path) -> None:
        config, _ = self._run_mcp_install(
            tmp_path,
            '[mcp_servers.my-server]\ncommand = "my-cmd"\n\n',
            {"pilot-server": {"command": "echo", "args": ["hello"]}},
        )
        assert "my-server" in config
        assert "pilot-server" in config

    def test_heals_orphaned_mcp_block_missing_start_marker(self, tmp_path: Path) -> None:
        """A prior write that lost its start marker leaves [mcp_servers.context7]
        as plain (unmarked) content followed by a lone end marker. Appending a
        fresh managed block on top of that -- instead of recognizing and
        removing the orphaned table -- declares [mcp_servers.context7] a
        second time: a duplicate key/table that aborts Codex startup."""
        content, _ = self._run_mcp_install(
            tmp_path,
            'approval_policy = "never"\n'
            "\n"
            "[mcp_servers.context7]\n"
            'command = "npx"\n'
            'args = ["-y", "@upstash/context7-mcp@3.2.1"]\n'
            "\n"
            "[mcp_servers.herd]\n"
            'command = "php"\n'
            'args = ["/Applications/Herd.app/Contents/Resources/herd-mcp.phar"]\n'
            "\n"
            "# --- end pilot-shell managed MCP servers ---\n",
            self._CONTEXT7,
        )
        assert content.count("[mcp_servers.context7]") == 1
        assert "[mcp_servers.herd]" in content  # non-pilot entry preserved
        # the lone END marker must be gone; only the freshly appended pair remains
        assert content.count("# --- end pilot-shell managed MCP servers ---") == 1
        assert content.count("# --- pilot-shell managed MCP servers ---") == 1
        tomllib.loads(content)  # must not raise: duplicate key/table = Codex startup crash

    def test_orphaned_start_marker_does_not_swallow_user_content(self, tmp_path: Path) -> None:
        """An orphaned START marker must not greedily pair with a LATER region's
        END marker -- that span contains user content."""
        content, _ = self._run_mcp_install(
            tmp_path,
            "# --- pilot-shell managed MCP servers ---\n"
            "\n"
            "[mcp_servers.usercustom]\n"
            'command = "my-cmd"\n'
            "\n"
            "# --- pilot-shell managed MCP servers ---\n"
            "[mcp_servers.context7]\n"
            'command = "npx"\n'
            "# --- end pilot-shell managed MCP servers ---\n",
            self._CONTEXT7,
        )
        assert "[mcp_servers.usercustom]" in content
        assert content.count("[mcp_servers.context7]") == 1
        tomllib.loads(content)

    def test_heals_quoted_managed_table_name(self, tmp_path: Path) -> None:
        """[mcp_servers."context7"] is the same TOML table as the bare spelling;
        missing it would re-declare the table and abort Codex startup."""
        content, _ = self._run_mcp_install(
            tmp_path,
            '[mcp_servers."context7"]\ncommand = "old"\n',
            self._CONTEXT7,
        )
        parsed = tomllib.loads(content)
        assert parsed["mcp_servers"]["context7"]["command"] == "npx"

    def test_heals_managed_table_with_nested_array(self, tmp_path: Path) -> None:
        """A continuation line of a multi-line array starting with '[' must not
        truncate the table removal (dangling fragments fail the TOML gate)."""
        content, _ = self._run_mcp_install(
            tmp_path,
            "[mcp_servers.context7]\narg_matrix = [\n    [1, 2],\n    [3, 4],\n]\n",
            self._CONTEXT7,
        )
        assert content.count("[mcp_servers.context7]") == 1
        parsed = tomllib.loads(content)
        assert "arg_matrix" not in parsed["mcp_servers"]["context7"]

    def test_preserves_multiline_string_values(self, tmp_path: Path) -> None:
        """User values must survive byte-for-byte -- a global newline collapse
        previously corrupted multi-line strings containing blank lines."""
        existing = 'banner = """line1\n\n\n\nline2"""\n'
        content, _ = self._run_mcp_install(tmp_path, existing, self._CONTEXT7)
        assert tomllib.loads(content)["banner"] == tomllib.loads(existing)["banner"]

    def test_removes_non_env_subtables_of_managed_server(self, tmp_path: Path) -> None:
        """Leftover sub-tables of a managed server (.headers etc.) must not
        graft stale keys onto the freshly written server."""
        content, _ = self._run_mcp_install(
            tmp_path,
            '[mcp_servers.context7]\ncommand = "old"\n[mcp_servers.context7.headers]\nAuthorization = "Bearer stale"\n',
            self._CONTEXT7,
        )
        parsed = tomllib.loads(content)
        assert "headers" not in parsed["mcp_servers"]["context7"]

    def test_heals_marker_concatenated_with_header(self, tmp_path: Path) -> None:
        """The historical newline-loss corruption (marker glued to the next
        table header on one line) must still be recognized as a marker."""
        content, _ = self._run_mcp_install(
            tmp_path,
            'approval_policy = "never"\n'
            "# --- pilot-shell managed MCP servers ---[mcp_servers.context7]\n"
            'command = "npx"\n'
            "# --- end pilot-shell managed MCP servers ---\n",
            self._CONTEXT7,
        )
        parsed = tomllib.loads(content)
        assert "command" not in parsed  # stranded keys must not leak to top level
        assert content.count("[mcp_servers.context7]") == 1

    def test_warns_when_dropping_unmarked_managed_table(self, tmp_path: Path) -> None:
        """Deleting content the user may regard as their own must be surfaced."""
        _, ctx = self._run_mcp_install(
            tmp_path,
            '[mcp_servers.context7]\ncommand = "my-own-copy"\n',
            self._CONTEXT7,
        )
        warnings = [str(c.args[0]) for c in ctx.ui.warning.call_args_list]
        assert any("context7" in w for w in warnings)

    def test_reports_existing_invalid_config(self, tmp_path: Path) -> None:
        """A pre-existing user syntax error must be attributed to the existing
        file (actionable), not to Pilot's generated config."""
        with pytest.raises(_TomlStructureError, match="invalid TOML and could not be healed"):
            self._run_mcp_install(tmp_path, "key =\n", self._CONTEXT7)


class TestAdaptInvocationSyntax:
    def test_strips_cc_only_blocks(self) -> None:
        from installer.steps.codex_files import _adapt_invocation_syntax

        content = "Before.\n<!-- CC-ONLY -->\nCC-specific content here.\n<!-- /CC-ONLY -->\nAfter."
        result = _adapt_invocation_syntax(content)
        assert "CC-specific content" not in result
        assert "Before." in result
        assert "After." in result

    def test_shipped_rules_never_leak_claude_only_tool_names_to_codex(self) -> None:
        """No adapted rule body may name a Claude-only tool.

        `ToolSearch` does not exist in Codex (it is `tool_search`). Naming it in
        SHARED rule text (outside a CC-ONLY block) survives adaptation and sends
        every Codex install toward a nonexistent tool. Guards the real rule files,
        not a fixture, so a future edit to any of them trips this.
        """
        from installer.steps.codex_files import _adapt_invocation_syntax

        rules_dir = Path(__file__).parents[4] / "pilot" / "rules"
        assert rules_dir.is_dir(), f"rules source not found at {rules_dir}"

        offenders: list[str] = []
        for rule in sorted(rules_dir.glob("*.md")):
            adapted = _adapt_invocation_syntax(rule.read_text(encoding="utf-8"))
            for claude_only in ("ToolSearch", "AskUserQuestion("):
                if claude_only in adapted:
                    offenders.append(f"{rule.name}: {claude_only}")

        assert not offenders, (
            "Claude-only tool names survived Codex adaptation - move them inside a "
            f"<!-- CC-ONLY --> block or make them tool-neutral: {offenders}"
        )

    def test_unwraps_codex_blocks(self) -> None:
        from installer.steps.codex_files import _adapt_invocation_syntax

        content = "Before.\n<!-- CODEX-START\nCodex alternative here.\nCODEX-END -->\nAfter."
        result = _adapt_invocation_syntax(content)
        assert "Codex alternative here." in result
        assert "CODEX-START" not in result
        assert "CODEX-END" not in result
        assert "Before." in result
        assert "After." in result

    def test_cc_only_stripped_and_codex_revealed(self) -> None:
        from installer.steps.codex_files import _adapt_invocation_syntax

        content = (
            "Shared.\n"
            "<!-- CC-ONLY -->\nLaunch subagent.\n<!-- /CC-ONLY -->\n"
            "<!-- CODEX-START\nSkip reviewers (Codex).\nCODEX-END -->\n"
            "More shared."
        )
        result = _adapt_invocation_syntax(content)
        assert "Launch subagent" not in result
        assert "Skip reviewers (Codex)." in result
        assert "Shared." in result
        assert "More shared." in result

    def test_transforms_skill_calls(self) -> None:
        from installer.steps.codex_files import _adapt_invocation_syntax

        content = "Then invoke Skill(skill='spec-implement', args='docs/plans/plan.md')"
        result = _adapt_invocation_syntax(content)
        assert "the `$spec-implement` skill instructions with arguments: `docs/plans/plan.md`" in result
        assert "Skill(" not in result

    def test_transforms_skill_calls_without_args(self) -> None:
        from installer.steps.codex_files import _adapt_invocation_syntax

        content = "Skill(skill='spec-verify')"
        result = _adapt_invocation_syntax(content)
        assert "the `$spec-verify` skill instructions" in result
        assert "Skill(" not in result

    def test_transforms_skill_calls_with_single_quotes(self) -> None:
        from installer.steps.codex_files import _adapt_invocation_syntax

        content = """Skill('spec', args='implement feature — PRD: docs/prd/file.md')"""
        result = _adapt_invocation_syntax(content)
        assert "$spec" in result
        assert "Skill(" not in result

    def test_transforms_ask_user_question_blocks(self) -> None:
        from installer.steps.codex_files import _adapt_invocation_syntax

        content = """AskUserQuestion(
  question="Ready?",
  options=["Yes", "No"]
)"""
        result = _adapt_invocation_syntax(content)
        assert "Present numbered options in plain text" in result
        assert 'question="Ready?"' in result
        assert 'options=["Yes", "No"]' in result
        assert "AskUserQuestion" not in result
        assert "plain-text numbered options(" not in result

    def test_real_spec_skill_uses_codex_phase_handoff(self) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills/spec"))
        assert "Codex has no callable phase-dispatch tool" in result
        assert "continue immediately with the `$spec-plan` skill instructions" in result
        assert (
            "sub-agents (spec-review, changes-review), and the Codex companion reviewer are not available" not in result
        )
        assert "Native `spec-review` and `changes-review` run as managed Codex custom agents" in result
        assert (
            "The current running session may not expose newly generated skills or agent types until the next install or SessionStart sync"
            in result
        )
        assert "Skill(skill=" not in result
        assert "Skill('" not in result

    def test_real_spec_plan_codex_uses_native_review_agent(self) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills/spec-plan"))
        assert "review agents are not available in Codex CLI" not in result
        assert "Skip automated plan review agents" not in result
        assert "multi_agent_v1.spawn_agent" in result
        assert "multi_agent_v1.wait_agent" in result
        assert 'agent_type="spec-review"' in result
        assert "PILOT_SPEC_REVIEW_ENABLED" in result
        assert "PILOT_CODEX_SPEC_REVIEW_ENABLED" not in result

    def test_real_spec_verify_codex_uses_native_review_agent(self) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills/spec-verify"))
        assert "No reviewer agents in Codex" not in result
        assert "Skip automated code review agents" not in result
        assert "reviewer agents were launched (not available in Codex CLI)" not in result
        assert "multi_agent_v1.spawn_agent" in result
        assert "multi_agent_v1.wait_agent" in result
        assert 'agent_type="changes-review"' in result
        assert "changes-review-agent-id-" in result
        assert "Do not silently skip review" in result
        assert 'FIND_BIN="/usr/bin/find"' in result
        assert "Reviewable file preflight" in result
        assert "Broad-check failure classification" in result
        assert "Final-status-only findings are not implementation fixes" in result
        assert "PILOT_CHANGES_REVIEW_ENABLED" in result
        assert "PILOT_CODEX_CHANGES_REVIEW_ENABLED" not in result

    def test_real_spec_verify_codex_strips_inline_code_review_blocks(self) -> None:
        """The CC-only inline /code-review flow (Skill invocation + Plan
        Compliance & Goal-Truth Audit) must be fully stripped from the Codex
        build, and stripping the indented CC-ONLY block inside the Step 2
        checklist must not corrupt the numbered list (item 6 stays at
        column 0)."""
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills/spec-verify"))
        assert "code-review" not in result.replace("changes-review", "")
        assert "Plan Compliance & Goal-Truth Audit" not in result
        assert "\n6. **Build**" in result
        assert "\n   6. **Build**" not in result

    @pytest.mark.parametrize(
        "skill_name",
        [
            "spec",
            "spec-plan",
            "spec-bugfix-plan",
            "spec-implement",
            "spec-verify",
            "spec-bugfix-verify",
            "prd",
            "fix",
            "benchmark",
            "setup-rules",
            "create-skill",
        ],
    )
    def test_real_codex_skills_do_not_expose_claude_tool_calls(self, skill_name: str) -> None:
        from installer.steps.codex_files import build_codex_skill_md

        result = build_codex_skill_md(Path("pilot/skills") / skill_name)
        assert "<!-- CC-ONLY -->" not in result
        assert "<!-- CODEX-START" not in result
        for forbidden in (
            "AskUserQuestion",
            "TaskList",
            "TaskCreate",
            "TaskOutput",
            "Skill()",
            "Skill(",
            "Agent(",
            "Task(",
            "suppressOutput",
            "hookSpecificOutput",
            "CLAUDE_CODE_TASK_LIST_ID",
            "CLAUDE_PROJECT_ROOT",
            "WebFetch",
            "WebSearch",
            "ToolSearch",
            "Bash(",
            "Read(",
            "Write(",
            "Edit(",
            "plain-text numbered options(",
            "plain-text numbered options tool",
            "SendMessage",
            "codex-companion.mjs",
            "codex:codex-rescue",
        ):
            assert forbidden not in result
        assert (
            re.search(r"(^|[^A-Za-z0-9_`])/(spec|fix|prd|setup-rules|create-skill|benchmark)([^A-Za-z0-9_/]|$)", result)
            is None
        )

    def test_multiline_cc_only_block(self) -> None:
        from installer.steps.codex_files import _adapt_invocation_syntax

        content = "Step 1.\n<!-- CC-ONLY -->\nLine 1.\nLine 2.\nLine 3.\n<!-- /CC-ONLY -->\nStep 2."
        result = _adapt_invocation_syntax(content)
        assert "Line 1" not in result
        assert "Line 2" not in result
        assert "Step 1." in result
        assert "Step 2." in result

    def test_preserves_user_hooks_in_existing_codex_hooks(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)

        existing = {
            "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo user-hook"}]}]}
        }
        (codex_dir / "hooks.json").write_text(json.dumps(existing))

        incoming = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo pilot"}]}]}}

        step = CodexFilesStep()
        step._merge_codex_hooks(codex_dir, incoming)

        result = json.loads((codex_dir / "hooks.json").read_text())
        assert "SessionStart" in result["hooks"]
        assert "PreToolUse" in result["hooks"]
        assert result["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "echo user-hook"


class TestTomlValidation:
    def test_valid_toml_passes(self) -> None:
        content = (
            'approval_policy = "never"\n'
            "\n"
            "[notice]\n"
            "hide_full_access_warning = true\n"
            "\n"
            "[sandbox_workspace_write]\n"
            "network_access = true\n"
        )
        _validate_toml_structure(content)

    def test_section_concatenated_on_value_line(self) -> None:
        content = "[notice]\nhide_full_access_warning = true[sandbox_workspace_write]\nnetwork_access = true\n"
        with pytest.raises(_TomlStructureError, match="section header not at start of line"):
            _validate_toml_structure(content)

    def test_section_concatenated_on_key_line(self) -> None:
        content = "bypass_hook_trust = true[notice]\nhide_full_access_warning = true\n"
        with pytest.raises(_TomlStructureError, match="line 1"):
            _validate_toml_structure(content)

    def test_exact_regression_notice_sandbox(self) -> None:
        """Exact reproduction of the real-world bug: hide_full_access_warning = true[sandbox_workspace_write]."""
        content = "[notice]\nhide_full_access_warning = true[sandbox_workspace_write]\nnetwork_access = true\n"
        with pytest.raises(_TomlStructureError):
            _validate_toml_structure(content)

    def test_comments_and_blanks_ignored(self) -> None:
        content = "# comment with [fake] section\n\n[real]\nkey = true\n"
        _validate_toml_structure(content)

    def test_managed_marker_comments_ignored(self) -> None:
        content = (
            "# --- pilot-shell managed MCP servers ---\n"
            "[mcp_servers.codegraph]\n"
            'command = "codegraph"\n'
            "# --- end pilot-shell managed MCP servers ---\n"
        )
        _validate_toml_structure(content)

    def test_brackets_inside_quoted_values_ignored(self) -> None:
        content = 'args = ["--from", "semble[mcp]", "semble"]\n'
        _validate_toml_structure(content)

    def test_array_values_with_brackets_ignored(self) -> None:
        content = '[mcp_servers.semble]\ncommand = "uvx"\nargs = ["--from", "semble[mcp]", "semble"]\n'
        _validate_toml_structure(content)

    def test_dotted_and_quoted_section_names(self) -> None:
        content = '[hooks.state."/path/to/file:event:0:0"]\ntrusted_hash = "sha256:abc"\n'
        _validate_toml_structure(content)


class TestEnsureSectionKeys:
    def test_creates_section_when_missing(self) -> None:
        content = 'approval_policy = "never"\n'
        result, changed = _ensure_section_keys(content, "features", {"memories": "true", "hooks": "true"})
        assert changed is True
        assert "[features]" in result
        assert "memories = true" in result
        assert "hooks = true" in result
        _validate_toml_structure(result)

    def test_adds_missing_keys_to_existing_section(self) -> None:
        content = "[features]\nmemories = true\n\n[notice]\nhide = true\n"
        result, changed = _ensure_section_keys(content, "features", {"hooks": "true", "memories": "true"})
        assert changed is True
        assert "hooks = true" in result
        assert result.count("memories") == 1  # not duplicated

    def test_noop_when_all_keys_present(self) -> None:
        content = "[features]\nmemories = true\nhooks = true\n"
        result, changed = _ensure_section_keys(content, "features", {"memories": "true", "hooks": "true"})
        assert changed is False
        assert result == content


class TestTuiStatuslineConfiguration:
    def test_installs_tui_statusline_on_fresh_config(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        config = codex_dir / "config.toml"
        config.write_text('approval_policy = "never"\n')

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_config(ctx)

        result = config.read_text()
        assert "[tui]" in result
        assert "status_line" in result
        assert "project-name" in result
        assert "model-with-reasoning" in result
        assert "status_line_use_colors = true" in result
        _validate_toml_structure(result)

    def test_preserves_existing_tui_settings(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        config = codex_dir / "config.toml"
        config.write_text(
            'approval_policy = "never"\n'
            "\n"
            "[tui]\n"
            'status_line = ["project-name", "run-state"]\n'
            "status_line_use_colors = false\n"
        )

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_config(ctx)

        result = config.read_text()
        assert 'status_line = ["project-name", "run-state"]' in result
        assert "status_line_use_colors = false" in result
        assert result.count("status_line =") == 1


class TestDeprecatedKeyRemoval:
    def test_removes_bypass_hook_trust(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        config = codex_dir / "config.toml"
        config.write_text('approval_policy = "never"\nbypass_hook_trust = true\n\n[features]\nhooks = true\n')

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_config(ctx)

        result = config.read_text()
        assert "bypass_hook_trust" not in result
        assert "hooks = true" in result
        assert "undo = true" in result
        assert "mentions_v2 = true" in result
        assert "tool_search = true" in result
        assert "apps = false" in result


class TestUnstableFeaturesWarningSuppression:
    def test_suppresses_unstable_features_warning_on_fresh_config(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        config = codex_dir / "config.toml"
        config.write_text('approval_policy = "never"\n')

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_config(ctx)

        result = config.read_text()
        assert "suppress_unstable_features_warning = true" in result
        # Must be a top-level key, inserted before the first [section] header.
        first_section = result.index("[")
        assert "suppress_unstable_features_warning" in result[:first_section]
        _validate_toml_structure(result)

    def test_does_not_duplicate_existing_suppression(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        config = codex_dir / "config.toml"
        config.write_text('approval_policy = "never"\nsuppress_unstable_features_warning = true\n')

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_config(ctx)

        result = config.read_text()
        assert result.count("suppress_unstable_features_warning") == 1


class TestMcpMarkerReplacement:
    """Regression tests: MCP managed block replacement must not corrupt surrounding sections."""

    def _make_step_with_mcp_json(self, tmp_path: Path, mcp_data: dict) -> tuple[CodexFilesStep, Path]:
        pilot_home = tmp_path / ".pilot"
        pilot_home.mkdir(parents=True)
        (pilot_home / ".mcp.json").write_text(json.dumps(mcp_data))
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        return CodexFilesStep(), codex_dir / "config.toml"

    @patch("installer.steps.codex_files._get_codex_config_dir")
    @patch("installer.steps.codex_files.Path.home")
    def test_second_install_preserves_section_newlines(
        self, mock_home: MagicMock, mock_codex_dir: MagicMock, tmp_path: Path
    ) -> None:
        mock_home.return_value = tmp_path
        mock_codex_dir.return_value = tmp_path / ".codex"
        step, config_path = self._make_step_with_mcp_json(
            tmp_path, {"mcpServers": {"codegraph": {"command": "codegraph", "args": ["serve", "--mcp"]}}}
        )

        initial = (
            'approval_policy = "never"\n'
            "\n"
            "[notice]\n"
            "hide_full_access_warning = true\n"
            "\n"
            "# --- pilot-shell managed MCP servers ---\n"
            "[mcp_servers.codegraph]\n"
            'command = "codegraph"\n'
            'args = ["serve", "--mcp"]\n'
            "\n"
            "# --- end pilot-shell managed MCP servers ---\n"
            "\n"
            "[sandbox_workspace_write]\n"
            "network_access = true\n"
        )
        config_path.write_text(initial)

        ctx = MagicMock()
        step._install_codex_mcp(ctx)

        result = config_path.read_text()
        _validate_toml_structure(result)
        assert "[notice]" in result
        assert "[sandbox_workspace_write]" in result

    @patch("installer.steps.codex_files._get_codex_config_dir")
    @patch("installer.steps.codex_files.Path.home")
    def test_markers_between_user_sections_preserved(
        self, mock_home: MagicMock, mock_codex_dir: MagicMock, tmp_path: Path
    ) -> None:
        mock_home.return_value = tmp_path
        mock_codex_dir.return_value = tmp_path / ".codex"
        step, config_path = self._make_step_with_mcp_json(
            tmp_path, {"mcpServers": {"ctx7": {"command": "npx", "args": ["-y", "@upstash/context7-mcp"]}}}
        )

        initial = (
            "[notice]\n"
            "hide_full_access_warning = true\n"
            "\n"
            "# --- pilot-shell managed MCP servers ---\n"
            "[mcp_servers.old]\n"
            'command = "old"\n'
            "\n"
            "# --- end pilot-shell managed MCP servers ---\n"
            "\n"
            "[sandbox_workspace_write]\n"
            "network_access = true\n"
        )
        config_path.write_text(initial)

        ctx = MagicMock()
        step._install_codex_mcp(ctx)

        result = config_path.read_text()
        assert "[notice]" in result
        assert "[sandbox_workspace_write]" in result
        assert "mcp_servers.ctx7" in result
        assert "mcp_servers.old" not in result
        _validate_toml_structure(result)


class TestProjectDocMaxBytes:
    """Codex silently truncates AGENTS.md beyond project_doc_max_bytes (default
    32 KiB). Pilot's merged rules are ~88 KB, so the installer must raise the
    ceiling or most rules never prime Codex startup instructions."""

    def test_raises_project_doc_max_bytes_above_codex_default(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        config = codex_dir / "config.toml"
        config.write_text('approval_policy = "never"\n')

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_config(ctx)

        result = config.read_text()
        # Must be a top-level key, inserted before the first [section] header.
        first_section = result.index("[")
        assert "project_doc_max_bytes" in result[:first_section]
        parsed = tomllib.loads(result)
        value = parsed["project_doc_max_bytes"]
        assert isinstance(value, int)
        # Must exceed Codex's 32 KiB default that causes the truncation, with
        # real headroom above the current ~88 KB merged AGENTS.md.
        assert value > 32768
        assert value >= 131072
        _validate_toml_structure(result)

    def test_preserves_user_project_doc_max_bytes(self, tmp_path: Path) -> None:
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir(parents=True)
        config = codex_dir / "config.toml"
        config.write_text('approval_policy = "never"\nproject_doc_max_bytes = 65536\n')

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None
        with (
            patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
        ):
            step._install_codex_config(ctx)

        result = config.read_text()
        assert result.count("project_doc_max_bytes") == 1
        assert tomllib.loads(result)["project_doc_max_bytes"] == 65536


class TestCodexConfigEnvHeal:
    """CodexFilesStep heals ~/.codex/config.toml's managed env block at
    install/update time, so a duplicate-key leftover from a pre-fix version is
    repaired immediately rather than lazily via the license-gated,
    startup-only session hook (which misses Codex-only / resume-only / lapsed
    users)."""

    def test_run_heals_codex_config_via_sync_env(self, tmp_path: Path) -> None:
        pilot_bin = tmp_path / ".pilot" / "bin" / "pilot"
        pilot_bin.parent.mkdir(parents=True)
        pilot_bin.touch()

        step = CodexFilesStep()
        ctx = MagicMock()
        ctx.ui = None

        with (
            patch("installer.steps.codex_files.is_codex_installed", return_value=True),
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
            patch("installer.steps.codex_files.subprocess.run") as mock_run,
            patch.object(step, "_install_codex_hooks", return_value=0),
            patch.object(step, "_install_codex_skills", return_value=0),
            patch.object(step, "_install_codex_agents", return_value=0),
            patch.object(step, "_install_codex_config", return_value=False),
            patch.object(step, "_install_codex_mcp", return_value=0),
            patch.object(step, "_install_codex_rules", return_value=0),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            step.run(ctx)

        invoked = [call.args[0] for call in mock_run.call_args_list]
        # Codex-scoped heal: must NOT let `pilot sync-env` touch Claude settings.
        assert any(str(pilot_bin) in cmd and "sync-env" in cmd and "--codex-only" in cmd for cmd in invoked)

    def test_heal_skips_when_pilot_binary_missing(self, tmp_path: Path) -> None:
        step = CodexFilesStep()
        with (
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
            patch("installer.steps.codex_files.subprocess.run") as mock_run,
        ):
            step._heal_codex_config_env()

        mock_run.assert_not_called()

    def test_heal_warns_on_nonzero_returncode(self, tmp_path: Path) -> None:
        """A failed heal must surface a warning, not be silently swallowed."""
        pilot_bin = tmp_path / ".pilot" / "bin" / "pilot"
        pilot_bin.parent.mkdir(parents=True)
        pilot_bin.touch()

        step = CodexFilesStep()
        ui = MagicMock()
        with (
            patch("installer.steps.codex_files.Path.home", return_value=tmp_path),
            patch("installer.steps.codex_files.subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=1, stderr="permission denied", stdout="")
            step._heal_codex_config_env(ui)

        ui.warning.assert_called_once()


class TestCodexSourcesHonourClaudeConfigDir:
    """Codex adaptation reads skills/agents/rules FROM the Claude profile.

    With a custom profile these hardcoded reads find nothing, so a Codex user
    silently gets zero skills and no review agents.
    """

    def test_skills_source_follows_config_dir(self, tmp_path, monkeypatch):
        from installer.steps.codex_files import CodexFilesStep

        work = tmp_path / ".claude_work"
        skill_dir = work / "skills" / "spec"
        skill_dir.mkdir(parents=True)
        (skill_dir / "manifest.json").write_text(
            json.dumps({"version": 1, "orchestrator": "orchestrator.md", "steps": []})
        )
        (skill_dir / "orchestrator.md").write_text(
            "---\nname: spec\ndescription: Spec workflow\n---\n\nRun /spec to plan."
        )
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(work))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        from installer.context import InstallContext

        ctx = InstallContext(project_dir=tmp_path)
        built = CodexFilesStep()._install_codex_skills(ctx)

        assert built > 0, "no skills adapted from the custom profile"
        assert (tmp_path / ".agents" / "skills" / "spec" / "SKILL.md").exists()

    def test_review_agents_source_follows_config_dir(self, tmp_path, monkeypatch):
        from installer.steps.codex_files import CodexFilesStep

        work = tmp_path / ".claude_work"
        (work / "agents").mkdir(parents=True)
        (work / "agents" / "spec-review.md").write_text("# spec review\n")
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(work))
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        from installer.context import InstallContext

        ctx = InstallContext(project_dir=tmp_path)
        found = CodexFilesStep()._find_codex_review_agents_source(ctx)

        assert found is not None, "review-agent source not found in the custom profile"
        assert str(work) in str(found)


class TestCodexSourcesFailClosedOnInvalidConfigDir:
    """A set-but-relative CLAUDE_CONFIG_DIR must never fall back to ~/.claude.

    Mirrors the invalid-value coverage dependencies.py already has; without it
    a regression could reintroduce the personal-profile read silently.
    """

    def test_skills_install_reads_nothing(self, tmp_path, monkeypatch):
        from installer.context import InstallContext
        from installer.steps.codex_files import CodexFilesStep

        personal = tmp_path / ".claude" / "skills" / "spec"
        personal.mkdir(parents=True)
        (personal / "manifest.json").write_text(
            json.dumps({"version": 1, "orchestrator": "orchestrator.md", "steps": []})
        )
        (personal / "orchestrator.md").write_text("---\nname: spec\ndescription: d\n---\n\nx")
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", "relative/path")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        built = CodexFilesStep()._install_codex_skills(InstallContext(project_dir=tmp_path))

        assert built == 0
        assert not (tmp_path / ".agents" / "skills" / "spec").exists()

    def test_review_agents_source_is_none(self, tmp_path, monkeypatch):
        from installer.context import InstallContext
        from installer.steps.codex_files import CodexFilesStep

        (tmp_path / ".claude" / "agents").mkdir(parents=True)
        (tmp_path / ".claude" / "agents" / "spec-review.md").write_text("# x\n")
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", "relative/path")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        assert CodexFilesStep()._find_codex_review_agents_source(InstallContext(project_dir=tmp_path)) is None

    def test_rules_fallback_is_none(self, tmp_path, monkeypatch):
        from installer.steps.codex_files import _claude_rules_dir_or_none

        monkeypatch.setenv("CLAUDE_CONFIG_DIR", "relative/path")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        assert _claude_rules_dir_or_none() is None
