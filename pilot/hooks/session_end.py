#!/usr/bin/env python3
"""SessionEnd hook - completes session in Console and stops worker if last session.

1. Marks the session as completed in the Console (so the sessions tab updates)
2. Stops the worker only when the current session is the last active one

Both side-effects are handed off to detached subprocesses so this hook never
blocks on network or child-process I/O. Claude Code's harness may cancel the
SessionEnd hook at any point; detaching guarantees the work still completes.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

SESSIONS_DIR = Path.home() / ".pilot" / "sessions"
SKIP_NAMES = {"default", "pipes"}
CONSOLE_URL = "http://localhost:41777"

# Inlined script run by the detached Console POST worker. Kept minimal so the
# subprocess startup cost is the only overhead when Console is down.
_COMPLETE_SESSION_WORKER = """
import json, sys, urllib.request
url, sid = sys.argv[1], sys.argv[2]
req = urllib.request.Request(
    url,
    data=json.dumps({'contentSessionId': sid}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
try:
    urllib.request.urlopen(req, timeout=5)
except Exception:
    pass
"""


def _complete_session() -> None:
    """Mark the current session as completed in the Console.

    Fully detached fire-and-forget. Spawns a short-lived Python subprocess
    that does the POST so this hook never blocks on network I/O — the harness
    can cancel the hook mid-flight and the notification still goes out in
    its own process group. Errors inside the worker are swallowed.
    """
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    if not session_id:
        return

    try:
        _ = subprocess.Popen(
            [
                sys.executable,
                "-c",
                _COMPLETE_SESSION_WORKER,
                f"{CONSOLE_URL}/api/sessions/complete",
                session_id,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )
    except OSError:
        pass


def _has_other_active_sessions() -> bool:
    """Check if any other Pilot wrapper sessions are still active.

    Iterates session directories directly (no subprocess) to avoid failures
    during shutdown. Skips the current session via PILOT_SESSION_ID.
    Returns True on any error (safe default: don't stop the worker).
    """
    try:
        if not SESSIONS_DIR.exists():
            return False

        my_session = os.environ.get("PILOT_SESSION_ID", "")

        for entry in SESSIONS_DIR.iterdir():
            if not entry.is_dir() or entry.name in SKIP_NAMES:
                continue
            if entry.name == my_session:
                continue
            try:
                pid = int(entry.name)
            except ValueError:
                continue
            try:
                os.kill(pid, 0)
            except OSError:
                continue

            # Another wrapper PID is alive → another session exists
            return True

        return False
    except OSError:
        # Can't read directory → assume other sessions exist (safe default)
        return True


def main() -> int:
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        return 0

    # Spawn the detached worker-stop BEFORE any network I/O so the critical
    # side effect (releasing port 41777, closing SQLite WAL handles) survives
    # even if the harness cancels this hook mid-flight.
    if not _has_other_active_sessions():
        stop_script = Path(plugin_root) / "scripts" / "worker-service.cjs"
        try:
            _ = subprocess.Popen(
                ["bun", str(stop_script), "stop"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                close_fds=True,
            )
        except OSError:
            pass

    # Mark session as completed in Console (fully detached, never blocks)
    _complete_session()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
