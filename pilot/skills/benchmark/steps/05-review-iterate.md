# Step 5 — Present findings

The runner has finished. Read the artifacts directly and present findings inline — no external viewer.

This step is **reporting only**. Translating the findings into proposed edits happens in Step 6 (`steps/06-improvement-plan.md`). Always advance to Step 6 — a benchmark without a follow-up plan is a report card, not a tool.

## Goal

Render a report a busy user can absorb in **30 seconds** and act on. Lead with the verdict, surface the quadrant shape, then drill into divergent assertions only. Save full evidence and matching assertions for "tell me more".

## Artifacts to read

For the run directory `benchmarks/<target>/runs/<timestamp>/`:

| File | Purpose |
|------|---------|
| `benchmark.json` | Aggregate metrics + delta |
| `eval-N/eval_metadata.json` | Prompt + assertion list per eval |
| `eval-N/{with_skill,without_skill}/run-M/grading.json` | Per-assertion verdict + evidence + grader critiques |
| `eval-N/{with_skill,without_skill}/run-M/failed.json` | Present only when the run failed |

## Delta interpretation rubric (read this BEFORE writing the report)

The pass-rate delta from `benchmark.json → run_summary.delta.pass_rate` is the headline number. Map it to a label so the user knows whether to celebrate, iterate, or worry:

| `delta.pass_rate` | Label | What it means |
|---|---|---|
| **≥ +0.50** | 🟢 Strong signal | Rule clearly lifts model behavior. Ready to ship; consider expanding coverage. |
| **+0.20 to +0.49** | 🟢 Moderate signal | Rule helps. Worth shipping if the lift justifies the rule's maintenance cost. |
| **+0.05 to +0.19** | 🟡 Weak signal | Real but small. Either tighten assertions to expose a sharper effect, or strengthen the rule's language/examples. |
| **−0.05 to +0.04** | ⚪ Indistinguishable | Either assertions don't discriminate (most common — see Quadrant breakdown), or the rule isn't landing, or both. **Step 6 will diagnose which.** |
| **< −0.05** | 🔴 Regression | The rule actively misled the model. Investigate before shipping — Step 6 will name the regressing assertions. |

Stddev > 0.30 on any single eval = flaky/model-dependent — re-run with `--runs 3` before drawing conclusions.

## Compute quadrants in the same pass

For each `(eval, assertion)`, classify the `(with, without)` verdict pair:

| `with` | `without` | Quadrant | One-line meaning |
|---|---|---|---|
| ✓ | ✗ | **Signal** | Rule works here |
| ✓ | ✓ | **Baseline** | Eval doesn't discriminate |
| ✗ | ✗ | **Unreachable** | Rule isn't cutting through |
| ✗ | ✓ | **Regression** | Rule is making it worse — surface loudly |

Counting these up front lets the user see the shape immediately and gives Step 6 the input it needs.

## Presentation format — render in this order

### 1. One-line verdict + headline (always at the top)

```
VERDICT  🟢 Moderate signal — rule lifts pass rate from 0.33 to 0.78 (+0.44).
         Ship after addressing 1 Unreachable assertion (eval-1, #3).

         Pass rate     with 7/9 (0.78)   without 3/9 (0.33)   Δ +0.44 🟢
         Avg time      with 27.5s        without 25.9s        Δ +1.6s
         Avg tokens    with 200k         without 206k         Δ −6k
         Runs          3/3 ok            3/3 ok               0 failed
```

The verdict sentence has a **fixed shape**:
1. Emoji + label (from the rubric above)
2. Quantified claim using the delta and raw pass rates
3. Action hint pointing forward to Step 6 (e.g. "Ship after fixing the 1 regression" / "Tighten assertions before re-running" / "Investigate eval-2 regression")

If `delta.pass_rate` is in the **Indistinguishable** band, the verdict must say **why** based on the quadrant shape — otherwise the user doesn't know if the rule is broken or the evals are. Examples:
- Quadrant heavy in Baseline → "rule works but evals don't measure it; rewrite assertions"
- Quadrant heavy in Unreachable → "rule isn't landing; sharpen its cues"
- Mixed → "investigate per-eval — Step 6 will propose edits"

