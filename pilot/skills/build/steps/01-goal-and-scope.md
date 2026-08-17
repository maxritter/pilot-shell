## Step 1: Name the Goal, Scope the Work

**Goal of this step:** know enough to draft tasks and criteria in Step 2 with concrete pass conditions. Research that would not change a task or a criterion is waste — stop there.

⛔ **This step holds the run's only user interaction, and it belongs here or nowhere.** The goal is your directive: acknowledge it, settle anything that would change *what gets built* (1.5), and then build without pausing again. Everything after this step is decided by the criteria, the round ceiling, and the evidence in the file.

### 1.1 Restate the end state in one line

To yourself, not to the user. If you cannot say what the finished thing is in one sentence, the criteria will be mush and the tasks will be worse.

If the request is genuinely vague about *who it serves* or *what done means* — not just about how to build it — say so in one sentence and point at `/prd`. Do not run a loop against an idea that has not settled.

### 1.2 Spend a bounded research budget

**Typically 5–15 tool calls**, on exactly three things:

- **What already exists locally** that the build should reuse or match — the conventions, components, or prose style already in play.
- **What specifically "good" means here.** You need particulars to write criteria that name real dimensions. "Good typography" is what you write when you did not look.
- **A reference, if one exists.** See 1.3 — do not invent one.

<!-- CC-ONLY -->
For the local sweep, prefer `codegraph_explore(query="<area>")` for structure and `mcp__semble__search` for intent over raw Grep/Glob — one call returns the verbatim source plus the call path. Drop to Grep only to verify a result or find exact text in a known file.

For a reference on the web, the web MCP tools are the fetchers: discover them with `ToolSearch(query="+web-fetch fetch")` and `ToolSearch(query="+web-search search")`. Built-in `WebFetch`/`WebSearch` are hook-blocked. For a live page whose *appearance* is the reference, screenshot it with the Chrome tools rather than reading its DOM — you cannot judge typography from HTML.
<!-- /CC-ONLY -->
<!-- CODEX-START
For the local sweep, use `codegraph_explore` when the area is structural or the entry point is unclear; for named files, docs, config, or UI copy, read them directly or use Semble. For a reference on the web, use the current Codex tool schema's web access, or the Pilot web MCP tools if they are listed (`tool_search(query="+web-fetch fetch")`). For a live page whose appearance is the reference, use playwright-cli or agent-browser to capture it — you cannot judge typography from HTML.
CODEX-END -->

**Widen to ~30 calls when** the domain is unfamiliar, the goal names a stack or API you have not verified, or a reference is a codebase you would have to read to compare against.

<!-- CC-ONLY -->
**One `Explore` subagent is allowed here, and only here** — when the sweep is genuinely wide (many directories, unknown naming, several unfamiliar references). One, in Step 1 only, never inside the loop. Pass `model` explicitly; do not inherit the session model.
<!-- /CC-ONLY -->
<!-- CODEX-START
When the sweep has two or more independent questions or surfaces, use the agent tools exposed in the current Codex schema to investigate them in parallel. Keep each assignment bounded, read-only, and explicit about the evidence it must return. Give agents distinct ownership, then use their results without repeating the same exploration in the main thread.
CODEX-END -->

### 1.3 A reference is optional

Some goals have a real thing to sit beside: a competitor's page, a named author's post, the pre-migration version of a screen. Others do not, and forcing one is worse than having none — a reference nobody can obtain is a comparison the judge invents, and an invented comparison passes everything.

**Use a reference only when all three hold:**

- **Named.** A specific thing. "Stripe's pricing page" works; "award-winning SaaS sites" does not.
- **Obtainable.** You can fetch it, screenshot it, read it, run it, or open it — and you do so *now*, in this step, not later.
- **Comparable.** Both artifacts can sit side by side and someone can pick one. If you cannot picture the A/B, it is not a reference.

| Goal | Reference that works |
|---|---|
| Website, app, UI | A named product's live page, screenshotted at the same viewport |
| Writing | A named author's published piece, same length and format |
| Code, tooling | A named repo's implementation, plus its benchmark or test suite |
| A rewrite or migration | The **existing** artifact, captured before you touch it |

