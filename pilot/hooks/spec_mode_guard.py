#!/usr/bin/env python3
"""Guard for /spec invocations (UserPromptSubmit hook).

- Always blocks /spec when the user is manually in plan mode (in Automated
  mode the skill, not the user, enters plan mode via EnterPlanMode).
- Warns when not in bypassPermissions mode.
- Model gate (three-way Model Switching mode, read FRESH from config.json):
    * automated: the session must run `opusplan`, whose non-plan leg is Sonnet,
      so at /spec-submit time a correct user shows Sonnet. A non-Sonnet model
      (e.g. plain Opus or plain Fable) means they are not on `opusplan` --
      blocked, UNLESS settings.json shows `opusplan` is the selected model AND
      the cache is not a Fable id (the async statusline cache may lag the
      `/model opusplan` the user just ran; a Fable cache value, never an
      opusplan resolution, is proof the session is live on Fable and stays
      blocked). A user wrongly on plain Sonnet is indistinguishable from
      opusplan and is allowed (accepted false-negative).
      Additionally, a pre-flight context check warns (non-blocking) when the
      conversation likely exceeds the Opus plan leg's effective window --
      Claude Code would then silently keep serving the Sonnet leg.
    * manual / off: NO model gate. Manual mode's /spec flow reminds the user
      to pick their planning model themselves; off means Pilot stays out of
      model management entirely.

Reads:
  - `permission_mode` from hook stdin (plan-mode block, bypassPermissions warn)
  - the Model Switching mode fresh from ~/.pilot/config.json ("manual" fallback)
  - `model_id` from the statusline cache at ``~/.pilot/sessions/<sid>/context-pct.json``
  - `model` from ``$CLAUDE_CONFIG_DIR/settings.json`` (the *selected* alias,
    persisted synchronously by `/model`) as the opusplan tie-breaker
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import read_model_switch_mode, resolve_session_id

_CLAUDE_OPUS_PREFIX_RE = re.compile(r"^claude-opus(-|$)")
_CLAUDE_SONNET_PREFIX_RE = re.compile(r"^claude-sonnet(-|$)")
_CLAUDE_FABLE_MYTHOS_PREFIX_RE = re.compile(r"^claude-(fable|mythos)(-|$)")


_TRAILING_1M_RE = re.compile(r"(?:\[1[mM]\])+$")


def _strip_1m(model: str) -> str:
    """Strip trailing ``[1m]``/``[1M]`` alias suffixes (including doubled ones).

    Real-world cache values can carry a doubled suffix (env var + model name
    concatenation) and statusline renders may uppercase it. Anchored at the end
    so mid-string occurrences are never touched.
    """
    return _TRAILING_1M_RE.sub("", model)


def _is_opus(model: str) -> bool:
    """Return True iff ``model`` resolves to an Opus alias or explicit Opus ID.

    Strips the ``[1m]`` alias suffix (explicit IDs may legitimately carry it,
    e.g. ``claude-opus-4-8[1m]``). Accepts the bare ``opus`` alias and any
    explicit ID matching ``claude-opus(-|$)`` so misspellings like
    ``claude-opusculus-1`` are rejected.
    """
    if not isinstance(model, str) or not model:
        return False
    base = _strip_1m(model)
    if base == "opus":
        return True
    return bool(_CLAUDE_OPUS_PREFIX_RE.match(base))


def _is_sonnet(model: str) -> bool:
    """Return True iff ``model`` resolves to a Sonnet alias or explicit Sonnet ID.

    Mirror of :func:`_is_opus`. Under Model Switching ON the session runs the
    ``opusplan`` model, whose non-plan leg is Sonnet -- so at ``/spec``-submit
    time (before plan mode) a correctly-configured user resolves to Sonnet.
    Accepts the bare ``sonnet`` alias and any explicit ID matching
    ``claude-sonnet(-|$)``; rejects lookalikes like ``claude-sonnetics-1``.
    """
    if not isinstance(model, str) or not model:
        return False
    base = _strip_1m(model)
    if base == "sonnet":
        return True
    return bool(_CLAUDE_SONNET_PREFIX_RE.match(base))


def _is_fable(model: str) -> bool:
    """Return True iff ``model`` is a Fable-family alias or explicit ID.

    Mirror of :func:`_is_opus`. Fable-class models (Fable 5, Mythos 5) have no
    plan/execute alias split, so under Automated they are blocked (opusplan is
    required); under Manual/Off there is no gate at all. Accepts the bare ``fable``,
    ``mythos``, and ``best`` aliases (``best`` resolves to Fable where
    available) and any explicit ID matching ``claude-(fable|mythos)(-|$)``
    (e.g. ``claude-fable-5``); rejects lookalikes like ``claude-fabletastic-1``.

    Accepted set is kept byte-identical to
    ``launcher/model_config.py::_is_fable_family`` (vendored mirror -- the
    package boundary forbids imports between hooks and launcher).
    """
    if not isinstance(model, str) or not model:
        return False
    base = _strip_1m(model)
    if base in ("fable", "mythos", "best"):
        return True
    return bool(_CLAUDE_FABLE_MYTHOS_PREFIX_RE.match(base))


def _is_opusplan(model: str) -> bool:
    """Return True iff ``model`` is the opusplan alias.

    Mirror of :func:`_is_opus`. Matches the bare ``opusplan`` alias after
    stripping the ``[1m]`` suffix, so a legacy ``opusplan[1m]`` value an older
    Pilot wrote to settings.json still counts.
    """
    if not isinstance(model, str) or not model:
        return False
    return _strip_1m(model) == "opusplan"


def _managed_opusplan_pin_present() -> bool:
    """True when settings.json env carries a Pilot-managed ANTHROPIC_MODEL pin.

    In Automated mode the env pin outranks the ``model`` field on the next
    session start, so a Fable-family ``model`` value alongside the managed pin
    still boots as opusplan -- the pin, not the field, is decisive there.
    """
    claude_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
    try:
        data = json.loads((claude_dir / "settings.json").read_text())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return False
    env = data.get("env") if isinstance(data, dict) else None
    pin = env.get("ANTHROPIC_MODEL") if isinstance(env, dict) else None
    return _is_opusplan(pin) if isinstance(pin, str) else False


def _read_selected_model_from_settings() -> str | None:
    """Read the *selected* model alias from Claude Code's settings.json, or None.

    `/model <choice>` persists the selection here synchronously ("saved as your
    default for new sessions"). Unlike the statusline cache -- async, and only
    ever holding the *resolved* model id -- this is where the ``opusplan``
    alias itself is observable. The value is global across sessions while the
    cache is per-session, so it is only consulted as a tie-breaker when the
    cache would block, never to override a cache that already passes the gate.
    """
    claude_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
    try:
        data = json.loads((claude_dir / "settings.json").read_text())
    except (OSError, json.JSONDecodeError):
        return None
    model = data.get("model") if isinstance(data, dict) else None
    return model if isinstance(model, str) and model else None


def _read_active_model_from_cache() -> str | None:
    """Read ``model_id`` from the statusline cache file, or None if unavailable.

    Falls through cleanly when no statusline render has run yet (e.g. the very
    first prompt after a session starts) — the caller treats None as "skip the
    Opus check" rather than as a block trigger.
    """
    cache_file = Path.home() / ".pilot" / "sessions" / resolve_session_id() / "context-pct.json"
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
    `/spec-bugfix-verify`, which run on Sonnet under automated model switching
    (the opusplan default leg). Restrict to bare `/spec` or `/spec ` (with
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
    gate -- the resume path runs on whichever model is active (Sonnet under
    automated model switching) for implementation/verification.

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


# The opusplan plan leg's effective context window: 200K. CC 2.1.172 nominally
# lifted it to 1M for entitled accounts, but current versions regressed to the
# hard >200K guard even WITH the entitlement (anthropics/claude-code#65512
# comments show it on 2.1.216; #74325 tracks the silent fallback) -- and
# accounts without the entitlement or with exhausted usage credits were always
# capped. The pre-flight warns at 90% of it -- the statusline `pct` is rounded
# and render-lagged, so the 10% margin prevents false negatives right at the
# boundary (documented plan decision).
OPUS_PLAN_CONTEXT_FLOOR = int(200_000 * 0.9)


def _opus_context_preflight() -> str | None:
    """Warn when the conversation likely exceeds the Opus plan leg's window.

    Automated mode only. opusplan can only switch the planning leg to Opus if
    the conversation fits Opus's effective window; past it, Claude Code
    silently keeps serving the Sonnet leg (verified against CC 2.1.209/2.1.211
    -- print mode errors "Prompt is too long", interactive stays on Sonnet).
    This currently hits 1M-entitled accounts too: the CC 2.1.172 entitled-1M
    fix regressed upstream (anthropics/claude-code#65512, #74325), so the
    warning must never imply the entitlement exempts anyone.
    Estimates current tokens from the statusline cache; falls open silently
    when the cache is missing or invalid.
    """
    session_dir = Path.home() / ".pilot" / "sessions" / resolve_session_id()
    marker = session_dir / "preflight-context-warned"
    if marker.exists():
        return None  # once per session -- don't re-nag every /spec submit
    cache_file = session_dir / "context-pct.json"
    try:
        data = json.loads(cache_file.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    pct = data.get("pct")
    window = data.get("context_window_size")
    if not isinstance(pct, (int, float)) or not isinstance(window, int) or window <= 0:
        return None
    est_tokens = int(pct / 100 * window)
    if est_tokens <= OPUS_PLAN_CONTEXT_FLOOR:
        return None
    try:
        marker.write_text("")
    except OSError:
        pass
    return (
        f"[Pilot] PRE-FLIGHT CONTEXT CHECK: this conversation is at ~{est_tokens // 1000}K tokens, "
        "which likely exceeds the Opus plan leg's effective 200K window. The cap currently "
        "applies even with the Opus 1M entitlement -- current Claude Code versions fail to "
        "switch the opusplan plan leg to Opus past 200K (known upstream regression, "
        "anthropics/claude-code#65512); accounts without the entitlement or with exhausted "
        "usage credits were always capped. If so, Claude Code will SILENTLY keep planning on "
        "Sonnet after EnterPlanMode. Tell the user in one short paragraph BEFORE starting the "
        "/spec workflow: planning may stay on Sonnet at this context size -- to plan on Opus, "
        "run /compact or /clear first, or switch Model Switching to Manual (Console -> "
        "Settings) and pick the planning model yourself. Then continue with the workflow on "
        "their call."
    )


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

    # The model gate targets the *planning* leg of /spec. Resuming an existing
    # plan (`/spec <path/to/plan.md>`) dispatches to spec-implement / spec-verify,
    # which run on whichever model is active (Sonnet under automated switching).
    # Skipping the gate for resume keeps it reachable on Sonnet.
    if _is_resume_existing_plan(prompt):
        return 0

    # Model gate -- Automated mode only (mode read FRESH from config.json; env
    # is startup-frozen and a Console change must reach running sessions).
    #
    #   * automated: the session runs the `opusplan` model, whose non-plan leg
    #     is Sonnet. At /spec-submit time the skill has NOT yet entered plan
    #     mode, so a correctly-configured user resolves to *Sonnet*. Anything
    #     else (plain Opus, plain Fable) means they never ran `/model opusplan`
    #     -- block and tell them to fix it. A user wrongly on plain Sonnet is
    #     indistinguishable from opusplan and is allowed (accepted
    #     false-negative, avoids false-blocking every correct user).
    #   * manual / off: NO model gate -- the user drives /model themselves.
    mode = read_model_switch_mode()
    context_notes: list[str] = []

    if mode == "automated":
        active_model = _read_active_model_from_cache()
        cache_warn = (
            "\033[0;33m[Pilot] Warning: could not verify active model for /spec "
            "(statusline cache unavailable). Proceeding without the model check -- "
            "if you are not on the opusplan model, run '/model opusplan' before planning.\033[0m\n"
        )
        block_reason = (
            "[Pilot] /spec with Automated Model Switching requires the 'opusplan' model. "
            "Run '/model opusplan' and try again, or switch Model Switching to Manual or Off "
            "(Pilot Console -> Settings) to run /spec on whatever model you pick. "
            "(Resuming an existing plan with '/spec <path/to/plan.md>' is allowed on any model.)"
        )
        block_stderr = (
            "\033[0;31m[Pilot] /spec blocked: Automated Model Switching needs 'opusplan' "
            "(shows as Sonnet before planning) -- plain Fable/Opus won't switch. "
            "Current model: "
            + (active_model or "unknown")
            + ". Run '/model opusplan', or pick Manual/Off in the Console.\033[0m\n"
        )

        model_ok = active_model is not None and _is_sonnet(active_model)

        # The cache can never show 'opusplan' -- only its resolved leg -- so when
        # it would block, consult the alias the user actually SELECTED
        # (settings.json, written synchronously by /model) before issuing model
        # guidance. Read lazily: a passing cache never touches settings.
        if not model_ok:
            selected_model = _read_selected_model_from_settings()
            opusplan_selected = selected_model is not None and _is_opusplan(selected_model)
            if opusplan_selected:
                # A Fable cache value is NEVER an opusplan resolution (opusplan
                # resolves only to Opus or Sonnet), so it is proof the session is
                # live on Fable despite the selection -- block so the switch
                # actually engages. Any other cache value is either correct or a
                # transient post-`/model opusplan` lag -- allow.
                if active_model is not None and _is_fable(active_model):
                    print(json.dumps({"decision": "block", "reason": block_reason}))
                    sys.stderr.write(block_stderr)
                    return 2
            elif active_model is None:
                # Cache may not have been written yet (very first prompt of a
                # fresh session). A Fable-family SELECTION blocks even without a
                # cache (a fresh Fable session must not enter plan mode under
                # Automated) -- UNLESS the managed ANTHROPIC_MODEL env pin is
                # present: the pin outranks the model field on session start,
                # so the session actually boots on opusplan despite the Fable
                # field (the injector deliberately preserves both in Automated).
                if selected_model is not None and _is_fable(selected_model) and not _managed_opusplan_pin_present():
                    print(json.dumps({"decision": "block", "reason": block_reason}))
                    sys.stderr.write(block_stderr)
                    return 2
                sys.stderr.write(cache_warn)
            else:
                print(json.dumps({"decision": "block", "reason": block_reason}))
                sys.stderr.write(block_stderr)
                return 2

        preflight = _opus_context_preflight()
        if preflight:
            context_notes.append(preflight)

    if permission_mode and permission_mode != "bypassPermissions":
        sys.stderr.write(
            f"\033[0;33m[Pilot] Warning: /spec works best in 'Bypass Permissions' mode "
            f"(current: {permission_mode}). Press Shift+Tab to switch.\033[0m\n"
        )
        context_notes.append(
            f"NOTE: Current permission mode is '{permission_mode}'. "
            "For uninterrupted /spec execution, 'bypassPermissions' mode is recommended "
            "(Shift+Tab to cycle). In the current mode the workflow may pause for "
            "permission prompts. Briefly warn the user, then proceed with the workflow."
        )

    if context_notes:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": "\n\n".join(context_notes),
                    }
                }
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(run_spec_mode_guard())
