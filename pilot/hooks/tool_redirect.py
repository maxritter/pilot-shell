#!/usr/bin/env python3
"""Hook to block built-in WebSearch/WebFetch/Plan mode and research/explore-type Agent calls.

Agent calls for /spec workflow reviewers (pilot:spec-review, pilot:changes-review)
and web-search-agent (used by /prd deep research) pass through silently.
Explore and Plan agents are hard-blocked (both by subagent_type AND description).
Research-pattern agents (description starts with "Research") are blocked,
unless the subagent_type is in SILENT_AGENT_TYPES.

Also nudges (non-deny) on recursive code-search Bash commands (grep -r, rg, find,
fd, ag), built-in Grep, and built-in Glob — pointing at codegraph_search /
codegraph_files / probe search. Throttled per-(category, session) so the
reminder stays salient.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import pre_tool_use_context, pre_tool_use_deny

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
    "EnterPlanMode": {
        "message": "EnterPlanMode is blocked (conflicts with /spec workflow)",
        "alternative": "Use /spec for structured planning. Plan mode interferes with autonomous spec execution",
        "example": "Type /spec <task description> to start a structured planning workflow",
    },
    "ExitPlanMode": {
        "message": "ExitPlanMode is blocked (plan mode should not be entered)",
        "alternative": "Plan mode is blocked entirely — use /spec for structured planning",
        "example": "Type /spec <task description> to start a structured planning workflow",
    },
}

RESEARCH_BLOCK = (
    "Research agent blocked: use CodeGraph + Probe CLI directly",
    "Research sub-agents are blocked. Use direct tools instead:\n"
    '-> Orient: codegraph_context(task="...") — ALWAYS start here\n'
    '-> Deep dive: codegraph_search → codegraph_explore(query="SymbolA SymbolB") — full source in one call\n'
    "-> Trace: codegraph_callers/codegraph_callees/codegraph_impact\n"
    '-> Intent search: probe search "query" ./ --max-results 5 --max-tokens 2000\n'
    "-> Exact text: Grep/Glob (last resort)",
)

EXPLORE_BLOCK = (
    "Explore-description agent blocked: use CodeGraph + Probe CLI directly",
    "Agent with Explore description is blocked. Use CodeGraph for structural analysis and "
    "Probe CLI for intent-based search instead.\n"
    '-> Orient: codegraph_context(task="...") — ALWAYS start here\n'
    '-> Deep dive: codegraph_search → codegraph_explore(query="SymbolA SymbolB") — full source in one call\n'
    "-> Trace: codegraph_callers/codegraph_callees/codegraph_impact\n"
    '-> Intent search: probe search "query" ./ --max-results 5 --max-tokens 2000',
)

BLOCKED_AGENT_REASONS: dict[str, tuple[str, str]] = {
    "Explore": (
        "Explore agent blocked: use CodeGraph + Probe CLI",
        "The Explore agent is blocked. Use CodeGraph for structural analysis and "
        "Probe CLI for intent-based search instead.\n"
        '-> Orient: codegraph_context(task="...") — ALWAYS start here\n'
        '-> Deep dive: codegraph_search → codegraph_explore(query="SymbolA SymbolB") — full source in one call\n'
        "-> Trace: codegraph_callers/codegraph_callees/codegraph_impact\n"
        '-> Intent search: probe search "query" ./ --max-results 5 --max-tokens 2000',
    ),
    "Plan": (
        "Plan agent blocked: use /spec for structured planning",
        "The Plan agent is blocked. Use /spec for structured planning with TDD, "
        "verification, and code review instead.\n"
        "-> Type /spec <task description> to start a structured planning workflow",
    ),
}

SILENT_AGENT_TYPES: set[str] = {
    "pilot:spec-review",
    "pilot:changes-review",
    "pilot:web-search-agent",
    "web-search-agent",
}

BLOCKED_AGENT_TYPES: set[str] = set(BLOCKED_AGENT_REASONS)

RESEARCH_PATTERN: re.Pattern[str] = re.compile(r"^research\b", re.IGNORECASE)
EXPLORE_PATTERN: re.Pattern[str] = re.compile(r"\bexplore\b", re.IGNORECASE)

GIT_GLOBAL_OPTS_RE: re.Pattern[str] = re.compile(r"\bgit\s+(?:-[Cc]\s+\S+\s+)+")

SHELL_SEGMENT_SEP_RE: re.Pattern[str] = re.compile(r"(?:&&|\|\||;|\n)")

DANGEROUS_GIT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bgit\s+push\b[^\n|;&]*\s(?:--force(?:-with-lease)?(?:=\S+)?|-f)\b"), "git push --force"),
    (re.compile(r"\bgit\s+push\b[^\n|;&]*--mirror\b"), "git push --mirror"),
    (re.compile(r"\bgit\s+push\s+\S+\s+:[^\s]"), "git push <remote> :<branch>"),
    (re.compile(r"\bgit\s+push\b[^\n|;&]*--delete\b"), "git push --delete"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "git reset --hard"),
    (re.compile(r"\bgit\s+clean\b[^\n|;&]*\s-[a-zA-Z]*f"), "git clean -f"),
    (re.compile(r"\bgit\s+clean\b[^\n|;&]*--force\b"), "git clean --force"),
    (re.compile(r"\bgit\s+branch\b[^\n|;&]*\s-D\b"), "git branch -D"),
    (re.compile(r"\bgit\s+branch\b[^\n|;&]*--delete\b[^\n|;&]*(?:--force|-f)\b"), "git branch --delete --force"),
    (re.compile(r"\bgit\s+branch\b[^\n|;&]*(?:--force|-f)\b[^\n|;&]*--delete\b"), "git branch --force --delete"),
    (re.compile(r"\bgit\s+checkout\s+\.(?:\s|$)"), "git checkout ."),
    (re.compile(r"\bgit\s+checkout\s+(?:\S+\s+)?--\s+\S"), "git checkout -- <file>"),
    (re.compile(r"\bgit\s+restore\s+(?!--staged\b)\."), "git restore ."),
    (re.compile(r"\bgit\s+restore\b[^\n|;&]*--source(?:=|\s+)\S+[^\n|;&]*\s\.(?:\s|$)"), "git restore --source ."),
    (re.compile(r"\bgit\s+restore\b[^\n|;&]*--worktree\b[^\n|;&]*\s\.(?:\s|$)"), "git restore --worktree ."),
]


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
    "Recursive grep on the project. For symbol search by name, codegraph_search is faster "
    "(returns structured matches by file). For find-by-intent, probe search 'query' ./ "
    "--max-results 5 --max-tokens 2000 ranks results by relevance. If you need exact text "
    "in known files, proceed."
)
_NUDGE_BASH_RG = (
    "Recursive ripgrep. For symbol search use codegraph_search; for project file structure "
    "use codegraph_files; for intent-based code search use probe search 'query' ./ "
    "--max-results 5 --max-tokens 2000. If you need exact text/regex on the filesystem, proceed."
)
_NUDGE_BASH_FIND = (
    "Project file enumeration. codegraph_files returns the indexed file tree faster and "
    "with metadata. If you need a filesystem-level operation (e.g., -delete, -exec), proceed."
)
_NUDGE_BASH_FD = (
    "Project file discovery. codegraph_files returns the indexed file tree faster. "
    "Proceed if you specifically need fd's filesystem behavior."
)
_NUDGE_BASH_AG = (
    "Silver searcher. codegraph_search (by symbol) and probe search (by intent) are faster "
    "on indexed projects. Proceed if you need exact text in arbitrary filesystem paths."
)
_NUDGE_BUILTIN_GREP = (
    "Built-in Grep is valid for exact text/regex and as a completeness check after "
    "codegraph_callers. For symbol search by name, codegraph_search is faster. For "
    "intent-based code search, probe search 'query' ./ --max-results 5 --max-tokens 2000 "
    "ranks by relevance."
)
_NUDGE_BUILTIN_GLOB = (
    "Built-in Glob lists files by pattern. For project file structure, codegraph_files "
    "returns the indexed tree faster (with language and symbol metadata). Proceed if you "
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
    session_id = os.environ.get("PILOT_SESSION_ID", "").strip() or "default"
    return Path.home() / ".pilot" / "sessions" / session_id / "search_nudge_sent.json"


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


def _normalize_git_command(command: str) -> str:
    """Strip leading `git -C <path>` / `git -c <key=val>` global options so patterns can match the subcommand.

    Limitation: assumes single-token values for `-C` / `-c`. Quoted values containing
    spaces (e.g., `git -c core.sshCommand="ssh -i key" push --force`) are NOT fully
    normalized — the rest of the command is still scanned for dangerous patterns,
    so force pushes are still caught via the substring match against the trailing
    `git push --force`. Documented gap; not a full bypass in practice.
    """
    return GIT_GLOBAL_OPTS_RE.sub("git ", command)


def _check_dangerous_git(command: str) -> tuple[str, str] | None:
    """Return (pattern_name, deny_reason) when the bash command matches a dangerous git form, else None.

    Splits the command on shell separators (`;`, `&&`, `||`, `|`, newline) and
    checks each segment independently. The `--dry-run` exemption is per-segment so
    a benign `git push --dry-run` in one segment cannot mask a `git reset --hard`
    in the next.
    """
    for segment in SHELL_SEGMENT_SEP_RE.split(command):
        segment = segment.strip()
        if not segment:
            continue
        if "--dry-run" in segment:
            continue
        normalized = _normalize_git_command(segment)
        for pattern, name in DANGEROUS_GIT_PATTERNS:
            if pattern.search(normalized):
                reason = (
                    f"Dangerous git operation blocked: '{name}'. "
                    "This rewrites remote history or destroys local work irreversibly. "
                    "If you intend this, ask the user to confirm and re-issue. "
                    "See pilot/rules/development-practices.md -> 'Git Operations' for the full rule."
                )
                return (name, reason)
    return None


def run_tool_redirect() -> int:
    """Block WebSearch/WebFetch/Explore/Plan agents, research-pattern and explore-pattern agents."""
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = hook_data.get("tool_name", "")

    if tool_name == "Agent":
        tool_input = hook_data.get("tool_input", {})
        subagent_type = tool_input.get("subagent_type", "")
        description = tool_input.get("description", "")

        if subagent_type in SILENT_AGENT_TYPES:
            return 0
        if subagent_type in BLOCKED_AGENT_TYPES:
            stderr_msg, deny_reason = BLOCKED_AGENT_REASONS[subagent_type]
            sys.stderr.write(f"\033[0;31m[Pilot] {stderr_msg}\033[0m\n")
            print(pre_tool_use_deny(deny_reason))
            return 2
        if RESEARCH_PATTERN.search(description):
            stderr_msg, deny_reason = RESEARCH_BLOCK
            sys.stderr.write(f"\033[0;31m[Pilot] {stderr_msg}\033[0m\n")
            print(pre_tool_use_deny(deny_reason))
            return 2
        if EXPLORE_PATTERN.search(description):
            stderr_msg, deny_reason = EXPLORE_BLOCK
            sys.stderr.write(f"\033[0;31m[Pilot] {stderr_msg}\033[0m\n")
            print(pre_tool_use_deny(deny_reason))
            return 2
        return 0

    if tool_name == "Bash":
        command = hook_data.get("tool_input", {}).get("command", "")
        match = _check_dangerous_git(command)
        if match:
            pattern_name, reason = match
            sys.stderr.write(f"\033[0;31m[Pilot] Dangerous git blocked: {pattern_name}\033[0m\n")
            print(pre_tool_use_deny(reason))
            return 2
        nudge = _bash_search_nudge(command)
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
