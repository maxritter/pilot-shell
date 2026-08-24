#!/usr/bin/env python3
"""SessionStart hook (Claude Code only): deliver one-time announcements.

Each announcement is injected into the session via `additionalContext` exactly
once. The hook touches the ack sentinel itself before injecting, so the message
shows once regardless of session outcome -- no AskUserQuestion round-trip needed.

Extensible: add entries to ANNOUNCEMENTS. Stdlib only (package boundary);
never raises.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# Ordered list of one-time announcements. Add new entries here; each shows once
# (per machine) until acknowledged. Keep messages ASCII (no-emojis-in-source).
ANNOUNCEMENTS: list[dict[str, str]] = [
    {
        "id": "model-switching-modes",
        "message": (
            "Pilot Shell -- Model Switching now has three modes: Automated (default), Manual, Off.\n\n"
            "What changed: the 9.12 window-scoped Fable/Opus pin machinery has been removed --\n"
            "it remapped model aliases across ALL sessions (a Fable planning session could pull\n"
            "your other sessions' Opus to Fable too). Pilot no longer touches those aliases, so\n"
            "/model always means what it says.\n\n"
            "The modes (Console -> Settings -> Model Switching):\n"
            "  - Automated (default): /spec runs on `opusplan` -- Opus plans, Sonnet executes,\n"
            "    switched automatically. Requires /model opusplan (Pilot sets it for you). Pilot\n"
            "    pre-flight-checks whether your context is too large for the Opus plan leg\n"
            "    (where Claude Code would otherwise silently keep planning on Sonnet).\n"
            "  - Manual: you pick models yourself with /model. /spec never pauses to switch --\n"
            "    it runs start to finish on your active model; interrupt and run /model to change.\n"
            "  - Off: no model management, no prompts -- everything runs on your active /model.\n\n"
            "Your existing setting migrated: Model Switching ON -> Automated, OFF -> Off.\n\n"
            "Docs: https://pilot-shell.com/docs/features/model-routing"
        ),
    },
    {
        "id": "opus-5",
        "message": (
            "Pilot Shell -- Claude Opus 5 is now the model `opusplan` plans with.\n\n"
            "What changed on Anthropic's side: the `opus` alias resolves to Opus 5, and under\n"
            "Automated Model Switching /spec now plans on Opus 5 and executes on Sonnet 5.\n"
            "Pilot still writes the bare `opusplan` alias -- nothing to change on your end.\n\n"
            "What changed in Pilot:\n"
            "  - Console usage now prices Opus 5 ($5/$25 per MTok, 2x on fast mode). Before\n"
            "    this release Opus 5 sessions were billed at $0 and flagged as an unknown\n"
            "    model, because the upstream pricing feed has no Opus 5 row yet.\n"
            "  - The statusline labels Opus 5 instead of showing the raw model id.\n"
            "  - `/benchmark --model opus` now runs on Opus 5.\n\n"
            "Unchanged, and worth knowing: the Opus plan leg still caps at 200K. Past that,\n"
            "Claude Code silently keeps planning on Sonnet -- the 1M entitlement does NOT\n"
            "exempt you (verified against Claude Code 2.1.219). Pilot's pre-flight warns you\n"
            "at /spec submit; /compact or /clear first, or switch Model Switching to Manual.\n\n"
            "Docs: https://pilot-shell.com/docs/features/model-routing"
        ),
    },
]


def _pilot_dir() -> Path:
    return Path.home() / ".pilot"


def _ack_path(announce_id: str, base: Path) -> Path:
    """Ack sentinel path: ``<base>/.announce-<id>-ack``."""
    return base / f".announce-{announce_id}-ack"


def pending(base: Path, announcements: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return announcements whose ack sentinel does not yet exist."""
    result: list[dict[str, str]] = []
    for a in announcements:
        try:
            if not _ack_path(a["id"], base).exists():
                result.append(a)
        except OSError:
            result.append(a)
    return result


def render_context(pending_list: list[dict[str, str]]) -> str:
    """Build the SessionStart additionalContext for the pending announcements.

    Empty string when nothing is pending.
    Ack sentinels are touched by the hook before this context is injected.
    """
    if not pending_list:
        return ""
    blocks: list[str] = [
        "[Pilot one-time announcement] Display the following announcement(s) to "
        "the user as clearly formatted text output. "
        "Do NOT use AskUserQuestion. "
        "Just show the announcement text, then continue with the user's request."
    ]
    for a in pending_list:
        blocks.append(f"\n--- Announcement ---\n{a['message']}")
    return "\n".join(blocks)


def main() -> None:
    # Claude Code only -- Codex has no SessionStart announcement channel here.
    if not os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return
    try:
        base = _pilot_dir()
        pending_list = pending(base, ANNOUNCEMENTS)
        ctx = render_context(pending_list)
        if not ctx:
            return
        # Touch ack sentinels now so each announcement shows exactly once.
        for a in pending_list:
            try:
                _ack_path(a["id"], base).touch()
            except OSError:
                pass
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": ctx,
                    }
                }
            )
        )
    except Exception:
        # SessionStart hook: never raise / never block the session.
        return


if __name__ == "__main__":
    main()
