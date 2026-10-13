"""Central hook gate keeps inactive Pilot hooks from touching host-agent work."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from unittest.mock import patch

from pilot.hooks.run_if_licensed import acquire_single_flight, main, pilot_access_is_active


def _licensed_home(tmp_path: Path) -> Path:
    pilot_dir = tmp_path / ".pilot"
    pilot_dir.mkdir()
    (pilot_dir / ".license").write_text("signed-state")
    return tmp_path


def test_single_flight_skips_while_another_run_holds_the_lock(tmp_path: Path) -> None:
    home = _licensed_home(tmp_path)
    held = acquire_single_flight("summarize", home)
    assert held is not None
    try:
        with (
            patch("pilot.hooks.run_if_licensed.Path.home", return_value=home),
            patch("pilot.hooks.run_if_licensed.os.execvp") as execvp,
        ):
            assert main(["--single-flight", "summarize", "--exec", "bun", "worker.cjs"]) == 0
        execvp.assert_not_called()
    finally:
        os.close(held)


def test_single_flight_runs_when_the_lock_is_free(tmp_path: Path) -> None:
    home = _licensed_home(tmp_path)
    with (
        patch("pilot.hooks.run_if_licensed.Path.home", return_value=home),
        patch("pilot.hooks.run_if_licensed.os.execvp") as execvp,
    ):
        assert main(["--single-flight", "summarize", "--exec", "bun", "worker.cjs"]) == 0
    execvp.assert_called_once_with("bun", ["bun", "worker.cjs"])


def test_single_flight_lock_lives_as_long_as_the_exec_d_hook(tmp_path: Path) -> None:
    # A real exec: the hook process keeps the lock until it exits, so a second run skips meanwhile.
    home = _licensed_home(tmp_path)
    gate = Path(__file__).resolve().parents[1] / "run_if_licensed.py"
    ready = tmp_path / "ready"
    release = tmp_path / "release"
    hook = tmp_path / "slow_hook.py"
    hook.write_text(
        textwrap.dedent(
            f"""
            import pathlib, time
            pathlib.Path({str(ready)!r}).write_text("up")
            deadline = time.time() + 10
            while not pathlib.Path({str(release)!r}).exists() and time.time() < deadline:
                time.sleep(0.05)
            """
        )
    )
    env = {**os.environ, "HOME": str(home)}
    first = subprocess.Popen(
        [sys.executable, str(gate), "--single-flight", "t", "--exec", sys.executable, str(hook)], env=env
    )
    try:
        deadline = time.monotonic() + 10
        while not ready.exists() and first.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        assert ready.exists(), "the first hook never started"
        assert acquire_single_flight("t", home) is None, "the lock was not held by the running hook"
    finally:
        release.write_text("go")
        first.wait(timeout=10)
    fd = acquire_single_flight("t", home)
    assert fd is not None, "the lock was not released when the hook exited"
    os.close(fd)


def test_single_flight_refuses_an_unsafe_lock_name(tmp_path: Path) -> None:
    home = _licensed_home(tmp_path)
    assert acquire_single_flight("../escape", home) is None
    assert not (home / ".pilot" / "state" / "escape.lock").exists()


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
