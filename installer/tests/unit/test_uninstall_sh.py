"""Tests for uninstall.sh — Codex cleanup coverage."""

from __future__ import annotations

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


def test_uninstall_sh_codex_hooks_cleanup_uses_pilot_path_marker():
    """Pilot hooks are identified by /.pilot/ in command strings — mirrors _is_pilot_managed_entry."""
    assert "/.pilot/" in _content()


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
    config.write_text(
        'approval_policy = "never"\n'
        f'model_catalog_json = "{catalog}"\n'
        'model = "gpt-5.6-sol"\n'
    )

    result = _run_uninstall(home)

    assert result.returncode == 0, result.stderr
    assert not catalog.exists()
    codex_config = config.read_text()
    assert "model_catalog_json" not in codex_config
    assert 'approval_policy = "never"' in codex_config
    assert 'model = "gpt-5.6-sol"' in codex_config
