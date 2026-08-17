"""Tests for tool_token_saver hook."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))
from tool_token_saver import _rewrite_command, run_tool_token_saver


class TestRewriteCommand:
    @patch("tool_token_saver.subprocess.run")
    def test_accepts_rewrite_when_rtk_exits_nonzero_with_output(self, mock_run):
        """rtk rewrite exits 3 on success — hook must accept non-empty stdout regardless of exit code."""
        mock_run.return_value = MagicMock(
            returncode=3,
            stdout="rtk git status\n",
            stderr="",
        )
        result = _rewrite_command("git status")
        assert result == "rtk git status"

    @patch("tool_token_saver.subprocess.run")
    def test_returns_none_when_rtk_produces_no_output(self, mock_run):
        """No stdout means no rewrite available, regardless of exit code."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="",
        )
        assert _rewrite_command("echo hi") is None

    @patch("tool_token_saver.subprocess.run")
    def test_returns_none_when_rewrite_equals_original(self, mock_run):
        """If rtk echoes back the same command, there's no savings."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="echo hi\n",
            stderr="",
        )
        assert _rewrite_command("echo hi") is None

    @patch("tool_token_saver.subprocess.run")
    def test_accepts_rewrite_on_exit_zero(self, mock_run):
        """Normal exit 0 with output still works."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="rtk ls\n",
            stderr="",
        )
        assert _rewrite_command("ls") == "rtk ls"

    @patch("tool_token_saver.subprocess.run")
    def test_returns_none_on_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="rtk", timeout=5)
        assert _rewrite_command("git status") is None

    @patch("tool_token_saver.subprocess.run")
    def test_returns_none_on_os_error(self, mock_run):
        mock_run.side_effect = OSError("not found")
        assert _rewrite_command("git status") is None


def test_rewrite_preserves_codex_native_permission_decision(capsys):
    payload = {"tool_input": {"command": "git status", "timeout": 10}}

    with (
        patch("tool_token_saver.sys.stdin", io.StringIO(json.dumps(payload))),
        patch("tool_token_saver.shutil.which", return_value="/usr/local/bin/rtk"),
        patch("tool_token_saver._get_rtk_version", return_value=(0, 23, 0)),
        patch("tool_token_saver._rewrite_command", return_value="rtk git status"),
    ):
        assert run_tool_token_saver() == 0

    output = json.loads(capsys.readouterr().out)
    hook_output = output["hookSpecificOutput"]
    assert hook_output["updatedInput"] == {"command": "rtk git status", "timeout": 10}
    assert "permissionDecision" not in hook_output
    assert "permissionDecisionReason" not in hook_output
