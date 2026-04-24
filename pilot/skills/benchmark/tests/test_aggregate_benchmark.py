"""Tests for scripts.aggregate_benchmark — stats, parsing, markdown."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest
from scripts.aggregate_benchmark import (
    _coerce_float,
    _coerce_int,
    _empty_summary,
    _parse_run,
    _resolve_eval_id,
    aggregate_results,
    calculate_stats,
    generate_benchmark,
    generate_markdown,
    load_run_results,
)
from scripts.utils import BenchmarkSnapshot, ParsedRunRecord, RunSummaryEntry

# ----------------------------------------------------------------------------
# Coercion helpers
# ----------------------------------------------------------------------------


class TestCoerceFloat:
    def test_passes_floats(self) -> None:
        assert _coerce_float(1.5) == 1.5

    def test_promotes_ints(self) -> None:
        assert _coerce_float(7) == 7.0

    def test_default_for_non_numeric(self) -> None:
        assert _coerce_float("nope") == 0.0
        assert _coerce_float(None, default=2.5) == 2.5


class TestCoerceInt:
    def test_passes_ints(self) -> None:
        assert _coerce_int(42) == 42

    def test_default_for_non_int(self) -> None:
        assert _coerce_int("12") == 0
        assert _coerce_int(3.5, default=99) == 99


# ----------------------------------------------------------------------------
# calculate_stats
# ----------------------------------------------------------------------------


class TestCalculateStats:
    def test_empty_returns_zeros(self) -> None:
        result = calculate_stats([])
        assert result == {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}

    def test_single_value_has_zero_stddev(self) -> None:
        result = calculate_stats([5.0])
        assert result["mean"] == 5.0
        assert result["stddev"] == 0.0
        assert result["min"] == 5.0
        assert result["max"] == 5.0

    def test_known_values(self) -> None:
        result = calculate_stats([1.0, 2.0, 3.0])
        assert result["mean"] == 2.0
        # sample stddev with n-1 = sqrt(1.0) = 1.0
        assert result["stddev"] == 1.0
        assert result["min"] == 1.0
        assert result["max"] == 3.0


# ----------------------------------------------------------------------------
# Run-directory helpers
# ----------------------------------------------------------------------------


def _write_run(
    run_dir: Path,
    *,
    pass_rate: float = 1.0,
    duration: float = 5.0,
    tokens: int = 1000,
    errors: int = 0,
) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    grading = {
        "summary": {"pass_rate": pass_rate, "passed": 3, "failed": 0, "total": 3},
        "timing": {"total_duration_seconds": duration},
        "execution_metrics": {"errors_encountered": errors},
        "expectations": [
            {"text": "did the thing", "passed": True, "evidence": "ok"},
        ],
    }
    timing = {"total_duration_seconds": duration, "total_tokens": tokens}
    _ = (run_dir / "grading.json").write_text(json.dumps(grading))
    _ = (run_dir / "timing.json").write_text(json.dumps(timing))
    return run_dir


class TestResolveEvalId:
    def test_uses_metadata_when_present(self, tmp_path: Path) -> None:
        eval_dir = tmp_path / "eval-7"
        eval_dir.mkdir()
        _ = (eval_dir / "eval_metadata.json").write_text(json.dumps({"eval_id": 99}))
        assert _resolve_eval_id(eval_dir, 0) == 99

    def test_falls_back_to_dir_suffix(self, tmp_path: Path) -> None:
        eval_dir = tmp_path / "eval-3"
        eval_dir.mkdir()
        assert _resolve_eval_id(eval_dir, 1) == 3

    def test_falls_back_to_index_when_unparseable(self, tmp_path: Path) -> None:
        eval_dir = tmp_path / "weird-name"
        eval_dir.mkdir()
        assert _resolve_eval_id(eval_dir, 5) == 5


class TestParseRun:
    def test_returns_none_when_no_grading(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run-1"
        run_dir.mkdir()
        assert _parse_run(run_dir, eval_id=1) is None

    def test_returns_none_when_invalid_json(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run-1"
        run_dir.mkdir()
        _ = (run_dir / "grading.json").write_text("not json")
        assert _parse_run(run_dir, eval_id=1) is None

    def test_parses_complete_run(self, tmp_path: Path) -> None:
        run_dir = _write_run(tmp_path / "run-2", pass_rate=0.75, duration=10.0, tokens=2500)
        result = _parse_run(run_dir, eval_id=4)
        assert result is not None
        assert result["eval_id"] == 4
        assert result["run_number"] == 2
        assert result["pass_rate"] == 0.75
        assert result["time_seconds"] == 10.0
        assert result["tokens"] == 2500
        assert len(result["expectations"]) == 1
        assert result["expectations"][0]["text"] == "did the thing"

    def test_falls_back_to_timing_json_when_grading_missing_timing(
        self, tmp_path: Path
    ) -> None:
        run_dir = tmp_path / "run-1"
        run_dir.mkdir()
        _ = (run_dir / "grading.json").write_text(
            json.dumps({"summary": {"pass_rate": 1.0}, "expectations": []})
        )
        _ = (run_dir / "timing.json").write_text(
            json.dumps({"total_duration_seconds": 7.5, "total_tokens": 500})
        )
        result = _parse_run(run_dir, eval_id=1)
        assert result is not None
        assert result["time_seconds"] == 7.5
        assert result["tokens"] == 500

    def test_collects_user_notes(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run-1"
        run_dir.mkdir()
        _ = (run_dir / "grading.json").write_text(
            json.dumps(
                {
                    "summary": {"pass_rate": 1.0},
                    "expectations": [],
                    "user_notes_summary": {
                        "uncertainties": ["maybe X"],
                        "needs_review": ["check Y"],
                        "workarounds": [],
                    },
                }
            )
        )
        result = _parse_run(run_dir, eval_id=1)
        assert result is not None
        assert "maybe X" in result["notes"]
        assert "check Y" in result["notes"]


# ----------------------------------------------------------------------------
# load_run_results
# ----------------------------------------------------------------------------


def _make_workspace(tmp_path: Path, configs: list[str], n_evals: int = 2) -> Path:
    """Create a workspace-style benchmark layout under tmp_path."""
    for eval_id in range(1, n_evals + 1):
        for cfg in configs:
            _ = _write_run(
                tmp_path / f"eval-{eval_id}" / cfg / "run-1",
                pass_rate=1.0 if cfg == "with_skill" else 0.5,
                duration=10.0 if cfg == "with_skill" else 5.0,
                tokens=2000 if cfg == "with_skill" else 1000,
            )
    return tmp_path


class TestLoadRunResults:
    def test_workspace_layout(self, tmp_path: Path) -> None:
        bench = _make_workspace(tmp_path, ["with_skill", "without_skill"])
        results = load_run_results(bench)
        assert set(results.keys()) == {"with_skill", "without_skill"}
        assert len(results["with_skill"]) == 2
        assert len(results["without_skill"]) == 2

    def test_legacy_runs_subdir_layout(self, tmp_path: Path) -> None:
        runs_dir = tmp_path / "runs"
        _ = _make_workspace(runs_dir, ["with_skill"])
        results = load_run_results(tmp_path)
        assert "with_skill" in results

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        assert load_run_results(tmp_path) == {}


# ----------------------------------------------------------------------------
# aggregate_results
# ----------------------------------------------------------------------------


def _record(eval_id: int, pass_rate: float, time_s: float, tokens: int) -> ParsedRunRecord:
    return ParsedRunRecord(
        eval_id=eval_id,
        run_number=1,
        pass_rate=pass_rate,
        time_seconds=time_s,
        tokens=tokens,
        expectations=[],
        notes=[],
    )


class TestAggregateResults:
    def test_computes_means_and_delta(self) -> None:
        results = {
            "with_skill": [_record(1, 1.0, 10.0, 2000), _record(2, 1.0, 12.0, 2200)],
            "without_skill": [_record(1, 0.5, 5.0, 1000), _record(2, 0.5, 6.0, 1100)],
        }
        summary = aggregate_results(results)
        with_entry = cast(RunSummaryEntry, summary["with_skill"])
        without_entry = cast(RunSummaryEntry, summary["without_skill"])
        delta = summary["delta"]
        assert with_entry["pass_rate"]["mean"] == 1.0
        assert without_entry["pass_rate"]["mean"] == 0.5
        # delta is formatted "+0.50" when first config beats baseline
        assert delta["pass_rate"] == "+0.50"  # type: ignore[index]

    def test_empty_config_yields_zero_summary(self) -> None:
        results = {"with_skill": [], "without_skill": [_record(1, 1.0, 1.0, 100)]}
        summary = aggregate_results(results)
        with_entry = cast(RunSummaryEntry, summary["with_skill"])
        assert with_entry == _empty_summary()


# ----------------------------------------------------------------------------
# generate_benchmark + generate_markdown
# ----------------------------------------------------------------------------


class TestGenerateBenchmark:
    def test_full_pipeline(self, tmp_path: Path) -> None:
        bench = _make_workspace(tmp_path, ["with_skill", "without_skill"])
        snapshot: BenchmarkSnapshot = generate_benchmark(
            bench, skill_name="my-skill", skill_path="/some/path"
        )
        assert snapshot["metadata"].get("skill_name") == "my-skill"
        assert snapshot["metadata"].get("skill_path") == "/some/path"
        assert sorted(snapshot["metadata"].get("evals_run", [])) == [1, 2]
        assert "with_skill" in snapshot["run_summary"]


class TestGenerateMarkdown:
    @pytest.fixture
    def benchmark(self, tmp_path: Path) -> BenchmarkSnapshot:
        bench = _make_workspace(tmp_path, ["with_skill", "without_skill"])
        return generate_benchmark(bench, skill_name="probe", skill_path="/p")

    def test_includes_summary_table(self, benchmark: BenchmarkSnapshot) -> None:
        md = generate_markdown(benchmark)
        assert "# Skill Benchmark: probe" in md
        assert "| Pass Rate |" in md
        assert "| Time |" in md
        assert "| Tokens |" in md

    def test_handles_missing_configs(self) -> None:
        snapshot = BenchmarkSnapshot(
            metadata={"skill_name": "x", "evals_run": [], "runs_per_configuration": 1},
            runs=[],
            run_summary={},
            notes=[],
        )
        md = generate_markdown(snapshot)
        assert "config_a" in md or "Config A" in md
