"""Behavioral reproductions from the independent Opus review."""

import io
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import spec_interaction
import spec_stop_guard
from _lib.user_questions import decision_has_answer, latest_structured_question, routine_wait_question


def question(options=None):
    return {
        "questions": [
            {
                "question": "Still building. Keep waiting?",
                "options": options
                or [
                    {"label": "Stop checking for now", "description": "Check later"},
                    {"label": "Keep waiting", "description": "Report the result"},
                ],
            }
        ]
    }


@pytest.mark.parametrize("prompt", ["keep waiting", "continue", "resume", "2", "proceed"])
def test_stop_first_options_never_invert_continuation(prompt):
    assert spec_interaction._wait_answer(prompt, question()) == "continue"
    assert spec_interaction._wait_answer("Stop checking for now", question()) == "pause"


@pytest.mark.parametrize("text", ["DB is up. Please continue.", "Resource created; proceed", "Update\nweiter"])
def test_continuation_after_an_update_is_recognized(text):
    assert spec_interaction._is_resume_request(text)


@pytest.mark.parametrize(
    "command",
    [
        "gh run watch 1 --exit-status",
        "gh pr checks 1 --watch",
        "pytest tests/server/",
        "uv run pytest tests/",
        "vitest run",
        "npm run build",
        "cargo test",
    ],
)
def test_finite_commands_allow_passive_wait(command):
    assert spec_stop_guard._native_background_wait(
        {
            "last_assistant_message": "Waiting for https://ci.example/job?id=1 to finish.",
            "background_tasks": [{"id": "job", "type": "shell", "status": "running", "command": command}],
        }
    )


@pytest.mark.parametrize(
    "command",
    [
        "npm start",
        "docker compose up",
        "cargo watch",
        "vitest",
        "tsc -w",
        "nodemon",
        "flask run",
        "python -m http.server",
        "gh run watch 1; npm start",
        "unknown-script --wait",
    ],
)
def test_persistent_or_unknown_commands_do_not_release_the_guard(command):
    assert not spec_stop_guard._finite_background_command(command)


def transcript(path, *, failed=False, answered=True):
    events = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "q",
                        "name": "AskUserQuestion",
                        "input": question(),
                    }
                ]
            },
        }
    ]
    if answered:
        events.append(
            {
                "type": "user",
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "q",
                            "is_error": failed,
                            "content": "Keep waiting",
                        }
                    ]
                },
            }
        )
    events.append({"type": "assistant", "message": {"content": [{"type": "text", "text": "Summary"}]}})
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")


@pytest.mark.parametrize("failed,answered,expected", [(False, True, True), (True, True, False), (False, False, False)])
def test_answer_evidence_survives_a_summary_but_not_denials(tmp_path, failed, answered, expected):
    path = tmp_path / "transcript"
    transcript(path, failed=failed, answered=answered)
    assert decision_has_answer(str(path), "Still building. Keep waiting?") is expected
    assert latest_structured_question(str(path)) is None


