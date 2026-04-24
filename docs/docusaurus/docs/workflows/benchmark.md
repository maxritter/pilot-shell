---
sidebar_position: 6
title: /benchmark
description: Measure the real impact of rules and skills with quantitative before/after comparisons
---

# /benchmark

Measure whether your rules and skills actually improve outputs — with numbers, not vibes.

```bash
pilot
> /benchmark pilot/skills/create-skill
> /benchmark pilot/rules/testing.md
```

## When to use

- You shipped a rule or skill and want evidence it helps
- You're iterating and need before/after feedback
- You want to catch regressions quantitatively

## How it works

`/benchmark` runs your prompts twice — **with** and **without** the target — grades both against falsifiable assertions, and shows the results inline.

| Type | `with` | `without` |
|------|--------|-----------|
| `skill` | Skill installed | Empty `.claude/` |
| `rule` | Rule loaded | Empty `.claude/` |

## Writing good assertions

The only thing that matters: **baseline must plausibly fail**.

Modern models already write tests and mock things — assertions have to reach past that. Target project-specific patterns, strict markers, exact naming regexes, coverage gates. The benchmark enforces a falsifiability gate before burning compute.

**Good:** `Every test function is decorated with @pytest.mark.unit` — grep-verifiable, baseline often skips.
**Bad:** `The code is well-designed` — unverifiable.

## Reading the delta

- `> 0` — target helps
- `≈ 0` — no-op OR assertions don't discriminate
- `< 0` — regression, investigate

## The improvement plan

After the run, `/benchmark` classifies every assertion into one of four quadrants and proposes **concrete edits**:

| Quadrant | `with` / `without` | Meaning | Fix |
|----------|---|---|---|
| **Signal** | ✓ / ✗ | Rule works here | Keep |
| **Baseline** | ✓ / ✓ | Doesn't discriminate | Tighten the eval |
| **Unreachable** | ✗ / ✗ | Rule isn't landing | Sharpen the target |
| **Regression** | ✗ / ✓ | Rule misdirects | Fix the target |

Each proposed edit names the file + lines, quotes the current text, and shows the replacement. Then you pick:

1. Apply target edits and re-run
2. Apply eval edits and re-run
3. Both (harder to attribute the lift)
4. Stop and save the plan

`/benchmark` never applies edits silently.

## Gotcha: global contamination

A globally-installed copy of your target in `~/.claude/` would leak into the `without` config. The runner moves it aside for the run and restores it automatically.

Pass `--no-isolate-global` to measure "target + your day-to-day setup" instead.
