"""Run one Pilot hook only while an active local license state exists."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def pilot_access_is_active(home: Path | None = None) -> bool:
    """Return whether hook execution is allowed by the latest verified state."""
    pilot_dir = (home or Path.home()) / ".pilot"
    if (pilot_dir / ".license-access.json").exists():
        return False
    return (pilot_dir / ".license").is_file()


def main(argv: list[str] | None = None) -> int:
    """Replace this process with a Python or external hook when access is active."""
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or not pilot_access_is_active():
        return 0

    if args[0] == "--exec":
        command = args[1:]
        if not command:
            return 0
        os.execvp(command[0], command)

    target = Path(args[0]).expanduser()
    if not target.is_file():
        return 0
    os.execv(sys.executable, [sys.executable, str(target), *args[1:]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
