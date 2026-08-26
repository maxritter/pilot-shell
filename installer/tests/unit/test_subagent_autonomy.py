"""Pilot leaves subagent topology to the active Claude Code or Codex agent."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from installer.skill_builder import build_skill_md
from installer.steps.codex_files import _adapt_invocation_syntax, build_codex_skill_md

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ("build", "spec-plan", "spec-implement", "spec-verify", "spec-bugfix-verify")
BANNED = (
    "no sub-agents",
    "no subagents",
    "no writing sub-agents",
    "one research agent is allowed",
    "only reviewer sub-agent",
)


def _runtime_text(name: str, *, codex: bool) -> str:
    skill = ROOT / "pilot" / "skills" / name
    manifest = json.loads((skill / "manifest.json").read_text())
    main = build_codex_skill_md(skill) if codex else build_skill_md(skill)
    parts = [main]
    if manifest.get("delivery") == "progressive":
        for step in manifest["steps"]:
            content = (skill / step["file"]).read_text()
            parts.append(_adapt_invocation_syntax(content) if codex else content)
    return "\n".join(parts).lower()


@pytest.mark.parametrize("skill_name", SKILLS)
@pytest.mark.parametrize("codex", [False, True], ids=["claude", "codex"])
def test_workflow_skills_have_no_blanket_subagent_prohibition(skill_name: str, codex: bool) -> None:
    text = _runtime_text(skill_name, codex=codex)

    for phrase in BANNED:
        assert phrase not in text


def test_shared_rules_forbid_delegation_permission_questions() -> None:
    rule = (ROOT / "pilot" / "rules" / "task-and-workflow.md").read_text().lower()
    codex = (ROOT / "pilot" / "codex" / "AGENTS.md").read_text().lower()

    assert "never stop a running task to ask the user for permission" in rule
    assert "never stop work to ask the user for permission to delegate" in codex


def test_hook_matrix_has_no_subagent_permission_gate() -> None:
    matrix = json.loads((ROOT / "pilot" / "hooks" / "hook-lifecycle.json").read_text())

    for entry in matrix["entries"]:
        matcher = (entry.get("matcher") or "").lower()
        assert "agent" not in matcher
        assert "task" not in matcher
