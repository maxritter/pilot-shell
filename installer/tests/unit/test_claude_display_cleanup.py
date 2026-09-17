"""Retiring the Claude display patch (issue #191) must leave a stock binary behind."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from installer import claude_display_cleanup as cleanup

ORIGINAL = b"\xcf\xfa\xed\xfeofficial claude"
PATCHED = b"\xcf\xfa\xed\xfepatched claude"


@pytest.fixture
def patched(tmp_path: Path):
    """A machine in the pre-removal state: patched binary + verified backup."""
    target = tmp_path / "versions" / "2.1.274"
    target.parent.mkdir()
    target.write_bytes(PATCHED)
    target.chmod(0o755)
    state_dir = tmp_path / ".pilot" / "claude-display-patch"
    (state_dir / "originals").mkdir(parents=True)
    original_hash = hashlib.sha256(ORIGINAL).hexdigest()
    (state_dir / "originals" / original_hash).write_bytes(ORIGINAL)
    (state_dir / "source-kits" / "27ef91e").mkdir(parents=True)
    (state_dir / "manager.py").write_text("# fixture")
    record = {
        "original_hash": original_hash,
        "patched_hash": hashlib.sha256(PATCHED).hexdigest(),
        "backup": f"originals/{original_hash}",
        "original_version": "2.1.274 (Claude Code)",
        "original_mode": 0o755,
    }
    (state_dir / "state.json").write_text(json.dumps({"schema": 1, "entries": {str(target): record}}))
    marker = tmp_path / ".claude" / ".pilot-display-patch-migration.json"
    marker.parent.mkdir(parents=True)
    marker.write_text('{"version": 1}\n')
    return SimpleNamespace(target=target, state_dir=state_dir, marker=marker, record=record)


def test_restores_the_original_binary_and_deletes_the_state(patched):
    result = cleanup.remove_display_patch(state_dir=patched.state_dir, marker_path=patched.marker)

    assert result.status == "removed"
    assert patched.target.read_bytes() == ORIGINAL
    assert patched.target.stat().st_mode & 0o777 == 0o755
    assert not patched.state_dir.exists()
    assert not patched.marker.exists()


def test_second_run_is_a_silent_no_op(patched):
    assert cleanup.remove_display_patch(state_dir=patched.state_dir, marker_path=patched.marker).status == "removed"
    repeat = cleanup.remove_display_patch(state_dir=patched.state_dir, marker_path=patched.marker)

    assert repeat.status == "unchanged"
    assert patched.target.read_bytes() == ORIGINAL


def test_binary_claude_replaced_itself_is_left_alone(patched):
    """The patch is gone already; that target is no longer Pilot's to write."""
    patched.target.write_bytes(b"\xcf\xfa\xed\xfenewer official claude")

    result = cleanup.remove_display_patch(state_dir=patched.state_dir, marker_path=patched.marker)

    assert result.status == "removed"
    assert patched.target.read_bytes() == b"\xcf\xfa\xed\xfenewer official claude"
    assert not patched.state_dir.exists()


def test_corrupt_backup_keeps_the_binary_and_the_backup_directory(patched):
    (patched.state_dir / patched.record["backup"]).write_bytes(b"tampered backup")

    result = cleanup.remove_display_patch(state_dir=patched.state_dir, marker_path=patched.marker)

    assert result.status == "failed"
    assert "SHA-256 mismatch" in result.message
    assert patched.target.read_bytes() == PATCHED
    assert patched.state_dir.is_dir()
    assert patched.marker.exists()
    assert json.loads((patched.state_dir / "state.json").read_text())["entries"]


def test_interrupted_patch_upgrade_journal_still_restores(patched):
    state_path = patched.state_dir / "state.json"
    state = json.loads(state_path.read_text())
    previous = state["entries"][str(patched.target)]
    # A later patch journalled its candidate, then stopped before replacing the binary.
    state["entries"][str(patched.target)] = {**previous, "patched_hash": "f" * 64, "previous": previous}
    state_path.write_text(json.dumps(state))

    assert cleanup.remove_display_patch(state_dir=patched.state_dir, marker_path=patched.marker).status == "removed"
    assert patched.target.read_bytes() == ORIGINAL


def test_concurrent_repair_defers_instead_of_racing_the_binary(patched, monkeypatch):
    def busy(*_args, **_kwargs):
        raise BlockingIOError("busy")

    monkeypatch.setattr(cleanup.fcntl, "flock", busy)

    result = cleanup.remove_display_patch(state_dir=patched.state_dir, marker_path=patched.marker)

    assert result.status == "busy"
    assert patched.target.read_bytes() == PATCHED
    assert patched.state_dir.is_dir()


def test_missing_state_directory_is_the_fresh_install_case(tmp_path):
    result = cleanup.remove_display_patch(state_dir=tmp_path / "absent", marker_path=tmp_path / "absent-marker")

    assert result.status == "unchanged"


def test_unreadable_state_preserves_everything(patched):
    (patched.state_dir / "state.json").write_text("{not json")

    result = cleanup.remove_display_patch(state_dir=patched.state_dir, marker_path=patched.marker)

    assert result.status == "failed"
    assert patched.target.read_bytes() == PATCHED
    assert patched.state_dir.is_dir()
