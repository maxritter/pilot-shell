"""Remove the retired RTK integration without requiring a working RTK binary."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from installer.claude_paths import get_claude_config_dir


def _write(path: Path, text: str) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".pilot-cleanup-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def _remove_hooks(path: Path, *, owned: bool) -> None:
    if path.is_symlink():
        raise ValueError("symlinked configuration requires manual RTK cleanup; assets are retained")
    if not path.is_file():
        return
    content = path.read_text()
    if not owned and "tool_token_saver.py" not in content:
        return
    data = json.loads(content)
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return
    changed = False
    for event, groups in list(hooks.items()):
        if not isinstance(groups, list):
            continue
        kept = []
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                kept.append(group)
                continue
            handlers = []
            for handler in group["hooks"]:
                command = handler.get("command", "") if isinstance(handler, dict) else ""
                retired = isinstance(command, str) and (
                    ".pilot/hooks/tool_token_saver.py" in command
                    or (
                        owned
                        and (
                            "rtk-rewrite.sh" in command
                            or re.search(r"(?:^|[\s/])rtk\s+(?:hook|rewrite)(?:\s|$)", command)
                        )
                    )
                )
                if retired:
                    changed = True
                else:
                    handlers.append(handler)
            if handlers:
                kept.append({**group, "hooks": handlers})
        if kept:
            hooks[event] = kept
        else:
            hooks.pop(event, None)
    if changed:
        _write(path, json.dumps(data, indent=2) + "\n")


def _remove_instructions(path: Path) -> None:
    if path.is_symlink():
        raise ValueError("symlinked instructions require manual RTK cleanup; assets are retained")
    if not path.is_file():
        return
    content = path.read_text()
    cleaned = re.sub(
        r"(?m)^<!-- rtk-instructions[^\n]*\n.*?^<!-- /rtk-instructions -->[^\n]*\n?", "", content, flags=re.S
    )
    cleaned = re.sub(r"(?m)^[ \t]*@(?:[^\r\n]*[/])?RTK[.]md[ \t]*(?:\r?\n|$)", "", cleaned)
    if cleaned != content:
        _write(path, cleaned)


def _safe_path(path: Path, root: Path) -> None:
    parent = path.parent
    while parent != root and root in parent.parents:
        if parent.is_symlink():
            raise ValueError(f"refusing to follow symlinked directory {parent}")
        parent = parent.parent
    if root.is_symlink():
        raise ValueError(f"refusing to follow symlinked directory {root}")


def _remove_owned(path: Path, root: Path) -> None:
    _safe_path(path, root)
    if path.is_symlink() or not path.is_dir():
        path.unlink(missing_ok=True)
    else:
        shutil.rmtree(path)


def _cleanup_profile(profile: Path, name: str, owned: bool, managed: bool) -> list[str]:
    errors = []
    if not owned and not managed:
        return errors
    try:
        if profile.is_symlink():
            raise ValueError("symlinked profile requires manual RTK cleanup; assets are retained")
        for path in (profile / "settings.json", profile / "settings.local.json", profile / "hooks.json"):
            _remove_hooks(path, owned=owned)
        if owned:
            _remove_instructions(profile / name)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        errors.append(f"{profile}: {error}")
    return errors


def remove_rtk(*, home: Path | None = None, claude_dir: Path | None = None, codex_dir: Path | None = None) -> list[str]:
    """Retire integration artifacts; remove the executable only with Pilot ownership proof.

    Fresh installs are a no-op. Other tools and user settings remain intact.
    Return failures so the installer can report them and retry on a later update.
    """
    home = home if home is not None else Path.home()
    claude_dir = claude_dir if claude_dir is not None else get_claude_config_dir()
    codex_dir = codex_dir if codex_dir is not None else Path(os.environ.get("CODEX_HOME", str(home / ".codex")))
    pilot = home / ".pilot"
    manifest = pilot / ".pilot-owned-tools.json"
    data = {}
    errors: list[str] = []
    try:
        if manifest.is_file() and not manifest.is_symlink():
            data = json.loads(manifest.read_text())
    except (OSError, ValueError):
        # No ownership proof means preserve user RTK integrations and data.
        data = {}
    owned = isinstance(data, dict) and isinstance(data.get("tools"), list) and "rtk" in data["tools"]
    managed = (pilot / "hooks/tool_token_saver.py").exists()
    for profile, name in ((claude_dir, "CLAUDE.md"), (codex_dir, "AGENTS.md")):
        errors.extend(_cleanup_profile(profile, name, owned, managed))
    if errors:
        return errors  # Keep scripts, imports, binaries and ownership for a later retry.
    try:
        for path in (pilot / "bin/rtk", pilot / "hooks/tool_token_saver.py"):
            _remove_owned(path, home)
        if owned:
            for profile in (claude_dir, codex_dir):
                for name in ("RTK.md", "hooks/rtk-rewrite.sh", "hooks/rtk-rewrite.sh.sha256"):
                    _remove_owned(profile / name, profile)
            for path in (home / ".local/bin/rtk", home / ".config/rtk", home / ".local/share/rtk"):
                _remove_owned(path, home)
            data["tools"] = [tool for tool in data["tools"] if tool != "rtk"]
            _write(manifest, json.dumps(data, indent=2) + "\n")
    except (OSError, ValueError) as error:
        errors.append(f"{pilot}: {error}")
    return errors
