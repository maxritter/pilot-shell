"""Tests for browser automation tool installation functions in dependencies step."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestIsAgentBrowserReady:
    """Test _is_agent_browser_ready function."""

    @patch("installer.steps.dependencies.subprocess")
    @patch("installer.steps.dependencies.command_exists")
    def test_returns_false_when_command_not_found(self, mock_cmd, _mock_subprocess):
        """Returns False when agent-browser is not installed."""
        from installer.steps.dependencies import _is_agent_browser_ready

        mock_cmd.return_value = False
        assert _is_agent_browser_ready() is False
        mock_cmd.assert_called_once_with("agent-browser")

    @patch("installer.steps.dependencies.subprocess")
    @patch("installer.steps.dependencies.command_exists")
    def test_returns_true_when_version_succeeds(self, mock_cmd, mock_subprocess):
        """Returns True when agent-browser --version succeeds."""
        from installer.steps.dependencies import _is_agent_browser_ready

        mock_cmd.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.run.return_value = mock_result
        assert _is_agent_browser_ready() is True

    @patch("installer.steps.dependencies.subprocess")
    @patch("installer.steps.dependencies.command_exists")
    def test_returns_false_when_version_fails(self, mock_cmd, mock_subprocess):
        """Returns False when agent-browser --version fails."""
        from installer.steps.dependencies import _is_agent_browser_ready

        mock_cmd.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_subprocess.run.return_value = mock_result
        assert _is_agent_browser_ready() is False

    @patch("installer.steps.dependencies.subprocess")
    @patch("installer.steps.dependencies.command_exists")
    def test_returns_false_on_exception(self, mock_cmd, mock_subprocess):
        """Returns False when subprocess raises exception."""
        from installer.steps.dependencies import _is_agent_browser_ready

        mock_cmd.return_value = True
        mock_subprocess.run.side_effect = OSError("command not found")
        assert _is_agent_browser_ready() is False


class TestInstallAgentBrowser:
    """Test install_agent_browser function."""

    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_updates_npm_and_skips_chrome_when_already_ready(self, mock_ready, mock_run, _mock_npm):
        """Updates npm package but skips Chrome install when already ready."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = True
        mock_run.return_value = True
        assert install_agent_browser() is True
        mock_run.assert_called_once_with("npm install -g agent-browser")

    @patch("platform.system", return_value="Darwin")
    @patch("installer.steps.dependencies.is_linux_arm64", return_value=False)
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_installs_npm_and_chrome_macos(self, mock_ready, mock_run, _mock_npm, _mock_arm, _mock_system):
        """Installs agent-browser via npm then runs install on macOS."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.return_value = True
        assert install_agent_browser() is True
        assert mock_run.call_count == 2
        mock_run.assert_any_call("npm install -g agent-browser")
        mock_run.assert_any_call("agent-browser install", timeout=300)

    @patch("platform.system", return_value="Linux")
    @patch("installer.steps.dependencies.is_linux_arm64", return_value=False)
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_installs_with_deps_on_linux_x86(self, mock_ready, mock_run, _mock_npm, _mock_arm, _mock_system):
        """Installs with --with-deps on Linux x86_64."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.return_value = True
        assert install_agent_browser() is True
        mock_run.assert_any_call("agent-browser install --with-deps", timeout=300)

    @patch("installer.steps.dependencies.is_linux_arm64", return_value=True)
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_installs_chromium_apt_on_linux_arm64(
        self,
        mock_ready,
        mock_run,
        _mock_npm,
        _mock_command_exists,
        _mock_arm,
    ):
        """Installs system chromium via apt on Linux ARM64."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.return_value = True
        assert install_agent_browser() is True
        mock_run.assert_any_call(
            "sudo -n apt-get update -qq && sudo -n apt-get install -y -qq chromium",
            timeout=180,
        )

    @patch("installer.steps.dependencies.is_linux_arm64", return_value=True)
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_returns_false_when_chromium_install_fails_on_linux_arm64(
        self,
        mock_ready,
        mock_run,
        _mock_npm,
        _mock_command_exists,
        _mock_arm,
    ):
        """Returns False when chromium install fails on Linux ARM64."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.side_effect = [True, False]

        assert install_agent_browser() is False

    @patch("installer.steps.dependencies.is_linux_arm64", return_value=True)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_returns_false_when_apt_get_missing_on_linux_arm64(
        self,
        mock_ready,
        mock_run,
        _mock_npm,
        _mock_command_exists,
        _mock_arm,
    ):
        """Returns False when apt-get is unavailable on Linux ARM64."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.return_value = True

        assert install_agent_browser() is False
        mock_run.assert_called_once_with("npm install -g agent-browser")

    @patch("installer.steps.dependencies._is_agent_browser_ready")
    @patch("installer.steps.dependencies._run_bash_with_retry")
    def test_returns_false_when_npm_fails(self, mock_run, mock_ready):
        """Returns False when npm install fails."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.return_value = False
        assert install_agent_browser() is False


