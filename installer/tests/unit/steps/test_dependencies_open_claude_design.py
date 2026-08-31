"""Tests for Pilot's external Open Claude Design dependency."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest


def _doctor_payload(*, version: str = "1.1.0") -> str:
    skill_status = {
        "open-claude-design-quality": True,
        "open-claude-ui-design": True,
        "open-claude-design-system": True,
        "open-claude-ui-review": True,
        "open-claude-design": True,
    }
    return json.dumps(
        {
            "package_version": version,
            "agent_skills": {"ready": True, "skills": skill_status},
        }
    )


class FakeReleaseResponse:
    def __init__(self, body: bytes, *, url: str) -> None:
        self.body = body
        self.url = url
        self.status = 200
        self.headers = {"Content-Length": str(len(body))}

    def read(self, amount: int | None = None) -> bytes:
        return self.body if amount is None else self.body[:amount]

    def geturl(self) -> str:
        return self.url

    def __enter__(self) -> FakeReleaseResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


@patch("installer.steps.dependencies.command_exists", return_value=False)
@patch("installer.steps.dependencies.is_codex_installed", return_value=True)
@patch("installer.steps.dependencies.is_claude_installed", return_value=True)
@patch("installer.steps.dependencies._open_claude_design_source")
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

    manifest_get.return_value = SimpleNamespace(version="live-github-release", sha256="0" * 64)
    _source.side_effect = lambda _ctx, destination: destination / "open_claude_design-1.2.3-py3-none-any.whl"
    which.side_effect = lambda command: f"/usr/local/bin/{command}"
    preflight = SimpleNamespace(returncode=0, stdout="sync help", stderr="")
    installed = SimpleNamespace(returncode=0, stdout="", stderr="")
    materialized = SimpleNamespace(returncode=0, stdout="[]", stderr="")
    compatible = SimpleNamespace(returncode=0, stdout="sync help", stderr="")
    verified = SimpleNamespace(returncode=0, stdout=_doctor_payload(version="1.2.3"), stderr="")
    run.side_effect = [preflight, installed, materialized, compatible, verified]
    ctx = SimpleNamespace(project_dir=tmp_path, local_mode=True, local_repo_dir=tmp_path / "pilot-shell")
    monkeypatch.setenv("UV_CONFIG_FILE", str(tmp_path / "untrusted-uv.toml"))
    monkeypatch.setenv("UV_INDEX", "https://packages.invalid/simple")

    assert install_open_claude_design(cast(Any, ctx)) is True

    assert run.call_args_list[0].args[0][:5] == [
        "/usr/local/bin/uv",
        "tool",
        "run",
        "--no-config",
        "--from",
    ]
    assert run.call_args_list[0].args[0][-3:] == ["open-claude-design", "sync", "--help"]
    assert run.call_args_list[1].args[0][:-1] == [
        "/usr/local/bin/uv",
        "tool",
        "install",
        "--no-config",
        "--default-index",
        "https://pypi.org/simple",
        "--no-sources",
        "--force",
    ]
    uv_environment = run.call_args_list[1].kwargs["env"]
    assert uv_environment["UV_NO_CONFIG"] == "1"
    assert uv_environment["UV_DEFAULT_INDEX"] == "https://pypi.org/simple"
    assert "UV_CONFIG_FILE" not in uv_environment
    assert "UV_INDEX" not in uv_environment
    assert run.call_args_list[2].args[0] == [
        "/usr/local/bin/open-claude-design",
        "install",
        "--agents=claude-code,codex",
        "--scope=global",
        "--yes",
        "--json",
    ]
    assert run.call_args_list[3].args[0] == [
        "/usr/local/bin/open-claude-design",
        "sync",
        "--help",
    ]
    assert run.call_args_list[4].args[0] == [
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
@patch("installer.steps.dependencies._open_claude_design_source")
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

    manifest_get.return_value = SimpleNamespace(version="live-github-release", sha256="0" * 64)
    _source.side_effect = lambda _ctx, destination: destination / "open_claude_design-1.2.3-py3-none-any.whl"
    which.side_effect = lambda command: f"/usr/local/bin/{command}"
    run.side_effect = [
        SimpleNamespace(returncode=0, stdout="sync help", stderr=""),
        SimpleNamespace(returncode=0, stdout="", stderr=""),
        SimpleNamespace(returncode=0, stdout="[]", stderr=""),
        SimpleNamespace(returncode=0, stdout="sync help", stderr=""),
        SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {
                    "package_version": "1.2.3",
                    "agent_skills": {
                        "ready": True,
                        "skills": {"open-claude-design": False},
                    },
                }
            ),
            stderr="",
        ),
    ]
    ctx = SimpleNamespace(project_dir=tmp_path, local_mode=True, local_repo_dir=tmp_path / "pilot-shell")

    assert install_open_claude_design(cast(Any, ctx)) is False


@patch("installer.steps.dependencies.command_exists", return_value=True)
@patch("installer.steps.dependencies.is_codex_installed", return_value=True)
@patch("installer.steps.dependencies.is_claude_installed", return_value=False)
@patch("installer.steps.dependencies._open_claude_design_source")
@patch("installer.steps.dependencies.shutil.which", return_value="/usr/local/bin/uv")
@patch("installer.steps.dependencies.subprocess.run")
def test_incompatible_latest_release_is_rejected_before_replacing_installed_tool(
    run: MagicMock,
    _which: MagicMock,
    source: MagicMock,
    _claude: MagicMock,
    _codex: MagicMock,
    _exists: MagicMock,
    tmp_path: Path,
) -> None:
    from installer.steps.dependencies import install_open_claude_design

    source.side_effect = lambda _ctx, destination: destination / "open_claude_design-2.0.0-py3-none-any.whl"
    run.return_value = SimpleNamespace(returncode=1, stdout="", stderr="sync command missing")
    ctx = SimpleNamespace(project_dir=tmp_path, local_mode=False, local_repo_dir=None)

    assert install_open_claude_design(cast(Any, ctx)) is False
    assert run.call_count == 1
    assert run.call_args.args[0][1:4] == ["tool", "run", "--no-config"]


@patch("installer.steps.dependencies.manifest_get")
@patch("installer.steps.dependencies.urllib.request.urlopen")
def test_latest_release_resolver_verifies_release_local_checksum(
    urlopen: MagicMock,
    manifest_get: MagicMock,
    tmp_path: Path,
) -> None:
    from installer.steps.dependencies import _download_latest_open_claude_design_wheel

    filename = "open_claude_design-1.4.0-py3-none-any.whl"
    wheel = b"synthetic wheel bytes"
    digest = hashlib.sha256(wheel).hexdigest()
    checksum_url = "https://github.com/maxritter/open-claude-design/releases/latest/download/SHA256SUMS"
    manifest_get.return_value = SimpleNamespace(source_url=checksum_url)
    urlopen.side_effect = [
        FakeReleaseResponse(
            f"{digest}  {filename}\n".encode(),
            url="https://release-assets.githubusercontent.com/latest/SHA256SUMS",
        ),
        FakeReleaseResponse(
            wheel,
            url=f"https://release-assets.githubusercontent.com/latest/{filename}",
        ),
    ]

    resolved = _download_latest_open_claude_design_wheel(tmp_path)

    assert resolved is not None
    assert resolved == tmp_path / filename
    assert resolved.read_bytes() == wheel
    assert urlopen.call_count == 2


@patch("installer.steps.dependencies.manifest_get")
@patch("installer.steps.dependencies.urllib.request.urlopen")
def test_latest_release_resolver_rejects_tampered_wheel(
    urlopen: MagicMock,
    manifest_get: MagicMock,
    tmp_path: Path,
) -> None:
    from installer.steps.dependencies import _download_latest_open_claude_design_wheel

    filename = "open_claude_design-1.4.0-py3-none-any.whl"
    checksum_url = "https://github.com/maxritter/open-claude-design/releases/latest/download/SHA256SUMS"
    manifest_get.return_value = SimpleNamespace(source_url=checksum_url)
    urlopen.side_effect = [
        FakeReleaseResponse(
            f"{'0' * 64}  {filename}\n".encode(),
            url="https://release-assets.githubusercontent.com/latest/SHA256SUMS",
        ),
        FakeReleaseResponse(
            b"tampered wheel",
            url=f"https://release-assets.githubusercontent.com/latest/{filename}",
        ),
    ]

    assert _download_latest_open_claude_design_wheel(tmp_path) is None
    assert not (tmp_path / filename).exists()


@patch("installer.steps.dependencies.urllib.request.urlopen")
def test_latest_release_downloader_rejects_untrusted_redirect(urlopen: MagicMock) -> None:
    from installer.steps.dependencies import _download_open_claude_design_bytes

    urlopen.return_value = FakeReleaseResponse(b"payload", url="https://downloads.invalid/payload")

    assert (
        _download_open_claude_design_bytes(
            "https://github.com/maxritter/open-claude-design/releases/latest/download/SHA256SUMS",
            maximum_bytes=1024,
        )
        is None
    )


def test_claude_code_tips_surface_open_claude_design() -> None:
    settings_path = Path(__file__).parents[4] / "pilot" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    tips = settings["spinnerTipsOverride"]["tips"]

    assert any("Open Claude Design" in tip and "visual workspace" in tip for tip in tips)
