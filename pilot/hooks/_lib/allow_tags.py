"""Allow-tag parsing — port of sensitive-canary's user-prompt tag bypass.

Tags `[allow-secret]` / `[allow-all]` are honoured ONLY from user-role transcript
messages. Tags in assistant messages or in command-string content are ignored
(prompt-injection defense).

Authoritative reference for transcript tail logic:
sensitive-canary/src/pre-tool-use-hook.ts:75-96. The flag
`tool_result_after_last_text` tracks SUBSEQUENT TOP-LEVEL JSONL RECORDS, not
content blocks within the same record.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .secret_scanner import Finding

MAX_TRANSCRIPT_TAIL_BYTES = 65_536  # 64 KB

_ALLOW_TAG_RE = re.compile(r"\[allow-([a-z]+)\]", re.IGNORECASE)


def parse_allow_tags(text: str) -> set[str]:
    """Extract `[allow-<name>]` tags from text. Names are lowercased."""
    if not text:
        return set()
    return {m.group(1).lower() for m in _ALLOW_TAG_RE.finditer(text)}


def _has_text_block(content: object) -> bool:
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        return any(isinstance(b, dict) and b.get("type") == "text" for b in content)
    return False


def _extract_text(content: object) -> str:
    """Concatenate text blocks (or return string content as-is)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text":
                t = b.get("text")
                if isinstance(t, str):
                    parts.append(t)
        return "\n".join(parts)
    return ""


def load_from_transcript(transcript_path: str, *, for_post_tool_use: bool = False) -> set[str]:
    """Read tail of transcript JSONL and resolve effective allow tags.

    Args:
        transcript_path: filesystem path to Claude Code's session transcript JSONL.
        for_post_tool_use: when True, treat the LAST tool_result-only user record
            as the call that triggered THIS PostToolUse hook (so the tag is NOT
            yet consumed by it). Earlier tool_result records still consume the tag.

    Returns set of allow-tag names (lowercased), e.g. {"secret"} or {"all"}.
    Returns empty set on missing/unreadable file or when the most recent tag has
    been consumed by a subsequent tool call.
    """
    try:
        path = Path(transcript_path)
        size = path.stat().st_size
    except OSError:
        return set()

    try:
        if size <= MAX_TRANSCRIPT_TAIL_BYTES:
            raw = path.read_text(errors="replace")
        else:
            with path.open("rb") as f:
                f.seek(size - MAX_TRANSCRIPT_TAIL_BYTES)
                raw = f.read().decode("utf-8", errors="replace")
    except OSError:
        return set()

    last_user_text: str | None = None
    tool_result_records_after_text = 0
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = parsed.get("message") if isinstance(parsed, dict) else None
        if not isinstance(msg, dict):
            continue
        if msg.get("role") != "user":
            continue
        content = msg.get("content")
        if content is None:
            continue
        if _has_text_block(content):
            last_user_text = _extract_text(content)
            tool_result_records_after_text = 0
        else:
            tool_result_records_after_text += 1

    if last_user_text is None:
        return set()

    if for_post_tool_use:
        # The LAST tool_result record represents the call that triggered THIS
        # PostToolUse hook — the tag is NOT yet consumed by it. But any earlier
        # tool_result already used it up.
        if tool_result_records_after_text > 1:
            return set()
    else:
        if tool_result_records_after_text > 0:
            return set()

    return parse_allow_tags(last_user_text)


def apply_allow_tags(findings: list[Finding], tags: set[str]) -> list[Finding]:
    """Drop findings per tags + dedupe by secret_value.

    All findings in this port are secret-category (PII rules excluded).
    `[allow-all]` and `[allow-secret]` both drop everything.
    """
    deduped: list[Finding] = []
    seen: set[str] = set()
    for f in findings:
        if f.secret_value in seen:
            continue
        seen.add(f.secret_value)
        deduped.append(f)

    if not tags:
        return deduped
    if "all" in tags or "secret" in tags:
        return []
    return deduped
