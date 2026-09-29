#!/usr/bin/env python3
"""Persist user-driven interaction pauses for an active Pilot plan.

The Stop hook's ``stop_hook_active`` flag describes a continuation chain, not
whether the latest prompt came from a human.  UserPromptSubmit is the reliable
boundary for that distinction.  This hook therefore owns discussion-pause
transitions and keeps the Stop guard focused on completion enforcement.

The one exception is a harness-delivered turn: Claude Code submits a finished
background task as a ``<task-notification>`` prompt through the same event, with
no other field marking it non-human.  Those are ignored outright.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.session_artifacts import DISCUSSION_PAUSE, MANUAL_SWITCH_SENTINEL  # noqa: E402
from _lib.user_questions import latest_structured_question, routine_wait_question  # noqa: E402
from _lib.util import (  # noqa: E402
    _read_plan_approved_and_type,
    _sessions_base,
    plan_in_current_project,
    read_workflow_toggle,
    resolve_hook_session_id,
)

_PAUSE_COMMANDS = frozenset({"pause", "please pause", "stop", "stop working", "hold on", "/spec pause", "$spec pause"})
_RESUME_COMMANDS = frozenset({"resume", "/spec resume", "$spec resume"})
_CONTINUE_PHRASES = frozenset(
    {"continue", "keep waiting", "continue waiting", "go on", "proceed", "weiter", "fortsetzen"}
)
_SPEC_COMMAND_PREFIXES = ("/spec", "$spec")
_HARNESS_PROMPT_PREFIXES = ("<task-notification>",)
_LEGACY_PAUSE_FILE = DISCUSSION_PAUSE
_LEGACY_PAUSE_MAX_AGE_SECONDS = 3600
_MANUAL_SWITCH_MAX_AGE_SECONDS = 24 * 3600


def _atomic_write_json(path: Path, data: dict) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        temporary.write_text(json.dumps(data, sort_keys=True))
        os.replace(temporary, path)
        return True
    except OSError:
        try:
            temporary.unlink(missing_ok=True)
        except (OSError, UnboundLocalError):
            pass
        return False


def _load_registration(session_id: str) -> tuple[Path, dict, Path] | None:
    registration_path = _sessions_base() / session_id / "active_plan.json"
    try:
        data = json.loads(registration_path.read_text())
        plan = Path(data["plan_path"])
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
    if not isinstance(data, dict) or not plan.is_file() or not plan_in_current_project(plan):
        return None
    try:
        header = re.search(r"^Status:\s*(PENDING|COMPLETE|VERIFIED)\b", plan.read_text(), re.M | re.I)
    except (OSError, UnicodeError):
        header = None
    if header:
        # Registration binds the plan; its cached status may lag a phase update.
        # The canonical file controls gates. Avoid writes in this read helper.
        data = {**data, "status": header.group(1).upper()}
    return registration_path, data, plan


def _context(message: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": message,
        }
    }


def _consume_expected_continuation(session_id: str, prompt: str) -> bool:
    state_path = _sessions_base() / session_id / "spec-stop-guard"
    try:
        state = json.loads(state_path.read_text())
    except (OSError, json.JSONDecodeError, TypeError):
        return False
    if not isinstance(state, dict):
        return False
    expected = state.pop("expected_prompt_sha256", None)
    if expected is None:
        return False
    _atomic_write_json(state_path, state)
    return expected == hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _is_spec_command(prompt: str) -> bool:
    return any(prompt == prefix or prompt.startswith(f"{prefix} ") for prefix in _SPEC_COMMAND_PREFIXES)


def _is_harness_prompt(prompt: str) -> bool:
    return prompt.startswith(_HARNESS_PROMPT_PREFIXES)


def _is_resume_request(prompt: str) -> bool:
    """Recognize clear continuation directives, including a sentence after an update."""
    normalized = prompt.lower().strip().rstrip(".! ")
    if normalized in _RESUME_COMMANDS:
        return True
    directive = re.sub(r"^(?:yes[, ]+|please\s+)", "", normalized)
    if directive in _CONTINUE_PHRASES or directive == "resume":
        return True
    trailing = re.split(r"[.!;]\s+|\n\s*", normalized)[-1]
    return trailing != normalized and _is_resume_request(trailing)


def _migrate_legacy_pause(
    session_id: str,
    registration_path: Path,
    registration: dict,
    plan: Path,
    plan_type: str,
) -> dict:
    """Convert one valid pre-durable pause marker, then retire the marker."""
    marker = _sessions_base() / session_id / _LEGACY_PAUSE_FILE
    if not marker.exists():
        return registration
    valid = plan_type != "Build" and str(registration.get("status", "")).upper() != "VERIFIED"
    try:
        if time.time() - marker.stat().st_mtime > _LEGACY_PAUSE_MAX_AGE_SECONDS:
            valid = False
        raw = marker.read_text().strip()
        if raw:
            binding = json.loads(raw)
            bound_plan = binding.get("plan_path") if isinstance(binding, dict) else None
            if not bound_plan or os.path.realpath(str(bound_plan)) != os.path.realpath(plan):
                valid = False
    except (OSError, json.JSONDecodeError, TypeError):
        valid = False

    if not valid:
        marker.unlink(missing_ok=True)
        return registration
    interaction = registration.get("interaction")
    if isinstance(interaction, dict) and interaction.get("state") == "paused":
        marker.unlink(missing_ok=True)
        return registration

    migrated = {**registration, "interaction": {"state": "paused", "kind": "discussion"}}
    if _atomic_write_json(registration_path, migrated):
        marker.unlink(missing_ok=True)
        return migrated
    return registration


def _consume_expected_verify_gate(
    session_id: str,
    plan: Path,
    status: str,
    plan_type: str,
) -> bool:
    """Consume the persisted marker for an expected COMPLETE-state answer."""
    marker = _sessions_base() / session_id / "verify-gate-pending"
    if not marker.exists():
        return False
    valid = status == "COMPLETE" and plan_type != "Build"
    try:
        if time.time() - marker.stat().st_mtime > _LEGACY_PAUSE_MAX_AGE_SECONDS:
            valid = False
        binding = json.loads(marker.read_text())
        expected_fingerprint = hashlib.sha256(plan.read_bytes()).hexdigest()
        valid = valid and isinstance(binding, dict)
        valid = valid and os.path.realpath(str(binding.get("plan_path", ""))) == os.path.realpath(plan)
        valid = valid and binding.get("expected_status") == status
        valid = valid and binding.get("plan_content_fingerprint") == expected_fingerprint
    except (OSError, json.JSONDecodeError, TypeError):
        valid = False
    marker.unlink(missing_ok=True)
    return valid


def _manual_switch_gate_pending(
    session_id: str,
    plan: Path,
    status: str,
    approved: bool,
    plan_type: str,
    *,
    interaction: object = None,
) -> Path | None:
    """Return a valid, bound Manual model-switch marker without consuming it."""
    marker = _sessions_base() / session_id / MANUAL_SWITCH_SENTINEL
    if not marker.exists():
        return None
    valid = status == "PENDING" and approved and plan_type != "Build"
    if isinstance(interaction, dict) and interaction.get("kind") in {"manual", "decision"}:
        # A concurrent decision must not consume a still-valid handoff. Manual
        # tasks prove implementation already started, so their old marker is stale.
        if interaction.get("kind") == "decision":
            return None
        valid = False
    try:
        if time.time() - marker.stat().st_mtime > _MANUAL_SWITCH_MAX_AGE_SECONDS:
            valid = False
        raw = marker.read_text().strip()
        if raw:
            binding = json.loads(raw)
            expected_fingerprint = hashlib.sha256(plan.read_bytes()).hexdigest()
            valid = valid and isinstance(binding, dict)
            valid = valid and os.path.realpath(str(binding.get("plan_path", ""))) == os.path.realpath(plan)
            valid = valid and binding.get("expected_status") == status
            if valid and binding.get("plan_content_fingerprint") != expected_fingerprint:
                binding["plan_content_fingerprint"] = expected_fingerprint
                binding["created_at"] = time.time()
                valid = _atomic_write_json(marker, binding)
    except (OSError, json.JSONDecodeError, TypeError):
        valid = False
    if not valid:
        marker.unlink(missing_ok=True)
        return None
    return marker


def _paused_context(interaction: dict) -> dict:
    if interaction.get("kind") == "manual":
        return _context(
            "The active Pilot plan remains paused at its user-owned task. Answer without restarting "
            "implementation. Only exact `done` confirms the user action; `resume` does not complete it."
        )
    if interaction.get("kind") == "decision" and interaction.get("origin") != "user":
        return _context(
            "This message concerns the pending material decision. Interpret the actual answer against "
            f"the recorded question: {interaction.get('message', '')}. If it resolves the decision and "
            "authorizes proceeding, apply the agreed amendments, run `pilot plan-state resume` with "
            "the current lane flag, and continue in this turn. Require no extra standalone resume message. "
            "If it does not resolve the decision, keep it pending and answer or clarify it."
        )
    return _context(
        "The active Pilot plan remains paused. Answer the user's message without restarting implementation. "
        "A clear request to resume or continue clears this pause; `/spec resume` is also available. "
        "For other unambiguous continuation wording, run `pilot plan-state resume` before continuing."
    )


def _wait_answer(prompt: str, question: dict) -> str | None:
    """Interpret an old waiting question's numbered/label response without guessing approval."""
    if not routine_wait_question(question) or len(question["questions"]) != 1:
        return None
    options = question["questions"][0]["options"]
    value = prompt.strip().lower()
    selected = None
    if re.fullmatch(r"(?:option\s+)?\d+[.)]?", value):
        number = int(re.search(r"\d+", value)[0])
        selected = options[number - 1] if 1 <= number <= len(options) else None
    else:
        for option in options:
            label = re.sub(r"\s*\(recommended\)\s*$", "", option["label"], flags=re.I).strip().lower()
            if value == label:
                selected = option
                break
        if selected is None and _is_resume_request(value):
            selected = next(
                (option for option in options if not re.search(r"\b(?:stop|pause|no)\b", option["label"], re.I)),
                None,
            )
    if not isinstance(selected, dict):
        return None
    if re.search(r"\b(?:stop|pause|no)\b", selected["label"], re.I):
        return "pause"
    return "continue" if re.search(r"\b(?:keep|continue|wait)\b", selected["label"], re.I) else None


