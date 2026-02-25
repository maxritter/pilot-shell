"""Tests for dependencies step."""

from __future__ import annotations

import tempfile
from pathlib import Path
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

    @patch("installer.steps.dependencies.install_pbt_tools", return_value=True)
    @patch("installer.steps.dependencies.install_golangci_lint", return_value=True)
    @patch("installer.steps.dependencies.install_prettier", return_value=True)
    @patch("installer.steps.dependencies._precache_npx_mcp_servers", return_value=True)
    @patch("installer.steps.dependencies.install_vexor")
    @patch("installer.steps.dependencies._install_plugin_dependencies")
    @patch("installer.steps.dependencies._setup_pilot_memory")
    @patch("installer.steps.dependencies.install_claude_code")
    @patch("installer.steps.dependencies.install_python_tools")
    @patch("installer.steps.dependencies.install_uv")
    @patch("installer.steps.dependencies.install_nodejs")
    def test_dependencies_run_installs_core(
        self,
        mock_nodejs,
        mock_uv,
        mock_python_tools,
        mock_claude,
        mock_setup_pilot_memory,
        mock_plugin_deps,
        mock_vexor,
        _mock_precache,
        _mock_prettier,
        _mock_golangci_lint,
        _mock_pbt_tools,
    ):
        """DependenciesStep installs all dependencies including Python tools."""
        from installer.context import InstallContext
        from installer.steps.dependencies import DependenciesStep
        from installer.ui import Console

        mock_nodejs.return_value = True
        mock_uv.return_value = True
        mock_python_tools.return_value = True
        mock_claude.return_value = (True, "latest")
        mock_setup_pilot_memory.return_value = True
        mock_plugin_deps.return_value = True
        mock_vexor.return_value = True

        step = DependenciesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = InstallContext(
                project_dir=Path(tmpdir),
                ui=Console(non_interactive=True),
            )

            step.run(ctx)

            mock_nodejs.assert_called_once()
            mock_uv.assert_called_once()
            mock_python_tools.assert_called_once()
            mock_claude.assert_called_once()
            mock_plugin_deps.assert_called_once()


class TestDependencyInstallFunctions:
    """Test individual dependency install functions."""

    def test_install_nodejs_exists(self):
        """install_nodejs function exists."""
        from installer.steps.dependencies import install_nodejs

        assert callable(install_nodejs)

    def test_install_claude_code_exists(self):
        """install_claude_code function exists."""
        from installer.steps.dependencies import install_claude_code

        assert callable(install_claude_code)

    def test_install_uv_exists(self):
        """install_uv function exists."""
        from installer.steps.dependencies import install_uv

        assert callable(install_uv)

    def test_install_python_tools_exists(self):
        """install_python_tools function exists."""
        from installer.steps.dependencies import install_python_tools

        assert callable(install_python_tools)


