---
title: "Context Engineering for the Claude 5 Family: The New Rules"
description: "Anthropic cut 80% of Claude Code's system prompt. We ran the same surgery on a production framework: 8,798 agent lines to 664. Here is the diff."
slug: claude-5-context-engineering
date: 2026-07-29
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Anthropic cut 80% of Claude Code's system prompt. We ran the same surgery on a production framework: 8,798 agent lines to 664. Here is the diff.

<!-- truncate -->

On July 24, 2026, Anthropic published something unusual: an article explaining how they deleted most of their own work. They **removed over 80% of Claude Code's system prompt** for Claude Opus 5 and Claude Fable 5, "with no measurable loss on our coding evaluations."

The article names six shifts in context engineering that made the deletion possible. It is a good article, and within a week there were at least eight write-ups summarising it. A ninth summary is worth nothing to you.

So we did the other thing. We ran the same surgery on this framework, a real production Claude Code setup, in the week the article landed, and this post is the diff. What came out, what stayed, and the single test that decided every line.

The headline numbers, all verifiable in this repo's git history:

| File | Before | After | Cut |
| --- | --- | --- | --- |
| `CLAUDE.md` | 260 lines | 165 | 37% |
| `.claude/rules/repo-primer.md` | 256 lines | 147 | 43% |
| 18 agent definitions | 8,798 lines | **664** | **92.5%** |

The agent fleet is the number that should get your attention. Eighteen specialist definitions went from an average of 489 lines each to an average of 37, and the fleet got measurably better at following plans. The largest single cut was the SEO specialist, from 951 lines to 91.

## Context Engineering vs Prompt Engineering

Worth ninety seconds on the distinction, because the two get used interchangeably and this article only makes sense if you separate them.

**Prompt engineering is what you write for one request.** It is specific. You know the task, you know the input, you can be precise about what you want back.

**Context engineering is everything else that arrives with that request**: the system prompt, your CLAUDE.md, loaded skills, memory, tool descriptions, rules files. Anthropic's framing of the hard part is exact: "Unlike a prompt, context is used generally across many requests, so it cannot be as specific. How do you build these general prompts and guidance for Claude, especially when you don't know what a user's prompt might be?"

That constraint is why context engineering has its own failure mode. A prompt that is slightly wrong costs you one bad response. A CLAUDE.md line that is slightly wrong costs you a small tax on **every request for months**, and because it is always present you stop seeing it.

## The Old Rules Were Real Advice, and They Expired

The thing most write-ups get wrong is treating the old practices as mistakes. They were not. They were correct engineering for the models that existed, and they stopped being correct when the models changed. Holding both halves is what makes the shift usable rather than just fashionable.

Anthropic's own example is the clearest one available. The old system prompt told Claude to default to writing no comments, never to write multi-paragraph docstrings or multi-line comment blocks (one short line maximum), and not to create planning, decision, or analysis documents unless the user asked for them, working from conversation context rather than intermediate files.

Their assessment of why that existed: "without these guardrails for older models, the comments Claude wrote would be incorrect in many cases and we had to accept this tradeoff." The rule was a trade. It bought protection against bad comments and it paid for that with being wrong whenever a user actually wanted documentation, or whenever complex code genuinely needed a multi-line block.

The replacement is one sentence:

> Write code that reads like the surrounding code: match its comment density, naming, and idiom.

That is the whole shift in miniature. **A rule that is right most of the time became a criterion that is right all of the time**, because the criterion delegates the judgment to something now capable of making it.

### The Six Shifts, Named

The article's structure, verbatim:

1. **Then: Give Claude rules. Now: Let Claude use judgement.**
2. **Then: Give Claude examples. Now: Design interfaces.**
3. **Then: Put it all upfront. Now: Use progressive disclosure.**
4. **Then: Repeat yourself. Now: Simple tool descriptions.**
5. **Then: Memory in CLAUDE.md files. Now: Auto-memory.**
6. **Then: Simple specs. Now: Rich references.**

Anthropic's diagnosis of what went wrong across all six is a single word: **overconstraining.** Reading transcripts of their own internal usage, they found "several conflicting messages in a single request," the system prompt saying `DO NOT add comments` while a skill said `leave documentation as appropriate` while the user asked for something else again. Claude resolves that. It just has to spend real capacity resolving it first.

That is the cost model to hold onto. **An unnecessary instruction is not free and it is not neutral. It is a conflict the model has to adjudicate before it can start.**

## The One Test That Decided Every Line

Six shifts do not tell you what to do with the specific line in front of you. We needed something mechanical, and this is what we used on every line of every file:

> **Would a strong model behave worse without this line?**

If no, delete it. That is the entire method, and it is brutal in practice because most lines fail it.