def _paused_reply(
    prompt: str, question: dict | None, interaction: dict, registration: dict, registration_path: Path
) -> dict:
    kind = interaction.get("kind")
    if kind == "decision" and interaction.get("origin") == "user":
        if not _is_resume_request(prompt):
            return _paused_context(interaction)
        interaction = {key: value for key, value in interaction.items() if key != "origin"}
        registration["interaction"] = interaction
        if not _atomic_write_json(registration_path, registration):
            return {}
    if kind != "manual" and question is not None:
        wait_answer = _wait_answer(prompt, question)
        if wait_answer == "pause":
            registration["interaction"] = {"state": "paused", "kind": "discussion", "origin": "user"}
            if not _atomic_write_json(registration_path, registration):
                return {}
            return _context(
                "The user chose to stop checking for now. The plan is explicitly paused; honor that choice until they request continuation."
            )
        automatic = kind == "discussion" and interaction.get("origin") == "automatic"
        old_wait = kind == "discussion" and interaction.get("origin") != "user" and wait_answer == "continue"
        false_wait_decision = (
            kind == "decision"
            and wait_answer == "continue"
            and interaction.get("message") in {item["question"] for item in question["questions"]}
        )
        if automatic or old_wait or false_wait_decision:
            registration.pop("interaction", None)
            if not _atomic_write_json(registration_path, registration):
                return {}
            return _context(
                "This message answers the agent's pending question. The automatic discussion pause is cleared. "
                "Interpret the actual answer, honor any requested stop or required approval, and continue authorized work. "
                "A running job remains authorized; retain its handle and wait for the result without asking again."
            )
        if kind == "decision":
            return _context(
                "This is input to the pending material decision, not a new interruption. Interpret the actual answer. "
                "If it resolves the decision and authorizes proceeding, apply the agreed plan amendments, run "
                "`pilot plan-state resume` with the current lane flag, and continue in this turn. Do not require "
                "an extra standalone resume message. Otherwise keep the decision pending and answer or clarify it."
            )
    return _paused_context(interaction)


