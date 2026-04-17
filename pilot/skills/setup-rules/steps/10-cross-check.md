## Step 10: Cross-Check

**Re-read all generated/updated files and verify against source docs and each other.**

1. **Build entity index** — collect all services, entry points, modules, config keys, and enum values mentioned across generated files
2. **Cross-file completeness** — for each entity, verify it appears in all related files (e.g., a service in `{slug}-deployment.md` must also be in `{slug}-architecture.md` and `{slug}-project.md`)
3. **Source fidelity** — for each identifier in generated rules, search source docs (Probe if available, otherwise Grep) to confirm exact spelling. If spelling differs between source and generated rule, fix the rule to match the source verbatim
4. **Section coverage** — for each significant section in source docs (CLAUDE.md, `docs/`), confirm a corresponding rule section exists
5. **Reference validity** — cross-references between files point to files that actually exist
6. **README currency** — if `.claude/rules/README.md` exists, verify it lists all current rule files and directories. Update if stale.
7. **Path-scoping enforcement** — re-verify all team-level rules have `paths` frontmatter (final check)

Auto-fix any issues found. Report fixes in summary.
