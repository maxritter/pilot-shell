"""The license notice disables Pilot without blocking the host agent."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from pilot.hooks import license_check


def _run_with(payload: dict, capsys) -> dict:
    result = MagicMock(stdout=json.dumps(payload))
    with (
        patch.object(Path, "is_file", return_value=True),
        patch.object(license_check.subprocess, "run", return_value=result),
    ):
        license_check.main()
    return json.loads(capsys.readouterr().out)


def test_deactivated_license_keeps_claude_running_and_explains_choices(capsys) -> None:
    output = _run_with(
        {"valid": False, "state": "deactivated", "tier": "team"},
        capsys,
    )

    assert output["continue"] is True
    assert "deactivated" in output["systemMessage"].lower()
    assert "Claude Code and Codex remain usable" in output["systemMessage"]
    assert "pilot activate <LICENSE_KEY>" in output["systemMessage"]
    assert "uninstall" in output["systemMessage"].lower()
    assert "stopReason" not in output


def test_active_license_remains_quiet(capsys) -> None:
    assert _run_with({"valid": True, "state": "active", "tier": "solo"}, capsys) == {
        "continue": True,
    }
