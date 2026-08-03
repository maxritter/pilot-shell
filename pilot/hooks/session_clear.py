#!/usr/bin/env python3
"""SessionStart(clear) hook - reset session state when user runs /clear.

Removes stale spec artifacts (reviewer findings, plan association, stop guard,
context caches) and task list so the next /spec starts clean. Preserves
worktree.json since that tracks a physical git resource that outlives /clear.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import claude_config_dir, resolve_session_id

SESSIONS_DIR = Path.home() / ".pilot" / "sessions"

STALE_FILES = [
    "active_plan.json",
    "plan-mode-active",  # keep in sync with PLAN_MODE_SENTINEL in _lib/util.py (no _lib import here by design)
    "spec-stop-guard",
    "spec-approval-pending",
    "continuation.md",
    "context-cache.json",
    "context-pct.json",
    "pre-compact-state.json",
]

# Glob patterns for files with variable names (e.g. findings include plan slug)
STALE_PATTERNS = [
    "findings-spec-review*.json",
    "findings-changes-review*.json",
    "findings-codex-spec-review*.json",
    "findings-codex-changes-review*.json",
]


def _clean_task_list(session_id: str) -> None:
    """Remove stale task files so the next /spec doesn't resume old tasks.

    CLAUDE_CODE_TASK_LIST_ID is 'pilot-<PID>' where PID == PILOT_SESSION_ID.
    """
    claude_config = claude_config_dir()
    if claude_config is None:
        return
    task_dir = claude_config / "tasks" / f"pilot-{session_id}"
    if not task_dir.is_dir():
        return
    try:
        for f in task_dir.iterdir():
            if f.suffix == ".json":
                try:
                    f.unlink(missing_ok=True)
                except OSError:
                    pass
    except OSError:
        pass


def main() -> int:
    # Stale-file cleanup follows the same agent-native chain as the rest of the hook
    # layer (issue #157) -- it must run even when PILOT_SESSION_ID is unset (IDE/desktop
    # launch), since active_plan.json / plan-mode-active / findings are already written
    # via resolve_session_id() elsewhere (_lib/util.py).
    session_dir = SESSIONS_DIR / resolve_session_id()
    if session_dir.is_dir():
        for name in STALE_FILES:
            try:
                (session_dir / name).unlink(missing_ok=True)
            except OSError:
                pass

        for pattern in STALE_PATTERNS:
            for f in session_dir.glob(pattern):
                try:
                    f.unlink(missing_ok=True)
                except OSError:
                    pass

    # Task-list cleanup needs the literal wrapper PID: CLAUDE_CODE_TASK_LIST_ID is set
    # to "pilot-<PID>" only by the claude()/codex() shell functions, so a non-wrapper
    # session (no PILOT_SESSION_ID) has no matching task dir to clean -- skip, don't
    # guess at a directory that can't exist.
    pilot_pid = os.environ.get("PILOT_SESSION_ID", "").strip()
    if pilot_pid:
        _clean_task_list(pilot_pid)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
