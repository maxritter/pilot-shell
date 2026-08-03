#!/usr/bin/env python3
"""SessionStart hook (Claude Code only): warn when the Claude profile has drifted.

Pilot records the Claude config directory it was last installed into. When the
directory serving THIS session is a different one, the assets in it are stale
(or absent) and the user almost certainly did not intend the mismatch - typically
after re-installing into a second profile, or after setting/unsetting
CLAUDE_CONFIG_DIR between installs.

Known limitation, stated plainly because it bounds what this can do: the guard
cannot fire when the resolved directory has NO Pilot install, because then no
Pilot hook is registered there to run. The install-time report in
installer/steps/finalize.py covers that case; this hook covers the rest.

The recorded value is used ONLY for this comparison. It is never consulted to
resolve a path - resolution is ambient-env-only (see _lib/util.claude_config_dir).

Stdlib only (package boundary); never raises.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import claude_config_dir  # noqa: E402

RECORD_FILENAME = "last-claude-config-dir"


def _state_path() -> Path:
    """Location of the install-time record. Mirrors ~/.pilot/state/ convention."""
    return Path.home() / ".pilot" / "state" / RECORD_FILENAME


def _canonical(path: Path) -> str:
    """Comparable form: resolves symlinks and normalises trailing slashes.

    Falls back to lexical normalisation when the path does not exist, so a
    recorded directory that has since been deleted still compares sensibly.
    """
    try:
        return str(path.resolve())
    except OSError:
        return os.path.normpath(str(path))


def record_path(record: Path, claude_dir: Path) -> None:
    """Persist the config dir Pilot was installed into. Never raises."""
    try:
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(str(claude_dir), encoding="utf-8")
    except OSError:
        pass


def resolve_warning(record: Path, active_dir: Path | None) -> str | None:
    """Return a warning when the recorded and active config dirs differ.

    None (stay silent) when: there is no record yet, the record is unreadable,
    the two directories match, or the active dir could not be resolved at all
    (an invalid CLAUDE_CONFIG_DIR is a different problem, reported elsewhere).
    """
    if active_dir is None:
        return None
    try:
        recorded_raw = record.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    if not recorded_raw:
        return None

    recorded = Path(recorded_raw)
    if _canonical(recorded) == _canonical(active_dir):
        return None

    return (
        "Pilot Shell - Claude config directory mismatch.\n\n"
        f"  Installed into: {recorded}\n"
        f"  This session:   {active_dir}\n\n"
        "Pilot's skills, rules and agents were installed into the first directory, so "
        "this session may be missing them or running stale copies.\n\n"
        "To fix, either relaunch against the installed profile:\n"
        f"  CLAUDE_CONFIG_DIR={recorded} claude\n"
        "or re-run the Pilot installer with this session's directory set, so the "
        "assets are installed there instead."
    )


def main() -> None:
    # Claude Code only - Codex has no SessionStart additionalContext channel here.
    if not os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return
    try:
        warning = resolve_warning(_state_path(), claude_config_dir())
        if not warning:
            return
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": (
                            "[Pilot config-directory check] Show the following to the user as "
                            "plainly formatted text, then continue with their request.\n\n" + warning
                        ),
                    }
                }
            )
        )
    except Exception:
        # SessionStart hook: never raise / never block the session.
        return


if __name__ == "__main__":
    main()
