"""Tests for config files step."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


class TestConfigFilesStep:
    """Test ConfigFilesStep class."""

    def test_config_files_step_has_correct_name(self):
        """ConfigFilesStep has name 'config_files'."""
        from installer.steps.config_files import ConfigFilesStep

        step = ConfigFilesStep()
        assert step.name == "config_files"


class TestMCPConfigMerge:
    """Test MCP config merging."""

    def test_merge_adds_missing_servers(self):
        """Merging adds required servers that don't exist."""
        from installer.steps.config_files import merge_mcp_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".mcp.json"

            new_config = {
                "mcpServers": {
                    "tavily": {"command": "npx", "args": ["tavily"]},
                    "Ref": {"command": "npx", "args": ["ref"]},
                }
            }

            added = merge_mcp_config(config_file, new_config)

            assert added == 2  # tavily and Ref only (claude-context removed)
            result = json.loads(config_file.read_text())
            assert "tavily" in result["mcpServers"]
            assert "Ref" in result["mcpServers"]

    def test_merge_preserves_user_servers(self):
        """Merging preserves existing user servers."""
        from installer.steps.config_files import merge_mcp_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".mcp.json"

            existing = {"mcpServers": {"my-custom-server": {"command": "my-tool"}}}
            config_file.write_text(json.dumps(existing))

            new_config = {
                "mcpServers": {
                    "tavily": {"command": "npx", "args": ["tavily"]},
                    "Ref": {"command": "npx", "args": ["ref"]},
                }
            }

            added = merge_mcp_config(config_file, new_config)

            assert added == 2  # tavily and Ref only (claude-context removed)
            result = json.loads(config_file.read_text())
            assert "my-custom-server" in result["mcpServers"]
            assert "tavily" in result["mcpServers"]
            assert "Ref" in result["mcpServers"]

    def test_merge_skips_existing_required_servers(self):
        """Merging skips required servers that already exist."""
        from installer.steps.config_files import merge_mcp_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".mcp.json"

            existing = {
                "mcpServers": {
                    "my-server": {"command": "my-tool"},
                }
            }
            config_file.write_text(json.dumps(existing))

            new_config = {
                "mcpServers": {
                    "tavily": {"command": "npx", "args": ["tavily"]},
                    "Ref": {"command": "npx", "args": ["ref"]},
                }
            }

            added = merge_mcp_config(config_file, new_config)

            assert added == 2  # Only tavily and Ref added
            result = json.loads(config_file.read_text())
            assert "tavily" in result["mcpServers"]
            assert "Ref" in result["mcpServers"]
            assert "my-server" in result["mcpServers"]

    def test_merge_handles_empty_existing(self):
        """Merging handles empty existing config."""
        from installer.steps.config_files import merge_mcp_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".mcp.json"
            config_file.write_text("{}")

            new_config = {
                "mcpServers": {
                    "tavily": {"command": "npx"},
                }
            }

            added = merge_mcp_config(config_file, new_config)

            assert added == 1
            result = json.loads(config_file.read_text())
            assert "tavily" in result["mcpServers"]

    def test_merge_handles_invalid_json(self):
        """Merging handles invalid JSON in existing file."""
        from installer.steps.config_files import merge_mcp_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".mcp.json"
            config_file.write_text("not valid json {")

            new_config = {
                "mcpServers": {
                    "tavily": {"command": "npx"},
                }
            }

            added = merge_mcp_config(config_file, new_config)

            assert added == 1
            result = json.loads(config_file.read_text())
            assert "tavily" in result["mcpServers"]

    def test_merge_no_backup_created(self):
        """Merging does not create backup files."""
        from installer.steps.config_files import merge_mcp_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".mcp.json"

            existing = {"mcpServers": {"existing": {"command": "existing-server"}}}
            config_file.write_text(json.dumps(existing))

            new_config = {
                "mcpServers": {
                    "tavily": {"command": "npx"},
                }
            }

            merge_mcp_config(config_file, new_config)

            backup_files = list(Path(tmpdir).glob(".mcp.json.backup*"))
            assert len(backup_files) == 0, "No backup should be created"


