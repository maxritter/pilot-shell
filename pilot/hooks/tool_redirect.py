#!/usr/bin/env python3
"""Privately nudge built-in tools toward Pilot's preferred alternatives.

Authenticated Claude artifact URLs pass through to WebFetch because only the
built-in tool has access to the user's claude.ai session.

The hook does not gate Agent calls. Delegation limits live in Pilot's shared
instructions because this PreToolUse hook has no reliable semantic signal for
whether a task is simple, independent, or an explicitly required workflow
review. It therefore neither encourages fan-out nor blocks qualifying agents.

Also nudges (non-deny) on recursive code-search Bash commands (grep -r, rg, find,
fd, ag), built-in Grep, and built-in Glob - pointing at codegraph_explore /
semble search. Throttled per-(category, session) so the reminder stays salient.

Reminds (non-deny, not throttled) on Bash commands that edit files (sed -i,
heredoc or redirect into a project file, tee, inline python/node scripts that
write files) that the user wants changes made with the Edit/Write tools, where
they show up as a diff in the terminal. The command itself is never blocked.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import pre_tool_use_context, resolve_session_id

WEB_TOOL_NUDGES: dict[str, dict[str, str]] = {
    "WebSearch": {
        "message": "Prefer the Pilot web-search MCP when it is available",
        "alternative": "Use ToolSearch to load mcp__plugin_pilot_web-search__search, then call it directly",
        "example": 'ToolSearch(query="+web-search search") then mcp__plugin_pilot_web-search__search(query="...")',
    },
    "WebFetch": {
        "message": "Prefer the Pilot web-fetch MCP when it is available because built-in output may truncate",
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


def _is_authenticated_claude_artifact_url(tool_input: object) -> bool:
    """Return whether WebFetch needs the user's Claude session for this URL."""
    if not isinstance(tool_input, dict):
        return False
    url = tool_input.get("url")
    if not isinstance(url, str):
        return False
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.port not in {None, 443}:
            return False
    except ValueError:
        return False
    if parsed.hostname == "preview.claude.ai":
        return True
    return parsed.hostname == "claude.ai" and parsed.path.startswith("/code/artifact/")


# --- Shell file-edit reminder ------------------------------------------------
# Claude Code's bypass-permissions mode tells the model to prefer heredocs, sed
# and inline scripts over the Edit/Write tools. Those edits render no diff in
# the terminal, so the user cannot see what changed. Point back at the dedicated
# tools on every such command; the rule text alone did not survive the harness
# hint. Deliberately a reminder, not a deny: a heuristic match must never stop a
# user's legitimate shell work.

_TEMP_TARGET_PREFIXES: tuple[str, ...] = ("/tmp/", "/private/tmp/", "/var/folders/", "/dev/", "$TMPDIR", "${TMPDIR")

_QUOTED_SPAN_RE: re.Pattern[str] = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
_HEREDOC_OPEN_RE: re.Pattern[str] = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n")
_REDIRECT_RE: re.Pattern[str] = re.compile(r"(?<![<>&\d])\d?>{1,2}\s*(?P<target>[^\s&|;)]+)")
_TEE_RE: re.Pattern[str] = re.compile(r"(?:^|\|)\s*tee\s+(?:-[a-zA-Z]+\s+)*(?P<target>[^\s&|;)]+)")
_INLINE_INTERPRETER_RE: re.Pattern[str] = re.compile(
    r"(?:^|\s)(?:uv\s+run\s+(?:\S+\s+)*?)?(?:python[0-9.]*|node|bun|deno|perl|ruby)\s+(?:-[ce](?:\s|$)|--eval\b|-\s*<<)"
)
_WRITE_IDIOM_RE: re.Pattern[str] = re.compile(
    r"write_text\(|write_bytes\(|open\([^)]*['\"][wax]\+?b?['\"]|open\([^)]*['\"]>|writeFileSync|writeFile\(|appendFile"
    r"|Bun\.write\(|Deno\.write|File\.(?:write|open)\(|shutil\.(?:copy|move)|os\.replace\(|os\.rename\("
)
_SED_IN_PLACE_OPTION_RE: re.Pattern[str] = re.compile(r"^-(?:[a-zA-Z]*i[a-zA-Z]*)(?:\.\S*)?$|^--in-place")
_PERL_IN_PLACE_RE: re.Pattern[str] = re.compile(r"^perl\s+(?:-\S+\s+)*-[a-zA-Z]*i")
_AWK_IN_PLACE_RE: re.Pattern[str] = re.compile(r"^g?awk\s+(?:\S+\s+)*-i\s+inplace\b")


