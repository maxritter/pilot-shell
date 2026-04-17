---

## Step 8: Example

**Scenario:** User asks to create a skill for finding dead code using LSP.

**Result:** `.claude/skills/my-project-lsp-cleaner/SKILL.md`

```yaml
name: my-project-lsp-cleaner
description: |
  Find dead/unused code using LSP findReferences. Use when: (1) user asks
  to find dead code, (2) cleaning up codebase, (3) refactoring. Key insight:
  function with only 1 reference (definition) or only test refs is dead code.
targets: [claude]
tags: [refactoring, code-quality]
license: MIT
author: Claude Code
version: 1.0.0
```
