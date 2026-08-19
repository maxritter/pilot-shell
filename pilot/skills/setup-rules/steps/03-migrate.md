## Step 3: Migrate Unscoped Assets — CONDITIONAL

**Only if Step 2 found unscoped files.**

AskUserQuestion: "Found unscoped assets that should be prefixed with '{slug}-' for better Team sharing. Migrate now?"

- **"Yes, migrate all"** — classify each instruction, move repo-wide guidance into `AGENTS.md`, rename path-specific rules to `{slug}-{name}`, add `paths`, update references, and delete superseded files
- **"Review each"** — show each file, let user decide per-file
- **"Skip"** — leave as-is, continue sync

**Migration rules:**

- Repo-wide content → preserve under the matching `AGENTS.md` section
- Path-specific `project.md` → `{slug}-project.md` | `mcp-servers.md` → `{slug}-mcp-servers.md` | `{topic}.md` → `{slug}-{topic}.md` (unless managed by a framework like Pilot Shell); every resulting detailed rule gets real `paths` frontmatter
- Do NOT migrate files from `~/.claude/rules/` — those are global user rules
