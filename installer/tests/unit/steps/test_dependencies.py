"""Tests for dependencies step."""

from __future__ import annotations

import json
import subprocess
import tempfile
import time

import pytest
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import MagicMock, patch


class TestDependenciesStep:
    """Test DependenciesStep class."""

    def test_dependencies_step_has_correct_name(self):
        """DependenciesStep has name 'dependencies'."""
        from installer.steps.dependencies import DependenciesStep

        step = DependenciesStep()
        assert step.name == "dependencies"

    def test_dependencies_check_returns_false(self):
        """DependenciesStep.check returns False (always runs)."""
        from installer.context import InstallContext
        from installer.steps.dependencies import DependenciesStep
        from installer.ui import Console

        step = DependenciesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = InstallContext(
                project_dir=Path(tmpdir),
                ui=Console(non_interactive=True),
            )
            assert step.check(ctx) is False

    @patch("installer.steps.dependencies.install_rtk", return_value=True)
    @patch("installer.steps.dependencies.install_probe", return_value=True)
    @patch("installer.steps.dependencies.install_agent_browser", return_value=True)
    @patch("installer.steps.dependencies.install_ccusage", return_value=True)
    @patch("installer.steps.dependencies.install_pbt_tools", return_value=True)
    @patch("installer.steps.dependencies.install_golangci_lint", return_value=True)
    @patch("installer.steps.dependencies.install_prettier", return_value=True)
    @patch("installer.steps.dependencies.install_typescript_lsp", return_value=True)
    @patch("installer.steps.dependencies._precache_npx_mcp_servers", return_value=True)
    @patch("installer.steps.dependencies.install_context_mode_plugin", return_value=True)
    @patch("installer.steps.dependencies._install_plugin_dependencies")
    @patch("installer.steps.dependencies._setup_pilot_memory")
    @patch("installer.steps.dependencies.install_python_tools")
    @patch("installer.steps.dependencies.install_uv")
    @patch("installer.steps.dependencies.install_nodejs")
    @patch("installer.steps.dependencies.install_claude_code", return_value=True)
    def test_dependencies_run_installs_core(
        self,
        mock_claude_code,
        mock_nodejs,
        mock_uv,
        mock_python_tools,
        mock_setup_pilot_memory,
        mock_plugin_deps,
        _mock_ctx_mode_plugin,
        _mock_precache,
        _mock_ts_lsp,
        _mock_prettier,
        _mock_golangci_lint,
        _mock_pbt_tools,
        _mock_ccusage,
        _mock_playwright,
        _mock_probe,
        _mock_rtk,
    ):
        """DependenciesStep installs all dependencies including Python tools."""
        from installer.context import InstallContext
        from installer.steps.dependencies import DependenciesStep
        from installer.ui import Console

        mock_claude_code.return_value = True
        mock_nodejs.return_value = True
        mock_uv.return_value = True
        mock_python_tools.return_value = True
        mock_setup_pilot_memory.return_value = True
        mock_plugin_deps.return_value = True

        step = DependenciesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = InstallContext(
                project_dir=Path(tmpdir),
                ui=Console(non_interactive=True),
            )

            step.run(ctx)

            mock_claude_code.assert_called_once()
            mock_nodejs.assert_called_once()
            mock_uv.assert_called_once()
            mock_python_tools.assert_called_once()
            mock_plugin_deps.assert_called_once()


class TestInstallClaudeCode:
    """Test Claude Code installation."""

    def test_install_claude_code_exists(self):
        """install_claude_code function exists."""
        from installer.steps.dependencies import install_claude_code

        assert callable(install_claude_code)

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_install_claude_code_skips_if_already_installed(self, _mock_cmd):
        """install_claude_code returns True without installing when claude is in PATH."""
        from installer.steps.dependencies import install_claude_code

        with patch("installer.steps.dependencies._run_bash_with_retry") as mock_run:
            result = install_claude_code()

        assert result is True
        mock_run.assert_not_called()

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_claude_code_runs_native_installer(self, _mock_cmd, mock_run):
        """install_claude_code runs the native installer when claude is not in PATH."""
        from installer.steps.dependencies import install_claude_code

        result = install_claude_code()

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "claude.ai/install.sh" in call_args
        assert mock_run.call_args[1].get("timeout") == 300 or (
            len(mock_run.call_args[0]) > 1 or "timeout" in str(mock_run.call_args)
        )

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=False)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_claude_code_returns_false_on_failure(self, _mock_cmd, mock_run):
        """install_claude_code returns False when native installer fails."""
        from installer.steps.dependencies import install_claude_code

        result = install_claude_code()

        assert result is False


class TestDependencyInstallFunctions:
    """Test individual dependency install functions."""

    def test_install_nodejs_exists(self):
        """install_nodejs function exists."""
        from installer.steps.dependencies import install_nodejs

        assert callable(install_nodejs)

    def test_install_uv_exists(self):
        """install_uv function exists."""
        from installer.steps.dependencies import install_uv

        assert callable(install_uv)

    def test_install_python_tools_exists(self):
        """install_python_tools function exists."""
        from installer.steps.dependencies import install_python_tools

        assert callable(install_python_tools)


class TestSetupPilotMemory:
    """Test pilot-memory setup."""

    def test_setup_pilot_memory_exists(self):
        """_setup_pilot_memory function exists."""
        from installer.steps.dependencies import _setup_pilot_memory

        assert callable(_setup_pilot_memory)

    def test_setup_pilot_memory_returns_true(self):
        """_setup_pilot_memory returns True."""
        from installer.steps.dependencies import _setup_pilot_memory

        result = _setup_pilot_memory(ui=None)

        assert result is True


class TestProbeInstall:
    """Test Probe code search installation."""

    def test_install_probe_exists(self):
        """install_probe function exists."""
        from installer.steps.dependencies import install_probe

        assert callable(install_probe)

    @patch("installer.steps.dependencies._run_bash_with_retry")
    def test_install_probe_always_runs_npm_install(self, mock_bash):
        """install_probe always runs npm install to update to latest."""
        from installer.steps.dependencies import install_probe

        mock_bash.return_value = True

        result = install_probe()

        assert result is True
        mock_bash.assert_called_once()
        call_args = mock_bash.call_args[0][0]
        assert "@probelabs/probe" in call_args

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    def test_install_probe_uses_longer_timeout(self, mock_bash):
        """Probe install gets a longer timeout because npm downloads can be slow."""
        from installer.steps.dependencies import GLOBAL_NPM_INSTALL_TIMEOUT, install_probe

        result = install_probe()

        assert result is True
        assert mock_bash.call_args.kwargs["timeout"] == GLOBAL_NPM_INSTALL_TIMEOUT

    @patch("installer.steps.dependencies._run_bash_with_retry")
    def test_install_probe_returns_false_on_failure(self, mock_bash):
        """install_probe returns False when npm install fails."""
        from installer.steps.dependencies import install_probe

        mock_bash.return_value = False

        result = install_probe()

        assert result is False


class TestInstallRtk:
    """Tests for install_rtk() — RTK CLI installation (brew primary, curl fallback)."""

    def test_install_rtk_exists(self):
        """install_rtk function exists and is callable."""
        from installer.steps.dependencies import install_rtk

        assert callable(install_rtk)

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_install_rtk_skips_when_already_installed(self, _mock_cmd):
        """install_rtk returns True without curl when rtk already exists (e.g., via brew)."""
        from installer.steps.dependencies import install_rtk

        result = install_rtk()
        assert result is True

    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_rtk_runs_curl_fallback(self, _mock_cmd):
        """install_rtk runs curl installer when rtk not found."""
        from installer.steps.dependencies import install_rtk

        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=True) as mock_bash:
            result = install_rtk()

        assert result is True
        mock_bash.assert_called_once()
        call_args = str(mock_bash.call_args)
        assert "rtk-ai/rtk" in call_args
        assert "install.sh" in call_args

    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_rtk_returns_false_when_curl_fails(self, _mock_cmd):
        """install_rtk returns False when curl installer fails."""
        from installer.steps.dependencies import install_rtk

        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=False):
            result = install_rtk()

        assert result is False


