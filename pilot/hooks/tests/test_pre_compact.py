"""Tests for pre_compact hook."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPreCompactHook:
    """Test PreCompact hook state capture."""

    @patch("pre_compact.urllib.request.urlopen")
    @patch("pre_compact.read_hook_stdin")
    @patch("pre_compact.get_session_plan_path")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123"})
    def test_captures_active_plan_state(self, mock_plan_path, mock_stdin, mock_urlopen, capsys):
        """Should capture active plan state from session data."""
        from pre_compact import run_pre_compact

        with tempfile.TemporaryDirectory() as tmpdir:
            plan_json = Path(tmpdir) / "active_plan.json"
            plan_json.write_text(
                json.dumps(
                    {
                        "status": "PENDING",
                        "plan_path": "docs/plans/2026-02-16-test.md",
                        "current_task": 3,
                    }
                )
            )
            mock_plan_path.return_value = plan_json

            mock_stdin.return_value = {
                "session_id": "test123",
                "trigger": "auto",
                "custom_instructions": "",
            }

            mock_response = MagicMock()
            mock_response.status = 200
            mock_urlopen.return_value = mock_response

            result = run_pre_compact()

            assert mock_urlopen.called
            call_args = mock_urlopen.call_args
            req = call_args[0][0]
            payload = json.loads(req.data.decode())
            assert "PENDING" in payload["text"]
            assert "2026-02-16-test.md" in payload["text"]

            assert result == 0
            captured = capsys.readouterr()
            assert "Compaction in progress" in captured.err

    @patch("pre_compact.urllib.request.urlopen")
    @patch("pre_compact.read_hook_stdin")
    @patch("pre_compact.get_session_plan_path")
    @patch("pre_compact._sessions_base")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123"})
    def test_fallback_to_local_file_on_http_failure(
        self, mock_sessions_base, mock_plan_path, mock_stdin, mock_urlopen, capsys
    ):
        """Should write to local file if HTTP API fails."""
        from pre_compact import run_pre_compact

        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            mock_sessions_base.return_value = sessions_dir

            mock_plan_path.return_value = Path(tmpdir) / "nonexistent.json"

            mock_stdin.return_value = {
                "session_id": "test123",
                "trigger": "manual",
                "custom_instructions": "compress heavily",
            }

            mock_urlopen.side_effect = Exception("Connection refused")

            result = run_pre_compact()

            fallback_file = sessions_dir / "test123" / "pre-compact-state.json"
            assert fallback_file.exists()

            state = json.loads(fallback_file.read_text())
            assert state["trigger"] == "manual"

            assert result == 0
            captured = capsys.readouterr()
            assert "local file" in captured.err

    @patch("pre_compact.urllib.request.urlopen")
    @patch("pre_compact.read_hook_stdin")
    @patch("pre_compact.get_session_plan_path")
    @patch("pre_compact._sessions_base")
    @patch("os.environ", {"CLAUDE_CODE_SESSION_ID": "cc-uuid-9999"})
    def test_fallback_file_uses_agent_native_id_when_no_session_id_anywhere(
        self, mock_sessions_base, mock_plan_path, mock_stdin, mock_urlopen
    ):
        """Issue #157: when hook_data carries no session_id (unusual, but not guaranteed
        by every caller) AND PILOT_SESSION_ID is unset (non-wrapper launch), the fallback
        file must resolve via the same agent-native chain as the rest of the hook layer
        (_lib/util.py:resolve_session_id()) instead of the hardcoded 'default' bucket,
        so post_compact_restore.py (which resolves the same way) can find it back.
        """
        from pre_compact import run_pre_compact

        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            mock_sessions_base.return_value = sessions_dir

            mock_plan_path.return_value = Path(tmpdir) / "nonexistent.json"

            mock_stdin.return_value = {
                "trigger": "manual",
                "custom_instructions": "",
            }

            mock_urlopen.side_effect = Exception("Connection refused")

            result = run_pre_compact()

            fallback_file = sessions_dir / "cc-uuid-9999" / "pre-compact-state.json"
            assert fallback_file.exists(), (
                f"expected fallback file under the resolved agent-native session dir, "
                f"got: {list(sessions_dir.rglob('*.json'))}"
            )
            assert result == 0

    @pytest.mark.parametrize("payload_kind", ["traversal", "absolute", "non-string"])
    @patch("pre_compact.urllib.request.urlopen")
    @patch("pre_compact.read_hook_stdin")
    @patch("pre_compact.get_session_plan_path")
    @patch("pre_compact._sessions_base")
    def test_fallback_rejects_unsafe_or_non_string_payload_session_ids(
        self,
        mock_sessions_base,
        mock_plan_path,
        mock_stdin,
        mock_urlopen,
        tmp_path,
        payload_kind,
    ):
        """Payload-first compaction keys must still be safe single components."""
        from pre_compact import run_pre_compact

        payload_id = {
            "traversal": "../victim",
            "absolute": str(tmp_path / "victim"),
            "non-string": 123,
        }[payload_kind]
        sessions = tmp_path / "sessions"
        mock_sessions_base.return_value = sessions
        mock_plan_path.return_value = tmp_path / "missing-active-plan.json"
        mock_stdin.return_value = {"session_id": payload_id, "trigger": "auto"}
        mock_urlopen.side_effect = OSError("offline")

        with patch.dict(os.environ, {}, clear=True):
            assert run_pre_compact() == 0

        assert (sessions / "default" / "pre-compact-state.json").is_file()
        assert not (tmp_path / "victim" / "pre-compact-state.json").exists()

    @patch("pre_compact.urllib.request.urlopen")
    @patch("pre_compact.read_hook_stdin")
    @patch("pre_compact.get_session_plan_path")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123"})
    def test_captures_trigger_type(self, mock_plan_path, mock_stdin, mock_urlopen, capsys):
        """Should capture whether compaction was manual or auto."""
        from pre_compact import run_pre_compact

        mock_plan_path.return_value = Path("/nonexistent")
        mock_stdin.return_value = {
            "session_id": "test123",
            "trigger": "manual",
            "custom_instructions": "focus on recent work",
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value = mock_response

        result = run_pre_compact()

        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode())
        assert "manual" in payload["text"]

        assert result == 0

    @patch("pre_compact.urllib.request.urlopen")
    @patch("pre_compact.read_hook_stdin")
    @patch("pre_compact.get_session_plan_path")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123"})
    def test_handles_no_active_plan(self, mock_plan_path, mock_stdin, mock_urlopen):
        """Should handle case where no active plan exists."""
        from pre_compact import run_pre_compact

        mock_plan_path.return_value = Path("/nonexistent")
        mock_stdin.return_value = {
            "session_id": "test123",
            "trigger": "auto",
            "custom_instructions": "",
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value = mock_response

        result = run_pre_compact()

        assert result == 0
        assert mock_urlopen.called


class TestCaptureActivePlan:
    """Test _capture_active_plan project-scoping guard."""

    @patch("pre_compact.urllib.request.urlopen")
    @patch("pre_compact.read_hook_stdin")
    @patch("pre_compact._sessions_base")
    def test_same_repo_default_bucket_plan_not_captured_for_identified_session(
        self, mock_sessions_base, mock_stdin, mock_urlopen, tmp_path
    ):
        """Same-repo sibling bleed: a plan another (env-less) session registered in
        the shared 'default' bucket must not be captured into THIS session's
        pre-compact state when the hook payload carries this session's own id.
        The project-scoping guard cannot help here - the plan IS in this repo."""
        import _lib.util as util
        from pre_compact import run_pre_compact

        project = tmp_path / "repo"
        plan = project / "docs" / "plans" / "2026-08-13-sibling.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("# Sibling\n\nStatus: PENDING\n")

        sessions = tmp_path / "sessions"
        (sessions / "default").mkdir(parents=True)
        (sessions / "default" / "active_plan.json").write_text(
            json.dumps({"status": "PENDING", "plan_path": str(plan)})
        )
        mock_sessions_base.return_value = sessions
        mock_stdin.return_value = {"session_id": "session-b-uuid", "trigger": "auto", "custom_instructions": ""}
        mock_urlopen.side_effect = Exception("Connection refused")

        with (
            patch.object(util, "_sessions_base", return_value=sessions),
            patch.dict(os.environ, {"CLAUDE_PROJECT_ROOT": str(project)}, clear=True),
        ):
            result = run_pre_compact()

        assert result == 0
        state = json.loads((sessions / "session-b-uuid" / "pre-compact-state.json").read_text())
        assert state["active_plan"] is None, (
            "a same-repo plan from the shared 'default' bucket belongs to another "
            "session and must not be captured into this session's pre-compact state"
        )

    @patch("pre_compact.get_session_plan_path")
    def test_does_not_capture_foreign_project_plan(self, mock_plan_path, tmp_path):
        """Cross-session bleed (source): a foreign-project plan reached through the
        shared 'default' active_plan.json must not be captured into this session's
        pre-compact state. Without the guard, compaction poisons the per-session
        fallback file with another repo's plan."""
        from pre_compact import _capture_active_plan

        current_project = tmp_path / "current-project"
        current_project.mkdir()
        foreign_plan = tmp_path / "other-project" / "docs" / "plans" / "2026-05-31-foreign.md"
        foreign_plan.parent.mkdir(parents=True)
        foreign_plan.write_text("# Foreign\n")

        plan_json = tmp_path / "active_plan.json"
        plan_json.write_text(json.dumps({"status": "PENDING", "plan_path": str(foreign_plan)}))
        mock_plan_path.return_value = plan_json

        with patch.dict(os.environ, {"CLAUDE_PROJECT_ROOT": str(current_project)}, clear=True):
            result = _capture_active_plan()

        assert result is None, "Foreign-project plan must not be captured into pre-compact state"

    @patch("pre_compact.get_session_plan_path")
    def test_captures_plan_in_current_project(self, mock_plan_path, tmp_path):
        """A plan that lives in the current project is still captured."""
        from pre_compact import _capture_active_plan

        current_project = tmp_path / "current-project"
        own_plan = current_project / "docs" / "plans" / "2026-05-31-own.md"
        own_plan.parent.mkdir(parents=True)
        own_plan.write_text("# Own\n")

        plan_json = tmp_path / "active_plan.json"
        plan_json.write_text(json.dumps({"status": "PENDING", "plan_path": str(own_plan)}))
        mock_plan_path.return_value = plan_json

        with patch.dict(os.environ, {"CLAUDE_PROJECT_ROOT": str(current_project)}, clear=True):
            result = _capture_active_plan()

        assert result is not None
        assert result["plan_path"] == str(own_plan)