If any **Regression** assertions exist, surface them in the verdict regardless of overall delta.

### 2. Quadrant breakdown

```
Quadrant breakdown   (out of 9 assertions)
  🟢 Signal        5    rule works here
  ⚪ Baseline      3    eval doesn't discriminate (Step 6 will tighten)
  🟡 Unreachable   1    rule isn't cutting through (Step 6 will sharpen)
  🔴 Regression    0
```

This is the same data Step 6 needs — print it once here, refer back from Step 6 instead of recomputing.

### 3. Per-eval drill-down — divergent assertions only

For each eval, show **only** assertions where `with ≠ without` (Signal or Regression) plus any Regression assertions explicitly. Fold Baseline and Unreachable into a count summary so the user isn't drowned in matching rows.

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

Quote evidence ≤ 200 chars. Drop matching assertions entirely from the body and fold them into the per-eval header counts so the row count stays low.

### 4. Grader-flagged critiques (only if any)

Walk each `grading.json` → `eval_feedback.suggestions`. These are the grader pointing out trivially-satisfied assertions or important uncovered behaviors. They feed directly into Step 6's eval-edit proposals.

```
Grader critiques
  eval-2 #3  "Wall-time check is loose — would also pass for a partially-mocked test
              that hits localhost. Consider asserting the mock was called instead."
```

Skip this section entirely when no critiques exist.

### 5. Failures (only if any)

If any run wrote `failed.json`, list them with reason + suggested fix. Don't bury these — a single failed run can flip the delta.

## Read the files efficiently

One sandbox script does the whole walk and prints the structured report. Keep grading blobs out of context — only the compact lines reach the user.

```python
import json
from pathlib import Path

run_dir = Path("benchmarks/<target>/runs/<timestamp>")
bm = json.loads((run_dir / "benchmark.json").read_text())
delta = float(bm["run_summary"]["delta"]["pass_rate"])

# Map delta to label per the rubric.
if delta >= 0.50:    label = "🟢 Strong signal"
elif delta >= 0.20:  label = "🟢 Moderate signal"
elif delta >= 0.05:  label = "🟡 Weak signal"
elif delta >= -0.05: label = "⚪ Indistinguishable"
else:                label = "🔴 Regression"

# Per-assertion quadrant classification + structured output.
quadrants = {"signal": 0, "baseline": 0, "unreachable": 0, "regression": 0}
for eval_dir in sorted(run_dir.glob("eval-*")):
    meta = json.loads((eval_dir / "eval_metadata.json").read_text())
    for i in range(len(meta["assertions"])):
        with_g = json.loads((eval_dir / "with_skill" / "run-1" / "grading.json").read_text())
        without_g = json.loads((eval_dir / "without_skill" / "run-1" / "grading.json").read_text())
        w = with_g["expectations"][i]["passed"]
        wo = without_g["expectations"][i]["passed"]
        if w and not wo:    quadrants["signal"] += 1
        elif w and wo:      quadrants["baseline"] += 1
        elif not w and wo:  quadrants["regression"] += 1
        else:               quadrants["unreachable"] += 1

print(f"VERDICT {label} — Δ pass-rate {delta:+.2f}")
print(f"Quadrants: signal={quadrants['signal']} baseline={quadrants['baseline']} "
      f"unreachable={quadrants['unreachable']} regression={quadrants['regression']}")
# ... then drill-down loop, divergent rows only ...
```

## Style rules

- **Verdict first, evidence second.** Top three lines should answer "did it work?" without scrolling.
- **One emoji per quadrant**, used consistently throughout the report. Don't introduce new emojis later.
- **Fold the ordinary, surface the divergent.** Matching assertions are summarized as counts, never enumerated as rows.
- **Cap evidence at 200 chars** per quote. Long evidence is a sign the assertion is too prosey.
- **No markdown headings deeper than `###`** — heavy headers compete with the data.
- **Skip empty sections.** No "Grader critiques (none)" filler — just don't print the header.

## Exit

Go to Step 6 (`steps/06-improvement-plan.md`) — translate quadrant counts into specific edits and ask the user which path to take.
