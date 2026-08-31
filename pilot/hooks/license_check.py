"""SessionStart hook: verify Pilot access without blocking the host agent.

Reads cached license state via `pilot verify --json`. If the license is
inactive, explains the recovery choices while allowing Claude Code to proceed.
Uses the existing 24h TTL cache in auth.py so this adds no network latency
on the happy path.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def main() -> None:
    pilot_bin = Path.home() / ".pilot" / "bin" / "pilot"
    if not pilot_bin.is_file():
        _allow()
        return

    try:
        result = subprocess.run(
            [str(pilot_bin), "verify", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        _allow()
        return

    try:
        data = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        _allow()
        return

    if data.get("valid", False):
        _allow()
        return

    state = data.get("state")
    if state is None and data.get("tier") == "trial" and data.get("trial_expired", False):
        state = "trial_expired"
    _notify(str(state or "invalid"))


def _allow() -> None:
    print(json.dumps({"continue": True}))


def _notify(state: str) -> None:
    if state == "deactivated":
        heading = "Pilot Shell access was deactivated, so Pilot features are now paused."
    elif state == "trial_expired":
        heading = "Your Pilot Shell trial has ended, so Pilot features are now paused."
    elif state == "validation_required":
        heading = "Pilot Shell could not verify this license, so Pilot features are paused."
    else:
        heading = "Pilot Shell needs an active license, so Pilot features are paused."

    message = "\n".join(
        [
            heading,
            "Pilot workflows, context, quality hooks, Console, and statusline metrics are unavailable.",
            "Claude Code and Codex remain usable, but without Pilot's engineering harness.",
            "Activate a new key: pilot activate <LICENSE_KEY>",
            "Get a license: https://pilot-shell.com/pricing",
            (
                "Not continuing with Pilot? Uninstall it safely: "
                "curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/uninstall.sh | bash"
            ),
        ]
    )
    print(
        json.dumps(
            {
                "continue": True,
                "systemMessage": message,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": (
                        "Pilot Shell is inactive. Do not apply Pilot-managed rules or invoke Pilot-managed "
                        "skills, review agents, hooks, tools, workflows, or Console features in this session. "
                        "Native Claude Code and Codex features remain available."
                    ),
                },
            }
        )
    )


if __name__ == "__main__":
    main()
