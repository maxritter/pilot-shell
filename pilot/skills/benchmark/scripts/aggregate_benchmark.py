"""Aggregate individual run results into benchmark summary statistics.

Reads grading.json files from run directories and produces:
- run_summary with mean, stddev, min, max for each metric
- delta between with_skill and without_skill configurations

Usage:
    uv run python aggregate_benchmark.py <benchmark_dir>

Example:
    uv run python aggregate_benchmark.py benchmarks/create-skill/runs/2026-04-23T10-30-00/

The script supports two directory layouts:

    Workspace layout (default for the /benchmark runner):
    <benchmark_dir>/
    └── eval-N/
        ├── with_skill/
        │   ├── run-1/grading.json
        │   └── run-2/grading.json
        └── without_skill/
            ├── run-1/grading.json
            └── run-2/grading.json

    Legacy layout (with runs/ subdirectory):
    <benchmark_dir>/
    └── runs/
        └── eval-N/
            ├── with_skill/
            │   └── run-1/grading.json
            └── without_skill/
                └── run-1/grading.json

The emitted benchmark.json has the shape declared by BenchmarkSnapshot in utils.py:
`metadata` + `runs` + `run_summary` (per-config mean/stddev/min/max + signed delta).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.utils import (
    BenchmarkSnapshot,
    DeltaEntry,
    ParsedRunRecord,
    RunSummaryEntry,
    StatBlock,
)


def calculate_stats(values: list[float]) -> StatBlock:
    """Calculate mean, stddev, min, max for a list of values."""
    if not values:
        return StatBlock(mean=0.0, stddev=0.0, min=0.0, max=0.0)

    n = len(values)
    mean = sum(values) / n

    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0

    return StatBlock(
        mean=round(mean, 4),
        stddev=round(stddev, 4),
        min=round(min(values), 4),
        max=round(max(values), 4),
    )


def _resolve_eval_id(eval_dir: Path, eval_idx: int) -> int:
    """Prefer eval_metadata.json's eval_id; fall back to the dir suffix, then index."""
    metadata_path = eval_dir / "eval_metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path) as mf:
                metadata: Any = json.load(mf)
            if isinstance(metadata, dict):
                value = metadata.get("eval_id", eval_idx)
                if isinstance(value, int):
                    return value
            return eval_idx
        except (json.JSONDecodeError, OSError):
            return eval_idx
    try:
        return int(eval_dir.name.split("-")[1])
    except (ValueError, IndexError):
        return eval_idx


def _load_json(path: Path) -> dict[str, Any] | None:
    """Read a JSON file and return it if it parses as an object; else None."""
    try:
        with open(path) as f:
            data: Any = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return cast(dict[str, Any], data)


