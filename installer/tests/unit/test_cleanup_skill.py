"""Cross-agent packaging contract for Pilot's report-only cleanup skill."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from installer.skill_builder import build_skill_md, canonicalize, load_manifest
from installer.steps.codex_files import (
    _CODEX_SKILL_DESCRIPTIONS,
    CodexFilesStep,
    build_codex_skill_md,
    build_codex_skill_openai_yaml,
)

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = REPO_ROOT / "pilot" / "skills" / "cleanup"
SCRIPT = SKILL_DIR / "scripts" / "codegraph-candidates.mjs"
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


def _seed_10_7_progressive_codex_install(root: Path) -> Path:
    installed = root / ".agents" / "skills" / "cleanup"
    step_files = [step["file"] for step in load_manifest(SKILL_DIR / "manifest.json")["steps"]]
    for relative in step_files:
        path = installed / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"10.7 progressive resource: {relative}\n")
    (installed / "SKILL.md").write_text("## Required phase resources\n\nRead `steps/01-scope.md` completely.\n")
    (installed / ".pilot-resources.json").write_text(
        json.dumps({"files": step_files, "directories": ["steps"]}, indent=2) + "\n"
    )
    return installed


def test_manifest_and_claude_artifact_are_explicit_bundled_and_report_only() -> None:
    manifest = load_manifest(SKILL_DIR / "manifest.json")
    content = build_skill_md(SKILL_DIR)
    metadata = _frontmatter(content)

    assert manifest["delivery"] == "bundled"
    assert manifest["invocation"] == "explicit"
    assert manifest["evals"] == "tests/evals.json"
    assert not manifest["platform"]["codex"]["description"].casefold().startswith("use only")
    assert "explicit /cleanup workflow" in manifest["platform"]["codex"]["description"]
    assert metadata["name"] == "cleanup"
    assert metadata["user-invocable"] is True
    assert metadata["disable-model-invocation"] is True
    assert "report-only" in str(metadata["description"]).lower()
    assert "Project-native analyzers nominate candidates" in content
    assert "likely removable" in content
    assert "test-supported production code" in content
    assert "scripts/codegraph-candidates.mjs" in content
    for step in manifest["steps"]:
        assert canonicalize((SKILL_DIR / step["file"]).read_text()) in content


def test_cleanup_evals_are_self_contained_and_cover_four_safety_cases() -> None:
    payload = json.loads((SKILL_DIR / "tests" / "evals.json").read_text())

    assert payload["target"] == {
        "type": "skill",
        "path": "pilot/skills/cleanup",
        "name": "cleanup",
    }
    assert [case["name"] for case in payload["evals"]] == [
        "private-unused-two-signals",
        "public-api-boundary-blocks-removal",
        "dynamic-registration-false-positive",
        "test-only-is-separate",
    ]
    assert all(len(case["expectations"]) == 3 for case in payload["evals"])
    assert all(case["prompt"].startswith("$cleanup ") for case in payload["evals"])
    assert all("self-contained read-only evidence packet" in case["prompt"] for case in payload["evals"])
    assert all("do not run commands or change files" in case["prompt"] for case in payload["evals"])
    expectation_text = "\n".join(expectation for case in payload["evals"] for expectation in case["expectations"])
    for label in (
        "Likely removable",
        "Needs boundary review",
        "Test-supported production code",
        "Test-only candidate",
        "Referenced / false positive",
        "Unresolved",
    ):
        assert label in expectation_text


def test_codex_generators_match_and_keep_cleanup_explicit() -> None:
    installer_skill = build_codex_skill_md(SKILL_DIR)
    hook_skill = codex_skill_sync._build_codex_skill(SKILL_DIR)
    installer_metadata = build_codex_skill_openai_yaml(SKILL_DIR)
    hook_metadata = codex_skill_sync._build_openai_yaml(SKILL_DIR)

    assert hook_skill is not None
    assert hook_metadata is not None
    assert installer_skill == hook_skill
    assert installer_metadata == hook_metadata
    assert "$cleanup" in installer_skill
    assert "/cleanup" not in installer_skill
    assert "disable-model-invocation" not in _frontmatter(installer_skill)
    parsed_metadata = yaml.safe_load(installer_metadata)
    assert parsed_metadata["interface"]["short_description"] == "Report dead-code candidates without changing code"
    assert parsed_metadata["policy"]["allow_implicit_invocation"] is False


def test_codex_registries_and_routing_catalog_include_cleanup() -> None:
    assert "cleanup" in CodexFilesStep._CODEX_SUPPORTED_SKILLS
    assert "cleanup" in CodexFilesStep._CODEX_EXPLICIT_ONLY_SKILLS
    assert "cleanup" in codex_skill_sync._SUPPORTED_SKILLS
    assert "cleanup" in codex_skill_sync._EXPLICIT_ONLY_SKILLS
    assert "cleanup" in codex_skill_sync._PILOT_SKILL_NAMES
    assert _CODEX_SKILL_DESCRIPTIONS["cleanup"] == codex_skill_sync._SKILL_DESCRIPTIONS["cleanup"]

    catalog = json.loads((REPO_ROOT / "benchmarks" / "skill-routing" / "catalog.json").read_text())
    cleanup = next(skill for skill in catalog["skills"] if skill["id"] == "cleanup")
    assert cleanup["invocation"] == "explicit"
    assert all("cleanup" in case["prompt"] for case in cleanup["positives"])
    assert all(case["owner"] == "direct" for case in cleanup["negatives"])


def test_local_installer_embeds_steps_and_packages_read_only_script(tmp_path: Path) -> None:
    ctx = MagicMock(local_mode=True, local_repo_dir=REPO_ROOT, ui=None)

    with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
        written = CodexFilesStep()._install_codex_skills(ctx)

    installed = tmp_path / ".agents" / "skills" / "cleanup"
    assert written >= 1
    assert (installed / "SKILL.md").read_text() == build_codex_skill_md(SKILL_DIR)
    assert (installed / "agents" / "openai.yaml").read_text() == build_codex_skill_openai_yaml(SKILL_DIR)
    assert (installed / ".pilot-resources.json").is_file()
    assert not (installed / "steps").exists()
    installed_script = installed / "scripts" / "codegraph-candidates.mjs"
    assert installed_script.read_bytes() == SCRIPT.read_bytes()
    assert os.access(installed_script, os.X_OK)
    assert not (installed / "manifest.json").exists()
    assert not (installed / "orchestrator.md").exists()
    assert not (installed / "tests").exists()


def test_session_sync_embeds_cleanup_steps_and_packages_script(tmp_path: Path) -> None:
    source = tmp_path / ".pilot" / "skills" / "cleanup"
    shutil.copytree(SKILL_DIR, source)

    with patch("codex_skill_sync.Path.home", return_value=tmp_path):
        built, failed = codex_skill_sync._sync_codex_skills()

    installed = tmp_path / ".agents" / "skills" / "cleanup"
    assert (built, failed) == (1, 0)
    assert not (installed / "steps").exists()
    installed_script = installed / "scripts" / "codegraph-candidates.mjs"
    assert installed_script.read_bytes() == SCRIPT.read_bytes()
    assert os.access(installed_script, os.X_OK)
    resources = json.loads((installed / ".pilot-resources.json").read_text())
    assert "scripts/codegraph-candidates.mjs" in resources["files"]
    assert all(not path.startswith("steps/") for path in resources["files"])


@pytest.mark.parametrize("runtime", ["installer", "session-sync"])
def test_10_7_upgrade_replaces_progressive_artifact_and_removes_step_resources(
    tmp_path: Path,
    runtime: str,
) -> None:
    installed = _seed_10_7_progressive_codex_install(tmp_path)

    if runtime == "installer":
        ctx = MagicMock(local_mode=True, local_repo_dir=REPO_ROOT, ui=None)
        with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
            CodexFilesStep()._install_codex_skills(ctx)
    else:
        source = tmp_path / ".pilot" / "skills" / "cleanup"
        shutil.copytree(SKILL_DIR, source)
        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            assert codex_skill_sync._sync_codex_skills() == (1, 0)

    artifact = (installed / "SKILL.md").read_text()
    resources = json.loads((installed / ".pilot-resources.json").read_text())
    assert "## Required phase resources" not in artifact
    assert "Read `steps/" not in artifact
    assert not (installed / "steps").exists()
    assert all(not path.startswith("steps/") for path in resources["files"])
    assert all(not path.startswith("steps") for path in resources["directories"])


@pytest.mark.parametrize("runtime", ["installer", "session-sync"])
def test_codex_packaging_preserves_unowned_same_name_skill(tmp_path: Path, runtime: str) -> None:
    installed = tmp_path / ".agents" / "skills" / "cleanup"
    installed.mkdir(parents=True)
    (installed / "SKILL.md").write_text("user-owned cleanup\n")

    if runtime == "installer":
        ctx = MagicMock(local_mode=True, local_repo_dir=REPO_ROOT, ui=MagicMock())
        with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
            CodexFilesStep()._install_codex_skills(ctx)
        assert any("unowned" in str(call.args[0]) for call in ctx.ui.warning.call_args_list)
    else:
        source = tmp_path / ".pilot" / "skills" / "cleanup"
        shutil.copytree(SKILL_DIR, source)
        with patch("codex_skill_sync.Path.home", return_value=tmp_path):
            built, failed = codex_skill_sync._sync_codex_skills()
        assert (built, failed) == (0, 1)

    assert (installed / "SKILL.md").read_text() == "user-owned cleanup\n"
    assert not (installed / ".pilot-resources.json").exists()
    assert not (installed / "scripts").exists()
    assert not (installed / "steps").exists()


def test_license_cleanup_preserves_unowned_same_name_skill(tmp_path: Path) -> None:
    installed = tmp_path / ".agents" / "skills" / "cleanup"
    installed.mkdir(parents=True)
    (installed / "SKILL.md").write_text("user-owned cleanup\n")

    with patch("codex_skill_sync.Path.home", return_value=tmp_path):
        removed = codex_skill_sync._remove_codex_skills()

    assert removed == 0
    assert (installed / "SKILL.md").read_text() == "user-owned cleanup\n"


def test_codegraph_helper_is_scoped_deterministic_and_read_only(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")

    package = tmp_path / "global" / "node_modules" / "@colbymchenry" / "codegraph"
    package.mkdir(parents=True)
    (package / "package.json").write_text(
        json.dumps({"name": "@colbymchenry/codegraph", "version": "test", "main": "index.cjs"})
    )
    (package / "index.cjs").write_text(
        """
