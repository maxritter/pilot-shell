"""Tests for scripts.progress — formatters, RunState, ProgressReporter."""

from __future__ import annotations

import io

from scripts.progress import (
    PlanHeader,
    ProgressReporter,
    RunState,
    _format_duration,
    _format_tokens,
    render_plan_header,
)


class TestFormatDuration:
    def test_seconds(self) -> None:
        assert _format_duration(7.5) == "7.5s"
        assert _format_duration(0.1) == "0.1s"

    def test_minutes_and_seconds(self) -> None:
        assert _format_duration(75) == "1m15s"
        assert _format_duration(3599) == "59m59s"

    def test_hours(self) -> None:
        assert _format_duration(3600) == "1h00m00s"
        assert _format_duration(7325) == "2h02m05s"


class TestFormatTokens:
    def test_under_1k(self) -> None:
        assert _format_tokens(0) == "0"
        assert _format_tokens(999) == "999"

    def test_thousands(self) -> None:
        assert _format_tokens(1_000) == "1.0k"
        assert _format_tokens(12_345) == "12.3k"

    def test_millions(self) -> None:
        assert _format_tokens(1_500_000) == "1.5M"


class TestRunState:
    def test_label_includes_eval_config_run(self) -> None:
        state = RunState(eval_id=2, eval_name="eval-2", config="with_skill", run_idx=1)
        assert "eval-2" in state.label
        assert "with_skill" in state.label
        assert "run-1" in state.label

    def test_elapsed_returns_none_when_unstarted(self) -> None:
        state = RunState(eval_id=1, eval_name="x", config="with_skill", run_idx=1)
        assert state.elapsed(now=100.0) is None

    def test_elapsed_uses_finished_at_when_present(self) -> None:
        state = RunState(eval_id=1, eval_name="x", config="with_skill", run_idx=1)
        state.started_at = 10.0
        state.finished_at = 25.0
        assert state.elapsed(now=999.0) == 15.0

    def test_elapsed_uses_now_when_in_flight(self) -> None:
        state = RunState(eval_id=1, eval_name="x", config="with_skill", run_idx=1)
        state.started_at = 10.0
        assert state.elapsed(now=42.5) == 32.5


class TestProgressReporter:
    def _make(self, total: int = 4) -> tuple[ProgressReporter, io.StringIO]:
        stream = io.StringIO()
        reporter = ProgressReporter(
            total,
            workers=2,
            snapshot_interval=999,
            stream=stream,
            use_color=False,
        )
        return reporter, stream

    def test_register_then_complete_emits_progress_line(self) -> None:
        reporter, stream = self._make(total=2)
        reporter.register(1, "eval-1", "with_skill", 1)
        reporter.start()
        try:
            reporter.on_started(1, "with_skill", 1)
            reporter.on_completed(1, "with_skill", 1, duration_s=4.0, tokens=12_000)
        finally:
            reporter.stop()
        out = stream.getvalue()
        assert "[1/2]" in out
        assert "eval-1" in out
        assert "with_skill" in out
        assert "4.0s" in out
        assert "12.0k tok" in out

    def test_failure_records_reason(self) -> None:
        reporter, stream = self._make(total=1)
        reporter.register(1, "eval-1", "without_skill", 1)
        reporter.start()
        try:
            reporter.on_started(1, "without_skill", 1)
            reporter.on_failed(1, "without_skill", 1, "timeout")
        finally:
            reporter.stop()
        out = stream.getvalue()
        assert "✗" in out
        assert "failed: timeout" in out

    def test_summary_shows_per_config_aggregates(self) -> None:
        reporter, _ = self._make(total=4)
        reporter.register(1, "eval-1", "with_skill", 1)
        reporter.register(2, "eval-2", "with_skill", 1)
        reporter.register(1, "eval-1", "without_skill", 1)
        reporter.register(2, "eval-2", "without_skill", 1)
        reporter.start()
        try:
            reporter.on_started(1, "with_skill", 1)
            reporter.on_completed(1, "with_skill", 1, duration_s=10.0, tokens=1000)
            reporter.on_started(2, "with_skill", 1)
            reporter.on_completed(2, "with_skill", 1, duration_s=20.0, tokens=2000)
            reporter.on_started(1, "without_skill", 1)
            reporter.on_failed(1, "without_skill", 1, "no-result-event")
        finally:
            reporter.stop()
        summary = reporter.summary()
        assert "Benchmark complete" in summary
        assert "With Skill" in summary
        assert "ok 2/2" in summary
        # without_skill: 1 failed + 1 queued (registered but not started) = 0 ok / 2 total
        assert "ok 0/2" in summary
        assert "no-result-event" in summary

    def test_eta_present_after_two_completions(self) -> None:
        reporter, stream = self._make(total=4)
        for run_idx in range(1, 4):
            reporter.register(run_idx, f"eval-{run_idx}", "with_skill", 1)
        reporter.register(4, "eval-4", "with_skill", 1)
        reporter.start()
        try:
            reporter.on_started(1, "with_skill", 1)
            reporter.on_completed(1, "with_skill", 1, duration_s=1.0, tokens=10)
            reporter.on_started(2, "with_skill", 1)
            reporter.on_completed(2, "with_skill", 1, duration_s=1.0, tokens=10)
        finally:
            reporter.stop()
        out = stream.getvalue()
        assert "ETA" in out


class TestRenderPlanHeader:
    def test_includes_all_fields_no_color(self) -> None:
        plan = PlanHeader(
            config_path="evals.json",
            target_type="skill",
            target_path="pilot/skills/prd",
            output_dir="benchmarks/prd/runs/x",
            n_evals=6,
            n_configs=2,
            n_runs=1,
            workers=4,
            executor_model="claude-opus-4-7",
            grader_model="claude-opus-4-7",
        )
        rendered = render_plan_header(plan, use_color=False)
        assert "evals.json" in rendered
        assert "skill @ pilot/skills/prd" in rendered
        assert "6 evals × 2 configs × 1 run = 12 runs" in rendered
        assert "claude-opus-4-7" in rendered
        # No ANSI when use_color=False
        assert "\x1b[" not in rendered

    def test_color_codes_present_when_enabled(self) -> None:
        plan = PlanHeader(
            config_path="x",
            target_type="rules",
            target_path="rules/y",
            output_dir="o",
            n_evals=1,
            n_configs=1,
            n_runs=2,
            workers=1,
            executor_model="m",
            grader_model="m",
        )
        rendered = render_plan_header(plan, use_color=True)
        assert "\x1b[" in rendered
        # n_runs=2 → "2 runs" (plural). n_runs=1 → "1 run" (singular).
        assert "× 2 runs" in rendered
        assert "× 2 run " not in rendered  # would indicate broken pluralization
