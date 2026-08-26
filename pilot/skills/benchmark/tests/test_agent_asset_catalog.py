import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[4] / "scripts" / "validate_agent_assets.py"
SPEC = importlib.util.spec_from_file_location("validate_agent_assets", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def test_shipped_catalog_rules_and_generated_descriptions_pass() -> None:
    result = validator.validate(validator.REPO_ROOT, validator.DEFAULT_CATALOG, validator.DEFAULT_RATCHET)

    assert result["findings"] == []
    assert result["metrics"]["positive_top_three_rate"] == 1.0
    assert result["metrics"]["positive_rank_one_rate"] >= 0.8
    assert result["metrics"]["unscoped_lines"] <= 500
    assert result["metrics"]["unscoped_words"] <= 7500


def test_manifest_routing_metadata_overrides_catalog_fallback() -> None:
    entry = {"visibility": "public", "invocation": "explicit"}
    manifest = {"version": 2, "visibility": "internal", "invocation": "implicit", "parent": "spec"}

    assert validator._resolve_metadata(entry, manifest) == ("internal", "implicit", "spec")
    assert validator._resolve_metadata(entry, {"version": 1}) == ("public", "explicit", None)


def test_explicit_and_internal_skills_do_not_hijack_direct_requests() -> None:
    catalog = validator._read_json(validator.DEFAULT_CATALOG)
    records = validator._load_records(validator.REPO_ROOT, catalog)

    direct_ranked = [name for name, _ in validator._route("Fix the login redirect bug.", {}, records)]
    internal_ranked = [name for name, _ in validator._route("$spec-implement this plan", {}, records)]
    handoff_ranked = [
        name for name, _ in validator._route("Continue with $spec-implement.", {"parent": "spec"}, records)
    ]

    assert "fix" not in direct_ranked
    assert "spec-implement" not in internal_ranked
    assert internal_ranked[0] == "spec"
    assert handoff_ranked[0] == "spec-implement"


def test_rule_budget_counts_only_unscoped_rules(tmp_path: Path) -> None:
    rules = tmp_path / "pilot" / "rules"
    rules.mkdir(parents=True)
    (rules / "global.md").write_text("first line\nsecond line\n", encoding="utf-8")
    (rules / "scoped.md").write_text("---\npaths: ['**/*.py']\n---\nDated 2099 claim\n", encoding="utf-8")
    config = {"max_unscoped_lines": 2, "max_unscoped_words": 4, "max_unscoped_file_lines": 2}

    findings, metrics = validator._validate_rules(tmp_path, config)

    assert findings == []
    assert metrics == {"unscoped_files": 1, "unscoped_lines": 2, "unscoped_words": 4}


def test_rule_budget_reports_overflow_and_dated_claims(tmp_path: Path) -> None:
    rules = tmp_path / "pilot" / "rules"
    rules.mkdir(parents=True)
    (rules / "global.md").write_text("A dated 2026 claim.\nToo many lines.\n", encoding="utf-8")
    config = {"max_unscoped_lines": 1, "max_unscoped_words": 3, "max_unscoped_file_lines": 1}

    findings, _ = validator._validate_rules(tmp_path, config)

    assert {finding.code for finding in findings} == {
        "rules.dated-claim",
        "rules.file-lines",
        "rules.lines",
        "rules.words",
    }