class TestInstallCodegraph:
    """Tests for install_codegraph() — CodeGraph code knowledge graph."""

    def test_install_codegraph_exists(self):
        """install_codegraph function exists and is callable."""
        from installer.steps.dependencies import install_codegraph

        assert callable(install_codegraph)

    @patch("installer.steps.dependencies._symlink_to_pilot_bin")
    def test_install_codegraph_always_runs_npm_install(self, mock_symlink):
        """install_codegraph always runs npm install to update to latest."""
        from installer.steps.dependencies import install_codegraph

        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=True) as mock_bash:
            result = install_codegraph()

        assert result is True
        mock_bash.assert_called_once()
        call_args = str(mock_bash.call_args)
        assert "@colbymchenry/codegraph" in call_args
        assert "--force" in call_args
        mock_symlink.assert_called_once_with("codegraph")

    @patch("installer.steps.dependencies._symlink_to_pilot_bin")
    def test_install_codegraph_uses_longer_timeout(self, mock_symlink):
        """CodeGraph install gets a longer timeout because it can build native modules."""
        from installer.steps.dependencies import GLOBAL_NPM_INSTALL_TIMEOUT, install_codegraph

        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=True) as mock_bash:
            result = install_codegraph()

        assert result is True
        assert mock_bash.call_args.kwargs["timeout"] == GLOBAL_NPM_INSTALL_TIMEOUT
        mock_symlink.assert_called_once_with("codegraph")

    @patch("installer.steps.dependencies._symlink_to_pilot_bin")
    def test_install_codegraph_returns_false_when_npm_fails(self, _mock_symlink):
        """install_codegraph returns False when npm install fails."""
        from installer.steps.dependencies import install_codegraph

        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=False):
            result = install_codegraph()

        assert result is False


class TestInitializeCodegraph:
    """Tests for initialize_codegraph() — init, enable embeddings, index, sync."""

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies._is_codegraph_indexed", return_value=True)
    def test_skips_index_when_already_indexed(self, _mock_indexed, _mock_cmd, tmp_path: Path):
        """Skips index and just syncs when already indexed."""
        from installer.steps.dependencies import initialize_codegraph

        (tmp_path / ".git").mkdir()
        codegraph_dir = tmp_path / ".codegraph"
        codegraph_dir.mkdir()
        (codegraph_dir / "config.json").write_text(json.dumps({"enableEmbeddings": True}))

        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=True) as mock_bash:
            result = initialize_codegraph(tmp_path)

        assert result is True
        calls = [str(c) for c in mock_bash.call_args_list]
        assert not any("codegraph init" in c for c in calls)
        assert not any("codegraph index" in c for c in calls)
        assert any("codegraph sync" in c for c in calls)

    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_returns_false_when_codegraph_not_installed(self, _mock_cmd, tmp_path: Path):
        """Returns False when codegraph binary is not available."""
        from installer.steps.dependencies import initialize_codegraph

        result = initialize_codegraph(tmp_path)

        assert result is False

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies._is_codegraph_indexed", return_value=False)
    def test_full_init_sequence(self, _mock_indexed, _mock_cmd, tmp_path: Path):
        """Runs init, enables embeddings, index, sync in sequence."""
        from installer.steps.dependencies import initialize_codegraph

        (tmp_path / ".git").mkdir()
        codegraph_dir = tmp_path / ".codegraph"

        def fake_bash(command: str, cwd: Path | None = None, timeout: int = 120, stream: bool = False) -> bool:
            if "codegraph init" in command:
                codegraph_dir.mkdir(parents=True, exist_ok=True)
                config = {"version": 1, "enableEmbeddings": False}
                (codegraph_dir / "config.json").write_text(json.dumps(config))
            return True

        with patch("installer.steps.dependencies._run_bash_with_retry", side_effect=fake_bash) as mock_bash:
            result = initialize_codegraph(tmp_path)

        assert result is True
        calls = [str(c) for c in mock_bash.call_args_list]
        assert any("codegraph init" in c for c in calls)
        assert any("codegraph index" in c for c in calls)
        assert any("codegraph sync" in c for c in calls)

        # Verify embeddings were enabled in config
        config = json.loads((codegraph_dir / "config.json").read_text())
        assert config["enableEmbeddings"] is True

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies._is_codegraph_indexed", return_value=False)
    def test_index_streams_output(self, _mock_indexed, _mock_cmd, tmp_path: Path):
        """Index is called with stream=True for visible progress."""
        from installer.steps.dependencies import initialize_codegraph

        (tmp_path / ".git").mkdir()
        codegraph_dir = tmp_path / ".codegraph"
        codegraph_dir.mkdir()
        (codegraph_dir / "config.json").write_text(json.dumps({"enableEmbeddings": True}))

        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=True) as mock_bash:
            initialize_codegraph(tmp_path)

        index_calls = [c for c in mock_bash.call_args_list if "codegraph index" in str(c)]
        assert len(index_calls) == 1
        assert index_calls[0].kwargs.get("stream") is True or (
            len(index_calls[0].args) > 3 and index_calls[0].args[3] is True
        )

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_returns_false_when_not_git_repo(self, _mock_cmd, tmp_path: Path):
        """Returns False when directory is not a git repository."""
        from installer.steps.dependencies import initialize_codegraph

        result = initialize_codegraph(tmp_path)

        assert result is False

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies._is_codegraph_indexed", return_value=True)
    def test_works_in_git_subdirectory(self, _mock_indexed, _mock_cmd, tmp_path: Path):
        """Works when .git is in a parent directory (monorepo subdirectory)."""
        from installer.steps.dependencies import initialize_codegraph

        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "packages" / "my-app"
        subdir.mkdir(parents=True)
        (subdir / ".codegraph").mkdir()
        (subdir / ".codegraph" / "config.json").write_text(json.dumps({"enableEmbeddings": True}))

        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=True):
            result = initialize_codegraph(subdir)

        assert result is True

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies._is_codegraph_indexed", return_value=False)
    def test_returns_false_when_init_fails(self, _mock_indexed, _mock_cmd, tmp_path: Path):
        """Returns False when codegraph init fails."""
        from installer.steps.dependencies import initialize_codegraph

        (tmp_path / ".git").mkdir()
        with patch("installer.steps.dependencies._run_bash_with_retry", return_value=False):
            result = initialize_codegraph(tmp_path)

        assert result is False

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies._is_codegraph_indexed", return_value=False)
    def test_returns_false_when_index_fails(self, _mock_indexed, _mock_cmd, tmp_path: Path):
        """Returns False when codegraph index fails."""
        from installer.steps.dependencies import initialize_codegraph

        (tmp_path / ".git").mkdir()
        codegraph_dir = tmp_path / ".codegraph"

        def fake_bash(command: str, cwd: Path | None = None, timeout: int = 120, stream: bool = False) -> bool:
            if "codegraph init" in command:
                codegraph_dir.mkdir(parents=True, exist_ok=True)
                # Create config so _enable_codegraph_embeddings doesn't sleep
                (codegraph_dir / "config.json").write_text(json.dumps({"enableEmbeddings": False}))
                return True
            if "codegraph index" in command:
                return False
            return True

        with patch("installer.steps.dependencies._run_bash_with_retry", side_effect=fake_bash):
            result = initialize_codegraph(tmp_path)

        assert result is False

    def test_enable_embeddings_writes_config(self, tmp_path: Path):
        """_enable_codegraph_embeddings sets enableEmbeddings to true."""
        from installer.steps.dependencies import _enable_codegraph_embeddings

        codegraph_dir = tmp_path / ".codegraph"
        codegraph_dir.mkdir()
        config_path = codegraph_dir / "config.json"
        config_path.write_text(json.dumps({"version": 1, "enableEmbeddings": False}))

        _enable_codegraph_embeddings(tmp_path)

        config = json.loads(config_path.read_text())
        assert config["enableEmbeddings"] is True

    def test_enable_embeddings_idempotent(self, tmp_path: Path):
        """_enable_codegraph_embeddings is a no-op when already enabled."""
        from installer.steps.dependencies import _enable_codegraph_embeddings

        codegraph_dir = tmp_path / ".codegraph"
        codegraph_dir.mkdir()
        config_path = codegraph_dir / "config.json"
        original = json.dumps({"version": 1, "enableEmbeddings": True}, indent=2) + "\n"
        config_path.write_text(original)

        _enable_codegraph_embeddings(tmp_path)

        assert config_path.read_text() == original