The test works because it separates the two things that look identical in a doctrine file. **Instruction that duplicates competence** ("verify your work", "write clean code", "think step by step", "check for errors") fails, because a capable model already does it and your line only adds a voice to reconcile. **Information the model cannot derive** ("this repo's meta.json files are generated, never edit them", "we deploy on Thursdays", "the operator prefers automation over manual UI steps") passes, because no amount of capability recovers a fact that is not in the repo.

Four categories survived across our whole doctrine layer:

- **Operator opinions.** Preferences a model cannot infer and would not guess. What we value when correctness and brevity conflict. When to ask versus proceed.
- **Project facts that surprise.** Gotchas, generated files, non-obvious build steps, the specific thing that broke last time.
- **Routing rules with real thresholds.** Decisions that need a stated boundary rather than a vibe.
- **Named integrations.** Which service, which env var, which endpoint.

Four categories died:

- **Persona theater.** "You are a senior engineer with 12+ years of experience."
- **Restated general knowledge.** Explaining React hooks to a model that knows React better than the person writing the explanation.
- **Emphasis scaffolding.** THINK HARD, CRITICAL, IMPORTANT, emoji section markers, all-caps imperatives.
- **Redundant verification demands.** Covered below, because this one actively backfires.

## The Verification Trap

One deletion deserves its own section because it is counterintuitive and it costs money.

Anthropic's guidance for prompting Opus 5 is blunt: if your prompt contains explicit verification instructions, **remove them.** Instructions like those "cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality."

Every framework accumulates these. "Verify your work before reporting." "Double-check the output." "Re-read the file to confirm the edit applied." Each one felt like diligence when it was written. Stacked, they produce a model that spends a large fraction of its budget re-confirming things it already established, and the reconfirmation is not free: you pay for the tokens, and you wait for them.

The same document flags two more habits to strip, under the headings "Controlling subagent spawning" and "Self-correction". What we would call **delegation inflation**: Opus 5 already delegates to subagents more readily than prior models, so instructions pushing it further overshoot. And what we would call **self-correction over-instruction**: the same over-prompting problem applied to a model that already corrects itself. Those two labels are ours, not Anthropic's; the underlying guidance is theirs.

We cut all three. The framework's validation doctrine now says the lead validates by default and a dedicated validator agent is assigned only at a declared high-reliability bar, production data mutation, security surface, irreversible operations. Before, it recommended a verification pass on essentially everything. The gates that matter (build, tests, typecheck) still run, because those are deterministic checks rather than instructions to be diligent. What went was telling a model to be careful.

## Worked Example: A Rule Replaced by a Criterion

Abstractions are cheap. Here is a specific rule we deleted and what replaced it.

**Before**, routing work to subagents was decided by size. The rule counted things: how many files a task touched, how long it would take, how many steps were involved. Cross a threshold, spin up the pipeline.

That rule is easy to follow and it is wrong constantly. A 40-file rename is enormous by file count and is one domain, one agent, one mechanical pass. A three-file change spanning a database migration, an API contract, and a frontend form is small by every count and genuinely needs specialists handing off to each other.

**After**, the criterion is domain count: how many specialist domains does this work genuinely span, and do those domains have to hand off to each other? Size is explicitly not a routing signal.

The interesting part is what the replacement required. A judgment criterion needs **calibration, not thresholds.** So the doctrine now carries one worked example of where the bar sits: research to establish an approach, then a frontend and a backend agent collaborating on a real feature, then a security auditor verifying it, then a content writer polishing the copy. Four domains, real handoffs, genuine sequencing. Below that bar, one agent.

That is the shape of the whole migration. You do not delete a rule and leave a hole. **You replace a threshold with a criterion, and you spend a few of the saved lines on calibrating the criterion.** Our routing section got shorter and more decisive at the same time.

## What Progressive Disclosure Actually Bought Us

Shift three is the one with real mechanics behind it, and those mechanics are covered properly elsewhere on this site: [the skills guide](/blog/claude-skills-guide) for how skills load on demand, and [the rules directory](/blog/rules-directory) for splitting always-loaded content into targeted files. Read those for the how.

What is worth adding here is the accounting, because progressive disclosure is what makes aggressive deletion safe rather than reckless.

Deleting a line is only correct if the information was not needed. Most of what we cut was not information at all, it was instruction, and instruction genuinely disappears. But some of it was real content that mattered occasionally, and that content did not get deleted. It **moved behind a pointer.** Verification procedure became a skill loaded when verification is happening. Domain protocol became a session-type file loaded when that session type is detected.

Anthropic did exactly this at their own scale: "we moved verification and code review into their own skills that Claude Code could selectively call." They extended it to tools as well, with deferred-loading tools whose full definitions are fetched via ToolSearch only when needed, so a large tool surface costs nothing until it is used.

The line that matters most for anyone auditing their own setup: "A common myth is that you want to make these a central repository for every known practice that you *might* run into, because Claude would not find it otherwise. Instead, consider having a tree of files that can be loaded at the right time."

