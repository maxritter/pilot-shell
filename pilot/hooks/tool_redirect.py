#!/usr/bin/env python3
"""Hook to block built-in WebSearch/WebFetch/Plan mode and research-type Agent sub-agent calls.

Agent calls for /spec workflow reviewers (pilot:spec-review, pilot:changes-review)
pass through silently. Explore and Plan agents are hard-blocked.
Research-pattern agents (description starts with "Research") are blocked.
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
    "Research agent blocked: use Probe CLI, Grep/Glob, and CodeGraph directly",
    "Research sub-agents are blocked. Use direct tools instead:\n"
    "-> Probe: probe search \"query\" ./ --max-results 5 --max-tokens 2000\n"
    "-> Grep/Glob: for exact pattern matching\n"
    "-> Graph: codegraph_search/codegraph_callers/codegraph_callees/codegraph_impact",
)

BLOCKED_AGENT_REASONS: dict[str, tuple[str, str]] = {
    "Explore": (
        "Explore agent blocked: use Probe CLI + CodeGraph",
        "The Explore agent is blocked. Use Probe CLI for intent-based search and "
        "CodeGraph for structural analysis instead.\n"
        "-> Probe: probe search \"query\" ./ --max-results 5 --max-tokens 2000\n"
        "-> Graph: codegraph_search/codegraph_callers/codegraph_callees/codegraph_impact/codegraph_context",
    ),
    "Plan": (
        "Plan agent blocked: use /spec for structured planning",
        "The Plan agent is blocked. Use /spec for structured planning with TDD, "
        "verification, and code review instead.\n"
        "-> Type /spec <task description> to start a structured planning workflow",
    ),
}

# Agent sub-agent types that pass through without any warning
SILENT_AGENT_TYPES: set[str] = {"pilot:spec-review", "pilot:changes-review"}

# Agent sub-agent types that are hard-blocked
BLOCKED_AGENT_TYPES: set[str] = set(BLOCKED_AGENT_REASONS)

# Patterns in Agent description that indicate research (case-insensitive)
RESEARCH_PATTERN: re.Pattern[str] = re.compile(r"^research\b", re.IGNORECASE)


def run_tool_redirect() -> int:
    """Block WebSearch/WebFetch/Explore/Plan agents and research-pattern agents."""
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
        return 0

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
