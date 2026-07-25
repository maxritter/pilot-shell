## Documentation Sync

**Update affected docs in the same change as the code, not as a follow-up.** Stale docs are a bug; the user should never have to ask "now update the README".

After any change, ask: **did this change something a reader of the docs is told?** If yes, update them in the same turn. The usual triggers are a public API or CLI flag added/renamed/removed, changed behaviour of a documented feature, a new or renamed config field, a new command or endpoint, a breaking change (CHANGELOG + migration notes), or a shifted directory layout.

Grep the docs tree for the symbol being changed rather than trusting memory — references hide in FAQ entries, examples, and blog posts. Change only what is now wrong; don't rewrite surrounding prose. **Verify counts and lists** ("11 phases", "supports X, Y, Z") — off-by-one numbers are the most common stale-doc bug. Use one name for a thing across code, docs, and `--help`.

**Skip** for internal refactors with no user-visible effect, bug fixes that restore already-documented behaviour, test-only changes, typos, and work the user marked WIP.

**⛔ Don't** document features that don't exist yet, bloat docs to explain a trivial change, or leave a TODO instead of updating.

List the doc files you touched alongside the code files in your summary. If the change genuinely has no doc impact, say so explicitly, so the user knows it was considered rather than forgotten.