def test_answered_decision_cannot_end_before_being_applied(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text("Status: PENDING\nApproved: Yes\nType: Feature\n")
    directory = tmp_path / "review"
    directory.mkdir()
    registration = {
        "plan_path": str(plan),
        "interaction": {
            "state": "paused",
            "kind": "decision",
            "message": "Still building. Keep waiting?",
        },
    }
    (directory / "active_plan.json").write_text(json.dumps(registration))
    path = tmp_path / "transcript"
    transcript(path)
    with (
        patch("spec_stop_guard._sessions_base", return_value=tmp_path),
        patch("spec_stop_guard.find_active_plan", return_value=(plan, "PENDING")),
        patch("spec_stop_guard.resolve_hook_session_id", return_value="review"),
        patch("spec_stop_guard.get_stop_guard_path", return_value=directory / "guard"),
        patch("sys.stdin", io.StringIO(json.dumps({"transcript_path": str(path)}))),
        patch("sys.stdout", new_callable=io.StringIO) as output,
    ):
        assert spec_stop_guard.main() == 0
        assert "received a user answer" in output.getvalue()
        assert "plan-state resume" in output.getvalue()
    assert json.loads((directory / "active_plan.json").read_text()) == registration


@pytest.mark.parametrize(
    "version,quiet", [("2.1.277", False), ("2.1.278", True), ("2.1.284", True), ("unknown", False)]
)
def test_quiet_stop_has_a_legacy_fallback(monkeypatch, version, quiet):
    monkeypatch.setenv("CLAUDE_PROJECT_PLATFORM", "claude")
    with (
        patch("spec_stop_guard.shutil.which", return_value="claude"),
        patch("spec_stop_guard.subprocess.run", return_value=subprocess.CompletedProcess([], 0, version, "")),
    ):
        value = json.loads(spec_stop_guard._continuation_output("Continue"))
    assert (value.get("hookSpecificOutput", {}).get("additionalContext") == "Continue") is quiet
    assert (value.get("decision") == "block") is not quiet


def test_human_tasks_are_not_suppressed_as_waiting():
    value = question()
    value["questions"][0]["question"] = "Wait for you to configure the resource?"
    assert not routine_wait_question(value)
    value["questions"][0]["question"] = "Deployment CI is still running. Keep waiting?"
    assert routine_wait_question(value)
    value["questions"][0]["question"] = "Should we deploy the changes now or keep waiting?"
    assert not routine_wait_question(value)


def test_transcript_lookup_reads_the_recent_tail_not_the_entire_history(tmp_path):
    path = tmp_path / "large.jsonl"
    with path.open("w") as stream:
        stream.write((json.dumps({"type": "assistant", "message": {"content": []}}) + "\n") * 200000)
        stream.write(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "AskUserQuestion",
                                "id": "recent",
                                "input": question(),
                            }
                        ]
                    },
                }
            )
            + "\n"
        )
    original_open = Path.open
    bytes_read = []

    class Reader:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.stream.close()

        def seek(self, *args):
            return self.stream.seek(*args)

        def read(self, count):
            result = self.stream.read(count)
            bytes_read.append(len(result))
            return result

    def open_counted(file, *args, **kwargs):
        return Reader(original_open(file, *args, **kwargs))

    with patch.object(Path, "open", open_counted):
        assert latest_structured_question(str(path)) == question()
    assert sum(bytes_read) < 128 * 1024


@pytest.mark.parametrize("kind", ["manual", "decision"])
def test_cli_discussion_pause_preserves_an_existing_required_action(tmp_path, kind):
    from launcher.session import set_plan_interaction

    plan = tmp_path / "plan.md"
    plan.write_text("Type: Feature\n### Task 1: Human action\n**Owner:** User\n**User Action:** Configure resource.\n")
    path = tmp_path / "active_plan.json"
    path.write_text(json.dumps({"plan_path": str(plan)}))
    with patch("launcher.session.resolve_lane_dir", return_value=tmp_path):
        set_plan_interaction(kind, task_number=1 if kind == "manual" else None, message="Required action")
        set_plan_interaction("discussion")
    value = json.loads(path.read_text())["interaction"]
    assert value["kind"] == kind and value["message"] == "Required action"
    if kind == "manual":
        assert value["task_number"] == 1


def test_decision_temporarily_suspends_but_never_deletes_a_model_handoff(tmp_path):
    from _lib.session_artifacts import MANUAL_SWITCH_SENTINEL

    plan = tmp_path / "plan.md"
    plan.write_text("Status: PENDING\nApproved: Yes\nType: Feature\n")
    session = tmp_path / "review"
    session.mkdir()
    marker = session / MANUAL_SWITCH_SENTINEL
    marker.write_text("")
    with patch("spec_interaction._sessions_base", return_value=tmp_path):
        assert (
            spec_interaction._manual_switch_gate_pending(
                "review", plan, "PENDING", True, "Feature", interaction={"state": "paused", "kind": "decision"}
            )
            is None
        )
        assert marker.exists()
        assert spec_interaction._manual_switch_gate_pending("review", plan, "PENDING", True, "Feature") == marker
