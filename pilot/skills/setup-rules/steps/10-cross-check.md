## Step 10: Cross-Check

**Re-read all proposed/generated files and verify against source docs and each other before installing the mirror.**

1. **Build entity index** — collect all services, entry points, modules, config keys, and enum values mentioned across generated files
2. **Cross-file completeness** — for each entity, verify it appears where required without duplicating scoped detail into the shared core
3. **Source fidelity** — for each identifier in generated rules, search source docs (Semble if available, otherwise Grep) to confirm exact spelling. If spelling differs between source and generated rule, fix the rule to match the source verbatim
4. **Section coverage** — account for every significant section in existing `AGENTS.md`, non-shim `CLAUDE.md`, scoped rules, and canonical docs. Record its preserved destination.
5. **Reference validity** — cross-references between files point to files that actually exist
6. **README currency** — if `.claude/rules/README.md` exists, verify it lists all current rule files and directories. Update if stale.
7. **Path-scoping enforcement** — re-verify every detailed rule has non-empty `paths` frontmatter
8. **Rule routing parity** — verify every scoped rule appears in `AGENTS.md` with its exact globs and purpose so Codex can load the same detail on demand
9. **Skill migration safety** — account for valid skills in both trees, including untracked and gitignored skills. One-sided skills may be copied; independently changed copies must remain preserved until explicitly reconciled.
10. **Automatic sync and backstops** — verify the proposed root shim is exactly `@AGENTS.md`, the bundled installer is available, Pilot's shared hook covers SessionStart, supported edits from both agents and Stop for Code Mode, and an existing CI job has been selected for `--check` when CI exists. Do not add a second repository hook.

Auto-fix issues that do not change a user decision. Return conflicts to Step 7 or Step 11's decision gate. Keep this inventory for the evidence summary.
