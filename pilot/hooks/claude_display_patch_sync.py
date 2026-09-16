#!/usr/bin/env python3
"""Repair Pilot's Claude display patch after Claude replaces its native binary."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path


def _context(message: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": message,
        }
    }


def _repair_attempt_key(state_dir: Path) -> str:
    candidates = [
        shutil.which("claude"),
        str(Path.home() / ".local" / "bin" / "claude"),
        str(Path.home() / ".claude" / "local" / "bin" / "claude"),
        "/usr/local/bin/claude",
    ]
    identity = "missing"
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        try:
            target = path.resolve(strict=True)
            stat = target.stat()
        except OSError:
            continue
        identity = f"{target}:{stat.st_mtime_ns}:{stat.st_size}"
        break
    try:
        source = json.loads((state_dir / "state.json").read_text()).get("source", {})
        commit = source.get("commit", "") if isinstance(source, dict) else ""
    except (OSError, json.JSONDecodeError, TypeError):
        commit = ""
    return hashlib.sha256(f"{identity}:{commit}".encode("utf-8")).hexdigest()


def _failure_context_once(state_dir: Path, message: str, attempt_key: str) -> dict:
    marker = state_dir / "repair-warning.json"
    fingerprint = hashlib.sha256(message.encode("utf-8")).hexdigest()
    try:
        previous = json.loads(marker.read_text())
    except (OSError, json.JSONDecodeError, TypeError):
        previous = {}
    if (
        isinstance(previous, dict)
        and previous.get("fingerprint") == fingerprint
        and previous.get("attempt_key") == attempt_key
    ):
        return {}
    try:
        marker.write_text(json.dumps({"fingerprint": fingerprint, "attempt_key": attempt_key}))
    except OSError:
        pass
    return _context(
        "Pilot could not restore Claude's inline tool and thinking details after a Claude Code update: "
        f"{message}. Ctrl+O still opens Claude's verbose transcript in this session. `pilot repair-display` "
        "retries visibly; if the installed patch kit does not support this Claude version, install a later Pilot "
        "update with a compatible kit. Automatic startup repair will not retry this same binary and kit."
    )


def _run_manager(argv: list[str]) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        if hasattr(os, "killpg"):
            os.killpg(process.pid, signal.SIGKILL)
        else:  # pragma: no cover - supported repair platforms are POSIX
            process.kill()
        process.communicate()
        raise
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)


def repair_on_startup(state_dir: Path | None = None) -> dict:
    """Run the installed offline repair manager and return SessionStart context."""
    directory = state_dir or Path.home() / ".pilot" / "claude-display-patch"
    manager = directory / "manager.py"
    if not manager.is_file():
        return {}
    attempt_key = _repair_attempt_key(directory)
    warning = directory / "repair-warning.json"
    try:
        prior_warning = json.loads(warning.read_text())
    except (OSError, json.JSONDecodeError, TypeError):
        prior_warning = {}
    if isinstance(prior_warning, dict) and prior_warning.get("attempt_key") == attempt_key:
        return {}
    try:
        result = _run_manager(
            [
                sys.executable,
                str(manager),
                "--repair",
                "--state-dir",
                str(directory),
                "--json",
            ]
        )
        payload = json.loads(result.stdout)
        status = payload.get("status") if isinstance(payload, dict) else None
        message = payload.get("message") if isinstance(payload, dict) else None
        if not isinstance(status, str) or not isinstance(message, str):
            raise ValueError("repair manager returned an invalid response")
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError) as error:
        return _failure_context_once(directory, str(error), attempt_key)

    if status == "patched":
        (directory / "repair-warning.json").unlink(missing_ok=True)
        return _context(
            "Pilot restored Claude's inline tool and thinking details after Claude Code replaced its binary. "
            "This already-running process cannot reload patched code: restart Claude Code once. Ctrl+O remains "
            "available until then."
        )
    if status == "failed" or result.returncode != 0:
        return _failure_context_once(directory, message, attempt_key)
    if status == "busy":
        return _context(
            "Another Claude Code session is already restoring Pilot's inline tool and thinking details. "
            "Restart Claude Code after that repair completes. Ctrl+O remains available in this process."
        )
    (directory / "repair-warning.json").unlink(missing_ok=True)
    return {}


def main() -> int:
    if not os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return 0
    try:
        result = repair_on_startup()
    except Exception:
        result = {}
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
