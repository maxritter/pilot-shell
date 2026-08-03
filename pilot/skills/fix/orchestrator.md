---
name: fix
description: "The standard command for bugs — resolves one defect at its root cause with end-to-end proof it is gone. Use when something crashes, throws, returns wrong output, regressed, or behaves differently than it should, and when the user types /fix or reports a failing test. Stops cleanly and asks the user to re-invoke with /spec when the bug turns out to span multiple components or need an architectural change."
argument-hint: "<bug description>"
user-invocable: true
---

# /fix — Bugfix Workflow

Bugfix with TDD: investigate the bug, write the failing test, fix at the root cause, verify end-to-end, done. No plan file, no mid-flow approval gate, no separate verify phase.

```bash
> /fix "annotation persistence drops fields between save and reload"
> /fix "off-by-one in pagination at boundary"
> /fix "wrong default for max_retries"
```

**Always quick.** If investigation shows the bug is multi-component, architectural, or otherwise bigger than a quick fix, STOP cleanly and tell the user to re-invoke with `/spec`. Never switch lanes silently — `/fix` means quick, `/spec` means the full workflow. Honour the user's command choice.

---

## Iron Laws

```
1. NO FIXES WITHOUT ROOT CAUSE — traced to file:line, explained WHY.
2. RUN THE REPRO BEFORE THEORIZING — execute the reproduction FIRST and read its
   COMPLETE output: warnings, stderr, and log lines above the failure, not just
   the assertion. If the environment blocks the run, ask the user to unblock it.
3. NO CODE WITHOUT A FAILING REPRODUCING TEST — TDD.
4. FIX AT THE SOURCE — not where the error appears.
5. END-TO-END VERIFICATION IS MANDATORY — Step 4 runs the actual program and
   captures concrete evidence. Unit tests alone are never accepted as proof.
6. STOP WHEN OVER YOUR HEAD — multi-component / architectural bugs need /spec.
```

Three failure modes are common enough to name, because each one *feels* reasonable in the moment:

| Tempting move | Why it fails |
|--------------|--------------|
| "I can find it by reading the code — no need to run the test" | The failing run's output (warnings, stderr, swallowed-exception notices) often names the root cause outright. Running it first is faster than tracing. |
| "The repro can't run here, I'll reason it out instead" | An environment blocker is a user-involvement point, not a licence to speculate. Ask for the unblock, then run (Step 1.1). |
| "One more fix attempt" (after two failures) | Two failed quick-lane attempts means the lane is wrong, not that the third try is the charm. Bail to `/spec`. |

---

## Critical Constraints

- **No plan file.** All state lives in this conversation. After compaction, re-read the summary and resume.
- **Worktree mode** means: this session is *already* running inside a `.worktrees/spec-*` checkout. `/fix` never creates a worktree. Where Steps 2/6 branch on "worktree mode", that branch applies only when this is already true; otherwise treat every step as working-tree mode.
- **No `Iterations:` counter.** If the fix doesn't work after one re-attempt, stop and hand off to `/spec` — don't loop.
- **No approval mid-flow.** A single end-of-flow confirmation, and only when `PILOT_PLAN_APPROVAL_ENABLED` is enabled.
- **Stopping is success, not failure.** Recognising "this is bigger than a quick fix" is the right call; grinding on a multi-component bug in the quick lane is the failure.
<!-- CC-ONLY -->
- **Use `AskUserQuestion` for user questions** — it renders a structured form; don't fall back to plain-text numbered questions.
<!-- /CC-ONLY -->
<!-- CODEX-START
- **Use plain-text numbered options for user questions** — the `AskUserQuestion` tool isn't callable in Codex
- **Browser tools for E2E verification:** Use playwright-cli or agent-browser (Claude Code Chrome and Chrome DevTools MCP are not available in Codex)
- **The Codex plugin companion review is not available** — its broker is Claude-Code-only. The native `changes-review` custom agent still runs in Step 6.1 when the Changes Review toggle is enabled.
CODEX-END -->

---

## Bail-Out Triggers — Stop and Hand Off to `/spec`

Stop and tell the user to re-invoke with `/spec` when ANY of these holds after Step 1:

- **Confidence is Low** — you can't pin the root cause to `file:line`.
- Two quick-lane fix attempts have already failed.
- The fix has **non-trivial UI implications** warranting a recorded Verification Scenario (multi-step flow, regression-prone interaction, visual states worth capturing).
- The fix introduces **new abstractions** — a new module, public API, data structure, workflow phase, or a file outside the existing surface area.
- The fix requires **architectural redesign** — the existing pattern itself must change (swapping the storage layer, restructuring a state machine, replacing a contract). Adding a missing guard or field along an existing pattern is *not* a redesign.
- Net new production code is likely to exceed **~150 lines** (rough ceiling — if you can't size it yet, sketch the diff first).
- The change spans **independent components with unrelated logic** — e.g. a frontend bug bundled with an unrelated backend bug.

### The one distinction that decides most bail-outs

**Logic divergence, not file count.** Applying the *same* conceptual fix at N existing sites is one logical bug with multiple guard sites — the correct quick-lane move, however many files it touches. Example: adding the same iteration cap to both a verify orchestrator and a stop-guard hook, because they are two layers of one missing-budget defect.

Bail out when each site needs **different** logic — entry validation *plus* a business rule *plus* a storage migration, each non-trivial. That is `/spec` territory. Steps 1.3, 3.1, and 3.2 all defer to this paragraph rather than restating it.

**How to bail out:** summarise what you found (root-cause hypothesis, files involved, why it exceeds the lane) → tell the user "This bug needs the full workflow. Please re-invoke with `/spec '<bug description>'`" → do NOT invoke `spec-bugfix-plan` yourself; the user chose `/fix` → stop.

---

## Workflow — Six Steps, No Ceremony

Investigate → RED → Fix → Verify E2E → Quality → Finalise.
