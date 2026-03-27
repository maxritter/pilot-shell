"""Tests for agent-browser installation functions in dependencies step."""

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

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_upgrades_when_already_ready(self, mock_ready, mock_run):
        """Upgrades existing installation when agent-browser is already ready."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = True
        mock_run.return_value = True
        assert install_agent_browser() is True
        mock_run.assert_called_once_with("agent-browser upgrade", timeout=120)

    @patch("platform.system", return_value="Darwin")
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_installs_npm_package_and_chrome_macos(self, mock_ready, mock_run, _mock_npm, _mock_system):
        """Installs agent-browser via npm then runs install on macOS."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.return_value = True
        assert install_agent_browser() is True
        assert mock_run.call_count == 2
        mock_run.assert_any_call("npm install -g agent-browser")
        mock_run.assert_any_call("agent-browser install", timeout=300)

    @patch("platform.system", return_value="Linux")
    @patch("installer.steps.dependencies.npm_global_cmd", side_effect=lambda x: x)
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_agent_browser_ready")
    def test_installs_with_deps_on_linux(self, mock_ready, mock_run, _mock_npm, _mock_system):
        """Installs with --with-deps on Linux for system dependencies."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.return_value = True
        assert install_agent_browser() is True
        mock_run.assert_any_call("agent-browser install --with-deps", timeout=300)

    @patch("installer.steps.dependencies._is_agent_browser_ready")
    @patch("installer.steps.dependencies._run_bash_with_retry")
    def test_returns_false_when_npm_fails(self, mock_run, mock_ready):
        """Returns False when npm install fails."""
        from installer.steps.dependencies import install_agent_browser

        mock_ready.return_value = False
        mock_run.return_value = False
        assert install_agent_browser() is False
