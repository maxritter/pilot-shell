"""Canonical fragment hashes for installer-generated skill artifacts."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from installer.skill_builder import BuildError, canonicalize, load_manifest


def compute_skill_hashes(skill_dir: Path) -> dict[str, str]:
    """Compute canonical SHA256 hashes for every manifest step."""
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.is_file():
        raise BuildError(f"manifest.json not found in {skill_dir}")
    manifest = load_manifest(manifest_path)

    hashes: dict[str, str] = {}
    for step in manifest["steps"]:
        step_id = step["id"]
        step_path = skill_dir / step["file"]
        if not step_path.is_file():
            raise BuildError(f"fragment file not found: {step_path} (step id: {step_id})")
        canonical = canonicalize(step_path.read_text(encoding="utf-8"))
        hashes[step_id] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return hashes


def write_hash_manifest(skill_dir: Path, output_path: Path | None = None) -> Path:
    """Write a deterministic hashes.json beside an installed skill."""
    data: dict[str, Any] = {
        "version": 1,
        "skill": skill_dir.name,
        "fragments": compute_skill_hashes(skill_dir),
    }
    target = output_path if output_path is not None else skill_dir / "hashes.json"
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(target))
    return target
