#!/usr/bin/env python3
"""Unified benchmark runner — orchestrates with/without comparison runs.

Handles two target types:
    skill  — installs the target skill under `with/.claude/skills/<name>/`
    rules  — copies rule file(s) into `with/.claude/rules/`

Both configs materialize an explicit `.claude/` directory under /tmp/pilot-bench-*/
so Claude Code's project-root discovery stops there and never walks UP into a
parent repo's `.claude/`. Each `claude -p` subprocess writes a stream-json
transcript; the final `result` event supplies duration_ms + usage (token counts).
Missing those required fields → run is marked FAILED rather than silently zeroed.
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.isolation import (
    detect_global_contamination,
    install_signal_handlers,
    isolate_global_contamination,
    recover_stale_manifests,
)
from scripts.progress import PlanHeader, ProgressReporter, render_plan_header
from scripts.utils import (
    DEFAULT_FALLBACK_MODEL,
    EvalSpec,
    ExecuteFailure,
    ExecuteResult,
    ExecuteSuccess,
    GraderFailure,
    GraderResult,
    GraderSuccess,
    ParsedResult,
    ResultEvent,
    TargetConfig,
    load_target_config,
    resolve_executor_model,
)


@dataclass(frozen=True, slots=True)
class RunConfig:
    """Bundled runtime parameters that apply to every eval × config × run."""

    runs: int
    model: str
    grader_model: str
    timeout: int
    grader_timeout: int
    skip_permissions: bool = False


@dataclass(frozen=True, slots=True)
class RunSpec:
    """One unit of pool work: a single (eval, config, run_idx) triple."""

    eval_obj: EvalSpec
    config_kind: str
    run_idx: int


__version__ = "0.1.0"

REQUIRED_RESULT_FIELDS = ("duration_ms", "usage")
TEMP_DIRS: list[Path] = []

SANDBOX_PLACEHOLDER = "{sandbox}"


def substitute_sandbox(prompt: str, sandbox_path: Path) -> str:
    """Replace {sandbox} in the prompt with the per-run isolated directory.

    This is the safe way for evals.json to reference filesystem paths — the path
    is unique per (eval, config, run) so concurrent or sequential runs can never
    read each other's outputs.
    """
    return prompt.replace(SANDBOX_PLACEHOLDER, str(sandbox_path))


def validate_prompt_isolation(prompt: str) -> str | None:
    """Return a warning string if the prompt hardcodes shared filesystem paths.

    Returns None when the prompt looks safe. Flags prompts that reference
    `/tmp/` without using {sandbox} — those paths are shared across `with`/
    `without` runs and cause the two configs to read each other's outputs,
    which produces false-positive pass rates.
    """
    if SANDBOX_PLACEHOLDER in prompt:
        return None
    if "/tmp/" not in prompt:
        return None
    return (
        "prompt references hardcoded `/tmp/...` paths without using "
        f"`{SANDBOX_PLACEHOLDER}` — the `with` and `without` runs will share "
        "these paths and contaminate each other. Either use relative paths "
        f"(cwd is already per-run isolated) or substitute `{SANDBOX_PLACEHOLDER}` "
        "so each run gets a unique directory."
    )


def _cleanup_temp_dirs() -> None:
    for path in TEMP_DIRS:
        shutil.rmtree(path, ignore_errors=True)


atexit.register(_cleanup_temp_dirs)


def parse_result_event(event: ResultEvent) -> ParsedResult:
    """Parse the final `result` event into a normalized timing dict.

    Raises ValueError if the event is not a result or required fields are missing.
    """
    if event.get("type") != "result":
        raise ValueError("not a result event")
    missing = [k for k in REQUIRED_RESULT_FIELDS if k not in event]
    if missing:
        raise ValueError(f"result event missing required fields: {missing}")

    usage = event.get("usage") or {}
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    cache_creation = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)

    duration_ms = event.get("duration_ms")
    if duration_ms is None:
        raise ValueError("result event missing duration_ms")
    return ParsedResult(
        duration_ms=duration_ms,
        duration_api_ms=event.get("duration_api_ms"),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_input_tokens=cache_creation,
        cache_read_input_tokens=cache_read,
        total_tokens=input_tokens + output_tokens + cache_creation + cache_read,
        total_cost_usd=event.get("total_cost_usd"),
        is_error=event.get("is_error", False),
        result_text=event.get("result", ""),
        stop_reason=event.get("stop_reason"),
        session_id=event.get("session_id"),
    )


def extract_final_result_event(lines: list[str]) -> ResultEvent | None:
    """Find the final `result` JSON event from a stream-json transcript.

    Tolerates malformed lines and non-JSON noise.
    """
    last_result = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") == "result":
            last_result = obj
    return last_result


def _safe_prefixes() -> tuple[Path, ...]:
    """Return the set of filesystem prefixes where target.path is allowed to live.

    Evaluated at runtime so /tmp resolves correctly (macOS /tmp → /private/tmp).
    """
    prefixes = [Path.home().resolve(), Path("/tmp").resolve()]
    var_folders = Path("/var/folders")
    if var_folders.exists():
        prefixes.append(var_folders.resolve())
    return tuple(prefixes)


def _validate_target_path(source_path: Path) -> None:
    """Reject paths that look like traversal attacks.

    We allow absolute paths (users legitimately benchmark skills anywhere on their
    system) but reject paths that are siblings of sensitive root dirs. The real
    risk is a malicious committed evals.json — guard against that by requiring the
    resolved path to be within the user's home tree or /tmp.
    """
    try:
        resolved = source_path.resolve()
    except OSError:
        raise ValueError(f"target.path could not be resolved: {source_path}")

    safe = any((resolved == p or resolved.is_relative_to(p)) for p in _safe_prefixes())
    if not safe:
        raise ValueError(
            f"target.path resolves outside approved locations: {resolved}\n"
            "Expected a path under your home directory or /tmp. "
            "If intentional, pass an approved location explicitly."
        )


def prepare_config_dir(target: TargetConfig, config_kind: str, tmp_root: Path) -> Path:
    """Create an ephemeral project dir with `.claude/` populated for the config.

    `config_kind` is "with" or "without".
    Returns the path to the project directory the subprocess will use as cwd.
    """
    dest = tmp_root / config_kind
    dest.mkdir(parents=True, exist_ok=True)
    claude_dir = dest / ".claude"
    claude_dir.mkdir(exist_ok=True)

    if config_kind == "without":
        return dest

    target_type = target.get("type", "skill")
    raw_path = target.get("path")
    if not raw_path:
        raise ValueError("target.path is required when config_kind is 'with'")
    source_path = Path(raw_path).expanduser().resolve()
    _validate_target_path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(f"target.path does not exist: {source_path}")

    if target_type == "skill":
        skill_name = target.get("name") or source_path.name
        skills_dir = claude_dir / "skills" / skill_name
        shutil.copytree(source_path, skills_dir)
    elif target_type == "rules":
        rules_dir = claude_dir / "rules"
        rules_dir.mkdir(exist_ok=True)
        if source_path.is_file():
            shutil.copy2(source_path, rules_dir / source_path.name)
        else:
            for md in source_path.rglob("*.md"):
                shutil.copy2(md, rules_dir / md.name)
    else:
        raise ValueError(f"unsupported target type: {target_type}")

    return dest


def _make_subprocess_env() -> dict[str, str]:
    """Strip CLAUDECODE so nested `claude -p` calls don't hit the nesting guard."""
    return {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}


