"""One-time migrations for ~/.pilot/config.json (model preferences).

Uses a _configVersion field to track which migrations have been applied.
Each migration runs exactly once, even across repeated installer runs.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CURRENT_CONFIG_VERSION = 6

# Old agent names removed in v7.1 (merged into plan-reviewer + spec-reviewer)
_STALE_AGENT_KEYS = frozenset(
    {
        "plan-challenger",
        "plan-verifier",
        "spec-reviewer-compliance",
        "spec-reviewer-quality",
        "spec-reviewer-goal",
    }
)


def migrate_model_config(config_path: Path | None = None) -> bool:
    """Run pending one-time migrations on ~/.pilot/config.json.

    Returns True if any migration was applied, False otherwise.
    Safe to call repeatedly — already-applied migrations are skipped.
    """
    if config_path is None:
        config_path = Path.home() / ".pilot" / "config.json"

    if not config_path.exists():
        return False

    try:
        raw: dict[str, Any] = json.loads(config_path.read_text())
    except (OSError, json.JSONDecodeError):
        return False

    version = raw.get("_configVersion", 0)
    if not isinstance(version, int):
        version = 0

    if version >= CURRENT_CONFIG_VERSION:
        return False

    modified = False

    if version < 1:
        modified = _migration_v1(raw) or modified

    if version < 2:
        modified = _migration_v2(raw) or modified

    if version < 3:
        modified = _migration_v3(raw) or modified

    if version < 4:
        modified = _migration_v4(raw) or modified

    if version < 5:
        modified = _migration_v5(raw) or modified

    if version < 6:
        modified = _migration_v6(raw) or modified

    raw["_configVersion"] = CURRENT_CONFIG_VERSION
    modified = True

    if modified:
        _write_atomic(config_path, raw)

    return modified


def _migration_v1(raw: dict[str, Any]) -> bool:
    """v0 → v1: Update model routing defaults from v7.0 to v7.1.

    - spec-verify: opus → sonnet (new recommended default)
    - Remove stale agent keys (plan-challenger, plan-verifier, etc.)
    - Ensure new agent keys exist (plan-reviewer, spec-reviewer)
    """
    modified = False

    commands = raw.get("commands")
    if isinstance(commands, dict):
        if commands.get("spec-verify") == "opus":
            commands["spec-verify"] = "sonnet"
            modified = True

    agents = raw.get("agents")
    if isinstance(agents, dict):
        for stale_key in _STALE_AGENT_KEYS:
            if stale_key in agents:
                del agents[stale_key]
                modified = True

        if "plan-reviewer" not in agents:
            agents["plan-reviewer"] = "sonnet"
            modified = True
        if "spec-reviewer" not in agents:
            agents["spec-reviewer"] = "sonnet"
            modified = True

    return modified


def _migration_v2(raw: dict[str, Any]) -> bool:
    """v1 → v2: Switch sync and learn commands from sonnet to opus.

    Both build rules/skills and only run periodically — best model, not a cost driver.
    """
    modified = False

    commands = raw.get("commands")
    if isinstance(commands, dict):
        if commands.get("sync") == "sonnet":
            commands["sync"] = "opus"
            modified = True
        if commands.get("learn") == "sonnet":
            commands["learn"] = "opus"
            modified = True

    return modified


def _migration_v3(raw: dict[str, Any]) -> bool:
    """v2 → v3: Disable plan review, spec review, and worktree support by default.

    These features consume significant tokens (~50k for plan review, ~100k for
    spec review) as they run in separate context windows. Disable them for all
    existing users — they can re-enable via Console Settings if desired.
    """
    modified = False

    reviewer_agents = raw.get("reviewerAgents")
    if isinstance(reviewer_agents, dict):
        if reviewer_agents.get("planReviewer") is True:
            reviewer_agents["planReviewer"] = False
            modified = True
        if reviewer_agents.get("specReviewer") is True:
            reviewer_agents["specReviewer"] = False
            modified = True
        for key in ("planReviewer", "specReviewer"):
            if key not in reviewer_agents:
                reviewer_agents[key] = False
                modified = True
    else:
        raw["reviewerAgents"] = {"planReviewer": False, "specReviewer": False}
        modified = True

    spec_workflow = raw.get("specWorkflow")
    if isinstance(spec_workflow, dict):
        if spec_workflow.get("worktreeSupport") is True:
            spec_workflow["worktreeSupport"] = False
            modified = True
    else:
        raw["specWorkflow"] = {
            "worktreeSupport": False,
            "askQuestionsDuringPlanning": True,
            "planApproval": True,
        }
        modified = True

    return modified


def _migration_v4(raw: dict[str, Any]) -> bool:
    """v3 → v4: Enable worktree support and reviewer subagents by default.

    Re-enables the features disabled in v3 now that token costs are acceptable.
    """
    modified = False

    reviewer_agents = raw.get("reviewerAgents")
    if isinstance(reviewer_agents, dict):
        if reviewer_agents.get("planReviewer") is False:
            reviewer_agents["planReviewer"] = True
            modified = True
        if reviewer_agents.get("specReviewer") is False:
            reviewer_agents["specReviewer"] = True
            modified = True
    else:
        raw["reviewerAgents"] = {"planReviewer": True, "specReviewer": True}
        modified = True

    spec_workflow = raw.get("specWorkflow")
    if isinstance(spec_workflow, dict):
        if spec_workflow.get("worktreeSupport") is False:
            spec_workflow["worktreeSupport"] = True
            modified = True
    else:
        raw["specWorkflow"] = {
            "worktreeSupport": True,
            "askQuestionsDuringPlanning": True,
            "planApproval": True,
        }
        modified = True

    return modified


def _migration_v5(raw: dict[str, Any]) -> bool:
    """v4 → v5: Enable extended context (1M) by default.

    1M context is now GA for Opus 4.6 and Sonnet 4.6. Set extendedContext
    to true for all users. Users who don't have 1M access can disable it
    via Console Settings.
    """
    if raw.get("extendedContext") is True:
        return False
    raw["extendedContext"] = True
    return True


def _get_subscription_type() -> str | None:
    """Detect Claude Code subscription type via `claude auth status`.

    Returns the raw subscriptionType string (e.g. "max", "pro", "team", "enterprise")
    or None if detection fails.
    """
    import subprocess

    # Primary: claude auth status (works on all platforms)
    try:
        result = subprocess.run(
            ["claude", "auth", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            sub_type = data.get("subscriptionType", "")
            if sub_type:
                return sub_type.lower()
    except Exception:
        pass

    # Fallback: credentials file (Linux has claudeAiOauth, macOS may not)
    creds_path = Path.home() / ".claude" / ".credentials.json"
    try:
        if creds_path.exists():
            content = json.loads(creds_path.read_text())
            oauth = content.get("claudeAiOauth", {})
            sub_type = oauth.get("subscriptionType", "")
            if sub_type:
                return sub_type.lower()
    except Exception:
        pass

    return None


def _migration_v6(raw: dict[str, Any]) -> bool:
    """v5 → v6: Disable reviewer sub-agents for non-Max users.

    Sub-agents (plan-reviewer, spec-reviewer) consume ~150k extra tokens per
    /spec run. Disable them for Pro, Team, and Enterprise users to reduce
    token usage. Users can re-enable via Console Settings if desired.

    Max users keep sub-agents enabled (they have higher rate limits).
    If subscription type can't be detected, leave settings unchanged.
    """
    sub_type = _get_subscription_type()

    # Can't detect → don't change anything (safe default)
    if sub_type is None:
        return False

    # Max users keep current settings
    if sub_type == "max":
        return False

    # Non-Max: disable both sub-agents
    modified = False

    reviewer_agents = raw.get("reviewerAgents")
    if isinstance(reviewer_agents, dict):
        if reviewer_agents.get("planReviewer") is True:
            reviewer_agents["planReviewer"] = False
            modified = True
        if reviewer_agents.get("specReviewer") is True:
            reviewer_agents["specReviewer"] = False
            modified = True
    else:
        raw["reviewerAgents"] = {"planReviewer": False, "specReviewer": False}
        modified = True

    return modified


def _write_atomic(path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically using temp file + os.rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data, indent=2))
    os.replace(tmp_path, path)
