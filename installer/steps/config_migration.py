"""One-time migrations for ~/.pilot/config.json (model preferences).

Uses a _configVersion field to track which migrations have been applied.
Each migration runs exactly once, even across repeated installer runs.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CURRENT_CONFIG_VERSION = 12

_STALE_AGENT_KEYS = frozenset(
    {
        "plan-challenger",
        "plan-verifier",
        "spec-reviewer-compliance",
        "spec-reviewer-quality",
        "spec-reviewer-goal",
    }
)


def migrate_model_config(
    config_path: Path | None = None,
    *,
    create_if_missing: bool = False,
) -> bool:
    """Run pending one-time migrations on ~/.pilot/config.json.

    Returns True if any migration was applied, False otherwise.
    Safe to call repeatedly — already-applied migrations are skipped.

    `create_if_missing=True` (used by the installer at install time) treats
    a missing config as an empty one and runs all migrations against it so
    subscription-aware defaults (notably v9's Max-vs-non-Max spec-implement
    / spec-verify defaulting) get written. The install path passes True;
    tests default to False so they don't trigger subprocess calls + write
    the user's real ~/.pilot/config.json.
    """
    if config_path is None:
        config_path = Path.home() / ".pilot" / "config.json"

    raw: dict[str, Any]
    if not config_path.exists():
        if not create_if_missing:
            return False
        raw = {}
    else:
        try:
            raw = json.loads(config_path.read_text())
        except (OSError, json.JSONDecodeError):
            return False

    version = raw.get("_configVersion", 0)
    if not isinstance(version, int):
        version = 0

    if version >= CURRENT_CONFIG_VERSION:
        return False

    # v12 safety: before applying any migration that prunes user-visible model
    # keys, snapshot the pre-migration JSON to `<config>.bak.v11` exactly once
    # (the file holds the genuine v11 state for the entire machine lifetime,
    # never overwritten on subsequent runs).
    if version < 12 and config_path.exists():
        bak_path = config_path.with_suffix(".json.bak.v11")
        if not bak_path.exists():
            try:
                _write_atomic(bak_path, raw)
            except OSError:
                # Backup is best-effort — never fail the migration on disk errors.
                pass

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

    if version < 7:
        modified = _migration_v7(raw) or modified

    if version < 8:
        modified = _migration_v8(raw) or modified

    if version < 9:
        modified = _migration_v9(raw) or modified

    if version < 10:
        modified = _migration_v10(raw) or modified

    if version < 11:
        modified = _migration_v11(raw) or modified

    if version < 12:
        modified = _migration_v12(raw) or modified

    if raw.get("_configVersion") != CURRENT_CONFIG_VERSION:
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
    """v3 → v4: Enable reviewer subagents by default. Ensure specWorkflow exists.

    Originally also force-enabled worktreeSupport, but that overwrote explicit
    user preferences (if a user disabled worktree via Console Settings and their
    _configVersion was < 4, this migration would re-enable it). Worktree is now
    left at whatever value the user set — only the specWorkflow dict structure
    is ensured to exist.
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

    # Ensure specWorkflow dict exists, but do NOT override worktreeSupport —
    # the user may have explicitly disabled it via Console Settings.
    spec_workflow = raw.get("specWorkflow")
    if not isinstance(spec_workflow, dict):
        raw["specWorkflow"] = {
            "worktreeSupport": False,
            "askQuestionsDuringPlanning": True,
            "planApproval": True,
        }
        modified = True

    return modified


