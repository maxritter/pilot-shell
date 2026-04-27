#!/usr/bin/env python3
"""Hook to block built-in WebSearch/WebFetch/Plan mode and research/explore-type Agent calls.

Agent calls for /spec workflow reviewers (pilot:spec-review, pilot:changes-review)
and web-search-agent (used by /prd deep research) pass through silently.
Explore and Plan agents are hard-blocked (both by subagent_type AND description).
Research-pattern agents (description starts with "Research") are blocked,
unless the subagent_type is in SILENT_AGENT_TYPES.
All other Agent calls pass through silently.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import pre_tool_use_deny

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

# Agent sub-agent types that pass through without any warning
SILENT_AGENT_TYPES: set[str] = {
    "pilot:spec-review",
    "pilot:changes-review",
    "pilot:web-search-agent",
    "web-search-agent",
}

# Agent sub-agent types that are hard-blocked
BLOCKED_AGENT_TYPES: set[str] = set(BLOCKED_AGENT_REASONS)

# Patterns in Agent description that indicate research or exploration (case-insensitive)
RESEARCH_PATTERN: re.Pattern[str] = re.compile(r"^research\b", re.IGNORECASE)
EXPLORE_PATTERN: re.Pattern[str] = re.compile(r"\bexplore\b", re.IGNORECASE)

# Strip leading `git -C <path>` and `git -c <key=val>` global options before pattern matching.
GIT_GLOBAL_OPTS_RE: re.Pattern[str] = re.compile(r"\bgit\s+(?:-[Cc]\s+\S+\s+)+")

# Split a Bash command into independent shell segments at command separators.
SHELL_SEGMENT_SEP_RE: re.Pattern[str] = re.compile(r"(?:&&|\|\||;|\n)")

# Truly irreversible git variants. Plain `git push` and `git commit` are NOT here —
# pilot's social rule already requires explicit user authorization for those, and
# hard-denying them would break daily workflow without adding safety.
DANGEROUS_GIT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Force pushes (short and long forms; -f and --force-with-lease=<ref>)
    (re.compile(r"\bgit\s+push\b[^\n|;&]*\s(?:--force(?:-with-lease)?(?:=\S+)?|-f)\b"), "git push --force"),
    (re.compile(r"\bgit\s+push\b[^\n|;&]*--mirror\b"), "git push --mirror"),
    # Remote branch delete: colon-syntax (`git push origin :branch`) and long-form (`git push --delete`)
    (re.compile(r"\bgit\s+push\s+\S+\s+:[^\s]"), "git push <remote> :<branch>"),
    (re.compile(r"\bgit\s+push\b[^\n|;&]*--delete\b"), "git push --delete"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "git reset --hard"),
    # Force clean: short forms (-f, -fd) and long form (--force)
    (re.compile(r"\bgit\s+clean\b[^\n|;&]*\s-[a-zA-Z]*f"), "git clean -f"),
    (re.compile(r"\bgit\s+clean\b[^\n|;&]*--force\b"), "git clean --force"),
    # Force-delete branch: short (-D) and long (--delete --force in any order)
    (re.compile(r"\bgit\s+branch\b[^\n|;&]*\s-D\b"), "git branch -D"),
    (re.compile(r"\bgit\s+branch\b[^\n|;&]*--delete\b[^\n|;&]*(?:--force|-f)\b"), "git branch --delete --force"),
    (re.compile(r"\bgit\s+branch\b[^\n|;&]*(?:--force|-f)\b[^\n|;&]*--delete\b"), "git branch --force --delete"),
    # Discard all unstaged
    (re.compile(r"\bgit\s+checkout\s+\.(?:\s|$)"), "git checkout ."),
    # Discard files via `[<ref>] -- <file>` — any revision before `--` is destructive
    (re.compile(r"\bgit\s+checkout\s+(?:\S+\s+)?--\s+\S"), "git checkout -- <file>"),
    # Restore: working-tree forms. Default git restore (no --staged) writes the working tree.
    (re.compile(r"\bgit\s+restore\s+(?!--staged\b)\."), "git restore ."),
    # `git restore` with --source=<rev> ending in `.` — broad-pathspec, working-tree destructive.
    (re.compile(r"\bgit\s+restore\b[^\n|;&]*--source(?:=|\s+)\S+[^\n|;&]*\s\.(?:\s|$)"), "git restore --source ."),
    # `git restore --worktree` (with or without --staged) ending in broad pathspec
    (re.compile(r"\bgit\s+restore\b[^\n|;&]*--worktree\b[^\n|;&]*\s\.(?:\s|$)"), "git restore --worktree ."),
]


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
            continue  # this segment is a read-only preview
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

    # Agent: silent pass for /spec reviewers, block Explore/Plan/research, warn others
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

    # Bash: dangerous git pattern check (denies on match; otherwise falls through to BLOCKS check)
    if tool_name == "Bash":
        command = hook_data.get("tool_input", {}).get("command", "")
        match = _check_dangerous_git(command)
        if match:
            pattern_name, reason = match
            sys.stderr.write(f"\033[0;31m[Pilot] Dangerous git blocked: {pattern_name}\033[0m\n")
            print(pre_tool_use_deny(reason))
            return 2

    # WebSearch/WebFetch: hard block
    if tool_name in BLOCKS:
        info = BLOCKS[tool_name]
        reason = f"{info['message']}\n-> {info['alternative']}\nExample: {info['example']}"
        sys.stderr.write(f"\033[0;31m[Pilot] {info['message']}\033[0m\n")
        print(pre_tool_use_deny(reason))
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(run_tool_redirect())
