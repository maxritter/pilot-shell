# Agent Gate Protocol

> Shared runbook for every Pilot workflow step that puts a decision to the user:
> plan approval (`spec-plan` 12, `spec-bugfix-plan` 6), the worktree merge-back
> (`spec-verify` 8.1.6, `spec-bugfix-verify` 4.5), the code-review sign-off that
> precedes `VERIFIED` (`spec-verify` 10, `spec-bugfix-verify` 6), `/build`'s single
> pre-work clarification round (`01-goal-and-scope` 1.5), `/fix` 6.2, and the
> `/prd` question steps.
>
> That list is the audit surface for "which gates are lane-safe" — a gate missing
> from it is a gate nobody checked. Add new ones here as they are written, and keep
> the merge and sign-off entries above in it: those two were left out once, and
> because a merge looks identical whether or not it was reviewed, nothing surfaced
> it until an orchestration lane had already merged unreviewed (issue #175).
>
> ⛔ `/build` has no approval, round-budget, or hand-back gate — it runs
> autonomously once the goal is clear. If you are following this file inside a
> `/build` run at any point after Step 1.5, you have invented a gate: go back and
> take one of the run's four hand-back doors instead.
>
> Skill steps reference this file instead of restating it. Read it when you reach
> a gate and **cannot emit `AskUserQuestion`**.

## When this applies

Check the capability, not the agent. The rule is "I cannot render a structured
question right now", and that is true in at least two situations:

- **Codex**, where `AskUserQuestion` is rewritten to plain-text options.
- **A Claude Code subagent** — an orchestration lane dispatched by a coordinating
  session. `AskUserQuestion`, `TaskCreate`, `TaskList` and `TaskUpdate` are all
  absent from a subagent's toolset.

Keying on "am I Codex" leaves the second case undefined, which is where the
damage happens: an agent that cannot ask, and believes it may not stop, resolves
the contradiction by answering the gate itself.

If you CAN emit `AskUserQuestion`, ignore this file and use the form.

## What the caller supplies

| Value | Meaning |
|---|---|
| `GATE_NAME` | What is being decided, in the user's terms ("Plan approval", "Round budget") |
| `OPTIONS` | The same options the `AskUserQuestion` form would have offered, verbatim |
| `SENTINEL_PATH` | The pause sentinel this gate uses, or `none` when the gate needs no stop-guard permission |

## The contract — both halves, always

### 1. Ask, in prose

State `GATE_NAME`, the context the user needs to decide, and every option from
`OPTIONS` as a numbered list. Same content as the form; only the rendering
changes. Then say plainly that you are waiting for their choice.

### 2. Yield, so the answer can arrive

Touch `SENTINEL_PATH` if the caller supplied one, then **end your turn**.

```bash
SESS_DIR="$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}"
mkdir -p "$SESS_DIR" && touch "$SESS_DIR/<sentinel-name>"
```

The stop guard honours the sentinel for the state that gate is in, so the session
is allowed to pause. Treat the user's **next message** as their answer. On resume,
remove the sentinel if the caller's step says to, then act on the choice.

## Why both halves, and never one

Each half alone fails, in opposite directions:

- **Asking without yielding** leaves the question stranded in a turn that keeps
  going. Nobody answers, and the gate is passed by momentum.
- **Yielding without asking** produces a lane that halts silently. Whoever is
  waiting — a human or a coordinating session — sees a turn end with no question
  in it and cannot tell an approval gate from a crash.

## ⛔ Never resolve the gate yourself

Not being able to ask is never grounds not to ask.

- **Never** write `Approved: Yes`, tick an acceptance criterion, or pick an option
  on the user's behalf because the form was unavailable.
- **Never** treat "I can reason about what they'd probably say" as an answer. For
  `/prd`'s elicitation steps the same rule reads: never invent the user's answer
  and carry on as though it were given.

This is the failure `spec_stop_guard.get_approval_sentinel_path` was written to
prevent — a literal agent, told it may not stop, editing `Approved: No -> Yes`
itself. A plan nobody approved is worse than a plan nobody wrote, because it
carries the appearance of review.

Under orchestration the cost is concrete: a coordinating session stands in for the
user at every gate. It can only answer a question that was actually emitted, and a
lane that self-approves removes the only chance to catch a bad plan before
implementation starts.

## If a stop is blocked anyway

The stop guard may still block when the sentinel does not apply to the plan's
current state. Do **not** answer your own gate to escape the block. Re-state the
question in one line, touch the sentinel again, and end the turn. A repeated block
is a guard/sentinel mismatch to report, never a licence to decide.
