#!/usr/bin/env python3
"""PostToolUse(ExitPlanMode) hook: file an approved native plan under docs/plans/.

Claude Code's own plan mode parks the plan in a throwaway
`~/.claude/plans/<random-words>.md` that nothing ever reads again: it is outside
the repo, invisible to the Pilot Console, and gone the moment the user forgets
the random name. This hook copies the plan the user just approved into the
project's registered-run directory (`docs/plans/`), in the Pilot plan format, so
it renders in the Console next to `/spec` plans and stays with the repo.

⛔ It captures ONLY plans that no Pilot workflow owns. `pilot_run_in_flight`
reporting a live run means `/spec` or `/build` already maintains its own file -
capturing there would write a duplicate that competes with the real plan in the
Console list. That predicate reads `active_plan.json` (the session slot AND every
orchestration lane's, since a lane's `/spec` owns a plan this session's slot never
names) and deliberately NOT the plan-mode sentinel, because `plan_mode_tracker`
deletes that sentinel on this same PostToolUse event and the two hooks would race
for it. It fails CLOSED: an unreadable registration means "a run may be running",
so an ambiguous state skips the capture rather than filing a competing document.

STATUS IS TERMINAL BY CONSTRUCTION. A captured plan is written `Status: SAVED`,
never PENDING, because nothing will ever advance it: native plan mode has no
implement phase, no verify phase, and no completion signal to hook. Pilot's
active-run surfaces (the Console top bar, `/api/plan`, the Spec view's
auto-selection) only track PENDING/COMPLETE, so a SAVED record can never rot
into a phantom in-flight spec - the exact failure that a "capture it as PENDING
and hope someone closes it" design produces on the first abandoned plan. It is a
record of a decision, and it is filed as one.

Fails silent and open: an unreadable payload, a missing project root, an
undeterminable plan body, or any write error simply skips the capture. A hook
that cannot file a document must never disturb the session that produced it.
"""

from __future__ import annotations

import datetime
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _lib.util import (
    claude_config_dir,
    current_project_root,
    post_tool_use_context,
    read_hook_stdin,
    resolve_session_id,
)

PLANS_DIRNAME = ("docs", "plans")

# Terminal, non-workflow status. Outside the PENDING/COMPLETE lifecycle every
# Pilot active-run surface tracks, so a captured plan is listed and readable but
# never counted as work in flight.
CAPTURED_STATUS = "SAVED"

# `Type:` value the Console renders with its own badge (see specType.ts). A
# captured plan is not a Feature, Bugfix, or Buildout - it is a plan someone
# approved outside a workflow, and mislabelling it as a Feature is how it starts
# looking like a spec that was abandoned.
CAPTURED_TYPE = "Plan"

_MAX_SLUG_LEN = 60

