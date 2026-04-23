"""Tests for installer.skill_builder.

The module is a vendored copy of launcher/skill_builder.py. The first test
asserts byte-equality so the two copies cannot drift — `canonicalize()` must
match exactly across the boundary or customize-apply drift detection breaks.
See .claude/rules/pilot-shell-package-boundaries.md for why we vendor.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

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
