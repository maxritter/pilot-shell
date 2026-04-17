## Step 4: Quality Audit

**Audit all existing rules and CLAUDE.md files against Claude Code best practices (Step 1 → Best Practices Reference).** Present findings as improvement suggestions — do NOT modify files without user confirmation.

**Skip this phase if:** No existing rules or CLAUDE.md files found in Step 2 (nothing to audit).

### Step 4.1: Run Checks

For each rule file and CLAUDE.md found in Step 2, evaluate:

| Check                          | What to look for                                                                                                                                 | Severity |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| **Size**                 | Files over 200 lines (context bloat, reduced adherence)                                                                                          | Warning  |
| **Specificity**          | Vague instructions: "format properly", "write clean code", "keep organized" — suggest concrete alternatives                                     | Warning  |
| **Redundancy**           | Standard conventions Claude already knows (e.g., "use const for immutable variables" in a JS project)                                            | Info     |
| **Conflicts**            | Contradicting instructions across different files (e.g., one rule says "use tabs", another says "use spaces")                                    | Error    |
| **Path-scoping**         | Rules that mention specific file types/directories but lack `paths` frontmatter — these load every session unnecessarily                      | Info     |
| **Nested path-scoping**  | Rules in team-level subdirectories (`.claude/rules/{product}/{team}/`) without `paths` frontmatter — MUST be scoped (see Step 1 → Recommended Directory Structure) | Error    |
| **Structure**            | Dense paragraphs without headers/bullets, poor scanability, missing section organization                                                         | Warning  |
| **Stale references**     | References to files, commands, paths, or tools that no longer exist in the codebase — verify with `ls` or Probe                               | Error    |
| **Import opportunities** | Large files that could split content using `@path/to/import` syntax                                                                            | Info     |
| **Emphasis gaps**        | Critical rules (security, data loss, breaking changes) without emphasis markers ("IMPORTANT", "YOU MUST")                                        | Info     |
| **CLAUDE.md overlap**    | Content duplicated between CLAUDE.md and `.claude/rules/` files                                                                                | Warning  |

**How to check for specificity:** Look for adjectives without measurable criteria ("good", "clean", "proper", "nice"), instructions that restate language defaults, and rules without concrete examples or verifiable outcomes.

**How to check for stale references:** For each file path, command, or tool name referenced in rules, verify existence:

```bash
# File paths
ls -la <referenced-path> 2>/dev/null

# Commands
which <referenced-command> 2>/dev/null

# Code patterns (Probe if available, otherwise Grep)
probe search "<referenced-pattern>" ./ --max-results 1 --max-tokens 500
# Fallback: Grep(pattern="<referenced-pattern>", head_limit=5)
```

### Step 4.2: Present Findings

Group findings by severity and present to user:

```
## Quality Audit Results

### Errors (should fix)
- ❌ **Conflict:** `.claude/rules/style.md` says "use tabs" but `CLAUDE.md` says "use 2-space indent"
- ❌ **Stale:** `.claude/rules/project.md` references `src/legacy/` which no longer exists

### Warnings (recommended)
- ⚠️ **Size:** `CLAUDE.md` is 340 lines — split into modular rules or use @imports (target: <200 lines)
- ⚠️ **Vague:** `.claude/rules/style.md` line 12: "Format code properly" → suggest: "Run `prettier --write` before committing"
- ⚠️ **Overlap:** Authentication instructions appear in both `CLAUDE.md` and `.claude/rules/auth.md`

### Suggestions (nice to have)
- 💡 **Path-scope:** `.claude/rules/testing.md` only mentions `*.test.ts` files — add `paths: ["**/*.test.ts"]` frontmatter
- 💡 **Emphasis:** `.claude/rules/security.md` line 5: "Never commit secrets" — add "IMPORTANT:" prefix
- 💡 **Import:** `CLAUDE.md` inlines API docs — replace with `@docs/api-reference.md`
```

### Step 4.3: User Decision

AskUserQuestion (multiSelect): "Select improvements to apply:"

- List each finding with checkbox
- Group by file for clarity
- Options: **"Fix all errors & warnings"** | **"Review each"** | **"Fix errors only"** | **"Skip audit"**

### Step 4.4: Apply Selected Fixes

For each selected improvement:

1. Read the target file
2. Apply the specific fix (rewrite vague instruction, add `paths` frontmatter, split large file, remove stale reference, add emphasis, resolve conflict)
3. Show the diff to user before writing
4. Write the updated file

**For file splits:** When splitting a file over 200 lines, create new modular files in `.claude/rules/` with the `{slug}-` prefix and add `@path` imports in the original if appropriate.

**For conflict resolution:** Present both conflicting instructions, ask user which is correct, update both files to be consistent.