**If the user named one, use it.** If they did not and a genuine A/B exists, **pick it yourself** — take the most useful candidate you can actually reach, name it in the Buildout, and say in one line which you took and why. A reference is a measuring stick, not a design decision; a run that stalls to have one chosen for it has spent a user's attention on the cheapest question it will face all session.

Take it to 1.5 only when the candidates would send the build somewhere genuinely different — matching a minimalist documentation site versus a maximalist marketing page is a different artifact, not a different yardstick.

**When there is no reference, say so in one line and move on.** The criteria carry the standard by themselves. Do not manufacture a comparison to fill the field.

### 1.4 Capture the reference so later rounds cannot drift

Only when you have one. Recalling a reference is how the comparison quietly becomes "whatever we already made", so pin it to something re-openable and record *how* in the Buildout:

- A URL plus the exact fetch or screenshot command.
- A file path under the project (a screenshot, a saved page, a reference doc).
- A command that reproduces it (`git show <ref>:<path>`, a benchmark invocation, a binary to run).

For a rewrite, capture the "before" **now** — once you start editing, the old version stops being obtainable.

### 1.5 Grill the goal until you can write criteria against it

This is `/build`'s only user interaction, and it is a real interrogation, not a courtesy check. Everything downstream runs unsupervised against the criteria you are about to write — so a vague goal here does not produce a vague result, it produces four rounds of confident work aimed slightly wrong.

**The stopping condition is objective, and it is not "the user seems happy":**

> 1. Can you name the **oracle** — the one observable signal that would show this outcome is actually true?
> 2. For every criterion you intend to write, can you name — right now — the specific evidence that settles it pass or fail?
> 3. Can you name the **misfire** — how this run could pass every criterion and still be the wrong thing?

While any answer is no, you do not understand the goal well enough to build it. Keep asking. Once all three are yes, stop asking and build; more questions past that point buy nothing and cost the user's attention.

**This is the step where Pilot earns what `/goal` leaves to you.** A native `/goal` condition is only as good as the sentence the user typed. `/build` writes that condition itself, so it has to do the work of understanding first.

#### Calibrate the depth to the goal you were handed

| The goal you got | What this step is |
|---|---|
| **Sharp** — end state unambiguous, yardstick implicit but obvious, you can already name every criterion's evidence ("port these three screens to React, same behaviour, same tests green") | **Ask nothing.** Say in one line what you took it to mean, and build. |
| **One fork** — mostly clear, with a single branch point that changes what gets built | **One targeted round.** Ask about the fork, not around it. |
| **Weak** — "better", "nicer", "modernise", "make it good", "clean this up", with no stated yardstick | **Grill properly.** Up to two rounds, and expect to use both. This is the case the step exists for. |
| **Still vague about who it serves or what done means** after a round of grilling | **Not a build.** Say so in one sentence and point at `/prd` (1.1). Do not loop against an idea that has not settled. |

#### What to grill about

Five things determine whether a decidable criterion can exist. Ask about the ones the goal left open, in this order of damage:

1. **The oracle** — the *one* observable signal that proves the user's outcome is actually true. Not the standard in the abstract: the thing you could show them. A test suite going green, a benchmark number, a walkthrough of the flow, a reader restating the mechanism, a released artifact. **No oracle, no serious build.** "Better than now" is not one — better *at what*, shown *how*. Weak goals fail here first, and everything else on this list is downstream of it.
2. **The observable end state.** What is true when this is done that is not true now? If the answer is only a feeling, keep pulling until something observable falls out.
3. **The audience.** Who uses this, and what changes for them? Drives half the criteria on anything user-facing.
4. **What must not change.** Invariants, data that has to survive, behaviour that must stay identical, things explicitly out of scope. Cheap to ask, expensive to discover in round three.
5. **Where the work lands.** When `PILOT_BRANCH_ISOLATION_ENABLED` is `"true"` and no `--worktree` / `--new-branch` flag was supplied (2.2a): **Continue on current branch** (recommended) · **New branch from default branch** · **Use worktree (isolated, squash-merged after)**.

