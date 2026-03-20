"""PostToolUse hook — triggers dependency vulnerability scan after package installs.

Watches for Bash commands that install packages:
  npm install / npm add / yarn add / pnpm add / bun add
  pip install / pip3 install / uv add / uv pip install

When detected, runs the appropriate dependency scanner (npm audit / pip-audit)
in async-friendly fashion — prints results as additionalContext so Claude is
aware of newly introduced vulnerabilities immediately.

This hook should be registered as async=true so it doesn't block execution.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from security.scanners.orchestrator import FindingSeverity, ScanCategory, get_orchestrator
from security.intel.correlation import correlate
from security.audit.logger import log_scan_result
from _lib.util import find_git_root, post_tool_use_context

YELLOW = "\033[0;33m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
NC = "\033[0m"

# Commands that signal a package install
_INSTALL_TRIGGERS = {
    # Node
    "npm install", "npm i ", "npm add", "npm ci",
    "yarn add", "yarn install",
    "pnpm add", "pnpm install",
    "bun add", "bun install",
    # Python
    "pip install", "pip3 install",
    "uv add", "uv pip install",
    # Go
    "go get",
    # Rust
    "cargo add",
}

_NODE_MANAGERS = {"npm", "yarn", "pnpm", "bun"}
_PYTHON_MANAGERS = {"pip", "pip3", "uv"}


def _is_install_command(command: str) -> tuple[bool, str]:
    """Return (is_install, package_manager)."""
    cmd_lower = command.lower().strip()
    for trigger in _INSTALL_TRIGGERS:
        if trigger in cmd_lower:
            first_word = cmd_lower.split()[0] if cmd_lower.split() else ""
            if first_word in _NODE_MANAGERS:
                return True, first_word
            if first_word in _PYTHON_MANAGERS:
                return True, first_word
            if first_word == "uv":
                return True, "pip"  # pip-audit works on uv envs
            if first_word in ("go",):
                return True, "go"
            if first_word in ("cargo",):
                return True, "cargo"
            return True, "unknown"
    return False, ""


def run() -> int:
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = hook_data.get("tool_name", "")
    if tool_name != "Bash":
        return 0

    command = hook_data.get("tool_input", {}).get("command", "").strip()
    is_install, pkg_manager = _is_install_command(command)
    if not is_install:
        return 0

    # Use git root as scan target, fall back to cwd
    repo_root = find_git_root()
    target = str(repo_root) if repo_root else os.getcwd()

    sys.stderr.write(
        f"{YELLOW}[PilotSec] Dependency install detected — scanning for vulnerabilities…{NC}\n"
    )

    orchestrator = get_orchestrator()
    result = orchestrator.scan_on_install(target, pkg_manager)

    if not result.success:
        # Scanner not available — skip silently
        return 0

    # Log to audit trail
    log_scan_result(
        scan_type="deps",
        target=target,
        findings=[f.to_dict() for f in result.findings],
        tool=result.tool,
    )

    # Correlate findings to surface compound risks and delta
    report = correlate(result.findings, snapshot_label=f"deps-{pkg_manager}")

    if not result.findings:
        sys.stderr.write(f"{GREEN}[PilotSec] No vulnerabilities found in dependencies.{NC}\n")
        return 0

    # Build context for Claude
    high_crit = [
        f for f in result.findings
        if f.severity in (FindingSeverity.CRITICAL, FindingSeverity.HIGH)
    ]
    lines = [
        f"[PilotSec] Dependency scan complete ({result.tool}): {report.summary}",
    ]

    if high_crit:
        lines.append(f"\n{len(high_crit)} HIGH/CRITICAL vulnerabilities require attention:")
        for f in high_crit[:10]:
            fix = f" → fix: {f.fix_version}" if f.fix_available else " (no fix available)"
            lines.append(f"  • {f.identifier} in {f.target}{fix}")
        if len(high_crit) > 10:
            lines.append(f"  … and {len(high_crit) - 10} more")

    if report.new_since_last:
        lines.append(f"\n{len(report.new_since_last)} new vulnerabilities introduced by this install.")

    for risk in report.compound_risks[:2]:
        lines.append(f"\nCompound risk: {risk.title}\n  → {risk.recommendation}")

    print(post_tool_use_context("\n".join(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