def _write_failed_marker(run_dir: Path, reason: str, details: str = "") -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "failed.json").write_text(
        json.dumps(
            {
                "failed": True,
                "reason": reason,
                "details": details,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            indent=2,
        )
    )


def execute_run(
    *,
    prompt: str,
    config_dir: Path,
    run_dir: Path,
    model: str,
    timeout: int,
    skip_permissions: bool = False,
) -> ExecuteResult:
    """Run `claude -p` once in config_dir. Saves transcript + timing.json or failed.json."""
    run_dir.mkdir(parents=True, exist_ok=True)
    outputs = run_dir / "outputs"
    outputs.mkdir(exist_ok=True)

    cmd = [
        "claude",
        "-p",
        "--output-format",
        "stream-json",
        "--model",
        model,
    ]
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")

    try:
        completed = subprocess.run(
            cmd,
            input=prompt,
            cwd=str(config_dir),
            env=_make_subprocess_env(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        _write_failed_marker(run_dir, reason="timeout", details=f"after {timeout}s")
        return ExecuteFailure(success=False, reason="timeout")
    except FileNotFoundError:
        _write_failed_marker(run_dir, reason="claude-cli-not-found")
        return ExecuteFailure(success=False, reason="claude-cli-not-found")

    stdout = completed.stdout or ""
    _ = (outputs / "transcript.jsonl").write_text(stdout)
    if completed.stderr:
        _ = (outputs / "stderr.log").write_text(completed.stderr)

    lines = stdout.splitlines()
    result_event = extract_final_result_event(lines)
    if result_event is None:
        _write_failed_marker(
            run_dir,
            reason="no-result-event",
            details=f"exit={completed.returncode}; stdout head: {stdout[:500]}",
        )
        return ExecuteFailure(success=False, reason="no-result-event")

    try:
        parsed = parse_result_event(result_event)
    except ValueError as err:
        _write_failed_marker(run_dir, reason="malformed-result", details=str(err))
        return ExecuteFailure(success=False, reason="malformed-result")

    timing: dict[str, object] = {
        "duration_ms": parsed["duration_ms"],
        "duration_api_ms": parsed["duration_api_ms"],
        "total_duration_seconds": round(parsed["duration_ms"] / 1000.0, 3),
        "total_tokens": parsed["total_tokens"],
        "input_tokens": parsed["input_tokens"],
        "output_tokens": parsed["output_tokens"],
        "cache_creation_input_tokens": parsed["cache_creation_input_tokens"],
        "cache_read_input_tokens": parsed["cache_read_input_tokens"],
        "total_cost_usd": parsed["total_cost_usd"],
        "session_id": parsed["session_id"],
    }
    _ = (run_dir / "timing.json").write_text(json.dumps(timing, indent=2))
    _ = (outputs / "output.txt").write_text(parsed["result_text"])

    return ExecuteSuccess(
        success=True,
        duration_ms=parsed["duration_ms"],
        total_tokens=parsed["total_tokens"],
        run_dir=str(run_dir),
    )


def _run_grader(
    run_dir: Path,
    assertions: list[str],
    target_type: str,
    model: str,
    timeout: int,
    skip_permissions: bool = False,
) -> GraderResult:
    """Spawn the grader via `claude -p` with the grader.md prompt.

    Grader writes `grading.json` into run_dir. Returns a summary dict.
    """
    grader_prompt_path = Path(__file__).resolve().parent.parent / "agents" / "grader.md"
    grader_instructions = grader_prompt_path.read_text()

    outputs_dir = run_dir / "outputs"
    transcript = outputs_dir / "transcript.jsonl"
    expectations_block = "\n".join(f"- {a}" for a in assertions)
    prompt = (
        f"{grader_instructions}\n\n"
        f"# Grading task\n\n"
        f"- target_type: {target_type}\n"
        f"- transcript_path: {transcript}\n"
        f"- outputs_dir: {outputs_dir}\n\n"
        f"## Expectations\n\n"
        f"{expectations_block}\n\n"
        f"Write your JSON verdict to: {run_dir / 'grading.json'}"
    )

    grader_cmd = ["claude", "-p", "--output-format", "text", "--model", model]
    if skip_permissions:
        grader_cmd.append("--dangerously-skip-permissions")
    try:
        _ = subprocess.run(
            grader_cmd,
            input=prompt,
            env=_make_subprocess_env(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as err:
        _write_failed_marker(run_dir, reason="grader-failed", details=str(err))
        return GraderFailure(graded=False, reason="grader-failed")

    grading_file = run_dir / "grading.json"
    if not grading_file.exists():
        _write_failed_marker(run_dir, reason="grader-no-output")
        return GraderFailure(graded=False, reason="grader-no-output")
    try:
        grading_data: dict[str, object] = json.loads(grading_file.read_text())
        return GraderSuccess(graded=True, grading=grading_data)
    except json.JSONDecodeError as err:
        _write_failed_marker(run_dir, reason="grader-invalid-json", details=str(err))
        return GraderFailure(graded=False, reason="grader-invalid-json")


def _write_eval_metadata(eval_obj: EvalSpec, eval_dir: Path) -> None:
    """Write eval_metadata.json once per eval, before any run starts."""
    eval_id = eval_obj.get("id", 0)
    eval_name = eval_obj.get("name", f"eval-{eval_id}")
    eval_dir.mkdir(parents=True, exist_ok=True)
    (eval_dir / "eval_metadata.json").write_text(
        json.dumps(
            {
                "eval_id": eval_id,
                "eval_name": eval_name,
                "prompt": eval_obj.get("prompt", ""),
                "assertions": eval_obj.get("expectations", eval_obj.get("assertions", [])),
            }
        )
    )


def _run_single_run(
    spec: RunSpec,
    target: TargetConfig,
    output_dir: Path,
    run_cfg: RunConfig,
    reporter: ProgressReporter | None = None,
) -> None:
    """Execute one (eval, config, run_idx) — the unit of pool parallelism."""
    eval_obj = spec.eval_obj
    config_kind = spec.config_kind
    run_idx = spec.run_idx
    eval_id = eval_obj.get("id", 0)
    eval_dir = output_dir / f"eval-{eval_id}"
    eval_prompt = eval_obj.get("prompt", "")
    config_dir_name = "with_skill" if config_kind == "with" else "without_skill"
    run_dir = eval_dir / config_dir_name / f"run-{run_idx}"

    if reporter is not None:
        reporter.on_started(eval_id, config_dir_name, run_idx)

    tmp_root = Path(tempfile.mkdtemp(prefix="pilot-bench-", dir="/tmp"))
    TEMP_DIRS.append(tmp_root)
    try:
        cfg_dir = prepare_config_dir(target, config_kind, tmp_root)
        resolved_prompt = substitute_sandbox(eval_prompt, cfg_dir)
        result = execute_run(
            prompt=resolved_prompt,
            config_dir=cfg_dir,
            run_dir=run_dir,
            model=run_cfg.model,
            timeout=run_cfg.timeout,
            skip_permissions=run_cfg.skip_permissions,
        )
        if isinstance(result, ExecuteSuccess):
            _ = _run_grader(
                run_dir=run_dir,
                assertions=eval_obj.get("expectations", eval_obj.get("assertions", [])),
                target_type=target.get("type", "skill"),
                model=run_cfg.grader_model,
                timeout=run_cfg.grader_timeout,
                skip_permissions=run_cfg.skip_permissions,
            )
            if reporter is not None:
                reporter.on_completed(
                    eval_id,
                    config_dir_name,
                    run_idx,
                    duration_s=result.duration_ms / 1000.0,
                    tokens=result.total_tokens,
                )
        else:
            if reporter is not None:
                reporter.on_failed(eval_id, config_dir_name, run_idx, result.reason)
    except Exception as exc:
        if reporter is not None:
            reporter.on_failed(eval_id, config_dir_name, run_idx, f"worker-error: {exc}")
        raise
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
        if tmp_root in TEMP_DIRS:
            TEMP_DIRS.remove(tmp_root)


def _announce_contamination(target: TargetConfig, isolate_global: bool) -> list[Path]:
    """Log contamination status and return the paths that should be hidden.

    Returns an empty list when isolation is disabled (but still warns the user
    about detected-but-not-hidden duplicates so silent contamination is impossible).
    """
    suspects = detect_global_contamination(target)
    if not suspects:
        return []
    if isolate_global:
        print(
            f"  🛡  auto-isolating {len(suspects)} global counterpart(s) of the target in ~/.claude/ "
            "so the `without` config is truly without it:",
            file=sys.stderr,
        )
        for s in suspects:
            print(f"       {s}", file=sys.stderr)
        return suspects
    print(
        f"  ⚠  --no-isolate-global: {len(suspects)} global counterpart(s) of the target "
        "will contaminate the `without` config (use for realistic 'with + without' measurement):",
        file=sys.stderr,
    )
    for s in suspects:
        print(f"       {s}", file=sys.stderr)
    return []


def _warn_prompt_contamination(evals: list[EvalSpec]) -> None:
    for eval_obj in evals:
        warning = validate_prompt_isolation(eval_obj.get("prompt", ""))
        if warning:
            eval_id = eval_obj.get("id", 0)
            eval_name = eval_obj.get("name", f"eval-{eval_id}")
            print(f"  ⚠  eval-{eval_id} ({eval_name}): {warning}", file=sys.stderr)


def run_benchmark(
    config_path: Path,
    output_dir: Path,
    run_cfg: RunConfig,
    configs: list[str],
    workers: int,
    isolate_global: bool = True,
) -> int:
    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        return 1

    data: dict[str, object] = json.loads(config_path.read_text())
    target = load_target_config(config_path)
    target_path_str = target.get("path", "")
    if "name" not in target and target_path_str:
        target["name"] = Path(target_path_str).name

    raw_evals = data.get("evals")
    evals: list[EvalSpec] = list(raw_evals) if isinstance(raw_evals, list) else []
    if not evals:
        print("No evals in config.", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    _warn_prompt_contamination(evals)
    to_hide = _announce_contamination(target, isolate_global)

    plan = PlanHeader(
        config_path=str(config_path),
        target_type=target.get("type", "skill"),
        target_path=target_path_str,
        output_dir=str(output_dir),
        n_evals=len(evals),
        n_configs=len(configs),
        n_runs=run_cfg.runs,
        workers=workers,
        executor_model=run_cfg.model,
        grader_model=run_cfg.grader_model,
    )
    use_color = sys.stdout.isatty()
    print(render_plan_header(plan, use_color=use_color))

    for eval_obj in evals:
        eval_id = eval_obj.get("id", 0)
        _write_eval_metadata(eval_obj, output_dir / f"eval-{eval_id}")

    total_runs = len(evals) * len(configs) * run_cfg.runs
    reporter = ProgressReporter(total_runs, workers=workers, use_color=use_color)
    specs: list[RunSpec] = []
    for eval_obj in evals:
        eval_id = eval_obj.get("id", 0)
        eval_name = eval_obj.get("name", f"eval-{eval_id}")
        for cfg in configs:
            cfg_dir_name = "with_skill" if cfg == "with" else "without_skill"
            for run_idx in range(1, run_cfg.runs + 1):
                reporter.register(eval_id, eval_name, cfg_dir_name, run_idx)
                specs.append(RunSpec(eval_obj=eval_obj, config_kind=cfg, run_idx=run_idx))

    reporter.start()
    try:
        with isolate_global_contamination(to_hide):
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_run_single_run, spec, target, output_dir, run_cfg, reporter) for spec in specs]
                for fut in as_completed(futures):
                    try:
                        fut.result()
                    except Exception as exc:
                        print(f"Worker error (run may have partial results): {exc}", file=sys.stderr)
    finally:
        reporter.stop()

    print(reporter.summary())

    try:
        from scripts import aggregate_benchmark as agg
    except ImportError as err:
        print(f"Failed to import aggregate_benchmark: {err}", file=sys.stderr)
        return 1
    benchmark = agg.generate_benchmark(output_dir, skill_name=target.get("name", ""), skill_path=target_path_str)
    benchmark["metadata"]["target_type"] = target.get("type", "skill")
    benchmark["metadata"]["target_name"] = target.get("name", "")
    benchmark["metadata"]["target_path"] = target_path_str
    benchmark["metadata"]["executor_model"] = run_cfg.model
    benchmark["metadata"]["runs_per_configuration"] = run_cfg.runs

    _ = (output_dir / "benchmark.json").write_text(json.dumps(benchmark, indent=2))
    _ = (output_dir / "benchmark.md").write_text(agg.generate_markdown(benchmark))
    print(f"Wrote {output_dir / 'benchmark.json'}")
    return 0


def main() -> None:
    install_signal_handlers()
    recover_stale_manifests()

    parser = argparse.ArgumentParser(description="benchmark runner — run before/after comparison evaluations")
    parser.add_argument("--config", type=Path, help="Path to evals.json")
    parser.add_argument("--output", type=Path, help="Output directory (default: benchmarks/<target>/runs/<ts>/)")
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Runs per eval × config (default: 1 — bump for variance analysis)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Executor model. Default: skill's frontmatter `model:` (alias → ID), "
            f"falling back to {DEFAULT_FALLBACK_MODEL} for rules or skills without one."
        ),
    )
    parser.add_argument(
        "--grader-model",
        default=None,
        help=("Grader model. Default: same as --model so executor and grader stay matched."),
    )
    parser.add_argument(
        "--configs",
        default="with,without",
        help="Comma-separated list of configs: with,without (default: with,without)",
    )
    parser.add_argument("--timeout", type=int, default=600, help="Per-run timeout seconds (default: 600)")
    parser.add_argument("--grader-timeout", type=int, default=300, help="Grader timeout seconds (default: 300)")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument(
        "--skip-permissions",
        action="store_true",
        default=False,
        help="Pass --dangerously-skip-permissions to all claude -p calls. Required for automated "
        "runs (no interactive terminal). Grants the executor and grader permission to use any tool "
        "without prompting — only enable when running in a trusted, isolated environment.",
    )
    parser.add_argument(
        "--no-isolate-global",
        action="store_true",
        default=False,
        help="Do not hide ~/.claude/ counterparts of the target during the run. "
        "Default: auto-hide. Use when you want to measure the target IN ADDITION to "
        "globally-loaded guidance (realistic 'day-to-day' measurement).",
    )
    parser.add_argument(
        "--restore-hidden",
        action="store_true",
        default=False,
        help="Recover any .pilot-bench-hidden-* files left behind by a crashed prior "
        "run and exit. No benchmark is executed.",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args()

    if args.version:
        print(f"benchmark runner {__version__}")
        sys.exit(0)

    if args.restore_hidden:
        restored = recover_stale_manifests()
        print(f"Restored {restored} hidden path(s).")
        sys.exit(0)

    if args.config is None:
        parser.error("--config is required (unless --version or --restore-hidden)")

    if not args.config.exists():
        print(f"Config not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    if not configs:
        parser.error("--configs must list at least one of: with, without")

    target = load_target_config(args.config)
    output_dir = args.output
    if output_dir is None:
        name = target.get("name") or Path(target.get("path", "target")).name
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        output_dir = Path("benchmarks") / name / "runs" / ts

    executor_model: str = args.model or resolve_executor_model(target)
    grader_model: str = args.grader_model or executor_model

    run_cfg = RunConfig(
        runs=args.runs,
        model=executor_model,
        grader_model=grader_model,
        timeout=args.timeout,
        grader_timeout=args.grader_timeout,
        skip_permissions=args.skip_permissions,
    )
    code = run_benchmark(
        config_path=args.config,
        output_dir=output_dir,
        run_cfg=run_cfg,
        configs=configs,
        workers=args.workers,
        isolate_global=not args.no_isolate_global,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
