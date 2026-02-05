"""Tests for platform utilities module."""

from __future__ import annotations

from pathlib import Path


class TestCommandExists:
    """Test command_exists function."""

    def test_command_exists_finds_common_commands(self):
        """command_exists finds common system commands."""
        from installer.platform_utils import command_exists

        assert command_exists("ls") is True
        assert command_exists("cat") is True

    def test_command_exists_returns_false_for_nonexistent(self):
        """command_exists returns False for nonexistent commands."""
        from installer.platform_utils import command_exists

        assert command_exists("definitely_not_a_real_command_12345") is False


class TestShellConfig:
    """Test shell configuration utilities."""

    def test_get_shell_config_files_returns_list(self):
        """get_shell_config_files returns list of paths."""
        from installer.platform_utils import get_shell_config_files

        result = get_shell_config_files()
        assert isinstance(result, list)
        for path in result:
            assert isinstance(path, Path)

    def test_shell_config_files_includes_common_shells(self):
        """get_shell_config_files includes common shell configs."""
        from installer.platform_utils import get_shell_config_files

        result = get_shell_config_files()
        path_names = [p.name for p in result]
        common_configs = [".bashrc", ".zshrc", "config.fish"]
        assert any(name in path_names for name in common_configs)


class TestIsInDevcontainer:
    """Test devcontainer detection."""

    def test_is_in_devcontainer_returns_bool(self):
        """is_in_devcontainer returns boolean."""
        from installer.platform_utils import is_in_devcontainer

        result = is_in_devcontainer()
        assert isinstance(result, bool)


class TestIsAptAvailable:
    """Test apt availability detection."""

    def test_is_apt_available_returns_bool(self):
        """is_apt_available returns boolean."""
        from installer.platform_utils import is_apt_available

        result = is_apt_available()
        assert isinstance(result, bool)


class TestIsLinux:
    """Test Linux platform detection."""

    def test_is_linux_returns_bool(self):
        """is_linux returns boolean."""
        from installer.platform_utils import is_linux

        result = is_linux()
        assert isinstance(result, bool)

    def test_is_linux_matches_platform(self):
        """is_linux matches platform.system() check."""
        import platform

        from installer.platform_utils import is_linux

        expected = platform.system() == "Linux"
        assert is_linux() == expected
