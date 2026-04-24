# Step 1 — Intake

Figure out what the user wants to benchmark and whether they have eval config already.

## Ask the user

1. **What are you benchmarking?** If they named a target (skill name, rule file), proceed. If they were vague ("benchmark my setup", "see if my rules help"), ask them to name one specific artifact.
2. **Does `benchmarks/<target-name>/evals.json` already exist in this project?**
   - Yes → skip to Step 4 (Execute).
   - No → go to Step 2 (Target discovery) to determine type and path.

## Default conventions

- Target name defaults to the directory basename (e.g., `testing` for `pilot/rules/testing.md`, `create-skill` for `pilot/skills/create-skill/`).
- Config path: `benchmarks/<target-name>/evals.json` relative to the project root.
- Results path: `benchmarks/<target-name>/runs/<ISO-timestamp>/`.

## When evals already exist

Read the existing `benchmarks/<target>/evals.json` and summarize it back to the user:

- Target type and path
- Number of evals and their prompts (one-liner each)
- Whether there are prior runs committed under `runs/`

Confirm they want to re-run against the same config, then advance to Step 4.

## When target is ambiguous

If the user says something like "benchmark all my rules" or "test everything", push back:

- Benchmarks run per-target. Running 15 rules sequentially is ~30 min of compute.
- Start with ONE target — prove the eval set is falsifiable (baseline fails the assertions) — then copy the evals.json as a template for the next target.

## Exits

- Have target + evals → Step 4
- Have target, no evals → Step 2
- No target → ask again before spending compute
