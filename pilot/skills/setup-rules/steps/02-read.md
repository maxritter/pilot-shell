## Step 2: Read Existing Rules & Skills

**Do this first.**

1. Derive the project slug (see Step 1 → Project Slug)
2. `find .claude/rules/ -name '*.md' -not -name 'README.md' 2>/dev/null | sort` — read each rule file (including subdirectories)
3. Check for `CLAUDE.md`, `claude.md`, and `.claude.md`; read each file found. Record whether root `CLAUDE.md` is exactly the one-line `@AGENTS.md` import. Treat every other line as user-authored migration input, not disposable generated content.
4. Check for `AGENTS.md` and `agents.md`; read each file found. Root `AGENTS.md` is the shared cross-agent core. Its absence is a setup gap for both Claude Code and Codex.
5. Inventory project skills in both `.agents/skills/` and `.claude/skills/`. Use Git to distinguish tracked project assets from untracked or ignored local extensions. Compare names and every file under each tracked matching skill. Record canonical-only skills, tracked mirror-only skills, and content drift. Local untracked/ignored Claude-only skills are out of scope and must be preserved. Do not choose a winner for conflicting tracked copies until Step 11's decision gate.
6. Check for `scripts/sync-agent-assets.mjs`, Pilot's shared agent-asset hook registration for both Claude Code and Codex, and existing CI calls to `sync-agent-assets.mjs --check`. Record the checker path, hook coverage, and existing CI job.
7. **Detect unscoped legacy files** — look for `project.md`, `mcp-servers.md`, or any rule without the `{slug}-` prefix. Flag for migration in Step 3.
8. **Detect nested rule directories** — check for subdirectories within `.claude/rules/` (product/team structure per Step 1 → Recommended Directory Structure). Map each subdirectory, its depth level (product vs team), and contents. Also check for sub-projects with their own `.claude/rules/`, `CLAUDE.md`, or `AGENTS.md`.
9. **Validate path-scoping** — flag every detailed rule without `paths` frontmatter. The fix is either a real path scope or moving genuinely shared content into `AGENTS.md`.
10. Build inventory: shared core, import shim, scoped rules, skill source/mirror parity, automatic hook coverage, checker/CI backstops, gaps, outdated items, legacy files, nested directories, and path-scoping violations.