**Claude will find it.** That assumption, that anything not always-loaded is effectively invisible, is what inflated every CLAUDE.md in existence, and it is no longer true.

## Anthropic Shipped a Command For This

Buried in the article and largely missed in the coverage: this is now partly automated.

> We've put these best practices in `claude doctor`; use the command **/doctor** in Claude Code to rightsize your skills, and CLAUDE.md files.

Run `/doctor` before you start cutting by hand. It will not make your judgment calls for you, and it does not know which of your lines encode operator opinion versus which restate the obvious. But it is a free first pass from the people who ran this migration at the largest scale anyone has, and starting from its output beats starting from a blank diff.

## The Rest of the Stack

Three shifts we applied more narrowly, with what actually changed.

**Design interfaces instead of giving examples.** Anthropic's finding is specific and slightly alarming if you have invested in example libraries: "giving examples actually constrains them to a certain exploration space." Their replacement is to make the interface itself carry the meaning. Their Todo tool illustrates it: typing status as an enum of `pending`, `in_progress`, `completed` tells Claude how the tool works without a single example, and one instruction about keeping a single item `in_progress` defines the behaviour they want.

Applied to a framework, the equivalent is that a well-named file in a predictable location teaches more than a paragraph describing when to use it. Our agent definitions stopped carrying example dialogues entirely.

**Simple tool descriptions instead of repetition.** Older models needed instructions repeated, and weighted content at the end of the context window more heavily than the start. That produced doctrine files that said the same thing three times in three registers. It is deletable now, and the correct home for tool guidance is the tool description rather than the system prompt.

Duplication is the easiest audit you can run on your own files, because it is mechanical. Search for your core rules and count how many times each appears. We found several stated in CLAUDE.md, restated in a rules file, and restated again in individual agent bodies.

**Rich references instead of simple specs.** The article's push here is that a reference should be as high-fidelity as you can make it, and that code is the highest fidelity available: "A spec may also be a detailed test suite, or a function in a different codebase that Claude might port." Their example is sharp, an HTML mockup beats a description of a design, and it beats a screenshot too.

The practical version: stop writing prose descriptions of things that could be artifacts. A failing test that reproduces a bug is a better spec than a paragraph about the bug.

## What We Would Warn You About

Two things we got wrong first, so you do not have to.

**Deleting is not the goal, and a line count is not a target.** The test is "would a strong model behave worse without this line," and some lines pass it emphatically. We cut a section documenting a build gotcha on the theory that it read like boilerplate, and put it straight back after a session rediscovered the gotcha the expensive way. Project facts are the highest-value lines in your CLAUDE.md and they look boring, which makes them exactly what an enthusiastic deletion pass destroys.

**Your old guidance does not become wrong retroactively.** If you published or wrote doctrine under the old rules, the honest frame is that the trade changed, not that you were mistaken. We had a section in [CLAUDE.md mastery](/blog/claude-md-mastery) arguing for 200 to 400 always-loaded lines. Rather than pretend it was never there, it now carries a dated amendment: the relevance criterion it argued for was right, the number it recommended was calibrated to a generation of models that has passed.

## Run This on Your Own Setup

The sequence that produced the numbers at the top of this post, in the order that works:

1. **Run `/doctor`** for a first pass on your skills and CLAUDE.md.
2. **Apply the one test line by line.** Would a strong model behave worse without this line? Be honest, and expect to delete more than half.
3. **Sort survivors into keep and move.** Keep what must be always-present. Move occasional-but-real content behind a skill or a rules file rather than deleting it.
4. **Hunt duplication across layers.** The same rule in CLAUDE.md, a rules file, and an agent body is three conflicting voices, not reinforcement.
5. **Strip verification and delegation nudges.** Keep deterministic gates, cut the instructions to be careful.
6. **Replace thresholds with criteria, and calibrate them.** Spend a few saved lines on one worked example of where the bar sits.
7. **Start with agent definitions if you have them.** They are where the fat is, they are individually low-risk, and 92.5% is not an unusual result.

If you want the tactical single-file version of this, [what to delete from your CLAUDE.md](/blog/what-to-delete-from-claude-md) is a delete list you can run against one file this afternoon. If you have a fleet of agent definitions, [what survives cutting an agent fleet](/blog/agent-definitions-what-to-cut) covers that specific surgery, which is where the largest single win is available.

## Next Steps

- Read the [context engineering fundamentals](/blog/context-engineering) if the concept is new to you
- Set up [progressive disclosure with skills](/blog/claude-skills-guide) so deletion does not mean loss
- Split always-loaded content with the [rules directory](/blog/rules-directory)
- Apply the same subtraction to [your CLAUDE.md](/blog/claude-md-mastery)
- Choose settings deliberately with [model vs effort](/blog/model-vs-effort)

**Source:** [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models), by Thariq Shihipar, Anthropic, July 24, 2026. Deletion guidance for Opus 5 from [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5).
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
