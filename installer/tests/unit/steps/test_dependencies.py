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

    @patch("installer.steps.dependencies.install_sx", return_value=True)
    @patch("installer.steps.dependencies.update_sx", return_value=True)
    @patch("installer.steps.dependencies._install_probe_with_ui", return_value=True)
    @patch("installer.steps.dependencies._install_playwright_cli_with_ui", return_value=True)
    @patch("installer.steps.dependencies.install_ccusage", return_value=True)
    @patch("installer.steps.dependencies.install_pbt_tools", return_value=True)
    @patch("installer.steps.dependencies.install_golangci_lint", return_value=True)
    @patch("installer.steps.dependencies.install_prettier", return_value=True)
    @patch("installer.steps.dependencies.install_typescript_lsp", return_value=True)
    @patch("installer.steps.dependencies._precache_npx_mcp_servers", return_value=True)
    @patch("installer.steps.dependencies._install_plugin_dependencies")
    @patch("installer.steps.dependencies._setup_pilot_memory")
    @patch("installer.steps.dependencies.install_python_tools")
    @patch("installer.steps.dependencies.install_uv")
    @patch("installer.steps.dependencies.install_nodejs")
    def test_dependencies_run_installs_core(
        self,
        mock_nodejs,
        mock_uv,
        mock_python_tools,
        mock_setup_pilot_memory,
        mock_plugin_deps,
        _mock_precache,
        _mock_ts_lsp,
        _mock_prettier,
        _mock_golangci_lint,
        _mock_pbt_tools,
        _mock_ccusage,
        _mock_playwright,
        _mock_probe_ui,
        _mock_sx,
        _mock_update_sx,
    ):
        """DependenciesStep installs all dependencies including Python tools."""
        from installer.context import InstallContext
        from installer.steps.dependencies import DependenciesStep
        from installer.ui import Console

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

            mock_nodejs.assert_called_once()
            mock_uv.assert_called_once()
            mock_python_tools.assert_called_once()
            mock_plugin_deps.assert_called_once()


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

    @patch("installer.steps.dependencies._is_probe_installed")
    def test_install_probe_skips_if_already_installed(self, mock_installed):
        """install_probe skips installation if already installed."""
        from installer.steps.dependencies import install_probe

        mock_installed.return_value = True

        result = install_probe()

        assert result is True

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_probe_installed")
    def test_install_probe_runs_npm_install(self, mock_installed, mock_bash):
        """install_probe runs npm install when not installed."""
        from installer.steps.dependencies import install_probe

        mock_installed.return_value = False
        mock_bash.return_value = True

        result = install_probe()

        assert result is True
        mock_bash.assert_called_once()
        call_args = mock_bash.call_args[0][0]
        assert "@probelabs/probe" in call_args

    @patch("installer.steps.dependencies._run_bash_with_retry")
    @patch("installer.steps.dependencies._is_probe_installed")
    def test_install_probe_returns_false_on_failure(self, mock_installed, mock_bash):
        """install_probe returns False when npm install fails."""
        from installer.steps.dependencies import install_probe

        mock_installed.return_value = False
        mock_bash.return_value = False

        result = install_probe()

        assert result is False


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
