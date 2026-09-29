"""Reproduce the reported waiting question at the real PreToolUse boundary."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import spec_question_guard

WAIT = {
    "questions": [
        {
            "header": "Still building",
            "question": "Still building (both dp/beta and dh/beta in_progress on GitHub). No local work possible until they finish. Keep waiting?",
            "options": [
                {
                    "label": "Yes, keep waiting (Recommended)",
                    "description": "I'll report results as soon as both finish.",
                },
                {"label": "Stop checking for now", "description": "I'll pick this back up later when you ask."},
            ],
        }
    ]
}


def _run(
    tmp_path: Path, question: dict, *, approved: bool = True, interaction: dict | None = None
) -> tuple[dict, Path]:
    plan = tmp_path / "plan.md"
    plan.write_text(f"# Plan\nStatus: PENDING\nApproved: {'Yes' if approved else 'No'}\nType: Feature\n")
    registration = tmp_path / "active_plan.json"
    data = {"plan_path": str(plan), "status": "PENDING"}
    if interaction:
        data["interaction"] = interaction
    registration.write_text(json.dumps(data))
    with (
        patch("spec_question_guard._load_registration", return_value=(registration, data, plan)),
        patch("pathlib.Path.home", return_value=tmp_path),
    ):
        result = spec_question_guard.handle(
            {"session_id": "test", "tool_name": "AskUserQuestion", "tool_input": question}
        )
    return result, registration


def test_reported_keep_waiting_question_is_blocked_before_it_reaches_the_user(tmp_path: Path) -> None:
    result, _ = _run(tmp_path, WAIT)
    output = result["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "deny"
    assert "job handle" in output["permissionDecisionReason"]


@pytest.mark.parametrize(
    "text",
    [
        "Both builds are still running. Shall I stay here?",
        "The job hasn't finished yet. Should I check again?",
        "Still building. Keep waiting?",
    ],
)
def test_waiting_options_are_recognized_even_when_question_wording_varies(tmp_path: Path, text: str) -> None:
    result, _ = _run(tmp_path, {"questions": [{**WAIT["questions"][0], "question": text}]})
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_mixed_batch_removes_waiting_but_keeps_real_question_and_permissions(tmp_path: Path) -> None:
    budget = {**WAIT["questions"][0], "question": "The API budget is $100. Keep waiting?"}
    result, registration = _run(
        tmp_path,
        {"questions": [WAIT["questions"][0], budget]},
        interaction={"state": "paused", "kind": "decision", "message": budget["question"]},
    )
    output = result["hookSpecificOutput"]
    assert output["updatedInput"]["questions"] == [budget]
    assert "permissionDecision" not in output
    assert json.loads(registration.read_text())["interaction"]["kind"] == "decision"


def test_mixed_batch_rebinds_a_false_wait_pause_to_the_real_decision(tmp_path: Path) -> None:
    budget = {**WAIT["questions"][0], "question": "The API budget is $100. Keep waiting?"}
    _result, registration = _run(
        tmp_path,
        {"questions": [WAIT["questions"][0], budget]},
        interaction={"state": "paused", "kind": "decision", "message": WAIT["questions"][0]["question"]},
    )
    assert json.loads(registration.read_text())["interaction"]["message"] == budget["question"]


def test_false_waiting_decision_does_not_leave_the_plan_paused(tmp_path: Path) -> None:
    result, registration = _run(
        tmp_path,
        WAIT,
        interaction={
            "state": "paused",
            "kind": "decision",
            "message": WAIT["questions"][0]["question"],
        },
    )
    assert result
    assert "interaction" not in json.loads(registration.read_text())


@pytest.mark.parametrize(
    "change",
    [
        {"question": "The job failed. Keep waiting or choose a rollback?"},
        {"question": "Our budget is $100. Keep waiting?"},
        {
            "options": [
                {"label": "Keep waiting", "description": "Wait"},
                {"label": "Deploy now", "description": "Publish"},
            ]
        },
    ],
)
def test_real_failure_cost_or_release_choices_are_preserved(tmp_path: Path, change: dict) -> None:
    question = {"questions": [{**WAIT["questions"][0], **change}]}
    result, _ = _run(tmp_path, question)
    assert result == {}


def test_checkpoints_never_restore_routine_waiting_questions(tmp_path: Path) -> None:
    config = tmp_path / ".pilot/config.json"
    config.parent.mkdir()
    config.write_text(json.dumps({"specWorkflow": {"runawayGuard": True}}))
    assert _run(tmp_path, WAIT)[0]["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert _run(tmp_path, WAIT, approved=False)[0] == {}


@pytest.mark.parametrize("kind", ["discussion", "decision"])
def test_explicit_user_pause_is_preserved_even_if_agent_asks_a_waiting_question(tmp_path: Path, kind: str) -> None:
    interaction = {"state": "paused", "kind": kind, "origin": "user", "message": WAIT["questions"][0]["question"]}
    result, registration = _run(tmp_path, WAIT, interaction=interaction)
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "do not continue implementation" in result["hookSpecificOutput"]["permissionDecisionReason"]
    assert json.loads(registration.read_text())["interaction"] == interaction


@pytest.mark.parametrize("tool", ["AskUserQuestion", "functions.request_user_input", "request_user_input_async"])
def test_answer_receipt_is_bound_to_the_pending_decision(tmp_path, tool):
    plan = tmp_path / "plan.md"
    plan.write_text("Status: PENDING\nApproved: Yes\nType: Feature\n")
    path = tmp_path / "active_plan.json"
    held = {"state": "paused", "kind": "decision", "message": "Approve budget?"}
    registration = {"plan_path": str(plan), "interaction": held}
    path.write_text(json.dumps(registration))
    with patch("spec_question_guard._load_registration", return_value=(path, registration, plan)):
        result = spec_question_guard.handle_answer(
            {
                "tool_name": tool,
                "tool_input": {"questions": [{"question": "Approve budget?"}]},
                "tool_response": {"answers": {"Approve budget?": "Yes"}},
            }
        )
    assert result == {}
    assert json.loads(path.read_text())["interaction"] == {**held, "answer_received": True}


@pytest.mark.parametrize(
    "change",
    [
        {"tool_response": {"answers": {"unrelated": "Yes"}}},
        {"tool_response": {"answers": {"Approve budget?": {"answers": []}}}},
        {"tool_response": {"answers": {"Approve budget?": "Yes"}, "is_error": True}},
        {"origin": "user"},
        {"kind": "manual"},
    ],
)
def test_answer_receipt_does_not_invent_input_or_override_a_hold(tmp_path, change):
    plan = tmp_path / "plan.md"
    plan.write_text("Status: PENDING\nApproved: Yes\nType: Feature\n")
    path = tmp_path / "active_plan.json"
    held = {"state": "paused", "kind": change.get("kind", "decision"), "message": "Approve budget?"}
    if "origin" in change:
        held["origin"] = change["origin"]
    registration = {"plan_path": str(plan), "interaction": held}
    path.write_text(json.dumps(registration))
    payload = {
        "tool_name": "AskUserQuestion",
        "tool_input": {"questions": [{"question": "Approve budget?"}]},
        "tool_response": change.get("tool_response", {"answers": {"Approve budget?": "Yes"}}),
    }
    with patch("spec_question_guard._load_registration", return_value=(path, registration, plan)):
        spec_question_guard.handle_answer(payload)
    assert json.loads(path.read_text()) == registration


def test_denied_wait_question_does_not_erase_a_real_answer_receipt(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text("Status: PENDING\nApproved: Yes\nType: Feature\n")
    path = tmp_path / "active_plan.json"
    registration = {"plan_path": str(plan), "status": "PENDING", "interaction": {
        "state": "paused", "kind": "decision", "message": "Approve budget?", "answer_received": True,
    }}
    path.write_text(json.dumps(registration))
    with patch("spec_question_guard._load_registration", return_value=(path, registration, plan)):
        result = spec_question_guard.handle({"tool_name": "AskUserQuestion", "tool_input": WAIT})
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert json.loads(path.read_text())["interaction"]["answer_received"] is True
