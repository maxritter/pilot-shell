## Step 3: Approve the Run, Settle the Mode

### 3.1 The one gate

<!-- CC-ONLY -->
When `PILOT_PLAN_APPROVAL_ENABLED` is not `"false"`, ask once with `AskUserQuestion`:

> N tasks and M criteria drafted for GOAL. Approve to start the build-judge loop, or tell me what to change.

Options: **Approve** / **Change the tasks** / **Change the criteria**.
<!-- /CC-ONLY -->
<!-- CODEX-START
When `PILOT_PLAN_APPROVAL_ENABLED` is not `"false"`, ask once with plain-text numbered options — **1. Approve**, **2. Change the tasks**, **3. Change the criteria** — then touch the approval-wait sentinel so the stop guard lets you end the turn for the answer:

```bash
touch "$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}/spec-approval-pending" 2>/dev/null || true
```

That sentinel is honoured only while `Approved: No`, which is exactly this moment. Delete it on resume, then act on their choice.
CODEX-END -->

When the toggle is `"false"`, skip the question entirely.

On approval — or immediately when the gate is off — set `Approved: Yes` in the Buildout. Leave `Status: PENDING`. The statusline flips from `goal` to `build`, and the stop guard now holds the session open until the run reaches a hand-back.

If they ask for changes, edit the Buildout and re-show it. Do not start building against tasks or criteria the user rejected.

**Approval is about the criteria, mostly.** The tasks will change during the run and everyone knows it; the criteria are the contract. If the user only glances at one list, make sure it is that one.

### 3.2 Sequential is the default and it stays the default

**One thread, no subagents.** Build the tasks, judge the criteria, close the gaps, judge again — all in this conversation. Do not ask the user which mode to use; there is nothing to ask about until 3.3's threshold is met, and asking every time taxes every small build.

A subagent starts **blind**. It re-reads the files, re-derives the context this thread already holds, reports a summary, and you read that summary back. For judging work you just built, that is routinely several times the tokens of judging it yourself — spent to buy separation you can mostly recreate by judging from the artifact. The loop's quality comes from the criteria, not from the org chart running it.

<!-- CC-ONLY -->
### 3.3 Escalate to ultracode — only at whole-project scale, and only with permission

Propose ultracode only when **all three** hold:

1. The work splits into **5+ distinct surfaces that each need their own build-judge loop** — not 5 tasks against one artifact.
2. Those surfaces can progress **without waiting on each other**.
3. Running them one after another would take hours, not minutes.

That is whole-project scale: migrating a codebase to a new framework, rebuilding an app's surface area from the ground up, an overhaul spanning many independent screens or services. A landing page with six sections is one artifact — sequential. A long grind is still sequential. If any of the three fails, run sequentially and say nothing about ultracode.

When all three hold, ask with `AskUserQuestion` and say plainly what you are asking for:

> This is <N> independent surfaces, each needing its own build-judge loop. Running them in parallel needs `/effort ultracode` — xhigh effort plus dynamic workflow orchestration, session-only. It spends substantially more tokens than the sequential default. Want it, or should I run this sequentially?

State the mechanics accurately: `/effort ultracode` is session-scoped, the user has to type it, and it needs dynamic workflows enabled in `/config`. Organizations can restrict xhigh, in which case the command refuses and sequential is the only path.

**Take no for an answer.** Cost, org policy, or plain preference are all sufficient. Drop to sequential immediately, do not re-argue it, and do not raise it again this session. A declined escalation is not a degraded run — sequential is the design, not the fallback.
<!-- /CC-ONLY -->
<!-- CODEX-START
### 3.3 Parallel surfaces

Codex has no ultracode equivalent. When the work splits into 5+ independent surfaces that each need their own build-judge loop, say so, then run them sequentially surface by surface — closing one surface's criteria before opening the next, so a partial run still leaves finished work behind rather than N half-built pieces.
CODEX-END -->

**Do not deflect large work to `/spec`.** Scale is not what `/spec` is for; an approved plan file and an ordered task list are. Big work escalates here, or runs sequentially.

**Done when:** `Approved: Yes` is in the Buildout and the mode is settled.
