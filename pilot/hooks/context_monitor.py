#!/usr/bin/env python3
"""Context monitor - warns when context usage is high."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import (
    _get_max_context_tokens,
    get_session_cache_path,
    post_tool_use_context,
    resolve_session_id,
)

try:
    from plan_mode_tracker import planning_leg_model_context
except ImportError:  # version-skewed hooks dir: context monitoring still works

    def planning_leg_model_context() -> str | None:
        return None


THRESHOLD_AUTOCOMPACT = 90
_CODEX_TRANSCRIPT_TAIL_BYTES = 4_000_000


def _get_pilot_session_id() -> str:
    """Get the resolved session ID (agent-native fallback chain)."""
    return resolve_session_id()


def get_session_flags(session_id: str) -> bool:
    """Get shown_80_warn flag for this session."""
    if get_session_cache_path().exists():
        try:
            with get_session_cache_path().open() as f:
                cache = json.load(f)
                if cache.get("session_id") == session_id:
                    return cache.get("shown_80_warn", False)
        except (json.JSONDecodeError, OSError):
            pass
    return False


def get_autocompact_flag(session_id: str) -> bool:
    """Get shown_autocompact_warn flag for this session."""
    if get_session_cache_path().exists():
        try:
            with get_session_cache_path().open() as f:
                cache = json.load(f)
                if cache.get("session_id") == session_id:
                    return cache.get("shown_autocompact_warn", False)
        except (json.JSONDecodeError, OSError):
            pass
    return False


def save_cache(
    tokens: int,
    session_id: str,
    shown_80_warn: bool | None = None,
    shown_autocompact_warn: bool | None = None,
    reset_warnings: bool = False,
) -> None:
    """Save context calculation to cache with session ID."""
    existing_80_warn = False
    existing_autocompact_warn = False
    if get_session_cache_path().exists():
        try:
            with get_session_cache_path().open() as f:
                cache = json.load(f)
                if cache.get("session_id") == session_id:
                    existing_80_warn = cache.get("shown_80_warn", False)
                    existing_autocompact_warn = cache.get("shown_autocompact_warn", False)
        except (json.JSONDecodeError, OSError):
            pass

    if reset_warnings:
        existing_80_warn = False
        existing_autocompact_warn = False
    if shown_80_warn:
        existing_80_warn = True
    if shown_autocompact_warn:
        existing_autocompact_warn = True

    try:
        with get_session_cache_path().open("w") as f:
            json.dump(
                {
                    "tokens": tokens,
                    "timestamp": time.time(),
                    "session_id": session_id,
                    "shown_80_warn": existing_80_warn,
                    "shown_autocompact_warn": existing_autocompact_warn,
                },
                f,
            )
    except OSError:
        pass


def _read_statusline_context_pct() -> float | None:
    """Read authoritative context percentage from statusline cache.

    Returns None if cache is missing, corrupt, or stale (>60s).
    Cache is already scoped per Pilot session via PILOT_SESSION_ID.
    """
    cache_file = Path.home() / ".pilot" / "sessions" / resolve_session_id() / "context-pct.json"
    if not cache_file.exists():
        return None
    try:
        data = json.loads(cache_file.read_text())
        ts = data.get("ts")
        if ts is None or time.time() - ts > 60:
            return None
        pct = data.get("pct")
        return float(pct) if pct is not None else None
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return None


def _is_throttled(session_id: str) -> bool:
    """Check if context monitoring should be throttled (skipped).

    Returns True if the last check was recent and below the auto-compact
    warning threshold.

    Always returns False at high context (never throttle when approaching compaction).

    Orchestrator-aware: when a /spec orchestrator with a smaller window than main
    is active, the percentage is computed against the orchestrator's window so the
    throttle releases earlier — preventing silent skip when the orchestrator is
    already past its real compact point even though the main-frame pct looks low.
    """
    cache_path = get_session_cache_path()
    if not cache_path.exists():
        return False

    try:
        with cache_path.open() as f:
            cache = json.load(f)
            if cache.get("session_id") != session_id:
                return False

            timestamp = cache.get("timestamp")
            if timestamp is None:
                return False

            if time.time() - timestamp < 30:
                tokens = cache.get("tokens", 0)
                active_window = _get_max_context_tokens()
                percentage = (tokens / active_window) * 100
                if percentage < THRESHOLD_AUTOCOMPACT:
                    return True

            return False
    except (json.JSONDecodeError, OSError, KeyError):
        return False


def _read_recent_transcript_lines(transcript_path: str) -> list[str] | None:
    """Read recent JSONL lines from a Codex transcript without loading the whole file."""
    if not transcript_path:
        return None
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            start = max(0, file_size - _CODEX_TRANSCRIPT_TAIL_BYTES)
            f.seek(start)
            data = f.read()
    except OSError:
        return None

    if start > 0:
        _, _, data = data.partition(b"\n")
    return data.decode("utf-8", errors="replace").splitlines()


def _read_codex_token_count_context(transcript_path: str) -> tuple[float, int] | None:
    """Read Codex's latest token-count event as (pct, tokens).

    Codex transcripts include cumulative usage and the per-call
    ``last_token_usage``. Context pressure is the latest model-call input, not
    cumulative session spend and not the transcript file size.
    """
    lines = _read_recent_transcript_lines(transcript_path)
    if not lines:
        return None

    for line in reversed(lines):
        if '"token_count"' not in line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        payload = entry.get("payload")
        if not isinstance(payload, dict) or payload.get("type") != "token_count":
            continue

        info = payload.get("info")
        if not isinstance(info, dict):
            continue

        window = info.get("model_context_window")
        last_usage = info.get("last_token_usage")
        if not isinstance(window, (int, float)) or window <= 0 or not isinstance(last_usage, dict):
            continue

        input_tokens = last_usage.get("input_tokens")
        output_tokens = last_usage.get("output_tokens", 0)
        if not isinstance(input_tokens, (int, float)):
            continue
        if not isinstance(output_tokens, (int, float)):
            output_tokens = 0

        tokens = int(input_tokens + output_tokens)
        pct = min(tokens / int(window) * 100, 100)
        return pct, tokens

    return None


def _resolve_context(
    session_id: str,
    transcript_path: str | None = None,
    model: str | None = None,
) -> tuple[float, int, bool] | None:
    """Resolve context percentage and tokens. Returns (pct, tokens, shown_80) or None.

    Tries Claude Code's statusline cache first, then falls back to Codex's
    own token-count transcript events when transcript_path is provided.
    """
    statusline_pct = _read_statusline_context_pct()
    if statusline_pct is not None:
        main_window = _get_max_context_tokens()
        shown_80_warn = get_session_flags(session_id)
        return statusline_pct, int(statusline_pct / 100 * main_window), shown_80_warn

    if transcript_path:
        codex_context = _read_codex_token_count_context(transcript_path)
        if codex_context is not None:
            codex_pct, tokens = codex_context
            shown_80_warn = get_session_flags(session_id)
            return codex_pct, tokens, shown_80_warn

    return None


def _emit(notices: list[str]) -> int:
    """Emit the collected notices as ONE additionalContext payload.

    Two `print` calls would concatenate into invalid JSON and the whole hook
    payload would be discarded, so every notice funnels through here.
    """
    if notices:
        print(post_tool_use_context("\n\n".join(notices)))
    return 0


def _planning_leg_notice() -> str | None:
    """Warn when the /spec planning leg is observably not running on Opus.

    This hook is the per-turn anchor for that check: it is registered on the
    PostToolUse `*` matcher, so it costs no extra process and it sees every
    exploration tool call during which the conversation crosses 200K and Claude
    Code silently drops the opusplan plan leg back to Sonnet. The `*` is
    load-bearing, not incidental - a named tool list omits MCP tools, which is
    what Pilot's own rules steer planning toward (see
    tests/test_context_monitor.py::TestPlanningLegHookRegistration). Runs before
    the throttle below - the downgrade is unrelated to how recently context was
    sampled, and at planning-time context levels the throttle is almost always on.
    """
    try:
        return planning_leg_model_context()
    except OSError:
        return None


def run_context_monitor() -> int:
    """Run context monitoring. Always returns 0. Uses additionalContext JSON for all messages."""
    hook_data: dict = {}
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        pass

    session_id = _get_pilot_session_id()

    notices: list[str] = []
    planning_leg = _planning_leg_notice()
    if planning_leg:
        notices.append(planning_leg)

    if _is_throttled(session_id):
        return _emit(notices)

    transcript_path = hook_data.get("transcript_path")
    model = hook_data.get("model", "")

    resolved = _resolve_context(session_id, transcript_path=transcript_path, model=model)
    if resolved is None:
        return _emit(notices)

    percentage, total_tokens, _shown_80_warn = resolved
    display_pct = min(max(percentage, 0), 100)
    shown_autocompact_warn = get_autocompact_flag(session_id)

    if percentage < THRESHOLD_AUTOCOMPACT:
        save_cache(total_tokens, session_id, reset_warnings=True)
        return _emit(notices)

    save_cache(total_tokens, session_id, shown_autocompact_warn=True)
    if not shown_autocompact_warn:
        notices.append(
            f"Context at {display_pct:.0f}%. Auto-compact approaching — no context is lost. "
            f"Continue all workflow steps normally. Do NOT skip steps, sub-agents, or verification."
        )
    return _emit(notices)


if __name__ == "__main__":
    sys.exit(run_context_monitor())