class Graph {
  static async open(root, options) {
    if (options.sync !== false || options.readOnly !== true) throw new Error('unsafe open options')
    return new Graph()
  }
  getIndexState() { return 'complete' }
  getPendingReferenceCount() { return 0 }
  isIndexStale() { return false }
  findDeadCode() {
    return [
      { filePath: 'src/z.ts', startLine: 9, endLine: 10, name: 'zeta', qualifiedName: 'zeta', kind: 'function', language: 'typescript' },
      { filePath: 'vendor/no.ts', startLine: 1, endLine: 2, name: 'vendor', qualifiedName: 'vendor', kind: 'function', language: 'typescript' },
      { filePath: 'src/generated/no.ts', startLine: 2, endLine: 3, name: 'generated', qualifiedName: 'generated', kind: 'function', language: 'typescript' },
      { filePath: 'src/a.ts', startLine: 4, endLine: 6, name: 'alpha', qualifiedName: 'alpha', kind: 'function', language: 'typescript', visibility: 'private', isExported: false }
    ]
  }
  close() {}
}
module.exports = { CodeGraph: Graph }
""".strip()
        + "\n"
    )
    launcher = package / "npm-shim.js"
    launcher.write_text("#!/usr/bin/env node\n")
    launcher.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    os.symlink(launcher, bin_dir / "codegraph")

    project = tmp_path / "project"
    (project / ".codegraph").mkdir(parents=True)
    (project / ".codegraph" / "codegraph.db").write_bytes(b"read-only fixture")
    env = {**os.environ, "PATH": str(bin_dir), "NODE_PATH": ""}
    command = [
        node,
        str(SCRIPT),
        "--root",
        str(project),
        "--scope",
        "src",
        "--exclude",
        "src/generated",
        "--limit",
        "1",
    ]

    first = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
    second = subprocess.run(command, capture_output=True, text=True, env=env, check=False)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert payload["read_only"] is True
    assert payload["sync"] is False
    assert payload["scope"] == ["src"]
    assert payload["exclusions"] == ["src/generated"]
    assert payload["matching_candidates"] == 2
    assert payload["returned_candidates"] == 1
    assert payload["truncated"] is True
    assert payload["candidates"][0]["file"] == "src/a.ts"
    assert payload["candidates"][0]["name"] == "alpha"
    assert (project / ".codegraph" / "codegraph.db").read_bytes() == b"read-only fixture"
