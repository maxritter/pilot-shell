## Documentation Sync

**Update affected docs in the same change as the code, not as a follow-up.** Stale docs are a bug. The user should never have to ask "now update the README" after the code lands.

### When To Sync Docs

After any code change, ask: **"Did this change something a reader of the docs is told?"** If yes, update the docs in the same turn.

| Change | Update |
|--------|--------|
| Public API / CLI flag added, renamed, removed | README, `--help` text, API reference, examples |
| Behavior of a documented feature changed | Feature docs, examples, screenshots if outdated |
| Config field added / renamed / default changed | Settings docs, sample config, env var tables |
| New command, route, or endpoint | Reference list, getting-started, OpenAPI schema |
| Breaking change | CHANGELOG / release notes, migration guide |
| Architecture or directory layout shifted | Project rule (`*-project.md`), top-level README |

**Always include:** README, in-repo docs (`docs/`, Docusaurus, mkdocs), `CLAUDE.md` / `AGENTS.md` if present, `.claude/rules/*-project.md` if structure changed, code comments that reference renamed symbols.

### When NOT To Sync Docs

Skip doc updates for:

- Internal refactors with no user-visible effect
- Bug fixes that restore documented behavior (the docs were already right)
- Test-only changes
- Typos and formatting in code
- Work-in-progress commits the user explicitly marked as such

### How To Do It

1. **Locate** — grep the docs tree for the symbol/flag/feature being changed. Don't rely on memory; references hide in unexpected places (blog posts, FAQ entries, examples).
2. **Update minimally** — change only what's now wrong. Don't rewrite surrounding prose.
3. **Verify counts and lists** — if docs say "11 phases" or "supports X, Y, Z", update the count and list. Off-by-one numbers are the most common stale-doc bug.
4. **Match terminology** — use the same name in code, docs, and CLI help. Pick one and propagate.
5. **Report** — list the doc files touched alongside the code files in the final summary.

### ⛔ Do Not

- Add new docs for features that don't exist yet
- Bloat docs to "explain" trivial changes
- Leave a TODO instead of updating ("docs to follow")
- Update only the README when the same fact appears in three places

If the change is genuinely doc-irrelevant, say so explicitly in the summary ("no doc impact") so the user knows it was considered, not forgotten.
