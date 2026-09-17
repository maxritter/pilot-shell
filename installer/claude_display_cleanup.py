"""Retire Pilot's Claude display patch: restore the original binary, drop the state.

Pilot through 11.0.3 patched a native Claude binary so tool calls, thinking, and
subagent prompts rendered independently of Claude Code's own `verbose` setting,
and a SessionStart hook reapplied that patch whenever Claude replaced its binary.
Issue #191: the repair loop silently reverted a deliberate restore and the patch
had no opt-out. The feature is gone. This module is the migration that takes it
off machines that already carry it, so an update leaves a stock Claude behind.

Restore-only, and conservative about it: a binary is replaced only when its
current SHA-256 still matches the patch Pilot recorded AND the saved original
verifies against its own recorded hash. A Claude that has since updated itself,
or that the user replaced, is left exactly where it is — its stale record is just
dropped. The state directory is deleted only when nothing was left behind.

Restore logic vendored from the removed `installer/claude_display_patch.py`;
stdlib only, so it also runs from a bare `curl | sh` install.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STATE_DIR_NAME = "claude-display-patch"
MIGRATION_MARKER_NAME = ".pilot-display-patch-migration.json"


@dataclass(frozen=True)
class CleanupResult:
    status: str
    message: str


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(target: Path) -> tuple[int, int, int, int]:
    native = target.stat()
    return (native.st_dev, native.st_ino, native.st_mtime_ns, native.st_size)


def _load_state(state_dir: Path) -> dict[str, Any]:
    path = state_dir / "state.json"
    if not path.exists():
        return {"schema": 1, "entries": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != 1 or not isinstance(payload.get("entries"), dict):
        raise ValueError("Unrecognized Claude display patch state; preserving existing files")
    return payload


def _write_state(state_dir: Path, state: dict[str, Any]) -> None:
    descriptor, name = tempfile.mkstemp(prefix=".state-", dir=state_dir)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(state, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, state_dir / "state.json")
    finally:
        temporary.unlink(missing_ok=True)


def _matching_record(record: Any, binary_hash: str) -> dict[str, Any] | None:
    """Retain restore provenance if activation of a newer patch was interrupted."""
    while isinstance(record, dict):
        if record.get("patched_hash") == binary_hash:
            return record
        record = record.get("previous")
    return None


def _backup_path(state_dir: Path, record: dict[str, Any]) -> Path:
    original_hash = record.get("original_hash", "")
    if not isinstance(original_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", original_hash):
        raise ValueError("Invalid original binary hash in Claude display patch state")
    expected = f"originals/{original_hash}"
    if record.get("backup") != expected:
        raise ValueError("Invalid Claude display patch backup path")
    backup = state_dir / expected
    if _hash(backup) != original_hash:
        raise ValueError("Claude display patch original backup SHA-256 mismatch")
    return backup


def _restore_entries(state_dir: Path, state: dict[str, Any]) -> list[str]:
    """Put every still-patched binary back; return per-target failure messages."""
    failures: list[str] = []
    for target_name, stored_record in list(state["entries"].items()):
        try:
            target = Path(target_name)
            if not target.is_absolute() or not isinstance(stored_record, dict):
                raise ValueError("Invalid Claude display patch target record")
            record = (
                None if target.is_symlink() or not target.exists() else _matching_record(stored_record, _hash(target))
            )
            if record is None:
                del state["entries"][target_name]
                continue  # A user or Claude upgrade owns the changed target now.
            snapshot = _identity(target)
            backup = _backup_path(state_dir, record)
            with tempfile.TemporaryDirectory(prefix=".pilot-restore-", dir=target.parent) as work:
                candidate = Path(work) / "original"
                shutil.copyfile(backup, candidate)
                candidate.chmod(record["original_mode"])
                if _hash(candidate) != record["original_hash"]:
                    raise ValueError("Claude restore candidate SHA-256 mismatch")
                if _identity(target) != snapshot or _hash(target) != record["patched_hash"]:
                    del state["entries"][target_name]
                    continue  # A concurrent auto-update also supersedes our ownership.
                os.replace(candidate, target)
            del state["entries"][target_name]
        except (OSError, ValueError, KeyError, TypeError) as error:
            failures.append(f"{target_name}: {error}")
    return failures


def remove_display_patch(*, state_dir: Path | None = None, marker_path: Path | None = None) -> CleanupResult:
    """Restore Pilot-patched Claude binaries and delete the retired patch state.

    `marker_path` is the Claude profile's one-time view-mode migration marker;
    the caller resolves the profile, so omitting it just leaves the marker alone.

    Idempotent: with no state directory there is nothing to undo, which is the
    case on every fresh install. A failure keeps the directory — and therefore
    the verified original backups — so the next update can try again.
    """
    directory = state_dir if state_dir is not None else Path.home() / ".pilot" / STATE_DIR_NAME
    if not directory.is_dir() or directory.is_symlink():
        return CleanupResult("unchanged", "No Claude display patch to remove")
    try:
        with (directory / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state = _load_state(directory)
            failures = _restore_entries(directory, state)
            if failures:
                _write_state(directory, state)
                return CleanupResult(
                    "failed",
                    "Could not restore the original Claude binary; Pilot kept its backup in "
                    f"{directory}: {'; '.join(failures)}",
                )
        shutil.rmtree(directory)
    except BlockingIOError:
        return CleanupResult("busy", "Another process is still managing the Claude display patch")
    except (OSError, ValueError) as error:
        return CleanupResult("failed", f"Could not remove the Claude display patch: {error}")
    if marker_path is not None:
        try:
            marker_path.unlink(missing_ok=True)
        except OSError:
            pass  # Cosmetic leftover of the retired one-time view-mode migration.
    return CleanupResult("removed", "Removed Pilot's Claude display patch and restored the original binary")
