"""Block only Pilot skill prompts while access is inactive."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_PILOT_SKILLS = frozenset(
    {
        "benchmark",
        "build",
        "cleanup",
        "create-skill",
        "fix",
        "investigate",
        "prd",
        "setup-rules",
        "spec",
        "spec-bugfix-plan",
        "spec-bugfix-verify",
        "spec-implement",
        "spec-plan",
        "spec-verify",
    }
)
_INVOCATION = re.compile(
    r"(?<![A-Za-z0-9_/])(?:/|\$)("
    + "|".join(re.escape(name) for name in sorted(_PILOT_SKILLS, key=len, reverse=True))
    + r")(?![A-Za-z0-9_/-])"
)


def _access_is_active(home: Path | None = None) -> bool:
    pilot_dir = (home or Path.home()) / ".pilot"
    return (pilot_dir / ".license").is_file() and not (pilot_dir / ".license-access.json").exists()


def _inactive_reason() -> str:
    return (
        "Pilot Shell access is inactive, so this Pilot workflow is unavailable. "
        "Activate a valid key with `pilot activate <LICENSE_KEY>`, get a license at "
        "https://pilot-shell.com/pricing, or uninstall Pilot safely. "
        "Claude Code and Codex remain available for non-Pilot work."
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (OSError, json.JSONDecodeError):
        payload = {}

    if _access_is_active():
        print(json.dumps({"continue": True}))
        return 0

    event = str(payload.get("hook_event_name", "UserPromptSubmit"))
    prompt = payload.get("prompt", "")
    explicit_invocation = event == "UserPromptExpansion" or (
        isinstance(prompt, str) and _INVOCATION.search(prompt) is not None
    )
    if explicit_invocation:
        print(json.dumps({"decision": "block", "reason": _inactive_reason()}))
        return 0

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "Pilot Shell is inactive. Do not apply Pilot-managed rules or invoke Pilot-managed skills, "
                        "workflows, review agents, hooks, Console features, or Pilot tool integrations. Native agent "
                        "capabilities remain available."
                    ),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
