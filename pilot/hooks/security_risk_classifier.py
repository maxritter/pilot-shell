"""PreToolUse hook — risk-classifies every Bash command before execution.

Decision matrix:
  CRITICAL  → block (deny execution, surface reason to Claude)
  HIGH      → warn  (inject context, require confirmation for policy-gated cmds)
  MEDIUM    → annotate (additionalContext only, never block)
  LOW/INFO  → silent pass

Policy checks layer on top of risk scoring:
  - Some HIGH commands require a gate env var (e.g. terraform apply)
  - Some patterns are unconditionally blocked (pipe-to-shell, eval-subshell)

Exit codes (Claude Code hook protocol):
  0  → allow (optionally with additionalContext)
  2  → deny (block the tool call, reason shown to Claude)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make sibling packages importable from the repo root
_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from security.risk.classifier import RiskLevel, classify
from security.policy.engine import PolicyAction, get_engine
from security.audit.logger import log_command_evaluated, log_policy_blocked
from _lib.util import pre_tool_use_deny, pre_tool_use_context

NC = "\033[0m"
RED = "\033[0;31m"
BOLD_RED = "\033[1;31m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"


def _stderr(msg: str) -> None:
    sys.stderr.write(msg + "\n")


def _format_risk_label(level: RiskLevel) -> str:
    return f"{level.color()}[{level.label()}]{NC}"


def run() -> int:
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = hook_data.get("tool_name", "")
    if tool_name != "Bash":
        return 0

    command = hook_data.get("tool_input", {}).get("command", "").strip()
    if not command:
        return 0

    # ── 1. Risk classification ─────────────────────────────────────────────
    risk_result = classify(command)

    # ── 2. Policy evaluation ───────────────────────────────────────────────
    engine = get_engine()
    verdict = engine.evaluate(risk_result)

    # ── 3. Audit ───────────────────────────────────────────────────────────
    if verdict.is_blocked:
        log_policy_blocked(command, risk_result.to_dict(), verdict.to_dict())
    else:
        log_command_evaluated(command, risk_result.to_dict(), verdict.to_dict())

    # ── 4. Decision ────────────────────────────────────────────────────────

    # Unconditional block (policy says block / gate not satisfied)
    if verdict.action == PolicyAction.BLOCK:
        _stderr(
            f"{BOLD_RED}[PilotSec] BLOCKED {NC}"
            f"{_format_risk_label(risk_result.level)} {command[:80]}"
        )
        deny_reason = (
            f"Command blocked by security policy.\n"
            f"Risk: {risk_result.level.label()} — {risk_result.reason}\n"
            f"Policy: {verdict.block_reason}"
        )
        print(pre_tool_use_deny(deny_reason))
        return 2

    # Gate-required block (need approval env var)
    if verdict.action == PolicyAction.REQUIRE:
        _stderr(
            f"{RED}[PilotSec] GATE REQUIRED {NC}"
            f"{_format_risk_label(risk_result.level)} {command[:80]}"
        )
        deny_reason = (
            f"Command requires explicit approval before execution.\n"
            f"Risk: {risk_result.level.label()} — {risk_result.reason}\n"
            f"Gate: {verdict.block_reason}\n"
            f"How to approve: {verdict.gate_description}"
        )
        print(pre_tool_use_deny(deny_reason))
        return 2

    # CRITICAL without a blocking policy — still block (defence in depth)
    if risk_result.level == RiskLevel.CRITICAL and verdict.action != PolicyAction.ALLOW:
        _stderr(
            f"{BOLD_RED}[PilotSec] CRITICAL RISK — blocked {NC}{command[:80]}"
        )
        deny_reason = (
            f"Command has CRITICAL risk level and was blocked by defence-in-depth policy.\n"
            f"Reason: {risk_result.reason}\n"
            f"If this is intentional, verify the command manually in a terminal."
        )
        print(pre_tool_use_deny(deny_reason))
        return 2

    # HIGH risk — warn in context, allow execution
    if risk_result.level == RiskLevel.HIGH:
        _stderr(
            f"{RED}[PilotSec] HIGH RISK {NC}{command[:80]}"
        )
        warnings = verdict.warnings or [risk_result.reason]
        context_lines = [
            f"[PilotSec] HIGH risk command: {risk_result.reason}",
        ]
        if warnings:
            context_lines.extend(f"  Policy warning: {w}" for w in warnings)
        context_lines.append(
            "Proceed with caution. Verify intent before approving execution."
        )
        print(pre_tool_use_context("\n".join(context_lines)))
        return 0

    # MEDIUM — inject passive context (supply chain, env vars, etc.)
    if risk_result.level == RiskLevel.MEDIUM:
        _stderr(f"{YELLOW}[PilotSec] MEDIUM {NC}{command[:60]}")
        if verdict.warnings:
            context = "[PilotSec] " + "; ".join(verdict.warnings)
            print(pre_tool_use_context(context))
        return 0

    # LOW / INFO — silent pass
    return 0


if __name__ == "__main__":
    sys.exit(run())