class TestSymlinkToPilotBin:
    """Tests for _symlink_to_pilot_bin() — creates symlinks in ~/.pilot/bin/."""

    def test_creates_symlink_when_binary_exists(self, tmp_path: Path):
        """Creates a symlink in pilot bin dir pointing to the real binary."""
        from installer.steps.dependencies import _symlink_to_pilot_bin

        fake_bin = tmp_path / "src" / "codegraph"
        fake_bin.parent.mkdir(parents=True)
        fake_bin.write_text("#!/bin/sh\n")
        fake_bin.chmod(0o755)

        pilot_bin = tmp_path / "pilot_bin"

        with (
            patch("installer.steps.dependencies.shutil.which", return_value=str(fake_bin)),
            patch("installer.steps.dependencies.Path.home", return_value=tmp_path),
        ):
            pilot_bin_dir = tmp_path / ".pilot" / "bin"
            pilot_bin_dir.mkdir(parents=True, exist_ok=True)
            _symlink_to_pilot_bin("codegraph")

        link = tmp_path / ".pilot" / "bin" / "codegraph"
        assert link.is_symlink()
        assert link.resolve() == fake_bin.resolve()

    def test_skips_when_binary_not_found(self, tmp_path: Path):
        """Does nothing when the binary is not in PATH."""
        from installer.steps.dependencies import _symlink_to_pilot_bin

        with (
            patch("installer.steps.dependencies.shutil.which", return_value=None),
            patch("installer.steps.dependencies.Path.home", return_value=tmp_path),
        ):
            _symlink_to_pilot_bin("codegraph")

        link = tmp_path / ".pilot" / "bin" / "codegraph"
        assert not link.exists()

    def test_replaces_existing_symlink(self, tmp_path: Path):
        """Replaces an existing symlink with the new target."""
        from installer.steps.dependencies import _symlink_to_pilot_bin

        fake_bin = tmp_path / "new_codegraph"
        fake_bin.write_text("#!/bin/sh\n")
        fake_bin.chmod(0o755)

        pilot_bin_dir = tmp_path / ".pilot" / "bin"
        pilot_bin_dir.mkdir(parents=True)
        old_link = pilot_bin_dir / "codegraph"
        old_link.symlink_to("/nonexistent/old/path")

        with (
            patch("installer.steps.dependencies.shutil.which", return_value=str(fake_bin)),
            patch("installer.steps.dependencies.Path.home", return_value=tmp_path),
        ):
            _symlink_to_pilot_bin("codegraph")

        assert old_link.is_symlink()
        assert old_link.resolve() == fake_bin.resolve()


class TestInstallPluginDependencies:
    """Test plugin dependencies installation via bun/npm install."""

    def test_install_plugin_dependencies_exists(self):
        """_install_plugin_dependencies function exists."""
        from installer.steps.dependencies import _install_plugin_dependencies

        assert callable(_install_plugin_dependencies)

    def test_install_plugin_dependencies_returns_false_if_no_plugin_dir(self):
        """_install_plugin_dependencies returns False if plugin directory doesn't exist."""
        from installer.steps.dependencies import _install_plugin_dependencies

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "claude-config"
            config_dir.mkdir()

            with patch("installer.steps.claude_files.get_claude_config_dir", return_value=config_dir):
                result = _install_plugin_dependencies(Path(tmpdir), ui=None)
            assert result is False

    def test_install_plugin_dependencies_returns_false_if_no_package_json(self):
        """_install_plugin_dependencies returns False if no package.json exists."""
        from installer.steps.dependencies import _install_plugin_dependencies

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "claude-config"
            plugin_dir = config_dir / "pilot"
            plugin_dir.mkdir(parents=True)

            with patch("installer.steps.claude_files.get_claude_config_dir", return_value=config_dir):
                result = _install_plugin_dependencies(Path(tmpdir), ui=None)
            assert result is False

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.command_exists")
    def test_install_plugin_dependencies_runs_bun_install(self, mock_cmd_exists, mock_run):
        """_install_plugin_dependencies runs bun install when bun is available."""
        from installer.steps.dependencies import _install_plugin_dependencies

        mock_cmd_exists.side_effect = lambda cmd: cmd == "bun"
        mock_run.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "claude-config"
            plugin_dir = config_dir / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "package.json").write_text('{"name": "test"}')

            with patch("installer.steps.claude_files.get_claude_config_dir", return_value=config_dir):
                result = _install_plugin_dependencies(Path(tmpdir), ui=None)

            assert result is True
            mock_run.assert_called_with("bun install", cwd=plugin_dir)

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.command_exists")
    def test_install_plugin_dependencies_falls_back_to_npm(self, mock_cmd_exists, mock_run):
        """_install_plugin_dependencies falls back to npm install when bun is unavailable."""
        from installer.steps.dependencies import _install_plugin_dependencies

        mock_cmd_exists.side_effect = lambda cmd: cmd == "npm"
        mock_run.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "claude-config"
            plugin_dir = config_dir / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "package.json").write_text('{"name": "test"}')

            with patch("installer.steps.claude_files.get_claude_config_dir", return_value=config_dir):
                result = _install_plugin_dependencies(Path(tmpdir), ui=None)

        assert result is True
        npm_calls = [c for c in mock_run.call_args_list if "npm" in str(c)]
        assert len(npm_calls) > 0, "npm install should be called when bun is unavailable"

    @patch("installer.steps.dependencies.command_exists")
    def test_install_plugin_dependencies_returns_false_when_no_package_manager(self, mock_cmd_exists):
        """_install_plugin_dependencies returns False when neither bun nor npm is available."""
        from installer.steps.dependencies import _install_plugin_dependencies

        mock_cmd_exists.return_value = False

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "claude-config"
            plugin_dir = config_dir / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "package.json").write_text('{"name": "test"}')

            with patch("installer.steps.claude_files.get_claude_config_dir", return_value=config_dir):
                result = _install_plugin_dependencies(Path(tmpdir), ui=None)

        assert result is False


class TestNvmInstallBugCondition:
    """Bug-condition tests: verify NVM installation uses 300s timeout and explicit NVM_DIR.

    These tests FAIL on current code because timeout is 120s and NVM_DIR is not set.
    They pass after the fix is implemented.
    """

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.command_exists")
    def test_nvm_install_uses_300s_timeout(self, mock_cmd_exists, mock_run):
        """nvm install 22 must use 300s timeout (not the default 120s)."""
        from installer.steps.dependencies import install_nodejs

        mock_cmd_exists.return_value = False
        mock_run.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir)
            nvm_dir = home_dir / ".nvm"
            nvm_dir.mkdir()
            (nvm_dir / "nvm.sh").touch()

            with patch.object(Path, "home", return_value=home_dir):
                install_nodejs()

        nvm_install_calls = [c for c in mock_run.call_args_list if "nvm install" in str(c)]
        assert nvm_install_calls, "nvm install should be called"
        for call in nvm_install_calls:
            timeout = call.kwargs.get("timeout")
            assert timeout == 300, f"Expected timeout=300 for nvm install, got timeout={timeout}"

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.command_exists")
    def test_nvm_install_sets_nvm_dir_in_command(self, mock_cmd_exists, mock_run):
        """nvm install 22 command must explicitly export NVM_DIR before sourcing nvm.sh."""
        from installer.steps.dependencies import install_nodejs

        mock_cmd_exists.return_value = False
        mock_run.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            home_dir = Path(tmpdir)
            nvm_dir = home_dir / ".nvm"
            nvm_dir.mkdir()
            (nvm_dir / "nvm.sh").touch()

            with patch.object(Path, "home", return_value=home_dir):
                install_nodejs()

        nvm_install_calls = [c for c in mock_run.call_args_list if "nvm install" in str(c)]
        assert nvm_install_calls, "nvm install should be called"
        nvm_cmd = nvm_install_calls[0][0][0]
        assert "NVM_DIR" in nvm_cmd, f"NVM_DIR must be explicitly set in nvm install command, got: {nvm_cmd}"


