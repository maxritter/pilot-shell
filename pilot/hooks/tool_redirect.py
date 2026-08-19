#!/usr/bin/env python3
"""Hook to block built-in WebSearch/WebFetch (the MCP replacements return full content).

All Agent calls pass through untouched: built-in agents (Explore, Plan,
general-purpose), Pilot reviewer agents, and ad-hoc fan-outs alike. Native
subagents are a legitimate way to work; whether to use /spec instead of the
Plan agent is the user's call, not a hook's.

Also nudges (non-deny) on recursive code-search Bash commands (grep -r, rg, find,
fd, ag), built-in Grep, and built-in Glob - pointing at codegraph_explore /
semble search. Throttled per-(category, session) so the reminder stays salient.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import pre_tool_use_context, pre_tool_use_deny, resolve_session_id

BLOCKS: dict[str, dict[str, str]] = {
    "WebSearch": {
        "message": "WebSearch is blocked (use MCP alternative)",
        "alternative": "Use ToolSearch to load mcp__plugin_pilot_web-search__search, then call it directly",
        "example": 'ToolSearch(query="+web-search search") then mcp__plugin_pilot_web-search__search(query="...")',
    },
    "WebFetch": {
        "message": "WebFetch is blocked (truncates at ~8KB)",
        "alternative": "Use ToolSearch to load mcp__plugin_pilot_web-fetch__fetch_url, then call it directly",
        "example": 'ToolSearch(query="+web-fetch fetch") then mcp__plugin_pilot_web-fetch__fetch_url(url="...")',
    },
}

SHELL_SEGMENT_SEP_RE: re.Pattern[str] = re.compile(r"(?:&&|\|\||;|\n)")


_LEADING_PREFIX_RE: re.Pattern[str] = re.compile(
    r"^\s*(?:time|nice(?:\s+-n\s+\d+)?|sudo(?:\s+-\w+)?|env(?:\s+\S+=\S+)*)\s+"
)

_PIPELINE_FILTER_FIRST_TOKENS: set[str] = {
    "cat",
    "echo",
    "printf",
    "tail",
    "head",
    "awk",
    "sed",
    "tr",
    "sort",
    "uniq",
    "ls",
    "curl",
    "wget",
    "xargs",
}

_GREP_RECURSIVE_FLAG_RE: re.Pattern[str] = re.compile(r"(?:^|\s)(?:-[a-zA-Z]*[rR][a-zA-Z]*|--recursive|--include)\b")


def _is_single_file_path(token: str) -> bool:
    """True if token looks like a single-file path (extension after last slash, no glob)."""
    if not token or token.startswith("-"):
        return False
    if "*" in token or "?" in token:
        return False
    last = token.rsplit("/", 1)[-1]
    if "." not in last or last in {".", ".."}:
        return False
    name, _, ext = last.rpartition(".")
    if not name or not ext:
        return False
    return ext.replace("_", "").isalnum()


def _rg_targets_single_file(segment: str) -> bool:
    """True if rg invocation has a single-file path as its last positional arg."""
    tokens = segment.split()
    for token in reversed(tokens[1:]):
        if token.startswith("-"):
            continue
        return _is_single_file_path(token)
    return False


def _classify_segment(segment: str, first_token: str) -> str | None:
    """Classify a single shell segment as a recursive search command, or None."""
    if first_token == "grep":
        rest = segment[len(first_token) :]
        if _GREP_RECURSIVE_FLAG_RE.search(rest):
            return "grep"
        return None
    if first_token == "rg":
        if _rg_targets_single_file(segment):
            return None
        return "rg"
    if first_token == "find":
        return "find"
    if first_token == "fd":
        return "fd"
    if first_token == "ag":
        return "ag"
    return None


def classify_search_command(cmd: str) -> str | None:
    """Return search category (grep/rg/find/fd/ag) for the first matching shell segment, else None.

    Splits on `;`, `&&`, `||`, `|`, newline. Skips segments whose first token is a pipeline
    filter (cat, curl, xargs, etc.) or `git` (git grep is allowed).
    """
    for raw_segment in SHELL_SEGMENT_SEP_RE.split(cmd):
        segment = _LEADING_PREFIX_RE.sub("", raw_segment.strip())
        if not segment:
            continue
        first_token = segment.split(maxsplit=1)[0]
        if not first_token or first_token == "git" or first_token in _PIPELINE_FILTER_FIRST_TOKENS:
            continue
        category = _classify_segment(segment, first_token)
        if category:
            return category
    return None


_NUDGE_BASH_GREP = (
    "Recursive grep on the project. For symbol search by name, codegraph_explore is faster "
    "(one call returns structured source plus the call path). For find-by-intent, semble search 'query' ./ "
    "ranks results by relevance (hybrid BM25+semantic). If you need exact text "
    "in known files, proceed."
)
_NUDGE_BASH_RG = (
    "Recursive ripgrep. For symbol search or project structure use codegraph_explore; "
    "for intent-based code search use semble search 'query' ./ "
    "(or mcp__semble__search). If you need exact text/regex on the filesystem, proceed."
)
_NUDGE_BASH_FIND = (
    "Project file enumeration. codegraph_explore surfaces the files that define or relate to "
    "a symbol faster than a raw tree walk. If you need a filesystem-level operation (e.g., -delete, -exec), proceed."
)
_NUDGE_BASH_FD = (
    "Project file discovery. codegraph_explore surfaces structurally-related files faster. "
    "Proceed if you specifically need fd's filesystem behavior."
)
_NUDGE_BASH_AG = (
    "Silver searcher. codegraph_explore (by symbol/structure) and semble search (by intent) are faster "
    "on indexed projects. Proceed if you need exact text in arbitrary filesystem paths."
)
_NUDGE_BUILTIN_GREP = (
    "Built-in Grep is valid for exact text/regex and as a completeness check after "
    "codegraph_explore. For symbol search by name, codegraph_explore is faster. For "
    "intent-based code search, semble search 'query' ./ (or mcp__semble__search) "
    "ranks by relevance."
)
_NUDGE_BUILTIN_GLOB = (
    "Built-in Glob lists files by pattern. For project structure by symbol, codegraph_explore "
    "surfaces the relevant files faster (with call path and metadata). Proceed if you "
    "need exact-pattern matching."
)

_BASH_NUDGE_BY_CATEGORY: dict[str, str] = {
    "grep": _NUDGE_BASH_GREP,
    "rg": _NUDGE_BASH_RG,
    "find": _NUDGE_BASH_FIND,
    "fd": _NUDGE_BASH_FD,
    "ag": _NUDGE_BASH_AG,
}


def _throttle_sentinel_path() -> Path:
    """Return path to per-session search-nudge sentinel file.

    Tests monkeypatch this to redirect to a tmp_path.
    """
    return Path.home() / ".pilot" / "sessions" / resolve_session_id() / "search_nudge_sent.json"


def _nudge_already_sent(key: str) -> bool:
    """Best-effort check whether a nudge was already sent for this session+key."""
    try:
        path = _throttle_sentinel_path()
        if not path.exists():
            return False
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    sent = data.get("sent")
    return isinstance(sent, list) and key in sent


def _mark_nudge_sent(key: str) -> None:
    """Record that a nudge for this key was sent. Best-effort, never raises."""
    try:
        path = _throttle_sentinel_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        sent: list[str] = []
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if isinstance(data, dict) and isinstance(data.get("sent"), list):
                    sent = list(data["sent"])
            except (json.JSONDecodeError, ValueError, OSError):
                sent = []
        if key not in sent:
            sent.append(key)
        path.write_text(json.dumps({"sent": sent}))
    except OSError:
        pass


def _bash_search_nudge(command: str) -> str | None:
    """Return Bash search-nudge text if applicable and not throttled, else None."""
    category = classify_search_command(command)
    if category is None:
        return None
    key = f"Bash:{category}"
    if _nudge_already_sent(key):
        return None
    _mark_nudge_sent(key)
    return _BASH_NUDGE_BY_CATEGORY.get(category)


def _builtin_tool_nudge(tool_name: str) -> str | None:
    """Return nudge for built-in Grep/Glob if not throttled, else None."""
    if tool_name == "Grep":
        if _nudge_already_sent("Grep"):
            return None
        _mark_nudge_sent("Grep")
        return _NUDGE_BUILTIN_GREP
    if tool_name == "Glob":
        if _nudge_already_sent("Glob"):
            return None
        _mark_nudge_sent("Glob")
        return _NUDGE_BUILTIN_GLOB
    return None


def _extract_shell_commands(tool_name: str, tool_input: dict) -> list[str]:
    """Return the list of shell-command strings carried by this tool invocation."""
    if tool_name != "Bash":
        return []
    command = tool_input.get("command", "")
    return [command] if isinstance(command, str) and command else []


def run_tool_redirect() -> int:
    """Block WebSearch/WebFetch; nudge on recursive search; everything else passes through."""
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = hook_data.get("tool_name", "")

    if tool_name == "Bash":
        tool_input = hook_data.get("tool_input", {})
        commands = _extract_shell_commands(tool_name, tool_input)
        if commands:
            nudge = _bash_search_nudge(commands[0])
            if nudge:
                print(pre_tool_use_context(nudge))
                return 0

    if tool_name in {"Grep", "Glob"}:
        nudge = _builtin_tool_nudge(tool_name)
        if nudge:
            print(pre_tool_use_context(nudge))
            return 0

    if tool_name in BLOCKS:
        info = BLOCKS[tool_name]
        reason = f"{info['message']}\n-> {info['alternative']}\nExample: {info['example']}"
        sys.stderr.write(f"\033[0;31m[Pilot] {info['message']}\033[0m\n")
        print(pre_tool_use_deny(reason))
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(run_tool_redirect())
