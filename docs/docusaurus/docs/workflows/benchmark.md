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

## Reading the report

`/benchmark` shows results in **three layers**, designed to be absorbed in 30 seconds. Read top-to-bottom and stop when you have your answer.

### Layer 1 — Verdict + headline

The first three lines tell you whether to ship, iterate, or worry. The verdict sentence has a fixed shape: emoji label + quantified claim + forward-pointing action hint.

```
VERDICT  🟢 Moderate signal — rule lifts pass rate from 0.33 to 0.78 (+0.44).
         Ship after addressing 1 Unreachable assertion (eval-1, #3).

         Pass rate     with 7/9 (0.78)   without 3/9 (0.33)   Δ +0.44 🟢
         Avg time      with 27.5s        without 25.9s        Δ +1.6s
         Avg tokens    with 200k         without 206k         Δ −6k
         Runs          3/3 ok            3/3 ok               0 failed
```

The label maps directly to a recommended next step:

| Delta range | Label | What to do |
|---|---|---|
| `≥ +0.50` | 🟢 **Strong signal** | Rule clearly works. Ship; consider expanding coverage. |
| `+0.20 to +0.49` | 🟢 **Moderate signal** | Rule helps. Ship if the lift justifies the rule's maintenance cost. |
| `+0.05 to +0.19` | 🟡 **Weak signal** | Real but small. Tighten assertions or strengthen the rule's language/examples. |
| `−0.05 to +0.04` | ⚪ **Indistinguishable** | Either assertions don't discriminate, or the rule isn't landing — the quadrant breakdown below tells you which. |
| `< −0.05` | 🔴 **Regression** | Investigate before shipping. The rule actively misled the model. |

Stddev > 0.30 in pass rate on any single eval = flaky/model-dependent — re-run with `--runs 3` before drawing conclusions.

### Layer 2 — Quadrant breakdown

Each assertion is classified by its `(with, without)` verdict pair. The counts tell you whether to fix the rule or the evals:

```
Quadrant breakdown   (out of 9 assertions)
  🟢 Signal        5    rule works here
  ⚪ Baseline      3    eval doesn't discriminate — tighten assertions
  🟡 Unreachable   1    rule isn't cutting through — sharpen rule
  🔴 Regression    0
```

| Quadrant | `with` / `without` | Means | Fix |
|---|---|---|---|
| **Signal** | ✓ / ✗ | Rule works here | Keep — consider amplifying |
| **Baseline** | ✓ / ✓ | Eval doesn't discriminate | Tighten the assertion |
| **Unreachable** | ✗ / ✗ | Rule isn't cutting through | Sharpen the target |
| **Regression** | ✗ / ✓ | Rule misled the model | Fix the target — blocks shipping |

The dominant quadrant drives the improvement plan: Signal-heavy → ship, Baseline-heavy → fix evals, Unreachable-heavy → fix rule, any Regression → investigate first.

### Layer 3 — Per-eval drill-down (divergent only)

Only assertions where `with ≠ without` get a row. Matching ones are folded into the per-eval header counts so the report stays scannable. Evidence is capped at 200 chars.

```
Eval 1 — strict-tdd-naming-pbt          🟢×2  ⚪×0  🟡×1  🔴×0
  🟢 #1  Every test decorated with @pytest.mark.unit
         evidence (with):  "All 5 tests use @pytest.mark.unit decorator"
  🟢 #2  Test names follow strict 4-segment regex
         evidence (with):  "9 test names match test_slugify_<scenario>_<expected>"
  🟡 #3  ≥1 property-based test using hypothesis
         (both fail — rule doesn't teach hypothesis PBT)

Eval 2 — mock-audit-new-dependency       🟢×3  ⚪×0  🟡×0  🔴×0
  🟢 #1  BOTH pre-existing tests updated with subprocess mocks
         evidence (with):  "Both test_build_order_id_* updated with @patch"
  🟢 #2  Mock applied at module-of-consumption
         evidence (with):  "@patch('orders.subprocess.run') in all tests"
  🟢 #3  pytest run completes <1s wall time
         evidence (with):  "pytest finished in 0.04s, no real git invocation"
```

If the grader flagged any assertions as trivially-satisfied or noticed an uncovered behavior, those critiques appear in their own short section.

## The improvement plan

After the report, `/benchmark` proposes **specific edits** (≤ 5, ranked by expected delta) using a uniform format. Every proposal names a location, quotes the current text, shows the replacement, and labels the lever it pulls.

```
1. [TARGET]  pilot/rules/testing.md  L42–L44
       Quadrant: Unreachable (eval-1 #3 — hypothesis PBT)
       Current:  "Property-based testing is encouraged for complex inputs."
       Propose:  "⛔ Property-based test required for parsers and serializers — use `hypothesis.@given`."
       Lever:    Soft language → mandatory; adds the exact tool name.

2. [EVALS]   eval-2 assertion #3
       Quadrant: Baseline (grader: "would pass for partially-mocked test")
       Current:  "pytest run completes in <1s wall time"
       Propose:  "subprocess.run mock asserts called_once_with(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])"
       Lever:    Loose timing check → exact call signature.
```

Then `/benchmark` asks which path to take:

1. Apply target edits and re-run
2. Apply eval edits and re-run (with the falsifiability gate first)
3. Both (the lift becomes harder to attribute)
4. Save the plan and stop

`/benchmark` never applies edits silently. Re-runs land in a fresh `runs/<ts>/` so iteration-over-iteration deltas stay legible.

## Gotcha: global contamination

A globally-installed copy of your target in `~/.claude/` would leak into the `without` config. The runner moves it aside for the run and restores it automatically.

Pass `--no-isolate-global` to measure "target + your day-to-day setup" instead.

## Gotcha: conditional-loading frontmatter

Pilot rules (and skills) can scope themselves to specific files via YAML frontmatter — e.g. `paths: ["**/*.py"]` for Python-only rules. If the benchmark prompts don't fall inside that glob, the rule stays dormant in the `with` config too and the delta collapses to 0.00 — you'd be measuring activation, not the rule's content.

The runner strips `path:` and `paths:` from the **copy** installed into the `with` sandbox so the target loads unconditionally for every prompt during the run. The original source file is never touched. A one-line announcement at startup names which files and which fields were stripped, so it never happens silently.
