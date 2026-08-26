"""Tests for uninstall.sh — Codex cleanup coverage."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

UNINSTALL_SH = Path(__file__).parent.parent.parent.parent / "uninstall.sh"


def _content() -> str:
    return UNINSTALL_SH.read_text()


def test_uninstall_sh_has_remove_codex_files_function():
    """uninstall.sh must define a remove_codex_files function."""
    assert "remove_codex_files()" in _content()


def test_uninstall_sh_remove_codex_files_called_in_main_flow():
    """remove_codex_files must be called in the main uninstall sequence."""
    content = _content()
    assert content.count("remove_codex_files") >= 2, (
        "Expected at least 2 occurrences: the function definition and a call site"
    )


def test_uninstall_sh_codex_dir_respects_codex_home():
    """CODEX_DIR must be defined honouring the CODEX_HOME env var."""
    content = _content()
    assert "CODEX_HOME" in content
    assert ".codex" in content


def test_uninstall_sh_agents_skills_dir_defined():
    """~/.agents/skills path must be referenced for skills cleanup."""
    assert ".agents/skills" in _content()


def test_uninstall_sh_codex_hooks_cleanup_uses_install_baseline():
    """Codex hook cleanup uses exact installed signatures, not a broad path match."""
    assert ".pilot-hooks-baseline.json" in _content()


def test_uninstall_sh_codex_config_toml_mcp_block_removed():
    """Managed MCP block start marker must be present so the removal logic can strip it."""
    assert "pilot-shell managed MCP servers" in _content()


def test_uninstall_sh_codex_agents_md_cleaned():
    """AGENTS.md cleanup must use the PILOT:START and PILOT:END markers."""
    content = _content()
    assert "PILOT:START" in content
    assert "PILOT:END" in content


def test_uninstall_sh_codex_skills_removed():
    """Known Pilot skill names must appear in the skills cleanup block."""
    content = _content()
    assert "spec-plan" in content
    assert "spec-implement" in content
    assert "spec-bugfix-plan" in content
    assert '"build"' in content
    assert '"investigate"' in content
    assert '"cleanup"' in content


def test_uninstall_sh_documents_complete_code_search_tool_cleanup() -> None:
    """Third-party cleanup names current tools and the legacy native dependency."""
    content = _content()
    assert "npm uninstall -g @colbymchenry/codegraph" in content
    assert "semble clear all" in content
    assert "uv tool uninstall semble" in content
    assert "uv cache clean semble" in content
    assert "npm uninstall -g better-sqlite3" in content


def test_uninstall_sh_preserves_project_codegraph_indexes() -> None:
    """Global cleanup guidance must not suggest recursively deleting project indexes."""
    content = _content()
    assert "Project indexes (.codegraph/) were intentionally left intact." in content
    assert "codegraph uninit" in content
    assert "rm -rf .codegraph" not in content


def test_uninstall_sh_claude_dir_respects_claude_config_dir():
    """CLAUDE_DIR must honour CLAUDE_CONFIG_DIR, mirroring CODEX_DIR/CODEX_HOME."""
    assert "CLAUDE_CONFIG_DIR" in _content()


def _run_uninstall(home: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    env.pop("CODEX_HOME", None)
    env.pop("CLAUDE_CONFIG_DIR", None)
    env.update(extra_env or {})
    return subprocess.run(["bash", str(UNINSTALL_SH), "--yes"], env=env, text=True, capture_output=True, check=False)


def _seed_pilot_profile(claude_dir: Path) -> None:
    """Minimal Pilot-installed profile: a manifest plus one managed rule."""
    (claude_dir / "rules").mkdir(parents=True, exist_ok=True)
    (claude_dir / "rules" / "testing.md").write_text("managed\n")
    (claude_dir / ".pilot-manifest.json").write_text('{"files": ["rules/testing.md"]}\n')


class TestClaudeConfigDirIsolation:
    """uninstall.sh derives rm targets, so its path resolution is safety-critical."""

    def test_relative_config_dir_aborts_before_removing_anything(self, tmp_path: Path):
        """A relative value must abort, never resolve rm targets against cwd."""
        home = tmp_path / "home"
        personal = home / ".claude"
        _seed_pilot_profile(personal)

        result = _run_uninstall(home, {"CLAUDE_CONFIG_DIR": "relative/path"})

        assert result.returncode != 0, "expected a non-zero exit for a relative CLAUDE_CONFIG_DIR"
        assert (personal / "rules" / "testing.md").exists(), "personal profile was touched"
        assert (personal / ".pilot-manifest.json").exists()

    def test_explicit_config_dir_without_pilot_install_aborts(self, tmp_path: Path):
        """Pointing at a profile Pilot was never installed into must not half-clean."""
        home = tmp_path / "home"
        personal = home / ".claude"
        _seed_pilot_profile(personal)
        empty = home / ".claude_empty"
        empty.mkdir(parents=True)

        result = _run_uninstall(home, {"CLAUDE_CONFIG_DIR": str(empty)})

        assert result.returncode != 0
        assert "No Pilot install found" in result.stderr
        assert (personal / "rules" / "testing.md").exists()

    def test_missing_manifest_still_tolerated_when_unset(self, tmp_path: Path):
        """Legacy pre-manifest installs must still uninstall from the default dir."""
        home = tmp_path / "home"
        (home / ".claude").mkdir(parents=True)
        (home / ".pilot").mkdir(parents=True)

        result = _run_uninstall(home)

        assert result.returncode == 0, result.stderr
        assert not (home / ".pilot").exists(), "~/.pilot should still be removed"

    def test_custom_config_dir_leaves_personal_profile_untouched(self, tmp_path: Path):
        home = tmp_path / "home"
        personal = home / ".claude"
        _seed_pilot_profile(personal)
        work = home / ".claude_work"
        _seed_pilot_profile(work)

        result = _run_uninstall(home, {"CLAUDE_CONFIG_DIR": str(work)})

        assert result.returncode == 0, result.stderr
        assert not (work / "rules" / "testing.md").exists(), "custom profile was not cleaned"
        assert (personal / "rules" / "testing.md").exists(), "personal profile was cleaned"
        assert (personal / ".pilot-manifest.json").exists()


def test_uninstall_removes_shell_wrappers_and_codex_env_block(tmp_path: Path):
    """Uninstall should remove Pilot shell wrappers and Codex managed env vars."""
    home = tmp_path / "home"
    home.mkdir()
    zshrc = home / ".zshrc"
    zshrc.write_text(
        "\n".join(
            [
                "# before",
                "# Pilot Shell",
                'export PATH="$HOME/.pilot/bin:$HOME/.bun/bin:$PATH"',
                'alias pilot="$HOME/.pilot/bin/pilot"',
                'alias ccp="$HOME/.pilot/bin/pilot"',
                'claude() { local _sid="$$-$RANDOM"; PILOT_SESSION_ID=$_sid CLAUDE_CODE_TASK_LIST_ID="pilot-$_sid" command claude "$@"; }',
                'codex() { PILOT_SESSION_ID="$$-$RANDOM" command codex "$@"; }',
                "# after",
                "",
            ]
        )
    )

    codex_dir = home / ".codex"
    codex_dir.mkdir()
    (codex_dir / "config.toml").write_text(
        "\n".join(
            [
                'approval_policy = "never"',
                "# --- pilot-shell managed env vars ---",
                "[shell_environment_policy.set]",
                'PILOT_PLAN_APPROVAL_ENABLED = "false"',
                "# --- end pilot-shell managed env vars ---",
                'model = "gpt-5"',
                "",
            ]
        )
    )

    env = os.environ.copy()
    env["HOME"] = str(home)
    env.pop("CODEX_HOME", None)
    result = subprocess.run(["bash", str(UNINSTALL_SH), "--yes"], env=env, text=True, capture_output=True, check=False)

    assert result.returncode == 0, result.stderr
    shell_content = zshrc.read_text()
    assert "claude()" not in shell_content
    assert "codex()" not in shell_content
    assert "alias pilot=" not in shell_content
    assert "# before" in shell_content
    assert "# after" in shell_content

    codex_config = (codex_dir / "config.toml").read_text()
    assert "pilot-shell managed env vars" not in codex_config
    assert "PILOT_PLAN_APPROVAL_ENABLED" not in codex_config
    assert 'approval_policy = "never"' in codex_config
    assert 'model = "gpt-5"' in codex_config


def test_uninstall_removes_pilot_model_catalog_and_preserves_codex_config(tmp_path: Path):
    home = tmp_path / "home"
    codex_dir = home / ".codex"
    codex_dir.mkdir(parents=True)
    catalog = codex_dir / ".pilot-model-catalog.json"
    catalog.write_text('{"models": []}\n')
    config = codex_dir / "config.toml"
    config.write_text(f'approval_policy = "never"\nmodel_catalog_json = "{catalog}"\nmodel = "gpt-5.6-sol"\n')

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    assert not catalog.exists()
    codex_config = config.read_text()
    assert "model_catalog_json" not in codex_config
    assert 'approval_policy = "never"' in codex_config
    assert 'model = "gpt-5.6-sol"' in codex_config


def test_uninstall_removes_baselined_codex_hook_and_preserves_user_pilot_hook(tmp_path: Path):
    home = tmp_path / "home"
    codex_dir = home / ".codex"
    codex_dir.mkdir(parents=True)
    managed = {"hooks": [{"type": "command", "command": 'python "$HOME/.pilot/hooks/stop.py"'}]}
    user = {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": 'python "$HOME/.pilot/custom/my-hook.py"'}],
    }
    (codex_dir / "hooks.json").write_text(json.dumps({"hooks": {"Stop": [managed], "PreToolUse": [user]}}))
    (codex_dir / ".pilot-hooks-baseline.json").write_text(json.dumps({"Stop": [managed]}))

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    hooks = json.loads((codex_dir / "hooks.json").read_text())["hooks"]
    assert "Stop" not in hooks
    assert hooks["PreToolUse"] == [user]
    assert not (codex_dir / ".pilot-hooks-baseline.json").exists()


def test_uninstall_removes_generated_investigate_artifacts_and_preserves_user_files(tmp_path: Path):
    home = tmp_path / "home"
    skill_dir = home / ".agents" / "skills" / "investigate"
    references = skill_dir / "references"
    metadata_dir = skill_dir / "agents"
    references.mkdir(parents=True)
    metadata_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("generated skill\n")
    (metadata_dir / "openai.yaml").write_text("policy: {}\n")
    (references / "managed.md").write_text("managed\n")
    (references / "user-notes.md").write_text("keep\n")
    (skill_dir / "user-file.txt").write_text("keep\n")
    (skill_dir / ".pilot-resources.json").write_text(
        json.dumps({"files": ["references/managed.md"], "directories": ["references"]})
    )

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    assert not (skill_dir / "SKILL.md").exists()
    assert not (metadata_dir / "openai.yaml").exists()
    assert not (skill_dir / ".pilot-resources.json").exists()
    assert not (references / "managed.md").exists()
    assert (references / "user-notes.md").read_text() == "keep\n"
    assert (skill_dir / "user-file.txt").read_text() == "keep\n"


def test_uninstall_detects_and_removes_generated_cleanup_skill(tmp_path: Path):
    """A cleanup-only Codex install is still Pilot content and fully reversible."""
    home = tmp_path / "home"
    skill_dir = home / ".agents" / "skills" / "cleanup"
    steps_dir = skill_dir / "steps"
    metadata_dir = skill_dir / "agents"
    steps_dir.mkdir(parents=True)
    metadata_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("generated cleanup skill\n")
    (metadata_dir / "openai.yaml").write_text("policy: {}\n")
    (steps_dir / "01-scope.md").write_text("managed\n")
    (skill_dir / ".pilot-resources.json").write_text(
        json.dumps({"files": ["steps/01-scope.md"], "directories": ["steps"]})
    )

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    assert not skill_dir.exists()


def test_uninstall_removes_cleanup_resources_and_preserves_user_files(tmp_path: Path):
    home = tmp_path / "home"
    skill_dir = home / ".agents" / "skills" / "cleanup"
    steps_dir = skill_dir / "steps"
    scripts_dir = skill_dir / "scripts"
    metadata_dir = skill_dir / "agents"
    steps_dir.mkdir(parents=True)
    scripts_dir.mkdir()
    metadata_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("generated cleanup skill\n")
    (metadata_dir / "openai.yaml").write_text("policy: {}\n")
    (steps_dir / "01-scope.md").write_text("managed\n")
    (scripts_dir / "codegraph-candidates.mjs").write_text("managed\n")
    (scripts_dir / "user-helper.mjs").write_text("keep\n")
    (skill_dir / "user-notes.md").write_text("keep\n")
    (skill_dir / ".pilot-resources.json").write_text(
        json.dumps(
            {
                "files": ["steps/01-scope.md", "scripts/codegraph-candidates.mjs"],
                "directories": ["steps", "scripts"],
            }
        )
    )

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    assert not (skill_dir / "SKILL.md").exists()
    assert not (metadata_dir / "openai.yaml").exists()
    assert not (steps_dir / "01-scope.md").exists()
    assert not (scripts_dir / "codegraph-candidates.mjs").exists()
    assert (scripts_dir / "user-helper.mjs").read_text() == "keep\n"
    assert (skill_dir / "user-notes.md").read_text() == "keep\n"


def test_uninstall_malformed_skill_resource_manifest_preserves_unknown_files(tmp_path: Path):
    home = tmp_path / "home"
    skill_dir = home / ".agents" / "skills" / "investigate"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("generated skill\n")
    (skill_dir / ".pilot-resources.json").write_text("{broken")
    (skill_dir / "unknown-resource.txt").write_text("keep\n")

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    assert not (skill_dir / "SKILL.md").exists()
    assert not (skill_dir / ".pilot-resources.json").exists()
    assert (skill_dir / "unknown-resource.txt").read_text() == "keep\n"


def test_uninstall_preserves_unowned_same_name_investigate_skill(tmp_path: Path):
    home = tmp_path / "home"
    skill_dir = home / ".agents" / "skills" / "investigate"
    metadata_dir = skill_dir / "agents"
    metadata_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("user-owned investigate\n")
    (metadata_dir / "openai.yaml").write_text("user-owned metadata\n")

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    assert (skill_dir / "SKILL.md").read_text() == "user-owned investigate\n"
    assert (metadata_dir / "openai.yaml").read_text() == "user-owned metadata\n"


def test_uninstall_preserves_unowned_same_name_cleanup_skill(tmp_path: Path):
    home = tmp_path / "home"
    skill_dir = home / ".agents" / "skills" / "cleanup"
    metadata_dir = skill_dir / "agents"
    metadata_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("user-owned cleanup\n")
    (metadata_dir / "openai.yaml").write_text("user-owned metadata\n")

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    assert (skill_dir / "SKILL.md").read_text() == "user-owned cleanup\n"
    assert (metadata_dir / "openai.yaml").read_text() == "user-owned metadata\n"
