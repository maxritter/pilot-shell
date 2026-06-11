"""Tests for codex_skill_sync hook — Codex SKILL.md rebuild + license gating."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest

# Add hooks dir to path so we can import the module
_hooks_dir = Path(__file__).resolve().parent.parent
if str(_hooks_dir) not in sys.path:
    sys.path.insert(0, str(_hooks_dir))

from codex_skill_sync import (  # noqa: E402
    _adapt,
    _build_codex_review_agent,
    _build_codex_skill,
    _build_skill,
    _check_license,
    _remove_codex_review_agents,
    _remove_codex_skills,
    _sync_codex_env_vars,
    _sync_codex_review_agents,
    _sync_codex_skills,
    main,
)


@pytest.fixture()
def skill_tree(tmp_path: Path) -> Path:
    """Create a minimal decomposed skill under tmp_path/.claude/skills/fix/."""
    skill_dir = tmp_path / ".claude" / "skills" / "fix"
    skill_dir.mkdir(parents=True)
    (skill_dir / "manifest.json").write_text(
        json.dumps(
            {
                "version": 1,
                "orchestrator": "orchestrator.md",
                "steps": [{"id": "s1", "file": "steps/01-impl.md"}],
            }
        )
    )
    (skill_dir / "orchestrator.md").write_text(
        "---\nname: fix\ndescription: Bugfix workflow\n---\n\n# /fix\n\nFix bugs."
    )
    steps = skill_dir / "steps"
    steps.mkdir()
    (steps / "01-impl.md").write_text("## Step 1\n\nRun /spec if needed.")
    return tmp_path


class TestBuildSkill:
    def test_concatenates_orchestrator_and_steps(self, skill_tree: Path) -> None:
        result = _build_skill(skill_tree / ".claude" / "skills" / "fix")
        assert result is not None
        assert "# /fix" in result
        assert "## Step 1" in result
        assert "Run /spec if needed." in result

    def test_returns_none_for_missing_manifest(self, tmp_path: Path) -> None:
        assert _build_skill(tmp_path / "nonexistent") is None


class TestAdapt:
    def test_strips_cc_only_blocks(self) -> None:
        content = "Before.\n<!-- CC-ONLY -->\nCC stuff.\n<!-- /CC-ONLY -->\nAfter."
        result = _adapt(content)
        assert "CC stuff" not in result
        assert "Before." in result
        assert "After." in result

    def test_unwraps_codex_blocks(self) -> None:
        content = "Before.\n<!-- CODEX-START\nCodex alt.\nCODEX-END -->\nAfter."
        result = _adapt(content)
        assert "Codex alt." in result
        assert "CODEX-START" not in result

    def test_transforms_skill_calls(self) -> None:
        content = "Skill(skill='spec-implement', args='plan.md')"
        result = _adapt(content)
        assert "the `$spec-implement` skill instructions with arguments: `plan.md`" in result
        assert "plan.md" in result

    def test_replaces_slash_invocations(self) -> None:
        content = "Run /spec to plan. Use /fix for bugs."
        result = _adapt(content)
        assert "$spec" in result
        assert "$fix" in result

    def test_replaces_ask_user_question(self) -> None:
        content = "Use AskUserQuestion to ask."
        result = _adapt(content)
        assert "plain-text numbered options" in result

    def test_transforms_ask_user_question_blocks(self) -> None:
        content = """AskUserQuestion(
  question="Ready?",
  options=["Yes", "No"]
)"""
        result = _adapt(content)
        assert "Present numbered options in plain text" in result
        assert 'question="Ready?"' in result
        assert 'options=["Yes", "No"]' in result
        assert "AskUserQuestion" not in result
        assert "plain-text numbered options(" not in result


class TestBuildCodexSkill:
    def test_produces_frontmatter_and_adapted_content(self, skill_tree: Path) -> None:
        result = _build_codex_skill(skill_tree / ".claude" / "skills" / "fix")
        assert result is not None
        assert result.startswith("---\n")
        assert "name: fix" in result
        assert "$spec" in result  # /spec replaced
        assert "$fix" in result

    def test_real_spec_skill_uses_codex_phase_handoff(self) -> None:
        result = _build_codex_skill(Path("pilot/skills/spec"))
        assert result is not None
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
        result = _build_codex_skill(Path("pilot/skills/spec-plan"))
        assert result is not None
        assert "review agents are not available in Codex CLI" not in result
        assert "Skip automated plan review agents" not in result
        assert "multi_agent_v1.spawn_agent" in result
        assert "multi_agent_v1.wait_agent" in result
        assert 'agent_type="spec-review"' in result
        assert "PILOT_SPEC_REVIEW_ENABLED" in result
        assert "PILOT_CODEX_SPEC_REVIEW_ENABLED" not in result

    def test_real_spec_verify_codex_uses_native_review_agent(self) -> None:
        result = _build_codex_skill(Path("pilot/skills/spec-verify"))
        assert result is not None
        assert "No reviewer agents in Codex" not in result
        assert "Skip automated code review agents" not in result
        assert "reviewer agents were launched (not available in Codex CLI)" not in result
        assert "multi_agent_v1.spawn_agent" in result
        assert "multi_agent_v1.wait_agent" in result
        assert 'agent_type="changes-review"' in result
        assert "changes-review-agent-id-" in result
        assert "Do not silently skip review" in result
        assert "PILOT_CHANGES_REVIEW_ENABLED" in result
        assert "PILOT_CODEX_CHANGES_REVIEW_ENABLED" not in result

    def test_real_fix_codex_skill_uses_selective_codegraph_guidance(self) -> None:
        result = _build_codex_skill(Path("pilot/skills/fix"))
        assert result is not None
        assert 'Start with `codegraph_context(task="<bug description>")`' not in result
        assert "Use `codegraph_context` only when the bug is structural" in result
        assert "For docs, rules, markdown, config, UI copy, or a named local file/function" in result

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
        result = _build_codex_skill(Path("pilot/skills") / skill_name)
        assert result is not None
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
        ):
            assert forbidden not in result
        assert (
            re.search(r"(^|[^A-Za-z0-9_`])/(spec|fix|prd|setup-rules|create-skill|benchmark)([^A-Za-z0-9_/]|$)", result)
            is None
        )


class TestSyncCodexSkills:
    def test_builds_skills_to_agents_dir(self, skill_tree: Path) -> None:
        agents_dir = skill_tree / ".agents" / "skills"
        with patch("codex_skill_sync.Path.home", return_value=skill_tree):
            built, failed = _sync_codex_skills()
        assert built == 1
        assert failed == 0
        assert (agents_dir / "fix" / "SKILL.md").is_file()
        content = (agents_dir / "fix" / "SKILL.md").read_text()
        assert "name: fix" in content

    def test_skips_missing_skills(self, skill_tree: Path) -> None:
        with patch("codex_skill_sync.Path.home", return_value=skill_tree):
            built, failed = _sync_codex_skills()
        # Only "fix" exists, the rest of _SUPPORTED_SKILLS are missing → skipped
        assert built == 1


class TestSyncCodexReviewAgents:
    def test_builds_review_agent_toml_without_output_path_contract(self) -> None:
        result = _build_codex_review_agent(Path("pilot/agents/spec-review.md"))
        assert result is not None
        data = tomllib.loads(result)
        assert data["name"] == "spec-review"
        assert data["model"] == "codex-auto-review"
        instructions = data["developer_instructions"]
        assert "Output ONLY valid JSON" in instructions
        assert '"issues"' in instructions
        assert "output_path" not in instructions
        assert "MANDATORY: Write output" not in instructions
        assert "Your LAST action MUST be `Write`" not in instructions

    def test_syncs_review_agents_to_codex_agents_dir(self, tmp_path: Path) -> None:
        claude_agents_dir = tmp_path / ".claude" / "agents"
        claude_agents_dir.mkdir(parents=True)
        (claude_agents_dir / "spec-review.md").write_text(Path("pilot/agents/spec-review.md").read_text())
        (claude_agents_dir / "changes-review.md").write_text(Path("pilot/agents/changes-review.md").read_text())
        codex_agents_dir = tmp_path / ".codex" / "agents"
        codex_agents_dir.mkdir(parents=True)
        (codex_agents_dir / "user-agent.toml").write_text('name = "user-agent"\n')

        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            built, failed = _sync_codex_review_agents()

        assert built == 2
        assert failed == 0
        spec_data = tomllib.loads((codex_agents_dir / "spec-review.toml").read_text())
        changes_data = tomllib.loads((codex_agents_dir / "changes-review.toml").read_text())
        assert spec_data["name"] == "spec-review"
        assert spec_data["model"] == "codex-auto-review"
        assert changes_data["name"] == "changes-review"
        assert changes_data["model"] == "codex-auto-review"
        assert (codex_agents_dir / "user-agent.toml").exists()

    def test_syncs_review_agents_to_codex_home_agents_dir(self, tmp_path: Path) -> None:
        claude_agents_dir = tmp_path / ".claude" / "agents"
        claude_agents_dir.mkdir(parents=True)
        (claude_agents_dir / "spec-review.md").write_text(Path("pilot/agents/spec-review.md").read_text())
        codex_home = tmp_path / "custom-codex"

        with (
            patch("codex_skill_sync.Path.home", return_value=tmp_path),
            patch.dict("codex_skill_sync.os.environ", {"CODEX_HOME": str(codex_home)}),
        ):
            built, failed = _sync_codex_review_agents()

        assert built == 1
        assert failed == 0
        assert (codex_home / "agents" / "spec-review.toml").exists()
        assert not (tmp_path / ".codex" / "agents" / "spec-review.toml").exists()


class TestRemoveCodexSkills:
    def test_removes_existing_skill_files(self, skill_tree: Path) -> None:
        agents_dir = skill_tree / ".agents" / "skills" / "fix"
        agents_dir.mkdir(parents=True)
        (agents_dir / "SKILL.md").write_text("old content")

        with patch("codex_skill_sync.Path.home", return_value=skill_tree):
            removed = _remove_codex_skills()
        assert removed == 1
        assert not (agents_dir / "SKILL.md").exists()

    def test_noop_when_no_skills(self, skill_tree: Path) -> None:
        with patch("codex_skill_sync.Path.home", return_value=skill_tree):
            removed = _remove_codex_skills()
        assert removed == 0

    def test_manifest_scoping_preserves_user_skill_with_pilot_name(self, tmp_path: Path) -> None:
        # A user named their own skill "fix" (a Pilot name) — but it is NOT in
        # the install manifest, so it must survive license enforcement.
        agents = tmp_path / ".agents" / "skills"
        (agents / "spec").mkdir(parents=True)
        (agents / "spec" / "SKILL.md").write_text("pilot spec")
        (agents / "fix").mkdir(parents=True)
        (agents / "fix" / "SKILL.md").write_text("user fix")
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / ".pilot-manifest.json").write_text(json.dumps({"files": ["skills/spec/manifest.json"]}))

        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            removed = _remove_codex_skills()

        assert removed == 1
        assert not (agents / "spec" / "SKILL.md").exists()
        assert (agents / "fix" / "SKILL.md").exists()  # user skill preserved


class TestRemoveCodexReviewAgents:
    def test_removes_managed_review_agent_files_only(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / ".codex" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "spec-review.toml").write_text('# pilot-shell managed Codex review agent\nname = "spec-review"\n')
        (agents_dir / "changes-review.toml").write_text(
            '# pilot-shell managed Codex review agent\nname = "changes-review"\n'
        )
        (agents_dir / "user-agent.toml").write_text('name = "user-agent"\n')

        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            removed = _remove_codex_review_agents()

        assert removed == 2
        assert not (agents_dir / "spec-review.toml").exists()
        assert not (agents_dir / "changes-review.toml").exists()
        assert (agents_dir / "user-agent.toml").exists()

    def test_preserves_unmarked_same_name_review_agents(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / ".codex" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "spec-review.toml").write_text('name = "spec-review"\n')

        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            removed = _remove_codex_review_agents()

        assert removed == 0
        assert (agents_dir / "spec-review.toml").exists()

    def test_removes_managed_review_agents_from_codex_home(self, tmp_path: Path) -> None:
        codex_home = tmp_path / "custom-codex"
        agents_dir = codex_home / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "changes-review.toml").write_text(
            '# pilot-shell managed Codex review agent\nname = "changes-review"\n'
        )

        with (
            patch("codex_skill_sync.Path.home", return_value=tmp_path),
            patch.dict("codex_skill_sync.os.environ", {"CODEX_HOME": str(codex_home)}),
        ):
            removed = _remove_codex_review_agents()

        assert removed == 1
        assert not (agents_dir / "changes-review.toml").exists()


class TestCheckLicense:
    def test_returns_true_when_pilot_missing(self, tmp_path: Path) -> None:
        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            assert _check_license() is True

    def test_returns_true_on_valid_license(self, tmp_path: Path) -> None:
        pilot_bin = tmp_path / ".pilot" / "bin" / "pilot"
        pilot_bin.parent.mkdir(parents=True)
        pilot_bin.write_text("#!/bin/sh\necho '{\"valid\": true}'")
        pilot_bin.chmod(0o755)
        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            with patch("codex_skill_sync.subprocess.run") as mock_run:
                mock_run.return_value.stdout = '{"valid": true}'
                assert _check_license() is True

    def test_returns_false_on_invalid_license(self, tmp_path: Path) -> None:
        pilot_bin = tmp_path / ".pilot" / "bin" / "pilot"
        pilot_bin.parent.mkdir(parents=True)
        pilot_bin.write_text("#!/bin/sh")
        pilot_bin.chmod(0o755)
        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            with patch("codex_skill_sync.subprocess.run") as mock_run:
                mock_run.return_value.stdout = '{"valid": false}'
                assert _check_license() is False

    def test_main_invalid_license_removes_skills_and_review_agents(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        codex_bin = tmp_path / ".codex" / "bin" / "codex"
        codex_bin.parent.mkdir(parents=True)
        codex_bin.write_text("#!/bin/sh\n")
        skill_dir = tmp_path / ".agents" / "skills" / "fix"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("old skill")
        codex_agents_dir = tmp_path / ".codex" / "agents"
        codex_agents_dir.mkdir(parents=True)
        (codex_agents_dir / "spec-review.toml").write_text(
            '# pilot-shell managed Codex review agent\nname = "spec-review"\n'
        )

        with (
            patch("codex_skill_sync.Path.home", return_value=tmp_path),
            patch("codex_skill_sync._check_license", return_value=False),
        ):
            main()

        assert not (skill_dir / "SKILL.md").exists()
        assert not (codex_agents_dir / "spec-review.toml").exists()
        output = json.loads(capsys.readouterr().out)
        assert "removed 2 Codex managed asset(s)" in output["systemMessage"]


class TestSyncCodexEnvVars:
    def test_writes_env_vars_from_config(self, tmp_path: Path) -> None:
        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(
            json.dumps(
                {
                    "specWorkflow": {
                        "planApproval": False,
                        "branchIsolation": True,
                        "askQuestionsDuringPlanning": True,
                    }
                }
            )
        )
        codex_config = tmp_path / ".codex" / "config.toml"
        codex_config.parent.mkdir(parents=True)
        codex_config.write_text('approval_policy = "never"\n')

        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            count = _sync_codex_env_vars()

        assert count == 7
        content = codex_config.read_text()
        assert content.count("[shell_environment_policy.set]") == 1
        assert 'PILOT_PLAN_APPROVAL_ENABLED = "false"' in content
        assert 'PILOT_BRANCH_ISOLATION_ENABLED = "true"' in content
        # Automated model switching is Claude-Code-only -- Codex never gets the var.
        assert "PILOT_MODEL_SWITCH_ENABLED" not in content
        assert 'PILOT_PLAN_QUESTIONS_ENABLED = "true"' in content

    def test_writes_env_vars_to_codex_home_config(self, tmp_path: Path) -> None:
        codex_home = tmp_path / "custom-codex"
        codex_config = codex_home / "config.toml"
        codex_config.parent.mkdir(parents=True)
        codex_config.write_text('approval_policy = "never"\n')

        with (
            patch("codex_skill_sync.Path.home", return_value=tmp_path),
            patch.dict("codex_skill_sync.os.environ", {"CODEX_HOME": str(codex_home)}),
        ):
            count = _sync_codex_env_vars()

        assert count == 7
        assert 'PILOT_CHANGES_REVIEW_ENABLED = "true"' in codex_config.read_text()
        assert not (tmp_path / ".codex" / "config.toml").exists()

    def test_replaces_existing_managed_block(self, tmp_path: Path) -> None:
        config = tmp_path / ".pilot" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"specWorkflow": {"planApproval": True}}))
        codex_config = tmp_path / ".codex" / "config.toml"
        codex_config.parent.mkdir(parents=True)
        codex_config.write_text(
            'approval_policy = "never"\n'
            "\n[shell_environment_policy.set]\n"
            "# --- pilot-shell managed env vars ---\n"
            'PILOT_PLAN_APPROVAL_ENABLED = "false"\n'
            "# --- end pilot-shell managed env vars ---\n"
        )

        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            _sync_codex_env_vars()

        content = codex_config.read_text()
        assert content.count("[shell_environment_policy.set]") == 1
        assert 'PILOT_PLAN_APPROVAL_ENABLED = "true"' in content
        tomllib.loads(content)

    def test_does_not_duplicate_section_header_when_codex_config_already_has_one(
        self, tmp_path: Path
    ) -> None:
        codex_config = tmp_path / ".codex" / "config.toml"
        codex_config.parent.mkdir(parents=True)
        codex_config.write_text(
            'approval_policy = "never"\n'
            "\n[shell_environment_policy.set]\n"
            "SOME_EXISTING_VAR = \"1\"\n"
        )

        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            _sync_codex_env_vars()

        content = codex_config.read_text()
        assert content.count("[shell_environment_policy.set]") == 1
        assert "SOME_EXISTING_VAR" in content
        tomllib.loads(content)

    def test_defaults_branch_isolation_to_true_when_config_missing(self, tmp_path: Path) -> None:
        """When config.json is absent, branchIsolation should default to true (matching Console)."""
        codex_config = tmp_path / ".codex" / "config.toml"
        codex_config.parent.mkdir(parents=True)
        codex_config.write_text('approval_policy = "never"\n')

        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            _sync_codex_env_vars()

        content = codex_config.read_text()
        assert 'PILOT_BRANCH_ISOLATION_ENABLED = "true"' in content

    def test_noop_when_no_codex_config(self, tmp_path: Path) -> None:
        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            assert _sync_codex_env_vars() == 0
