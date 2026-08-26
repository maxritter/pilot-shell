## Step 8: Example

**Scenario:** User asks to create a report-only skill for finding dead-code candidates safely.

**Canonical result:** `.agents/skills/my-project-dead-code-audit/SKILL.md`

**Generated Claude Code mirror:** `.claude/skills/my-project-dead-code-audit/SKILL.md`

```yaml
name: my-project-dead-code-audit
description: |
  Report dead-code candidates using the project's configured static analyzers,
  CodeGraph impact tracing, and exact repository search. Use when auditing
  unused code or planning cleanup. Never delete automatically: public entry
  points, dynamic references, and test-only references require verification.
targets: [claude, codex]
tags: [refactoring, code-quality]
license: MIT
author: Pilot Shell
version: 1.0.0
```
