"""Workflow skills must route temp artifacts through the session-isolated
``$HOME/.pilot/sessions/<id>/`` directory, never bare ``/tmp``.

Claude Code injects a per-session scratchpad mandate ("use the session
scratchpad instead of ``/tmp``") into every session, so a skill that hardcodes
bare ``/tmp`` forces the agent to reconcile two live, authoritative instructions
on every run - wasted reasoning tokens, and a real failure tail when the agent
relocates the file at write time but reconstructs the literal ``/tmp`` path at a
later read/cleanup site. Bare ``/tmp`` is also machine-global: the
``${PILOT_SESSION_ID:-default}`` fallback collapses to a shared filename, so two
concurrent sessions (e.g. parallel worktrees) silently clobber each other's
in-flight artifacts.

The fix routes every temp artifact into ``$HOME/.pilot/sessions/<id>/`` — the
codebase's own session-isolated location, already used by these skills for
findings/flags, and agent-neutral so it works under both Claude Code and Codex
(the ``CODEX-START`` blocks have no Claude scratchpad to fall back to; see
issue #167.
"""

from __future__ import annotations

import re
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[3] / "pilot" / "skills"

# The workflow skills that drive the /fix and /spec temp-artifact flows.
_WORKFLOW_SKILLS = ("fix", "spec-plan", "spec-verify")

# A bare, machine-global /tmp path used as a temp-artifact location.
_BARE_TMP = re.compile(r"/tmp/")

# An incomplete session-id chain: it collapses to the shared "default" dir when
# PILOT_SESSION_ID (IDE/desktop launches) or CLAUDE_CODE_SESSION_ID (Codex) is
# unset, bleeding per-session state (e.g. the codex-once flag) across unrelated
# sessions. The canonical chain must fall through to CODEX_THREAD_ID before
# default, matching launcher/session.py:_SESSION_ID_ENV_CHAIN and
# pilot/hooks/_lib/util.py:resolve_session_id (issue #167 completion).
_INCOMPLETE_SESSION_CHAIN = re.compile(r"\$\{(?:PILOT_SESSION_ID|CLAUDE_CODE_SESSION_ID):-default\}")


def _bare_tmp_offenders() -> list[str]:
    offenders: list[str] = []
    for skill in _WORKFLOW_SKILLS:
        for md in sorted((SKILLS_DIR / skill).rglob("*.md")):
            for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                if _BARE_TMP.search(line):
                    offenders.append(f"{md.relative_to(SKILLS_DIR)}:{lineno}: {line.strip()}")
    return offenders


def test_workflow_skills_do_not_hardcode_bare_tmp() -> None:
    offenders = _bare_tmp_offenders()
    assert not offenders, (
        "Workflow skills must write temp artifacts under "
        "$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}/ "
        "(session-isolated, agent-neutral), never bare /tmp - which contradicts "
        "Claude Code's session-scratchpad mandate and collides across concurrent "
        "sessions (issue #167). Offenders:\n" + "\n".join(offenders)
    )


# A session-directory artifact whose filename carries no per-run component.
#
# `$SESS_DIR` resolves identically for a coordinating session and every subagent
# lane it dispatches (their hook payloads are byte-identical), so a fixed filename
# is shared by every concurrent run by construction. The observed damage: one lane
# read a sibling's changes-review findings as its own - a CLEAN report belonging to
# another diff, read as evidence this one is clean - and one lane's `rm -f` glob
# deleted a sibling's findings mid-write (issue #173).
#
# A run component is `<slug>`, `<lane>`, `<plan-slug>`, `<agent>`, or a shell
# expansion. Matching the ASSIGNMENT form keeps this robust to rewording: prose
# mentioning a filename is not an offence, writing one is.
_FIXED_SESSION_ARTIFACT = re.compile(
    r"""(?x)
    (?:
        \$(?:SESS_DIR|\{SESS_DIR\})     # the $SESS_DIR shorthand
      # ...or the long form. `[^/]*` rather than `[^}]*`: the session-id chain
      # nests braces (${A:-${B:-${C:-default}}}) but never contains a slash.
      | \$HOME/\.pilot/sessions/\$\{[^/]*\}
      | \$HOME/\.pilot/sessions/\$[A-Za-z_]+
    )/
    (?P<name>[A-Za-z0-9._-]+)           # a literal filename, no expansion
    (?=["'`\s)]|$)
    """
)

# Placeholders that make a filename per-run rather than per-session.
_RUN_COMPONENT = re.compile(r"<[^>]+>|\$\{?[A-Za-z_]")

# Session-level signals that are deliberately ONE per session, not per run: the
# stop guard resolves them from the session dir alone, and a lane that wrote its
# own copy would be signalling into a file no guard reads.
_SESSION_SCOPED_BY_DESIGN = frozenset(
    {
        "spec-approval-pending",
        "manual-switch-pending",
        "build-handback-pending",
        "verify-gate-pending",
        "plan-mode-active",
        "active_plan.json",
        "worktree.json",
    }
)


def _fixed_artifact_offenders() -> list[str]:
    offenders: list[str] = []
    for skill in (*_WORKFLOW_SKILLS, "build"):
        for md in sorted((SKILLS_DIR / skill).rglob("*.md")):
            for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                for match in _FIXED_SESSION_ARTIFACT.finditer(line):
                    name = match.group("name")
                    if name in _SESSION_SCOPED_BY_DESIGN or _RUN_COMPONENT.search(name):
                        continue
                    offenders.append(f"{md.relative_to(SKILLS_DIR)}:{lineno}: $SESS_DIR/{name}")
    return offenders


def test_session_artifacts_carry_a_per_run_component() -> None:
    offenders = _fixed_artifact_offenders()
    assert not offenders, (
        "Review artifacts written under $SESS_DIR must carry a per-run component "
        "(<slug>/<lane>/<plan-slug>). A fixed filename is shared by every concurrent "
        "orchestration lane, because a subagent resolves the same session id as its "
        "parent - so one lane reads a sibling's findings as its own, and one lane's "
        "cleanup glob deletes a sibling's in-flight file (issue #173). Offenders:\n" + "\n".join(offenders)
    )


def _incomplete_session_chain_offenders() -> list[str]:
    offenders: list[str] = []
    for md in sorted(SKILLS_DIR.rglob("*.md")):
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if _INCOMPLETE_SESSION_CHAIN.search(line):
                offenders.append(f"{md.relative_to(SKILLS_DIR)}:{lineno}: {line.strip()}")
    return offenders


def test_skill_bash_resolves_full_session_chain() -> None:
    offenders = _incomplete_session_chain_offenders()
    assert not offenders, (
        "Skill bash must resolve the session id via the full agent-native chain "
        "${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}} "
        "(matching launcher/session.py and pilot/hooks/_lib/util.py), never a "
        "shorter chain that collapses to the shared 'default' dir when "
        "PILOT_SESSION_ID (IDE/desktop) or CLAUDE_CODE_SESSION_ID (Codex) is unset "
        "- that bleeds per-session state (e.g. the codex-once flag) across "
        "unrelated sessions (issue #167). Offenders:\n" + "\n".join(offenders)
    )