class TestClaudeCodeInstall:
    """Test Claude Code installation via npm."""

    @patch("installer.steps.dependencies._get_forced_claude_version", return_value=None)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._clean_npm_stale_dirs")
    def test_install_claude_code_cleans_stale_dirs(self, mock_clean, _mock_run, _mock_version):
        """install_claude_code cleans stale npm temp directories before install."""
        from installer.steps.dependencies import install_claude_code

        with tempfile.TemporaryDirectory():
            install_claude_code()

        mock_clean.assert_called_once()

    @patch("installer.steps.dependencies._get_forced_claude_version", return_value=None)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    def test_install_claude_code_uses_npm(self, mock_run, _mock_version):
        """install_claude_code uses npm install -g."""
        from installer.steps.dependencies import install_claude_code

        with tempfile.TemporaryDirectory():
            success, version = install_claude_code()

        assert success is True
        assert version == "latest"
        mock_run.assert_called()
        call_args = mock_run.call_args[0][0]
        assert "npm install -g @anthropic-ai/claude-code" in call_args

    @patch("installer.steps.dependencies._get_forced_claude_version", return_value="2.1.19")
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    def test_install_claude_code_uses_version_tag(self, mock_run, _mock_version):
        """install_claude_code uses npm version tag for pinned version."""
        from installer.steps.dependencies import install_claude_code

        with tempfile.TemporaryDirectory():
            success, version = install_claude_code()

        assert success is True
        assert version == "2.1.19"
        mock_run.assert_called()
        call_args = mock_run.call_args[0][0]
        assert "npm install -g @anthropic-ai/claude-code@2.1.19" in call_args

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    @patch("installer.steps.dependencies._get_forced_claude_version", return_value=None)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=False)
    @patch("installer.steps.dependencies._get_installed_claude_version", return_value="1.0.0")
    def test_install_claude_code_succeeds_if_already_installed(
        self, _mock_get_ver, _mock_run, _mock_version, _mock_cmd_exists
    ):
        """install_claude_code returns success when npm fails but claude already exists."""
        from installer.steps.dependencies import install_claude_code

        with tempfile.TemporaryDirectory():
            success, version = install_claude_code()

        assert success is True, "Should succeed when claude is already installed"
        assert version == "1.0.0", "Should return actual installed version"

    @patch("installer.steps.dependencies._get_forced_claude_version", return_value="2.1.19")
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    def test_install_claude_code_with_ui_shows_pinned_version_info(self, _mock_run, _mock_version):
        """_install_claude_code_with_ui shows info about pinned version."""
        from installer.steps.dependencies import _install_claude_code_with_ui
        from installer.ui import Console

        ui = Console(non_interactive=True)
        info_calls = []
        _original_info = ui.info  # noqa: F841 - stored for potential restoration
        ui.info = lambda message: info_calls.append(message)

        with tempfile.TemporaryDirectory():
            result = _install_claude_code_with_ui(ui)

        assert result is True
        assert any("last stable release" in call for call in info_calls)
        assert any("FORCE_CLAUDE_VERSION" in call for call in info_calls)


