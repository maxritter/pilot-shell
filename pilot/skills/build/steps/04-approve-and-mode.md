## Step 4: Approve the Rubric, Choose the Mode

### 4.1 The one gate

<!-- CC-ONLY -->
When `PILOT_PLAN_APPROVAL_ENABLED` is not `"false"`, ask once with `AskUserQuestion`:

> Rubric ready — N criteria against BAR. Approve to start the build-judge loop, or tell me what to change.

Options: **Approve** / **Change the criteria** / **Change the bar**.
<!-- /CC-ONLY -->
<!-- CODEX-START
When `PILOT_PLAN_APPROVAL_ENABLED` is not `"false"`, ask once with plain-text numbered options — **1. Approve**, **2. Change the criteria**, **3. Change the bar** — then touch the approval-wait sentinel so the stop guard lets you end the turn for the answer:

```bash
touch "$HOME/.pilot/sessions/${PILOT_SESSION_ID:-${CODEX_THREAD_ID:-default}}/spec-approval-pending" 2>/dev/null || true
```
CODEX-END -->

When the toggle is `"false"`, skip the question entirely.

On approval — or immediately when the gate is off — set `Approved: Yes` in the rubric. Leave `Status: PENDING`. The statusline flips from `rubric` to `loop`, and the stop guard now holds the session open until every criterion passes.

If they ask for changes, edit the rubric and re-show it. Do not start building against criteria the user rejected.

### 4.2 Sequential is the default and it stays the default

**One thread, no subagents.** Build, judge, close the gap, judge again — all in this conversation. Do not ask the user which mode to use; there is nothing to ask about until 4.3's threshold is met, and asking every time taxes every small build.

A subagent starts **blind**. It re-reads the files, re-derives the context this thread already holds, reports a summary, and you read that summary back. For judging work you just built, that is routinely several times the tokens of judging it yourself — spent to buy separation you can mostly recreate by rejudging from the artifact. The loop's quality comes from the criteria, not from the org chart running it.

<!-- CC-ONLY -->
### 4.3 Escalate to ultracode — only at whole-project scale, and only with permission

Propose ultracode only when **all three** hold:

1. The work splits into **5+ distinct surfaces that each need their own build-judge loop** — not 5 sections of one artifact.
2. Those surfaces can progress **without waiting on each other**.
3. Running them one after another would take hours, not minutes.

That is whole-project scale: migrating a codebase to a new framework, rebuilding an app's surface area from the ground up, an overhaul spanning many independent screens or services. A landing page with six sections is one artifact — sequential. A long grind is still sequential. If any of the three fails, run sequentially and say nothing about ultracode.

When all three hold, ask with `AskUserQuestion` and say plainly what you are asking for:

> This is <N> independent surfaces, each needing its own build-judge loop. Running them in parallel needs `/effort ultracode` — xhigh effort plus dynamic workflow orchestration, session-only. It spends substantially more tokens than the sequential default. Want it, or should I run this sequentially?

State the mechanics accurately: `/effort ultracode` is session-scoped, the user has to type it, and it needs dynamic workflows enabled in `/config`. Organizations can restrict xhigh, in which case the command refuses and sequential is the only path.

**Take no for an answer.** Cost, org policy, or plain preference are all sufficient. Drop to sequential immediately, do not re-argue it, and do not raise it again this session. A declined escalation is not a degraded run — sequential is the design, not the fallback.
<!-- /CC-ONLY -->
<!-- CODEX-START
### 4.3 Parallel surfaces

Codex has no ultracode equivalent. When the work splits into 5+ independent surfaces that each need their own build-judge loop, say so, then run them sequentially surface by surface — closing one surface's criteria before opening the next, so a partial run still leaves finished work behind rather than N half-built pieces.
CODEX-END -->

**Do not deflect large work to `/spec`.** Scale is not what `/spec` is for; an approved plan file and an ordered task list are. Big work escalates here, or runs sequentially.

**Done when:** `Approved: Yes` is in the rubric and the mode is settled.
