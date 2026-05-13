"""Tests for spec-plan validation hooks."""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).parent.parent.parent.parent)


class TestSpecPlanValidator:
    """Test spec_plan_validator.py Stop hook."""

    def test_allows_stop_when_plan_created(self):
        """Should allow stop when plan file exists for today."""
        with tempfile.TemporaryDirectory() as tmpdir:
            today = datetime.date.today().strftime("%Y-%m-%d")
            plan_path = Path(tmpdir) / "docs" / "plans" / f"{today}-test-feature.md"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text("# Test Plan\n\nStatus: PENDING\n")

            result = subprocess.run(
                [sys.executable, "pilot/hooks/spec_plan_validator.py"],
                input=json.dumps({"project_root": tmpdir, "stop_hook_active": False}),
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )

            assert result.returncode == 0, f"Should allow stop when plan exists. stderr: {result.stderr}"

    def test_blocks_stop_when_no_plan(self):
        """Should output block decision when no plan file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, "pilot/hooks/spec_plan_validator.py"],
                input=json.dumps({"project_root": tmpdir, "stop_hook_active": False}),
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )

            assert result.returncode == 0, f"Unexpected return code. stderr: {result.stderr}"
            assert "Plan file not created yet" in result.stdout

    def test_escape_hatch_allows_stop(self):
        """Should allow stop when stop_hook_active is true (escape hatch)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, "pilot/hooks/spec_plan_validator.py"],
                input=json.dumps({"project_root": tmpdir, "stop_hook_active": True}),
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )

            assert result.returncode == 0, f"Escape hatch should allow stop. stderr: {result.stderr}"

    def test_allows_stop_when_asking_user_question(self):
        """Should allow stop when AskUserQuestion was the last tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript = Path(tmpdir) / "transcript.jsonl"
            msg = {
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": "AskUserQuestion", "input": {}}]},
            }
            transcript.write_text(json.dumps(msg) + "\n")

            result = subprocess.run(
                [sys.executable, "pilot/hooks/spec_plan_validator.py"],
                input=json.dumps(
                    {
                        "project_root": tmpdir,
                        "stop_hook_active": False,
                        "transcript_path": str(transcript),
                    }
                ),
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )

            assert result.returncode == 0, f"Should allow stop during AskUserQuestion. stderr: {result.stderr}"