def _migration_v5(raw: dict[str, Any]) -> bool:
    """v4 → v5: Enable extended context (1M) by default.

    1M context is now GA for Opus 4.7 and Sonnet 4.6. Set extendedContext
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

    if sub_type is None:
        return False

    if sub_type == "max":
        return False

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


def _migration_v7(raw: dict[str, Any]) -> bool:
    """v6 → v7: Rename reviewer agents and add Codex reviewer config.

    - reviewerAgents: planReviewer → specReview, specReviewer → changesReview
    - agents: plan-reviewer → spec-review, spec-reviewer → changes-review
    - Add codexReviewers section with defaults (both disabled)
    """
    modified = False

    reviewer_agents = raw.get("reviewerAgents")
    if isinstance(reviewer_agents, dict):
        if "planReviewer" in reviewer_agents:
            reviewer_agents["specReview"] = reviewer_agents.pop("planReviewer")
            modified = True
        if "specReviewer" in reviewer_agents:
            reviewer_agents["changesReview"] = reviewer_agents.pop("specReviewer")
            modified = True

    agents = raw.get("agents")
    if isinstance(agents, dict):
        if "plan-reviewer" in agents:
            agents["spec-review"] = agents.pop("plan-reviewer")
            modified = True
        if "spec-reviewer" in agents:
            agents["changes-review"] = agents.pop("spec-reviewer")
            modified = True

    if "codexReviewers" not in raw:
        raw["codexReviewers"] = {"specReview": False, "changesReview": False}
        modified = True

    return modified


def _migration_v8(raw: dict[str, Any]) -> bool:
    """v7 → v8: Rename "commands" → "skills" and default all skill models to opus.

    - Renames the config key from "commands" to "skills" for consistency
      with the new skill-based architecture.
    - Sets all skill models to opus (previously spec, spec-implement, and
      spec-verify defaulted to sonnet). Users who explicitly changed a model
      to sonnet keep their choice — only the old defaults are migrated.
    - Ensures extendedContext is true for 1M context.
    """
    modified = False

    if "commands" in raw and "skills" not in raw:
        raw["skills"] = raw.pop("commands")
        modified = True

    skills = raw.get("skills")
    if isinstance(skills, dict):
        for skill_name in ("spec", "spec-implement", "spec-verify"):
            if skills.get(skill_name) == "sonnet":
                skills[skill_name] = "opus"
                modified = True

    if raw.get("extendedContext") is not True:
        raw["extendedContext"] = True
        modified = True

    return modified


def _migration_v9(raw: dict[str, Any]) -> bool:
    """v8 → v9: Set spec-implement and spec-verify to sonnet for non-Max users.

    Sonnet 1M is not included in the Max plan, so Max users need Opus for
    1M context. All other tiers (Pro, Team, Enterprise, API) get Sonnet 1M
    included, so sonnet is the better default (cheaper).

    If subscription type can't be detected, leave settings unchanged (safe
    opus fallback). This migration runs once — after it, users control
    their own settings via Console Settings.
    """
    sub_type = _get_subscription_type()

    if sub_type is None:
        return False

    if sub_type == "max":
        return False

    modified = False

    skills = raw.get("skills")
    if not isinstance(skills, dict):
        skills = {}
        raw["skills"] = skills
        modified = True

    for skill_name in ("spec-implement", "spec-verify"):
        current = skills.get(skill_name)
        if current in ("opus", None):
            skills[skill_name] = "sonnet"
            modified = True

    return modified


_ALIAS_NAMES = ("opus", "sonnet")


def _migration_v10(raw: dict[str, Any]) -> bool:
    """v9 → v10: Strip alias [1m] suffix from `model` and `skills.<key>`.

    Issue #139: per-phase 1M context routes alias 1M through the
    `extendedContextOverrides` map, not the model literal. Legacy configs may
    contain `model: "opus[1m]"` or `skills.<key>: "sonnet[1m]"` from earlier
    versions. Normalize them to plain aliases. Explicit-ID `[1m]`
    (e.g. `claude-opus-4-7[1m]`) is preserved verbatim — Custom users encode
    their context window in the ID itself. Agents are not touched (no
    historical [1m] usage; out of scope for this issue).
    """

    def strip_alias_1m(value: Any) -> tuple[Any, bool]:
        if not isinstance(value, str) or not value.endswith("[1m]"):
            return value, False
        base = value[:-4]
        if base in _ALIAS_NAMES:
            return base, True
        return value, False

    modified = False

    if "model" in raw:
        new_val, changed = strip_alias_1m(raw["model"])
        if changed:
            raw["model"] = new_val
            modified = True

    skills = raw.get("skills")
    if isinstance(skills, dict):
        for k in list(skills.keys()):
            new_val, changed = strip_alias_1m(skills[k])
            if changed:
                skills[k] = new_val
                modified = True

    return modified


def _migration_v11(raw: dict[str, Any]) -> bool:
    """v10 → v11: Rename specWorkflow.worktreeSupport → branchIsolation.

    The toggle's semantics expanded: it now gates BOTH new-branch creation
    and worktree creation. Existing users keep their on/off preference;
    the legacy key is removed so config.json reflects the new name.

    Both-keys-present case: if branchIsolation is already set, the user's
    most-recent explicit write wins — keep it, just clean up worktreeSupport.
    """
    spec_workflow = raw.get("specWorkflow")
    if not isinstance(spec_workflow, dict):
        return False
    if "worktreeSupport" not in spec_workflow:
        return False
    old_value = spec_workflow.pop("worktreeSupport")
    if "branchIsolation" in spec_workflow:
        return True
    spec_workflow["branchIsolation"] = bool(old_value) if isinstance(old_value, bool) else False
    return True


def _migration_v12(raw: dict[str, Any]) -> bool:
    """v11 → v12: Strip dead model keys; seed specWorkflow.modelSwitch=true.

    After this migration, model selection is controlled entirely via Claude
    Code's `/model` slash command — `~/.pilot/config.json` no longer stores
    main / per-skill / per-agent model preferences, the 1M extended-context
    toggle, or per-row overrides. The launcher's settings injector stops
    rewriting `model:` lines in skill / agent frontmatter; the source files
    are authoritative.

    `specWorkflow.modelSwitch` is the new opt-out toggle: when true (default)
    the spec-plan skill ends its turn with a handoff message after approval
    so the user can `/clear` + `/model <…>` before implementation; when false
    the spec workflow continues plan → implement → verify in one session on
    whichever model is active.

    The caller writes `~/.pilot/config.json.bak.v11` (single-file safety
    copy, written exactly once per machine) before this migration runs, so
    advanced users can recover their pre-v12 preferences if needed.
    """
    modified = False

    for dead_key in ("model", "skills", "agents", "extendedContext", "extendedContextOverrides"):
        if dead_key in raw:
            del raw[dead_key]
            modified = True

    spec_workflow = raw.get("specWorkflow")
    if not isinstance(spec_workflow, dict):
        spec_workflow = {}
        raw["specWorkflow"] = spec_workflow
        modified = True
    if "modelSwitch" not in spec_workflow:
        spec_workflow["modelSwitch"] = True
        modified = True

    return modified


def _write_atomic(path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically using temp file + os.rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data, indent=2))
    os.replace(tmp_path, path)
