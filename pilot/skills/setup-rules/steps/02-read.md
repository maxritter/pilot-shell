---

## Step 2: Read Existing Rules & Skills

**MANDATORY FIRST STEP.**

1. Derive the project slug (see Step 1 → Project Slug)
2. `find .claude/rules/ -name '*.md' -not -name 'README.md' 2>/dev/null | sort` — read each rule file (including subdirectories)
3. Check for legacy CLAUDE.md: `ls CLAUDE.md claude.md .claude.md 2>/dev/null` — read if found
4. Check for AGENTS.md: `ls AGENTS.md agents.md 2>/dev/null` — read if found. This is the cross-framework agent context file (Codex, Cursor, etc.). Treat it as a migration source like CLAUDE.md, and remember it exists so Step 11 can offer to sync rules back into it. **Never create AGENTS.md if it doesn't exist.**
5. **Detect unscoped legacy files** — look for `project.md`, `mcp-servers.md`, or any rule without the `{slug}-` prefix. Flag for migration in Step 3.
6. **Detect nested rule directories** — check for subdirectories within `.claude/rules/` (product/team structure per Step 1 → Recommended Directory Structure). Map each subdirectory, its depth level (product vs team), and contents. Also check for sub-projects with their own `.claude/rules/` or `CLAUDE.md`.
7. **Validate path-scoping** — for rules in nested subdirectories, check that they have `paths` frontmatter. Flag any team-level rules (depth 2+) missing `paths` as errors for Step 4.
8. Build inventory: documented rules (with directory structure map), CLAUDE.md contents, AGENTS.md contents (if present), gaps, outdated items, legacy files, nested directories, path-scoping violations
