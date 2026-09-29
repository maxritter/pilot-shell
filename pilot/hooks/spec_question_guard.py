"""Prevent an approved autonomous plan from asking permission merely to keep waiting."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.user_questions import question_tool, routine_wait_question  # noqa: E402
from _lib.util import _read_plan_approved_and_type, resolve_hook_session_id  # noqa: E402
from spec_interaction import _atomic_write_json, _load_registration  # noqa: E402


def handle(payload: object) -> dict:
    if not isinstance(payload, dict) or not question_tool(payload.get("tool_name")):
        return {}
    question = payload.get("tool_input")
    if not isinstance(question, dict) or not isinstance(question.get("questions"), list):
        return {}
    loaded = _load_registration(resolve_hook_session_id(payload.get("session_id")))
    if loaded is None:
        return {}
    path, registration, plan = loaded
    approved, _plan_type = _read_plan_approved_and_type(str(plan))
    if not approved or str(registration.get("status", "")).upper() == "VERIFIED":
        return {}

    interaction = registration.get("interaction")
    waiting = [item for item in question["questions"] if routine_wait_question({"questions": [item]})]
    will_ask = any(item not in waiting for item in question["questions"])
    if will_ask and isinstance(interaction, dict) and interaction.get("kind") == "decision" and interaction.get("origin") != "user":
        if "answer_received" in interaction:
            registration["interaction"] = {key: value for key, value in interaction.items() if key != "answer_received"}
            if not _atomic_write_json(path, registration):
                return {}
            interaction = registration["interaction"]
    if not waiting:
        return {}
    if isinstance(interaction, dict) and (interaction.get("origin") == "user" or interaction.get("kind") == "manual"):
        resume = (
            "Only exact `done` confirms the manual action; verify its criteria before continuing. "
            "A resume or continuation request cannot complete that action."
            if interaction.get("kind") == "manual"
            else "A clear continuation request releases the explicit hold, but any pending decision still requires resolution."
        )
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "The plan is explicitly held for the user or a manual task. Preserve that hold; "
                    "do not continue implementation or independent work. A running job does not need "
                    f"a keep-waiting question. {resume}"
                ),
            }
        }

    remaining = [item for item in question["questions"] if item not in waiting]
    if remaining:
        interaction = registration.get("interaction")
        waiting_text = {item["question"] for item in waiting}
        if (
            isinstance(interaction, dict)
            and interaction.get("kind") == "decision"
            and interaction.get("message") in waiting_text
        ):
            texts = [
                item.get("question")
                for item in remaining
                if isinstance(item, dict) and isinstance(item.get("question"), str)
            ]
            if texts:
                registration["interaction"] = {**interaction, "message": "\n".join(texts)[:1000]}
                if not _atomic_write_json(path, registration):
                    return {}
        output = {"hookEventName": "PreToolUse", "updatedInput": {**question, "questions": remaining}}
        if str(payload["tool_name"]).rsplit(".", 1)[-1] != "AskUserQuestion":
            # Codex applies updatedInput only with allow. This rewrites question
            # input; it supplies no answers and leaves the native user gate intact.
            output["permissionDecision"] = "allow"
        return {"hookSpecificOutput": output}

    interaction = registration.get("interaction")
    if isinstance(interaction, dict):
        asked = {item["question"] for item in question["questions"]}
        accidental = interaction.get("origin") != "user" and (
            (interaction.get("kind") == "decision" and interaction.get("message") in asked)
            or (interaction.get("kind") == "discussion" and interaction.get("origin") == "automatic")
        )
        if accidental:
            registration.pop("interaction", None)
            if not _atomic_write_json(path, registration):
                return {}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "This approved plan is autonomous. A running job needs a progress update, not a keep-waiting question. "
                "Retain its job handle, wait or monitor through the runtime's task tools, and continue independent work. "
                "Collect its result and continue when it finishes. Ask only for a concrete failure or required user decision."
            ),
        }
    }


def _has_answer(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return _has_answer(value.get("answers"))
    if isinstance(value, list):
        return any(_has_answer(item) for item in value)
    return False


def handle_answer(payload: object) -> dict:
    """Record successful human input even when SDK transcript persistence is off."""
    if not isinstance(payload, dict) or not question_tool(payload.get("tool_name")):
        return {}
    question = payload.get("tool_input")
    response = payload.get("tool_response", payload.get("tool_output"))
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except ValueError:
            response = {"answered": response.startswith("The user answered:")}
    if (
        not isinstance(question, dict)
        or not isinstance(response, dict)
        or response.get("is_error")
        or response.get("error")
    ):
        return {}
    answers = response.get("answers")
    items = question.get("questions")
    if not isinstance(items, list):
        return {}
    keys = {
        value
        for item in items
        if isinstance(item, dict)
        for value in (item.get("question"), item.get("id"), item.get("header"))
        if isinstance(value, str)
    }
    if (
        not (isinstance(answers, dict) and any(key in keys and _has_answer(value) for key, value in answers.items()))
        and response.get("answered") is not True
    ):
        return {}
    loaded = _load_registration(resolve_hook_session_id(payload.get("session_id")))
    if loaded is None:
        return {}
    path, registration, _plan = loaded
    held = registration.get("interaction")
    if not isinstance(held, dict) or held.get("kind") != "decision" or held.get("origin") == "user":
        return {}
    texts = [item.get("question") for item in items if isinstance(item, dict)]
    joined = "\n".join(text for text in texts if isinstance(text, str))[:1000]
    if held.get("message") not in texts and held.get("message") != joined:
        return {}
    registration["interaction"] = {**held, "answer_received": True}
    _atomic_write_json(path, registration)
    return {}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = handle_answer(payload) if "--answer" in sys.argv[1:] else handle(payload)
    except (OSError, ValueError, TypeError):
        return 0
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