class TestNvmInstallPreservation:
    """Preservation tests: NVM behavior that must NOT change after the timeout/NVM_DIR fix."""

    @patch("installer.steps.dependencies.command_exists")
    def test_preservation_install_nodejs_returns_true_when_node_installed(self, mock_cmd_exists):
        """PRESERVATION: install_nodejs() returns True immediately when node is already in PATH."""
        import os

        from installer.steps.dependencies import install_nodejs

        mock_cmd_exists.return_value = True
        original_path = os.environ.get("PATH", "")
        result = install_nodejs()
        assert result is True
        assert os.environ.get("PATH", "") == original_path

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.command_exists")
    def test_preservation_install_nodejs_returns_false_when_nvm_install_fails(self, mock_cmd_exists, mock_run):
        """PRESERVATION: install_nodejs() returns False when NVM installation itself fails."""
        from installer.steps.dependencies import install_nodejs

        mock_cmd_exists.return_value = False
        mock_run.return_value = False

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                result = install_nodejs()

        assert result is False

class TestInstallNodejsPathUpdate:
    """Test that install_nodejs updates PATH after NVM installation."""

    @patch("installer.steps.dependencies.command_exists")
    def test_install_nodejs_returns_true_when_already_installed(self, mock_cmd_exists):
        """install_nodejs returns True without modifying PATH when node is already installed."""
        import os

        from installer.steps.dependencies import install_nodejs

        mock_cmd_exists.return_value = True
        original_path = os.environ.get("PATH", "")

        result = install_nodejs()

        assert result is True
        assert os.environ.get("PATH", "") == original_path, "PATH should not be modified when node already installed"

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.command_exists")
    def test_install_nodejs_updates_path_after_nvm_install(self, mock_cmd_exists, mock_run):
        """install_nodejs updates os.environ[PATH] after NVM successfully installs Node.js."""
        import os

        from installer.steps.dependencies import install_nodejs

        mock_cmd_exists.return_value = False
        mock_run.return_value = True

        original_path = os.environ.get("PATH", "")
        nvm_node_bin = None
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                home_dir = Path(tmpdir)
                nvm_dir = home_dir / ".nvm"
                nvm_dir.mkdir()
                (nvm_dir / "nvm.sh").touch()
                nvm_node_bin = nvm_dir / "versions" / "node" / "v22.0.0" / "bin"
                nvm_node_bin.mkdir(parents=True)

                with patch.object(Path, "home", return_value=home_dir):
                    result = install_nodejs()

            assert result is True
            assert str(nvm_node_bin) in os.environ.get("PATH", ""), (
                "NVM node bin dir should be added to PATH after successful install"
            )
        finally:
            current_path = os.environ.get("PATH", "")
            if nvm_node_bin and str(nvm_node_bin) in current_path:
                paths = [p for p in current_path.split(":") if p != str(nvm_node_bin)]
                os.environ["PATH"] = ":".join(paths)
            elif current_path != original_path:
                os.environ["PATH"] = original_path


class TestPrecacheNpxMcpServers:
    """Test pre-caching of npx-based MCP server packages."""

    def test_returns_true_when_no_mcp_json(self):
        """Returns True when .mcp.json doesn't exist."""
        from installer.steps.dependencies import _precache_npx_mcp_servers

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                assert _precache_npx_mcp_servers(None) is True

    def test_returns_true_when_all_cached(self):
        """Returns True immediately when all packages are already cached."""
        import json

        from installer.steps.dependencies import _precache_npx_mcp_servers

        mcp_config = {
            "mcpServers": {
                "web-fetch": {"command": "npx", "args": ["-y", "fetcher-mcp"]},
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / ".claude" / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / ".mcp.json").write_text(json.dumps(mcp_config))

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                with patch(
                    "installer.steps.dependencies._is_npx_package_cached",
                    return_value=True,
                ):
                    assert _precache_npx_mcp_servers(None) is True

    def test_extracts_npx_packages_from_mcp_json(self):
        """Extracts only npx -y packages from .mcp.json."""
        import json

        from installer.steps.dependencies import _precache_npx_mcp_servers

        mcp_config = {
            "mcpServers": {
                "web-fetch": {"command": "npx", "args": ["-y", "fetcher-mcp"]},
                "context7": {"command": "npx", "args": ["-y", "@upstash/context7-mcp"]},
                "grep": {"type": "http", "url": "https://mcp.grep.app"},
                "mem": {"command": "sh", "args": ["-c", "bun run server.cjs"]},
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / ".claude" / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / ".mcp.json").write_text(json.dumps(mcp_config))

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                with patch(
                    "installer.steps.dependencies._is_npx_package_cached",
                    return_value=True,
                ):
                    assert _precache_npx_mcp_servers(None) is True

    def test_launches_and_kills_uncached_packages(self):
        """Launches npx for uncached packages and kills after caching."""
        import json

        from installer.steps.dependencies import _precache_npx_mcp_servers

        mcp_config = {
            "mcpServers": {
                "web-fetch": {"command": "npx", "args": ["-y", "fetcher-mcp"]},
            }
        }

        mock_proc = MagicMock()
        mock_proc.wait = MagicMock(return_value=0)

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / ".claude" / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / ".mcp.json").write_text(json.dumps(mcp_config))

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                with patch(
                    "installer.steps.dependencies._is_npx_package_cached",
                    return_value=False,
                ):
                    with patch("installer.steps.dependencies.subprocess.Popen", return_value=mock_proc) as mock_popen:
                        result = _precache_npx_mcp_servers(None)

            assert result is True
            popen_args = mock_popen.call_args[0][0]
            assert popen_args[:2] == ["npx", "-y"]
            assert "--package" in popen_args
            assert "-c" in popen_args
            assert "true" in popen_args
            mock_proc.wait.assert_called_once()

    def test_is_npx_package_cached_finds_cached(self):
        """_is_npx_package_cached returns True when package exists in npx cache."""
        from installer.steps.dependencies import _is_npx_package_cached

        with tempfile.TemporaryDirectory() as tmpdir:
            npx_cache = Path(tmpdir) / ".npm" / "_npx" / "abc123" / "node_modules" / "fetcher-mcp"
            npx_cache.mkdir(parents=True)

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                assert _is_npx_package_cached("fetcher-mcp") is True

    def test_is_npx_package_cached_returns_false_when_missing(self):
        """_is_npx_package_cached returns False when package not in cache."""
        from installer.steps.dependencies import _is_npx_package_cached

        with tempfile.TemporaryDirectory() as tmpdir:
            npx_cache = Path(tmpdir) / ".npm" / "_npx"
            npx_cache.mkdir(parents=True)

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                assert _is_npx_package_cached("fetcher-mcp") is False

    def test_is_npx_package_cached_handles_scoped_packages(self):
        """_is_npx_package_cached handles @scope/package names."""
        from installer.steps.dependencies import _is_npx_package_cached

        with tempfile.TemporaryDirectory() as tmpdir:
            npx_cache = Path(tmpdir) / ".npm" / "_npx" / "abc123" / "node_modules" / "@upstash" / "context7-mcp"
            npx_cache.mkdir(parents=True)

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                assert _is_npx_package_cached("@upstash/context7-mcp") is True

    def test_is_npx_package_cached_strips_version_tag(self):
        """_is_npx_package_cached strips @latest/@version from package names."""
        from installer.steps.dependencies import _is_npx_package_cached

        with tempfile.TemporaryDirectory() as tmpdir:
            npx_cache = Path(tmpdir) / ".npm" / "_npx" / "abc123" / "node_modules" / "open-websearch"
            npx_cache.mkdir(parents=True)

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                assert _is_npx_package_cached("open-websearch@latest") is True

    def test_extract_npx_package_name(self):
        """_extract_npx_package_name strips version/tag suffixes correctly."""
        from installer.steps.dependencies import _extract_npx_package_name

        assert _extract_npx_package_name("fetcher-mcp") == "fetcher-mcp"
        assert _extract_npx_package_name("open-websearch@latest") == "open-websearch"
        assert _extract_npx_package_name("@upstash/context7-mcp") == "@upstash/context7-mcp"
        assert _extract_npx_package_name("@scope/pkg@1.0.0") == "@scope/pkg"

    def test_fix_npx_peer_dependencies_installs_zod(self):
        """_fix_npx_peer_dependencies installs zod when open-websearch is cached but zod is missing."""
        from installer.steps.dependencies import _fix_npx_peer_dependencies

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".npm" / "_npx" / "abc123" / "node_modules" / "open-websearch"
            cache_dir.mkdir(parents=True)

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                with patch("installer.steps.dependencies.subprocess.run") as mock_run:
                    _fix_npx_peer_dependencies()

            mock_run.assert_called_once()
            assert mock_run.call_args[0][0] == ["npm", "install", "zod"]

    def test_fix_npx_peer_dependencies_skips_when_zod_present(self):
        """_fix_npx_peer_dependencies skips when zod is already installed."""
        from installer.steps.dependencies import _fix_npx_peer_dependencies

        with tempfile.TemporaryDirectory() as tmpdir:
            hash_dir = Path(tmpdir) / ".npm" / "_npx" / "abc123" / "node_modules"
            (hash_dir / "open-websearch").mkdir(parents=True)
            (hash_dir / "zod").mkdir(parents=True)

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                with patch("installer.steps.dependencies.subprocess.run") as mock_run:
                    _fix_npx_peer_dependencies()

            mock_run.assert_not_called()

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_install_ccusage_skips_when_already_installed(self, _mock_cmd):
        """install_ccusage returns True without npm when already exists (e.g., via brew)."""
        from installer.steps.dependencies import install_ccusage

        result = install_ccusage()
        assert result is True

    @patch("installer.steps.dependencies.command_exists", return_value=False)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    def test_install_ccusage_runs_npm_fallback(self, _mock_run, _mock_cmd):
        """install_ccusage runs npm install when not found."""
        from installer.steps.dependencies import install_ccusage

        result = install_ccusage()
        assert result is True

    @patch("installer.steps.dependencies.command_exists", return_value=False)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=False)
    def test_install_ccusage_returns_false_on_failure(self, _mock_run, _mock_cmd):
        """install_ccusage returns False when npm install fails."""
        from installer.steps.dependencies import install_ccusage

        result = install_ccusage()
        assert result is False


