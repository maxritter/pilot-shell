#!/usr/bin/env python3
"""SessionStart(clear) hook - reset session state when user runs /clear.

Removes stale spec artifacts (reviewer findings, plan association, stop guard,
context caches) and task list so the next /spec starts clean. Preserves
worktree.json since that tracks a physical git resource that outlives /clear.
"""

from __future__ import annotations

import os
from pathlib import Path

SESSIONS_DIR = Path.home() / ".pilot" / "sessions"

STALE_FILES = [
    "active_plan.json",
    "spec-stop-guard",
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
    claude_config = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
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
    session_id = os.environ.get("PILOT_SESSION_ID", "").strip()
    if not session_id:
        return 0

    session_dir = SESSIONS_DIR / session_id
    if not session_dir.is_dir():
        return 0

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

    _clean_task_list(session_id)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
