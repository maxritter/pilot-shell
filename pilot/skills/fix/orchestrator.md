---
name: fix
description: "Structured bugfix workflow — resolves one defect at its root cause with end-to-end proof it is gone. Runs only when the user explicitly types /fix. Stops cleanly and asks the user to re-invoke with /spec when the bug turns out to span multiple components or need an architectural change. Not for making existing working behaviour better — that is /build."
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

**Not a bug?** If what the user actually wants is existing, working behaviour made *better* against some standard — faster, prettier, clearer, closer to a named reference — that is `/build`, not `/fix`. Say so and stop; do not run a root-cause investigation on a quality gap.

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
- **`/fix` owns its isolation.** It parses the same branch flags `/spec` does, creates the worktree, and owns the merge-back — see *Branch & Lane Setup* below. Where Steps 2/6 branch on "worktree mode", that branch applies whenever a worktree is active, whether `/fix` created it or the session was already inside one.
> **`$LANE_FLAG`** is `--lane <id>` when this run was dispatched as an orchestration lane, and **nothing at all** otherwise — the value the invocation parsed from its arguments. It keeps worktree and plan identity scoped to this lane; an unflagged call resolves a different identity and silently finds nothing (issue #174).

- **Detect a worktree with `pilot worktree detect --json <fix-slug> $LANE_FLAG`, never a path glob.** The old `.worktrees/spec-*` test keyed `/fix`'s isolation to a directory prefix another workflow produces; the resolver answers the same question without depending on the naming.
- **No `Iterations:` counter.** If the fix doesn't work after one re-attempt, stop and hand off to `/spec` — don't loop.
- **No approval mid-flow.** A single end-of-flow confirmation, and only when `PILOT_PLAN_APPROVAL_ENABLED` is enabled. It sits at 6.2, **ahead of** the commit and merge at 6.3 — one gate, placed in front of the step that cannot be undone. Do not add a second gate for the merge; move nothing behind it.
- **Stopping is success, not failure.** Recognising "this is bigger than a quick fix" is the right call; grinding on a multi-component bug in the quick lane is the failure.
<!-- CC-ONLY -->
- **Use `AskUserQuestion` for user questions** — it renders a structured form; don't fall back to plain-text numbered questions.
<!-- /CC-ONLY -->
<!-- CODEX-START
- **Use the runtime's structured user-input tool when available**; otherwise present numbered options in prose, end the turn, and wait for the answer
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

---

## Branch & Lane Setup (before Step 1)

**Parse the flags** off the argument string, then strip them from the bug description: `--worktree=yes|no`, `--new-branch`, `--lane <id>`. Default is `--worktree=no` — work continues on the current branch, exactly as before.

**Derive `<fix-slug>`** from the bug description: kebab-case, ~40 chars. It names the worktree, the branch, and every session artifact this run writes (Steps 1.1 and 6.1), so derive it once and reconstruct it the same way every time.

**Ask about branch isolation only when `PILOT_BRANCH_ISOLATION_ENABLED` is `"true"`** and the user supplied no flag — the same three options `/spec` offers, in the same order:

| Option | Flag | Behaviour |
|---|---|---|
| **Continue on current branch** (recommended) | `--worktree=no` | Works on the current branch as-is |
| New branch from default branch | `--new-branch` | Branches `fix/<fix-slug>` off `origin/<default>`, carrying your uncommitted work |
| Use worktree (isolated, squash-merged after) | `--worktree=yes` | Isolated checkout, merged back at Step 6.3, after the 6.2 approval gate |

When the toggle is `"false"`, ask nothing and use `--worktree=no`.

**For `--new-branch` or `--worktree=yes`,** read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/spec-branch-setup.md` and follow it with `<plan_slug>` = `<fix-slug>`, prefix `fix/`, and `<lane>` when one was supplied. Everything after this — the reproducing test included — is written inside the resulting checkout.

⛔ **`--lane <id>` implies `--worktree=yes` and fails closed.** Reject `--lane` combined with `--worktree=no` or `--new-branch`, and abort rather than continuing if the worktree cannot be created. A lane that quietly lands in the coordinator's checkout races every sibling's edits.

**`$LANE_FLAG`** stands for `--lane <id>` on a lane run and for **nothing at all** otherwise. **Every** `pilot worktree` call in this workflow carries it — `create`, `detect`, `diff`, `sync`, `cleanup` alike. The worktree directory and branch are keyed on `(slug, lane)`, so an unflagged `sync` resolves `spec/<slug>` rather than the `spec/<slug>-<lane>` the flagged `create` made, reports "not found", and the lane's finished work is stranded in an orphaned worktree that never reaches the base branch. Substitute it literally at each call site; shell state does not survive between Bash calls.

Probe once before the first flagged call and **abort if the binary predates the flag**, rather than dropping to an unflagged call that shares the coordinator's checkout:

```bash
~/.pilot/bin/pilot worktree create --help 2>&1 | grep -q -- --lane && echo LANE_OK || echo LANE_UNSUPPORTED
```

`/fix` registers no plan, so `register-plan` never appears here — the lane flag matters only for the worktree calls.

---

## Workflow — Six Steps, No Ceremony

Investigate → RED → Fix → Verify E2E → Quality → Finalise.
