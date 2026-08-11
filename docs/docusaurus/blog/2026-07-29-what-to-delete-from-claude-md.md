---
title: "How Long Should Your CLAUDE.md Be? What to Delete"
description: "Every CLAUDE.md guide tells you what to add. After Claude 5, subtraction wins. The delete list, the one test per line, and what must never be cut."
slug: what-to-delete-from-claude-md
date: 2026-07-29
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Every CLAUDE.md guide tells you what to add. After Claude 5, subtraction wins. The delete list, the one test per line, and what must never be cut.

<!-- truncate -->

Every CLAUDE.md guide ever written tells you what to add. Sections to include, headings to use, a template to fill in. Follow enough of them and you end up with a 400-line file that loads on every single request and that you have not read in four months.

The higher-leverage move now is subtraction. This post is a delete list: what to cut, in what order, what to move rather than delete, and the two categories you must never touch. You can run it against one file this afternoon.

If you want the reasoning behind the shift, the six changes Anthropic named, and our framework-wide numbers, that is [the new rules of context engineering for Claude 5](/blog/claude-5-context-engineering). This post assumes you are convinced and want the list.

## How Long Is Too Long?

The honest answer is that **the line count is the wrong question**, and asking it is what produced the bloat in the first place.

Popular guidance has ranged from "under 60 lines or Claude ignores it" to "200 to 400 lines is the sweet spot." We argued for the second one on this site and have since amended it. Both are targets, and a target is something you fill.

The diagnosis behind the 60-line advice was wrong: Claude does not ignore long files. The diagnosis behind the 400-line advice was closer, since relevance genuinely does matter more than brevity, but it badly overestimated how much content is universally relevant.

Here is what actually costs you. Anthropic, reading transcripts of their own Claude Code usage, found "several conflicting messages in a single request," their system prompt saying `DO NOT add comments` while a skill said `leave documentation as appropriate` while the user asked for something else again. Claude resolves that. It spends capacity resolving it first.

So the real cost of a line is not the tokens. **It is that every instruction is one more voice the model has to reconcile before it starts.** A file of 300 mostly-unnecessary lines is not 300 tokens of waste, it is a standing argument the model walks into on every request.

**The working answer:** apply one test per line, then let the number be whatever it is. Most files land between 100 and 200 lines afterward. Ours went from 260 to 165. That number is an output, not a goal.

## The One Test

> **Would a strong model behave worse without this line?**

If no, delete it.

The test works because it separates two things that look identical on the page. **Instruction that duplicates competence** fails: a capable model already writes clean code, already checks its work, already reads the file before editing it, and your line adds only a voice to reconcile. **Information the model cannot derive** passes: no amount of capability recovers a fact that is not in your repo.

Read every line and ask it. Be honest about the answer, and expect to delete more than half.

## The Delete List

In order of how much you will cut, which is also roughly the order of how safe it is.

### 1. Persona and identity blocks

```
You are a senior full-stack engineer with 12+ years of experience building
production systems. You are meticulous, thoughtful, and take pride in your work.
```

Delete all of it. This does not make the model more senior, and over-constraining identity early has a documented tendency to make later, more specific instructions land less well. You are spending your most valuable context real estate on flattery.

### 2. Restated general knowledge

Any section explaining a public technology to the model. React hooks rules. What REST is. How Git branching works. Standard TypeScript conventions.

The model knows these better than the person writing the summary, and a compressed summary of something it knows well is strictly worse than nothing, because a lossy restatement can conflict with the accurate version it already has.

**The exception is where you deviate.** "We use Zustand, not Redux, and stores live in `src/stores/`" is a project fact and stays. "Here is how state management works" goes.

### 3. Verification and diligence instructions

```
- Always verify your work before reporting complete
- Double-check the output for errors
- Re-read the file after editing to confirm your change applied
- Think carefully before responding
```

This one is not merely neutral, it is negative. Anthropic's guidance for prompting Opus 5 is direct: if your prompt contains explicit verification instructions, **remove them**, because they "cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality."

Stacked diligence reminders produce a model spending its budget reconfirming things it already established. You pay for those tokens and you wait for them.

**Keep deterministic gates.** "Run `pnpm test` before reporting complete" is a specific checkable action and it survives. "Be careful" does not. The distinction is whether a machine could tell you complied.

### 4. Emphasis scaffolding

`IMPORTANT`, `CRITICAL`, `THINK HARD`, `YOU MUST`, all-caps directives, emoji section markers, bold on every third phrase.

Emphasis is a finite resource and shouting spends it. If everything is critical, nothing is, and a file where every rule is marked mandatory conveys no priority ordering whatsoever. Keep emphasis for the two or three things that genuinely break production, and let the rest be prose.

### 5. Duplication across layers

The most mechanical win available, and the easiest to miss because each copy looks fine alone.

Search your core rules and count occurrences across CLAUDE.md, your rules files, your skills, and your agent definitions. We found several rules stated in three places. That is not reinforcement, it is three voices that will eventually drift out of sync, at which point you have a genuine contradiction rather than redundancy.

One rule, one home.

### 6. Instructions conditioned on things the model cannot see

Subtle and worth a paragraph, because these read as careful and are dead on arrival.

"If you are running in agent-teams mode, deliver via SendMessage." "If this is a production deploy, get approval." "If the repo uses TypeScript, run typecheck."

