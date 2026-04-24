"""Live progress reporting for the benchmark runner.

Thread-safe state machine + console renderer. Workers fire `on_started` /
`on_completed` / `on_failed` events from any thread; a background snapshot
thread prints periodic status while runs are in-flight; `summary()` produces
the final aggregate table.

ANSI color is auto-disabled when stdout is not a TTY.
"""

from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass
from typing import Final, Literal, TextIO, final

RunStatus = Literal["queued", "running", "completed", "failed"]

_RESET: Final = "\x1b[0m"
_BOLD: Final = "\x1b[1m"
_DIM: Final = "\x1b[2m"
_GREEN: Final = "\x1b[32m"
_RED: Final = "\x1b[31m"
_YELLOW: Final = "\x1b[33m"
_CYAN: Final = "\x1b[36m"


@final
@dataclass(slots=True)
class RunState:
    """Per-run state — one entry per (eval, config, run_idx) triple."""

    eval_id: int
    eval_name: str
    config: str
    run_idx: int
    status: RunStatus = "queued"
    started_at: float | None = None
    finished_at: float | None = None
    duration_s: float | None = None
    tokens: int | None = None
    failure_reason: str | None = None

    @property
    def label(self) -> str:
        return f"eval-{self.eval_id} {self.config:<14} run-{self.run_idx}"

    def elapsed(self, now: float) -> float | None:
        if self.started_at is None:
            return None
        end = self.finished_at if self.finished_at is not None else now
        return end - self.started_at


@final
@dataclass(frozen=True, slots=True)
class PlanHeader:
    """All inputs needed to render the pre-run plan banner."""

    config_path: str
    target_type: str
    target_path: str
    output_dir: str
    n_evals: int
    n_configs: int
    n_runs: int
    workers: int
    executor_model: str
    grader_model: str


