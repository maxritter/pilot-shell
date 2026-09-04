"""Tests for config_dir_guard.py - the session-start Claude-profile drift warning."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from config_dir_guard import main, record_path, resolve_warning  # noqa: E402


class TestResolveWarning:
    """Pure resolution logic: recorded dir vs the dir serving this session."""

    def test_silent_when_no_record(self, tmp_path: Path) -> None:
        """First run after an upgrade has no record - stay quiet, do not guess."""
        assert resolve_warning(tmp_path / "missing", tmp_path / ".claude") is None

    def test_silent_when_dirs_match(self, tmp_path: Path) -> None:
        record = tmp_path / "record"
        claude = tmp_path / ".claude"
        claude.mkdir()
        record.write_text(str(claude), encoding="utf-8")

        assert resolve_warning(record, claude) is None

    def test_silent_when_dirs_match_via_trailing_slash(self, tmp_path: Path) -> None:
        """A trailing slash is the same directory - must not warn."""
        record = tmp_path / "record"
        claude = tmp_path / ".claude"
        claude.mkdir()
        record.write_text(str(claude) + "/", encoding="utf-8")

        assert resolve_warning(record, claude) is None

    def test_warns_when_dirs_differ(self, tmp_path: Path) -> None:
        record = tmp_path / "record"
        installed = tmp_path / ".claude_work"
        installed.mkdir()
        active = tmp_path / ".claude"
        active.mkdir()
        record.write_text(str(installed), encoding="utf-8")

        warning = resolve_warning(record, active)

        assert warning is not None
        assert str(installed) in warning
        assert str(active) in warning

    def test_silent_when_active_dir_is_none(self, tmp_path: Path) -> None:
        """An invalid CLAUDE_CONFIG_DIR is a separate problem, not drift."""
        record = tmp_path / "record"
        record.write_text(str(tmp_path / ".claude_work"), encoding="utf-8")

        assert resolve_warning(record, None) is None

    def test_silent_on_unreadable_record(self, tmp_path: Path) -> None:
        record = tmp_path / "record"
        record.mkdir()  # a directory, not a file - read must not raise

        assert resolve_warning(record, tmp_path / ".claude") is None


class TestRecordPath:
    def test_writes_resolved_dir(self, tmp_path: Path) -> None:
        record = tmp_path / "state" / "last-claude-config-dir"
        claude = tmp_path / ".claude_work"
        claude.mkdir()

        record_path(record, claude)

        assert record.read_text(encoding="utf-8").strip() == str(claude)

    def test_never_raises_on_unwritable_parent(self, tmp_path: Path) -> None:
        blocker = tmp_path / "blocked"
        blocker.write_text("not a directory", encoding="utf-8")

        record_path(blocker / "state" / "rec", tmp_path / ".claude")


class TestMain:
    def test_emits_nothing_when_no_drift(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "cli")
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
        (tmp_path / ".claude").mkdir()
        state = tmp_path / ".pilot" / "state"
        state.mkdir(parents=True)
        (state / "last-claude-config-dir").write_text(str(tmp_path / ".claude"), encoding="utf-8")

        main()

        assert capsys.readouterr().out.strip() == ""

    def test_emits_warning_on_drift(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "cli")
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
        (tmp_path / ".claude").mkdir()
        state = tmp_path / ".pilot" / "state"
        state.mkdir(parents=True)
        (state / "last-claude-config-dir").write_text(str(tmp_path / ".claude_work"), encoding="utf-8")

        main()

        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["continue"] is True
        assert payload["suppressOutput"] is True
        assert "systemMessage" not in payload
        assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
        context = payload["hookSpecificOutput"]["additionalContext"]
        assert ".claude_work" in context
        assert "Show the following to the user" not in context

    def test_never_raises_on_malformed_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "cli")
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
        with patch("config_dir_guard.resolve_warning", side_effect=OSError("boom")):
            main()

        assert capsys.readouterr().out.strip() == ""

    def test_skips_when_not_claude_code(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.delenv("CLAUDE_CODE_ENTRYPOINT", raising=False)
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

        main()

        assert capsys.readouterr().out.strip() == ""