class TestCaptureTaskList:
    """Test _capture_task_list function."""

    def test_returns_none_when_no_session_id(self):
        """Should return None when PILOT_SESSION_ID is not set."""
        from pre_compact import _capture_task_list

        with patch.dict(os.environ, {"PILOT_SESSION_ID": ""}, clear=False):
            result = _capture_task_list()

        assert result is None

    def test_returns_none_when_tasks_dir_missing(self, tmp_path):
        """Should return None when task directory doesn't exist."""
        from pre_compact import _capture_task_list

        with patch.dict(os.environ, {"PILOT_SESSION_ID": "99999"}, clear=False):
            result = _capture_task_list()

        assert result is None

    def test_captures_task_count(self, tmp_path):
        """Should capture task count from task directory."""
        from pre_compact import _capture_task_list

        pid = "99999"
        tasks_dir = tmp_path / ".claude" / "tasks" / f"pilot-{pid}"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "1.json").write_text('{"id": "1", "subject": "task 1"}')
        (tasks_dir / "2.json").write_text('{"id": "2", "subject": "task 2"}')

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": pid}, clear=False),
            patch.object(Path, "home", return_value=tmp_path),
        ):
            result = _capture_task_list()

        assert result is not None
        assert result["task_count"] == 2

    def test_returns_none_when_no_task_files(self, tmp_path):
        """Should return None when task directory is empty."""
        from pre_compact import _capture_task_list

        pid = "99999"
        tasks_dir = tmp_path / ".claude" / "tasks" / f"pilot-{pid}"
        tasks_dir.mkdir(parents=True)

        with (
            patch.dict(os.environ, {"PILOT_SESSION_ID": pid}, clear=False),
            patch.object(Path, "home", return_value=tmp_path),
        ):
            result = _capture_task_list()

        assert result is None
