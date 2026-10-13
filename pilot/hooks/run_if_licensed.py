"""Run one Pilot hook only while an active local license state exists."""

from __future__ import annotations

import fcntl
import os
import re
import sys
from pathlib import Path

_LOCK_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def pilot_access_is_active(home: Path | None = None) -> bool:
    """Return whether hook execution is allowed by the latest verified state."""
    pilot_dir = (home or Path.home()) / ".pilot"
    if (pilot_dir / ".license-access.json").exists():
        return False
    return (pilot_dir / ".license").is_file()


def acquire_single_flight(name: str, home: Path | None = None) -> int | None:
    """Take the machine-wide lock for `name`, or return None when another run holds it.

    The descriptor is made inheritable, so the lock lives as long as the exec'd hook process
    and the kernel releases it when that process exits, however it exits.
    """
    if not _LOCK_NAME.match(name):
        return None
    lock_dir = (home or Path.home()) / ".pilot" / "state" / "locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_dir / f"{name}.lock", os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    os.set_inheritable(fd, True)
    return fd


def main(argv: list[str] | None = None) -> int:
    """Replace this process with a Python or external hook when access is active."""
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or not pilot_access_is_active():
        return 0

    # --single-flight NAME: at most one run of this hook on the machine at a time. A run that
    # finds the lock held exits at once. Async hooks are not killed at their timeout, so without
    # this every agent's Stop hook starts its own copy and they pile up.
    if args[0] == "--single-flight":
        if len(args) < 2 or acquire_single_flight(args[1]) is None:
            return 0
        args = args[2:]
        if not args:
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