class TestCleanNpmStaleDirs:
    """Test cleaning stale npm temp directories that cause ENOTEMPTY errors."""

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_clean_npm_stale_dirs_removes_temp_directories(self, _mock_cmd):
        """_clean_npm_stale_dirs removes .claude-code-* temp dirs under @anthropic-ai."""
        from installer.steps.dependencies import _clean_npm_stale_dirs

        with tempfile.TemporaryDirectory() as tmpdir:
            node_modules = Path(tmpdir) / "node_modules"
            anthropic_dir = node_modules / "@anthropic-ai"
            anthropic_dir.mkdir(parents=True)
            stale_dir = anthropic_dir / ".claude-code-HDmMpB7K"
            stale_dir.mkdir()
            (stale_dir / "package.json").write_text("{}")

            with patch("installer.steps.dependencies.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout=str(node_modules) + "\n")
                _clean_npm_stale_dirs()

            assert not stale_dir.exists(), "Stale temp directory should be removed"

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_clean_npm_stale_dirs_preserves_real_package(self, _mock_cmd):
        """_clean_npm_stale_dirs does not remove the real claude-code directory."""
        from installer.steps.dependencies import _clean_npm_stale_dirs

        with tempfile.TemporaryDirectory() as tmpdir:
            node_modules = Path(tmpdir) / "node_modules"
            anthropic_dir = node_modules / "@anthropic-ai"
            anthropic_dir.mkdir(parents=True)
            real_dir = anthropic_dir / "claude-code"
            real_dir.mkdir()
            (real_dir / "package.json").write_text("{}")

            with patch("installer.steps.dependencies.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout=str(node_modules) + "\n")
                _clean_npm_stale_dirs()

            assert real_dir.exists(), "Real claude-code directory should be preserved"

    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_clean_npm_stale_dirs_handles_npm_failure(self, _mock_cmd):
        """_clean_npm_stale_dirs does nothing when npm root fails."""
        from installer.steps.dependencies import _clean_npm_stale_dirs

        with patch("installer.steps.dependencies.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            _clean_npm_stale_dirs()

    def test_clean_npm_stale_dirs_skips_without_npm(self):
        """_clean_npm_stale_dirs does nothing when npm is not installed."""
        from installer.steps.dependencies import _clean_npm_stale_dirs

        with patch("installer.steps.dependencies.command_exists", return_value=False):
            with patch("installer.steps.dependencies.subprocess.run") as mock_run:
                _clean_npm_stale_dirs()
                mock_run.assert_not_called()


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


class TestVexorInstall:
    """Test Vexor semantic search installation."""

    def test_install_vexor_exists(self):
        """install_vexor function exists."""
        from installer.steps.dependencies import install_vexor

        assert callable(install_vexor)

    @patch("installer.steps.dependencies._configure_vexor_defaults")
    @patch("installer.steps.dependencies.command_exists")
    def test_install_vexor_skips_if_exists(self, mock_cmd_exists, mock_config):
        """install_vexor skips installation if already installed."""
        from installer.steps.dependencies import install_vexor

        mock_cmd_exists.return_value = True
        mock_config.return_value = True

        result = install_vexor()

        assert result is True
        mock_config.assert_called_once()

    def test_configure_vexor_defaults_creates_config(self):
        """_configure_vexor_defaults creates config file."""
        import json

        from installer.steps.dependencies import _configure_vexor_defaults

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                result = _configure_vexor_defaults()

                assert result is True
                config_path = Path(tmpdir) / ".vexor" / "config.json"
                assert config_path.exists()
                config = json.loads(config_path.read_text())
                assert config["model"] == "text-embedding-3-small"
                assert config["provider"] == "openai"
                assert config["rerank"] == "bm25"

    def test_configure_vexor_defaults_merges_existing(self):
        """_configure_vexor_defaults merges with existing config."""
        import json

        from installer.steps.dependencies import _configure_vexor_defaults

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".vexor"
            config_dir.mkdir()
            config_path = config_dir / "config.json"
            config_path.write_text(json.dumps({"custom_key": "custom_value"}))

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                result = _configure_vexor_defaults()

                assert result is True
                config = json.loads(config_path.read_text())
                assert config["custom_key"] == "custom_value"
                assert config["model"] == "text-embedding-3-small"

    @patch("installer.steps.dependencies._setup_vexor_local_model")
    @patch("installer.steps.dependencies._configure_vexor_local")
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.is_macos_arm64")
    @patch("installer.steps.dependencies._is_vexor_local_model_installed")
    @patch("installer.steps.dependencies.command_exists")
    def test_install_vexor_local_succeeds_when_model_download_fails(
        self, mock_cmd, mock_model, mock_mac, mock_bash, mock_config, mock_setup
    ):
        """install_vexor returns True when vexor installed but model pre-download fails."""
        from installer.steps.dependencies import install_vexor

        mock_cmd.return_value = False
        mock_model.return_value = False
        mock_mac.return_value = False
        mock_bash.return_value = True
        mock_config.return_value = True
        mock_setup.return_value = False

        mock_ui = MagicMock()
        result = install_vexor(use_local=True, ui=mock_ui)

        assert result is True
        mock_ui.info.assert_called_once_with("Embedding model will download on first use")

    @patch("installer.steps.dependencies._setup_vexor_local_model")
    @patch("installer.steps.dependencies._configure_vexor_local")
    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.is_macos_arm64")
    @patch("installer.steps.dependencies._is_vexor_local_model_installed")
    @patch("installer.steps.dependencies.command_exists")
    def test_install_vexor_local_fails_when_binary_install_fails(
        self, mock_cmd, mock_model, mock_mac, mock_bash, mock_config, mock_setup
    ):
        """install_vexor returns False when vexor binary installation fails."""
        from installer.steps.dependencies import install_vexor

        mock_cmd.return_value = False
        mock_model.return_value = False
        mock_mac.return_value = False
        mock_bash.return_value = False

        result = install_vexor(use_local=True)

        assert result is False
        mock_config.assert_not_called()
        mock_setup.assert_not_called()


class TestInstallPluginDependencies:
    """Test plugin dependencies installation via bun/npm install."""

    def test_install_plugin_dependencies_exists(self):
        """_install_plugin_dependencies function exists."""
        from installer.steps.dependencies import _install_plugin_dependencies

        assert callable(_install_plugin_dependencies)

    @patch("installer.steps.dependencies.Path")
    def test_install_plugin_dependencies_returns_false_if_no_plugin_dir(self, mock_path):
        """_install_plugin_dependencies returns False if plugin directory doesn't exist."""
        from installer.steps.dependencies import _install_plugin_dependencies

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_path.home.return_value = Path(tmpdir)
            result = _install_plugin_dependencies(Path(tmpdir), ui=None)
            assert result is False

    @patch("installer.steps.dependencies.Path")
    def test_install_plugin_dependencies_returns_false_if_no_package_json(self, mock_path):
        """_install_plugin_dependencies returns False if no package.json exists."""
        from installer.steps.dependencies import _install_plugin_dependencies

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / ".claude" / "pilot"
            plugin_dir.mkdir(parents=True)

            mock_path.home.return_value = Path(tmpdir)
            result = _install_plugin_dependencies(Path(tmpdir), ui=None)
            assert result is False

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.command_exists")
    @patch("installer.steps.dependencies.Path")
    def test_install_plugin_dependencies_runs_bun_install(self, mock_path, mock_cmd_exists, mock_run):
        """_install_plugin_dependencies runs bun install when bun is available."""
        from installer.steps.dependencies import _install_plugin_dependencies

        mock_cmd_exists.side_effect = lambda cmd: cmd == "bun"
        mock_run.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / ".claude" / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "package.json").write_text('{"name": "test"}')

            mock_path.home.return_value = Path(tmpdir)
            result = _install_plugin_dependencies(Path(tmpdir), ui=None)

            assert result is True
            mock_run.assert_called_with("bun install", cwd=plugin_dir)

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies.command_exists")
    @patch("installer.steps.dependencies.Path")
    def test_install_plugin_dependencies_falls_back_to_npm(self, mock_path, mock_cmd_exists, mock_run):
        """_install_plugin_dependencies falls back to npm install when bun is unavailable."""
        from installer.steps.dependencies import _install_plugin_dependencies

        mock_cmd_exists.side_effect = lambda cmd: cmd == "npm"
        mock_run.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / ".claude" / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "package.json").write_text('{"name": "test"}')

            mock_path.home.return_value = Path(tmpdir)
            result = _install_plugin_dependencies(Path(tmpdir), ui=None)

        assert result is True
        npm_calls = [c for c in mock_run.call_args_list if "npm" in str(c)]
        assert len(npm_calls) > 0, "npm install should be called when bun is unavailable"

    @patch("installer.steps.dependencies.command_exists")
    @patch("installer.steps.dependencies.Path")
    def test_install_plugin_dependencies_returns_false_when_no_package_manager(self, mock_path, mock_cmd_exists):
        """_install_plugin_dependencies returns False when neither bun nor npm is available."""
        from installer.steps.dependencies import _install_plugin_dependencies

        mock_cmd_exists.return_value = False

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / ".claude" / "pilot"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "package.json").write_text('{"name": "test"}')

            mock_path.home.return_value = Path(tmpdir)
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

    @patch("installer.steps.dependencies.subprocess.run")
    def test_is_ccusage_installed_returns_true_when_present(self, mock_run):
        """_is_ccusage_installed returns True when ccusage is globally installed."""
        from installer.steps.dependencies import _is_ccusage_installed

        mock_run.return_value = MagicMock(returncode=0, stdout="ccusage@1.0.0")
        assert _is_ccusage_installed() is True

    @patch("installer.steps.dependencies.subprocess.run")
    def test_is_ccusage_installed_returns_false_when_missing(self, mock_run):
        """_is_ccusage_installed returns False when ccusage is not installed."""
        from installer.steps.dependencies import _is_ccusage_installed

        mock_run.return_value = MagicMock(returncode=1, stdout="")
        assert _is_ccusage_installed() is False

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._is_ccusage_installed", return_value=False)
    def test_install_ccusage_installs_when_not_present(self, mock_check, mock_run):
        """install_ccusage runs npm install when ccusage not present."""
        from installer.steps.dependencies import install_ccusage

        result = install_ccusage()
        assert result is True
        mock_run.assert_called_once_with("npm install -g ccusage@latest")

    @patch("installer.steps.dependencies._is_ccusage_installed", return_value=True)
    def test_install_ccusage_skips_when_already_installed(self, mock_check):
        """install_ccusage returns True without installing when already present."""
        from installer.steps.dependencies import install_ccusage

        result = install_ccusage()
        assert result is True


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