class TestMacosArm64Detection:
    """Test macOS Apple Silicon detection."""

    @patch("platform.machine", return_value="arm64")
    @patch("platform.system", return_value="Darwin")
    def test_is_macos_arm64_true(self, _mock_system, _mock_machine):
        """Returns True on macOS arm64 (Apple Silicon)."""
        from installer.platform_utils import is_macos_arm64

        assert is_macos_arm64() is True

    @patch("platform.machine", return_value="x86_64")
    @patch("platform.system", return_value="Darwin")
    def test_is_macos_arm64_false_intel(self, _mock_system, _mock_machine):
        """Returns False on macOS Intel."""
        from installer.platform_utils import is_macos_arm64

        assert is_macos_arm64() is False

    @patch("platform.machine", return_value="arm64")
    @patch("platform.system", return_value="Linux")
    def test_is_macos_arm64_false_linux(self, _mock_system, _mock_machine):
        """Returns False on Linux arm64."""
        from installer.platform_utils import is_macos_arm64

        assert is_macos_arm64() is False




class TestInstallPrettier:
    """Test prettier global installation."""

    def test_install_prettier_exists(self):
        """install_prettier function exists."""
        from installer.steps.dependencies import install_prettier

        assert callable(install_prettier)

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_install_prettier_skips_if_already_installed(self, _mock_cmd):
        """install_prettier returns True without installing when prettier is in PATH."""
        from installer.steps.dependencies import install_prettier

        with patch("installer.steps.dependencies._run_bash_with_retry") as mock_run:
            result = install_prettier()

        assert result is True
        mock_run.assert_not_called()

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_prettier_installs_via_npm(self, _mock_cmd, mock_run):
        """install_prettier uses npm install -g prettier when not in PATH."""
        from installer.steps.dependencies import install_prettier

        result = install_prettier()

        assert result is True
        mock_run.assert_called_once()
        assert "prettier" in mock_run.call_args[0][0]
        assert "npm install -g" in mock_run.call_args[0][0]

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=False)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_prettier_returns_false_on_failure(self, _mock_cmd, mock_run):
        """install_prettier returns False when npm install fails."""
        from installer.steps.dependencies import install_prettier

        result = install_prettier()

        assert result is False


class TestInstallGolangciLint:
    """Test golangci-lint installation."""

    def test_install_golangci_lint_exists(self):
        """install_golangci_lint function exists."""
        from installer.steps.dependencies import install_golangci_lint

        assert callable(install_golangci_lint)

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_install_golangci_lint_skips_if_already_installed(self, mock_cmd):
        """install_golangci_lint returns True without installing when already in PATH."""
        from installer.steps.dependencies import install_golangci_lint

        with patch("installer.steps.dependencies._run_bash_with_retry") as mock_run:
            result = install_golangci_lint()

        assert result is True
        mock_run.assert_not_called()

    @patch("installer.steps.dependencies._install_go_via_apt", return_value=False)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_golangci_lint_fails_without_go_and_no_apt(self, mock_cmd, mock_apt):
        """install_golangci_lint returns False when go missing and apt install fails."""
        from installer.steps.dependencies import install_golangci_lint

        result = install_golangci_lint()

        assert result is False
        mock_apt.assert_called_once()

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._install_go_via_apt", return_value=True)
    @patch("installer.steps.dependencies.command_exists")
    def test_install_golangci_lint_installs_go_via_apt_then_lint(self, mock_cmd, mock_apt, mock_run):
        """install_golangci_lint installs Go via apt when missing, then installs lint."""
        from installer.steps.dependencies import install_golangci_lint

        mock_cmd.side_effect = lambda cmd: False

        result = install_golangci_lint()

        assert result is True
        mock_apt.assert_called_once()
        assert "golangci-lint" in mock_run.call_args[0][0]

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.command_exists", side_effect=lambda cmd: cmd == "go")
    @patch("installer.steps.dependencies._is_golangci_lint_installed", return_value=False)
    def test_install_golangci_lint_uses_official_script(self, mock_check, mock_cmd, mock_run):
        """install_golangci_lint uses the official install.sh script."""
        from installer.steps.dependencies import install_golangci_lint

        result = install_golangci_lint()

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "golangci-lint" in call_args
        assert "install.sh" in call_args
        assert "go env GOPATH" in call_args

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=False)
    @patch("installer.steps.dependencies.command_exists", side_effect=lambda cmd: cmd == "go")
    @patch("installer.steps.dependencies._is_golangci_lint_installed", return_value=False)
    def test_install_golangci_lint_returns_false_on_failure(self, mock_check, mock_cmd, mock_run):
        """install_golangci_lint returns False when install script fails."""
        from installer.steps.dependencies import install_golangci_lint

        result = install_golangci_lint()

        assert result is False


