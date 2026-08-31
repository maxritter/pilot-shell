"""Manifest-owned rules and agents suspend without touching user files."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from pilot.hooks import licensed_assets_sync


def _seed(tmp_path: Path) -> tuple[Path, Path]:
    claude = tmp_path / ".claude"
    codex = tmp_path / ".codex"
    (claude / "rules").mkdir(parents=True)
    (claude / "agents").mkdir()
    (claude / "rules" / "pilot.md").write_text("pilot rule\n")
    (claude / "rules" / "user.md").write_text("user rule\n")
    (claude / "agents" / "review.md").write_text("pilot agent\n")
    (claude / ".pilot-manifest.json").write_text(json.dumps({"files": ["rules/pilot.md", "agents/review.md"]}))

    (codex / "rules").mkdir(parents=True)
    (codex / "rules" / "pilot.rules").write_text("pilot codex rule\n")
    (codex / "rules" / "user.rules").write_text("user codex rule\n")
    (codex / "rules" / ".pilot-rules.json").write_text('["pilot.rules"]\n')
    (codex / "AGENTS.md").write_text(
        "user before\n\n<!-- PILOT:START -->\npilot instructions\n<!-- PILOT:END -->\n\nuser after\n"
    )
    return claude, codex


def test_suspend_and_restore_exact_managed_assets(tmp_path: Path) -> None:
    claude, codex = _seed(tmp_path)
    with (
        patch("pilot.hooks.licensed_assets_sync.Path.home", return_value=tmp_path),
        patch("pilot.hooks.licensed_assets_sync.claude_config_dir", return_value=claude),
        patch.dict("pilot.hooks.licensed_assets_sync.os.environ", {"CODEX_HOME": str(codex)}),
    ):
        assert licensed_assets_sync.suspend_assets() == 4

        assert not (claude / "rules" / "pilot.md").exists()
        assert not (claude / "agents" / "review.md").exists()
        assert (claude / "rules" / "user.md").read_text() == "user rule\n"
        assert not (codex / "rules" / "pilot.rules").exists()
        assert (codex / "rules" / "user.rules").read_text() == "user codex rule\n"
        agents_inactive = (codex / "AGENTS.md").read_text()
        assert "pilot instructions" not in agents_inactive
        assert "user before" in agents_inactive and "user after" in agents_inactive

        assert licensed_assets_sync.restore_assets() == 4

    assert (claude / "rules" / "pilot.md").read_text() == "pilot rule\n"
    assert (claude / "agents" / "review.md").read_text() == "pilot agent\n"
    assert (codex / "rules" / "pilot.rules").read_text() == "pilot codex rule\n"
    assert "pilot instructions" in (codex / "AGENTS.md").read_text()


def test_restore_does_not_overwrite_user_replacement(tmp_path: Path) -> None:
    claude, codex = _seed(tmp_path)
    with (
        patch("pilot.hooks.licensed_assets_sync.Path.home", return_value=tmp_path),
        patch("pilot.hooks.licensed_assets_sync.claude_config_dir", return_value=claude),
        patch.dict("pilot.hooks.licensed_assets_sync.os.environ", {"CODEX_HOME": str(codex)}),
    ):
        licensed_assets_sync.suspend_assets()
        replacement = claude / "rules" / "pilot.md"
        replacement.write_text("user replacement\n")

        licensed_assets_sync.restore_assets()

    assert replacement.read_text() == "user replacement\n"
    assert (tmp_path / ".pilot" / "inactive-assets" / "claude" / "rules" / "pilot.md").exists()


def test_unknown_license_state_mutates_nothing(tmp_path: Path, capsys) -> None:
    claude, codex = _seed(tmp_path)
    with (
        patch("pilot.hooks.licensed_assets_sync._check_license", return_value=None),
        patch("pilot.hooks.licensed_assets_sync.suspend_assets") as suspend,
        patch("pilot.hooks.licensed_assets_sync.restore_assets") as restore,
    ):
        licensed_assets_sync.main()

    suspend.assert_not_called()
    restore.assert_not_called()
    assert json.loads(capsys.readouterr().out) == {"continue": True}
    assert (claude / "rules" / "pilot.md").exists()
    assert (codex / "rules" / "pilot.rules").exists()


def test_suspend_refuses_manifest_path_through_symlinked_parent(tmp_path: Path) -> None:
    claude = tmp_path / ".claude"
    rules = claude / "rules"
    outside = tmp_path / "outside"
    rules.mkdir(parents=True)
    outside.mkdir()
    protected = outside / "pilot.md"
    protected.write_text("user data\n")
    (rules / "escape").symlink_to(outside, target_is_directory=True)
    (claude / ".pilot-manifest.json").write_text('{"files":["rules/escape/pilot.md"]}\n')

    with (
        patch("pilot.hooks.licensed_assets_sync.Path.home", return_value=tmp_path),
        patch("pilot.hooks.licensed_assets_sync.claude_config_dir", return_value=claude),
        patch("pilot.hooks.licensed_assets_sync._codex_config_dir", return_value=None),
    ):
        assert licensed_assets_sync.suspend_assets() == 0

    assert protected.read_text() == "user data\n"
    assert not (tmp_path / ".pilot" / "inactive-assets").exists()
