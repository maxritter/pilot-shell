#!/usr/bin/env python3
"""Detach quiet Codex bookkeeping hooks across Codex runtime versions."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from collections.abc import Sequence


def _resolve_command(args: Sequence[str]) -> list[str]:
    if not args:
        return []
    if args[0] == "--":
        return list(args[1:])
    if args[0] == "--python":
        return [sys.executable, *args[1:]]
    return list(args)


def main(args: Sequence[str] | None = None) -> int:
    """Copy hook input to a detached child and return without hook output."""
    command = _resolve_command(sys.argv[1:] if args is None else args)
    if not command:
        return 2

    try:
        with tempfile.TemporaryFile() as hook_input:
            hook_input.write(sys.stdin.buffer.read())
            hook_input.seek(0)
            if os.name == "posix":
                subprocess.Popen(  # noqa: S603
                    command,
                    stdin=hook_input,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                    start_new_session=True,
                )
            elif os.name == "nt":
                subprocess.Popen(  # noqa: S603
                    command,
                    stdin=hook_input,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                )
            else:
                subprocess.Popen(  # noqa: S603
                    command,
                    stdin=hook_input,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
    except (OSError, ValueError):
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
