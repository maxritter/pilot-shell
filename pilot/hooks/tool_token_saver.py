#!/usr/bin/env python3
"""Hook to rewrite Bash commands via rtk for token savings.

Delegates all rewrite logic to `rtk rewrite` (Rust binary).
To add or change rewrite rules, edit the Rust registry — not this file.
Requires: rtk >= 0.23.0
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import NC, YELLOW

MIN_RTK_VERSION = (0, 23, 0)


def _parse_version(version_str: str) -> tuple[int, ...] | None:
    """Parse version string like '0.23.1' into tuple."""
    try:
        parts = version_str.strip().split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, IndexError):
        return None


def _get_rtk_version() -> tuple[int, ...] | None:
    """Get rtk version, or None if not available."""
    try:
        result = subprocess.run(
            ["rtk", "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        for word in result.stdout.split():
            version = _parse_version(word)
            if version:
                return version
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _rewrite_command(cmd: str) -> str | None:
    """Call rtk rewrite and return rewritten command, or None if no rewrite."""
    try:
        result = subprocess.run(
            ["rtk", "rewrite", cmd],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        rewritten = result.stdout.strip()
        if not rewritten or rewritten == cmd:
            return None
        return rewritten
    except (OSError, subprocess.TimeoutExpired):
        return None


def run_tool_token_saver() -> int:
    """Rewrite Bash commands via rtk for token savings."""
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    cmd = hook_data.get("tool_input", {}).get("command")
    if not cmd:
        return 0

    if not shutil.which("rtk"):
        sys.stderr.write(
            f"{YELLOW}[rtk] WARNING: rtk is not installed or not in PATH. "
            f"Install: https://github.com/rtk-ai/rtk#installation{NC}\n"
        )
        return 0

    version = _get_rtk_version()
    if version and version < MIN_RTK_VERSION:
        min_str = ".".join(str(v) for v in MIN_RTK_VERSION)
        ver_str = ".".join(str(v) for v in version)
        sys.stderr.write(
            f"{YELLOW}[rtk] WARNING: rtk {ver_str} is too old (need >= {min_str}). Upgrade: cargo install rtk{NC}\n"
        )
        return 0

    rewritten = _rewrite_command(cmd)
    if not rewritten:
        return 0

    updated_input = dict(hook_data.get("tool_input", {}))
    updated_input["command"] = rewritten

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "updatedInput": updated_input,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(run_tool_token_saver())
