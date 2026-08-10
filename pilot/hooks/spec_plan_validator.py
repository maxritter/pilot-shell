#!/usr/bin/env python3
"""Stop hook for the planning phases - verifies the run's file was created.

Serves both structured workflows. `/spec`'s planning skills register it with no
argument and it guards `docs/plans/`; `/build` registers it as
`spec_plan_validator.py docs/builds Buildout` so the same guard covers the
window before the Buildout exists - the stop guard proper only engages once a
file has been registered, so without this a run could end with no artifact at
all.
"""

from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib.util import is_waiting_for_user_input, stop_block

DEFAULT_DOC_DIR = "docs/plans"
DEFAULT_ARTIFACT = "Plan"


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

    today = datetime.date.today().strftime("%Y-%m-%d")
    if not plans_dir.exists():
        print(stop_block(f"{artifact} file not created yet. Create it in {doc_dir}/ before stopping."))
        return 0

    today_plans = list(plans_dir.glob(f"{today}-*.md"))
    if not today_plans:
        print(stop_block(f"{artifact} file not created yet. Expected a file matching: {doc_dir}/{today}-*.md"))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
