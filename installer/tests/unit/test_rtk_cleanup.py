"""Retired command rewriting must disappear on upgrades, even without its binary."""

import json
from pathlib import Path

from installer.rtk_cleanup import remove_rtk


def test_upgrade_removes_hooks_and_instructions_without_binary(tmp_path: Path) -> None:
    manifest = tmp_path / ".pilot/.pilot-owned-tools.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"tools": ["rtk"]}))
    claude = tmp_path / "custom-claude"
    codex = tmp_path / "custom-codex"
    claude.mkdir()
    codex.mkdir()
    user_hook = {"type": "command", "command": "user-audit"}
    for path in (claude / "settings.json", codex / "hooks.json"):
        path.write_text(
            json.dumps(
                {
                    "model": "keep",
                    "hooks": {
                        "PreToolUse": [
                            {
                                "matcher": "Bash",
                                "hooks": [
                                    user_hook,
                                    {"type": "command", "command": "rtk hook"},
                                    {"type": "command", "command": 'python "$HOME/.pilot/hooks/tool_token_saver.py"'},
                                ],
                            }
                        ]
                    },
                }
            )
        )
    for profile, name in ((claude, "CLAUDE.md"), (codex, "AGENTS.md")):
        (profile / name).write_text(
            "User rules\n@RTK.md\n<!-- rtk-instructions v2 -->\nUse rtk\n<!-- /rtk-instructions -->\nMore rules\n"
        )
        (profile / "RTK.md").write_text("# RTK - Rust Token Killer\n")
    hook = claude / "hooks" / "rtk-rewrite.sh"
    hook.parent.mkdir()
    hook.write_text("legacy rewrite")

    remove_rtk(home=tmp_path, claude_dir=claude, codex_dir=codex)

    for path in (claude / "settings.json", codex / "hooks.json"):
        data = json.loads(path.read_text())
        assert data["model"] == "keep"
        assert data["hooks"]["PreToolUse"][0]["hooks"] == [user_hook]
    for profile, name in ((claude, "CLAUDE.md"), (codex, "AGENTS.md")):
        assert (profile / name).read_text() == "User rules\nMore rules\n"
        assert not (profile / "RTK.md").exists()
    assert not hook.exists()
    remove_rtk(home=tmp_path, claude_dir=claude, codex_dir=codex)


def test_upgrade_removes_only_pilot_owned_binary(tmp_path: Path) -> None:
    binary = tmp_path / ".local/bin/rtk"
    binary.parent.mkdir(parents=True)
    binary.write_text("owned binary")
    pilot = tmp_path / ".pilot"
    (pilot / "bin").mkdir(parents=True)
    link = pilot / "bin/rtk"
    link.symlink_to(binary)
    manifest = pilot / ".pilot-owned-tools.json"
    manifest.write_text(json.dumps({"schema": 1, "tools": ["rtk", "semble"]}))

    remove_rtk(home=tmp_path, claude_dir=tmp_path / ".claude", codex_dir=tmp_path / ".codex")

    assert not binary.exists()
    assert not link.is_symlink()
    assert json.loads(manifest.read_text())["tools"] == ["semble"]


def test_user_binary_is_preserved_and_dangling_pilot_link_removed(tmp_path: Path) -> None:
    binary = tmp_path / ".local/bin/rtk"
    binary.parent.mkdir(parents=True)
    binary.write_text("user binary")
    link = tmp_path / ".pilot/bin/rtk"
    link.parent.mkdir(parents=True)
    link.symlink_to(tmp_path / "absent")

    remove_rtk(home=tmp_path, claude_dir=tmp_path / ".claude", codex_dir=tmp_path / ".codex")

    assert binary.read_text() == "user binary"
    assert not link.is_symlink()


