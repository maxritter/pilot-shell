---
title: "How to Use Fable 5 in Claude Code: Best Practices"
description: "Fable 5 rewards a briefed outcome and punishes step-by-step prompting. Six practices for Claude Code, plus where Opus 5 still wins."
slug: fable-5-best-practices
date: 2026-07-25
authors:
  - max-ritter
tags:
  - guide
  - development
---

Fable 5 rewards a briefed outcome and punishes step-by-step prompting. Six practices for Claude Code, plus where Opus 5 still wins.

<!-- truncate -->

Most guidance on how to use Fable 5 in Claude Code is written for someone deciding whether to use it. This one assumes you already have it: a Max seat where it is sitting there available, or a workload you benchmarked and found Opus 5 short on.

That reader has a different problem. Fable 5 is not a faster Opus, and prompts tuned for a model you steer turn by turn will underuse it. It rewards being handed an outcome and left alone, and it punishes being walked through steps. Anthropic's own Claude Code documentation makes the same point in four bullets under a section titled "Work with Fable 5." The six practices below build on those, with the parts that only show up after you have run a few long sessions.

## How to Turn On Fable 5 in Claude Code

Fable 5 is not the default model on any plan. Select it explicitly:

```
/model fable              # alias
/model claude-fable-5     # pin the exact model ID
claude --model claude-fable-5   # per-session, at launch
```

There is also a `best` alias, which resolves to Fable 5 where your organization has access to it and the latest Opus model otherwise. That is the safer choice for a shared config, since it degrades rather than fails.

Three things stop the switch from working. Fable 5 requires **Claude Code v2.1.170 or later**, so run `claude update` if the picker does not list it. It is **not available under zero data retention**, where `/model` either omits the entry or shows it disabled. And on the Anthropic API the picker only lists Fable once the server reports it available for your organization, though typing `/model fable` checks availability directly, so the selection can succeed before the row appears.

Whether your plan covers it is a separate question with a longer answer. Fable 5 is included on Max and premium Team seats; Pro and standard seats need usage credits. See [whether your plan includes Fable 5](/blog/fable-5-usage-credits) for the eligibility and credit mechanics.

## What Actually Changes When You Switch

Five behavioral differences show up inside a Claude Code session. None of them are benchmark scores.

**Thinking is always on and cannot be turned off.** Fable 5 is the only current model whose adaptive thinking is documented as always on. Every other model lets you disable thinking to cut output tokens. On Fable that lever does not exist, and `MAX_THINKING_TOKENS` is not a substitute because adaptive-reasoning models ignore nonzero budgets.

**It investigates before acting.** Expect more reading and more tool calls before the first edit. On a task where you already know the answer this reads as slowness. On an ambiguous one it is the entire value.

**It verifies its own work.** Fable 5 checks its output with less prompting than smaller models, which changes what your prompt should contain. More on that in Practice 3.

**It is slower.** Fable 5 is the only current model Anthropic rates "Slower" on comparative latency, and there is no fast mode for it the way there is for Opus 5 and Opus 4.8.

**Its knowledge stops earlier than Opus 5's.** Fable 5's reliable knowledge cutoff is **January 2026**. Opus 5's is **May 2026**. The most capable model in the picker knows the world four months less well than the one below it.

## Practice 1: Brief the Outcome, Not the Steps

Anthropic's guidance is direct: "hand it the result you want and let it plan the path."

This is the practice everything else depends on, and it is the one most people get wrong by importing habits from a model they were steering. A step list caps Fable at your plan. An outcome lets it find a better one, which is what you are paying the premium for.

The difference in practice:

```
Weak:  Open src/auth/session.ts, extract the token refresh into a helper,
       then update the three call sites, then add a test.

Strong: Session tokens are being refreshed inconsistently across the auth
        module. Make refresh behavior identical everywhere it happens, with
        tests that would fail if the behavior diverges again.
```

The second brief contains no file paths and no sequence. It states an end condition and the constraint that matters. If the inconsistency turns out to live in four places rather than three, the first brief produces three fixed call sites and a bug, while the second produces four.

The same instinct explains the checkpoint pattern below. Judgment is worth more spread across a task than front-loaded into a plan you wrote before you knew what you would find.

## Practice 2: Hand Over the Whole Task, Then Leave It Alone

Anthropic's phrasing: "give it work you would normally break into pieces. It holds long sessions without losing the thread."

