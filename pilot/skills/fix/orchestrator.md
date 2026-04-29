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

---

## Critical Constraints

- **No plan file.** All state lives in this conversation. If compaction happens mid-fix, re-read the conversation summary and resume.
- **No `Iterations:` counter.** If your fix doesn't work after one re-attempt, stop and tell the user to switch to `/spec` — don't loop.
- **No approval mid-flow.** Single end-of-flow confirmation only when `PILOT_PLAN_APPROVAL_ENABLED` is enabled.
- **Stopping is success, not failure.** Recognising "this is bigger than a quick fix" and bailing out is the right call. Wasting time in the quick lane on a multi-component bug is the failure.

---

## Bail-Out Triggers — Stop and Tell the User to Use `/spec`

You MUST stop and tell the user to re-invoke with `/spec` when ANY of these is true after Step 1 investigation:

- Bug spans **3+ files** or **2+ components** (e.g. frontend + backend, multiple services).
- Root cause is **architectural** (the pattern itself is wrong, not a single line).
- Fix requires **defense-in-depth at multiple layers** (entry validation + business logic + storage).
- **Confidence is Low** — you can't pin root cause to `file:line`.
- The fix has **non-trivial UI implications** that warrant a recorded Verification Scenario.
- Two quick-lane fix attempts have already failed.

**How to bail out** — do all four:

1. Summarise what you found (root cause hypothesis, files involved, why it exceeds quick-lane scope).
2. Tell the user explicitly: "This bug needs the full workflow. Please re-invoke with `/spec '<bug description>'`."
3. Do NOT invoke `spec-bugfix-plan` yourself. Honour the command boundary — the user chose `/fix`.
4. Stop.

---

## Workflow — Six Steps, No Ceremony

See `steps/01-investigate.md` through `steps/06-finalise.md`.
