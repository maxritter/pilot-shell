"""Tests for spec_handoff_resume — UserPromptSubmit hook that resumes /spec
implementation after a model-switch handoff.

Behavior contract:
- No sentinel present → exit 0, no output, no side effects.
- Fresh sentinel + valid active_plan.json → emit `additionalContext` instructing
  the agent to invoke `Skill('spec-implement', '<plan-path>')`, then delete the
  sentinel.
- Stale sentinel (>1h) → delete the sentinel, emit NO additionalContext.
- Sentinel without an active_plan.json (e.g. `/clear` wiped it) → delete the
  sentinel, emit NO additionalContext.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parent.parent / "spec_handoff_resume.py"
TEST_SESSION_ID = "test-spec-handoff-resume"


def _test_session_dir() -> Path:
    return Path.home() / ".pilot" / "sessions" / TEST_SESSION_ID


def _write_active_plan(plan_path: Path, status: str = "PENDING") -> None:
    session_dir = _test_session_dir()
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "active_plan.json").write_text(json.dumps({"plan_path": str(plan_path), "status": status}))


@pytest.fixture(autouse=True)
def clear_session_state():
    session_dir = _test_session_dir()
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
    yield
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)


def _run(input_data: dict | None = None, project_root: Path | None = None) -> tuple[int, str, str]:
    env = {**os.environ, "PILOT_SESSION_ID": TEST_SESSION_ID}
    if project_root is not None:
        env["CLAUDE_PROJECT_ROOT"] = str(project_root)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(input_data or {}),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def _additional_context(stdout: str) -> str | None:
    """Extract the additionalContext string from hook stdout, or None if absent."""
    raw = stdout.strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    hso = data.get("hookSpecificOutput") if isinstance(data, dict) else None
    if not isinstance(hso, dict):
        return None
    ctx = hso.get("additionalContext")
    return ctx if isinstance(ctx, str) else None


class TestResumeHook:
    def test_no_sentinel_is_no_op(self, tmp_path: Path) -> None:
        plan_file = tmp_path / "plan.md"
        plan_file.write_text("# Plan\n\nStatus: PENDING\nApproved: Yes\n")
        _write_active_plan(plan_file)

        exit_code, stdout, _ = _run()

        assert exit_code == 0
        assert stdout.strip() == ""
        assert _additional_context(stdout) is None

    def test_fresh_sentinel_emits_resume_instruction_and_unlinks(self, tmp_path: Path) -> None:
        plan_file = tmp_path / "2026-05-22-plan.md"
        plan_file.write_text("# Plan\n\nStatus: PENDING\nApproved: Yes\n")
        _write_active_plan(plan_file)

        sentinel = _test_session_dir() / "spec-handoff-pending"
        sentinel.touch()

        exit_code, stdout, _ = _run()

        assert exit_code == 0
        ctx = _additional_context(stdout)
        assert ctx is not None, "Hook must emit additionalContext when sentinel is fresh"
        assert str(plan_file) in ctx, "Resume instruction must include the absolute plan path"
        assert "spec-implement" in ctx, "Resume instruction must reference spec-implement skill"
        assert not sentinel.exists(), "Sentinel must be unlinked after one consume"

    def test_stale_sentinel_is_unlinked_silently(self, tmp_path: Path) -> None:
        import time as _time

        plan_file = tmp_path / "plan.md"
        plan_file.write_text("# Plan\n\nStatus: PENDING\nApproved: Yes\n")
        _write_active_plan(plan_file)

        sentinel = _test_session_dir() / "spec-handoff-pending"
        sentinel.touch()
        stale = _time.time() - 7200  # 2 hours old
        os.utime(sentinel, (stale, stale))

        exit_code, stdout, _ = _run()

        assert exit_code == 0
        assert _additional_context(stdout) is None, "Stale sentinel must not produce a resume instruction"
        assert not sentinel.exists(), "Stale sentinel must be unlinked"

    def test_sentinel_without_active_plan_is_unlinked_silently(self) -> None:
        """If active_plan.json is missing (e.g. /clear wiped it), the hook cannot
        produce a resume instruction — drop the sentinel and exit quietly."""
        sentinel = _test_session_dir() / "spec-handoff-pending"
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.touch()

        exit_code, stdout, _ = _run()

        assert exit_code == 0
        assert _additional_context(stdout) is None
        assert not sentinel.exists()

    def test_relative_plan_path_is_resolved_against_project_root(self, tmp_path: Path) -> None:
        plans_dir = tmp_path / "docs" / "plans"
        plans_dir.mkdir(parents=True)
        plan_file = plans_dir / "2026-05-22-relative.md"
        plan_file.write_text("# Plan\n\nStatus: PENDING\nApproved: Yes\n")

        # Write a RELATIVE plan path into active_plan.json.
        session_dir = _test_session_dir()
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "active_plan.json").write_text(
            json.dumps({"plan_path": "docs/plans/2026-05-22-relative.md", "status": "PENDING"})
        )

        sentinel = _test_session_dir() / "spec-handoff-pending"
        sentinel.touch()

        exit_code, stdout, _ = _run(project_root=tmp_path)

        assert exit_code == 0
        ctx = _additional_context(stdout)
        assert ctx is not None
        assert str(plan_file) in ctx, "Relative path must be resolved against CLAUDE_PROJECT_ROOT"
        assert not sentinel.exists()
