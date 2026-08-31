"""Central hook gate keeps inactive Pilot hooks from touching host-agent work."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pilot.hooks.run_if_licensed import main, pilot_access_is_active


def test_inactive_marker_disables_hooks_even_when_old_license_file_remains(tmp_path: Path) -> None:
    pilot_dir = tmp_path / ".pilot"
    pilot_dir.mkdir()
    (pilot_dir / ".license").write_text("old-state")
    (pilot_dir / ".license-access.json").write_text('{"state":"deactivated"}')

    assert pilot_access_is_active(tmp_path) is False


def test_missing_license_disables_hooks_without_blocking(tmp_path: Path) -> None:
    with patch("pilot.hooks.run_if_licensed.Path.home", return_value=tmp_path):
        assert main(["/does/not/matter.py"]) == 0


def test_active_license_executes_python_hook(tmp_path: Path) -> None:
    pilot_dir = tmp_path / ".pilot"
    pilot_dir.mkdir()
    (pilot_dir / ".license").write_text("signed-state")
    hook = tmp_path / "hook.py"
    hook.write_text("pass")

    with (
        patch("pilot.hooks.run_if_licensed.Path.home", return_value=tmp_path),
        patch("pilot.hooks.run_if_licensed.os.execv") as execv,
    ):
        assert main([str(hook), "--flag"]) == 0

    execv.assert_called_once()