class TestDirectoryInstallation:
    """Test .qlty directory installation."""

    def test_install_qlty_directory(self):
        """ConfigFilesStep installs .qlty directory."""
        from unittest.mock import patch

        from installer.context import InstallContext
        from installer.steps.config_files import ConfigFilesStep
        from installer.ui import Console

        step = ConfigFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            claude_dir = project_dir / ".claude"
            claude_dir.mkdir()

            template = {"setting": "value"}
            (claude_dir / "settings.local.template.json").write_text(json.dumps(template))

            ctx = InstallContext(
                project_dir=project_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path("/fake"),
            )

            with patch("installer.steps.config_files.download_directory") as mock_download:
                mock_download.return_value = 2
                step.run(ctx)

                calls = mock_download.call_args_list
                qlty_calls = [c for c in calls if ".qlty" in str(c)]
                assert len(qlty_calls) >= 1, "Should install .qlty directory"

    def test_skips_existing_directories(self):
        """ConfigFilesStep skips directories that already exist."""
        from unittest.mock import patch

        from installer.context import InstallContext
        from installer.steps.config_files import ConfigFilesStep
        from installer.ui import Console

        step = ConfigFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            claude_dir = project_dir / ".claude"
            claude_dir.mkdir()

            template = {"setting": "value"}
            (claude_dir / "settings.local.template.json").write_text(json.dumps(template))

            (project_dir / ".qlty").mkdir()

            ctx = InstallContext(
                project_dir=project_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path("/fake"),
            )

            with patch("installer.steps.config_files.download_directory") as mock_download:
                mock_download.return_value = 0
                step.run(ctx)

                calls = mock_download.call_args_list
                qlty_calls = [c for c in calls if ".qlty" in str(c)]
                assert len(qlty_calls) == 0, "Should skip existing .qlty"


class TestMCPConfigInstallation:
    """Test MCP config file installation and merging."""

    def test_installs_mcp_json(self):
        """ConfigFilesStep installs .mcp.json."""
        from unittest.mock import patch

        from installer.context import InstallContext
        from installer.steps.config_files import ConfigFilesStep
        from installer.ui import Console

        step = ConfigFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            claude_dir = project_dir / ".claude"
            claude_dir.mkdir()

            template = {"setting": "value"}
            (claude_dir / "settings.local.template.json").write_text(json.dumps(template))

            ctx = InstallContext(
                project_dir=project_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path("/fake"),
            )

            with patch("installer.steps.config_files.download_directory") as mock_dir:
                mock_dir.return_value = 0
                with patch("installer.steps.config_files.download_file") as mock_download:

                    def fake_download(path, dest, config, progress_callback=None):
                        if ".mcp.json" in path:
                            dest.write_text(
                                json.dumps(
                                    {
                                        "mcpServers": {
                                            "tavily": {"command": "npx"},
                                            "Ref": {"command": "npx"},
                                        }
                                    }
                                )
                            )
                            return True
                        return False

                    mock_download.side_effect = fake_download
                    step.run(ctx)

                    mcp_calls = [c for c in mock_download.call_args_list if ".mcp.json" in str(c)]
                    assert len(mcp_calls) >= 1, "Should install .mcp.json"

    def test_merges_mcp_config_preserving_user_servers(self):
        """ConfigFilesStep merges MCP config preserving user servers."""
        from unittest.mock import patch

        from installer.context import InstallContext
        from installer.steps.config_files import ConfigFilesStep
        from installer.ui import Console

        step = ConfigFilesStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            claude_dir = project_dir / ".claude"
            claude_dir.mkdir()

            template = {"setting": "value"}
            (claude_dir / "settings.local.template.json").write_text(json.dumps(template))

            existing_mcp = {"mcpServers": {"user-server": {"command": "my-tool"}}}
            (project_dir / ".mcp.json").write_text(json.dumps(existing_mcp))

            ctx = InstallContext(
                project_dir=project_dir,
                ui=Console(non_interactive=True),
                local_mode=True,
                local_repo_dir=Path("/fake"),
            )

            with patch("installer.steps.config_files.download_directory") as mock_dir:
                mock_dir.return_value = 0
                with patch("installer.steps.config_files.download_file") as mock_download:

                    def fake_download(path, dest, config, progress_callback=None):
                        if ".mcp.json" in path:
                            dest.write_text(
                                json.dumps(
                                    {
                                        "mcpServers": {
                                            "tavily": {"command": "npx"},
                                            "Ref": {"command": "npx"},
                                        }
                                    }
                                )
                            )
                            return True
                        return False

                    mock_download.side_effect = fake_download
                    step.run(ctx)

                    mcp_file = project_dir / ".mcp.json"
                    result = json.loads(mcp_file.read_text())
                    assert "user-server" in result["mcpServers"], "User server preserved"
                    assert "tavily" in result["mcpServers"], "tavily added"
                    assert "Ref" in result["mcpServers"], "Ref added"

                    backup_files = list(project_dir.glob(".mcp.json.backup*"))
                    assert len(backup_files) == 0, "No backup should be created"
