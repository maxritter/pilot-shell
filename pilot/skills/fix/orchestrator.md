---
name: fix
description: "Bugfix workflow — investigate, RED test, fix, verify end-to-end, done. Standard command for bugs. Stops cleanly and asks the user to re-invoke with /spec when the bug exceeds this workflow's scope."
argument-hint: "<bug description>"
user-invocable: true
model: opus
---

# /fix — Bugfix Workflow

Bugfix workflow with TDD. Investigate the bug, write the failing test, fix at the root cause, verify the fix end-to-end, done. No plan file, no approval gate mid-flow, no separate verify phase.

```bash
> /fix "annotation persistence drops fields between save and reload"
> /fix "off-by-one in pagination at boundary"
> /fix "wrong default for max_retries"
```

**Always quick.** If investigation reveals the bug is multi-component, architectural, or otherwise larger than a quick fix, STOP cleanly and tell the user to re-invoke with `/spec`. Do NOT silently switch lanes — `/fix` means quick, `/spec` means the full workflow. Honour the user's command choice.

---

## Iron Laws

```
1. NO FIXES WITHOUT ROOT CAUSE — traced to file:line, explained WHY.
2. NO CODE WITHOUT A FAILING REPRODUCING TEST — TDD.
3. FIX AT THE SOURCE — not where the error appears.
4. END-TO-END VERIFICATION IS MANDATORY — Step 4 runs the actual program (UI: Claude Code Chrome / Chrome DevTools MCP / playwright-cli / agent-browser; CLI/API/library: real invocation) and captures concrete evidence. Unit tests alone are never accepted as proof.
5. STOP WHEN OVER YOUR HEAD — multi-component / architectural bugs need /spec.
```

### Common rationalizations

| Excuse | Reality |
|--------|---------|
| "Emergency, no time for process" | Systematic is faster than guess-and-check thrashing. |
| "Issue is simple, don't need to trace" | Simple bugs have root causes too — tracing one file is fast. |
| "I'll write the test after confirming the fix" | Tests written after pass immediately and prove nothing. RED first or it isn't TDD. |
| "One more fix attempt" (after 2 failures) | Two failed quick-lane attempts means the lane is wrong. Bail to /spec. |
| "Looks fixed, tests pass" | E2E evidence required. Unit-pass is not user-pass. |
| "Quick patch now, investigate later" | This IS the quick lane. If you can't trace it now, bail to /spec — don't patch blind. |

---

## Critical Constraints

- **No plan file.** All state lives in this conversation. If compaction happens mid-fix, re-read the conversation summary and resume.
- **No `Iterations:` counter.** If your fix doesn't work after one re-attempt, stop and tell the user to switch to `/spec` — don't loop.
- **No approval mid-flow.** Single end-of-flow confirmation only when `PILOT_PLAN_APPROVAL_ENABLED` is enabled.
- **Stopping is success, not failure.** Recognising "this is bigger than a quick fix" and bailing out is the right call. Wasting time in the quick lane on a multi-component bug is the failure.

---

## Bail-Out Triggers — Stop and Tell the User to Use `/spec`

You MUST stop and tell the user to re-invoke with `/spec` when ANY of these is true after Step 1 investigation:

- **Confidence is Low** — you can't pin root cause to `file:line` after Step 1.
- Two quick-lane fix attempts have already failed.
- The fix has **non-trivial UI implications** that warrant a recorded Verification Scenario (multi-step user flow, regression-prone interaction, visual states the user would want recorded).
- Fix introduces **new abstractions** — a new module, a new public API, a new data structure, a new workflow phase, or a new file that wasn't previously part of the surface area.
- Fix requires **architectural redesign** — the existing pattern itself must change (e.g., swapping the storage layer, restructuring a state machine, replacing a contract). Adding a missing guard or a missing field along an existing pattern is **not** a redesign.
- Net new production code is likely to exceed **~150 lines** (rough ceiling — if you can't size it yet, sketch the diff first).
- The change crosses **independent components with unrelated logic** — e.g., a frontend bug AND an unrelated backend bug bundled together. Coordinated changes that apply the **same conceptual fix** at multiple guard sites do NOT trigger this — that's a single logical bug, multiple sites. Example of allowed: adding the same iteration cap to both a feature-verify orchestrator and a stop-guard hook because they are two layers of the same missing-budget defect.

**Defense-in-depth nuance.** When the bug *is* "a guard is missing across N existing sites", fixing all N sites in one shot is the correct quick-lane move. That is not "defense-in-depth at multiple layers" in the bail-out sense — it's "one fix, applied consistently." Bail only when each layer needs **different** logic (entry validation + business rule + storage migration, each non-trivial).

**Multi-file is fine** when files share the same pattern. The trigger is **abstraction count and logic divergence**, not file count.

**How to bail out** — do all four:

1. Summarise what you found (root cause hypothesis, files involved, why it exceeds quick-lane scope).
2. Tell the user explicitly: "This bug needs the full workflow. Please re-invoke with `/spec '<bug description>'`."
3. Do NOT invoke `spec-bugfix-plan` yourself. Honour the command boundary — the user chose `/fix`.
4. Stop.

---

## Workflow — Six Steps, No Ceremony

See `steps/01-investigate.md` through `steps/06-finalise.md`.
