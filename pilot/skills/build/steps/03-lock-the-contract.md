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

### 3.2 Choose the execution graph autonomously

The active Claude Code or Codex agent decides whether the run is sequential, delegated, parallel, or nested. Default to the current agent and add the minimum number of workers only for genuinely independent tasks where parallelism or context isolation materially helps. Do not fan out agents for tightly coupled work, duplicate perspectives, or checks the active agent can run directly. **Never stop the run to ask the user for permission to spawn subagents or to select an orchestration mode.** If agent tools are absent, continue directly.

Give concurrent writers non-overlapping ownership and the evidence they must return. Preserve task dependencies and verify agent-owned work from the shared files, diff, and fresh commands. The Buildout remains the common ledger regardless of which agent performs a task or judge pass.

### 3.3 Scale the graph without a user gate

For independent surfaces, launch only the minimum workers concurrently. Keep their assignments flat; allow a worker to delegate further only when the task genuinely requires a hierarchy that the coordinator could not express as separate bounded assignments. For tightly coupled work, stay in one thread. This is the active agent's engineering decision, not a permission or approval question.

**Do not deflect large work to `/spec`.** Scale is not what `/spec` is for; an approved plan file and an ordered task list are. Big work escalates here, or runs sequentially.

**Done when:** `Approved: Yes` is in the Buildout, the agent has chosen its execution graph, and the next action is Step 4 — in this same turn.
