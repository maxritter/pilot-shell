#!/usr/bin/env python3
"""Stop hook for the planning phases - verifies the run's file was created.

Serves both structured workflows. `/spec`'s planning skills register it with no
argument and it guards `docs/plans/`; `/build` registers it as
`spec_plan_validator.py docs/builds Buildout` so the same guard covers the
window before the Buildout exists - the stop guard proper only engages once a
file has been registered, so without this a run could end with no artifact at
all.

Satisfaction is SESSION-SCOPED. The primary check is this session's own
`active_plan.json`: all three planning skills call `pilot register-plan` inside
their header-creation step, before any exploration and therefore before a stop is
reachable (spec-plan 02-create-header.md:66, spec-bugfix-plan
01-create-header.md:51, build 02-draft-the-run.md:173). A repo-wide
`{today}-*.md` glob remains as a fallback for a run that never registered, but it
now skips any candidate a DIFFERENT session owns - otherwise a sibling session's
plan silently satisfied this session's guard, which is the multi-session
cross-talk the community reported.

KNOWN RESIDUAL: when NEITHER session has registered, nothing attributes a plan
file to a session and the fallback still accepts a sibling's file. Inferring
ownership from mtime would misfire on a plan edited across a session boundary, so
the behaviour is documented instead (`pilot register-plan` is what earns
session-scoped guarding) and pinned by
`TestSessionScoping::test_documented_residual_two_unregistered_sessions_collide`.
"""

from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import (
    get_session_plan_path,
    is_waiting_for_user_input,
    plan_registered_by_other_session,
    resolve_session_id,
    stop_block,
)

DEFAULT_DOC_DIR = "docs/plans"
DEFAULT_ARTIFACT = "Plan"


def _own_registered_plan(session_id: str, plans_dir: Path) -> Path | None:
    """This session's registered plan when it lives under `plans_dir`, else None."""
    plan_json = get_session_plan_path(session_id)
    if not plan_json.exists():
        return None
    try:
        registered = str(json.loads(plan_json.read_text()).get("plan_path", ""))
    except (json.JSONDecodeError, OSError, AttributeError, TypeError):
        return None
    if not registered:
        return None

    plan_file = Path(registered)
    if not plan_file.exists():
        return None
    try:
        root = os.path.realpath(plans_dir)
        if os.path.commonpath([root, os.path.realpath(plan_file)]) != root:
            return None
    except (OSError, ValueError):
        return None
    return plan_file


def main(doc_dir: str = DEFAULT_DOC_DIR, artifact: str = DEFAULT_ARTIFACT) -> int:
    """Check the workflow's file was created before allowing stop.

    `doc_dir` and `artifact` are parameters rather than `sys.argv` reads so the
    hook stays callable from tests, where `sys.argv` carries pytest's own flags.
    """
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if input_data.get("stop_hook_active", False):
        return 0

    transcript_path = input_data.get("transcript_path", "")
    if transcript_path and is_waiting_for_user_input(transcript_path):
        return 0

    project_root = input_data.get("project_root") or os.environ.get("CLAUDE_PROJECT_ROOT") or str(Path.cwd())
    plans_dir = Path(project_root) / doc_dir
    session_id = resolve_session_id(str(input_data.get("session_id") or ""))

    # Primary: this session registered a file under doc_dir. Strictly stronger than
    # the glob - it cannot be satisfied by another session's work, and it holds for
    # a plan whose filename the today-glob would never match.
    if _own_registered_plan(session_id, plans_dir) is not None:
        return 0

    today = datetime.date.today().strftime("%Y-%m-%d")
    if not plans_dir.exists():
        print(stop_block(f"{artifact} file not created yet. Create it in {doc_dir}/ before stopping."))
        return 0

    unowned = [
        candidate
        for candidate in plans_dir.glob(f"{today}-*.md")
        if not plan_registered_by_other_session(candidate, session_id)
    ]
    if not unowned:
        print(stop_block(f"{artifact} file not created yet. Expected a file matching: {doc_dir}/{today}-*.md"))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
