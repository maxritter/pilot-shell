## Step 3: Lock the Contract, Settle the Mode

No gate lives here. This step turns the draft into the run's contract and starts the loop, in the same turn Step 2 finished in.

### 3.0 Pick up any Console annotations first

The Buildouts view has the same annotate surface as Specifications and saves automatically, so the user may have marked up the criteria while you drafted. Read `docs/builds/.annotations/<buildout-basename>.json`; a missing file or empty `planAnnotations` means nothing to do.

Otherwise fold every entry in — each carries `originalText` (the passage) and `text` (what they want) — then `rm -f` the file (direct deletion, since curl is blocked in several hook environments) and note "Incorporated N annotations from the Console."

**Annotations are how a running build gets steered.** With no approval gate, this file is the user's channel into a loop that does not stop to ask — so Step 4 re-checks it at the top of every round, not just here. An annotation that changes a criterion is a criterion change: record it in `## Round Log` with the before and after, exactly as 5.4 requires of any other one.

### 3.1 Lock it

Set `Approved: Yes` in the Buildout. Leave `Status: PENDING`. The statusline flips from `goal` to `build`, and the stop guard now holds the session open until the run reaches one of the four hand-back doors.

⛔ **`Approved: Yes` on a Buildout means the contract is locked, not that anyone signed off.** `/build` has no approval gate and does not read `PILOT_PLAN_APPROVAL_ENABLED` — that toggle governs `/spec`'s plan gate, where a human really does decide. Writing this field is yours to do, unprompted, every run. Do not ask first, do not wait for a reply, and do not report it as an approval.

**What the criteria are is now settled, and failing them is not a reason to change them.** They move only the two ways 5.4 allows — the user rewrote one, or one turned out to be undecidable as written — both recorded in `## Round Log` with the before and after. Never quietly, and never because they turned out to be hard.

<!-- CC-ONLY -->
### 3.2 Sequential is the default and it stays the default

**One thread. No subagents for building or judging.** Work the tasks, judge the criteria, close the gaps, judge again — all in this conversation. Do not ask the user which mode to use; there is nothing to ask about until 3.3's threshold is met, and asking every time taxes every small build.

A subagent starts **blind**. It re-reads the files, re-derives the context this thread already holds, reports a summary, and you read that summary back. For judging work you just built, that is routinely several times the tokens of judging it yourself — spent to buy separation you can mostly recreate by judging from the artifact. The loop's quality comes from the criteria, not from the org chart running it.

**Reviewers are the named exception, as a category** — they neither build nor judge, they look at axes the loop cannot see, and each runs once outside it: `build-review` before the first round (2.4) on whether the criteria are decidable at all, `changes-review` after the last (6.5) on the code behind the artifact. Both are gated by their Console toggles; neither ever runs inside a round.
<!-- /CC-ONLY -->
<!-- CODEX-START
### 3.2 Choose the smallest useful execution graph

Keep tightly coupled work in the main thread. Proactively delegate bounded, independent tasks or surfaces when the current Codex tool schema exposes agent tools and parallel work materially shortens the round or brings distinct expertise.

Give every agent non-overlapping file or surface ownership, the task objective, relevant constraints, and the evidence it must return. Tell it other agents share the checkout and it must not revert their work. Keep the Buildout ledger, integration decisions, criterion changes, and judge pass in the main thread. Verify an agent's completion from the shared files, diff, and fresh commands rather than from its success message alone.

Sequential execution remains appropriate when tasks share files, state, or one unresolved design decision. This is an engineering choice made from dependencies, not a user-facing mode question.
CODEX-END -->

<!-- CC-ONLY -->
### 3.3 Escalate to ultracode — only at whole-project scale, and only with permission

Propose ultracode only when **all three** hold:

1. The work splits into **5+ distinct surfaces that each need their own build-judge loop** — not 5 tasks against one artifact.
2. Those surfaces can progress **without waiting on each other**.
3. Running them one after another would take hours, not minutes.

That is whole-project scale: migrating a codebase to a new framework, rebuilding an app's surface area from the ground up, an overhaul spanning many independent screens or services. A landing page with six sections is one artifact — sequential. A long grind is still sequential. If any of the three fails, run sequentially and say nothing about ultracode.

⛔ **This is the one exception to "no interaction after Step 1.5", and only because it cannot be anything else:** `/effort ultracode` is session-scoped and the user has to type it — you cannot enable it, so proceeding without asking is not an option that exists. It is not a check-in, and it never becomes one for anything else.

When all three hold, ask with `AskUserQuestion` and say plainly what you are asking for:

> This is <N> independent surfaces, each needing its own build-judge loop. Running them in parallel needs `/effort ultracode` — xhigh effort plus dynamic workflow orchestration, session-only. It spends substantially more tokens than the sequential default. Want it, or should I run this sequentially?

State the mechanics accurately: `/effort ultracode` is session-scoped, the user has to type it, and it needs dynamic workflows enabled in `/config`. Organizations can restrict xhigh, in which case the command refuses and sequential is the only path.

**Take no for an answer, and take silence for one too.** Cost, org policy, plain preference, or an auto-continued question with no reply are all sufficient. Drop to sequential immediately, do not re-argue it, and do not raise it again this session. A declined escalation is not a degraded run — sequential is the design, not the fallback.
<!-- /CC-ONLY -->
<!-- CODEX-START
### 3.3 Parallel surfaces

When the work splits into independent surfaces, dispatch bounded worker agents with distinct ownership using the tools exposed in the current Codex schema. Run independent surfaces concurrently; preserve dependency order within each surface. Keep one integrated judge pass in the main thread after all workers have landed and their evidence has been checked.

Do not ask the user to enable a separate orchestration mode. If agent tools are absent, fall back to dependency-ordered work in the main thread without changing the goal or stopping to renegotiate the workflow.
CODEX-END -->

**Do not deflect large work to `/spec`.** Scale is not what `/spec` is for; an approved plan file and an ordered task list are. Big work escalates here, or runs sequentially.

**Done when:** `Approved: Yes` is in the Buildout, the mode is settled, and your next action is Step 4 — in this same turn.