def _is_temp_target(target: str) -> bool:
    return target.strip("'\"").startswith(_TEMP_TARGET_PREFIXES)


def _strip_heredoc_bodies(cmd: str) -> str:
    """Remove heredoc bodies so `>` inside embedded scripts is not read as a redirect."""
    out: list[str] = []
    pos = 0
    while True:
        match = _HEREDOC_OPEN_RE.search(cmd, pos)
        if not match:
            out.append(cmd[pos:])
            return "".join(out)
        out.append(cmd[pos : match.end()])
        terminator = re.compile(r"^\s*" + re.escape(match.group(2)) + r"\s*$", re.MULTILINE)
        end = terminator.search(cmd, match.end())
        pos = end.end() if end else len(cmd)


def _sed_edits_in_place(segment: str) -> bool:
    tokens = segment.split()
    if not tokens or tokens[0] != "sed":
        return False
    for token in tokens[1:]:
        if not token.startswith("-"):
            return False
        if _SED_IN_PLACE_OPTION_RE.match(token):
            return True
    return False


def classify_shell_file_edit(cmd: str) -> str | None:
    """Return a short label when the shell command writes or rewrites a file, else None.

    Writes to /tmp, the scratchpad, /dev and $TMPDIR are allowed: keeping command
    output is fine; editing project files through the shell is not.
    """
    for raw_segment in SHELL_SEGMENT_SEP_RE.split(cmd):
        segment = _LEADING_PREFIX_RE.sub("", raw_segment.strip())
        if _sed_edits_in_place(segment):
            return "in-place edit with sed -i"
        if _PERL_IN_PLACE_RE.match(segment):
            return "in-place edit with perl -i"
        if _AWK_IN_PLACE_RE.match(segment):
            return "in-place edit with awk -i inplace"

    if _INLINE_INTERPRETER_RE.search(cmd) and _WRITE_IDIOM_RE.search(cmd):
        return "inline script that writes files"

    scannable = _QUOTED_SPAN_RE.sub("QUOTED", _strip_heredoc_bodies(cmd))
    for match in _REDIRECT_RE.finditer(scannable):
        target = match.group("target")
        if target.startswith("&") or _is_temp_target(target):
            continue
        return "output redirected into a file"
    for match in _TEE_RE.finditer(scannable):
        if not _is_temp_target(match.group("target")):
            return "tee into a file"
    return None


def _file_edit_nudge(label: str) -> str:
    """Reminder text for a shell command that edits a file. Never blocks, never throttled.

    A false match must cost nothing, so this is additionalContext, not a deny:
    the command still runs and the model is told how the user wants edits made.
    """
    return (
        f"This shell command edits a file ({label}). The user does not see a diff for shell edits; "
        "make changes with the Edit tool, or Write for a new file, and keep the shell for running "
        "commands. Output you need to keep can go to /tmp or the scratchpad directory."
    )


def run_tool_redirect() -> int:
    """Privately nudge preferred tools without denying the requested operation."""
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = hook_data.get("tool_name", "")

    if tool_name == "Bash":
        tool_input = hook_data.get("tool_input", {})
        commands = _extract_shell_commands(tool_name, tool_input)
        if commands:
            edit_label = classify_shell_file_edit(commands[0])
            if edit_label:
                print(pre_tool_use_context(_file_edit_nudge(edit_label)))
                return 0
            nudge = _bash_search_nudge(commands[0])
            if nudge:
                print(pre_tool_use_context(nudge))
                return 0

    if tool_name in {"Grep", "Glob"}:
        nudge = _builtin_tool_nudge(tool_name)
        if nudge:
            print(pre_tool_use_context(nudge))
            return 0

    if tool_name == "WebFetch" and _is_authenticated_claude_artifact_url(hook_data.get("tool_input")):
        return 0

    if tool_name in WEB_TOOL_NUDGES:
        info = WEB_TOOL_NUDGES[tool_name]
        reason = f"{info['message']}\n-> {info['alternative']}\nExample: {info['example']}"
        print(pre_tool_use_context(reason))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(run_tool_redirect())
