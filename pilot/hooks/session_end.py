#!/usr/bin/env python3
"""SessionEnd hook - completes session in Console and stops worker if last session.

1. Stops the worker only when the current session is the last active one
2. Marks the session as completed in the Console (so the sessions tab updates),
   which is also what triggers the team-memory export for that session

Both side-effects are handed off to detached subprocesses so this hook never
blocks on network or child-process I/O. Claude Code's harness may cancel the
SessionEnd hook at any point; detaching guarantees the work still completes.

The two halves are gated differently because the agents differ. Claude Code has
a real SessionEnd event and passes ``--session-end``. Codex has none, so this
script is registered on its ``Stop`` hook, which fires every assistant turn -
completing the session there would abort the in-flight SDK agent. Worker-stop is
safe per turn and stays unconditional; session completion needs the flag.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _lib.console_settings import get_console_url
from _lib.util import read_hook_stdin

SESSIONS_DIR = Path.home() / ".pilot" / "sessions"
SKIP_NAMES = {"default", "pipes"}

# Marks an invocation as a genuine end-of-session rather than an end-of-turn.
SESSION_END_FLAG = "--session-end"

# Fallbacks for the agent's own session id when the hook payload has none.
# PILOT_SESSION_ID is deliberately absent: it is the shell-wrapper / PID id, not
# the ``contentSessionId`` the Console registered at session-init, so posting it
# would always resolve to not_found while looking like it worked.
_CONTENT_SESSION_ID_ENV_CHAIN = ("CLAUDE_CODE_SESSION_ID", "CODEX_THREAD_ID")

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


def _resolve_content_session_id(hook_data: dict) -> str:
    """Resolve the agent's own session id, or "" when none is available.

    The hook payload is authoritative: its ``session_id`` is the exact value the
    Console stored as ``contentSessionId`` when the session was registered (see
    the platform adapters in console/src/cli/adapters/). The env chain is only a
    fallback for a harness that supplies no payload.
    """
    session_id = str(hook_data.get("session_id") or "").strip()
    if session_id:
        return session_id

    for var in _CONTENT_SESSION_ID_ENV_CHAIN:
        value = os.environ.get(var, "").strip()
        if value:
            return value

    return ""


def _complete_session(hook_data: dict) -> None:
    """Mark the current session as completed in the Console.

    Fully detached fire-and-forget. Spawns a short-lived Python subprocess
    that does the POST so this hook never blocks on network I/O — the harness
    can cancel the hook mid-flight and the notification still goes out in
    its own process group. Errors inside the worker are swallowed.
    """
    session_id = _resolve_content_session_id(hook_data)
    if not session_id:
        return

    try:
        _ = subprocess.Popen(
            [
                sys.executable,
                "-c",
                _COMPLETE_SESSION_WORKER,
                f"{get_console_url()}/api/sessions/complete",
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


def _extract_session_pid(name: str) -> int | None:
    """Extract PID from session directory name.

    Supports '{PID}' (wrapper) and '{PID}-{suffix}' (shell alias) formats.
    """
    first = name.split("-", 1)[0] if name else ""
    try:
        return int(first)
    except ValueError:
        return None


def _has_other_active_sessions() -> bool:
    """Check if any other sessions are still active.

    Iterates session directories directly (no subprocess) to avoid failures
    during shutdown. Supports both Pilot wrapper ('{PID}') and shell-alias
    ('{PID}-{suffix}') session directory formats. Skips the current session
    via PILOT_SESSION_ID. Returns True on any error (safe default: don't
    stop the worker).
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
            pid = _extract_session_pid(entry.name)
            if pid is None:
                continue
            try:
                os.kill(pid, 0)
            except OSError:
                continue

            return True

        return False
    except OSError:
        return True


def main() -> int:
    # Spawn the detached worker-stop BEFORE any network I/O so the critical
    # side effect (releasing the worker port, closing SQLite WAL handles) survives
    # even if the harness cancels this hook mid-flight.
    if not _has_other_active_sessions():
        stop_script = Path.home() / ".pilot" / "scripts" / "worker-service.cjs"
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

    # Only a genuine session end may complete the session. On Codex this script
    # runs on every Stop, and completing there would delete the in-memory session
    # and abort the SDK agent still draining the observation queue. Read stdin
    # only on that path so an end-of-turn invocation never waits on the pipe.
    if SESSION_END_FLAG in sys.argv[1:]:
        _complete_session(read_hook_stdin())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