def _coerce_float(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    return default


def _extract_timing(grading: dict[str, Any], run_dir: Path) -> tuple[float, int]:
    """Pull (time_seconds, tokens) — preferring timing.json when present.

    timing.json is written by the runner with authoritative numbers from the
    stream-json `result` event. grading.json's `timing` block is the grader's
    secondary record. Use timing.json first; fall back to grading.json's timing
    for time, and to execution_metrics.output_chars as a last-resort token proxy.
    """
    timing_block = grading.get("timing")
    grading_timing = cast(dict[str, Any], timing_block) if isinstance(timing_block, dict) else cast(dict[str, Any], {})

    time_seconds = 0.0
    tokens = 0

    timing_file = run_dir / "timing.json"
    if timing_file.exists():
        timing_data = _load_json(timing_file)
        if timing_data is not None:
            time_seconds = _coerce_float(timing_data.get("total_duration_seconds", 0.0))
            tokens = _coerce_int(timing_data.get("total_tokens", 0))

    if time_seconds == 0.0:
        time_seconds = _coerce_float(grading_timing.get("total_duration_seconds", 0.0))

    if tokens == 0:
        metrics_block = grading.get("execution_metrics")
        if isinstance(metrics_block, dict):
            metrics = cast(dict[str, Any], metrics_block)
            tokens = _coerce_int(metrics.get("output_chars", 0))

    return time_seconds, tokens


def _extract_expectations(grading: dict[str, Any], grading_file: Path) -> list[dict[str, object]]:
    raw = grading.get("expectations") or []
    out: list[dict[str, object]] = []
    if not isinstance(raw, list):
        return out
    for exp in cast(list[Any], raw):
        if not isinstance(exp, dict):
            continue
        exp_dict = cast(dict[str, Any], exp)
        if "text" not in exp_dict or "passed" not in exp_dict:
            print(f"Warning: expectation in {grading_file} missing required fields (text, passed): {exp_dict}")
        out.append(cast(dict[str, object], exp_dict))
    return out


def _extract_notes(grading: dict[str, Any]) -> list[str]:
    summary_block = grading.get("user_notes_summary")
    summary = cast(dict[str, Any], summary_block) if isinstance(summary_block, dict) else cast(dict[str, Any], {})
    notes: list[str] = []
    for key in ("uncertainties", "needs_review", "workarounds"):
        bucket = summary.get(key) or []
        if isinstance(bucket, list):
            notes.extend(str(x) for x in cast(list[Any], bucket))
    return notes


def _parse_run(run_dir: Path, eval_id: int) -> ParsedRunRecord | None:
    """Parse a single run directory's grading.json (plus timing.json fallback)."""
    grading_file = run_dir / "grading.json"
    if not grading_file.exists():
        print(f"Warning: grading.json not found in {run_dir}")
        return None

    grading = _load_json(grading_file)
    if grading is None:
        print(f"Warning: invalid or non-object grading.json in {grading_file}")
        return None

    summary_block = grading.get("summary") or {}
    summary = cast(dict[str, Any], summary_block) if isinstance(summary_block, dict) else {}

    try:
        run_number = int(run_dir.name.split("-")[1])
    except (ValueError, IndexError):
        run_number = 0

    pass_rate = _coerce_float(summary.get("pass_rate", 0.0))
    time_seconds, tokens = _extract_timing(grading, run_dir)
    metrics_block = grading.get("execution_metrics") or {}
    metrics = cast(dict[str, Any], metrics_block) if isinstance(metrics_block, dict) else {}
    errors = _coerce_int(metrics.get("errors_encountered", 0))

    return ParsedRunRecord(
        eval_id=eval_id,
        run_number=run_number,
        pass_rate=pass_rate,
        time_seconds=time_seconds,
        tokens=tokens,
        expectations=_extract_expectations(grading, grading_file),
        notes=_extract_notes(grading),
        errors=errors,
    )


def load_run_results(benchmark_dir: Path) -> dict[str, list[ParsedRunRecord]]:
    """Load all run results from a benchmark directory.

    Returns dict keyed by config name (e.g. "with_skill"/"without_skill"),
    each containing a list of run results.
    """
    runs_dir = benchmark_dir / "runs"
    if runs_dir.exists():
        search_dir = runs_dir
    elif list(benchmark_dir.glob("eval-*")):
        search_dir = benchmark_dir
    else:
        print(f"No eval directories found in {benchmark_dir} or {benchmark_dir / 'runs'}")
        return {}

    results: dict[str, list[ParsedRunRecord]] = {}

    for eval_idx, eval_dir in enumerate(sorted(search_dir.glob("eval-*"))):
        eval_id = _resolve_eval_id(eval_dir, eval_idx)

        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir() or not list(config_dir.glob("run-*")):
                continue
            config = config_dir.name
            results.setdefault(config, [])
            for run_dir in sorted(config_dir.glob("run-*")):
                parsed = _parse_run(run_dir, eval_id)
                if parsed is not None:
                    results[config].append(parsed)

    return results


def _empty_summary() -> RunSummaryEntry:
    zero = StatBlock(mean=0.0, stddev=0.0, min=0.0, max=0.0)
    return RunSummaryEntry(pass_rate=zero, time_seconds=zero, tokens=zero)


def aggregate_results(
    results: dict[str, list[ParsedRunRecord]],
) -> dict[str, RunSummaryEntry | DeltaEntry]:
    """Aggregate run results into summary statistics.

    Returns a map of config-name → summary, plus a "delta" entry comparing
    the first two configs. The shape mirrors the legacy output for compatibility.
    """
    run_summary: dict[str, RunSummaryEntry | DeltaEntry] = {}
    configs = list(results.keys())

    for config in configs:
        runs = results.get(config, [])

        if not runs:
            run_summary[config] = _empty_summary()
            continue

        pass_rates = [r["pass_rate"] for r in runs]
        times = [r["time_seconds"] for r in runs]
        tokens = [float(r.get("tokens", 0)) for r in runs]

        run_summary[config] = RunSummaryEntry(
            pass_rate=calculate_stats(pass_rates),
            time_seconds=calculate_stats(times),
            tokens=calculate_stats(tokens),
        )

    primary: RunSummaryEntry = cast(RunSummaryEntry, run_summary[configs[0]]) if configs else _empty_summary()
    baseline: RunSummaryEntry = (
        cast(RunSummaryEntry, run_summary[configs[1]]) if len(configs) >= 2 else _empty_summary()
    )

    delta_pass_rate = primary["pass_rate"]["mean"] - baseline["pass_rate"]["mean"]
    delta_time = primary["time_seconds"]["mean"] - baseline["time_seconds"]["mean"]
    delta_tokens = primary["tokens"]["mean"] - baseline["tokens"]["mean"]

    run_summary["delta"] = DeltaEntry(
        pass_rate=f"{delta_pass_rate:+.2f}",
        time_seconds=f"{delta_time:+.1f}",
        tokens=f"{delta_tokens:+.0f}",
    )

    return run_summary


def generate_benchmark(benchmark_dir: Path, skill_name: str = "", skill_path: str = "") -> BenchmarkSnapshot:
    """Generate complete benchmark.json from run results."""
    results = load_run_results(benchmark_dir)
    run_summary = aggregate_results(results)

    runs: list[dict[str, object]] = []
    for config, config_runs in results.items():
        for record in config_runs:
            runs.append(
                {
                    "eval_id": record["eval_id"],
                    "configuration": config,
                    "run_number": record["run_number"],
                    "result": {
                        "pass_rate": record["pass_rate"],
                        "time_seconds": record["time_seconds"],
                        "tokens": record.get("tokens", 0),
                        "errors": record.get("errors", 0),
                    },
                    "expectations": record["expectations"],
                    "notes": record["notes"],
                }
            )

    eval_ids = sorted({r["eval_id"] for runs_in_cfg in results.values() for r in runs_in_cfg})

    return BenchmarkSnapshot(
        metadata={
            "skill_name": skill_name or "<skill-name>",
            "skill_path": skill_path or "<path/to/skill>",
            "executor_model": "<model-name>",
            "analyzer_model": "<model-name>",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": eval_ids,
            "runs_per_configuration": 3,
        },
        runs=runs,
        run_summary=run_summary,
        notes=[],
    )


def generate_markdown(benchmark: BenchmarkSnapshot) -> str:
    """Generate human-readable benchmark.md from benchmark data."""
    metadata = benchmark["metadata"]
    run_summary = benchmark["run_summary"]

    configs = [k for k in run_summary if k != "delta"]
    config_a = configs[0] if configs else "config_a"
    config_b = configs[1] if len(configs) >= 2 else "config_b"
    label_a = config_a.replace("_", " ").title()
    label_b = config_b.replace("_", " ").title()

    skill_name = metadata.get("skill_name", "<skill-name>")
    executor_model = metadata.get("executor_model", "<model-name>")
    timestamp = metadata.get("timestamp", "")
    evals_run = metadata.get("evals_run", [])
    runs_per_cfg = metadata.get("runs_per_configuration", 0)

    lines = [
        f"# Skill Benchmark: {skill_name}",
        "",
        f"**Model**: {executor_model}",
        f"**Date**: {timestamp}",
        f"**Evals**: {', '.join(map(str, evals_run))} ({runs_per_cfg} runs each per configuration)",
        "",
        "## Summary",
        "",
        f"| Metric | {label_a} | {label_b} | Delta |",
        "|--------|------------|---------------|-------|",
    ]

    a_summary = cast(RunSummaryEntry, run_summary.get(config_a, _empty_summary()))
    b_summary = cast(RunSummaryEntry, run_summary.get(config_b, _empty_summary()))
    delta = cast(DeltaEntry, run_summary.get("delta", DeltaEntry(pass_rate="—", time_seconds="—", tokens="—")))

    a_pr = a_summary["pass_rate"]
    b_pr = b_summary["pass_rate"]
    lines.append(
        f"| Pass Rate | {a_pr['mean'] * 100:.0f}% ± {a_pr['stddev'] * 100:.0f}% "
        f"| {b_pr['mean'] * 100:.0f}% ± {b_pr['stddev'] * 100:.0f}% "
        f"| {delta.get('pass_rate', '—')} |"
    )

    a_time = a_summary["time_seconds"]
    b_time = b_summary["time_seconds"]
    lines.append(
        f"| Time | {a_time['mean']:.1f}s ± {a_time['stddev']:.1f}s "
        f"| {b_time['mean']:.1f}s ± {b_time['stddev']:.1f}s "
        f"| {delta.get('time_seconds', '—')}s |"
    )

    a_tokens = a_summary["tokens"]
    b_tokens = b_summary["tokens"]
    lines.append(
        f"| Tokens | {a_tokens['mean']:.0f} ± {a_tokens['stddev']:.0f} "
        f"| {b_tokens['mean']:.0f} ± {b_tokens['stddev']:.0f} "
        f"| {delta.get('tokens', '—')} |"
    )

    if benchmark.get("notes"):
        lines.extend(["", "## Notes", ""])
        for note in benchmark["notes"]:
            lines.append(f"- {note}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate benchmark run results into summary statistics")
    parser.add_argument("benchmark_dir", type=Path, help="Path to the benchmark directory")
    parser.add_argument("--skill-name", default="", help="Name of the target being benchmarked")
    parser.add_argument("--skill-path", default="", help="Path to the target being benchmarked")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path for benchmark.json (default: <benchmark_dir>/benchmark.json)",
    )

    args = parser.parse_args()

    if not args.benchmark_dir.exists():
        print(f"Directory not found: {args.benchmark_dir}", file=sys.stderr)
        sys.exit(1)

    benchmark = generate_benchmark(args.benchmark_dir, args.skill_name, args.skill_path)

    output_json: Path = args.output or (args.benchmark_dir / "benchmark.json")
    output_md = output_json.with_suffix(".md")

    with open(output_json, "w") as f:
        json.dump(benchmark, f, indent=2)
    print(f"Generated: {output_json}")

    markdown = generate_markdown(benchmark)
    with open(output_md, "w") as f:
        _ = f.write(markdown)
    print(f"Generated: {output_md}")

    summary = benchmark["run_summary"]
    configs = [k for k in summary if k != "delta"]
    delta = cast(DeltaEntry, summary.get("delta", DeltaEntry(pass_rate="—", time_seconds="—", tokens="—")))

    print("\nSummary:")
    for config in configs:
        entry = cast(RunSummaryEntry, summary[config])
        pr = entry["pass_rate"]["mean"]
        label = config.replace("_", " ").title()
        print(f"  {label}: {pr * 100:.1f}% pass rate")
    print(f"  Delta:         {delta.get('pass_rate', '—')}")


if __name__ == "__main__":
    main()
