## Step 2: Read Existing Rules & Skills

**Do this first.**

1. Derive the project slug (see Step 1 → Project Slug)
2. `find .claude/rules/ -name '*.md' -not -name 'README.md' 2>/dev/null | sort` — read each rule file (including subdirectories)
3. Check for `CLAUDE.md`, `claude.md`, and `.claude.md`; read each file found. Record whether root `CLAUDE.md` is exactly the one-line `@AGENTS.md` import. Treat every other line as user-authored migration input, not disposable generated content.
4. Check for `AGENTS.md` and `agents.md`; read each file found. Root `AGENTS.md` is the shared cross-agent core. Its absence is a setup gap for both Claude Code and Codex.
5. Inventory project skills in both `.agents/skills/` and `.claude/skills/`. Compare names and complete trees for tracked, untracked, and gitignored valid skills. Record one-sided skills, synchronized pairs, and two-sided drift. Invalid one-sided directories remain private and untouched. Do not choose a winner when both valid copies changed independently; preserve both for Step 11's decision gate.
6. Check for `scripts/sync-agent-assets.mjs`, Pilot's shared agent-asset hook registration for both Claude Code and Codex, and existing CI calls to `sync-agent-assets.mjs --check`. Record the checker path, hook coverage, and existing CI job.
7. **Detect unscoped legacy files** — look for `project.md`, `mcp-servers.md`, or any rule without the `{slug}-` prefix. Flag for migration in Step 3.
8. **Detect nested rule directories** — check for subdirectories within `.claude/rules/` (product/team structure per Step 1 → Recommended Directory Structure). Map each subdirectory, its depth level (product vs team), and contents. Also check for sub-projects with their own `.claude/rules/`, `CLAUDE.md`, or `AGENTS.md`.
9. **Validate path-scoping** — flag every detailed rule without `paths` frontmatter. The fix is either a real path scope or moving genuinely shared content into `AGENTS.md`.
10. Build inventory: shared core, import shim, scoped rules, skill source/mirror parity, SessionStart/edit/Stop hook coverage, checker/CI backstops, gaps, outdated items, legacy files, nested directories, and path-scoping violations.