Splitting a task into five prompts you approve one by one is a habit built around models that lose the thread. It costs you twice here. You cap the work at your own decomposition, and every interruption re-reads the conversation so far, which is why the `/model` picker asks for confirmation when a switch happens after prior output.

Check in at points where new information would change the plan, not on a timer. A build failing, a test suite going red, or an assumption in the brief turning out false are all worth a turn. "How is it going" is not.

This is about check-in cadence inside one session, which is a different question from splitting work across several agents. That one has its own arithmetic, and it does not always come out in favor of splitting: see [when splitting work across agents costs more](/blog/multi-agent-orchestration-cost).

## Practice 3: Cut the Scaffolding Your Opus Prompts Needed

Anthropic is explicit: "it verifies its own work with less prompting, so reminders to test or check are usually unnecessary."

Prompt libraries accumulate defensive instructions. "Double-check before returning." "Add a final verification step." "Use a sub-agent to confirm." Each was earned against some model that needed it. On Fable 5 they compound with behavior the model already has, and you pay output-token rates for the duplication.

Strip these first:

- Verification reminders, since it already verifies
- Progress-update requests, since it reports as it goes
- "Think carefully before responding," since thinking is always on and cannot be raised this way

What is worth keeping is anything that constrains the outcome rather than the process: acceptance criteria, things that must not change, and the definition of done. Those are not scaffolding, they are the brief.

If you are migrating a prompt library, [how the same prompts behaved on Opus 4.7](/blog/opus-4-7-best-practices) is a useful contrast, because 4.7 rewarded exactly the explicit detail Fable 5 makes redundant.

## Practice 4: Put the Constraints in CLAUDE.md, Not the Prompt

A long autonomous session outlives any single prompt. Constraints stated once in a prompt decay across turns as context shifts; constraints in CLAUDE.md are present at the start of every request.

This matters more on Fable than on models you steer, because you have deliberately stopped intervening. The things that belong in the file are the ones you would otherwise repeat: which directories are off limits, what the test command is, what "done" requires, and which conventions are not up for renegotiation.

There is a second reason to care about that file here. Claude Code's first request of a session carries workspace context including your CLAUDE.md and your git status, which is also how a badly scoped file can cause a problem discussed in the limits section below.

Keep it structured and short. A sprawling file gets skimmed; a tight one gets followed. [Structuring CLAUDE.md so rules actually get followed](/blog/claude-md-mastery) covers the file itself in depth.

## Practice 5: Make Acceptance Criteria Machine-Checkable

If you are going to leave the model alone, something other than you has to decide when it is done. Claude Code ships that as `/goal`:

```
/goal all tests in test/auth pass and the lint step is clean
```

After each turn a small fast model checks whether the condition holds. If it does not, Claude starts another turn rather than handing control back, and the goal clears itself once the condition is met.

The constraint that decides whether this works: **the evaluator does not run commands or read files.** It judges only what Claude has already surfaced in the conversation. So "the code is well structured" is unusable, and "`npm test` exits 0" works, because running the tests puts the result in the transcript where the evaluator can read it.

One thing a goal does not do is change your permissions. In the default permission mode Claude still stops and asks before any tool call your settings do not already allow, and a test command is usually one of them. If the point is to set the goal and walk away, pair it with auto mode; otherwise you will come back to a prompt rather than a finished task.

Write conditions with one measurable end state, a stated way to prove it, and any constraint that must hold on the way there. Conditions can run to 4,000 characters, and adding a clause like `or stop after 20 turns` bounds a loop that might otherwise run long. `/goal` with no argument shows turns and tokens spent; `/goal clear` ends it early.

## Practice 6: Spend Fable on the Passes That Change the Answer

A long session is not one uniform block of work. It has passes where judgment decides the outcome and passes where the answer is already determined and just needs typing.

Fable earns its place on the first kind: the ambiguous investigation, the root-cause hunt, the architectural call with four defensible options. Anthropic points at the same set, calling out root-cause investigations, outage debugging, and architecture decisions as where the extra investigation pays off.

It earns nothing on the second kind. Applying a spec you already wrote, renaming across a directory, or updating config to match a decision already made produces the same output from a cheaper model, because the hard part happened before the pass started.

The practical version is to notice when a session crosses that line and stop paying for judgment you are no longer using. What a long session actually draws down is a separate topic covered in what a heavy session actually costs.

## Where Fable 5 Still Loses to Opus 5

