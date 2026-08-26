"""Tests for installer.skill_builder.

The module is a vendored copy of launcher/skill_builder.py. The first test
asserts byte-equality so the two copies cannot drift — `canonicalize()` must
match exactly across the boundary or customize-apply drift detection breaks.
See .claude/rules/pilot-shell-package-boundaries.md for why we vendor.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from installer.skill_builder import (
    BuildError,
    build_skill_md,
    canonicalize,
    write_skill_md,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestVendoredCopyMatchesLauncher:
    def test_skill_builder_byte_identical_to_launcher_copy(self) -> None:
        """installer/skill_builder.py must be byte-identical to launcher/skill_builder.py.

        Drift breaks customize hash matching. If you intentionally changed one,
        update the other in the same commit.
        """
        launcher_copy = REPO_ROOT / "launcher" / "skill_builder.py"
        installer_copy = REPO_ROOT / "installer" / "skill_builder.py"
        assert launcher_copy.read_bytes() == installer_copy.read_bytes(), (
            "installer/skill_builder.py drifted from launcher/skill_builder.py — update both copies in the same commit."
        )


class TestCanonicalize:
    def test_normalizes_crlf_line_endings(self) -> None:
        assert canonicalize("a\r\nb\r\nc") == "a\nb\nc"

    def test_strips_trailing_whitespace_per_line(self) -> None:
        assert canonicalize("a   \nb\t\nc") == "a\nb\nc"

    def test_collapses_blank_line_runs(self) -> None:
        assert canonicalize("a\n\n\n\nb") == "a\n\nb"


class TestBuildSkillMd:
    def _make_skill(self, root: Path, name: str = "demo") -> Path:
        skill_dir = root / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "orchestrator.md").write_text("# Orchestrator")
        (skill_dir / "steps").mkdir()
        (skill_dir / "steps" / "01.md").write_text("## Step 1")
        (skill_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "orchestrator": "orchestrator.md",
                    "steps": [{"id": "step-1", "file": "steps/01.md"}],
                }
            )
        )
        return skill_dir

    def test_concatenates_orchestrator_and_fragments(self, tmp_path: Path) -> None:
        skill_dir = self._make_skill(tmp_path)
        built = build_skill_md(skill_dir)
        assert "# Orchestrator" in built
        assert "## Step 1" in built

    def test_raises_on_missing_manifest(self, tmp_path: Path) -> None:
        with pytest.raises(BuildError, match="manifest.json not found"):
            build_skill_md(tmp_path)

    def test_raises_on_missing_fragment(self, tmp_path: Path) -> None:
        skill_dir = self._make_skill(tmp_path)
        (skill_dir / "steps" / "01.md").unlink()
        with pytest.raises(BuildError, match="fragment file not found"):
            build_skill_md(skill_dir)

    def test_write_skill_md_writes_atomically(self, tmp_path: Path) -> None:
        skill_dir = self._make_skill(tmp_path)
        output = write_skill_md(skill_dir)
        assert output == skill_dir / "SKILL.md"
        assert output.is_file()
        assert "# Orchestrator" in output.read_text()
        assert not (skill_dir / "SKILL.md.tmp").exists()

    def test_progressive_manifest_builds_compact_step_index(self, tmp_path: Path) -> None:
        skill_dir = self._make_skill(tmp_path)
        manifest_path = skill_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.update(
            {
                "version": 2,
                "delivery": "progressive",
                "targets": ["claude", "codex"],
                "visibility": "public",
                "invocation": "implicit",
            }
        )
        manifest_path.write_text(json.dumps(manifest))

        built = build_skill_md(skill_dir)

        assert "## Step 1" not in built
        assert "Read `steps/01.md` completely" in built


class TestRealSkillFrontmatterIsValidYaml:
    """Every built SKILL.md must carry frontmatter that parses under a strict YAML loader.

    Claude Code's lenient frontmatter reader tolerated an `argument-hint` whose value
    was a double-quoted scalar followed by trailing content (`"a" or "b"`), but strict
    PyYAML-based loaders used by third-party agents reject it ("while parsing a block
    mapping ... expected <block end>, but found '<scalar>'") and silently skip the skill.
    Guards every shipped skill, not just the one that regressed.
    """

    SKILLS_ROOT = REPO_ROOT / "pilot" / "skills"

    def _skill_dirs(self) -> list[Path]:
        return sorted(
            d
            for d in self.SKILLS_ROOT.iterdir()
            if (d / "manifest.json").is_file() and (d / "orchestrator.md").is_file()
        )

    def test_all_built_skill_frontmatter_parses_with_strict_yaml(self) -> None:
        skill_dirs = self._skill_dirs()
        assert skill_dirs, f"no skills discovered under {self.SKILLS_ROOT}"

        failures: list[str] = []
        for skill_dir in skill_dirs:
            built = build_skill_md(skill_dir)
            match = re.match(r"^---\n(.*?)\n---", built, re.DOTALL)
            assert match is not None, f"{skill_dir.name}: built SKILL.md has no YAML frontmatter"
            try:
                yaml.safe_load(match.group(1))
            except yaml.YAMLError as exc:
                failures.append(f"{skill_dir.name}: {str(exc).splitlines()[0]}")

        assert not failures, "invalid YAML frontmatter in built skills:\n" + "\n".join(failures)

    def test_every_step_file_on_disk_is_listed_in_its_manifest(self) -> None:
        """A step file the manifest omits is authored, reviewed, and shipped - but never built.

        `build_skill_md` assembles SKILL.md strictly from `manifest.json`, so an
        unlisted `steps/*.md` silently contributes nothing. It fails loudly in
        neither direction: the file is on disk and readable, the orchestrator can
        even document the step by name, and the build still succeeds. `benchmark`
        shipped exactly that way - its orchestrator listed a step 6 pointing at
        `steps/06-improvement-plan.md` that no manifest entry ever loaded.

        The reverse direction (manifest entry with no file) already raises
        BuildError, so only orphans need guarding here.
        """
        failures: list[str] = []
        for skill_dir in self._skill_dirs():
            steps_dir = skill_dir / "steps"
            if not steps_dir.is_dir():
                continue
            listed = {s["file"] for s in json.loads((skill_dir / "manifest.json").read_text())["steps"]}
            on_disk = {p.relative_to(skill_dir).as_posix() for p in steps_dir.rglob("*.md")}
            orphans = sorted(on_disk - listed)
            if orphans:
                failures.append(f"{skill_dir.name}: {', '.join(orphans)}")

        assert not failures, (
            "step files present on disk but absent from manifest.json - they build into "
            "nothing and ship as dead weight. Add a manifest entry, or delete the file:\n" + "\n".join(failures)
        )
