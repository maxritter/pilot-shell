"""Tests for finalize step."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

class TestGetPilotVersion:
    """Test _get_pilot_version function."""

    @patch("installer.steps.finalize.subprocess.run")
    def test_returns_version_from_pilot_binary(self, mock_run):
        """_get_pilot_version returns version from pilot --version output."""
        from installer.steps.finalize import _get_pilot_version

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Pilot Shell v5.2.3",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("installer.steps.finalize.Path.home", return_value=Path(tmpdir)):
                bin_dir = Path(tmpdir) / ".pilot" / "bin"
                bin_dir.mkdir(parents=True)
                pilot_path = bin_dir / "pilot"
                pilot_path.write_text("#!/bin/bash\necho 'Pilot Shell v5.2.3'")

                version = _get_pilot_version()
                assert version == "5.2.3"

    @patch("installer.steps.finalize.subprocess.run")
    def test_returns_dev_version_from_pilot_binary(self, mock_run):
        """_get_pilot_version returns dev version from pilot --version output."""
        from installer.steps.finalize import _get_pilot_version

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Pilot Shell vdev-abc1234-20260125",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("installer.steps.finalize.Path.home", return_value=Path(tmpdir)):
                bin_dir = Path(tmpdir) / ".pilot" / "bin"
                bin_dir.mkdir(parents=True)
                pilot_path = bin_dir / "pilot"
                pilot_path.write_text("#!/bin/bash")

                version = _get_pilot_version()
                assert version == "dev-abc1234-20260125"

    def test_returns_fallback_when_pilot_not_found(self):
        """_get_pilot_version returns installer version when pilot not found."""
        from installer import __version__
        from installer.steps.finalize import _get_pilot_version

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("installer.steps.finalize.Path.home", return_value=Path(tmpdir)):
                version = _get_pilot_version()
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

            assert step.check(ctx) is False


class TestKillStaleWorker:
    """Test FinalizeStep._kill_stale_worker."""

    @patch("installer.steps.finalize.subprocess.run")
    def test_kills_pids_found_by_lsof(self, mock_run):
        """Calls kill -9 for each PID returned by lsof."""
        from installer.steps.finalize import FinalizeStep

        mock_run.side_effect = [
            MagicMock(stdout="1234\n5678\n"),  # lsof result
            MagicMock(),  # kill 1234
            MagicMock(),  # kill 5678
        ]

        FinalizeStep._kill_stale_worker()

        assert mock_run.call_count == 3
        mock_run.assert_any_call(["kill", "-9", "1234"], capture_output=True, timeout=5)
        mock_run.assert_any_call(["kill", "-9", "5678"], capture_output=True, timeout=5)

    @patch("installer.steps.finalize.subprocess.run")
    def test_does_nothing_when_no_pids(self, mock_run):
        """Does not call kill when lsof returns no PIDs."""
        from installer.steps.finalize import FinalizeStep

        mock_run.return_value = MagicMock(stdout="")

        FinalizeStep._kill_stale_worker()

        mock_run.assert_called_once()  # only lsof, no kill

    @patch("installer.steps.finalize.subprocess.run", side_effect=FileNotFoundError("lsof not found"))
    def test_swallows_exception_when_lsof_missing(self, _mock_run):
        """Does not raise when lsof is not installed."""
        from installer.steps.finalize import FinalizeStep

        FinalizeStep._kill_stale_worker()  # must not raise


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

            with patch.object(console, "next_steps") as mock_next_steps:
                step.run(ctx)

                mock_next_steps.assert_called()