Every other guide on this SERP is uncritically positive. Four things go wrong in real sessions.

**Stale knowledge on fast-moving libraries.** The January 2026 cutoff is four months behind Opus 5's. On a framework that shipped a breaking change since then, Fable will confidently write the old API. The fix is to put current documentation in context rather than trusting recall, which is the one place a verification instruction is still worth its tokens.

**The classifier fallback, which can fire before you type anything unusual.** Fable 5 runs safety classifiers for cybersecurity and biology content. When one flags a request, Claude Code re-runs it on another model and shows a notice: biology-flagged requests move to Opus 5, cybersecurity-flagged ones to Opus 4.8. That category split needs Claude Code v2.1.219 or later; before it, every flagged request re-ran on your provider's default Opus model. The non-obvious part is that the first request of a session carries your CLAUDE.md and git status, so a repository containing security or biology material can trip the classifier on that context alone, before you have asked for anything. Security work, CTF exercises, and biology-adjacent codebases hit this often.

Two controls are worth knowing. Run `/config` and turn off "switch models when a message is flagged" if you would rather decide each time; a flagged request then pauses and offers to switch or let you edit the prompt and retry. And in non-interactive mode, where no prompt can be shown, a flagged request simply ends the turn with a refusal.

**Latency, with no escape hatch.** Fable is the only current model rated "Slower," and fast mode does not support it.

**Always-on thinking.** On a task that does not need deliberation you cannot turn it down, and thinking bills as output.

None of that decides which model you should run. For that question, see choosing between Fable 5, Opus 5 and Sonnet 5.

## Effort Levels and Fable 5

Effort decides how long the model works, separately from which model answers. It is a real lever on Fable, with one Fable-specific caveat: because thinking is always on and adaptive-reasoning models ignore nonzero thinking budgets, effort is the control you have, and `MAX_THINKING_TOKENS` is not.

The ladder itself, what each rung costs, and when the top of it is worth using are covered properly in [the full Claude Code effort ladder](/blog/ultracode).

## Frequently Asked Questions

**Can you use Fable 5 in Claude Code?** Yes, on Claude Code v2.1.170 or later. Select it with `/model fable`. It is not the default on any plan.

**How to enable Fable in Claude Code?** Run `/model fable`, or `/model claude-fable-5` to pin the exact ID. If it is missing from the picker, run `claude update`.

**How to change Claude Code model to Fable 5?** `/model fable` mid-session, or launch with `claude --model claude-fable-5`. Session choices override your settings file.

**How to use Fable 5 Claude?** Brief an outcome rather than steps, hand over whole tasks, and remove verification reminders your older prompts carried. The six practices above cover it.

**What is the best way to use Fable 5?** Give it an ambiguous problem with a clear definition of done, then stop interrupting. Pair it with `/goal` so a condition rather than your attention decides when it is finished.

**What is Fable 5 best at?** Long-horizon work that does not fit one sitting: root-cause investigations, outage debugging, and architecture decisions where the investigation is the hard part.

**What makes Fable 5 better than Opus?** Sustained autonomy on long tasks and more investigation before acting. On most published evals Opus 5 is ahead, so treat the difference as workload-specific rather than general.

**Is Fable 5 the best AI model?** It is Anthropic's most capable widely released model, which is not the same as the best choice for a given task. Opus 5 wins most published head-to-heads at half the price.

**What should I use Claude Fable 5 for?** Work you would otherwise break into pieces, where the end state is checkable and the path is genuinely unclear at the start.

**What is Fable 5 best used for?** Ambiguous, long-running tasks with a verifiable outcome. It is a poor fit for mechanical passes where the decision is already made.

**When to use Fable 5 vs Opus?** Use Opus 5 by default and reach for Fable 5 on a workload you have measured it winning. Choosing between Fable 5, Opus 5 and Sonnet 5 works through it.

**Where to use Fable 5?** Claude Code, the Claude API, claude.ai, Claude Cowork, and the major cloud providers. It is unavailable under zero data retention.

## Next Steps

- Switch with `/model fable`, then set one `/goal` and let a full task run without interrupting it
- Move the constraints you keep retyping out of prompts and into CLAUDE.md
- Check [whether your plan includes Fable 5](/blog/fable-5-usage-credits) before a long session
- Compare against [how the same prompts behaved on Opus 4.7](/blog/opus-4-7-best-practices)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
