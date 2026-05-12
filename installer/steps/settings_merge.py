"""Settings merge utilities for non-destructive installer updates.

Provides three-way merge logic for settings files (~/.claude/settings.json,
~/.claude.json) and manifest-based tracking for Pilot-managed files
in shared directories (commands/, rules/).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


def merge_settings(
    baseline: dict[str, Any] | None,
    current: dict[str, Any],
    incoming: dict[str, Any],
) -> dict[str, Any]:
    """Three-way merge of settings: baseline (last Pilot install), current (on disk), incoming (new Pilot).

    Rules:
    - If no baseline exists (first install), incoming wins for all keys.
    - For dict fields (env, permissions, attribution, statusLine): merge keys individually.
      If user changed a key from baseline value, keep user's value. Otherwise update to incoming.
    - For scalar fields: if user changed from baseline, keep user's value. Otherwise update.
    """
    result: dict[str, Any] = {}
    all_keys = set(incoming.keys()) | set(current.keys())

    for key in all_keys:
        in_incoming = key in incoming
        in_current = key in current
        in_baseline = baseline is not None and key in baseline

        if not in_incoming:
            if baseline is not None and in_baseline and current[key] == baseline[key]:
                pass
            else:
                result[key] = current[key]
        elif not in_current:
            result[key] = incoming[key]
        elif isinstance(incoming[key], dict) and isinstance(current[key], dict):
            result[key] = _merge_dict_field(
                baseline.get(key, {}) if baseline is not None and in_baseline else None,
                current[key],
                incoming[key],
            )
        else:
            if baseline is None or not in_baseline:
                result[key] = incoming[key]
            elif current[key] == baseline[key]:
                result[key] = incoming[key]
            else:
                result[key] = current[key]

    return result


def _merge_dict_field(
    baseline: dict[str, Any] | None,
    current: dict[str, Any],
    incoming: dict[str, Any],
) -> dict[str, Any]:
    """Merge a dict field (env, attribution, etc.) key by key.

    - New incoming keys are added.
    - User-only keys (not in incoming) are preserved.
    - If user changed a value from baseline, keep user's value.
    - Otherwise update to incoming value.
    """
    result: dict[str, Any] = {}
    all_keys = set(incoming.keys()) | set(current.keys())

    for key in all_keys:
        if key not in incoming:
            result[key] = current[key]
        elif key not in current:
            result[key] = incoming[key]
        elif baseline is None or key not in baseline:
            result[key] = incoming[key]
        elif current[key] == baseline[key]:
            result[key] = incoming[key]
        else:
            result[key] = current[key]

    return result


def _hook_entry_signature(entry: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    """Stable identity for a hooks-array entry: (matcher, sorted-commands).

    Matches the Claude Code hook config schema:
        {"matcher": "...", "hooks": [{"type": "command", "command": "..."}, ...]}
    """
    matcher = entry.get("matcher") or ""
    if not isinstance(matcher, str):
        matcher = str(matcher)
    cmds: list[str] = []
    for h in entry.get("hooks", []) or []:
        if isinstance(h, dict):
            cmd = h.get("command")
            if isinstance(cmd, str):
                cmds.append(cmd)
    return (matcher, tuple(sorted(cmds)))


def merge_pilot_hooks(
    current_hooks: dict[str, Any],
    incoming_hooks: dict[str, Any],
    baseline_hooks: dict[str, Any] | None,
) -> dict[str, Any]:
    """Merge Pilot's hooks dict into the user's hooks dict, identity-aware.

    Each event key (SessionStart, PostToolUse, ...) maps to a list of entries.
    Pilot-owned entries are identified by their signature (matcher + sorted
    command set) appearing in baseline. Entries in `current` whose signature
    is NOT in baseline are treated as user additions and preserved.

    Strategy per event key:
      - Only in current → preserve.
      - Only in incoming → install.
      - In both → user_only (current sigs NOT in baseline) ++ incoming entries.
      - Event in baseline but neither in incoming nor (modified by) user → drop.

    Validates signature uniqueness within each event key of `incoming` to lock
    in the invariant that pilot/hooks/hooks.json never ships two entries with
    the same matcher+command set. Uses `raise ValueError` (NOT `assert`) so the
    check survives `python -O`.

    Raises:
        ValueError: when two incoming entries under the same event share a signature.
    """
    # Defensive: validate incoming uniqueness once.
    for event_key, entries in incoming_hooks.items():
        seen: set[tuple[str, tuple[str, ...]]] = set()
        for entry in entries or []:
            sig = _hook_entry_signature(entry)
            if sig in seen:
                raise ValueError(f"Duplicate hook signature in event {event_key!r}: {sig!r}")
            seen.add(sig)

    baseline = baseline_hooks or {}
    result: dict[str, Any] = {}
    all_event_keys = set(current_hooks.keys()) | set(incoming_hooks.keys())

    for event_key in all_event_keys:
        in_current = event_key in current_hooks
        in_incoming = event_key in incoming_hooks

        if in_current and not in_incoming:
            current_entries = current_hooks[event_key] or []
            baseline_sigs = {_hook_entry_signature(e) for e in (baseline.get(event_key) or [])}
            user_only = [e for e in current_entries if _hook_entry_signature(e) not in baseline_sigs]
            if user_only:
                result[event_key] = user_only
            continue

        if not in_current and in_incoming:
            result[event_key] = list(incoming_hooks[event_key] or [])
            continue

        current_entries = current_hooks[event_key] or []
        incoming_entries = list(incoming_hooks[event_key] or [])
        baseline_sigs = {_hook_entry_signature(e) for e in (baseline.get(event_key) or [])}
        user_only = [e for e in current_entries if _hook_entry_signature(e) not in baseline_sigs]
        seen = {_hook_entry_signature(e) for e in user_only}
        merged = list(user_only)
        for entry in incoming_entries:
            sig = _hook_entry_signature(entry)
            if sig in seen:
                continue
            seen.add(sig)
            merged.append(entry)
        result[event_key] = merged

    return result


def merge_pilot_mcp_servers(
    current_servers: dict[str, Any],
    incoming_servers: dict[str, Any],
    baseline_servers: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str]]:
    """Value-aware merge of Pilot's mcpServers into the user's mcpServers.

    Strategy (preserves user-added AND user-modified entries):
      1. baseline_keys = keys in baseline_servers (Pilot has previously managed these).
      2. Copy every current entry whose key is NOT in baseline_keys (user-only).
      3. For each (key, value) in baseline where current[key] != value (user modified
         a Pilot server), preserve the user's value and emit a warning.
      4. For each (key, value) in incoming:
         - already in result (covered by 2 or 3) → skip.
         - else if key in current AND current[key] != value AND key NOT in baseline
           (name collision with non-Pilot user entry) → preserve user, warn.
         - else → install Pilot's value.

    Returns:
        (merged_servers, warnings) — warnings is a list of human-readable strings
        the installer surfaces to the UI.
    """
    baseline = baseline_servers or {}
    result: dict[str, Any] = {}
    warnings: list[str] = []

    # Step 2 — non-Pilot user entries (key not in baseline). If incoming also
    # has the key with a different value, that's a name collision — warn so
    # the user knows Pilot did NOT install its version.
    for key, value in current_servers.items():
        if key not in baseline:
            result[key] = value
            if key in incoming_servers and incoming_servers[key] != value:
                warnings.append(
                    f"MCP server '{key}' was already configured by the user; "
                    "Pilot's version was NOT installed. Existing value preserved."
                )

    # Step 3 — Pilot-named entries the user modified vs. baseline.
    for key, baseline_value in baseline.items():
        if key in current_servers and current_servers[key] != baseline_value:
            result[key] = current_servers[key]
            warnings.append(
                f"MCP server '{key}' was modified by the user; "
                "Pilot's update was NOT applied. Existing value preserved."
            )

    # Step 4 — install Pilot's incoming servers. Collisions with non-baseline
    # user entries are already handled in Step 2.
    for key, value in incoming_servers.items():
        if key in result:
            continue
        result[key] = value

    return result, warnings


def merge_app_config(
    target: dict[str, Any],
    source: dict[str, Any],
    baseline: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Merge app-level preferences from source into target (~/.claude.json).

    With baseline (three-way merge): only updates keys the user hasn't manually changed.
    Without baseline (first install): sets all source keys into target.
    Returns patched dict if changes were made, None if no changes needed.
    """
    modified = False
    for key, value in source.items():
        if key in target and baseline is not None and key in baseline:
            if target[key] != baseline[key]:
                continue
        if key not in target or target[key] != value:
            target[key] = value
            modified = True
    return target if modified else None


