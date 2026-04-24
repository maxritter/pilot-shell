# Step 5 — Present findings

The runner has finished. No external viewer — Claude reads the artifacts directly and presents findings inline so the user can see them without switching context.

This step is **reporting only**. Classifying the findings and proposing concrete edits happens in Step 6 (`steps/06-improvement-plan.md`). Do not skip Step 6 — a benchmark without an improvement plan is a report card, not a tool.

## Artifacts to read

For the run directory `benchmarks/<target>/runs/<timestamp>/`:

| File | Purpose |
|------|---------|
| `benchmark.json` | Aggregate metrics and delta |
| `benchmark.md` | Pre-rendered summary table |
| `eval-N/eval_metadata.json` | Prompt text + assertion list (per eval) |
| `eval-N/{with_skill,without_skill}/run-M/grading.json` | Per-assertion verdict + evidence + optional `eval_feedback.suggestions` |
| `eval-N/{with_skill,without_skill}/run-M/failed.json` | Present only when the run failed |

## Presentation format

Render **three sections** directly in chat — short, scannable, no links to external pages.

### 1. Headline

One table quoting the summary block from `benchmark.json → run_summary`:

```
| Config | Pass rate | Avg time | Avg tokens |
| with   | X/N (0.XX) | XXs | XXk |
| without| X/N (0.XX) | XXs | XXk |
| delta  | +0.XX pass-rate | ±Xs | ±Xk |
```

Call out any failed runs (presence of `failed.json`) and the failure reason.

### 2. Per-eval verdict matrix

For each eval, one compact block:

```
Eval N — <name>
  Assertion 1 …  with ✓  without ✗   evidence (with): "<quote from grading.json>"
  Assertion 2 …  with ✓  without ✓
  Assertion 3 …  with ✓  without ✗   evidence (with): "<quote>"
```

Cross-reference prompt text from `eval_metadata.json` only when the assertion wording needs context — otherwise keep the assertion text as-is and quote the grader's evidence field for any case where the two configs diverge.

### 3. Grader-flagged critiques

Walk each `grading.json` and read `eval_feedback.suggestions`. If any exist, surface them — these are the grader pointing out that an assertion was trivially satisfied or that an important outcome has no assertion. They are the richest source of signal for tightening the next iteration.

## Read the files efficiently

Don't inline dozens of `grading.json` files into the conversation. Use a single sandbox script to walk the directory tree and print the compact summary. Example approach (run via a Python executor if preferred):

```python
import json
from pathlib import Path

run_dir = Path("benchmarks/<target>/runs/<timestamp>")
benchmark = json.loads((run_dir / "benchmark.json").read_text())

for eval_dir in sorted(run_dir.glob("eval-*")):
    meta = json.loads((eval_dir / "eval_metadata.json").read_text())
    print(f"\nEval {meta['eval_id']} — {meta['eval_name']}")
    for i, assertion in enumerate(meta["assertions"], start=1):
        verdicts = {}
        for cfg in ("with_skill", "without_skill"):
            grading_file = eval_dir / cfg / "run-1" / "grading.json"
            if not grading_file.exists():
                continue
            grading = json.loads(grading_file.read_text())
            exp = grading["expectations"][i - 1]
            verdicts[cfg] = exp
        with_ok = verdicts.get("with_skill", {}).get("passed")
        without_ok = verdicts.get("without_skill", {}).get("passed")
        evidence = verdicts.get("with_skill", {}).get("evidence", "")[:200]
        print(f"  {i}. with={'✓' if with_ok else '✗'}  without={'✓' if without_ok else '✗'}  — {assertion[:80]}")
        if with_ok != without_ok:
            print(f"       evidence: {evidence}")
```

Only print the compact lines, not raw grading blobs.

## Exit

Go to Step 6 (`steps/06-improvement-plan.md`) — classify each assertion, propose concrete edits, and ask the user whether to apply target edits, iterate on evals, do both, or stop.
