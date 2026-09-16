"""Patch an existing native Claude safely; also ships as the standalone restorer."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

SOURCE_ENTRY_ID = "claude-display-patch"
DISABLED_PATCHES = "welcome-badge,installer-label,disable-spinner-tips"
_SUPPORTED = {("Darwin", "arm64"), ("Linux", "x86_64"), ("Linux", "aarch64")}


@dataclass(frozen=True)
class PatchResult:
    status: str
    message: str


@dataclass(frozen=True)
class PatchSource:
    commit: str
    source_url: str
    sha256: str


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(argv: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.run(argv, cwd=cwd, check=True, capture_output=True, text=True, timeout=300).stdout.strip()


def _version(path: Path) -> str:
    output = _run([str(path), "--version"]).replace("(patched)", "").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][\w.-]+)? \(Claude Code\)", output):
        raise ValueError("Claude did not report a recognizable version")
    return output


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


def _identity(command: Path) -> tuple[Path, tuple[int, int, int, int], tuple[int, int, int, int]]:
    target = command.resolve(strict=True)
    link = command.lstat()
    native = target.stat()
    return (
        target,
        (link.st_dev, link.st_ino, link.st_mtime_ns, link.st_size),
        (native.st_dev, native.st_ino, native.st_mtime_ns, native.st_size),
    )


def _native(path: Path) -> bool:
    with path.open("rb") as stream:
        magic = stream.read(4)
    return magic in {b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\x7fELF"}


def _find_claude_command(explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        command = Path(explicit).expanduser().absolute()
        return command if command.is_file() else None
    candidates: list[str | Path | None] = [
        shutil.which("claude"),
        Path.home() / ".local" / "bin" / "claude",
        Path.home() / ".claude" / "local" / "bin" / "claude",
        Path("/usr/local/bin/claude"),
        Path("/Applications/Claude.app/Contents/Resources/bin/claude"),
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        command = Path(candidate).expanduser().absolute()
        if command.is_file():
            return command
    return None


def _download_source(destination: Path) -> Path:
    # Imported only by installation: the copied restore.py stays stdlib-only.
    from installer.manifest import get

    entry = get(SOURCE_ENTRY_ID)
    archive = destination / "source.tar.gz"
    request = urllib.request.Request(entry.source_url, headers={"User-Agent": "Pilot-Shell-Installer"})
    with urllib.request.urlopen(request, timeout=60) as response, archive.open("wb") as output:
        total = 0
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > 20 * 1024 * 1024:
                raise ValueError("Claude display patch source download is too large")
            output.write(chunk)
    if _hash(archive) != entry.sha256:
        raise ValueError("Claude display patch source SHA-256 mismatch")
    extracted = destination / "source"
    extracted.mkdir()
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        if sum(member.size for member in members) > 50 * 1024 * 1024:
            raise ValueError("Claude display patch source archive is too large")
        for member in members:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or not (member.isfile() or member.isdir()):
                raise ValueError("Unsafe path in Claude display patch source archive")
        source.extractall(extracted, members=members, filter="data")
    roots = list(extracted.iterdir())
    if (
        len(roots) != 1
        or not (roots[0] / "scripts" / "patch-native.ts").is_file()
        or not (roots[0] / "bun.lock").is_file()
    ):
        raise ValueError("Claude display patch source layout is incomplete")
    return roots[0]


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


def _matching_record(record: Any, binary_hash: str) -> dict[str, Any] | None:
    """Retain restore provenance if activation of a newer patch was interrupted."""
    while isinstance(record, dict):
        if record.get("patched_hash") == binary_hash:
            return record
        record = record.get("previous")
    return None


def _manifest_source() -> PatchSource:
    from installer.manifest import get

    entry = get(SOURCE_ENTRY_ID)
    return PatchSource(commit=entry.commit, source_url=entry.source_url, sha256=entry.sha256)


def _source_kit_path(state_dir: Path, source: PatchSource) -> Path:
    if not re.fullmatch(r"[0-9a-f]{40}", source.commit):
        raise ValueError("Invalid Claude display patch source commit")
    return state_dir / "source-kits" / source.commit


def _source_kit_ready(project: Path) -> bool:
    return (
        (project / "scripts" / "patch-native.ts").is_file()
        and (project / "patch-claude-display.ts").is_file()
        and (project / "bun.lock").is_file()
        and (project / "node_modules" / "node-lief").exists()
    )


def _source_kit_hash(project: Path) -> str:
    """Hash the prepared source tree, including relative paths and symlinks."""
    digest = hashlib.sha256()
    for path in sorted(project.rglob("*"), key=lambda item: item.relative_to(project).as_posix()):
        relative = path.relative_to(project).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        if path.is_symlink():
            digest.update(b"L")
            digest.update(os.readlink(path).encode("utf-8"))
        elif path.is_file():
            digest.update(b"F")
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        elif path.is_dir():
            digest.update(b"D")
    return digest.hexdigest()


def _prepare_source_kit(state_dir: Path, source: PatchSource, bun: str) -> Path:
    """Persist the verified patcher and its locked dependency for offline repair."""
    project = _source_kit_path(state_dir, source)
    state = _load_state(state_dir)
    raw = state.get("source")
    stored_hash = raw.get("kit_sha256") if isinstance(raw, dict) else None
    trusted = (
        _source_kit_ready(project)
        and isinstance(raw, dict)
        and raw.get("commit") == source.commit
        and raw.get("sha256") == source.sha256
        and raw.get("options") == DISABLED_PATCHES
        and raw.get("kit") == f"source-kits/{source.commit}"
        and isinstance(stored_hash, str)
        and _source_kit_hash(project) == stored_hash
    )
    if not trusted:
        with tempfile.TemporaryDirectory(prefix=".pilot-source-", dir=state_dir) as work:
            staged = Path(work)
            downloaded = _download_source(staged)
            _run([bun, "install", "--frozen-lockfile", "--ignore-scripts"], cwd=downloaded)
            if not _source_kit_ready(downloaded):
                raise ValueError("Claude display patch source kit is incomplete")
            project.parent.mkdir(parents=True, exist_ok=True)
            candidate = project.parent / f".{source.commit}.{os.getpid()}.tmp"
            if candidate.is_dir():
                shutil.rmtree(candidate)
            else:
                candidate.unlink(missing_ok=True)
            shutil.copytree(downloaded, candidate, symlinks=True)
            if project.exists():
                shutil.rmtree(project)
            os.replace(candidate, project)

    state = _load_state(state_dir)
    state["source"] = {
        "commit": source.commit,
        "source_url": source.source_url,
        "sha256": source.sha256,
        "options": DISABLED_PATCHES,
        "kit": f"source-kits/{source.commit}",
        "kit_sha256": _source_kit_hash(project),
    }
    _write_state(state_dir, state)
    return project


def _load_cached_source(state_dir: Path) -> tuple[PatchSource, Path]:
    state = _load_state(state_dir)
    raw = state.get("source")
    if not isinstance(raw, dict):
        raise ValueError("Claude display repair kit is missing; rerun the Pilot installer")
    source = PatchSource(
        commit=str(raw.get("commit", "")),
        source_url=str(raw.get("source_url", "")),
        sha256=str(raw.get("sha256", "")),
    )
    kit_sha256 = raw.get("kit_sha256")
    if (
        not re.fullmatch(r"[0-9a-f]{64}", source.sha256)
        or not isinstance(kit_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", kit_sha256)
        or raw.get("options") != DISABLED_PATCHES
    ):
        raise ValueError("Claude display repair kit metadata is invalid")
    expected_relative = f"source-kits/{source.commit}"
    if raw.get("kit") != expected_relative:
        raise ValueError("Claude display repair kit path is invalid")
    project = _source_kit_path(state_dir, source)
    if not _source_kit_ready(project):
        raise ValueError("Claude display repair kit is incomplete; rerun the Pilot installer")
    if _source_kit_hash(project) != kit_sha256:
        raise ValueError("Claude display repair kit integrity check failed; rerun the Pilot installer")
    return source, project


def _install_manager(state_dir: Path) -> None:
    for name in ("manager.py", "restore.py"):
        destination = state_dir / name
        shutil.copyfile(Path(__file__), destination)
        destination.chmod(0o600)


def _record_backup_names(record: object) -> set[str]:
    names: set[str] = set()
    while isinstance(record, dict):
        backup = record.get("backup")
        if isinstance(backup, str):
            names.add(backup)
        record = record.get("previous")
    return names


def _prune_unreferenced_backups(state_dir: Path, state: dict[str, Any]) -> None:
    referenced = {
        name
        for record in state["entries"].values()
        for name in _record_backup_names(record)
    }
    originals = state_dir / "originals"
    if not originals.is_dir():
        return
    for backup in originals.iterdir():
        relative = f"originals/{backup.name}"
        if backup.is_file() and relative not in referenced:
            backup.unlink(missing_ok=True)


def _retire_superseded_targets(state_dir: Path, state: dict[str, Any], active_target: Path) -> list[str]:
    """Restore inactive Pilot-patched versions so only the active backup remains."""
    failures: list[str] = []
    for target_name, stored_record in list(state["entries"].items()):
        target = Path(target_name)
        if target == active_target:
            continue
        try:
            if not target.is_absolute() or not isinstance(stored_record, dict):
                raise ValueError("Invalid Claude display patch target record")
            record = None if target.is_symlink() or not target.exists() else _matching_record(stored_record, _hash(target))
            if record is not None:
                snapshot = _identity(target)
                backup = _backup_path(state_dir, record)
                with tempfile.TemporaryDirectory(prefix=".pilot-retire-", dir=target.parent) as work:
                    candidate = Path(work) / "original"
                    shutil.copyfile(backup, candidate)
                    candidate.chmod(record["original_mode"])
                    if _identity(target) != snapshot or _hash(target) != record["patched_hash"]:
                        continue
                    os.replace(candidate, target)
            del state["entries"][target_name]
        except (OSError, ValueError, KeyError, TypeError) as error:
            failures.append(f"{target_name}: {error}")
    _prune_unreferenced_backups(state_dir, state)
    return failures


def _cleanup_stale_patch_workdirs(parent: Path, *, now: float | None = None) -> None:
    """Remove abandoned staging dirs from killed repairs, never a live recent one."""
    cutoff = (time.time() if now is None else now) - 3600
    for candidate in parent.glob(".pilot-display-*"):
        try:
            if candidate.is_symlink() or not candidate.is_dir() or candidate.stat().st_mtime >= cutoff:
                continue
            shutil.rmtree(candidate)
        except OSError:
            continue


def _apply(command: Path, state_dir: Path, bun: str, source: PatchSource, project: Path) -> PatchResult:
    snapshot = _identity(command)
    target = snapshot[0]
    expected_hash = _hash(target)
    state = _load_state(state_dir)
    retire_failures = _retire_superseded_targets(state_dir, state, target)
    _write_state(state_dir, state)
    record = _matching_record(state["entries"].get(str(target)), expected_hash)
    original = target
    if record is not None:
        original = _backup_path(state_dir, record)
        if record.get("source_commit") == source.commit and record.get("options") == DISABLED_PATCHES:
            return PatchResult("unchanged", "Claude display details already enabled")

    _cleanup_stale_patch_workdirs(target.parent)
    with tempfile.TemporaryDirectory(prefix=".pilot-display-", dir=target.parent) as work:
        stage = Path(work)
        staged_original = stage / "original"
        candidate = stage / "candidate"
        shutil.copyfile(original, staged_original)
        original_mode = stat.S_IMODE(target.stat().st_mode)
        staged_original.chmod(original_mode)
        original_hash = _hash(staged_original)
        original_version = _version(staged_original)
        patch_command = [
            bun,
            "scripts/patch-native.ts",
            "--input",
            str(staged_original),
            "--output",
            str(candidate),
            "--disable",
            DISABLED_PATCHES,
        ]
        _run([*patch_command, "--dry-run"], cwd=project)
        _run(patch_command, cwd=project)
        if not _native(candidate):
            raise ValueError("Patched Claude is not a native executable")
        candidate.chmod(original_mode)
        if _version(candidate) != original_version:
            raise ValueError("Patched Claude version does not match the installed version")
        patched_hash = _hash(candidate)
        if patched_hash == original_hash:
            raise ValueError("Claude display patches made no changes")

        backups = state_dir / "originals"
        backups.mkdir(exist_ok=True)
        backup = backups / original_hash
        if backup.exists():
            if _hash(backup) != original_hash:
                raise ValueError("Existing Claude original backup SHA-256 mismatch")
        else:
            shutil.copyfile(staged_original, backup)
            backup.chmod(0o600)
        if _hash(backup) != original_hash:
            raise ValueError("Claude original backup SHA-256 mismatch")
        # Journal before activation: even interruption immediately after replace
        # leaves a verified original and enough provenance for standalone restore.
        state["entries"][str(target)] = {
            "original_hash": original_hash,
            "patched_hash": patched_hash,
            "backup": f"originals/{original_hash}",
            "source_commit": source.commit,
            "source_url": source.source_url,
            "source_sha256": source.sha256,
            "options": DISABLED_PATCHES,
            "original_version": original_version,
            "original_mode": original_mode,
        }
        if record is not None:
            state["entries"][str(target)]["previous"] = record
        _write_state(state_dir, state)
        if _identity(command) != snapshot or _hash(target) != expected_hash:
            raise ValueError("Claude changed while preparing display patches; keeping the new binary")
        os.replace(candidate, target)
    suffix = "" if not retire_failures else f"; inactive restore warnings: {'; '.join(retire_failures)}"
    return PatchResult("patched", f"Claude display details enabled (original saved for uninstall){suffix}")


def apply_display_patch(*, claude_path: Path | None = None, state_dir: Path | None = None) -> PatchResult:
    """Apply pinned source patches to an existing writable native Claude only."""
    try:
        if (platform.system(), platform.machine()) not in _SUPPORTED:
            return PatchResult("skipped", "Claude display patches are unavailable on this platform")
        command = _find_claude_command(claude_path)
        bun = shutil.which("bun")
        if command is None or not bun:
            return PatchResult("skipped", "Claude display patches need an existing Claude and Bun")
        target = command.resolve(strict=True)
        if not _native(target):
            return PatchResult("skipped", "Claude display patches require a native install; npm wrappers are preserved")
        if not os.access(target, os.W_OK) or not os.access(target.parent, os.W_OK):
            return PatchResult("skipped", "Claude executable is not writable; no elevated privileges requested")
        directory = state_dir or Path.home() / ".pilot" / "claude-display-patch"
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            source = _manifest_source()
            project = _prepare_source_kit(directory, source, bun)
            _install_manager(directory)
            return _apply(command, directory, bun, source, project)
    except BlockingIOError:
        return PatchResult("busy", "Claude display patch management is already running")
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as error:
        return PatchResult("failed", f"Claude display patches skipped: {error}")


def repair_display_patch(*, claude_path: Path | None = None, state_dir: Path | None = None) -> PatchResult:
    """Reapply the installed, verified patch kit after Claude replaces its binary."""
    try:
        if (platform.system(), platform.machine()) not in _SUPPORTED:
            return PatchResult("skipped", "Claude display patches are unavailable on this platform")
        command = _find_claude_command(claude_path)
        bun = shutil.which("bun")
        if command is None or not bun:
            return PatchResult("skipped", "Claude display repair needs an existing Claude and Bun")
        target = command.resolve(strict=True)
        if not _native(target):
            return PatchResult("skipped", "Claude display repair requires a native install")
        if not os.access(target, os.W_OK) or not os.access(target.parent, os.W_OK):
            return PatchResult("skipped", "Claude executable is not writable; no elevated privileges requested")
        if "(patched)" in _run([str(target), "--version"]):
            return PatchResult("unchanged", "Claude display details already enabled")
        directory = state_dir or Path.home() / ".pilot" / "claude-display-patch"
        if not directory.is_dir():
            return PatchResult("failed", "Claude display repair kit is missing; rerun the Pilot installer")
        with (directory / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            source, project = _load_cached_source(directory)
            return _apply(command, directory, bun, source, project)
    except BlockingIOError:
        return PatchResult("busy", "Claude display repair is already running")
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as error:
        return PatchResult("failed", f"Claude display repair skipped: {error}")


def restore_display_patch(state_dir: Path | None = None) -> PatchResult:
    """Restore only unchanged binaries whose patch hash and backup are verified."""
    directory = state_dir or Path(__file__).resolve().parent
    if not (directory / "state.json").exists():
        return PatchResult("restored", "No Claude display patches to restore")
    try:
        with (directory / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state = _load_state(directory)
            failures: list[str] = []
            for target_name, stored_record in list(state["entries"].items()):
                try:
                    target = Path(target_name)
                    if not target.is_absolute() or not isinstance(stored_record, dict):
                        raise ValueError("Invalid Claude display patch target record")
                    record = (
                        None
                        if target.is_symlink() or not target.exists()
                        else _matching_record(stored_record, _hash(target))
                    )
                    if record is None:
                        del state["entries"][target_name]
                        continue  # A user/Claude upgrade owns the changed target now.
                    snapshot = _identity(target)
                    backup = _backup_path(directory, record)
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
            _prune_unreferenced_backups(directory, state)
            _write_state(directory, state)
            if failures:
                return PatchResult("failed", "Claude restore incomplete: " + "; ".join(failures))
        return PatchResult("restored", "Claude originals restored; newer or modified binaries preserved")
    except BlockingIOError:
        return PatchResult("busy", "Claude display restore is already running")
    except (OSError, ValueError) as error:
        return PatchResult("failed", f"Claude restore incomplete: {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage native Claude binaries patched by Pilot")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--restore", action="store_true")
    action.add_argument("--repair", action="store_true")
    parser.add_argument("--state-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = restore_display_patch(args.state_dir) if args.restore else repair_display_patch(state_dir=args.state_dir)
    if args.json:
        print(json.dumps({"status": result.status, "message": result.message}))
    else:
        print(result.message)
    return 1 if result.status == "failed" or (args.restore and result.status == "busy") else 0


if __name__ == "__main__":
    raise SystemExit(main())