class TestVexorMlxInstall:
    """Test Vexor MLX installation for macOS Apple Silicon."""

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_is_vexor_mlx_installed_true(self, _mock_cmd, mock_run):
        """Returns True when uv pip show finds mlx-embedding-models in vexor's env."""
        from installer.steps.dependencies import _is_vexor_mlx_installed

        with tempfile.TemporaryDirectory() as tmpdir:
            vexor_env = Path(tmpdir) / "vexor"
            vexor_env.mkdir()

            def run_side_effect(cmd, **kwargs):
                if cmd == ["uv", "tool", "dir"]:
                    return MagicMock(returncode=0, stdout=tmpdir + "\n")
                return MagicMock(returncode=0, stdout="Name: mlx-embedding-models")

            mock_run.side_effect = run_side_effect
            assert _is_vexor_mlx_installed() is True

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_is_vexor_mlx_installed_false_cpu_only(self, _mock_cmd, mock_run):
        """Returns False when CPU-only vexor is installed (mlx-embedding-models absent)."""
        from installer.steps.dependencies import _is_vexor_mlx_installed

        with tempfile.TemporaryDirectory() as tmpdir:
            vexor_env = Path(tmpdir) / "vexor"
            vexor_env.mkdir()

            def run_side_effect(cmd, **kwargs):
                if cmd == ["uv", "tool", "dir"]:
                    return MagicMock(returncode=0, stdout=tmpdir + "\n")
                return MagicMock(returncode=1, stdout="", stderr="Package not found")

            mock_run.side_effect = run_side_effect
            assert _is_vexor_mlx_installed() is False

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies.command_exists", return_value=True)
    def test_is_vexor_mlx_installed_false_no_vexor_env(self, _mock_cmd, mock_run):
        """Returns False when vexor tool env directory does not exist."""
        from installer.steps.dependencies import _is_vexor_mlx_installed

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = MagicMock(returncode=0, stdout=tmpdir + "\n")
            assert _is_vexor_mlx_installed() is False

    @patch("installer.steps.dependencies.command_exists", return_value=False)
    def test_is_vexor_mlx_installed_false_no_vexor(self, _mock_cmd):
        """Returns False when vexor is not installed at all."""
        from installer.steps.dependencies import _is_vexor_mlx_installed

        assert _is_vexor_mlx_installed() is False

    @patch("installer.steps.dependencies.subprocess.run")
    def test_clone_vexor_fork_clones_repo(self, mock_run):
        """_clone_vexor_fork clones to ~/.pilot/vexor."""
        from installer.steps.dependencies import _clone_vexor_fork

        mock_run.return_value = MagicMock(returncode=0)

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                (Path(tmpdir) / ".pilot").mkdir()
                result = _clone_vexor_fork()

        assert result is not None
        clone_call = mock_run.call_args[0][0]
        assert "git" in clone_call
        assert "clone" in clone_call
        assert "mlx-support" in clone_call
        assert "maxritter/vexor" in " ".join(clone_call)

    @patch("installer.steps.dependencies.subprocess.run")
    def test_clone_vexor_fork_updates_existing(self, mock_run):
        """_clone_vexor_fork fetches and checks out when dir exists."""
        from installer.steps.dependencies import _clone_vexor_fork

        mock_run.return_value = MagicMock(returncode=0)

        with tempfile.TemporaryDirectory() as tmpdir:
            vexor_dir = Path(tmpdir) / ".pilot" / "vexor"
            vexor_dir.mkdir(parents=True)

            with patch.object(Path, "home", return_value=Path(tmpdir)):
                result = _clone_vexor_fork()

        assert result is not None
        assert mock_run.call_count == 3

    @patch("installer.steps.dependencies.subprocess.run")
    def test_clone_vexor_fork_returns_none_on_failure(self, mock_run):
        """_clone_vexor_fork returns None when clone fails."""
        from installer.steps.dependencies import _clone_vexor_fork

        mock_run.return_value = MagicMock(returncode=1, stderr="fatal: error")

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                (Path(tmpdir) / ".pilot").mkdir()
                result = _clone_vexor_fork()

        assert result is None

    @patch("installer.steps.dependencies._setup_vexor_local_model", return_value=True)
    @patch("installer.steps.dependencies._configure_vexor_local", return_value=True)
    @patch("installer.steps.dependencies._install_vexor_from_local", return_value=True)
    @patch("installer.steps.dependencies._clone_vexor_fork")
    @patch("installer.steps.dependencies._is_vexor_local_model_installed", return_value=False)
    @patch("installer.steps.dependencies._is_vexor_mlx_installed", return_value=False)
    def test_install_vexor_mlx_full_flow(
        self, _mock_mlx_check, _mock_model_check, mock_clone, mock_install, mock_config, mock_setup
    ):
        """_install_vexor_mlx clones fork and installs with MLX extra."""
        from installer.steps.dependencies import _install_vexor_mlx

        mock_clone.return_value = Path("/tmp/fake-vexor")
        result = _install_vexor_mlx()

        assert result is True
        mock_clone.assert_called_once()
        mock_install.assert_called_once_with(Path("/tmp/fake-vexor"), extra="local-mlx")
        mock_config.assert_called_once()
        mock_setup.assert_called_once()

    @patch("installer.steps.dependencies._configure_vexor_local", return_value=True)
    @patch("installer.steps.dependencies._is_vexor_local_functional", return_value=True)
    @patch("installer.steps.dependencies._is_vexor_local_model_installed", return_value=True)
    @patch("installer.steps.dependencies._is_vexor_mlx_installed", return_value=True)
    def test_install_vexor_mlx_skips_if_already_installed(
        self, _mock_mlx_check, _mock_model_check, _mock_functional, mock_config
    ):
        """_install_vexor_mlx skips clone when MLX vexor already installed."""
        from installer.steps.dependencies import _install_vexor_mlx

        result = _install_vexor_mlx()

        assert result is True
        mock_config.assert_called_once()

    @patch("installer.steps.dependencies._setup_vexor_local_model", return_value=True)
    @patch("installer.steps.dependencies._configure_vexor_local", return_value=True)
    @patch("installer.steps.dependencies._install_vexor_from_local", return_value=True)
    @patch("installer.steps.dependencies._clone_vexor_fork")
    @patch("installer.steps.dependencies._is_vexor_local_functional", return_value=False)
    @patch("installer.steps.dependencies._is_vexor_local_model_installed", return_value=True)
    @patch("installer.steps.dependencies._is_vexor_mlx_installed", return_value=True)
    def test_install_vexor_mlx_reinstalls_when_not_functional(
        self, _mock_mlx, _mock_model, _mock_functional, mock_clone, mock_install, mock_config, mock_setup
    ):
        """_install_vexor_mlx reinstalls when MLX is present but not functional."""
        from installer.steps.dependencies import _install_vexor_mlx

        mock_clone.return_value = Path("/tmp/fake-vexor")
        result = _install_vexor_mlx()

        assert result is True
        mock_clone.assert_called_once()

    @patch("installer.steps.dependencies._setup_vexor_local_model", return_value=True)
    @patch("installer.steps.dependencies._configure_vexor_local", return_value=True)
    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies.command_exists", return_value=False)
    @patch("installer.steps.dependencies._clone_vexor_fork", return_value=None)
    @patch("installer.steps.dependencies._is_vexor_local_model_installed", return_value=False)
    @patch("installer.steps.dependencies._is_vexor_mlx_installed", return_value=False)
    def test_install_vexor_mlx_falls_back_to_cpu_on_clone_failure(
        self, _mock_mlx, _mock_model, _mock_clone, _mock_cmd, mock_run, mock_config, mock_setup
    ):
        """_install_vexor_mlx falls back to CPU when clone fails."""
        from installer.steps.dependencies import _install_vexor_mlx

        result = _install_vexor_mlx()

        assert result is True
        mock_run.assert_called_once_with("uv tool install 'vexor[local]' --reinstall")

    @patch("installer.steps.dependencies._install_vexor_mlx", return_value=True)
    @patch("installer.steps.dependencies.is_macos_arm64", return_value=True)
    def test_install_vexor_routes_to_mlx_on_macos_arm64(self, _mock_platform, mock_mlx):
        """install_vexor routes to MLX path on macOS arm64."""
        from installer.steps.dependencies import install_vexor

        result = install_vexor(use_local=True)

        assert result is True
        mock_mlx.assert_called_once()


