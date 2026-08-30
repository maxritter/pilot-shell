"""Cross-agent packaging and scoping contract for Pilot's UI design pack."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from installer.skill_builder import build_skill_md, load_manifest
from installer.steps.claude_files import ClaudeFilesStep
from installer.steps.codex_files import (
    CodexFilesStep,
    build_codex_skill_md,
    build_codex_skill_openai_yaml,
)

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = REPO_ROOT / "pilot" / "skills"
RULE_PATH = REPO_ROOT / "pilot" / "rules" / "design-quality.md"
DESIGN_SKILLS = {
    "claude-design": {
        "references/tool-workflows.md",
    },
    "ui-design": {
        "references/discovery-and-direction.md",
        "references/exploration.md",
        "references/prototype.md",
        "references/UPSTREAM.md",
    },
    "design-system": {
        "references/tokens.md",
        "references/components.md",
        "references/UPSTREAM.md",
    },
    "ui-design-review": {
        "references/accessibility.md",
        "references/visual-quality.md",
        "references/interaction-and-verification.md",
        "references/UPSTREAM.md",
    },
}
UPSTREAM_DESIGN_SKILLS = frozenset({"ui-design", "design-system", "ui-design-review"})
FORBIDDEN_UPSTREAM_ASSUMPTIONS = (
    "${AGENT_TOOL_NAME}",
    "questions_v2",
    "copy_starter_component",
    "design_canvas.jsx",
    "deck_stage.js",
    "__activate_edit_mode",
    "window.parent.postMessage",
    "Codex runs as a single agent loop",
    "at least 10 questions",
)
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


def _runtime_text(skill_name: str) -> str:
    skill_dir = SKILLS_ROOT / skill_name
    parts = [build_skill_md(skill_dir)]
    parts.extend(path.read_text(encoding="utf-8") for path in sorted((skill_dir / "references").glob("*.md")))
    return "\n".join(parts)


def test_design_quality_rule_is_narrowly_path_gated() -> None:
    content = RULE_PATH.read_text(encoding="utf-8")
    metadata = _frontmatter(content)
    paths = metadata["paths"]

    assert isinstance(paths, list)
    assert "**/*.{tsx,jsx,html,vue,svelte,astro,razor}" in paths
    assert "**/*.{css,scss,sass,less}" in paths
    assert "**/*.module.css" in paths
    assert "**/*.razor.css" in paths
    assert "**/*.ts" not in paths
    assert "**/*.js" not in paths
    assert all("swift" not in pattern and "kt" not in pattern for pattern in paths)
    assert "Preserve the current visual language" in content
    assert "non-visual logic change" in content


@pytest.mark.parametrize("skill_name", sorted(DESIGN_SKILLS))
def test_design_skill_manifest_and_compiled_artifacts_are_implicit_and_cross_agent(skill_name: str) -> None:
    skill_dir = SKILLS_ROOT / skill_name
    manifest = load_manifest(skill_dir / "manifest.json")
    claude = build_skill_md(skill_dir)
    codex = build_codex_skill_md(skill_dir)
    metadata = yaml.safe_load(build_codex_skill_openai_yaml(skill_dir))

    assert manifest == {
        "version": 2,
        "orchestrator": "orchestrator.md",
        "delivery": "bundled",
        "targets": ["claude", "codex"],
        "visibility": "public",
        "invocation": "implicit",
        "evals": "tests/evals.json",
        "steps": [],
    }
    assert _frontmatter(claude)["name"] == skill_name
    assert _frontmatter(claude)["user-invocable"] is True
    assert _frontmatter(codex)["name"] == skill_name
    assert metadata["policy"]["allow_implicit_invocation"] is True
    assert codex_skill_sync._build_codex_skill(skill_dir) == codex
    assert codex_skill_sync._build_openai_yaml(skill_dir) == build_codex_skill_openai_yaml(skill_dir)


@pytest.mark.parametrize("skill_name", sorted(UPSTREAM_DESIGN_SKILLS))
def test_design_skill_references_are_complete_licensed_and_portable(skill_name: str) -> None:
    skill_dir = SKILLS_ROOT / skill_name
    relative_files = {path.relative_to(skill_dir).as_posix() for path in (skill_dir / "references").glob("*.md")}
    runtime = _runtime_text(skill_name)
    upstream = (skill_dir / "references" / "UPSTREAM.md").read_text(encoding="utf-8")

    assert relative_files == DESIGN_SKILLS[skill_name]
    assert "3c3ddb07d7aa3fef051d83608596470c95cfd8fe" in upstream
    assert "Copyright (c) 2026 Trystan Sarrade" in upstream
    assert "Permission is hereby granted, free of charge" in upstream
    for forbidden in FORBIDDEN_UPSTREAM_ASSUMPTIONS:
        assert forbidden not in runtime


def test_claude_design_skill_routes_natively_or_through_safe_pilot_cli() -> None:
    runtime = _runtime_text("claude-design")
    skill_dir = SKILLS_ROOT / "claude-design"
    relative_files = {path.relative_to(skill_dir).as_posix() for path in (skill_dir / "references").glob("*.md")}

    assert relative_files == DESIGN_SKILLS["claude-design"]
    assert "native `claude_design` MCP tools" in runtime
    assert "`pilot design`" in runtime
    assert "pilot design tools --json" in runtime
    assert "pilot design describe" in runtime
    assert "pilot design call" in runtime
    assert "pilot design pull" in runtime
    assert "pilot design push" in runtime
    assert "--allow-write" in runtime
    assert "--allow-external-local-path" in runtime
    assert "literal plan-token arguments are rejected" in runtime
    assert "repository-local scratch path" in runtime
    assert "Never pass `--allow-write`" in runtime
    assert "`/design-login`" in runtime
    assert "macOS Keychain" in runtime
    assert "never print, log, persist, or reconstruct" in runtime
    assert "`if_none_match`" in runtime
    assert "windowed" in runtime
    assert "`.dc.html`" in runtime
    assert "`create_support_js`" in runtime
    assert "mechanical gate" in runtime
    assert "fresh-eyes" in runtime


def test_design_review_distinguishes_report_only_review_from_requested_fixes() -> None:
    runtime = _runtime_text("ui-design-review")

    assert "Review and audit requests are report-only" in runtime
    assert "Change files only when the user asks to fix, polish, redesign, or implement" in runtime
    assert "24 by 24 CSS pixels" in runtime
    assert "44 by 44 CSS pixels" in runtime
    assert "Level AAA" in runtime
    assert "18 point" in runtime
    assert "14 point bold" in runtime


def test_ui_design_uses_project_context_and_does_not_persist_sensitive_inputs() -> None:
    runtime = _runtime_text("ui-design")

    assert "existing design system" in runtime
    assert "project-native framework" in runtime
    assert "Ask only when the answer materially changes" in runtime
    assert "Never persist passwords, authentication secrets, payment data, email/contact identifiers" in runtime
    assert "Do not populate unspecified fields, settings, sections, policies, or consequences" in runtime
    assert "Design only the named region" in runtime
    assert "Show only that region" in runtime
    assert "[verified deletion consequence]" in runtime
    assert "A missing repository never expands scope" in runtime
    assert "The user's explicit surface is the boundary" in runtime
    assert "ask one scope question" in runtime
    assert "include a **Verification plan** in the delivered artifact" in runtime
    assert "Every asynchronous action in a designed flow includes a retryable failure state" in runtime
    assert "Do not reopen visual direction" in runtime
    assert "state the assumed direction" in runtime


def test_design_review_runs_mechanical_gate_before_visual_judgment() -> None:
    runtime = _runtime_text("ui-design-review")

    assert "mechanical gate" in runtime
    assert "blank mount" in runtime
    assert "failed subresources" in runtime
    assert "fresh-eyes" in runtime
    assert "The screenshot is the visual ground truth" in runtime


def test_design_pack_is_registered_without_becoming_explicit_only() -> None:
    expected = set(DESIGN_SKILLS)
    catalog = json.loads((REPO_ROOT / "benchmarks" / "skill-routing" / "catalog.json").read_text())
    records = {entry["id"]: entry for entry in catalog["skills"]}

    assert expected <= CodexFilesStep._CODEX_SUPPORTED_SKILLS
    assert expected <= codex_skill_sync._SUPPORTED_SKILLS
    assert expected.isdisjoint(CodexFilesStep._CODEX_EXPLICIT_ONLY_SKILLS)
    assert expected.isdisjoint(codex_skill_sync._EXPLICIT_ONLY_SKILLS)
    for skill_name in expected:
        assert records[skill_name]["visibility"] == "public"
        assert records[skill_name]["invocation"] == "implicit"
        assert len(records[skill_name]["positives"]) >= 3
        assert len(records[skill_name]["negatives"]) >= 3


def test_local_installer_packages_design_references_for_codex(tmp_path: Path) -> None:
    ctx = MagicMock(local_mode=True, local_repo_dir=REPO_ROOT, ui=None)

    with patch("installer.steps.codex_files.Path.home", return_value=tmp_path):
        written = CodexFilesStep()._install_codex_skills(ctx)

    assert written >= len(DESIGN_SKILLS)
    for skill_name, references in DESIGN_SKILLS.items():
        installed = tmp_path / ".agents" / "skills" / skill_name
        assert (installed / "SKILL.md").read_text() == build_codex_skill_md(SKILLS_ROOT / skill_name)
        assert (installed / "agents" / "openai.yaml").is_file()
        assert (installed / ".pilot-resources.json").is_file()
        assert not (installed / "manifest.json").exists()
        assert not (installed / "orchestrator.md").exists()
        for relative in references:
            assert (installed / relative).is_file()


@pytest.mark.parametrize("skill_name", sorted(DESIGN_SKILLS))
def test_claude_installer_builds_design_skill_and_preserves_references(skill_name: str, tmp_path: Path) -> None:
    claude_root = tmp_path / ".claude"
    source = SKILLS_ROOT / skill_name
    installed = claude_root / "skills" / skill_name
    shutil.copytree(source, installed)
    ctx = MagicMock(
        config={"installed_files": [str(path) for path in installed.rglob("*") if path.is_file()]},
        ui=None,
    )
    step = ClaudeFilesStep()

    with (
        patch("installer.steps.claude_files.get_claude_config_dir", return_value=claude_root),
        patch.object(step, "_create_download_config", return_value=MagicMock()),
    ):
        step._build_skill_md_files(ctx, None)

    assert (installed / "SKILL.md").read_text(encoding="utf-8") == build_skill_md(source)
    assert (installed / "hashes.json").is_file()
    for relative in DESIGN_SKILLS[skill_name]:
        assert (installed / relative).is_file()


def test_real_codex_install_keeps_design_rule_body_on_demand(tmp_path: Path) -> None:
    codex_dir = tmp_path / ".codex"
    ctx = MagicMock(local_mode=True, local_repo_dir=REPO_ROOT, ui=None)

    with patch("installer.steps.codex_files._get_codex_config_dir", return_value=codex_dir):
        CodexFilesStep()._install_codex_rules(ctx)

    agents = (codex_dir / "AGENTS.md").read_text(encoding="utf-8")
    installed_rule = codex_dir / "rules" / "design-quality.md"
    assert "Preserve the current visual language" not in agents
    assert str(installed_rule) in agents
    assert "**/*.{tsx,jsx,html,vue,svelte,astro,razor}" in agents
    assert "Preserve the current visual language" in installed_rule.read_text(encoding="utf-8")
    assert "paths:" not in installed_rule.read_text(encoding="utf-8")


def test_existing_rules_and_verifier_have_single_design_owners() -> None:
    frontend = (REPO_ROOT / "pilot" / "rules" / "standards-frontend.md").read_text(encoding="utf-8")
    mobile = (REPO_ROOT / "pilot" / "rules" / "mobile-development.md").read_text(encoding="utf-8")
    spec_verify = (
        REPO_ROOT / "pilot" / "skills" / "spec-verify" / "steps" / "07-e2e-and-final-regression.md"
    ).read_text(encoding="utf-8")

    assert "## Design Direction" not in frontend
    assert "## Absolute Bans" not in frontend
    assert "design-quality.md" in frontend
    assert "WCAG 2.2 AA's 24×24" in mobile
    assert "including its touch-target floor (44x44 iOS, 48x48 Android)" not in mobile
    assert "Skill(skill='ui-design-review'" in spec_verify
    assert "impeccable detect --json" not in spec_verify
    assert "Design-Quality Detector (best-effort, advisory)" not in spec_verify


def test_spec_verify_design_handoff_compiles_for_both_agents() -> None:
    skill_dir = SKILLS_ROOT / "spec-verify"
    claude = build_skill_md(skill_dir)
    codex = build_codex_skill_md(skill_dir)

    assert "Skill(skill='ui-design-review'" in claude
    assert "Skill(skill='ui-design-review'" not in codex
    assert "$ui-design-review" in codex
    assert "The UI design review skill owns accessibility" in claude
    assert "The UI design review skill owns accessibility" in codex
