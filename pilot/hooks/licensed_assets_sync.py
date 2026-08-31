"""Suspend and restore manifest-owned agent assets with Pilot access."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.util import claude_config_dir  # noqa: E402

_CLAUDE_PREFIXES = ("agents/", "commands/", "rules/")
_CODEX_BLOCK_START = "<!-- PILOT:START -->"
_CODEX_BLOCK_END = "<!-- PILOT:END -->"


def _check_license() -> bool | None:
    pilot = Path.home() / ".pilot" / "bin" / "pilot"
    if not pilot.is_file():
        return None
    try:
        result = subprocess.run(
            [str(pilot), "verify", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        payload = json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
        return None
    return payload.get("valid", False) is True


def _codex_config_dir() -> Path | None:
    configured = os.environ.get("CODEX_HOME")
    path = Path(configured).expanduser() if configured else Path.home() / ".codex"
    if not path.is_absolute():
        return None
    return path


def _safe_relative(value: object, prefixes: tuple[str, ...]) -> Path | None:
    if not isinstance(value, str) or not value.startswith(prefixes) or "\\" in value or "\x00" in value:
        return None
    relative = Path(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        return None
    return relative


def _manifest_paths(path: Path, prefixes: tuple[str, ...]) -> list[Path]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    values = payload.get("files") if isinstance(payload, dict) else None
    if not isinstance(values, list):
        return []
    return [relative for value in values if (relative := _safe_relative(value, prefixes)) is not None]


def _codex_rule_paths(codex_dir: Path) -> list[Path]:
    manifest = codex_dir / "rules" / ".pilot-rules.json"
    try:
        values = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(values, list):
        return []
    paths: list[Path] = []
    for value in values:
        if not isinstance(value, str) or not value or "/" in value or "\\" in value or value in {".", ".."}:
            continue
        paths.append(Path(value))
    return paths


def _has_symlink_component(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    current = root
    if current.is_symlink():
        return True
    for part in relative.parts[:-1]:
        current /= part
        if current.is_symlink():
            return True
    return False


def _backup_file(source: Path, backup: Path, source_root: Path, backup_root: Path) -> bool:
    if not source.is_file() or source.is_symlink():
        return False
    if _has_symlink_component(source, source_root) or _has_symlink_component(backup, backup_root):
        return False
    try:
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup)
        source.unlink()
        return True
    except OSError:
        return False


def _restore_tree(backup_root: Path, target_root: Path) -> int:
    if not backup_root.is_dir() or backup_root.is_symlink():
        return 0
    restored = 0
    for backup in sorted(backup_root.rglob("*")):
        if not backup.is_file() or backup.is_symlink():
            continue
        relative = backup.relative_to(backup_root)
        target = target_root / relative
        if target.exists() or target.is_symlink() or _has_symlink_component(target, target_root):
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, target)
            backup.unlink()
            restored += 1
        except OSError:
            continue
    for directory in sorted((path for path in backup_root.rglob("*") if path.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        backup_root.rmdir()
    except OSError:
        pass
    return restored


def _write_atomic(path: Path, content: str) -> bool:
    temporary: str | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
        fd, temporary = tempfile.mkstemp(prefix=".pilot-assets-", dir=path.parent)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
        return True
    except OSError:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass
        return False


def _suspend_codex_block(codex_dir: Path, backup_root: Path) -> int:
    if codex_dir.is_symlink() or backup_root.is_symlink():
        return 0
    agents = codex_dir / "AGENTS.md"
    if not agents.is_file() or agents.is_symlink():
        return 0
    try:
        content = agents.read_text(encoding="utf-8")
    except OSError:
        return 0
    if content.count(_CODEX_BLOCK_START) != 1 or content.count(_CODEX_BLOCK_END) != 1:
        return 0
    start = content.index(_CODEX_BLOCK_START)
    end = content.index(_CODEX_BLOCK_END, start) + len(_CODEX_BLOCK_END)
    block = content[start:end].strip() + "\n"
    before = content[:start].rstrip("\n")
    after = content[end:].lstrip("\n")
    remaining = f"{before}\n\n{after}" if before and after.strip() else f"{before}\n" if before else after
    backup = backup_root / "AGENTS.block"
    if not _write_atomic(backup, block):
        return 0
    if remaining.strip():
        return 1 if _write_atomic(agents, remaining) else 0
    try:
        agents.unlink()
        return 1
    except OSError:
        return 0


def _restore_codex_block(codex_dir: Path, backup_root: Path) -> int:
    if codex_dir.is_symlink() or backup_root.is_symlink():
        return 0
    backup = backup_root / "AGENTS.block"
    if not backup.is_file() or backup.is_symlink():
        return 0
    try:
        block = backup.read_text(encoding="utf-8").strip()
        agents = codex_dir / "AGENTS.md"
        current = agents.read_text(encoding="utf-8") if agents.is_file() and not agents.is_symlink() else ""
    except OSError:
        return 0
    if _CODEX_BLOCK_START in current or agents.is_symlink():
        return 0
    content = f"{current.rstrip()}\n\n{block}\n" if current.strip() else f"{block}\n"
    if not _write_atomic(agents, content):
        return 0
    backup.unlink(missing_ok=True)
    return 1


def suspend_assets() -> int:
    pilot_home = Path.home() / ".pilot"
    backup_root = pilot_home / "inactive-assets"
    if backup_root.is_symlink():
        return 0
    changed = 0

    claude_dir = claude_config_dir()
    if claude_dir is not None:
        manifest = claude_dir / ".pilot-manifest.json"
        for relative in _manifest_paths(manifest, _CLAUDE_PREFIXES):
            changed += int(
                _backup_file(
                    claude_dir / relative,
                    backup_root / "claude" / relative,
                    claude_dir,
                    backup_root,
                )
            )

    codex_dir = _codex_config_dir()
    if codex_dir is not None:
        for relative in _codex_rule_paths(codex_dir):
            changed += int(
                _backup_file(
                    codex_dir / "rules" / relative,
                    backup_root / "codex-rules" / relative,
                    codex_dir,
                    backup_root,
                )
            )
        changed += _suspend_codex_block(codex_dir, backup_root / "codex")
    return changed


def restore_assets() -> int:
    backup_root = Path.home() / ".pilot" / "inactive-assets"
    if backup_root.is_symlink():
        return 0
    restored = 0
    claude_dir = claude_config_dir()
    if claude_dir is not None:
        restored += _restore_tree(backup_root / "claude", claude_dir)
    codex_dir = _codex_config_dir()
    if codex_dir is not None:
        restored += _restore_tree(backup_root / "codex-rules", codex_dir / "rules")
        restored += _restore_codex_block(codex_dir, backup_root / "codex")
    for directory in (backup_root / "codex", backup_root):
        try:
            directory.rmdir()
        except OSError:
            pass
    return restored


def main() -> None:
    valid = _check_license()
    if valid is True:
        restore_assets()
    elif valid is False:
        suspend_assets()
    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