⛔ **Do not grill about *how* to build it.** Which library, which pattern, which file layout, which naming, whether the tasks look right, whether to start — all of that is the judgement the goal delegated to you, and asking gives the work back to the person who handed it over.

#### Name the misfire yourself — do not ask about it

Before you stop asking, answer this on your own: **how could this run pass every criterion and still be the wrong thing?**

That is the misfire, and an autonomous run is exactly the shape that finds one. A landing page that scores well on every measurable axis and reads as a template. A migration where every screen works and the one flow the team actually uses regressed. A rewrite that is faster and lost the behaviour nobody wrote down.

Name it in one sentence, and make sure at least one criterion would **catch** it. If none would, that is a criterion you are missing, not a risk you have accepted. Record it in the Buildout so the judge and the report both carry it.

#### The shape of the questions

**A grilling is discovery, not a form.** The point is to help the user find what they mean, which rarely survives contact with a single batch of questions. So each round has a shape:

```
I read this as: <one sentence — the outcome as you now understand it>.
One thing this could miss: <a blind spot, unstated choice, or success dimension they have not named>.

<the one or two questions that matter most right now, with concrete options>
```

Reflecting the goal back is half the value — a user corrects a wrong reading faster than they answer an abstract question, and naming a blind spot surfaces requirements that a form would never have asked for.

- **Concrete options, never open prompts.** Two to four options per question, each a real answer someone can pick, recommended one first. "What do you mean by better?" is a worse question than three named readings of "better" and an *other*.
- **One or two questions per round, not four.** You are meant to learn something from the answer and let it choose the next question. A round that asks everything at once cannot do that.
- **Ask what you cannot find out.** Spend the research budget first (1.2) — a question you could have answered with three tool calls is a question that should not have been asked.
- **Each round must be opened by the last one's answers.** New ground the answers revealed, never the same ground asked again in different words.
- ⛔ **Three rounds is the hard ceiling.** Still unable to name the oracle after three? The goal is not underspecified, it is unformed — say so and point at `/prd`.

<!-- CC-ONLY -->
Render each round with `AskUserQuestion` — one call per round, all that round's questions in it. **When you cannot** — on Codex, or as a Claude Code subagent running this Buildout as an orchestration lane — read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/agent-gate-protocol.md` and follow it with `GATE_NAME` = `Build scope`, `OPTIONS` = your questions and their options, `SENTINEL_PATH` = `none`. No sentinel is needed: the Buildout does not exist yet, so nothing is registered and the stop guard is not holding this session.
<!-- /CC-ONLY -->
<!-- CODEX-START
Present each round as one plain-text numbered list with its options and wait for the answer. No pause sentinel is needed: the Buildout does not exist yet, so nothing is registered and the stop guard is not holding this session.
CODEX-END -->

#### Record the answers, then stop asking

Write what the grilling settled into the Buildout's `## Summary` — the oracle, the end state, the constraints, anything ruled out, and the misfire — in the user's own terms where they gave them. The criteria are drafted from these answers in Step 2, the judge rules against them for the whole run, and the hand-back report quotes them back. An answer that lives only in the conversation is gone at the first compaction.

⛔ **Then build.** Do not confirm the answers back for a nod, do not return with follow-ups after Step 2, do not restate the plan for approval. The next thing the user sees is Step 2.5's summary of what you drafted, and after that the hand-back.

#### When you cannot ask

**`PILOT_PLAN_QUESTIONS_ENABLED` is `"false"`** → ask nothing at all. Take the reading of the goal you would have recommended, use `--worktree=no`, record the assumption in `## Summary`, and say in one line what you assumed. If you cannot name the oracle, say *that* instead and point at `/prd` — with questions switched off, inventing a standard and then judging against your own invention is a closed loop that certifies itself.

**A question auto-continues without an answer** ("No response after Ns") → take the recommended option, say which in one line, and build. Do not re-ask, and do not stall: an autonomous run waiting on an absent user is the failure this workflow was rebuilt to remove. Name the assumption again in the hand-back report, where they will read it.

**Done when:** you can name the oracle, the settling evidence for every criterion you intend to write, and the misfire; any reference has been obtained once by you with its re-obtain command written down; and what the grilling settled is in `## Summary`.
