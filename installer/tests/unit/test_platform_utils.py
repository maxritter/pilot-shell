"""Tests for platform utilities module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


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


class TestEnsureBunOnPath:
    """Test ensure_bun_on_path: bun discovery when PATH alone does not show it."""

    def test_returns_true_without_touching_path_when_bun_is_already_on_path(self):
        """An already-visible bun needs no PATH surgery."""
        import os

        from installer.platform_utils import ensure_bun_on_path

        before = os.environ.get("PATH", "")
        with patch("installer.platform_utils.command_exists", return_value=True):
            assert ensure_bun_on_path() is True
        assert os.environ.get("PATH", "") == before

    def test_finds_standalone_bun_that_is_not_on_path(self, tmp_path: Path):
        """The case that made a machine WITH bun install its deps with npm.

        bun's standalone installer only appends its PATH export to the user's shell rc
        files, which a non-interactive installer process never sources.
        """
        import os

        from installer.platform_utils import ensure_bun_on_path

        bun_bin = tmp_path / ".bun" / "bin"
        bun_bin.mkdir(parents=True)
        bun = bun_bin / "bun"
        bun.write_text("#!/bin/sh\n")
        bun.chmod(0o755)

        original = os.environ.get("PATH", "")
        try:
            with (
                patch("installer.platform_utils.command_exists", return_value=False),
                patch.object(Path, "home", return_value=tmp_path),
            ):
                assert ensure_bun_on_path() is True
            assert str(bun_bin) in os.environ["PATH"]
        finally:
            os.environ["PATH"] = original


class TestCodexDetection:
    def test_includes_chatgpt_desktop_app_binary(self):
        from installer.platform_utils import is_codex_installed

        with patch("installer.platform_utils._agent_present", return_value=True) as present:
            assert is_codex_installed() is True

        fallback_paths = present.call_args.args[1:]
        assert Path.home() / "Applications" / "ChatGPT.app" / "Contents" / "Resources" / "codex" in fallback_paths
        assert Path("/Applications/ChatGPT.app/Contents/Resources/codex") in fallback_paths


class TestEnsureBunFallbacks:
    def test_returns_false_when_bun_is_genuinely_absent(self, tmp_path: Path):
        """No bun on PATH and none at ~/.bun/bin means npm really is the only option."""
        import os

        from installer.platform_utils import ensure_bun_on_path

        original = os.environ.get("PATH", "")
        try:
            with (
                patch("installer.platform_utils.command_exists", return_value=False),
                patch.object(Path, "home", return_value=tmp_path),
            ):
                assert ensure_bun_on_path() is False
            assert os.environ.get("PATH", "") == original
        finally:
            os.environ["PATH"] = original

    def test_ignores_a_non_executable_bun(self, tmp_path: Path):
        """A half-written bun file must not be reported as usable."""
        import os

        from installer.platform_utils import ensure_bun_on_path

        bun_bin = tmp_path / ".bun" / "bin"
        bun_bin.mkdir(parents=True)
        (bun_bin / "bun").write_text("")
        (bun_bin / "bun").chmod(0o644)

        original = os.environ.get("PATH", "")
        try:
            with (
                patch("installer.platform_utils.command_exists", return_value=False),
                patch.object(Path, "home", return_value=tmp_path),
            ):
                assert ensure_bun_on_path() is False
        finally:
            os.environ["PATH"] = original


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


class TestNeedsSudo:
    """Test needs_sudo detection."""

    def test_needs_sudo_true_when_npm_needs_sudo(self):
        from installer.platform_utils import needs_sudo

        with patch("installer.platform_utils.needs_npm_sudo", return_value=True):
            assert needs_sudo() is True

    def test_needs_sudo_false_when_npm_does_not_need_sudo(self):
        from installer.platform_utils import needs_sudo

        with patch("installer.platform_utils.needs_npm_sudo", return_value=False):
            assert needs_sudo() is False


class TestEnsureSudoCredentials:
    """Test sudo credential priming."""

    def test_ensure_sudo_returns_true_on_success(self):
        from installer.platform_utils import ensure_sudo_credentials

        with patch("installer.platform_utils.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            assert ensure_sudo_credentials() is True
            mock_run.assert_called_once_with(["sudo", "-v"], timeout=60)

    def test_ensure_sudo_returns_false_on_failure(self):
        from installer.platform_utils import ensure_sudo_credentials

        with patch("installer.platform_utils.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            assert ensure_sudo_credentials() is False

    def test_ensure_sudo_returns_false_when_sudo_missing(self):
        from installer.platform_utils import ensure_sudo_credentials

        with patch("installer.platform_utils.subprocess.run", side_effect=FileNotFoundError):
            assert ensure_sudo_credentials() is False

    def test_ensure_sudo_returns_false_on_timeout(self):
        import subprocess

        from installer.platform_utils import ensure_sudo_credentials

        with patch(
            "installer.platform_utils.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="sudo -v", timeout=60),
        ):
            assert ensure_sudo_credentials() is False
