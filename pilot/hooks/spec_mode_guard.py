#!/usr/bin/env python3
"""Guard: blocks /spec when in plan mode or on a non-Opus model, warns when not in
bypassPermissions mode.

Reads:
  - `permission_mode` from hook stdin (Plan mode block, bypassPermissions warn)
  - `model_id` from the statusline cache at ``~/.pilot/sessions/<sid>/context-pct.json``
    (Opus-only block) — the statusline writes this every render and Claude Code
    UserPromptSubmit stdin does NOT include the active model field.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

_CLAUDE_OPUS_PREFIX_RE = re.compile(r"^claude-opus(-|$)")


def _is_opus(model: str) -> bool:
    """Return True iff ``model`` resolves to an Opus alias or explicit Opus ID.

    Strips the ``[1m]`` alias suffix (explicit IDs may legitimately carry it,
    e.g. ``claude-opus-4-7[1m]``). Accepts the bare ``opus`` alias and any
    explicit ID matching ``claude-opus(-|$)`` so misspellings like
    ``claude-opusculus-1`` are rejected.
    """
    if not isinstance(model, str) or not model:
        return False
    base = model[:-4] if model.endswith("[1m]") else model
    if base == "opus":
        return True
    return bool(_CLAUDE_OPUS_PREFIX_RE.match(base))


def _read_active_model_from_cache() -> str | None:
    """Read ``model_id`` from the statusline cache file, or None if unavailable.

    Falls through cleanly when no statusline render has run yet (e.g. the very
    first prompt after a session starts) — the caller treats None as "skip the
    Opus check" rather than as a block trigger.
    """
    session_id = os.environ.get("PILOT_SESSION_ID", "").strip()
    if not session_id:
        return None
    cache_file = Path.home() / ".pilot" / "sessions" / session_id / "context-pct.json"
    if not cache_file.exists():
        return None
    try:
        data = json.loads(cache_file.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    model_id = data.get("model_id") if isinstance(data, dict) else None
    return model_id if isinstance(model_id, str) and model_id else None


def _is_spec_invocation(prompt: str) -> bool:
    """Return True iff ``prompt`` is a /spec slash command (not /spec-implement etc.).

    `prompt.startswith("/spec")` overmatches sibling commands such as
    `/spec-implement`, `/spec-verify`, `/spec-plan`, `/spec-bugfix-plan`,
    `/spec-bugfix-verify`, which are intentional Sonnet entry points after
    the model-switch handoff. Restrict to bare `/spec` or `/spec ` (with
    whitespace before any args).
    """
    if not prompt.startswith("/spec"):
        return False
    after = prompt[len("/spec") :]
    return after == "" or after[:1].isspace()


def _is_resume_existing_plan(prompt: str) -> bool:
    """Return True when /spec is resuming an existing plan, not starting a new one.

    The dispatcher routes `/spec <path/to/plan.md>` to existing-plan handling
    (status-based dispatch). Such invocations must NOT be blocked by the Opus
    gate — the resume path runs after the model-switch handoff when the user
    has deliberately switched to Sonnet for implementation/verification.

    A "resume" prompt is `/spec` followed by a token ending in `.md` (case
    insensitive). Paths containing spaces are honored when quoted, via shlex.
    A "new plan" prompt is `/spec <free-form task description>` and stays
    subject to the Opus block.
    """
    # Strip the leading "/spec" and any whitespace.
    body = prompt[len("/spec") :].strip()
    if not body:
        return False
    try:
        tokens = shlex.split(body, posix=True)
    except ValueError:
        # Unbalanced quotes — fall back to a permissive whitespace split.
        tokens = body.split(maxsplit=1)
    if not tokens:
        return False
    # First arg only — trailing flags don't change the verdict.
    return tokens[0].lower().endswith(".md")


def run_spec_mode_guard() -> int:
    """Check permission mode and active model before allowing /spec invocation."""
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    prompt = hook_data.get("prompt", "").strip()
    permission_mode = hook_data.get("permission_mode", "")

    if not _is_spec_invocation(prompt):
        return 0

    if permission_mode == "plan":
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        "[Pilot] /spec cannot run in Plan mode. "
                        "Press Shift+Tab to cycle to 'Bypass Permissions' mode, then try again."
                    ),
                }
            )
        )
        sys.stderr.write("\033[0;31m[Pilot] /spec blocked: Plan mode is incompatible with /spec workflow\033[0m\n")
        return 2

    # Opus is required only for the *planning* leg of /spec. Resuming an
    # existing plan (`/spec <path/to/plan.md>`) dispatches to spec-implement /
    # spec-verify — those phases run on whichever model the user chose during
    # the model-switch handoff. Skipping the gate for resume is the difference
    # between modelSwitch=true working and being unreachable on Sonnet.
    if _is_resume_existing_plan(prompt):
        return 0

    active_model = _read_active_model_from_cache()
    if active_model is None:
        # Cache may not have been written yet (very first prompt of a fresh
        # session, or a transient render that omitted model_id). Fall open
        # but warn so the user knows the Opus check did not run.
        sys.stderr.write(
            "\033[0;33m[Pilot] Warning: could not verify active model for /spec "
            "(statusline cache unavailable). Proceeding without the Opus check — "
            "if you are on Sonnet, run '/clear' then '/model opus[1m]' before planning.\033[0m\n"
        )
    elif not _is_opus(active_model):
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        "[Pilot] /spec requires Opus for planning. Run '/model opus[1m]' "
                        "(or '/model opus') and try again. "
                        "(Resuming an existing plan with '/spec <path/to/plan.md>' is allowed on any model.)"
                    ),
                }
            )
        )
        sys.stderr.write(
            "\033[0;31m[Pilot] /spec blocked: planning requires Opus. "
            "Current model: " + active_model + ". Run '/model opus[1m]' (or '/model opus').\033[0m\n"
        )
        return 2

    if permission_mode and permission_mode != "bypassPermissions":
        sys.stderr.write(
            f"\033[0;33m[Pilot] Warning: /spec works best in 'Bypass Permissions' mode "
            f"(current: {permission_mode}). Press Shift+Tab to switch.\033[0m\n"
        )
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": (
                            f"NOTE: Current permission mode is '{permission_mode}'. "
                            "For uninterrupted /spec execution, 'bypassPermissions' mode is recommended "
                            "(Shift+Tab to cycle). In the current mode the workflow may pause for "
                            "permission prompts. Briefly warn the user, then proceed with the workflow."
                        ),
                    }
                }
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(run_spec_mode_guard())
