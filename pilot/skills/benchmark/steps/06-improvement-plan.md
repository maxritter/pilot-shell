# Step 6 — Improvement plan

Step 5 reported what happened. Step 6 turns the quadrant breakdown into **specific edits the user can act on** — and asks which path to take. Never skip this step.

## Inputs from Step 5

You already have:

- `delta.pass_rate` and the verdict label (Strong / Moderate / Weak / Indistinguishable / Regression)
- Quadrant counts: `signal`, `baseline`, `unreachable`, `regression`
- Divergent assertions per eval, with evidence
- Grader critiques (if any)

Don't recompute these. Reuse them.

## Action priority — driven by the quadrant shape

The quadrant distribution tells you which lever to pull first:

| Dominant quadrant | First action | Why |
|---|---|---|
| **Signal** (≥60% of assertions) | **Ship.** Optionally expand coverage with sibling assertions or new evals. | The rule is doing its job; further tweaks risk breaking what works. |
| **Baseline** (≥40%) | **Fix the evals first.** Don't touch the rule until assertions discriminate. | A baseline-heavy run measures nothing — any rule edit's effect is unobservable. |
| **Unreachable** (≥40%) | **Fix the rule first.** Sharpen its cues, promote them earlier, upgrade soft language. | The rule isn't landing. Eval edits won't help when the rule never fires. |
| **Any Regression** | **Investigate the regression FIRST**, before any other edits. | A regressing assertion blocks shipping. Even one Regression must be addressed. |
| **Mixed** (no quadrant dominates) | **Per-assertion proposals**, ranked by expected delta. | Pick the highest-leverage 3–5 edits across both target and evals. |

## Translate non-Signal assertions into concrete edits

For every assertion NOT in the Signal quadrant, generate one specific proposal. Mechanical and observable — no platitudes.

### Target (rule/skill) edits — for Unreachable or Regression

Read the relevant section of the rule/skill file (`target.path`). Diagnose WHY it didn't land and pick one:

| Symptom | Edit pattern | Example |
|---|---|---|
| Rule is buried late in the file | Move the cue earlier, ideally into a numbered list in the first 40 lines | Promote "use `@pytest.mark.unit`" from prose to a checklist item |
| Rule uses soft language ("consider", "prefer") | Upgrade to mandatory (`⛔`, `MUST`, `MANDATORY`, `Required`) | `Consider adding @pytest.mark.unit` → `⛔ MUST decorate every unit test with @pytest.mark.unit` |
| Rule states the what but not the how | Add a code example showing the exact form | Add `@pytest.mark.unit\ndef test_...` block |
| Rule has competing guidance | Deduplicate or order by priority | Collapse two overlapping mocking sections |
| Rule teaches the wrong thing (Regression) | Pinpoint the misleading phrase and rewrite, or remove it | Rewrite "mock at the global module" → "mock at the import site" |

### Eval edits — for Baseline assertions and grader critiques

Pull from grader feedback AND your own analysis:

| Symptom | Edit pattern | Example |
|---|---|---|
| Both configs pass a shape check | Replace with a content/behavior check | "has a test" → "≥3 tests match `test_<fn>_<scenario>_<outcome>`" |
| Assertion passes on a trivial stub | Add a correctness assertion | Add "raises ValueError for inputs with fewer than 7 digits" |
| Grader said "trivially satisfied" | Adopt the grader's tighter form verbatim | Paste grader suggestion into `expectations` |
| Important behavior has no assertion | Add a new assertion covering it | Add mock-audit assertion |

## Proposal format — uniform, scannable

Every proposal cites a location, current text, replacement, and which quadrant it addresses. Keep each block ≤ 5 lines.

```
[TARGET]   path/to/rule.md  L42–L44
  Quadrant: Unreachable (eval-1 #3 — hypothesis PBT)
  Current:  "Property-based testing is encouraged for complex inputs."
  Propose:  "⛔ Property-based test required for parsers and serializers — use `hypothesis.@given`."
  Lever:    Soft language → mandatory; adds the exact tool name.

[EVALS]    eval-2 assertion #3
  Quadrant: Baseline (grader: "would pass for partially-mocked test")
  Current:  "pytest run completes in <1s wall time"
  Propose:  "subprocess.run mock asserts `called_once_with(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])`"
  Lever:    Loose timing check → exact call signature.
```

## Sanity-check the plan

Before presenting:

- **≤ 5 proposals total.** Rank by expected delta and drop the long tail. Focused next iteration > scattered one.
- **Every proposal names a file path or assertion id.** No abstract suggestions.
- **Mix reflects the quadrant distribution.** Baseline-heavy → mostly eval edits. Unreachable-heavy → mostly target edits.
- **Regressions surface at the top of the plan**, not buried in a list.

## Present the plan

Render in this exact order so the user always finds the same shape:

```
### Improvement plan

  Recommendation:  <single sentence — what to do first based on the dominant quadrant>

  Proposals (ranked by expected delta):

  1. [TARGET]  path/to/rule.md  L42–L44
       Quadrant: Unreachable (eval-1 #3)
       Current:  "..."
       Propose:  "..."
       Lever:    ...

  2. [EVALS]   eval-2 assertion #3
       ...

  Pre-shipping blocker (if any):
       <regression detail or "none">
```

Cap the body at ~25 lines so the user reads it in 60 seconds.

## ⛔ Mandatory user question

After presenting, you MUST ask which path to take. Do not silently apply edits. Use `AskUserQuestion` when the answer is genuinely uncertain; a plain question is fine when the recommendation is clear.

Options:

1. **Apply target edits and re-run** — modify the rule/skill, re-execute the existing evals to measure the lift cleanly.
2. **Apply eval edits and re-run** — modify `evals.json` (run `--configs without` first to confirm the new assertions actually fail baseline), then run both configs.
3. **Both** — only when at least one strong proposal exists in each bucket. Otherwise the lift becomes ambiguous (was it the rule change or the new assertion?).
4. **Stop** — write the plan to `benchmarks/<target>/runs/<ts>/improvement-plan.md` for later.

Phrasing:

> "Which would you like to do next — (1) apply target edits, (2) iterate on evals, (3) both, or (4) save the plan and stop?"

## Apply & re-run

- **Target edits:** `Edit` the rule/skill file. Re-run with the **same** `evals.json` so the delta is attributable to the target change. New outputs go to a fresh `runs/<ts>/`.
- **Eval edits:** `Edit` `benchmarks/<target>/evals.json`. For new/tightened assertions, run `--configs without --runs 1` first to confirm baseline still fails (the falsifiability gate from Step 3). Only then run the full pass.
- **Both:** apply edits, then run both configs. Note in the follow-up which lever changed so iteration-over-iteration attribution stays clean.

After re-running, return to Step 5 to present the new numbers. Compare against the prior `benchmark.json` in the headline so iteration lift is visible.

## Exit

- User picked 1/2/3 → edits applied, re-run launched, loop back to Step 5 when complete.
- User picked 4 → write `improvement-plan.md` into the run directory, stop.
- Quadrant is mostly Signal and user is happy → commit snapshot, update `benchmarks/README.md`, stop.