# Same title, same day, this many times over: the suffix search gives up rather
# than spinning. Far beyond any real planning session.
_MAX_CAPTURES_PER_TITLE = 50
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def _slugify(title: str) -> str:
    """Filename-safe slug from a plan title, or "" when nothing usable remains."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:_MAX_SLUG_LEN].rstrip("-")


def _trusted_scratch_dirs() -> tuple[Path, ...]:
    """Claude-owned plan directories the hook may read from."""
    config_dir = claude_config_dir()
    if config_dir is None:
        return ()

    directories = [config_dir / "plans"]
    try:
        settings = json.loads((config_dir / "settings.json").read_text())
        configured = settings.get("plansDirectory") if isinstance(settings, dict) else None
        if isinstance(configured, str) and configured.strip():
            custom = Path(configured).expanduser()
            if not custom.is_absolute():
                project_root = current_project_root()
                if project_root is not None:
                    custom = project_root / custom
                else:
                    custom = config_dir / custom
            directories.append(custom)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        pass

    resolved: list[Path] = []
    for directory in directories:
        try:
            candidate = directory.resolve()
        except OSError:
            continue
        if candidate not in resolved:
            resolved.append(candidate)
    return tuple(resolved)


def _read_scratch_plan(scratch: str) -> str:
    """Read a Claude-owned markdown scratch plan, never an arbitrary path."""
    try:
        candidate = Path(scratch).expanduser().resolve(strict=True)
        if candidate.suffix.lower() != ".md" or not any(
            candidate.is_relative_to(directory) for directory in _trusted_scratch_dirs()
        ):
            return ""
        return candidate.read_text()
    except (OSError, UnicodeDecodeError):
        return ""


def _plan_body(tool_input: dict, tool_response: dict) -> str:
    """The APPROVED plan markdown, preferring the response over the request.

    Three sources, in the order that keeps the captured document honest:

    1. ``tool_response.plan`` - what the tool actually approved. The user can
       edit a plan during the native review, so the response is the only source
       that reflects what they agreed to.
    2. ``tool_input.plan`` - what was proposed. Correct whenever the response
       carries no plan of its own, and the only source on builds that do not
       return one.
    3. ``tool_input.planFilePath`` - the scratch file Claude Code wrote, as a
       last resort when neither field carries the text.
    """
    for source in (tool_response.get("plan"), tool_input.get("plan")):
        if isinstance(source, str) and source.strip():
            return source
    scratch = tool_input.get("planFilePath")
    if isinstance(scratch, str) and scratch:
        return _read_scratch_plan(scratch)
    return ""


def _title_and_body(plan: str) -> tuple[str, str]:
    """Split the leading H1 off the plan; the rest becomes the Summary body.

    The H1 is lifted out because the captured file needs exactly one - the
    Console's parser takes the first `# ` line as the plan title and renders
    every `## ` heading below it as a section, so a second H1 in the body would
    read as stray text in the Summary card.
    """
    match = _H1_RE.search(plan)
    if match is None or plan[: match.start()].strip():
        return "", plan.strip()
    return match.group(1).strip(), plan[match.end() :].strip()


def _write_unique(plans_dir: Path, date: str, slug: str, render: Callable[[], str]) -> Path | None:
    """Write the capture to the first free `<date>-<slug>[-N].md`, or None.

    ⛔ Creation is exclusive (``O_CREAT|O_EXCL``), not check-then-write. Two
    sessions capturing plans with the same title on the same day would both see
    the same name as free and the second ``write_text`` would truncate the
    first. Losing a captured plan to a silent overwrite is the one failure this
    hook must not have, since the scratch copy it came from is throwaway.

    Never clobbers: a revised plan, a second planning session, or a re-run of
    this hook over an existing capture each get their own sibling file, leaving
    a document the user may have hand-edited untouched.
    """
    for counter in range(1, _MAX_CAPTURES_PER_TITLE + 1):
        suffix = "" if counter == 1 else f"-{counter}"
        target = plans_dir / f"{date}-{slug}{suffix}.md"
        try:
            with open(target, "x", encoding="utf-8") as handle:
                handle.write(render())
            return target
        except FileExistsError:
            continue
        except OSError:
            return None
    return None


def _render(title: str, body: str, date: str) -> str:
    """Compose the Pilot-format plan file.

    Every header field the format declares required is emitted, so the Console,
    the statusline, and the plan format's own readers agree on the file.

    The body is wrapped in `## Summary` only when it does not already open with
    a heading of its own. The Console renders one card per `## ` section, so
    wrapping a plan that starts with `## Context` would put an empty Summary
    card above it; a plan that is plain prose needs the wrapper, or its text
    belongs to no section at all.
    """
    sectioned = body.lstrip().startswith("## ")
    content = body if sectioned else f"## Summary\n\n{body}"
    return (
        f"# {title}\n"
        "\n"
        f"Created: {date}\n"
        "Agent: Claude Code\n"
        f"Status: {CAPTURED_STATUS}\n"
        "Approved: Yes\n"
        "Worktree: No\n"
        f"Type: {CAPTURED_TYPE}\n"
        "Iterations: 0\n"
        "\n"
        f"{content}\n"
    )


def _notice(target: Path, root: Path) -> str:
    try:
        shown = target.relative_to(root)
    except ValueError:
        shown = target
    return (
        f"[Pilot] Plan saved to {shown} (Status: {CAPTURED_STATUS} - a record, not a "
        "tracked run: no Pilot workflow will update it, and it stays out of the "
        "Console's active specs). Mention the path once, in one short sentence, the "
        "first time you report back. If the approach changes while you implement it, "
        "edit that file so the record matches what you actually did. Do NOT create a "
        "second plan file, and do NOT change its Status."
    )


_UNROOTED_NOTICE = (
    "[Pilot] Could not file this plan: no project root could be determined "
    "(no CLAUDE_PROJECT_ROOT and not inside a git repository), so there is no "
    "docs/plans/ to write to. Tell the user in one short sentence that the plan "
    "was NOT saved and still exists only in Claude Code's scratch copy."
)


def _write_failed_notice(root: Path) -> str:
    return (
        f"[Pilot] Could not file this plan into {root / Path(*PLANS_DIRNAME)} - the "
        "directory or file could not be written. Tell the user in one short "
        "sentence that the plan was NOT saved, so they can copy it out of "
        "Claude Code's scratch file before it is lost."
    )


def main() -> int:
    data = read_hook_stdin()
    if data.get("tool_name") != "ExitPlanMode":
        return 0

    raw_response = data.get("tool_response")
    response: dict = raw_response if isinstance(raw_response, dict) else {}
    if response.get("is_error"):
        return 0  # a rejected or failed exit approved nothing worth filing

    try:
        from _lib.util import pilot_run_in_flight

        if pilot_run_in_flight(resolve_session_id(str(data.get("session_id") or ""))):
            return 0  # a Pilot workflow owns this plan mode leg and its own file
    except Exception:
        # Cannot tell whether a workflow is running: skip. A missing capture
        # costs a document; a wrong one puts a duplicate plan in the Console
        # list, competing with the run the user is actually watching.
        return 0

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    plan = _plan_body(tool_input, response)
    if not plan.strip():
        return 0

    root = current_project_root()
    if root is None:
        # No authoritative project root, so there is no docs/plans/ this plan
        # provably belongs to. Say so instead of dropping it silently - the
        # scratch copy Claude Code wrote is the user's only remaining copy.
        print(post_tool_use_context(_UNROOTED_NOTICE))
        return 0

    title, body = _title_and_body(plan)
    date = datetime.date.today().isoformat()
    if not title:
        title = "Plan"
    slug = _slugify(title) or f"plan-{datetime.datetime.now().strftime('%H%M%S')}"

    try:
        plans_dir = root.joinpath(*PLANS_DIRNAME)
        plans_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        print(post_tool_use_context(_write_failed_notice(root)))
        return 0

    target = _write_unique(plans_dir, date, slug, lambda: _render(title, body, date))
    if target is None:
        print(post_tool_use_context(_write_failed_notice(root)))
        return 0

    print(post_tool_use_context(_notice(target, root)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
