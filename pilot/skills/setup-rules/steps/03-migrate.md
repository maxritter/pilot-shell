## Step 3: Migrate Unscoped Assets — CONDITIONAL

**Only if Step 2 found unscoped files.**

AskUserQuestion: "Found unscoped assets that should be prefixed with '{slug}-' for better Team sharing. Migrate now?"

- **"Yes, migrate all"** — rename each to `{slug}-{name}`, update internal references, delete old file
- **"Review each"** — show each file, let user decide per-file
- **"Skip"** — leave as-is, continue sync

**Migration rules:**

- `project.md` → `{slug}-project.md` | `mcp-servers.md` → `{slug}-mcp-servers.md` | `{topic}.md` → `{slug}-{topic}.md` (unless managed by a framework like Pilot Shell)
- Do NOT migrate files from `~/.claude/rules/` — those are global user rules