class TestInstallPbtTools:
    """Tests for install_pbt_tools() — property-based testing packages."""

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_pbt_tools_installs_both_when_missing(self, _mock_cmd, mock_run, mock_sub):
        """install_pbt_tools installs hypothesis and fast-check when not found."""
        from installer.steps.dependencies import install_pbt_tools

        mock_sub.return_value = MagicMock(returncode=1, stdout="")
        install_pbt_tools()

        calls = [str(c) for c in mock_run.call_args_list]
        assert any("hypothesis" in c for c in calls)
        assert any("fast-check" in c for c in calls)

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_pbt_tools_uses_longer_timeouts(self, _mock_cmd, mock_run, mock_sub):
        """Hypothesis and fast-check installs use timeouts sized for package downloads."""
        from installer.steps.dependencies import (
            GLOBAL_NPM_INSTALL_TIMEOUT,
            UV_TOOL_INSTALL_TIMEOUT,
            install_pbt_tools,
        )

        mock_sub.return_value = MagicMock(returncode=1, stdout="")

        result = install_pbt_tools()

        assert result is True
        timeout_by_command = {call.args[0]: call.kwargs["timeout"] for call in mock_run.call_args_list}
        assert timeout_by_command["uv tool install hypothesis"] == UV_TOOL_INSTALL_TIMEOUT
        assert timeout_by_command["npm install -g fast-check"] == GLOBAL_NPM_INSTALL_TIMEOUT

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_install_pbt_tools_returns_true_when_all_present(self, _mock_cmd):
        """install_pbt_tools returns True when all binaries already exist."""
        from installer.steps.dependencies import install_pbt_tools

        result = install_pbt_tools()

        assert result is True

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=False)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_install_pbt_tools_returns_false_on_install_failure(self, _mock_cmd, _mock_run, mock_sub):
        """install_pbt_tools returns False when installations fail."""
        from installer.steps.dependencies import install_pbt_tools

        mock_sub.return_value = MagicMock(returncode=1, stdout="")
        result = install_pbt_tools()

        assert result is False


class TestInstallContextModePlugin:
    """Tests for install_context_mode_plugin() — Claude CLI plugin system."""

    def test_install_context_mode_plugin_exists(self):
        """install_context_mode_plugin function exists and is callable."""
        from installer.steps.dependencies import install_context_mode_plugin

        assert callable(install_context_mode_plugin)

    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_returns_false_when_claude_not_installed(self, _mock_cmd):
        """Returns False immediately when claude CLI is not available."""
        from installer.steps.dependencies import install_context_mode_plugin

        result = install_context_mode_plugin()
        assert result is False

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_updates_when_already_installed(self, _mock_cmd, mock_sub, mock_bash):
        """Runs 'claude plugins update' when plugin is already installed."""
        from installer.steps.dependencies import install_context_mode_plugin

        mock_sub.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([{"id": "context-mode@context-mode", "version": "1.0.75"}]),
        )

        result = install_context_mode_plugin()

        assert result is True
        # marketplace refresh + plugin update = 2 calls
        assert mock_bash.call_count == 2
        calls = [c[0][0] for c in mock_bash.call_args_list]
        assert any("marketplace update context-mode" in c for c in calls)
        assert any("plugins update context-mode@context-mode" in c for c in calls)

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_fresh_install_adds_marketplace_then_installs(self, _mock_cmd, mock_sub, mock_bash):
        """Adds marketplace and installs plugin when not already installed."""
        from installer.steps.dependencies import install_context_mode_plugin

        mock_sub.return_value = MagicMock(returncode=0, stdout="[]")

        result = install_context_mode_plugin()

        assert result is True
        assert mock_bash.call_count == 2
        assert "marketplace add" in mock_bash.call_args_list[0][0][0]
        assert "plugins install" in mock_bash.call_args_list[1][0][0]

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_fresh_install_fails_if_marketplace_add_fails(self, _mock_cmd, mock_sub, mock_bash):
        """Returns False when marketplace add fails."""
        from installer.steps.dependencies import install_context_mode_plugin

        mock_sub.return_value = MagicMock(returncode=0, stdout="[]")
        mock_bash.return_value = False

        result = install_context_mode_plugin()

        assert result is False
        mock_bash.assert_called_once()
        assert "marketplace add" in mock_bash.call_args[0][0]

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_handles_plugins_list_failure_gracefully(self, _mock_cmd, mock_sub, mock_bash):
        """Falls through to fresh install when 'plugins list' fails."""
        from installer.steps.dependencies import install_context_mode_plugin

        mock_sub.return_value = MagicMock(returncode=1, stdout="")

        result = install_context_mode_plugin()

        assert result is True
        assert mock_bash.call_count == 2
        assert "marketplace add" in mock_bash.call_args_list[0][0][0]

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 30))
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_handles_plugins_list_timeout(self, _mock_cmd, _mock_sub, mock_bash):
        """Falls through to fresh install when 'plugins list' times out."""
        from installer.steps.dependencies import install_context_mode_plugin

        result = install_context_mode_plugin()

        assert result is True
        assert "marketplace add" in mock_bash.call_args_list[0][0][0]


class TestRunBashWithRetrySudoFallback:
    """Test sudo -n to sudo fallback in _run_bash_with_retry."""

    @patch("installer.steps.dependencies.subprocess.run")
    def test_sudo_fallback_raises_reauth_exception(self, mock_run):
        """When sudo -n fails with permission error, raises _SudoReauthNeeded."""
        import installer.steps.dependencies as deps
        from installer.steps.dependencies import _SudoReauthNeeded, _run_bash_with_retry

        deps._allow_sudo_fallback = True
        try:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "cmd", stderr=b"sudo: a password is required"
            )
            with pytest.raises(_SudoReauthNeeded):
                _run_bash_with_retry("sudo -n npm install -g probe")
        finally:
            deps._allow_sudo_fallback = False

    @patch("installer.steps.dependencies.subprocess.run")
    def test_no_sudo_fallback_when_disabled(self, mock_run):
        """When sudo fallback is disabled, sudo -n failure does not retry with sudo."""
        import installer.steps.dependencies as deps
        from installer.steps.dependencies import _run_bash_with_retry

        deps._allow_sudo_fallback = False
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr=b"sudo: a password is required"
        )
        result = _run_bash_with_retry("sudo -n npm install -g probe")
        assert result is False
        # All 3 retries should keep sudo -n
        for call in mock_run.call_args_list:
            assert "sudo -n" in " ".join(call[0][0])

    @patch("installer.steps.dependencies.subprocess.run")
    def test_no_sudo_fallback_for_non_sudo_errors(self, mock_run):
        """Regular errors (not sudo-related) don't trigger sudo fallback."""
        import installer.steps.dependencies as deps
        from installer.steps.dependencies import _run_bash_with_retry

        deps._allow_sudo_fallback = True
        try:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "cmd", stderr=b"npm ERR! code ENOENT"
            )
            result = _run_bash_with_retry("sudo -n npm install -g probe")
            assert result is False
            # All retries should keep sudo -n (no fallback for non-sudo errors)
            for call in mock_run.call_args_list:
                assert "sudo -n" in " ".join(call[0][0])
        finally:
            deps._allow_sudo_fallback = False