def _format_duration(seconds: float) -> str:
    """Format seconds as `Hh Mm Ss`, dropping leading zero units."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, sec = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m{sec:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m{sec:02d}s"


def _format_tokens(tokens: int) -> str:
    """Compact token count: 12345 → `12.3k`, 1234567 → `1.2M`."""
    if tokens < 1_000:
        return str(tokens)
    if tokens < 1_000_000:
        return f"{tokens / 1_000:.1f}k"
    return f"{tokens / 1_000_000:.1f}M"


@final
class ProgressReporter:
    """Thread-safe progress tracker with a periodic snapshot thread."""

    total: int
    workers: int
    snapshot_interval: float
    use_color: bool

    def __init__(
        self,
        total: int,
        *,
        workers: int,
        snapshot_interval: float = 30.0,
        stream: TextIO | None = None,
        use_color: bool | None = None,
    ) -> None:
        self.total = total
        self.workers = workers
        self.snapshot_interval = snapshot_interval
        self._stream: TextIO = stream if stream is not None else sys.stdout
        if use_color is None:
            use_color = self._stream.isatty()
        self.use_color = use_color
        self._runs: dict[tuple[int, str, int], RunState] = {}
        self._lock: threading.Lock = threading.Lock()
        self._stop: threading.Event = threading.Event()
        self._snapshot_thread: threading.Thread | None = None
        self._started_at: float = 0.0

    def _color(self, code: str, text: str) -> str:
        return f"{code}{text}{_RESET}" if self.use_color else text

    def _print(self, line: str) -> None:
        with self._lock:
            _ = self._stream.write(line + "\n")
            self._stream.flush()

    def start(self) -> None:
        self._started_at = time.monotonic()
        self._snapshot_thread = threading.Thread(target=self._snapshot_loop, name="benchmark-progress", daemon=True)
        self._snapshot_thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._snapshot_thread is not None:
            self._snapshot_thread.join(timeout=2.0)

    def register(self, eval_id: int, eval_name: str, config: str, run_idx: int) -> None:
        """Pre-register a run as queued. Idempotent."""
        key = (eval_id, config, run_idx)
        with self._lock:
            if key not in self._runs:
                self._runs[key] = RunState(eval_id=eval_id, eval_name=eval_name, config=config, run_idx=run_idx)

    def on_started(self, eval_id: int, config: str, run_idx: int) -> None:
        key = (eval_id, config, run_idx)
        with self._lock:
            run = self._runs.get(key)
            if run is None:
                return
            run.status = "running"
            run.started_at = time.monotonic()

    def on_completed(
        self,
        eval_id: int,
        config: str,
        run_idx: int,
        *,
        duration_s: float,
        tokens: int,
    ) -> None:
        key = (eval_id, config, run_idx)
        now = time.monotonic()
        with self._lock:
            run = self._runs.get(key)
            if run is None:
                return
            run.status = "completed"
            run.finished_at = now
            run.duration_s = duration_s
            run.tokens = tokens
            done, in_flight, queued, failed = self._counts_unlocked()
            label = run.label
        del queued
        check = self._color(_GREEN, "✓")
        meta_text = f"{_format_duration(duration_s)}, {_format_tokens(tokens)} tok"
        meta = self._color(_DIM, meta_text)
        eta = self._eta_line(done, failed, in_flight)
        self._print(f"  [{done + failed}/{self.total}] {check} {label}  {meta}{eta}")

    def on_failed(self, eval_id: int, config: str, run_idx: int, reason: str) -> None:
        key = (eval_id, config, run_idx)
        now = time.monotonic()
        with self._lock:
            run = self._runs.get(key)
            if run is None:
                return
            run.status = "failed"
            run.finished_at = now
            run.failure_reason = reason
            run.duration_s = run.elapsed(now)
            done, in_flight, queued, failed = self._counts_unlocked()
            label = run.label
        del queued
        cross = self._color(_RED, "✗")
        why = self._color(_RED, f"failed: {reason}")
        eta = self._eta_line(done, failed, in_flight)
        self._print(f"  [{done + failed}/{self.total}] {cross} {label}  {why}{eta}")

    def summary(self) -> str:
        """Render the final aggregate block. Call after all runs complete."""
        with self._lock:
            total_elapsed = time.monotonic() - self._started_at
            done, in_flight, queued, failed = self._counts_unlocked()
            by_config: dict[str, list[RunState]] = {}
            for run in self._runs.values():
                by_config.setdefault(run.config, []).append(run)

        lines: list[str] = []
        lines.append("")
        lines.append(self._color(_BOLD, "─" * 72))
        header = self._color(_BOLD, f"Benchmark complete in {_format_duration(total_elapsed)}")
        lines.append(f"{header}  ({done} ok, {failed} failed, {in_flight + queued} skipped)")
        lines.append(self._color(_BOLD, "─" * 72))
        for config in sorted(by_config):
            runs = by_config[config]
            total_runs = len(runs)
            ok_runs = [r for r in runs if r.status == "completed"]
            fail_runs = [r for r in runs if r.status == "failed"]
            avg_s = sum(r.duration_s or 0 for r in ok_runs) / len(ok_runs) if ok_runs else 0.0
            sum_tokens = sum(r.tokens or 0 for r in ok_runs)
            label = config.replace("_", " ").title()
            stats_text = f"avg {_format_duration(avg_s)}, {_format_tokens(sum_tokens)} tok total"
            colored_label = self._color(_CYAN, label)
            colored_stats = self._color(_DIM, stats_text)
            row = f"  {colored_label:<28} ok {len(ok_runs)}/{total_runs}  {colored_stats}"
            lines.append(row)
            for fr in fail_runs:
                reason = fr.failure_reason or "unknown"
                lines.append(f"    {self._color(_RED, '✗')} {fr.label}: {reason}")
        lines.append(self._color(_BOLD, "─" * 72))
        return "\n".join(lines)

    def _counts_unlocked(self) -> tuple[int, int, int, int]:
        """Return (done, in_flight, queued, failed). Caller holds the lock."""
        done = 0
        in_flight = 0
        queued = 0
        failed = 0
        for r in self._runs.values():
            if r.status == "completed":
                done += 1
            elif r.status == "running":
                in_flight += 1
            elif r.status == "queued":
                queued += 1
            elif r.status == "failed":
                failed += 1
        return done, in_flight, queued, failed

    def _eta_line(self, done: int, failed: int, in_flight: int) -> str:
        """Compact ETA string appended to completion lines."""
        finished = done + failed
        remaining = self.total - finished - in_flight
        if done < 2:
            return self._color(_DIM, f"  · {in_flight} in-flight, {remaining} queued")
        elapsed = time.monotonic() - self._started_at
        avg_per_finished = elapsed / max(1, finished)
        remaining_runs = remaining + in_flight
        eta_s = (remaining_runs * avg_per_finished) / max(1, self.workers)
        tail = f"{in_flight} in-flight, {remaining} queued · ETA {_format_duration(eta_s)}"
        return self._color(_DIM, f"  · {tail}")

    def _snapshot_loop(self) -> None:
        while not self._stop.wait(self.snapshot_interval):
            self._render_snapshot()

    def _render_snapshot(self) -> None:
        now = time.monotonic()
        with self._lock:
            done, in_flight, queued, failed = self._counts_unlocked()
            running_runs = [(r.label, r.elapsed(now) or 0.0) for r in self._runs.values() if r.status == "running"]
            elapsed = now - self._started_at
        if in_flight == 0 and queued == 0:
            return
        running_runs.sort(key=lambda pair: -pair[1])
        head = (
            f"[snapshot {_format_duration(elapsed)} elapsed] "
            f"{done} done · {in_flight} in-flight · {queued} queued · {failed} failed"
        )
        self._print(self._color(_DIM, "  · " + head))
        for label, secs in running_runs[:3]:
            running_for = _format_duration(secs)
            self._print(self._color(_DIM, f"      ↳ {label} (running {running_for})"))


def render_plan_header(plan: PlanHeader, *, use_color: bool = True) -> str:
    """Pretty header printed before runs start. Pure function, easy to test."""

    def color(code: str, text: str) -> str:
        return f"{code}{text}{_RESET}" if use_color else text

    total = plan.n_evals * plan.n_configs * plan.n_runs
    plural = "s" if plan.n_runs != 1 else ""
    plan_line = (
        f"  Plan:      {plan.n_evals} evals × {plan.n_configs} configs × "
        f"{plan.n_runs} run{plural} = {total} runs ({plan.workers} workers)"
    )
    models_line = f"  Models:    executor={color(_CYAN, plan.executor_model)}, grader={color(_CYAN, plan.grader_model)}"
    lines = [
        color(_BOLD, "benchmark runner"),
        f"  Config:    {plan.config_path}",
        f"  Target:    {plan.target_type} @ {plan.target_path}",
        f"  Output:    {plan.output_dir}",
        plan_line,
        models_line,
        "",
        color(_YELLOW, "Running..."),
    ]
    return "\n".join(lines)
