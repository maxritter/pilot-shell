# Step 6 — Improvement plan

Step 5 reported what happened. Step 6 translates it into **specific edits the user can act on** — either to the target (rule/skill) or to `evals.json` — and ends by asking the user which path to take.

Do NOT skip this step after presenting findings. A benchmark without actionable next steps is a report card, not a tool.

## Classify every assertion into one of four quadrants

Using the per-eval verdict matrix from Step 5, bucket each assertion:

| Quadrant | with | without | Diagnosis | Primary remedy |
|----------|------|---------|-----------|----------------|
| **Signal** | ✓ | ✗ | Rule/skill is doing its job — clear lift over baseline. | Keep. Consider amplifying (reuse the pattern in sibling rules/assertions). |
| **Baseline** | ✓ | ✓ | Baseline already satisfies this; assertion measures nothing. | **Eval fix:** tighten the assertion or replace it with a harder form. |
| **Unreachable** | ✗ | ✗ | Rule isn't cutting through OR the behavior is not reachable from this prompt. | **Target fix** first (sharper cue, example, stronger language); **eval fix** second (weaker form that still discriminates). |
| **Regression** | ✗ | ✓ | Rule made things worse — it misdirected the model. | **Target fix** — re-read the relevant section, find the misdirection. |

After classifying, count each quadrant. The distribution alone tells a story:
- Mostly **Signal** → rule is working, stop or expand coverage.
- Mostly **Baseline** → eval set is the problem, rewrite before touching the rule.
- Mostly **Unreachable** → rule is too quiet or the prompts don't give it an opportunity.
- Any **Regression** → investigate immediately before shipping.

## Translate each non-Signal assertion into a concrete edit

For every assertion NOT in the Signal quadrant, generate a specific proposal. Keep proposals mechanical and observable — no "make it better" platitudes.

### Target (rule/skill) edits — for Unreachable or Regression

Read the relevant section of the rule/skill file (`target.path`). Diagnose WHY it didn't land and pick one:

| Symptom | Edit pattern | Example |
|---------|-------------|---------|
| Rule is buried late in the file | Move the cue earlier, ideally into a numbered list in the first 40 lines | Promote "use `@pytest.mark.unit`" from a prose mention to a checklist item |
| Rule uses soft language ("consider", "prefer") | Upgrade to mandatory language (`⛔`, `MUST`, `MANDATORY`, `Required`) | `Consider adding @pytest.mark.unit` → `⛔ MUST decorate every unit test with @pytest.mark.unit` |
| Rule states the what but not the how | Add a code example showing the exact form | Add `@pytest.mark.unit\ndef test_...` block |
| Rule has competing guidance nearby | Deduplicate or order by priority | Collapse two overlapping mocking sections into one |
| Rule teaches the wrong thing (Regression) | Pinpoint the misleading phrase and rewrite, or remove it | Rewrite "mock at the global module" → "mock at the import site" |

For each proposed edit, cite:
1. **Target file + line range** (Read the file if needed for precise line numbers)
2. **Current text** (quote the ≤2 lines you'd change)
3. **Proposed text** (≤2 lines)
4. **Why this should move the needle** (which quadrant it addresses)

### Eval edits — for Baseline assertions and grader-flagged critiques

Pull from the Step 5 grader feedback AND from your own analysis. Typical eval-fix patterns:

| Symptom | Edit pattern | Example |
|---------|-------------|---------|
| Both configs pass a shape check | Replace with a content/behavior check | "has a test" → "≥3 tests match `test_<fn>_<scenario>_<outcome>`" |
| Assertion passes on a trivial stub | Add a correctness assertion covering actual behavior | Add "the implementation actually raises ValueError for inputs with fewer than 7 digits" |
| Grader said "assertion X is trivially satisfied" | Adopt the grader's suggested tighter form verbatim | Paste grader suggestion into `expectations` |
| Important behavior has no assertion | Add a new assertion covering it | "no assertion checks mock audit" → add one |

For each eval edit, cite:
1. **Eval id + assertion index**
2. **Current assertion text**
3. **Proposed assertion text**
4. **Which grader feedback or quadrant drove the change**

## Sanity-check the plan

Before presenting to the user:

- **≤5 proposals total.** A focused next iteration beats a scattered one. If more than 5 ideas exist, rank by expected delta and drop the long tail.
- **Every proposal names a file path** (for target edits) or an assertion id (for eval edits). No abstract suggestions.
- **Mix of target edits and eval edits should reflect the quadrant distribution.** If most assertions are Baseline, the plan is mostly eval edits. If most are Unreachable, mostly target edits.
- **Flag any Regression prominently.** A regressing assertion blocks shipping the rule as-is — call it out at the top of the plan, not buried in a list.

## Present the plan in chat

Render as two compact sections:

```
### Quadrant summary
  Signal:       N assertions  (rule is working here)
  Baseline:     N assertions  (eval doesn't discriminate)
  Unreachable:  N assertions  (rule isn't cutting through)
  Regression:   N assertions  (rule is making things worse)  ← if >0, surface loud

### Proposed edits
  [Target] path/to/rule.md  lines X–Y
    Current:   "<quote>"
    Proposed:  "<quote>"
    Fixes:     Eval N assertion M (Unreachable)

  [Evals] eval-N assertion M
    Current:   "<quote>"
    Proposed:  "<quote>"
    Fixes:     Baseline — grader flagged as trivially satisfied
  ...
```

Keep edit blocks short. The goal is a user can read them in 60 seconds and make a decision.

## ⛔ Mandatory user question

After presenting the plan, you MUST ask the user which path to take. Do not silently apply edits. Options:

1. **Apply target edits and re-run** — modify the rule/skill, re-execute the existing evals to measure the lift.
2. **Apply eval edits and re-run** — modify `evals.json` (optionally re-running `--configs without` first to confirm the new assertions actually fail baseline), then run both configs.
3. **Both** — apply target and eval edits together. Only choose this when at least one proposal of each kind is strong; otherwise the lift becomes ambiguous (was it the rule change or the new assertion?).
4. **Stop** — plan is valuable but not acting now. Commit the plan to `benchmarks/<target>/runs/<ts>/improvement-plan.md` for later.

Exact prompt form (use `AskUserQuestion` if multiple options feel evenly weighted; otherwise a plain question is fine):

> "Which would you like to do next — (1) apply the target edits, (2) iterate on the evals, (3) both, or (4) stop and save the plan?"

## Apply & re-run

Once the user picks an action:

- **Target edits:** use `Edit` on the rule/skill file. After editing, re-run with the **same** `evals.json` so the delta is attributable to the target change. New outputs land in a fresh `runs/<ts>/` directory.
- **Eval edits:** `Edit` `benchmarks/<target>/evals.json`. If adding new assertions or tightening existing ones, run `--configs without --runs 1` first to confirm the new assertions fail on baseline (the falsifiability gate from Step 3). Only then run the full with+without pass.
- **Both:** apply edits, then run both configs. Expect a noisier delta; note in the follow-up report which lever changed.

After re-running, return to Step 5 to present the new numbers, then Step 6 again. Compare against the prior iteration's `benchmark.json` in the headline table so iteration-over-iteration lift is visible.

## Exit

- User picked 1, 2, or 3 → edits applied, re-run launched, loop back to Step 5 when it completes.
- User picked 4 → write `improvement-plan.md` into the current run directory, stop.
- Quadrant is ~all Signal and user is happy → commit snapshot, update `benchmarks/README.md`, stop.