def load_manifest(manifest_path: Path) -> set[str]:
    """Load the set of Pilot-managed filenames from manifest."""
    if not manifest_path.exists():
        return set()
    try:
        data = json.loads(manifest_path.read_text())
        return set(data.get("files", []))
    except (json.JSONDecodeError, OSError, IOError):
        return set()


def save_manifest(manifest_path: Path, files: set[str]) -> None:
    """Save the set of Pilot-managed filenames to manifest."""
    try:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps({"files": sorted(files)}, indent=2) + "\n")
    except (OSError, IOError):
        pass


def cleanup_managed_files(directory: Path, manifest_path: Path, prefix: str) -> None:
    """Remove only Pilot-managed files from a directory, preserving user files.

    Reads the manifest to know which files Pilot previously installed,
    removes those files (cleaning up stale ones from previous versions),
    and leaves all other files untouched.

    Args:
        directory: The directory to clean (e.g. ~/.claude/commands/)
        manifest_path: Path to .pilot-manifest.json
        prefix: Manifest entry prefix to filter (e.g. "commands/" or "rules/")
    """
    managed = load_manifest(manifest_path)
    if not managed or not directory.exists():
        return

    for entry in managed:
        if not entry.startswith(prefix):
            continue
        relative = entry[len(prefix) :]
        file_path = directory / relative
        if file_path.exists():
            try:
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
            except (OSError, IOError):
                pass
