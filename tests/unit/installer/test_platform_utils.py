"""Tests for platform utilities module."""

from __future__ import annotations

from pathlib import Path


class TestCommandExists:
    """Test command_exists function."""

    def test_command_exists_finds_common_commands(self):
        """command_exists finds common system commands."""
        from installer.platform_utils import command_exists

        # These should exist on any Unix-like system
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
        # Should include at least one of these common configs
        common_configs = [".bashrc", ".zshrc", "config.fish"]
        assert any(name in path_names for name in common_configs)


class TestIsInDevcontainer:
    """Test devcontainer detection."""

    def test_is_in_devcontainer_returns_bool(self):
        """is_in_devcontainer returns boolean."""
        from installer.platform_utils import is_in_devcontainer

        result = is_in_devcontainer()
        assert isinstance(result, bool)


class TestPlatformDetection:
    """Test platform detection functions."""

    def test_is_macos_returns_bool(self):
        """is_macos returns boolean."""
        from installer.platform_utils import is_macos

        result = is_macos()
        assert isinstance(result, bool)

    def test_is_linux_returns_bool(self):
        """is_linux returns boolean."""
        from installer.platform_utils import is_linux

        result = is_linux()
        assert isinstance(result, bool)

    def test_is_windows_returns_bool(self):
        """is_windows returns boolean."""
        from installer.platform_utils import is_windows

        result = is_windows()
        assert isinstance(result, bool)

    def test_is_wsl_returns_bool(self):
        """is_wsl returns boolean."""
        from installer.platform_utils import is_wsl

        result = is_wsl()
        assert isinstance(result, bool)

    def test_is_wsl_false_on_non_linux(self):
        """is_wsl returns False when not on Linux."""
        from unittest.mock import patch

        from installer.platform_utils import is_wsl

        with patch("installer.platform_utils.is_linux", return_value=False):
            assert is_wsl() is False


class TestHasNvidiaGpu:
    """Test NVIDIA GPU detection."""

    def test_returns_true_when_nvidia_smi_succeeds(self):
        """has_nvidia_gpu returns True when nvidia-smi succeeds."""
        from unittest.mock import MagicMock, patch

        from installer.platform_utils import has_nvidia_gpu

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"NVIDIA-SMI 535.104.05"
        mock_result.stderr = b""

        with patch("subprocess.run", return_value=mock_result):
            assert has_nvidia_gpu() is True

    def test_returns_false_when_nvidia_smi_fails(self):
        """has_nvidia_gpu returns False when nvidia-smi fails with non-zero."""
        from unittest.mock import MagicMock, patch

        from installer.platform_utils import has_nvidia_gpu

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = b""
        mock_result.stderr = b"command not found"

        with patch("subprocess.run", return_value=mock_result):
            with patch("pathlib.Path.glob", return_value=[]):
                assert has_nvidia_gpu() is False

    def test_returns_false_when_nvidia_smi_not_found(self):
        """has_nvidia_gpu returns False when nvidia-smi is not found."""
        from unittest.mock import patch

        from installer.platform_utils import has_nvidia_gpu

        with patch("subprocess.run", side_effect=FileNotFoundError("nvidia-smi not found")):
            with patch("pathlib.Path.glob", return_value=[]):
                assert has_nvidia_gpu() is False

    def test_returns_false_on_timeout(self):
        """has_nvidia_gpu returns False when nvidia-smi times out."""
        import subprocess
        from unittest.mock import patch

        from installer.platform_utils import has_nvidia_gpu

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("nvidia-smi", 10)):
            with patch("pathlib.Path.glob", return_value=[]):
                assert has_nvidia_gpu() is False

    def test_verbose_mode_returns_dict(self):
        """has_nvidia_gpu with verbose=True returns dict with diagnostic info."""
        from unittest.mock import MagicMock, patch

        from installer.platform_utils import has_nvidia_gpu

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"NVIDIA-SMI 535.104.05"
        mock_result.stderr = b""

        with patch("subprocess.run", return_value=mock_result):
            result = has_nvidia_gpu(verbose=True)

            assert isinstance(result, dict)
            assert result["detected"] is True
            assert result["method"] == "nvidia_smi"

    def test_fallback_to_dev_nvidia(self):
        """has_nvidia_gpu falls back to /dev/nvidia* when nvidia-smi fails."""
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from installer.platform_utils import has_nvidia_gpu

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = b"not found"

        mock_devices = [Path("/dev/nvidia0"), Path("/dev/nvidiactl")]

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(Path, "glob", return_value=mock_devices):
                assert has_nvidia_gpu() is True

    def test_verbose_fallback_shows_dev_nvidia_method(self):
        """has_nvidia_gpu verbose mode shows dev_nvidia method when using fallback."""
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from installer.platform_utils import has_nvidia_gpu

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = b"not found"

        mock_devices = [Path("/dev/nvidia0")]

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(Path, "glob", return_value=mock_devices):
                result = has_nvidia_gpu(verbose=True)

                assert isinstance(result, dict)
                assert result["detected"] is True
                assert result["method"] == "dev_nvidia"
