"""Tests for Pilot's external Open Claude Design dependency."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest


def _doctor_payload() -> str:
    skill_status = {
        "open-claude-design-quality": True,
        "open-claude-ui-design": True,
        "open-claude-design-system": True,
        "open-claude-ui-review": True,
        "open-claude-design": True,
    }
    return json.dumps(
        {
            "agent_skills": {"ready": True, "skills": skill_status}
        }
    )


@patch("installer.steps.dependencies.command_exists", return_value=False)
@patch("installer.steps.dependencies.is_codex_installed", return_value=True)
@patch("installer.steps.dependencies.is_claude_installed", return_value=True)
@patch("installer.steps.dependencies._open_claude_design_source", return_value=True)
@patch("installer.steps.dependencies.shutil.which")
@patch("installer.steps.dependencies.subprocess.run")
@patch("installer.steps.dependencies.manifest_get")
def test_installs_materializes_and_verifies_external_design_pack(
    manifest_get: MagicMock,
    run: MagicMock,
    which: MagicMock,
    _source: MagicMock,
    _claude: MagicMock,
    _codex: MagicMock,
    _exists: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from installer.steps.dependencies import install_open_claude_design

    manifest_get.return_value = SimpleNamespace(version="1.0.0", sha256="0" * 64)
    which.side_effect = lambda command: f"/usr/local/bin/{command}"
    installed = SimpleNamespace(returncode=0, stdout="", stderr="")
    materialized = SimpleNamespace(returncode=0, stdout="[]", stderr="")
    verified = SimpleNamespace(returncode=0, stdout=_doctor_payload(), stderr="")
    run.side_effect = [installed, materialized, verified]
    ctx = SimpleNamespace(project_dir=tmp_path, local_mode=True, local_repo_dir=tmp_path / "pilot-shell")
    monkeypatch.setenv("UV_CONFIG_FILE", str(tmp_path / "untrusted-uv.toml"))
    monkeypatch.setenv("UV_INDEX", "https://packages.invalid/simple")

    assert install_open_claude_design(cast(Any, ctx)) is True

    assert run.call_args_list[0].args[0][:-1] == [
        "/usr/local/bin/uv",
        "tool",
        "install",
        "--no-config",
        "--default-index",
        "https://pypi.org/simple",
        "--no-sources",
        "--force",
    ]
    uv_environment = run.call_args_list[0].kwargs["env"]
    assert uv_environment["UV_NO_CONFIG"] == "1"
    assert uv_environment["UV_DEFAULT_INDEX"] == "https://pypi.org/simple"
    assert "UV_CONFIG_FILE" not in uv_environment
    assert "UV_INDEX" not in uv_environment
    assert run.call_args_list[1].args[0] == [
        "/usr/local/bin/open-claude-design",
        "install",
        "--agents=claude-code,codex",
        "--scope=global",
        "--yes",
        "--json",
    ]
    assert run.call_args_list[2].args[0] == [
        "/usr/local/bin/open-claude-design",
        "doctor",
        "--agents=claude-code,codex",
        "--scope=global",
        "--offline",
        "--json",
    ]


@patch("installer.steps.dependencies.command_exists", return_value=True)
@patch("installer.steps.dependencies.is_codex_installed", return_value=True)
@patch("installer.steps.dependencies.is_claude_installed", return_value=False)
@patch("installer.steps.dependencies._open_claude_design_source", return_value=True)
@patch("installer.steps.dependencies.shutil.which")
@patch("installer.steps.dependencies.subprocess.run")
@patch("installer.steps.dependencies.manifest_get")
def test_fails_when_installed_artifact_is_incomplete(
    manifest_get: MagicMock,
    run: MagicMock,
    which: MagicMock,
    _source: MagicMock,
    _claude: MagicMock,
    _codex: MagicMock,
    _exists: MagicMock,
    tmp_path: Path,
) -> None:
    from installer.steps.dependencies import install_open_claude_design

    manifest_get.return_value = SimpleNamespace(version="1.0.0", sha256="0" * 64)
    which.side_effect = lambda command: f"/usr/local/bin/{command}"
    run.side_effect = [
        SimpleNamespace(returncode=0, stdout="", stderr=""),
        SimpleNamespace(returncode=0, stdout="[]", stderr=""),
        SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {
                    "agent_skills": {
                        "ready": True,
                        "skills": {"open-claude-design": False},
                    }
                }
            ),
            stderr="",
        ),
    ]
    ctx = SimpleNamespace(project_dir=tmp_path, local_mode=True, local_repo_dir=tmp_path / "pilot-shell")

    assert install_open_claude_design(cast(Any, ctx)) is False


def test_claude_code_tips_surface_open_claude_design() -> None:
    settings_path = Path(__file__).parents[4] / "pilot" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    tips = settings["spinnerTipsOverride"]["tips"]

    assert any("Open Claude Design" in tip and "visual workspace" in tip for tip in tips)
