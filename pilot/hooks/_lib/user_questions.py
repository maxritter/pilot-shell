"""Recognize structured questions and narrowly identify routine waiting checkpoints."""

from __future__ import annotations

import json
import re
from pathlib import Path

QUESTION_TOOLS = frozenset({"AskUserQuestion", "request_user_input", "request_user_input_async"})


def question_tool(name: object) -> bool:
    return isinstance(name, str) and name.rsplit(".", 1)[-1] in QUESTION_TOOLS


def _recent_events(transcript_path: str):
    """Read newest events first without scanning a session's entire history.

    Bound malformed or enormous transcript rows as well as total IO. A missing
    event supplies no evidence of an answer; callers never invent permission.
    """
    try:
        with Path(transcript_path).open("rb") as stream:
            position = stream.seek(0, 2)
            remaining = 8 * 1024 * 1024
            suffix = b""
            dropping = False
            while position and remaining:
                size = min(position, remaining, 64 * 1024)
                position -= size
                remaining -= size
                stream.seek(position)
                chunk = stream.read(size)
                if dropping:
                    boundary = chunk.rfind(b"\n")
                    if boundary < 0:
                        continue
                    chunk = chunk[:boundary]
                    dropping = False
                lines = (chunk + suffix).split(b"\n")
                suffix = lines[0]
                for line in reversed(lines[1:]):
                    if len(line) > 4 * 1024 * 1024:
                        continue
                    try:
                        event = json.loads(line)
                    except (ValueError, UnicodeError):
                        continue
                    if isinstance(event, dict):
                        yield event
                if len(suffix) > 4 * 1024 * 1024:
                    suffix = b""
                    dropping = True
            if not position and suffix and not dropping:
                try:
                    event = json.loads(suffix)
                except (ValueError, UnicodeError):
                    return
                if isinstance(event, dict):
                    yield event
    except (OSError, UnicodeError):
        return


def _question_call(event: dict) -> tuple[dict | None, object, bool]:
    """Extract the last Claude/Codex tool call and its assistant boundary."""
    if event.get("type") == "assistant":
        message = event.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        for block in reversed(content if isinstance(content, list) else []):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                value = block.get("input")
                return (
                    value if question_tool(block.get("name")) and isinstance(value, dict) else None,
                    block.get("id"),
                    True,
                )
        return None, None, True
    payload = event.get("payload")
    if event.get("type") != "response_item" or not isinstance(payload, dict):
        return None, None, False
    if payload.get("type") in ("function_call", "custom_tool_call"):
        value = payload.get("arguments", payload.get("input", {}))
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                value = {}
        return (
            value if question_tool(payload.get("name")) and isinstance(value, dict) else None,
            payload.get("call_id"),
            True,
        )
    return None, None, payload.get("type") == "message" and payload.get("role") == "assistant"


def _results(event: dict) -> dict[str, bool]:
    message = event.get("message")
    content = message.get("content", []) if event.get("type") == "user" and isinstance(message, dict) else []
    results = {}
    for block in content if isinstance(content, list) else []:
        if isinstance(block, dict) and block.get("type") == "tool_result" and isinstance(block.get("tool_use_id"), str):
            results[block["tool_use_id"]] = not block.get("is_error", False)
    payload = event.get("payload")
    if (
        event.get("type") == "response_item"
        and isinstance(payload, dict)
        and payload.get("type") in ("function_call_output", "custom_tool_call_output")
        and isinstance(payload.get("call_id"), str)
    ):
        value = payload.get("output")
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                pass
        failed = isinstance(value, dict) and (
            value.get("error") or value.get("is_error") or value.get("behavior") == "deny"
        )
        results[payload["call_id"]] = not failed
    return results


def latest_structured_question(transcript_path: str, *, unanswered_only: bool = False) -> dict | None:
    """Return the latest actionable question, retaining it through its tool result."""
    results = {}
    for event in _recent_events(transcript_path):
        results.update({key: value for key, value in _results(event).items() if key not in results})
        question, call_id, boundary = _question_call(event)
        if boundary:
            return None if unanswered_only and isinstance(call_id, str) and call_id in results else question
    return None


def decision_has_answer(transcript_path: str, message: str) -> bool:
    """Find the most recent matching question, including after an assistant summary.

    A denied question or an unanswered replacement never counts as user input.
    The caller still interprets the answer; this never clears a decision itself.
    """
    results = {}
    for event in _recent_events(transcript_path):
        results.update({key: value for key, value in _results(event).items() if key not in results})
        question, call_id, _boundary = _question_call(event)
        if question is not None:
            texts = [item.get("question") for item in question.get("questions", []) if isinstance(item, dict)]
            if message in texts or message == "\n".join(text for text in texts if isinstance(text, str))[:1000]:
                return isinstance(call_id, str) and results.get(call_id) is True
            return False  # A later clarification supersedes an older answer.
    return False


_POSITIVE_WAIT = re.compile(r"\b(?:(?:keep|continue) (?:waiting|checking|monitoring|polling)|wait(?: longer)?)\b", re.I)
_MATERIAL = re.compile(
    r"(?:\b(?:cost|charge|payment|budget|quota|deadline|failed|failure|error|permission|credentials?|approve|approval|authorization|cancel|kill|terminate|rollback|delete|publish|commit|sign|contract)\b|[$€£]\s*\d|\b(?:deploy|release|merge)(?: now| it| this| the changes)\b|\b(?:wait(?:ing)? for (?:you|the user|a human)|(?:you|the user) (?:to|must|need to)|manual (?:task|action)|your (?:input|action|approval))\b)",
    re.I,
)
_WAIT_LABEL = re.compile(
    r"^(?:(?:yes|no)[, ]+)?(?:(?:keep|continue) (?:waiting|checking|monitoring|polling)|"
    r"wait(?: longer)?|stop (?:checking|waiting|monitoring)(?: for now)?|stop for now|pause(?: for now)?|"
    r"check (?:later|again later)|continue)$",
    re.I,
)


def routine_wait_question(value: object) -> bool:
    """True only when every question offers continuing or stopping a routine wait."""
    if not isinstance(value, dict):
        return False
    questions = value.get("questions")
    if not isinstance(questions, list) or not questions:
        return False
    for item in questions:
        if not isinstance(item, dict) or not isinstance(item.get("question"), str):
            return False
        text = item["question"]
        options = item.get("options")
        if _MATERIAL.search(text) or not isinstance(options, list) or len(options) < 2:
            return False
        positive_wait = False
        for option in options:
            if not isinstance(option, dict) or not isinstance(option.get("label"), str):
                return False
            label = re.sub(r"\s*\(recommended\)\s*$", "", option["label"], flags=re.I).strip(" .!")
            if not _WAIT_LABEL.fullmatch(label):
                return False
            if not re.search(r"\b(?:no|stop|pause)\b", label, re.I) and _POSITIVE_WAIT.search(label):
                positive_wait = True
            description = option.get("description", "")
            if isinstance(description, str) and _MATERIAL.search(description):
                return False
        if not positive_wait:
            return False
    return True
