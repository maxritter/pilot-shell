"""Tests for scripts.isolation — contamination detection, hide/restore, fail-safe recovery."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from scripts import isolation
from scripts.isolation import (
    HIDDEN_RESTORE_QUEUE,
    HIDDEN_SUFFIX,
    _clear_manifest,
    _manifest_path,
    _process_alive,
    _write_manifest,
    detect_global_contamination,
    isolate_global_contamination,
    recover_stale_manifests,
)
from scripts.utils import TargetConfig


# ----------------------------------------------------------------------------
# detect_global_contamination
# ----------------------------------------------------------------------------


class TestDetectContamination:
    def _with_home(self, monkeypatch: pytest.MonkeyPatch, tmp_home: Path):
        monkeypatch.setenv("HOME", str(tmp_home))
        # Path.home() reads HOME on POSIX.
        (tmp_home / ".claude").mkdir(parents=True, exist_ok=True)

    def test_missing_path_returns_empty(self, tmp_path: Path) -> None:
        target: TargetConfig = {"type": "rules", "path": str(tmp_path / "nope.md")}
        assert detect_global_contamination(target) == []

    def test_no_path_returns_empty(self) -> None:
        target: TargetConfig = {"type": "rules"}
        assert detect_global_contamination(target) == []

    def test_rules_file_with_matching_global(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        tmp_home = tmp_path / "home"
        self._with_home(monkeypatch, tmp_home)
        (tmp_home / ".claude" / "rules").mkdir(parents=True)
        global_rule = tmp_home / ".claude" / "rules" / "testing.md"
        _ = global_rule.write_text("global copy")

        project_rule = tmp_path / "pilot" / "rules" / "testing.md"
        project_rule.parent.mkdir(parents=True)
        _ = project_rule.write_text("project copy")

        target: TargetConfig = {"type": "rules", "path": str(project_rule)}
        result = detect_global_contamination(target)
        assert result == [global_rule]

    def test_rules_file_skips_if_target_is_global_itself(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        tmp_home = tmp_path / "home"
        self._with_home(monkeypatch, tmp_home)
        (tmp_home / ".claude" / "rules").mkdir(parents=True)
        global_rule = tmp_home / ".claude" / "rules" / "testing.md"
        _ = global_rule.write_text("user's rule")

        # Benchmarking the global file directly — it must NOT be flagged as its
        # own contaminator (would hide the source the runner needs to copy).
        target: TargetConfig = {"type": "rules", "path": str(global_rule)}
        assert detect_global_contamination(target) == []

    def test_rules_directory_finds_per_file_matches(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        tmp_home = tmp_path / "home"
        self._with_home(monkeypatch, tmp_home)
        (tmp_home / ".claude" / "rules").mkdir(parents=True)
        _ = (tmp_home / ".claude" / "rules" / "a.md").write_text("global a")
        _ = (tmp_home / ".claude" / "rules" / "b.md").write_text("global b")

        project_rules = tmp_path / "pilot" / "rules"
        project_rules.mkdir(parents=True)
        _ = (project_rules / "a.md").write_text("project a")
        _ = (project_rules / "b.md").write_text("project b")

        target: TargetConfig = {"type": "rules", "path": str(project_rules)}
        result = detect_global_contamination(target)
        names = sorted(p.name for p in result)
        assert names == ["a.md", "b.md"]

    def test_skill_with_matching_global(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        tmp_home = tmp_path / "home"
        self._with_home(monkeypatch, tmp_home)
        (tmp_home / ".claude" / "skills" / "my-skill").mkdir(parents=True)
        project_skill = tmp_path / "proj" / "skills" / "my-skill"
        project_skill.mkdir(parents=True)
        _ = (project_skill / "SKILL.md").write_text("---\nname: my-skill\n---\n")

        target: TargetConfig = {
            "type": "skill",
            "path": str(project_skill),
            "name": "my-skill",
        }
        result = detect_global_contamination(target)
        assert result == [tmp_home / ".claude" / "skills" / "my-skill"]

    def test_no_match_returns_empty(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        tmp_home = tmp_path / "home"
        self._with_home(monkeypatch, tmp_home)
        project_rule = tmp_path / "rules" / "unique.md"
        project_rule.parent.mkdir(parents=True)
        _ = project_rule.write_text("x")

        target: TargetConfig = {"type": "rules", "path": str(project_rule)}
        assert detect_global_contamination(target) == []


# ----------------------------------------------------------------------------
# isolate_global_contamination — happy path + restore guarantees
# ----------------------------------------------------------------------------


class TestIsolateContamination:
    def test_happy_path_hides_and_restores(self, tmp_path: Path) -> None:
        victim = tmp_path / "testing.md"
        _ = victim.write_text("rule content")

        with isolate_global_contamination([victim]) as hidden:
            assert not victim.exists(), "file should be hidden"
            assert len(hidden) == 1
            assert hidden[0].exists()
            assert HIDDEN_SUFFIX in hidden[0].name

        assert victim.exists(), "file must be restored on normal exit"
        assert victim.read_text() == "rule content"

    def test_restores_on_exception_within_block(self, tmp_path: Path) -> None:
        victim = tmp_path / "rule.md"
        _ = victim.write_text("x")

        with pytest.raises(RuntimeError, match="boom"):
            with isolate_global_contamination([victim]):
                assert not victim.exists()
                raise RuntimeError("boom")

        assert victim.exists(), "exception in the block must still restore"
        assert victim.read_text() == "x"

    def test_empty_list_is_noop(self) -> None:
        with isolate_global_contamination([]) as hidden:
            assert hidden == []

    def test_multiple_paths_all_restored(self, tmp_path: Path) -> None:
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        _ = a.write_text("A")
        _ = b.write_text("B")

        with isolate_global_contamination([a, b]):
            assert not a.exists() and not b.exists()

        assert a.read_text() == "A"
        assert b.read_text() == "B"

    def test_collision_leaves_source_intact(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        victim = tmp_path / "c.md"
        _ = victim.write_text("c")
        # Pre-create the exact hidden filename to simulate a stale leftover.
        stale = victim.with_name(f"{victim.name}{HIDDEN_SUFFIX}-{os.getpid()}")
        _ = stale.write_text("stale")

        with isolate_global_contamination([victim]) as hidden:
            # We could not hide it — source must still be there.
            assert victim.exists()
            assert hidden == []

        err = capsys.readouterr().err
        assert "already exists" in err
        stale.unlink()

    def test_queue_drained_after_successful_restore(self, tmp_path: Path) -> None:
        victim = tmp_path / "q.md"
        _ = victim.write_text("q")

        with isolate_global_contamination([victim]):
            pass

        # After restore, nothing for this victim should remain queued.
        assert not any(src == victim for src, _ in HIDDEN_RESTORE_QUEUE)


# ----------------------------------------------------------------------------
# Manifest write / recovery on crash
# ----------------------------------------------------------------------------


class TestManifestRecovery:
    @pytest.fixture(autouse=True)
    def _isolate_recovery_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # Redirect RECOVERY_DIR so tests don't touch the user's real ~/.pilot/.
        monkeypatch.setattr(isolation, "RECOVERY_DIR", tmp_path / "recovery")
        yield

    def test_manifest_writes_atomically(self, tmp_path: Path) -> None:
        pairs = [(tmp_path / "a", tmp_path / "a.hidden")]
        _write_manifest(pairs)
        manifest = _manifest_path(os.getpid())
        assert manifest.exists()
        data = json.loads(manifest.read_text())
        assert data["pid"] == os.getpid()
        assert len(data["pairs"]) == 1

    def test_recover_restores_from_dead_pid_manifest(
        self, tmp_path: Path
    ) -> None:
        # Simulate a crashed prior run: rename a file and write a manifest
        # with a *dead* PID so the recovery code will pick it up.
        src = tmp_path / "rule.md"
        _ = src.write_text("content")
        hidden = src.with_name(src.name + ".pilot-bench-hidden-99999")
        src.rename(hidden)

        dead_pid = 99999  # Won't be alive on any reasonable system during a test.
        isolation.RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
        manifest = isolation.RECOVERY_DIR / f"hidden-{dead_pid}.json"
        _ = manifest.write_text(
            json.dumps({"pid": dead_pid, "pairs": [[str(src), str(hidden)]]})
        )

        with patch("scripts.isolation._process_alive", return_value=False):
            restored = recover_stale_manifests()

        assert restored == 1
        assert src.exists()
        assert src.read_text() == "content"
        assert not hidden.exists()
        assert not manifest.exists(), "manifest should be cleared after recovery"

    def test_recover_skips_live_pid(self, tmp_path: Path) -> None:
        # Manifest from a live PID should NOT be touched.
        isolation.RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
        src = tmp_path / "x.md"
        hidden = tmp_path / "x.md.pilot-bench-hidden-OTHER"
        _ = hidden.write_text("still hidden")
        manifest = isolation.RECOVERY_DIR / "hidden-12345.json"
        _ = manifest.write_text(
            json.dumps({"pid": 12345, "pairs": [[str(src), str(hidden)]]})
        )

        with patch("scripts.isolation._process_alive", return_value=True):
            restored = recover_stale_manifests()

        assert restored == 0
        assert hidden.exists(), "live-PID manifest must not be touched"
        assert manifest.exists()

    def test_recover_tolerates_corrupt_manifest(self, tmp_path: Path) -> None:
        isolation.RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
        manifest = isolation.RECOVERY_DIR / "hidden-777.json"
        _ = manifest.write_text("{ not json")
        # Should not raise; corrupt manifest is skipped.
        restored = recover_stale_manifests()
        assert restored == 0

    def test_recover_when_dir_missing_returns_zero(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(isolation, "RECOVERY_DIR", tmp_path / "does-not-exist")
        assert recover_stale_manifests() == 0

    def test_manifest_is_cleared_on_clean_exit(self, tmp_path: Path) -> None:
        victim = tmp_path / "clean.md"
        _ = victim.write_text("c")

        with isolate_global_contamination([victim]):
            manifest = _manifest_path(os.getpid())
            assert manifest.exists(), "manifest should exist during the block"

        # After clean exit, manifest should be gone.
        manifest = _manifest_path(os.getpid())
        assert not manifest.exists()
        _clear_manifest()  # no-op cleanup

    def test_manifest_survives_when_restore_fails(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """If the final restore fails, the manifest must stay on disk so the
        next run can try again — the whole point of the fail-safe."""
        victim = tmp_path / "surv.md"
        _ = victim.write_text("s")

        original_rename = Path.rename
        calls: list[int] = []

        def flaky_rename(self: Path, target: Path) -> Path:
            calls.append(1)
            # First call (hide) succeeds; restore (second call back to victim) fails.
            if len(calls) >= 2 and str(target) == str(victim):
                raise OSError("disk full")
            return original_rename(self, target)

        monkeypatch.setattr(Path, "rename", flaky_rename)

        # The context manager must NOT raise — it logs the failure and leaves
        # the manifest on disk so next-run recovery can retry.
        with isolate_global_contamination([victim]):
            pass

        assert _manifest_path(os.getpid()).exists(), (
            "manifest must persist so next-run recovery can retry"
        )
        # Manually clean up the hidden leftover so the test tmp_path disposal works.
        for hidden in tmp_path.glob("surv.md.pilot-bench-hidden-*"):
            hidden.unlink()


# ----------------------------------------------------------------------------
# Process-alive helper
# ----------------------------------------------------------------------------


class TestProcessAlive:
    def test_current_pid_alive(self) -> None:
        assert _process_alive(os.getpid()) is True

    def test_zero_is_dead(self) -> None:
        assert _process_alive(0) is False

    def test_negative_is_dead(self) -> None:
        assert _process_alive(-1) is False

    def test_very_large_pid_is_dead(self) -> None:
        # Unlikely any reasonable system has PID 9999999 alive during a test.
        assert _process_alive(9999999) is False