def _pause_for_user(path: Path, registration: dict) -> dict:
    """An explicit pause outranks one-shot gates and upgrades automatic provenance."""
    interaction = registration.get("interaction")
    if isinstance(interaction, dict) and interaction.get("state") == "paused" and interaction.get("kind") == "manual":
        return _paused_context(interaction)
    if isinstance(interaction, dict) and interaction.get("kind") == "decision":
        held = {**interaction, "state": "paused", "origin": "user"}
    else:
        held = {"state": "paused", "kind": "discussion", "origin": "user"}
    registration["interaction"] = held
    if not _atomic_write_json(path, registration):
        return {}
    return _paused_context(held)


def handle(payload: object) -> dict:
    """Return UserPromptSubmit context and update the registered interaction."""
    if not isinstance(payload, dict):
        return {}
    session_id = resolve_hook_session_id(payload.get("session_id", ""))
    loaded = _load_registration(session_id)
    if loaded is None:
        return {}
    registration_path, registration, plan = loaded
    approved, plan_type = _read_plan_approved_and_type(str(plan))
    registration = _migrate_legacy_pause(session_id, registration_path, registration, plan, plan_type)

    prompt_raw = payload.get("prompt")
    if not isinstance(prompt_raw, str):
        return {}
    prompt = prompt_raw.strip()
    normalized = prompt.lower()

    # Before every one-shot consumer below: a notification must neither pause the
    # plan nor spend a marker that belongs to the human's next message.
    if _is_harness_prompt(prompt):
        held = registration.get("interaction")
        if (
            isinstance(held, dict)
            and held.get("state") == "paused"
            and (plan_type != "Build" or (held.get("kind") == "discussion" and held.get("origin") == "user"))
        ):
            return _paused_context(held)
        return {}
    if _consume_expected_continuation(session_id, prompt):
        return {}
    status = str(registration.get("status", "")).upper()
    interaction = registration.get("interaction")
    paused = isinstance(interaction, dict) and interaction.get("state") == "paused"
    if normalized in _PAUSE_COMMANDS and status != "VERIFIED":
        return _pause_for_user(registration_path, registration)
    transcript = payload.get("transcript_path")
    question = latest_structured_question(transcript) if isinstance(transcript, str) else None
    manual_switch_marker = _manual_switch_gate_pending(
        session_id, plan, status, approved, plan_type, interaction=registration.get("interaction")
    )
    if manual_switch_marker is not None:
        if _is_resume_request(prompt):
            interaction = registration.get("interaction")
            if isinstance(interaction, dict) and interaction.get("state") == "paused":
                registration.pop("interaction", None)
                if not _atomic_write_json(registration_path, registration):
                    return {}
            manual_switch_marker.unlink(missing_ok=True)
            return _context(
                f"The user completed the Manual model-switch handoff for {plan}. The one-shot gate is consumed; "
                "invoke `spec-implement` for this approved PENDING plan now. Do not repeat plan approval or re-arm "
                "the model-switch gate."
            )
        return _context(
            "The Manual model switch is still pending. Answer without starting implementation and keep the gate "
            "armed. The user may run `/model`; a clear request to resume or continue completes this handoff."
        )
    held = paused and (interaction.get("kind") in {"manual", "decision"} or interaction.get("origin") == "user")
    if not held and _consume_expected_verify_gate(session_id, plan, status, plan_type):
        return _context(
            "This user message answers a pending /spec verification gate; it is expected input, not a new "
            "implementation interruption. Interpret it against the gate choices, preserve any explicit approval, "
            "and continue or re-arm the gate as required."
        )
    if status == "VERIFIED":
        return {}

    if plan_type == "Build" and not (
        paused and interaction.get("kind") == "discussion" and interaction.get("origin") == "user"
    ):
        paused = False

    if _is_resume_request(prompt):
        if paused and interaction.get("kind") == "manual":
            return _paused_context(interaction)
        if paused and interaction.get("kind") == "decision":
            return _paused_reply(prompt, question, interaction, registration, registration_path)
        if paused:
            registration.pop("interaction", None)
            if not _atomic_write_json(registration_path, registration):
                return {}
        return _context(
            f"Resume the active Pilot plan at {plan} (Status: {registration.get('status', 'PENDING')}). "
            "Re-read it, apply any agreed amendments before implementation, and continue from its current task."
        )

    if normalized == "done" and paused and interaction.get("kind") == "manual":
        task_number = interaction.get("task_number")
        registration.pop("interaction", None)
        if not _atomic_write_json(registration_path, registration):
            return {}
        task_label = f"Task {task_number}" if isinstance(task_number, int) else "The manual task"
        return _context(
            f"The user explicitly confirmed {task_label} is done. Verify every observable criterion; "
            "only then mark it complete and continue. Re-enter the manual pause if verification fails."
        )

    if paused:
        return _paused_reply(prompt, question, interaction, registration, registration_path)

    if plan_type == "Build":
        return {}

    # A slash/dollar workflow invocation owns its own dispatch semantics. The
    # hook must not reinterpret `/spec <plan>` or a new `/spec <task>` as an
    # interruption of the currently registered plan.
    if _is_spec_command(normalized) or not approved:
        return {}

    # Answers belong to the question the agent asked, not a fresh interruption.
    # Keep explicit/manual/decision pauses authoritative by checking this only
    # after the paused branch above. Codex prose answers are covered by the
    # autonomous default and the bound approval/verification gates above.
    if question is not None:
        return {}
    if not read_workflow_toggle("autoPause"):
        return _context(
            "Answer the user's message and incorporate its steering, then continue the authorized plan. "
            "Pause only when the user explicitly asks to pause or a required decision or user-owned action blocks work."
        )

    registration["interaction"] = {"state": "paused", "kind": "discussion", "origin": "automatic"}
    if not _atomic_write_json(registration_path, registration):
        return {}
    return _context(
        "The user's new message interrupted an approved /spec run, so the plan is now paused for discussion. "
        "Answer the message without resuming implementation; the plan remains paused until a clear request to resume or continue."
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = handle(payload)
    except Exception:
        result = {}
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
