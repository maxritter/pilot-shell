---
name: create-skill
description: Create, edit, synchronize, and test a reusable skill future agents can find and follow. Use when the user types /create-skill, asks to make, write, add, or extract a skill, wants a repeatable workflow or technique from this session captured for reuse, asks to change an existing skill's steps, description, or trigger keywords, or needs one project skill to work in both Claude Code and Codex.
user-invocable: true
---

# /create-skill — Skill Creator

**Create a reusable skill.** Provide a topic or workflow description, and this command explores the codebase, gathers relevant patterns, and builds a well-structured skill interactively with you. Project skills are authored once in `.agents/skills/`; Pilot's shared hook automatically generates `.claude/skills/` after edits from either agent. If no topic is given, it evaluates the current session for extractable knowledge.

## Editing existing skills

For NEW skills, Step 6 runs the with-skill vs baseline subagent comparison — no skill ships without it.

For EDITS, classify the change first:

- **Behavioural** — adds/removes a step, changes a rule, reorders critical sections, edits the description, changes Iron Laws / red flags / rationalization tables, modifies trigger keywords. **Re-run Step 6 (or write 2–3 prompts if none exist).** These changes shift trigger accuracy and step compliance.
- **Cosmetic** — typo, prose polish, link fix, formatting, example clarification with no semantic shift. Skip the test re-run.

When uncertain, treat as behavioural. Skill changes that go unverified are how skill quality drifts.
