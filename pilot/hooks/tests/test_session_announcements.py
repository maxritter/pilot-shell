"""Tests for session_announcements hook -- CC-only SessionStart one-time
announcements, re-injected until the user acknowledges (ack sentinel)."""

from __future__ import annotations

from pathlib import Path

from session_announcements import (
    ANNOUNCEMENTS,
    _ack_path,
    pending,
    render_context,
)


class TestRegistry:
    def test_has_model_switching_modes_announcement(self) -> None:
        entry = next((a for a in ANNOUNCEMENTS if a["id"] == "model-switching-modes"), None)
        assert entry is not None
        # Names all three modes, the new default, and the migration mapping.
        assert "Automated (default)" in entry["message"]
        assert "Manual" in entry["message"]
        assert "Off" in entry["message"]
        assert "no longer touches those aliases" in entry["message"]

    def test_has_opus_5_announcement(self) -> None:
        entry = next((a for a in ANNOUNCEMENTS if a["id"] == "opus-5"), None)
        assert entry is not None
        # Names the new opusplan pair and the surviving 200K boundary condition.
        assert "Opus 5" in entry["message"]
        assert "Sonnet 5" in entry["message"]
        assert "200K" in entry["message"]

    def test_model_switching_announcement_drops_stale_preflight_claim(self) -> None:
        """The 'new pre-flight check' wording described a then-new feature; it now
        reads as a promise to fresh installs. The check still exists, but the
        announcement should not advertise it as new."""
        entry = next(a for a in ANNOUNCEMENTS if a["id"] == "model-switching-modes")
        assert "A new" not in entry["message"]

    def test_stale_pin_era_announcements_pruned(self) -> None:
        ids = [a["id"] for a in ANNOUNCEMENTS]
        for stale in (
            "automated-model-switching",
            "model-switching-1m-planning",
            "configurable-plan-exec-models",
            "fable-5-support",
            "opusplan-sonnet-default",
        ):
            assert stale not in ids

    def test_every_announcement_has_id_and_message(self) -> None:
        for a in ANNOUNCEMENTS:
            assert a["id"] and isinstance(a["id"], str)
            assert a["message"] and isinstance(a["message"], str)


class TestPending:
    def test_all_pending_when_no_ack_sentinels(self, tmp_path: Path) -> None:
        result = pending(tmp_path, ANNOUNCEMENTS)
        assert len(result) == len(ANNOUNCEMENTS)

    def test_acked_announcement_excluded(self, tmp_path: Path) -> None:
        _ack_path("automated-model-switching", tmp_path).touch()
        result = pending(tmp_path, ANNOUNCEMENTS)
        assert all(a["id"] != "automated-model-switching" for a in result)

    def test_custom_registry_all_acked_returns_empty(self, tmp_path: Path) -> None:
        reg = [{"id": "x", "message": "hello"}]
        _ack_path("x", tmp_path).touch()
        assert pending(tmp_path, reg) == []

    def test_ack_path_under_pilot_dir(self, tmp_path: Path) -> None:
        p = _ack_path("foo", tmp_path)
        assert p == tmp_path / ".announce-foo-ack"


class TestRenderContext:
    def test_includes_message(self) -> None:
        reg = [{"id": "x", "message": "BIG NEWS"}]
        ctx = render_context(reg)
        assert "BIG NEWS" in ctx
        # Ack is handled by the hook itself -- no touch instruction needed.
        assert "touch" not in ctx
        # Must instruct display-only, not interactive acknowledgment.
        assert "text output" in ctx

    def test_empty_pending_returns_empty_string(self) -> None:
        assert render_context([]) == ""