class TestErrorCapture:
    """Test error detail capture and display in _install_with_spinner."""

    @patch("installer.steps.dependencies.subprocess.run")
    def test_last_error_captured_on_failure(self, mock_run):
        """_run_bash_with_retry captures stderr from failed commands."""
        import installer.steps.dependencies as deps
        from installer.steps.dependencies import _run_bash_with_retry

        deps._thread_local.last_retry_stderr = ""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr=b"npm ERR! code EACCES\nnpm ERR! permission denied"
        )
        _run_bash_with_retry("npm install -g foo")
        assert "permission denied" in deps._get_last_error()

    def test_install_with_spinner_shows_error_detail(self):
        """_install_with_spinner shows last error line when install fails."""
        import installer.steps.dependencies as deps
        from installer.steps.dependencies import _install_with_spinner

        ui = MagicMock()
        deps._thread_local.last_retry_stderr = ""

        def failing_install():
            deps._thread_local.last_retry_stderr = "npm ERR! code EACCES\nnpm ERR! permission denied /usr/lib"
            return False

        _install_with_spinner(ui, "TestPkg", failing_install)
        ui.warning.assert_called_once()
        assert "TestPkg" in ui.warning.call_args[0][0]
        ui.info.assert_called_once()
        assert "permission denied" in ui.info.call_args[0][0]

    def test_install_with_spinner_no_error_detail_when_stderr_empty(self):
        """_install_with_spinner shows generic message when no stderr captured."""
        import installer.steps.dependencies as deps
        from installer.steps.dependencies import _install_with_spinner

        ui = MagicMock()
        deps._thread_local.last_retry_stderr = ""

        _install_with_spinner(ui, "TestPkg", lambda: False)
        ui.warning.assert_called_once()
        assert "TestPkg" in ui.warning.call_args[0][0]
        ui.info.assert_not_called()


class TestInstallWithSpinnerSudoReauth:
    """Test _install_with_spinner handling of sudo re-authentication."""

    @patch("installer.steps.dependencies.start_sudo_keepalive")
    @patch("installer.steps.dependencies.ensure_sudo_credentials", return_value=True)
    def test_reauth_succeeds_retries_install(self, mock_ensure, mock_keepalive):
        """When sudo reauth succeeds, retries install outside spinner and succeeds."""
        from installer.steps.dependencies import _SudoReauthNeeded, _install_with_spinner

        ui = MagicMock()
        call_count = 0

        def install_fn():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise _SudoReauthNeeded()
            return True

        result = _install_with_spinner(ui, "TestPkg", install_fn)
        assert result is True
        assert call_count == 2
        mock_ensure.assert_called_once()
        mock_keepalive.assert_called_once()
        ui.status.assert_called_once()
        assert "re-authenticating" in ui.status.call_args[0][0]
        ui.success.assert_called_once()

    @patch("installer.steps.dependencies.ensure_sudo_credentials", return_value=False)
    def test_reauth_fails_reports_error(self, mock_ensure):
        """When sudo reauth fails, reports clear error without hanging."""
        import installer.steps.dependencies as deps
        from installer.steps.dependencies import _SudoReauthNeeded, _install_with_spinner

        ui = MagicMock()

        def install_fn():
            raise _SudoReauthNeeded()

        result = _install_with_spinner(ui, "TestPkg", install_fn)
        assert result is False
        mock_ensure.assert_called_once()
        assert "sudo credentials expired" in deps._get_last_error()
        ui.warning.assert_called_once()

    @patch("installer.steps.dependencies.start_sudo_keepalive")
    @patch("installer.steps.dependencies.ensure_sudo_credentials", return_value=True)
    def test_reauth_succeeds_but_retry_also_fails_does_not_crash(self, mock_ensure, mock_keepalive):
        """When reauth succeeds but retry also raises _SudoReauthNeeded, fails cleanly."""
        import installer.steps.dependencies as deps
        from installer.steps.dependencies import _SudoReauthNeeded, _install_with_spinner

        ui = MagicMock()

        def install_fn():
            raise _SudoReauthNeeded()

        result = _install_with_spinner(ui, "TestPkg", install_fn)
        assert result is False
        assert "sudo credentials expired" in deps._get_last_error()


class TestDependenciesCleanup:
    """Lifecycle cleanup around sudo state."""

    @patch("installer.steps.dependencies.stop_sudo_keepalive")
    @patch("installer.steps.dependencies.start_sudo_keepalive")
    @patch("installer.steps.dependencies.ensure_sudo_credentials", return_value=True)
    @patch("installer.steps.dependencies.needs_sudo", return_value=True)
    @patch("installer.steps.dependencies.install_claude_code", side_effect=RuntimeError("boom"))
    def test_run_resets_sudo_state_on_exception(
        self,
        _mock_install,
        _mock_needs_sudo,
        _mock_ensure,
        mock_start,
        mock_stop,
    ):
        """Dependency step always tears down keepalive and sudo fallback state."""
        import installer.steps.dependencies as deps
        from installer.context import InstallContext
        from installer.steps.dependencies import DependenciesStep
        from installer.ui import Console

        deps._allow_sudo_fallback = False
        step = DependenciesStep()

        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = InstallContext(
                project_dir=Path(tmpdir),
                ui=Console(non_interactive=False),
            )

            with pytest.raises(RuntimeError, match="boom"):
                step.run(ctx)

        mock_start.assert_called_once()
        mock_stop.assert_called_once()
        assert deps._allow_sudo_fallback is False

    @patch("installer.steps.dependencies.stop_sudo_keepalive")
    @patch("installer.steps.dependencies.start_sudo_keepalive")
    @patch("installer.steps.dependencies.ensure_sudo_credentials", side_effect=[True, True])
    @patch("installer.steps.dependencies.needs_sudo", return_value=True)
    @patch("installer.steps.dependencies._precache_npx_mcp_servers", return_value=True)
    @patch("installer.steps.dependencies.install_context_mode_plugin", return_value=True)
    @patch("installer.steps.dependencies.initialize_codegraph", return_value=True)
    @patch("installer.steps.dependencies.codegraph_needs_work", return_value=False)
    @patch("installer.steps.dependencies.install_codegraph", return_value=True)
    @patch("installer.steps.dependencies.install_rtk", return_value=True)
    @patch("installer.steps.dependencies.install_agent_browser", return_value=True)
    @patch("installer.steps.dependencies.install_ccusage", return_value=True)
    @patch("installer.steps.dependencies.install_pbt_tools", return_value=True)
    @patch("installer.steps.dependencies.install_golangci_lint", return_value=True)
    @patch("installer.steps.dependencies.install_prettier", return_value=True)
    @patch("installer.steps.dependencies.install_typescript_lsp", return_value=True)
    @patch("installer.steps.dependencies._install_plugin_dependencies", return_value=True)
    @patch("installer.steps.dependencies._setup_pilot_memory", return_value=True)
    @patch("installer.steps.dependencies.install_python_tools", return_value=True)
    @patch("installer.steps.dependencies.install_uv", return_value=True)
    @patch("installer.steps.dependencies.install_nodejs", return_value=True)
    @patch("installer.steps.dependencies.install_claude_code", return_value=True)
    def test_run_reauths_after_spinner_closes_and_continues(
        self,
        _mock_claude,
        _mock_node,
        _mock_uv,
        _mock_python,
        _mock_memory,
        _mock_plugin_deps,
        _mock_ts_lsp,
        _mock_prettier,
        _mock_golangci,
        _mock_pbt,
        _mock_ccusage,
        _mock_agent_browser,
        _mock_rtk,
        _mock_codegraph,
        _mock_needs_work,
        _mock_initialize_codegraph,
        _mock_ctx_mode_plugin,
        _mock_precache,
        _mock_needs_sudo,
        mock_ensure,
        mock_start,
        mock_stop,
    ):
        """A sudo expiry during one package install closes the spinner, reauths, and completes."""
        from contextlib import contextmanager

        import installer.steps.dependencies as deps
        from installer.context import InstallContext
        from installer.steps.dependencies import DependenciesStep

        class _FakeProgress:
            def advance(self, amount: int = 1) -> None:
                pass

        class RecordingUI:
            quiet = False

            def __init__(self) -> None:
                self.events: list[tuple[str, str]] = []

            @contextmanager
            def spinner(self, message: str):
                self.events.append(("spinner_start", message))
                try:
                    yield
                finally:
                    self.events.append(("spinner_end", message))

            @contextmanager
            def progress(self, total: int, description: str = "Processing"):
                self.events.append(("progress_start", description))
                try:
                    yield _FakeProgress()
                finally:
                    self.events.append(("progress_end", description))

            def status(self, message: str) -> None:
                self.events.append(("status", message))

            def success(self, message: str) -> None:
                self.events.append(("success", message))

            def warning(self, message: str) -> None:
                self.events.append(("warning", message))

            def info(self, message: str) -> None:
                self.events.append(("info", message))

        ui = RecordingUI()
        step = DependenciesStep()
        deps._allow_sudo_fallback = False

        # Use agent-browser (still sequential) to test sudo reauth flow
        ab_attempts = 0

        def flaky_agent_browser() -> bool:
            nonlocal ab_attempts
            ab_attempts += 1
            if ab_attempts == 1:
                raise deps._SudoReauthNeeded()
            return True

        with patch("installer.steps.dependencies.install_agent_browser", side_effect=flaky_agent_browser):
            with tempfile.TemporaryDirectory() as tmpdir:
                ctx = InstallContext(
                    project_dir=Path(tmpdir),
                    non_interactive=False,
                    ui=ui,
                )
                step.run(ctx)

        assert ab_attempts == 2
        assert mock_ensure.call_count == 2
        assert mock_start.call_count == 2
        mock_stop.assert_called_once()
        assert deps._allow_sudo_fallback is False
        assert "agent_browser" in ctx.config["installed_dependencies"]

        ab_flow = [
            event
            for event in ui.events
            if event[1] in {
                "Installing agent-browser (browser automation)...",
                "sudo credentials expired — re-authenticating...",
                "agent-browser (browser automation) installed",
            }
        ]
        assert ab_flow == [
            ("spinner_start", "Installing agent-browser (browser automation)..."),
            ("spinner_end", "Installing agent-browser (browser automation)..."),
            ("status", "sudo credentials expired — re-authenticating..."),
            ("spinner_start", "Installing agent-browser (browser automation)..."),
            ("spinner_end", "Installing agent-browser (browser automation)..."),
            ("success", "agent-browser (browser automation) installed"),
        ]