class TestIsPlaywrightCliReady:
    """Test _is_playwright_cli_ready function."""

    @patch("installer.steps.dependencies.command_exists")
    def test_returns_false_when_command_not_found(self, mock_cmd):
        """Returns False when playwright-cli is not installed."""
        from installer.steps.dependencies import _is_playwright_cli_ready

        mock_cmd.return_value = False
        assert _is_playwright_cli_ready() is False
        mock_cmd.assert_called_once_with("playwright-cli")

    @patch("installer.steps.dependencies._get_playwright_cache_dirs")
    @patch("installer.steps.dependencies.command_exists")
    def test_returns_true_when_chromium_installed(self, mock_cmd, mock_dirs, tmp_path):
        """Returns True when playwright-cli exists and Chromium is installed."""
        from installer.steps.dependencies import _is_playwright_cli_ready

        mock_cmd.return_value = True
        cache_dir = tmp_path / "ms-playwright"
        chromium_dir = cache_dir / "chromium-1234"
        chromium_dir.mkdir(parents=True)
        (chromium_dir / "INSTALLATION_COMPLETE").touch()
        mock_dirs.return_value = [cache_dir]
        assert _is_playwright_cli_ready() is True

    @patch("installer.steps.dependencies._get_playwright_cache_dirs")
    @patch("installer.steps.dependencies.command_exists")
    def test_returns_false_when_no_chromium(self, mock_cmd, mock_dirs, tmp_path):
        """Returns False when playwright-cli exists but Chromium is not installed."""
        from installer.steps.dependencies import _is_playwright_cli_ready

        mock_cmd.return_value = True
        cache_dir = tmp_path / "ms-playwright"
        cache_dir.mkdir(parents=True)
        mock_dirs.return_value = [cache_dir]
        assert _is_playwright_cli_ready() is False


class TestInstallPlaywrightCli:
    """Test install_playwright_cli function."""

    @patch("installer.steps.dependencies._is_playwright_cli_ready", return_value=True)
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    def test_skips_browser_install_when_chromium_present(self, _mock_run, _mock_npm, _mock_ready):
        """Skips install-browser when Chromium is already in cache after npm update."""
        from installer.steps.dependencies import install_playwright_cli

        assert install_playwright_cli() is True

    @patch("installer.steps.dependencies.subprocess")
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._is_playwright_cli_ready", return_value=False)
    def test_installs_npm_and_browser(self, _mock_ready, _mock_run, _mock_npm, mock_subprocess):
        """Installs via npm then runs install-browser when Chromium missing."""
        from installer.steps.dependencies import install_playwright_cli

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.run.return_value = mock_result
        assert install_playwright_cli() is True

    @patch("installer.steps.dependencies._is_playwright_cli_ready", return_value=False)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=False)
    def test_returns_false_when_npm_fails(self, _mock_run, _mock_ready):
        """Returns False when npm install fails."""
        from installer.steps.dependencies import install_playwright_cli

        assert install_playwright_cli() is False
