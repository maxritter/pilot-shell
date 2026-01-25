"""Tests for finalize step."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGetCcpVersion:
    """Test _get_ccp_version function."""

    @patch("installer.steps.finalize.subprocess.run")
    def test_returns_version_from_ccp_binary(self, mock_run):
        """_get_ccp_version returns version from ccp --version output."""
        from installer.steps.finalize import _get_ccp_version

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Claude CodePro v5.2.3",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("installer.steps.finalize.Path.cwd", return_value=Path(tmpdir)):
                # Create fake ccp binary
                bin_dir = Path(tmpdir) / ".claude" / "bin"
                bin_dir.mkdir(parents=True)
                ccp_path = bin_dir / "ccp"
                ccp_path.write_text("#!/bin/bash\necho 'Claude CodePro v5.2.3'")

                version = _get_ccp_version()
                assert version == "5.2.3"

    @patch("installer.steps.finalize.subprocess.run")
    def test_returns_dev_version_from_ccp_binary(self, mock_run):
        """_get_ccp_version returns dev version from ccp --version output."""
        from installer.steps.finalize import _get_ccp_version

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Claude CodePro vdev-abc1234-20260125",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("installer.steps.finalize.Path.cwd", return_value=Path(tmpdir)):
                bin_dir = Path(tmpdir) / ".claude" / "bin"
                bin_dir.mkdir(parents=True)
                ccp_path = bin_dir / "ccp"
                ccp_path.write_text("#!/bin/bash")

                version = _get_ccp_version()
                assert version == "dev-abc1234-20260125"

    def test_returns_fallback_when_ccp_not_found(self):
        """_get_ccp_version returns installer version when ccp not found."""
        from installer import __version__
        from installer.steps.finalize import _get_ccp_version

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("installer.steps.finalize.Path.cwd", return_value=Path(tmpdir)):
                # No ccp binary exists
                version = _get_ccp_version()
                assert version == __version__


class TestFinalizeStep:
    """Test FinalizeStep class."""

    def test_finalize_step_has_correct_name(self):
        """FinalizeStep has name 'finalize'."""
        from installer.steps.finalize import FinalizeStep

        step = FinalizeStep()
        assert step.name == "finalize"

    def test_check_always_returns_false(self):
        """check() always returns False (always runs)."""
        from installer.context import InstallContext
        from installer.steps.finalize import FinalizeStep
        from installer.ui import Console

        step = FinalizeStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            ctx = InstallContext(
                project_dir=project_dir,
                ui=Console(non_interactive=True),
            )

            # Finalize always runs
            assert step.check(ctx) is False


class TestFinalSuccessPanel:
    """Test final success panel display."""

    def test_run_displays_success_message(self):
        """run() displays success panel."""
        from installer.context import InstallContext
        from installer.steps.finalize import FinalizeStep
        from installer.ui import Console

        step = FinalizeStep()
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            (project_dir / ".claude").mkdir()

            console = Console(non_interactive=True)
            ctx = InstallContext(
                project_dir=project_dir,
                ui=console,
            )

            # Mock to capture output
            with patch.object(console, "next_steps") as mock_next_steps:
                step.run(ctx)

                # Should display next steps
                mock_next_steps.assert_called()
