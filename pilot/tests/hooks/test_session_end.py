"""Tests for session_end hook - handoff detection logic."""

from __future__ import annotations

import json
import os
import subprocess
from unittest.mock import patch

import pytest

import session_end


@pytest.mark.unit
def test_skips_stop_when_continuation_file_exists(tmp_path):
    """Worker stop is skipped during endless mode handoff (continuation file present)."""
    session_dir = tmp_path / "sessions" / "test-session"
    session_dir.mkdir(parents=True)
    (session_dir / "continuation.md").write_text("# Session Continuation")

    sessions_response = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=json.dumps({"count": 0}), stderr=""
    )

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "test-session"}),
        patch("session_end._sessions_base", return_value=tmp_path / "sessions"),
        patch("session_end.subprocess.run", return_value=sessions_response) as mock_run,
    ):
        result = session_end.main()

    assert result == 0
    assert mock_run.call_count == 1


@pytest.mark.unit
def test_skips_stop_when_active_plan_pending(tmp_path):
    """Worker stop is skipped when an active spec plan has PENDING status."""
    session_dir = tmp_path / "sessions" / "test-session"
    session_dir.mkdir(parents=True)
    plan_data = {"plan_path": "/fake/plan.md", "status": "PENDING"}
    (session_dir / "active_plan.json").write_text(json.dumps(plan_data))

    sessions_response = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=json.dumps({"count": 0}), stderr=""
    )

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "test-session"}),
        patch("session_end._sessions_base", return_value=tmp_path / "sessions"),
        patch("session_end.subprocess.run", return_value=sessions_response) as mock_run,
    ):
        result = session_end.main()

    assert result == 0
    assert mock_run.call_count == 1


@pytest.mark.unit
def test_skips_stop_when_active_plan_complete(tmp_path):
    """Worker stop is skipped when an active spec plan has COMPLETE status."""
    session_dir = tmp_path / "sessions" / "test-session"
    session_dir.mkdir(parents=True)
    plan_data = {"plan_path": "/fake/plan.md", "status": "COMPLETE"}
    (session_dir / "active_plan.json").write_text(json.dumps(plan_data))

    sessions_response = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=json.dumps({"count": 0}), stderr=""
    )

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "test-session"}),
        patch("session_end._sessions_base", return_value=tmp_path / "sessions"),
        patch("session_end.subprocess.run", return_value=sessions_response) as mock_run,
    ):
        result = session_end.main()

    assert result == 0
    assert mock_run.call_count == 1


@pytest.mark.unit
def test_stops_worker_when_plan_verified(tmp_path):
    """Worker stop proceeds when plan status is VERIFIED (workflow complete)."""
    session_dir = tmp_path / "sessions" / "test-session"
    session_dir.mkdir(parents=True)
    plan_data = {"plan_path": "/fake/plan.md", "status": "VERIFIED"}
    (session_dir / "active_plan.json").write_text(json.dumps(plan_data))

    sessions_response = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=json.dumps({"count": 0}), stderr=""
    )
    stop_response = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="", stderr=""
    )

    def run_side_effect(cmd, **_kwargs):
        if "sessions" in str(cmd):
            return sessions_response
        return stop_response

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "test-session"}),
        patch("session_end._sessions_base", return_value=tmp_path / "sessions"),
        patch("session_end.subprocess.run", side_effect=run_side_effect) as mock_run,
    ):
        result = session_end.main()

    assert result == 0
    assert mock_run.call_count == 2


@pytest.mark.unit
def test_stops_worker_when_no_plan_no_continuation(tmp_path):
    """Worker stop proceeds when no continuation file and no active plan exist."""
    session_dir = tmp_path / "sessions" / "test-session"
    session_dir.mkdir(parents=True)

    sessions_response = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=json.dumps({"count": 0}), stderr=""
    )
    stop_response = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="", stderr=""
    )

    def run_side_effect(cmd, **_kwargs):
        if "sessions" in str(cmd):
            return sessions_response
        return stop_response

    with (
        patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "/fake/plugin", "PILOT_SESSION_ID": "test-session"}),
        patch("session_end._sessions_base", return_value=tmp_path / "sessions"),
        patch("session_end.subprocess.run", side_effect=run_side_effect) as mock_run,
    ):
        result = session_end.main()

    assert result == 0
    assert mock_run.call_count == 2
