"""Contract tests for the canonical cross-platform hook lifecycle matrix."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GENERATOR_PATH = ROOT / "scripts" / "gen_hook_manifests.py"
SPEC = importlib.util.spec_from_file_location("gen_hook_manifests", GENERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


def test_matrix_entries_have_unique_ids_and_valid_schema() -> None:
    matrix = generator.load_matrix()

    assert generator.validate_matrix(matrix) == []
    ids = [entry["id"] for entry in matrix["entries"]]
    assert len(ids) == len(set(ids))


def test_every_entry_has_an_explicit_contract_coverage_tag() -> None:
    entries = generator.load_matrix()["entries"]

    for entry in entries:
        test_path, test_name = entry["contract_test"].split("::", 1)
        assert (ROOT / test_path).is_file(), entry["id"]
        assert test_name, entry["id"]


def test_referenced_local_command_targets_exist() -> None:
    targets = generator.referenced_local_targets(generator.load_matrix())

    assert targets
    missing = [path.relative_to(ROOT) for path in targets if not path.is_file()]
    assert missing == []


def test_generated_manifests_preserve_the_shipped_bytes() -> None:
    matrix = generator.load_matrix()

    for platform, path in generator.OUTPUTS.items():
        assert generator.render_manifest(matrix, platform) == path.read_text()


def test_check_reports_zero_drift() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATOR_PATH), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "zero drift" in result.stdout.lower()