class TestVexorLocalFunctional:
    """Test vexor local functionality runtime check."""

    @patch("installer.steps.dependencies.subprocess.run")
    def test_get_uv_tool_vexor_bin_returns_path(self, mock_run):
        """Returns vexor binary path when it exists in uv tool dir."""
        from installer.steps.dependencies import _get_uv_tool_vexor_bin

        with tempfile.TemporaryDirectory() as tmpdir:
            vexor_bin = Path(tmpdir) / "vexor" / "bin" / "vexor"
            vexor_bin.parent.mkdir(parents=True)
            vexor_bin.touch()

            mock_run.return_value = MagicMock(returncode=0, stdout=tmpdir + "\n")
            result = _get_uv_tool_vexor_bin()

            assert result == vexor_bin

    @patch("installer.steps.dependencies.subprocess.run")
    def test_get_uv_tool_vexor_bin_returns_none_when_missing(self, mock_run):
        """Returns None when vexor binary doesn't exist in uv tool dir."""
        from installer.steps.dependencies import _get_uv_tool_vexor_bin

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_run.return_value = MagicMock(returncode=0, stdout=tmpdir + "\n")
            result = _get_uv_tool_vexor_bin()

            assert result is None

    @patch("installer.steps.dependencies.subprocess.run")
    def test_get_uv_tool_vexor_bin_returns_none_on_uv_failure(self, mock_run):
        """Returns None when uv tool dir command fails."""
        from installer.steps.dependencies import _get_uv_tool_vexor_bin

        mock_run.return_value = MagicMock(returncode=1)
        result = _get_uv_tool_vexor_bin()

        assert result is None

    @patch("installer.steps.dependencies._get_uv_tool_vexor_bin")
    def test_is_vexor_local_functional_returns_false_when_no_binary(self, mock_bin):
        """Returns False when uv tool vexor binary not found."""
        from installer.steps.dependencies import _is_vexor_local_functional

        mock_bin.return_value = None
        assert _is_vexor_local_functional() is False

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies._get_uv_tool_vexor_bin")
    def test_is_vexor_local_functional_returns_true_when_working(self, mock_bin, mock_run):
        """Returns True when vexor index --help runs without error message."""
        from installer.steps.dependencies import _is_vexor_local_functional

        mock_bin.return_value = Path("/fake/vexor")
        mock_run.return_value = MagicMock(returncode=0, stdout="Usage: vexor index", stderr="")
        assert _is_vexor_local_functional() is True

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies._get_uv_tool_vexor_bin")
    def test_is_vexor_local_functional_returns_false_when_broken(self, mock_bin, mock_run):
        """Returns False when vexor reports local model support missing."""
        from installer.steps.dependencies import _is_vexor_local_functional

        mock_bin.return_value = Path("/fake/vexor")
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Local model support is not installed")
        assert _is_vexor_local_functional() is False

    @patch("installer.steps.dependencies.subprocess.run")
    @patch("installer.steps.dependencies._get_uv_tool_vexor_bin")
    def test_is_vexor_local_functional_handles_subprocess_exception(self, mock_bin, mock_run):
        """Returns False when subprocess raises an exception."""
        from installer.steps.dependencies import _is_vexor_local_functional

        mock_bin.return_value = Path("/fake/vexor")
        mock_run.side_effect = OSError("permission denied")
        assert _is_vexor_local_functional() is False


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

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._is_fast_check_installed", return_value=False)
    @patch("installer.steps.dependencies._is_hypothesis_installed", return_value=False)
    def test_install_pbt_tools_installs_hypothesis_when_missing(self, _mock_hyp, _mock_fc, mock_run):
        """install_pbt_tools installs hypothesis when not already installed."""
        from installer.steps.dependencies import install_pbt_tools

        install_pbt_tools()

        calls = [str(c) for c in mock_run.call_args_list]
        assert any("hypothesis" in c for c in calls)

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._is_fast_check_installed", return_value=False)
    @patch("installer.steps.dependencies._is_hypothesis_installed", return_value=True)
    def test_install_pbt_tools_skips_hypothesis_when_present(self, _mock_hyp, _mock_fc, mock_run):
        """install_pbt_tools skips hypothesis install when already present."""
        from installer.steps.dependencies import install_pbt_tools

        install_pbt_tools()

        calls = [str(c) for c in mock_run.call_args_list]
        assert not any("hypothesis" in c for c in calls)

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._is_fast_check_installed", return_value=False)
    @patch("installer.steps.dependencies._is_hypothesis_installed", return_value=True)
    def test_install_pbt_tools_installs_fast_check_when_missing(self, _mock_hyp, _mock_fc, mock_run):
        """install_pbt_tools installs fast-check when not already installed."""
        from installer.steps.dependencies import install_pbt_tools

        install_pbt_tools()

        calls = [str(c) for c in mock_run.call_args_list]
        assert any("fast-check" in c for c in calls)

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._is_fast_check_installed", return_value=True)
    @patch("installer.steps.dependencies._is_hypothesis_installed", return_value=True)
    def test_install_pbt_tools_skips_fast_check_when_present(self, _mock_hyp, _mock_fc, mock_run):
        """install_pbt_tools skips fast-check install when already present."""
        from installer.steps.dependencies import install_pbt_tools

        install_pbt_tools()

        calls = [str(c) for c in mock_run.call_args_list]
        assert not any("fast-check" in c for c in calls)

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=True)
    @patch("installer.steps.dependencies._is_fast_check_installed", return_value=True)
    @patch("installer.steps.dependencies._is_hypothesis_installed", return_value=True)
    def test_install_pbt_tools_returns_true_when_all_present(self, _mock_hyp, _mock_fc, _mock_run):
        """install_pbt_tools returns True when all packages already installed."""
        from installer.steps.dependencies import install_pbt_tools

        result = install_pbt_tools()

        assert result is True

    @patch("installer.steps.dependencies._run_bash_with_retry", return_value=False)
    @patch("installer.steps.dependencies._is_fast_check_installed", return_value=False)
    @patch("installer.steps.dependencies._is_hypothesis_installed", return_value=False)
    def test_install_pbt_tools_returns_false_on_install_failure(self, _mock_hyp, _mock_fc, _mock_run):
        """install_pbt_tools returns False when installations fail."""
        from installer.steps.dependencies import install_pbt_tools

        result = install_pbt_tools()

        assert result is False
