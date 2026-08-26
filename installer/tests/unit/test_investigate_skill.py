"""Cross-agent packaging contract for Pilot's investigate skill."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from installer.skill_builder import build_skill_md, canonicalize
from installer.steps.codex_files import (
    _CODEX_SKILL_DESCRIPTIONS,
    CodexFilesStep,
    build_codex_skill_md,
    build_codex_skill_openai_yaml,
)

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = REPO_ROOT / "pilot" / "skills" / "investigate"
HOOKS_DIR = REPO_ROOT / "pilot" / "hooks"
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

import codex_skill_sync  # noqa: E402


def _frontmatter(content: str) -> dict[str, object]:
    assert content.startswith("---\n")
    end = content.index("\n---", 4)
    metadata = yaml.safe_load(content[4:end])
    assert isinstance(metadata, dict)
    return metadata


def test_claude_artifact_is_manual_read_only_and_complete() -> None:
    content = build_skill_md(SKILL_DIR)
    manifest = json.loads((SKILL_DIR / "manifest.json").read_text())
    metadata = _frontmatter(content)

    assert metadata["name"] == "investigate"
    assert metadata["user-invocable"] is True
    assert metadata["disable-model-invocation"] is True
    assert "read-only" in str(metadata["description"])
    assert manifest["delivery"] == "bundled"
    assert "## Required phase resources" not in content
    for step in manifest["steps"]:
        assert canonicalize((SKILL_DIR / step["file"]).read_text()) in content
    assert "do not create a report file" in content
    assert "Claim only recorded work" in content

    challenge = (SKILL_DIR / "steps" / "03-challenge.md").read_text()
    report = (SKILL_DIR / "steps" / "04-report.md").read_text()
    assert "every execution claim maps to a real result" in challenge
    assert "**Runtime check:**" in report
    assert "No readiness, process, or evidence-status preamble" in report
    assert "opening paragraph branch-complete" in report


def test_manifest_exposes_discriminating_investigation_evals() -> None:
    manifest = json.loads((SKILL_DIR / "manifest.json").read_text())
    assert manifest["evals"] == "tests/evals.json"

    payload = json.loads((SKILL_DIR / manifest["evals"]).read_text())
    assert payload["target"] == {
        "type": "skill",
        "path": "pilot/skills/investigate",
        "name": "investigate",
    }
    assert [case["name"] for case in payload["evals"]] == [
        "branch-complete-active-path",
        "test-is-not-runtime-proof",
        "installed-artifact-controls",
        "challenge-false-premise",
    ]
    assert all(len(case["expectations"]) == 3 for case in payload["evals"])
    assert all(case["prompt"].startswith("$investigate ") for case in payload["evals"])
    assert all("self-contained read-only evidence packet" in case["prompt"] for case in payload["evals"])
    assert all("do not run target-repository commands or change files" in case["prompt"] for case in payload["evals"])
    assert all("follow the loaded skill instructions" in case["prompt"].lower() for case in payload["evals"])


def test_codex_generators_match_and_keep_explicit_invocation() -> None:
    installer_skill = build_codex_skill_md(SKILL_DIR)
    hook_skill = codex_skill_sync._build_codex_skill(SKILL_DIR)
    installer_metadata = build_codex_skill_openai_yaml(SKILL_DIR)
    hook_metadata = codex_skill_sync._build_openai_yaml(SKILL_DIR)

    assert hook_skill is not None
    assert hook_metadata is not None
    assert installer_skill == hook_skill
    assert installer_metadata == hook_metadata
    assert "$investigate" in installer_skill
    assert "/investigate" not in installer_skill
    assert "disable-model-invocation" not in _frontmatter(installer_skill)
    assert yaml.safe_load(installer_metadata)["policy"]["allow_implicit_invocation"] is False


def test_codex_allowlists_and_descriptions_stay_in_sync() -> None:
    assert "investigate" in CodexFilesStep._CODEX_SUPPORTED_SKILLS
    assert "investigate" in CodexFilesStep._CODEX_EXPLICIT_ONLY_SKILLS
    assert "investigate" in codex_skill_sync._SUPPORTED_SKILLS
    assert "investigate" in codex_skill_sync._EXPLICIT_ONLY_SKILLS
    assert _CODEX_SKILL_DESCRIPTIONS["investigate"] == codex_skill_sync._SKILL_DESCRIPTIONS["investigate"]


def test_local_installer_writes_runtime_codex_artifacts(tmp_path: Path) -> None:
    ctx = MagicMock()
    ctx.local_mode = True
    ctx.local_repo_dir = REPO_ROOT
    ctx.ui = None

    with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
        written = CodexFilesStep()._install_codex_skills(ctx)

    installed = tmp_path / ".agents" / "skills" / "investigate"
    assert written >= 1
    assert (installed / "SKILL.md").read_text() == build_codex_skill_md(SKILL_DIR)
    assert (installed / "agents" / "openai.yaml").read_text() == build_codex_skill_openai_yaml(SKILL_DIR)
    assert (installed / ".pilot-resources.json").is_file()
    assert not (installed / "steps").exists()
    assert not (installed / "manifest.json").exists()
    assert not (installed / "orchestrator.md").exists()


def test_local_installer_preserves_unowned_same_name_codex_skill(tmp_path: Path) -> None:
    installed = tmp_path / ".agents" / "skills" / "investigate"
    installed.mkdir(parents=True)
    (installed / "SKILL.md").write_text("user-owned investigate\n")
    ctx = MagicMock()
    ctx.local_mode = True
    ctx.local_repo_dir = REPO_ROOT
    ctx.ui = MagicMock()

    with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
        CodexFilesStep()._install_codex_skills(ctx)

    assert (installed / "SKILL.md").read_text() == "user-owned investigate\n"
    assert not (installed / ".pilot-resources.json").exists()
    assert any("unowned" in str(call.args[0]) for call in ctx.ui.warning.call_args_list)


def test_session_sync_preserves_unowned_same_name_codex_skill(tmp_path: Path) -> None:
    source = tmp_path / ".pilot" / "skills" / "investigate"
    shutil.copytree(SKILL_DIR, source)
    installed = tmp_path / ".agents" / "skills" / "investigate"
    installed.mkdir(parents=True)
    (installed / "SKILL.md").write_text("user-owned investigate\n")

    with patch("codex_skill_sync.Path.home", return_value=tmp_path):
        built, failed = codex_skill_sync._sync_codex_skills()

    assert built == 0
    assert failed == 1
    assert (installed / "SKILL.md").read_text() == "user-owned investigate\n"
    assert not (installed / ".pilot-resources.json").exists()


def test_license_cleanup_preserves_unowned_same_name_codex_skill(tmp_path: Path) -> None:
    installed = tmp_path / ".agents" / "skills" / "investigate"
    installed.mkdir(parents=True)
    (installed / "SKILL.md").write_text("user-owned investigate\n")

    with patch("codex_skill_sync.Path.home", return_value=tmp_path):
        removed = codex_skill_sync._remove_codex_skills()

    assert removed == 0
    assert (installed / "SKILL.md").read_text() == "user-owned investigate\n"
