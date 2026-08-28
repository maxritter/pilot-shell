"""PreCompact hook - capture Pilot state before compaction.

Fires before Claude Code compaction to preserve Pilot-specific session state
(active plan, task list, context) to Pilot Memory for post-compaction restoration.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _lib.console_settings import get_console_url
from _lib.util import (
    claude_config_dir,
    get_session_plan_path,
    plan_in_current_project,
    read_hook_stdin,
    resolve_payload_session_id,
    resolve_session_id,
)


def _sessions_base() -> Path:
    """Get base sessions directory."""
    return Path.home() / ".pilot" / "sessions"


def _capture_active_plan(session_id: str | None = None) -> dict | None:
    """Capture active plan state from session data.

    Cross-session bleed guard: skips a plan that belongs to ANOTHER project,
    which can leak through the shared "default" active_plan.json when no native,
    wrapper, or payload session id resolves. Without this, compaction poisons
    this session's pre-compact-state.json with a foreign repo's /spec plan, which
    post_compact_restore would then surface. Fails open for relative or
    unresolvable paths so the legacy capture is never weakened.

    ``session_id`` is the caller-resolved id (env chain first, hook payload
    fallback): the same-repo half of that bleed, which the project guard above
    cannot catch, is closed by never reading the shared "default" bucket when
    this session's own id is known.
    """
    plan_path = get_session_plan_path(session_id)
    if not plan_path.exists():
        return None

    try:
        plan_data = json.loads(plan_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    raw_path = plan_data.get("plan_path")
    if isinstance(raw_path, str) and raw_path:
        p = Path(raw_path)
        if not p.is_absolute():
            project_root = os.environ.get("CLAUDE_PROJECT_ROOT", str(Path.cwd()))
            p = Path(project_root) / p
        if not plan_in_current_project(p):
            return None

    return {
        "plan_path": plan_data.get("plan_path"),
        "status": plan_data.get("status"),
        "current_task": plan_data.get("current_task"),
    }


def _capture_task_list() -> dict | None:
    """Capture task list state from Claude Code task directory."""
    try:
        pid = os.environ.get("PILOT_SESSION_ID", "")
        if not pid:
            return None
        claude_config = claude_config_dir()
        if claude_config is None:
            return None
        tasks_dir = claude_config / "tasks" / f"pilot-{pid}"
        if not tasks_dir.exists():
            return None

        task_files = list(tasks_dir.glob("*.json"))
        if not task_files:
            return None

        return {
            "task_count": len(task_files),
            "tasks_dir": str(tasks_dir),
        }
    except Exception as e:
        print(f"Warning: task list capture failed: {e}", file=sys.stderr)
        return None


def _save_to_worker_api(state: dict, session_id: str) -> bool:
    """Save state to worker HTTP API.

    Returns True if successful, False otherwise.
    """
    try:
        text_parts = ["Pre-compaction state capture"]

        if state.get("trigger"):
            text_parts.append(f"Trigger: {state['trigger']}")

        if state.get("custom_instructions"):
            text_parts.append(f"Custom instructions: {state['custom_instructions']}")

        if state.get("active_plan"):
            plan = state["active_plan"]
            text_parts.append(
                f"Active plan: {plan.get('plan_path')} (Status: {plan.get('status')}, Task: {plan.get('current_task')})"
            )

        if state.get("task_list"):
            task_list = state["task_list"]
            text_parts.append(f"Task list: {task_list.get('task_count')} tasks active")

        text = "\n".join(text_parts)

        project_name = Path.cwd().name

        payload = {
            "text": text,
            "title": f"Pre-compaction state [session:{session_id}]",
            "project": project_name,
        }

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{get_console_url()}/api/memory/save",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status == 200
    except Exception as e:
        print(f"Warning: worker API save failed: {e}", file=sys.stderr)
        return False


def _save_fallback_file(state: dict, session_id: str) -> None:
    """Save state to local fallback file."""
    session_dir = _sessions_base() / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    fallback_file = session_dir / "pre-compact-state.json"
    fallback_file.write_text(json.dumps(state, indent=2))


def run_pre_compact() -> int:
    """Run PreCompact hook to capture state before compaction.

    Returns exit code: 0. stderr messages visible in verbose mode only.
    """
    hook_data = read_hook_stdin()
    session_id = resolve_payload_session_id(hook_data.get("session_id"))
    trigger = hook_data.get("trigger", "auto")
    custom_instructions = hook_data.get("custom_instructions", "")

    state = {
        "trigger": trigger,
        "custom_instructions": custom_instructions,
        # active_plan.json is written by `pilot register-plan` under the ENV-chain
        # id, so resolve env-first with the payload as last resort (unlike the
        # pre-compact-state key above, which stays payload-first to match its
        # post_compact_restore reader).
        "active_plan": _capture_active_plan(resolve_session_id(hook_data.get("session_id"))),
        "task_list": _capture_task_list(),
    }

    saved_to_api = _save_to_worker_api(state, session_id)
    if not saved_to_api:
        _save_fallback_file(state, session_id)

    if saved_to_api:
        print("🔄 Compaction in progress — Pilot state captured to memory", file=sys.stderr)
    else:
        print("🔄 Compaction in progress — Pilot state captured to local file (worker unavailable)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(run_pre_compact())
