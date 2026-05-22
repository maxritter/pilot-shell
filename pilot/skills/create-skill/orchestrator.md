---
name: create-skill
description: Create a well-structured skill — provide a topic to explore the codebase and build a skill interactively, or capture a workflow from the current session
user-invocable: true
---

# /create-skill — Skill Creator

**Create a reusable skill.** Provide a topic or workflow description, and this command explores the codebase, gathers relevant patterns, and builds a well-structured skill interactively with you. If no topic is given, it evaluates the current session for extractable knowledge.

## Editing existing skills

For NEW skills, Step 6 runs the with-skill vs baseline subagent comparison — no skill ships without it.

For EDITS, classify the change first:

- **Behavioural** — adds/removes a step, changes a rule, reorders critical sections, edits the description, changes Iron Laws / red flags / rationalization tables, modifies trigger keywords. **Re-run Step 6 (or write 2–3 prompts if none exist).** These changes shift trigger accuracy and step compliance.
- **Cosmetic** — typo, prose polish, link fix, formatting, example clarification with no semantic shift. Skip the test re-run.

When uncertain, treat as behavioural. Skill changes that go unverified are how skill quality drifts.
