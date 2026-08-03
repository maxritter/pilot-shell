"""Tests for the installer's Claude config-directory resolvers."""

from __future__ import annotations

from pathlib import Path

import pytest

from installer.claude_paths import get_claude_app_config_path, get_claude_config_dir


class TestGetClaudeConfigDir:
    """Resolution of the Claude config directory."""

    def test_unset_returns_home_claude(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

        assert get_claude_config_dir() == tmp_path / ".claude"

    def test_absolute_value_is_used(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        custom = tmp_path / ".claude_work"
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(custom))

        assert get_claude_config_dir() == custom

    @pytest.mark.parametrize("bad", ["relative/path", ".claude_work", "", "   "])
    def test_set_but_invalid_raises(self, monkeypatch: pytest.MonkeyPatch, bad: str) -> None:
        """Fail closed: a set-but-invalid value must never resolve to ~/.claude.

        Falling back to the default would point Pilot at the personal profile
        precisely when the user was trying to avoid it.
        """
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", bad)

        with pytest.raises(ValueError, match="CLAUDE_CONFIG_DIR"):
            get_claude_config_dir()


class TestGetClaudeAppConfigPath:
    """Resolution of Claude Code's app-config JSON.

    Mirrors Claude Code 2.1.220:
        if exists(<config_dir>/.config.json): -> that file
        else: -> (CLAUDE_CONFIG_DIR or $HOME)/.claude.json
    """

    def test_unset_returns_home_dot_claude_json(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Unset means $HOME/.claude.json, NOT ~/.claude/.claude.json."""
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

        assert get_claude_app_config_path() == tmp_path / ".claude.json"

    def test_set_returns_config_dir_dot_claude_json(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        custom = tmp_path / ".claude_work"
        custom.mkdir()
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(custom))

        assert get_claude_app_config_path() == custom / ".claude.json"

    def test_dot_config_json_takes_precedence_when_set(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        custom = tmp_path / ".claude_work"
        custom.mkdir()
        (custom / ".config.json").write_text("{}")
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(custom))

        assert get_claude_app_config_path() == custom / ".config.json"

    def test_dot_config_json_takes_precedence_when_unset(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """A default-dir user with ~/.claude/.config.json resolves there too."""
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / ".config.json").write_text("{}")

        assert get_claude_app_config_path() == claude_dir / ".config.json"

    def test_set_but_invalid_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", "relative/path")

        with pytest.raises(ValueError, match="CLAUDE_CONFIG_DIR"):
            get_claude_app_config_path()