class TestParallelInstalls:
    """Tests for parallel installation infrastructure."""

    def test_run_install_silent_success(self):
        """_run_install_silent returns success result for passing install."""
        from installer.steps.dependencies import _InstallTask, _run_install_silent

        task = _InstallTask(name="TestPkg", key="test_pkg", fn=lambda: True)
        result = _run_install_silent(task)

        assert result.success is True
        assert result.name == "TestPkg"
        assert result.key == "test_pkg"
        assert result.error == ""

    def test_run_install_silent_failure(self):
        """_run_install_silent captures error on failure."""
        from installer.steps.dependencies import _InstallTask, _run_install_silent

        def failing_fn():
            from installer.steps.dependencies import _thread_local

            _thread_local.last_retry_stderr = "npm ERR! code EACCES"
            return False

        task = _InstallTask(name="FailPkg", key="fail_pkg", fn=failing_fn)
        result = _run_install_silent(task)

        assert result.success is False
        assert "EACCES" in result.error

    def test_run_install_silent_catches_sudo_reauth(self):
        """_run_install_silent catches _SudoReauthNeeded and returns failure."""
        from installer.steps.dependencies import (
            _InstallTask,
            _SudoReauthNeeded,
            _run_install_silent,
        )

        def sudo_fn():
            raise _SudoReauthNeeded()

        task = _InstallTask(name="SudoPkg", key="sudo_pkg", fn=sudo_fn)
        result = _run_install_silent(task)

        assert result.success is False
        assert "sudo credentials expired" in result.error

    def test_run_install_silent_catches_exceptions(self):
        """_run_install_silent catches unexpected exceptions gracefully."""
        from installer.steps.dependencies import _InstallTask, _run_install_silent

        def exploding_fn():
            raise RuntimeError("disk full")

        task = _InstallTask(name="BoomPkg", key="boom_pkg", fn=exploding_fn)
        result = _run_install_silent(task)

        assert result.success is False
        assert "disk full" in result.error

    def test_run_parallel_installs_returns_installed_keys(self):
        """_run_parallel_installs returns keys of successfully installed packages."""
        from installer.steps.dependencies import _InstallTask, _run_parallel_installs

        tasks = [
            _InstallTask(name="Pkg A", key="pkg_a", fn=lambda: True),
            _InstallTask(name="Pkg B", key="pkg_b", fn=lambda: True),
            _InstallTask(name="Pkg C", key="pkg_c", fn=lambda: False),
        ]

        installed = _run_parallel_installs(tasks, ui=None)

        assert "pkg_a" in installed
        assert "pkg_b" in installed
        assert "pkg_c" not in installed

    def test_run_parallel_installs_with_ui_reports_results(self):
        """_run_parallel_installs reports success/failure via UI."""
        from installer.steps.dependencies import _InstallTask, _run_parallel_installs

        class _FakeProgress:
            def advance(self, amount: int = 1) -> None:
                pass

        class FakeUI:
            def __init__(self):
                self.successes = []
                self.warnings = []
                self.infos = []

            @contextmanager
            def progress(self, total, description="Processing"):
                yield _FakeProgress()

            def success(self, msg):
                self.successes.append(msg)

            def warning(self, msg):
                self.warnings.append(msg)

            def info(self, msg):
                self.infos.append(msg)

        ui = FakeUI()
        tasks = [
            _InstallTask(name="Good", key="good", fn=lambda: True),
            _InstallTask(name="Bad", key="bad", fn=lambda: False),
        ]

        installed = _run_parallel_installs(tasks, ui=ui)

        assert "good" in installed
        assert "bad" not in installed
        assert any("Good" in s for s in ui.successes)
        assert any("Bad" in w for w in ui.warnings)

    def test_run_parallel_installs_empty_list(self):
        """_run_parallel_installs handles empty task list."""
        from installer.steps.dependencies import _run_parallel_installs

        installed = _run_parallel_installs([], ui=None)
        assert installed == []

    def test_parallel_installs_are_actually_concurrent(self):
        """Verify parallel installs overlap in time (not sequential)."""
        from installer.steps.dependencies import _InstallTask, _run_parallel_installs

        def slow_fn():
            time.sleep(0.3)
            return True

        tasks = [
            _InstallTask(name=f"Pkg {i}", key=f"pkg_{i}", fn=slow_fn)
            for i in range(4)
        ]

        start = time.monotonic()
        installed = _run_parallel_installs(tasks, ui=None, max_workers=4)
        elapsed = time.monotonic() - start

        assert len(installed) == 4
        # 4 tasks x 0.3s each = 1.2s sequential, should be ~0.3s parallel
        assert elapsed < 0.8, f"Expected parallel execution but took {elapsed:.1f}s"

    def test_thread_local_error_isolation(self):
        """Thread-local error tracking isolates errors between parallel installs."""
        from installer.steps.dependencies import _InstallTask, _run_install_silent, _thread_local

        def fn_sets_error():
            _thread_local.last_retry_stderr = "error from thread A"
            return False

        def fn_no_error():
            _thread_local.last_retry_stderr = ""
            return True

        task_a = _InstallTask(name="A", key="a", fn=fn_sets_error)
        task_b = _InstallTask(name="B", key="b", fn=fn_no_error)

        result_a = _run_install_silent(task_a)
        result_b = _run_install_silent(task_b)

        assert result_a.success is False
        assert "error from thread A" in result_a.error
        assert result_b.success is True
        assert result_b.error == ""

    def test_install_task_with_args(self):
        """_InstallTask passes args to fn correctly."""
        from installer.steps.dependencies import _InstallTask, _run_install_silent

        def fn_with_args(a, b):
            return a + b == 3

        task = _InstallTask(name="ArgPkg", key="arg", fn=fn_with_args, args=(1, 2))
        result = _run_install_silent(task)

        assert result.success is True