An agent that cannot observe the condition cannot act on the instruction. We measured this: a mode-conditional line in agent definitions went **0 for 2**, while the same duty stated unconditionally in the dispatch prompt went **1 for 1**. Either give the model a way to check the condition, or move the instruction somewhere that already knows the answer. The full case is in [why conditional agent instructions silently fail](/blog/subagent-reported-done).

### 7. Aspirational process

Workflow sections describing how you wish you worked. Ceremony nobody performs. A six-step review process the team abandoned last spring.

If the process is not real, the model following it produces friction against how you actually work, and you will override it every time until you stop reading your own file.

## What to Move, Not Delete

Some content genuinely matters and genuinely does not belong in an always-loaded file. Deleting it loses real information. Moving it costs nothing.

**Anything needed occasionally but not always** belongs behind a pointer: a skill, a rules file, a session-type protocol. Deployment runbooks. Domain-specific conventions for one part of the codebase. A verification procedure used on one class of work.

Anthropic did precisely this at their own scale, moving verification and code review out of the system prompt and into skills that Claude Code calls selectively. The line worth quoting, because it names the belief that inflated everyone's file:

> A common myth is that you want to make these a central repository for every known practice that you *might* run into, because Claude would not find it otherwise. Instead, consider having a tree of files that can be loaded at the right time.

**Claude will find it.** Once you believe that, most of your file can move.

The mechanics of moving are covered properly elsewhere: [the skills guide](/blog/claude-skills-guide) for on-demand loading, [the rules directory](/blog/rules-directory) for splitting always-loaded content into targeted files, and [subdirectory CLAUDE.md files](/blog/subdirectory-claude-md) for content that only applies to one part of the tree.

## What You Must Never Delete

Two categories, and an aggressive first pass will destroy both because they look like boilerplate.

**Project facts that surprise.** Gotchas. Generated files that must not be hand-edited. The non-obvious build step. The thing that broke last time and why. These are the highest-value lines in your file and they read as mundane, which is exactly the problem. We cut a build-gotcha section on the theory that it looked like filler and restored it after a session rediscovered the gotcha the expensive way.

The test for this category: **could the model learn this by reading the repo?** If the answer is no, or only by reading fifteen files, it stays. "Never edit `meta.json` directly, it is generated from `blog-structure.ts`" is invisible in the tree until you have already broken something.

**Operator opinions.** Preferences a model cannot infer and would not guess. What you value when correctness and brevity conflict. When to ask versus proceed. Which of two valid approaches your team has standardised on. Anthropic's own framing of what a CLAUDE.md is for lands here: keep it light on description and "spend most of the tokens on gotchas inside of the codebase," and avoid stating "the obvious things Claude should know by looking at your file system or your repo."

Opinions and gotchas are the entire point of the file. Everything else is a candidate for deletion.

## Why Not Use a CLAUDE.md At All?

A fair question that comes up often enough to deserve an answer rather than a defensive one.

The case against is real: it is always-loaded, it goes stale silently, and a stale instruction is worse than no instruction because it actively misleads. Nobody gets a build error for a CLAUDE.md line that stopped being true.

The case for is narrower than it used to be and still decisive. **Two things have no other home.** Project facts a model cannot infer from the tree, and your opinions about how work should be done. Skills load on demand and cannot carry things needed on every request. Auto-memory records what emerges from work but does not encode a standing preference you have never had a session about.

So the answer is not to abandon the file. It is to shrink it to those two categories and let everything else live where it can be loaded conditionally. A 150-line CLAUDE.md of pure gotchas and opinions earns its place on every request. A 400-line one carrying a React tutorial does not.

The staleness problem is worth taking seriously, though: **anything you keep, you have signed up to maintain.** That is a second, quieter argument for a short file.

## Run It

Forty minutes, in this order:

1. **Run `/doctor`.** Anthropic shipped it for exactly this, and it gives you a first pass on your CLAUDE.md and skills for free.
2. **Delete categories 1 through 4 without agonising.** Persona, restated knowledge, verification nudges, emphasis scaffolding. These are safe, and they are usually 40% of the file.
3. **Hunt duplication across layers.** One rule, one home.
4. **Test every remaining line.** Would a strong model behave worse without this? Delete the noes.
5. **Sort survivors into keep and move.** Always-needed stays. Occasionally-needed goes behind a skill or rules file.
6. **Read what is left in one sitting.** If you cannot, it is still too long.
7. **Work for a week, then add back anything you actually missed.** You will add back less than you expect, and what you add back is worth knowing.

That last step is the one people skip and it is the one that makes the whole exercise safe. Deletion is reversible; git has your old file. The only real risk is deleting something load-bearing and never noticing, and a week of ordinary work surfaces that quickly.

## Next Steps

- Get the full reasoning and the six shifts in [the new rules of context engineering](/blog/claude-5-context-engineering)
- Read the structural guide to what a CLAUDE.md is for in [CLAUDE.md mastery](/blog/claude-md-mastery)
- Set up on-demand loading with [the skills guide](/blog/claude-skills-guide)
- Split always-loaded content using [the rules directory](/blog/rules-directory)
- Apply the same cut to agent definitions in [what survives cutting an agent fleet](/blog/agent-definitions-what-to-cut)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
