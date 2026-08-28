"""SessionStart(compact) hook - restore Pilot context after compaction.

Fires after Claude Code or Codex compaction completes to re-inject Pilot-specific context
(active plan, task state) that may have been compressed during compaction.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _lib.util import (
    get_session_plan_path,
    plan_in_current_project,
    read_hook_stdin,
    resolve_payload_session_id,
    resolve_session_id,
)


def _sessions_base() -> Path:
    """Get base sessions directory."""
    return Path.home() / ".pilot" / "sessions"


def _read_active_plan(session_id: str | None = None) -> dict | None:
    """Read active plan state from session data.

    ``session_id`` is the caller-resolved id (env chain first, hook payload
    fallback), so an env-less session restores ITS OWN plan and never one a
    sibling same-repo session registered into the shared "default" bucket -
    the case the project-scoping guard below cannot catch.
    """
    plan_path = get_session_plan_path(session_id)
    if not plan_path.exists():
        return None

    try:
        return json.loads(plan_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _plan_belongs_to_project(plan_data: dict | None) -> bool:
    """True when the active plan is absent OR lives in the current project.

    Cross-session bleed guard: suppresses a foreign-project plan that leaked
    through the shared "default" active_plan.json when no session id resolved,
    so compaction doesn't re-anchor the agent onto another repo's /spec plan.
    Fails open for relative or unresolvable paths so the legacy informational
    display is never weakened.
    """
    if not plan_data:
        return True
    plan_path = plan_data.get("plan_path")
    if not isinstance(plan_path, str) or not plan_path:
        return True
    p = Path(plan_path)
    if not p.is_absolute():
        project_root = os.environ.get("CLAUDE_PROJECT_ROOT", str(Path.cwd()))
        p = Path(project_root) / p
    return plan_in_current_project(p)


def _read_fallback_state(session_id: str) -> dict | None:
    """Read pre-compact fallback state if available."""
    fallback_file = _sessions_base() / session_id / "pre-compact-state.json"
    if not fallback_file.exists():
        return None

    try:
        state = json.loads(fallback_file.read_text())
        fallback_file.unlink()
        return state
    except (json.JSONDecodeError, OSError):
        return None


def _format_context_message(plan_data: dict | None, fallback_state: dict | None) -> str:
    """Format structured context restoration message."""
    lines = ["[Pilot Context Restored After Compaction]"]

    if plan_data:
        plan_path = plan_data.get("plan_path", "Unknown")
        status = plan_data.get("status", "Unknown")
        current_task = plan_data.get("current_task")

        if current_task:
            lines.append(f"Active Plan: {plan_path} (Status: {status}, Task {current_task} in progress)")
        else:
            lines.append(f"Active Plan: {plan_path} (Status: {status})")

    elif fallback_state and fallback_state.get("active_plan"):
        plan = fallback_state["active_plan"]
        plan_path = plan.get("plan_path", "Unknown")
        status = plan.get("status", "Unknown")
        lines.append(f"Active Plan: {plan_path} (Status: {status}) [from pre-compact state]")

    else:
        lines.append("No active plan")

    if fallback_state and fallback_state.get("task_list"):
        task_count = fallback_state["task_list"].get("task_count")
        if task_count:
            lines.append(f"Tasks: {task_count} active")

    return "\n".join(lines)


def run_post_compact_restore() -> int:
    """Run SessionStart(compact) hook to restore context after compaction.

    Returns exit code: 0 with a SessionStart JSON payload on stdout.
    """
    hook_data = read_hook_stdin()
    session_id = resolve_payload_session_id(hook_data.get("session_id"))

    # Env-first with payload fallback (unlike the fallback-state key above,
    # which stays payload-first to match pre_compact's writer): active_plan.json
    # was written by `pilot register-plan` under the env-chain id.
    plan_data = _read_active_plan(resolve_session_id(hook_data.get("session_id")))
    if not _plan_belongs_to_project(plan_data):
        plan_data = None

    fallback_state = _read_fallback_state(session_id)
    # Same cross-session bleed guard for the fallback branch: a pre-compact-state
    # captured before the pre_compact guard landed (or from an older Pilot build)
    # may still carry a foreign-project plan. Drop only that key, keeping other
    # fallback fields (e.g. task_list, which is session-scoped).
    if fallback_state and not _plan_belongs_to_project(fallback_state.get("active_plan")):
        fallback_state = {k: v for k, v in fallback_state.items() if k != "active_plan"}

    message = _format_context_message(plan_data, fallback_state)
    platform = os.environ.get("CLAUDE_PROJECT_PLATFORM") or hook_data.get("platform") or ""
    if str(platform).lower() == "codex":
        # Codex hooks consume additionalContext on stderr instead of the
        # Claude Code SessionStart hookSpecificOutput envelope.
        print(message, file=sys.stderr)
    else:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": message,
                    }
                }
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(run_post_compact_restore())
