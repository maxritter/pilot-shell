#!/usr/bin/env python3
"""SessionEnd hook - stops worker only when no other sessions are active."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

PILOT_BIN = Path.home() / ".pilot" / "bin" / "pilot"


def _get_active_session_count() -> int:
    """Get active session count from the pilot binary."""
    try:
        result = subprocess.run(
            [str(PILOT_BIN), "sessions", "--json"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("count", 0)
    except (json.JSONDecodeError, OSError, subprocess.TimeoutExpired):
        pass
    return 0


def main() -> int:
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if not plugin_root:
        return 1

    count = _get_active_session_count()
    if count > 1:
        return 0

    stop_script = Path(plugin_root) / "scripts" / "worker-service.cjs"
    result = subprocess.run(
        ["bun", str(stop_script), "stop"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
