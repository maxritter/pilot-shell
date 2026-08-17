"""Behavioral tests for the detached Codex bookkeeping launcher."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "codex_background.py"


def test_launcher_returns_before_child_and_preserves_hook_stdin(tmp_path: Path) -> None:
    output = tmp_path / "received.json"
    child = tmp_path / "child.py"
    child.write_text(
        "import pathlib, sys, time\ntime.sleep(0.8)\npathlib.Path(sys.argv[1]).write_text(sys.stdin.read())\n",
        encoding="utf-8",
    )
    payload = {"hook_event_name": "PostToolUse", "tool_name": "Bash"}

    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, str(HOOK), "--", sys.executable, str(child), str(output)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=2,
        check=False,
    )
    elapsed = time.monotonic() - started

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    assert elapsed < 0.5

    deadline = time.monotonic() + 2
    while not output.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert json.loads(output.read_text(encoding="utf-8")) == payload


def test_launcher_rejects_an_empty_command() -> None:
    result = subprocess.run(
        [sys.executable, str(HOOK), "--"],
        text=True,
        capture_output=True,
        timeout=2,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == ""
