"""Tests for post_compact_restore hook."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPostCompactRestoreHook:
    """Test SessionStart(compact) hook context restoration."""

    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123"})
    def test_restores_active_plan_context(self, mock_plan_path, mock_stdin, capsys):
        """Should restore active plan context with structured message."""
        from post_compact_restore import run_post_compact_restore

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

            mock_stdin.return_value = {"session_id": "test123"}

            result = run_post_compact_restore()

            assert result == 0

            captured = capsys.readouterr()
            assert "[Pilot Context Restored After Compaction]" in captured.out
            assert "Active Plan:" in captured.out
            assert "2026-02-16-test.md" in captured.out
            assert "PENDING" in captured.out

    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123"})
    def test_outputs_valid_session_start_json(self, mock_plan_path, mock_stdin, capsys):
        """Should emit valid SessionStart JSON for Codex hooks."""
        from post_compact_restore import run_post_compact_restore

        with tempfile.TemporaryDirectory() as tmpdir:
            plan_json = Path(tmpdir) / "active_plan.json"
            plan_json.write_text(
                json.dumps(
                    {
                        "status": "PENDING",
                        "plan_path": "docs/plans/2026-02-16-test.md",
                    }
                )
            )
            mock_plan_path.return_value = plan_json
            mock_stdin.return_value = {"session_id": "test123"}

            result = run_post_compact_restore()

            assert result == 0
            captured = capsys.readouterr()
            payload = json.loads(captured.out)
            assert payload == {
                "continue": True,
                "suppressOutput": True,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": (
                        "[Pilot Context Restored After Compaction]\n"
                        "Active Plan: docs/plans/2026-02-16-test.md (Status: PENDING)"
                    ),
                },
            }

    @patch("post_compact_restore.read_hook_stdin", return_value={"platform": "codex", "session_id": "codex-test"})
    @patch("post_compact_restore.get_session_plan_path")
    def test_codex_uses_context_only_without_stderr_or_unsupported_suppression(
        self, mock_plan_path, _mock_stdin, capsys, tmp_path
    ):
        from post_compact_restore import run_post_compact_restore

        mock_plan_path.return_value = tmp_path / "missing-active-plan.json"

        assert run_post_compact_restore() == 0

        captured = capsys.readouterr()
        payload = json.loads(captured.out)
        assert captured.err == ""
        assert "continue" not in payload
        assert "suppressOutput" not in payload
        assert "No active plan" in payload["hookSpecificOutput"]["additionalContext"]

    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    def test_suppresses_foreign_project_plan(self, mock_plan_path, mock_stdin, capsys, tmp_path):
        """Cross-session bleed: an absolute plan path belonging to ANOTHER project
        (the shared 'default' active_plan.json when PILOT_SESSION_ID is unset) must
        not be surfaced as the restored active plan in an unrelated repo."""
        from post_compact_restore import run_post_compact_restore

        current_project = tmp_path / "current-project"
        current_project.mkdir()
        foreign_plan = tmp_path / "other-project" / "docs" / "plans" / "2026-05-27-foreign.md"
        foreign_plan.parent.mkdir(parents=True)
        foreign_plan.write_text("# Foreign\n\nStatus: PENDING\n")

        plan_json = tmp_path / "active_plan.json"
        plan_json.write_text(json.dumps({"status": "PENDING", "plan_path": str(foreign_plan)}))
        mock_plan_path.return_value = plan_json
        mock_stdin.return_value = {"session_id": "test123"}

        with patch.dict(
            os.environ,
            {"PILOT_SESSION_ID": "test123", "CLAUDE_PROJECT_ROOT": str(current_project)},
            clear=True,
        ):
            result = run_post_compact_restore()

        assert result == 0
        captured = capsys.readouterr()
        assert str(foreign_plan) not in captured.out, "Foreign-project plan must not be surfaced after compaction"
        assert "No active plan" in captured.out

    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    @patch("post_compact_restore._sessions_base")
    def test_suppresses_foreign_project_plan_from_fallback_state(
        self, mock_sessions_base, mock_plan_path, mock_stdin, capsys, tmp_path
    ):
        """Cross-session bleed (fallback path): a foreign-project plan that reached
        this session's pre-compact-state.json (captured from the shared 'default'
        active_plan.json before compaction) must not be surfaced after compaction.

        Mirrors test_suppresses_foreign_project_plan but for the fallback-state
        branch, which previously had no plan_in_current_project guard."""
        from post_compact_restore import run_post_compact_restore

        current_project = tmp_path / "current-project"
        current_project.mkdir()
        foreign_plan = tmp_path / "other-project" / "docs" / "plans" / "2026-05-31-foreign.md"
        foreign_plan.parent.mkdir(parents=True)
        foreign_plan.write_text("# Foreign\n\nStatus: PENDING\n")

        sessions_dir = tmp_path / "sessions"
        mock_sessions_base.return_value = sessions_dir
        session_dir = sessions_dir / "test123"
        session_dir.mkdir(parents=True)
        (session_dir / "pre-compact-state.json").write_text(
            json.dumps(
                {
                    "trigger": "auto",
                    "active_plan": {"plan_path": str(foreign_plan), "status": "PENDING"},
                }
            )
        )

        mock_plan_path.return_value = tmp_path / "nonexistent.json"
        mock_stdin.return_value = {"session_id": "test123"}

        with patch.dict(
            os.environ,
            {"PILOT_SESSION_ID": "test123", "CLAUDE_PROJECT_ROOT": str(current_project)},
            clear=True,
        ):
            result = run_post_compact_restore()

        assert result == 0
        captured = capsys.readouterr()
        assert str(foreign_plan) not in captured.out, (
            "Foreign-project plan must not be surfaced from fallback state after compaction"
        )
        assert "No active plan" in captured.out

    @patch("post_compact_restore.read_hook_stdin")
    def test_same_repo_default_bucket_plan_not_restored_for_identified_session(self, mock_stdin, capsys, tmp_path):
        """Same-repo sibling bleed (issue #157's uncovered half): session A registered
        its plan without any session-id env var, so it sits in the shared 'default'
        bucket. Session B compacts in the SAME repo, with its own session_id in the
        hook payload and an empty env chain. plan_in_current_project passes here by
        definition, so only session-scoped resolution keeps B from being re-anchored
        onto A's plan."""
        import _lib.util as util
        from post_compact_restore import run_post_compact_restore

        project = tmp_path / "repo"
        plan = project / "docs" / "plans" / "2026-08-13-session-a-feature.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("# A\n\nStatus: PENDING\nApproved: Yes\nType: Feature\n")

        sessions = tmp_path / "sessions"
        (sessions / "default").mkdir(parents=True)
        (sessions / "default" / "active_plan.json").write_text(
            json.dumps({"status": "PENDING", "plan_path": str(plan)})
        )

        mock_stdin.return_value = {"session_id": "session-b-uuid"}

        with (
            patch.object(util, "_sessions_base", return_value=sessions),
            patch("post_compact_restore._sessions_base", return_value=sessions),
            patch.dict(os.environ, {"CLAUDE_PROJECT_ROOT": str(project)}, clear=True),
        ):
            result = run_post_compact_restore()

        assert result == 0
        captured = capsys.readouterr()
        assert str(plan) not in captured.out, (
            "another session's plan (shared 'default' bucket, same repo) must not be "
            "restored into a session whose payload carries its own session_id"
        )
        assert "No active plan" in captured.out

    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123"})
    def test_handles_no_active_plan(self, mock_plan_path, mock_stdin, capsys):
        """Should handle case where no active plan exists."""
        from post_compact_restore import run_post_compact_restore

        mock_plan_path.return_value = Path("/nonexistent")
        mock_stdin.return_value = {"session_id": "test123"}

        result = run_post_compact_restore()

        assert result == 0

        captured = capsys.readouterr()
        assert "[Pilot Context Restored After Compaction]" in captured.out
        assert "No active plan" in captured.out or "Active Plan:" not in captured.out

    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    @patch("post_compact_restore._sessions_base")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123"})
    def test_includes_fallback_state_if_available(self, mock_sessions_base, mock_plan_path, mock_stdin, capsys):
        """Should include pre-compact fallback state if available."""
        from post_compact_restore import run_post_compact_restore

        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            mock_sessions_base.return_value = sessions_dir

            session_dir = sessions_dir / "test123"
            session_dir.mkdir()
            fallback_file = session_dir / "pre-compact-state.json"
            fallback_file.write_text(
                json.dumps(
                    {
                        "trigger": "manual",
                        "active_plan": {
                            "plan_path": "docs/plans/2026-02-16-test.md",
                            "status": "COMPLETE",
                        },
                    }
                )
            )

            mock_plan_path.return_value = Path("/nonexistent")
            mock_stdin.return_value = {"session_id": "test123"}

            result = run_post_compact_restore()

            assert result == 0

            captured = capsys.readouterr()
            assert "2026-02-16-test.md" in captured.out or "Restored" in captured.out

    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    @patch("post_compact_restore._sessions_base")
    @patch("os.environ", {"CLAUDE_CODE_SESSION_ID": "cc-uuid-9999"})
    def test_fallback_state_found_via_agent_native_id_when_no_session_id_anywhere(
        self, mock_sessions_base, mock_plan_path, mock_stdin, capsys
    ):
        """Issue #157: pre_compact.py (the writer) and post_compact_restore.py (this
        reader) must resolve the SAME session directory when hook_data carries no
        session_id and PILOT_SESSION_ID is unset (non-wrapper launch) - both now use
        the agent-native chain (_lib/util.py:resolve_session_id()), so a fallback file
        written under the resolved CLAUDE_CODE_SESSION_ID dir is found here, not lost
        to a directory mismatch against the hardcoded 'default' bucket.
        """
        from post_compact_restore import run_post_compact_restore

        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            mock_sessions_base.return_value = sessions_dir

            # Simulates exactly what pre_compact.py's fallback writer produces for the
            # same unresolved-session_id scenario, at the id resolve_session_id() picks.
            session_dir = sessions_dir / "cc-uuid-9999"
            session_dir.mkdir()
            fallback_file = session_dir / "pre-compact-state.json"
            fallback_file.write_text(
                json.dumps(
                    {
                        "trigger": "manual",
                        "active_plan": {
                            "plan_path": "docs/plans/2026-02-16-test.md",
                            "status": "COMPLETE",
                        },
                    }
                )
            )

            mock_plan_path.return_value = Path("/nonexistent")
            mock_stdin.return_value = {}

            result = run_post_compact_restore()

            assert result == 0
            captured = capsys.readouterr()
            # Strict, not OR'd with the unconditional "Restored" header text (which
            # prints regardless of whether the fallback file was actually found) -
            # the plan path only appears if _read_fallback_state resolved the SAME
            # directory pre_compact.py's writer used.
            assert "2026-02-16-test.md" in captured.out

    @pytest.mark.parametrize("payload_kind", ["traversal", "absolute", "non-string"])
    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    @patch("post_compact_restore._sessions_base")
    def test_restore_rejects_unsafe_or_non_string_payload_session_ids(
        self,
        mock_sessions_base,
        mock_plan_path,
        mock_stdin,
        capsys,
        tmp_path,
        payload_kind,
    ):
        """Post-compaction lookup must sanitize the payload exactly like its writer."""
        from post_compact_restore import run_post_compact_restore

        payload_id = {
            "traversal": "../victim",
            "absolute": str(tmp_path / "victim"),
            "non-string": 123,
        }[payload_kind]
        sessions = tmp_path / "sessions"
        fallback = sessions / "default" / "pre-compact-state.json"
        fallback.parent.mkdir(parents=True)
        fallback.write_text(json.dumps({"active_plan": {"plan_path": "docs/plans/safe.md", "status": "PENDING"}}))
        mock_sessions_base.return_value = sessions
        mock_plan_path.return_value = tmp_path / "missing-active-plan.json"
        mock_stdin.return_value = {"session_id": payload_id}

        with patch.dict(os.environ, {}, clear=True):
            assert run_post_compact_restore() == 0

        assert "docs/plans/safe.md" in capsys.readouterr().out
        assert not fallback.exists(), "the sanitized default-bucket state should be consumed"

    @patch("post_compact_restore.read_hook_stdin")
    @patch("post_compact_restore.get_session_plan_path")
    @patch("os.environ", {"PILOT_SESSION_ID": "test123", "CLAUDE_CODE_TASK_LIST_ID": "test-tasks"})
    def test_fast_execution(self, mock_plan_path, mock_stdin):
        """Should complete in under 2 seconds."""
        import time

        from post_compact_restore import run_post_compact_restore

        mock_plan_path.return_value = Path("/nonexistent")
        mock_stdin.return_value = {"session_id": "test123"}

        start = time.time()
        result = run_post_compact_restore()
        elapsed = time.time() - start

        assert result == 0
        assert elapsed < 2.0, f"Hook took {elapsed:.2f}s, must be under 2s"
