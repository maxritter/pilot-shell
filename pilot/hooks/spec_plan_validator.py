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
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

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

_HEADER_LINE = re.compile(r"^(?P<key>[A-Z][A-Za-z]*): ?(?P<value>.*)$")
_SECTION_HEADING = re.compile(r"^## (?P<heading>.+)$")


def _pilot_executable() -> str | None:
    """Find the installed Pilot CLI without importing across package boundaries."""
    installed = Path.home() / ".pilot" / "bin" / "pilot"
    if installed.is_file() and os.access(installed, os.X_OK):
        return str(installed)
    return shutil.which("pilot")


def _canonical_validation_errors(plan_file: Path) -> list[str] | None:
    """Return canonical non-strict errors, or None when the CLI is unavailable."""
    executable = _pilot_executable()
    if executable is None:
        return None
    try:
        result = subprocess.run(
            [executable, "spec", "validate", str(plan_file), "--json"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
        payload = json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None

    findings = payload.get("errors") if isinstance(payload, dict) else None
    if not isinstance(findings, list):
        return None
    errors: list[str] = []
    for finding in findings:
        if isinstance(finding, dict) and isinstance(finding.get("message"), str):
            errors.append(finding["message"])
    return errors


def _load_plan_format() -> dict[str, Any] | None:
    """Load the canonical contract for the hook-local validation fallback."""
    candidates = (
        Path(__file__).resolve().parent.parent / "spec" / "plan-format.json",
        Path.home() / ".pilot" / "spec" / "plan-format.json",
    )
    for candidate in candidates:
        try:
            data = json.loads(candidate.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            return data
    return None


def _parse_header(lines: list[str]) -> dict[str, tuple[str, int]]:
    """Parse the header block before the first level-two section."""
    header: dict[str, tuple[str, int]] = {}
    for line_number, line in enumerate(lines, start=1):
        if _SECTION_HEADING.match(line):
            break
        if match := _HEADER_LINE.match(line.rstrip("\r")):
            header.setdefault(match.group("key"), (match.group("value").strip(), line_number))
    return header


def _header_renderability_errors(
    raw: bytes,
    header: dict[str, tuple[str, int]],
    fmt: dict[str, Any],
) -> tuple[str, list[str]]:
    """Return the plan type and renderer-critical header errors."""
    errors = ["The file uses CRLF line endings; plans must use LF so task cards render."] if b"\r\n" in raw else []
    plan_type = header.get("Type", ("Feature", 0))[0] or "Feature"
    for name, rule in fmt.get("header_fields", {}).items():
        if not isinstance(rule, dict):
            continue
        applies_to = rule.get("types")
        if isinstance(applies_to, list) and plan_type not in applies_to:
            continue
        if name not in header:
            if rule.get("required"):
                errors.append(f"Missing required header field `{name}:`.")
            continue
        value, _line = header[name]
        allowed = rule.get("allowed")
        if isinstance(allowed, list) and allowed and value not in allowed:
            errors.append(f"`{name}: {value}` is not allowed.")
        if rule.get("numeric") and not value.isdigit():
            errors.append(f"`{name}: {value}` must be a number.")
    return plan_type, errors


def _local_renderability_errors(plan_file: Path) -> list[str]:
    """Check renderer-critical rules when the installed CLI cannot be invoked."""
    try:
        raw = plan_file.read_bytes()
    except OSError as exc:
        return [f"Cannot read {plan_file}: {exc}"]

    fmt = _load_plan_format()
    if fmt is None:
        return ["Pilot's plan-format contract is unavailable; the artifact cannot be validated safely."]

    lines = raw.decode("utf-8", errors="replace").split("\n")
    header = _parse_header(lines)
    if len(header) < 2:
        return ["The file has no renderable plan header (`Created:`, `Status:`, and `Type:` fields)."]

    plan_type, errors = _header_renderability_errors(raw, header, fmt)

    spans: list[tuple[str, int, int]] = []
    starts = [
        (match.group("heading"), index)
        for index, line in enumerate(lines)
        if (match := _SECTION_HEADING.match(line.rstrip("\r")))
    ]
    for position, (heading, start) in enumerate(starts):
        end = starts[position + 1][1] if position + 1 < len(starts) else len(lines)
        spans.append((heading, start + 1, end))

    known = (
        set(fmt.get("sections_ordered", [])) | set(fmt.get("sections_hidden", [])) | set(fmt.get("tasks_headings", []))
    )
    for heading, _start, _end in spans:
        if heading not in known and heading.strip() in known:
            errors.append(f"`## {heading}` has surrounding whitespace and loses its special rendering.")

    task_pattern = re.compile(str(fmt.get("task_heading_pattern", r"(?!)")))
    task_headings = set(fmt.get("tasks_headings", []))
    tasks: list[tuple[int, int, int]] = []
    task_section_end = len(lines)
    for heading, start, end in spans:
        if heading not in task_headings:
            continue
        task_section_end = end
        for index in range(start, end):
            if match := task_pattern.match(lines[index]):
                tasks.append((int(match.group("number")), index + 1, end))

    for expected, (number, _line, _end) in enumerate(tasks, start=1):
        if number != expected:
            errors.append(f"Task headings must be numbered 1..n in order; expected {expected}, found {number}.")

    required_labels = fmt.get("task_field_labels", {}).get(plan_type, [])
    for position, (number, heading_line, _end) in enumerate(tasks):
        body_start = heading_line
        body_end = tasks[position + 1][1] - 1 if position + 1 < len(tasks) else task_section_end
        body = "\n".join(lines[body_start:body_end])
        missing = [label for label in required_labels if label not in body]
        if missing:
            errors.append(f"Task {number} is missing renderer labels: {', '.join(missing)}.")

    progress_pattern = re.compile(str(fmt.get("progress_line_patterns", {}).get("task", r"(?!)")))
    listed: set[int] = set()
    for heading, start, end in spans:
        if heading not in set(fmt.get("sections_hidden", [])):
            continue
        for index in range(start, end):
            if match := progress_pattern.match(lines[index]):
                listed.add(int(match.group("number")))
    headed = {number for number, _line, _end in tasks}
    if (listed or headed) and listed != headed:
        errors.append("`## Progress Tracking` disagrees with the task headings.")
    return errors


def _validation_errors(plan_file: Path) -> list[str]:
    """Validate with the canonical CLI, falling back to hook-local parity checks."""
    canonical = _canonical_validation_errors(plan_file)
    return canonical if canonical is not None else _local_renderability_errors(plan_file)


def _validation_block(artifact: str, plan_file: Path, errors: list[str]) -> str:
    """Render a concise stop reason for an unrenderable artifact."""
    summary = "; ".join(errors[:3])
    if len(errors) > 3:
        summary += f"; and {len(errors) - 3} more error(s)"
    return stop_block(
        f"{artifact} exists but is not renderable yet: {summary} "
        f"Run `pilot spec validate {plan_file} --json` and fix its errors before stopping."
    )


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
    session_id = resolve_session_id(input_data.get("session_id"))

    # Primary: this session registered a file under doc_dir. Strictly stronger than
    # the glob - it cannot be satisfied by another session's work, and it holds for
    # a plan whose filename the today-glob would never match.
    registered = _own_registered_plan(session_id, plans_dir)
    if registered is not None:
        errors = _validation_errors(registered)
        if errors:
            print(_validation_block(artifact, registered, errors))
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

    invalid: list[tuple[Path, list[str]]] = []
    for candidate in unowned:
        errors = _validation_errors(candidate)
        if not errors:
            return 0
        invalid.append((candidate, errors))

    candidate, errors = invalid[0]
    print(_validation_block(artifact, candidate, errors))

    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
