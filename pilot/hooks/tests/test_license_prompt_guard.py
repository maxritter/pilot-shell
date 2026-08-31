"""Inactive access blocks Pilot prompts without stopping ordinary agent work."""

from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

from pilot.hooks import license_prompt_guard


def _run(home: Path, payload: dict, capsys) -> dict:
    with (
        patch("pilot.hooks.license_prompt_guard.Path.home", return_value=home),
        patch("pilot.hooks.license_prompt_guard.sys.stdin", io.StringIO(json.dumps(payload))),
    ):
        assert license_prompt_guard.main() == 0
    return json.loads(capsys.readouterr().out)


def test_explicit_pilot_skill_is_blocked_but_not_the_session(tmp_path: Path, capsys) -> None:
    (tmp_path / ".pilot").mkdir()
    (tmp_path / ".pilot" / ".license-access.json").write_text('{"state":"deactivated"}')

    output = _run(
        tmp_path,
        {"hook_event_name": "UserPromptSubmit", "prompt": "/spec add account recovery"},
        capsys,
    )

    assert output["decision"] == "block"
    assert "workflow is unavailable" in output["reason"]
    assert "remain available for non-Pilot work" in output["reason"]
    assert "continue" not in output


def test_direct_skill_expansion_is_blocked_when_inactive(tmp_path: Path, capsys) -> None:
    (tmp_path / ".pilot").mkdir()

    output = _run(
        tmp_path,
        {"hook_event_name": "UserPromptExpansion", "prompt": "expanded skill body"},
        capsys,
    )

    assert output["decision"] == "block"


def test_ordinary_prompt_continues_with_inactive_context(tmp_path: Path, capsys) -> None:
    (tmp_path / ".pilot").mkdir()

    output = _run(
        tmp_path,
        {"hook_event_name": "UserPromptSubmit", "prompt": "Explain this stack trace"},
        capsys,
    )

    assert "decision" not in output
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "Native agent capabilities remain available" in output["hookSpecificOutput"]["additionalContext"]


def test_active_license_allows_pilot_prompt(tmp_path: Path, capsys) -> None:
    pilot_dir = tmp_path / ".pilot"
    pilot_dir.mkdir()
    (pilot_dir / ".license").write_text("signed")

    assert _run(tmp_path, {"prompt": "$build finish this"}, capsys) == {"continue": True}
