---
name: benchmark
description: Benchmark and evaluate Claude Code rules, skills, and workflows with quantitative before/after comparisons. Use whenever the user wants to measure the impact of rules/skills/workflows, compare versions, or validate that a rule pack improves outputs.
user-invocable: true
model: opus
---

# /benchmark — Benchmark & Evaluation Framework

Measure the real impact of Claude Code rules and skills by running with/without comparisons, grading outputs against assertions, and presenting the findings inline.

## When to use this skill

- User wants to validate that a skill, rule, or rule pack actually improves outputs
- User says "benchmark", "evaluate", "measure", "before/after", "with vs without", "does this skill help?"
- User wants to extend a pilot eval matrix to more targets
- User wants to iterate on a skill or rule pack and needs quantitative feedback

## Supported target types

Two target types — both run in isolated `/tmp/pilot-bench-*` directories, one fresh directory per (eval, config, run):

| Target type | `with/` config | `without/` config | Use when |
|-------------|---------------|-------------------|----------|
| `skill` | Skill installed in `.claude/skills/<name>/` | Empty `.claude/` | Measuring "should we ship this skill?" |
| `rules` | Rule file(s) copied into `.claude/rules/` | Empty `.claude/` | Measuring "does this rule/pack improve behavior?" |

Workflow-style skills like `/spec` are benchmarked as `type=skill` — present vs absent.

## Isolation guarantees

- **Per-run filesystem sandbox.** Each (eval, config, run) triple gets its own `/tmp/pilot-bench-*/` cwd. Use relative paths in prompts, or the `{sandbox}` placeholder when you need an absolute path. Hardcoded `/tmp/<fixed-name>/` in prompts is flagged at load time.
- **Global-rule auto-hiding.** `~/.claude/rules/<basename>.md` and `~/.claude/skills/<name>/` are moved aside for the duration of the run when they duplicate the target, then restored automatically. Layered fail-safes (on-disk recovery manifest + atexit + SIGINT/SIGTERM/SIGHUP handlers + next-run sweep) make the restore robust against kill -9, power loss, and segfaults. Opt out with `--no-isolate-global` for realistic "day-to-day" measurement.

## Workflow

Follow these steps sequentially:

1. **Intake** (`steps/01-intake.md`) — Detect what the user wants to benchmark. If an existing `benchmarks/<target>/evals.json` exists, skip to execute.
2. **Target discovery** (`steps/02-target-discovery.md`) — Help the user pick a target and determine its type.
3. **Author evals** (`steps/03-author-evals.md`) — Draft 3 falsifiable, discriminating assertions for the target. Get user sign-off before spending compute.
4. **Execute** (`steps/04-execute.md`) — Run the runner, watch for failures, summarize results inline.
5. **Present findings** (`steps/05-review-iterate.md`) — Parse benchmark.json + per-run grading.json, render a per-eval matrix with evidence quotes in chat.
6. **Improvement plan** (`steps/06-improvement-plan.md`) — Classify each assertion into Signal / Baseline / Unreachable / Regression, propose concrete edits to the target or to evals.json, ask the user which path to take, apply & re-run.

## Quick reference

**Config path:** `benchmarks/<target-name>/evals.json`
**Outputs:** `benchmarks/<target-name>/runs/<timestamp>/`
**Runner:** `PYTHONPATH=~/.claude/skills/benchmark uv run python -m scripts.runner --config <evals.json> --skip-permissions`

**Defaults worth knowing:**
- `--runs 1` (keeps token cost low; bump only for variance analysis)
- `--workers 4` (bump to `min(total_runs, 8)` for small eval sets so all runs land in one wave)
- `--model` is read from the target skill's frontmatter (alias → ID); rules and model-less skills fall back to `claude-sonnet-4-6`
- `--grader-model` defaults to the same model as `--model` so executor and grader stay matched