def test_owned_alias_is_removed_without_deleting_a_user_binary(tmp_path: Path) -> None:
    target = tmp_path / "user-rtk"
    target.write_text("user binary")
    alias = tmp_path / ".local/bin/rtk"
    alias.parent.mkdir(parents=True)
    alias.symlink_to(target)
    manifest = tmp_path / ".pilot/.pilot-owned-tools.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"schema": 1, "tools": ["rtk"]}))
    remove_rtk(home=tmp_path, claude_dir=tmp_path / ".claude", codex_dir=tmp_path / ".codex")
    assert not alias.is_symlink()
    assert target.read_text() == "user binary"


def test_malformed_settings_are_preserved(tmp_path: Path) -> None:
    profile = tmp_path / ".claude"
    profile.mkdir()
    settings = profile / "settings.json"
    settings.write_text("{broken user config")
    errors = remove_rtk(home=tmp_path, claude_dir=profile, codex_dir=tmp_path / ".codex")
    assert not errors  # Unrelated malformed user configuration is not an RTK cleanup failure.
    assert settings.read_text() == "{broken user config"


def test_user_owned_rtk_integration_and_data_are_preserved(tmp_path: Path) -> None:
    profile = tmp_path / ".claude"
    profile.mkdir()
    settings = profile / "settings.json"
    content = json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"command": "rtk hook"}]}]}})
    settings.write_text(content)
    (profile / "CLAUDE.md").write_text("@RTK.md\n")
    (profile / "RTK.md").write_text("User RTK setup")
    data = tmp_path / ".config/rtk"
    data.mkdir(parents=True)
    (data / "config").write_text("keep")
    assert not remove_rtk(home=tmp_path, claude_dir=profile, codex_dir=tmp_path / ".codex")
    assert settings.read_text() == content
    assert (profile / "CLAUDE.md").read_text() == "@RTK.md\n"
    assert (profile / "RTK.md").read_text() == "User RTK setup"
    assert (data / "config").read_text() == "keep"


def test_owned_cleanup_failure_retains_scripts_binary_and_ownership_for_retry(tmp_path: Path) -> None:
    profile = tmp_path / ".claude"
    profile.mkdir()
    target = tmp_path / "settings-target"
    target.write_text('{"hooks":{"PreToolUse":[{"hooks":[{"command":"rtk hook"}]}]}}')
    (profile / "settings.json").symlink_to(target)
    (profile / "RTK.md").write_text("owned")
    manifest = tmp_path / ".pilot/.pilot-owned-tools.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"tools": ["rtk"]}))
    binary = tmp_path / ".local/bin/rtk"
    binary.parent.mkdir(parents=True)
    binary.write_text("owned")
    errors = remove_rtk(home=tmp_path, claude_dir=profile, codex_dir=tmp_path / ".codex")
    assert errors and "symlink" in errors[0]
    assert binary.exists() and (profile / "RTK.md").exists()
    assert json.loads(manifest.read_text())["tools"] == ["rtk"]
    (profile / "settings.json").unlink()
    (profile / "settings.json").write_text(target.read_text())
    assert not remove_rtk(home=tmp_path, claude_dir=profile, codex_dir=tmp_path / ".codex")
    assert not binary.exists()
    assert json.loads(manifest.read_text())["tools"] == []
    assert "rtk hook" in target.read_text()


def test_owned_data_is_removed_without_following_aliases_and_blank_lines_survive(tmp_path: Path) -> None:
    manifest = tmp_path / ".pilot/.pilot-owned-tools.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"tools": ["rtk"]}))
    profile = tmp_path / ".claude"
    profile.mkdir()
    (profile / "CLAUDE.md").write_text("Before\n\n@RTK.md\n\nAfter\n")
    target = tmp_path / "user-data"
    target.mkdir()
    (target / "keep").write_text("keep")
    data = tmp_path / ".config/rtk"
    data.parent.mkdir()
    data.symlink_to(target, target_is_directory=True)
    assert not remove_rtk(home=tmp_path, claude_dir=profile, codex_dir=tmp_path / ".codex")
    assert not data.is_symlink()
    assert (target / "keep").read_text() == "keep"
    assert (profile / "CLAUDE.md").read_text() == "Before\n\n\nAfter\n"
