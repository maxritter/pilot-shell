"""Skill builder — concatenates fragment files into a single SKILL.md.

Used in two places:
1. Directly inside the launcher package (launcher.customize invokes after overlay apply).
2. Via the `pilot skill-build` CLI subcommand — invoked by the installer as a subprocess
   during install, and by pre-commit hooks / equivalence tests in this repo.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class BuildError(Exception):
    """Raised when a skill manifest is invalid or fragments cannot be assembled."""


def canonicalize(text: str) -> str:
    """Normalize a skill markdown string for equivalence comparison and hashing.

    Applied identically to both equivalence checks (Tasks 4/5) and drift hashing (Task 2)
    so CRLF/trailing-whitespace/blank-line-reflow changes never trigger false drift.
    """
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    # Collapse runs of 2+ blank lines to a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace
    return text.strip()


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Read and parse manifest.json. Raises BuildError on invalid JSON."""
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as e:
        raise BuildError(f"cannot read manifest {manifest_path}: {e}") from e
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise BuildError(f"invalid JSON in {manifest_path}: {e}") from e
    if not isinstance(data, dict):
        raise BuildError(f"manifest {manifest_path} must be a JSON object")
    validate_manifest(data)
    return data


def validate_manifest(data: dict[str, Any]) -> None:
    """Validate manifest structure. Raises BuildError on any issue."""
    if "version" not in data:
        raise BuildError("manifest missing required key: version")
    if "orchestrator" not in data:
        raise BuildError("manifest missing required key: orchestrator")
    if "steps" not in data:
        raise BuildError("manifest missing required key: steps")
    steps = data["steps"]
    if not isinstance(steps, list):
        raise BuildError("manifest.steps must be a list")

    seen_ids: set[str] = set()
    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            raise BuildError(f"manifest.steps[{idx}] must be an object")
        if "id" not in step:
            raise BuildError(f"manifest.steps[{idx}] missing required key: id")
        if "file" not in step:
            raise BuildError(f"manifest.steps[{idx}] missing required key: file")
        if step["id"] in seen_ids:
            raise BuildError(f"manifest has duplicate step id: {step['id']}")
        seen_ids.add(step["id"])


def build_skill_md(
    skill_dir: Path,
    effective_steps: list[dict[str, Any]] | None = None,
) -> str:
    """Concatenate orchestrator + ordered fragments into a single SKILL.md string.

    If effective_steps is provided, it overrides the manifest's steps list —
    used by customize overlay application after applying insert/replace/disable ops.
    """
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.is_file():
        raise BuildError(f"manifest.json not found in {skill_dir}")
    manifest = load_manifest(manifest_path)

    orchestrator_rel = manifest["orchestrator"]
    orchestrator_path = skill_dir / orchestrator_rel
    if not orchestrator_path.is_file():
        raise BuildError(f"orchestrator file not found: {orchestrator_path}")

    steps = effective_steps if effective_steps is not None else manifest["steps"]

    try:
        orchestrator_text = orchestrator_path.read_text(encoding="utf-8")
    except OSError as e:
        raise BuildError(f"cannot read orchestrator {orchestrator_path}: {e}") from e

    parts: list[str] = [orchestrator_text]

    for step in steps:
        rel = step["file"]
        step_path = skill_dir / rel
        if not step_path.is_file():
            raise BuildError(f"fragment file not found: {step_path} (step id: {step['id']})")
        try:
            parts.append(step_path.read_text(encoding="utf-8"))
        except OSError as e:
            raise BuildError(f"cannot read fragment {step_path}: {e}") from e

    raw = "\n\n".join(parts)
    return canonicalize(raw)


def write_skill_md(skill_dir: Path, output_path: Path | None = None) -> Path:
    """Build SKILL.md and write to disk atomically. Returns the written path."""
    built = build_skill_md(skill_dir)
    target = output_path if output_path is not None else (skill_dir / "SKILL.md")
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(built, encoding="utf-8")
    import os

    os.replace(str(tmp), str(target))
    return target
