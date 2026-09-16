"""Claude display patching keeps native upgrades and user binaries intact."""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from installer import claude_display_patch as patcher

ORIGINAL = b"\xcf\xfa\xed\xfeofficial claude"
PATCHED = b"\xcf\xfa\xed\xfepatched claude"


@pytest.fixture
def native(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    target = tmp_path / "versions" / "2.1.263"
    target.parent.mkdir()
    target.write_bytes(ORIGINAL)
    target.chmod(0o755)
    command = tmp_path / "claude"
    command.symlink_to(target)
    state = tmp_path / "state"
    project = tmp_path / "source"
    project.mkdir()
    (project / "scripts").mkdir()
    (project / "scripts" / "patch-native.ts").write_text("// fixture")
    (project / "patch-claude-display.ts").write_text("// fixture")
    (project / "bun.lock").write_text("fixture")
    (project / "node_modules" / "node-lief").mkdir(parents=True)
    calls: list[list[str]] = []
    downloads: list[Path] = []
    monkeypatch.setattr(patcher.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(patcher.platform, "machine", lambda: "arm64")
    monkeypatch.setattr(patcher.shutil, "which", lambda name: str(command) if name == "claude" else "/bun")

    def download(destination: Path):
        downloads.append(destination)
        return project

    def run(argv: list[str], *, cwd: Path | None = None):
        calls.append(argv)
        if argv[-1] == "--version":
            suffix = " (patched)" if Path(argv[0]).read_bytes() == PATCHED else ""
            return f"2.1.263 (Claude Code){suffix}"
        if "--output" in argv and "--dry-run" not in argv:
            Path(argv[argv.index("--output") + 1]).write_bytes(PATCHED)
        return "ok"

    monkeypatch.setattr(patcher, "_download_source", download)
    monkeypatch.setattr(patcher, "_run", run)
    return SimpleNamespace(
        target=target,
        command=command,
        state=state,
        calls=calls,
        downloads=downloads,
        run=run,
    )


def test_stages_copy_verifies_and_preserves_native_symlink(native):
    result = patcher.apply_display_patch(claude_path=native.command, state_dir=native.state)
    assert result.status == "patched"
    assert native.command.is_symlink()
    assert native.target.read_bytes() == PATCHED
    assert native.target.stat().st_mode & 0o777 == 0o755
    record = json.loads((native.state / "state.json").read_text())["entries"][str(native.target)]
    assert (native.state / record["backup"]).read_bytes() == ORIGINAL
    assert record["original_hash"] == hashlib.sha256(ORIGINAL).hexdigest()
    assert record["patched_hash"] == hashlib.sha256(PATCHED).hexdigest()
    assert record["source_commit"] == "27ef91e5d7fdeeec52dba727f2d2796b5b0fcdb3"
    assert (native.state / "restore.py").exists()
    assert (native.state / "manager.py").exists()
    assert (native.state / "source-kits" / record["source_commit"] / "scripts" / "patch-native.ts").exists()
    patch_calls = [call for call in native.calls if "--input" in call]
    assert len(patch_calls) == 2
    assert "--dry-run" in patch_calls[0]
    assert "--dry-run" not in patch_calls[1]
    assert all(str(native.target) not in call for call in patch_calls)
    assert all(
        call[call.index("--disable") + 1] == "welcome-badge,installer-label,disable-spinner-tips"
        for call in patch_calls
    )
    assert ["/bun", "install", "--frozen-lockfile", "--ignore-scripts"] in native.calls


def test_repeat_does_not_download_or_repatch(native):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    calls = len(native.calls)
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "unchanged"
    assert len(native.calls) == calls
    assert len(native.downloads) == 1


@pytest.mark.parametrize("reason", ["missing", "wrapper", "platform", "unwritable", "bun"])
def test_skip_before_network(native, monkeypatch, reason):
    if reason == "missing":
        native.command.unlink()
        monkeypatch.setattr(patcher, "_find_claude_command", lambda _explicit=None: None)
    elif reason == "wrapper":
        native.target.write_text("#!/bin/sh\nexec node cli.js\n")
    elif reason == "platform":
        monkeypatch.setattr(patcher.platform, "machine", lambda: "x86_64")
    elif reason == "unwritable":
        monkeypatch.setattr(patcher.os, "access", lambda *args: False)
    else:
        monkeypatch.setattr(patcher.shutil, "which", lambda name: str(native.command) if name == "claude" else None)
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "skipped"
    assert not native.downloads


@pytest.mark.parametrize("failure", ["download", "dry-run", "patch", "version", "race", "symlink-race"])
def test_failure_leaves_original_and_upgrades_intact(native, monkeypatch, failure):
    if failure == "download":
        monkeypatch.setattr(
            patcher, "_download_source", lambda _: (_ for _ in ()).throw(ValueError("SHA-256 mismatch"))
        )

    def run(argv, *, cwd=None):
        if failure == "dry-run" and "--dry-run" in argv:
            raise subprocess.CalledProcessError(1, argv, stderr="patch did not match")
        if failure == "patch" and "--output" in argv and "--dry-run" not in argv:
            raise subprocess.CalledProcessError(1, argv, stderr="patch failed")
        result = native.run(argv, cwd=cwd)
        if argv[-1] == "--version" and Path(argv[0]).read_bytes() == PATCHED:
            if failure == "version":
                return "2.1.200 (Claude Code)"
            if failure == "race":
                replacement = native.target.with_suffix(".new")
                replacement.write_bytes(ORIGINAL)
                replacement.replace(native.target)
            if failure == "symlink-race":
                newer = native.target.with_name("2.1.264")
                newer.write_bytes(ORIGINAL)
                native.command.unlink()
                native.command.symlink_to(newer)
        return result

    monkeypatch.setattr(patcher, "_run", run)
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "failed"
    assert native.target.read_bytes() == ORIGINAL
    assert native.command.read_bytes() == ORIGINAL


def test_source_download_enforces_hash(tmp_path, monkeypatch):
    monkeypatch.setattr(patcher.urllib.request, "urlopen", lambda *a, **kw: io.BytesIO(b"tampered archive"))
    with pytest.raises(ValueError, match="SHA-256"):
        patcher._download_source(tmp_path)


def test_source_download_is_bounded(tmp_path, monkeypatch):
    monkeypatch.setattr(patcher.urllib.request, "urlopen", lambda *a, **kw: io.BytesIO(b"x" * (21 * 1024 * 1024)))
    with pytest.raises(ValueError, match="too large"):
        patcher._download_source(tmp_path)
    assert (tmp_path / "source.tar.gz").stat().st_size == 20 * 1024 * 1024


def test_finds_standard_native_install_when_hook_path_is_minimal(tmp_path, monkeypatch):
    command = tmp_path / ".local" / "bin" / "claude"
    command.parent.mkdir(parents=True)
    command.write_bytes(ORIGINAL)
    command.chmod(0o755)
    monkeypatch.setattr(patcher.shutil, "which", lambda _name: None)
    monkeypatch.setattr(patcher.Path, "home", classmethod(lambda _cls: tmp_path))

    assert patcher._find_claude_command() == command


def test_lock_contention_is_reported_without_touching_binary(native, monkeypatch):
    def busy(*_args, **_kwargs):
        raise BlockingIOError("busy")

    monkeypatch.setattr(patcher.fcntl, "flock", busy)
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "busy"
    assert native.target.read_bytes() == ORIGINAL
    assert patcher.repair_display_patch(claude_path=native.command, state_dir=native.state).status == "busy"
    (native.state / "state.json").write_text(json.dumps({"schema": 1, "entries": {}}))
    assert patcher.restore_display_patch(native.state).status == "busy"
    assert native.target.read_bytes() == ORIGINAL


def test_stale_patch_workdirs_are_cleaned_without_touching_recent_or_symlinked_dirs(tmp_path):
    stale = tmp_path / ".pilot-display-stale"
    recent = tmp_path / ".pilot-display-recent"
    outside = tmp_path / "outside"
    link = tmp_path / ".pilot-display-link"
    stale.mkdir()
    recent.mkdir()
    outside.mkdir()
    link.symlink_to(outside, target_is_directory=True)
    os.utime(stale, (100, 100))
    os.utime(recent, (3900, 3900))

    patcher._cleanup_stale_patch_workdirs(tmp_path, now=4000)

    assert not stale.exists()
    assert recent.exists()
    assert link.is_symlink()
    assert outside.exists()


def test_repair_uses_cached_source_and_retires_inactive_target(native):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    older = native.target
    native.target = older.with_name("2.1.264")
    native.target.write_bytes(ORIGINAL)
    native.target.chmod(0o755)
    native.command.unlink()
    native.command.symlink_to(native.target)
    assert patcher.repair_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    assert len(native.downloads) == 1
    assert older.read_bytes() == ORIGINAL
    assert len(json.loads((native.state / "state.json").read_text())["entries"]) == 1
    assert patcher.restore_display_patch(native.state).status == "restored"
    assert native.command.read_bytes() == ORIGINAL
    assert native.command.is_symlink()


def test_repair_rejects_tampered_cached_source(native):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    state = json.loads((native.state / "state.json").read_text())
    kit = native.state / state["source"]["kit"]
    (kit / "scripts" / "patch-native.ts").write_text("tampered")
    newer = native.target.with_name("2.1.264")
    newer.write_bytes(ORIGINAL)
    newer.chmod(0o755)
    native.command.unlink()
    native.command.symlink_to(newer)

    result = patcher.repair_display_patch(claude_path=native.command, state_dir=native.state)

    assert result.status == "failed"
    assert "integrity check failed" in result.message
    assert newer.read_bytes() == ORIGINAL


def test_full_installer_rebuilds_tampered_cached_source(native):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    state = json.loads((native.state / "state.json").read_text())
    kit = native.state / state["source"]["kit"]
    (kit / "scripts" / "patch-native.ts").write_text("tampered")

    result = patcher.apply_display_patch(claude_path=native.command, state_dir=native.state)

    assert result.status == "unchanged"
    assert len(native.downloads) == 2
    assert (kit / "scripts" / "patch-native.ts").read_text() == "// fixture"


def test_restore_preserves_modified_binary(native):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    native.target.write_bytes(b"user upgrade")
    assert patcher.restore_display_patch(native.state).status == "restored"
    assert native.target.read_bytes() == b"user upgrade"


def test_restore_rejects_corrupt_backup(native):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    record = json.loads((native.state / "state.json").read_text())["entries"][str(native.target)]
    (native.state / record["backup"]).write_bytes(b"bad backup")
    assert patcher.restore_display_patch(native.state).status == "failed"
    assert native.target.read_bytes() == PATCHED


def test_restore_handles_interrupted_patch_upgrade_journal(native):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    state_path = native.state / "state.json"
    state = json.loads(state_path.read_text())
    previous = state["entries"][str(native.target)]
    # The next patch recorded its candidate, then stopped before native replace.
    state["entries"][str(native.target)] = {**previous, "patched_hash": "f" * 64, "previous": previous}
    state_path.write_text(json.dumps(state))
    assert patcher.restore_display_patch(native.state).status == "restored"
    assert native.target.read_bytes() == ORIGINAL


def test_restore_preserves_a_concurrent_auto_update(native, monkeypatch):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    real_hash = patcher._hash

    def hash_and_update(path):
        result = real_hash(path)
        if path.name == "original":
            newer = native.target.with_suffix(".new")
            newer.write_bytes(b"newer official binary")
            newer.replace(native.target)
        return result

    monkeypatch.setattr(patcher, "_hash", hash_and_update)
    assert patcher.restore_display_patch(native.state).status == "restored"
    assert native.target.read_bytes() == b"newer official binary"


def test_installed_restore_script_is_standalone(native):
    assert patcher.apply_display_patch(claude_path=native.command, state_dir=native.state).status == "patched"
    import sys

    result = subprocess.run(
        [sys.executable, str(native.state / "restore.py"), "--restore"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert native.target.read_bytes() == ORIGINAL
