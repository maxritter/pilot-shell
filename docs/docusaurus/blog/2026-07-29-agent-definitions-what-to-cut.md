---
title: "Claude Code Agent Definitions: What to Cut, Keep"
description: "Eighteen agent definitions went from 8,798 lines to 664 and got better. What died: persona theater, THINK HARD, emoji. What survived, and why."
slug: agent-definitions-what-to-cut
date: 2026-07-29
authors:
  - max-ritter
tags:
  - guide
  - agents
---

Eighteen agent definitions went from 8,798 lines to 664 and got better. What died: persona theater, THINK HARD, emoji. What survived, and why.

<!-- truncate -->

Eighteen Claude Code agent definitions. 8,798 lines before, **664 after**. The fleet follows plans more reliably now than it did at thirteen times the size.

That is a 92.5% cut, and it was not a tidying exercise. It came out of applying one test to every line of every agent body, and the results were consistent enough across eighteen very different specialists that the pattern is worth publishing: some categories of agent-definition content died everywhere, and some survived everywhere.

Per file, so you can see it is not an average hiding one outlier:

| Agent | Before | After | Cut |
| --- | --- | --- | --- |
| seo-specialist | 951 | 91 | 90% |
| frontend-specialist | 762 | 38 | 95% |
| content-writer | 707 | 47 | 93% |
| n8n-builder | 697 | 79 | 89% |
| flutter-expert | 567 | 23 | 96% |
| growth-engineer | 555 | 46 | 92% |
| backend-engineer | 525 | 29 | 94% |
| deep-researcher | 504 | 21 | 96% |
| security-auditor | 502 | 31 | 94% |
| performance-optimizer | 485 | 24 | 95% |
| quality-engineer | 465 | 39 | 92% |
| debugger-detective | 448 | 25 | 94% |
| supabase-specialist | 434 | 27 | 94% |
| ios-expert | 401 | 24 | 94% |
| master-orchestrator | 360 | 27 | 93% |
| session-librarian | 227 | 22 | 90% |
| visual-explainer | 155 | 52 | 66% |
| code-simplifier | 53 | 19 | 64% |

The two smallest files cut least, which is the tell: **they had the least fat to begin with, not the least content.** Everything above 300 lines was carrying roughly the same ballast.

## Why Agent Definitions Bloat Worse Than Anything Else

Agent files are the worst offenders in a typical Claude Code setup, and there is a structural reason.

A CLAUDE.md gets read. You look at it, you feel its length, you eventually trim it. An agent definition is written once, in a burst of enthusiasm about what the specialist should be, and then never opened again. It runs invisibly, inside a sub-agent's context, and nothing about your daily work brings you back to the file.

It also feels free. The definition loads into the sub-agent's window, not yours, so the usual pressure to conserve does not apply. That intuition is wrong in a specific way: the cost is not the tokens, it is that **every instruction is a voice the agent has to reconcile before it starts working**. A 700-line definition is a 700-line argument the specialist walks into.

Anthropic named the same failure at their own scale, finding "several conflicting messages in a single request" in transcripts of their own usage, the system prompt saying `DO NOT add comments` while a skill said `leave documentation as appropriate`. The more you write, the more of that you generate.

## The Test

One question, applied line by line:

> **Would a strong model behave worse without this line?**

That is the whole method, borrowed from [the new rules of context engineering for Claude 5](/blog/claude-5-context-engineering), where the fuller reasoning lives. Applied to eighteen agent bodies it produced a clean split.

## What Died

### Persona theater

The single largest category, and present in every definition:

```
You are a senior full-stack engineer with 12+ years of experience building
production systems at scale. You have deep expertise across the modern web
stack and a reputation for meticulous, thoughtful work. You take pride in
your craft and never cut corners.
```

Every word of that is gone from all eighteen files.

The distinction that matters, because it is easy to over-correct: **a role statement is not a persona.** Our security auditor still opens with one line, and it is doing real work:

> You are a security auditor: vulnerability assessment, authentication and authorization review, RLS policy validation, and threat-informed code review. You think from the attacker's side: what could be reached, escalated, injected, or exfiltrated, and what evidence proves it cannot.

That sentence scopes the domain and, more importantly, sets a **stance** that changes what the agent looks for. "Think from the attacker's side" is a genuine reframe. "12+ years of experience" is not; there is no behaviour it produces that the role statement does not already produce.

The test separates them cleanly. Would the agent behave worse without "you think from the attacker's side"? Yes, it would audit like a reviewer rather than an adversary. Would it behave worse without "12+ years of experience"? No.

Two things we observed stripping ours, offered as field notes rather than as measured results: compliments and superlatives in a definition ("you are exceptional at", "world-class") changed nothing we could detect in output quality, and the definitions where persona ran longest were the ones whose later, more specific instructions were followed least consistently. The persona block is not merely inert. It competes.

### THINK HARD and friends

`THINK HARD`, `IMPORTANT`, `CRITICAL`, `YOU MUST`, `NEVER FORGET`, all-caps directives, emoji section markers.

Emphasis is finite. A file where every rule is marked mandatory conveys no ordering at all, and stripping it lets the two or three genuinely load-bearing rules read as load-bearing. This is also why the [skill activation hook](/blog/skill-activation-hook) moved from `CRITICAL SKILLS (REQUIRED)` to advisory phrasing: an imperative that the model must sometimes override is worse than a statement it can evaluate.

### Restated general knowledge

Our frontend specialist carried several hundred lines explaining React patterns, hooks rules, and component composition. Our backend engineer explained REST conventions. Our supabase specialist explained what row-level security is.

The model knows all of it better than the summary did. A compressed restatement of well-known material is worse than nothing, because a lossy version can conflict with the accurate one already in the weights.

What survived from those sections was only where we deviate from the default. Not "here is how state management works" but "we use this library, stores live here, and here is the gotcha that bit us."

### Worked examples and sample dialogues

Long example exchanges showing the agent how to respond. Sample outputs. Template conversations.

Anthropic's finding here is the most counterintuitive in the whole shift, and it applies directly: "giving examples actually constrains them to a certain exploration space." An example does not just demonstrate the shape you want, it **bounds** the shapes considered. For a specialist whose value is judgment, that is an active loss.

The replacement is interface design. A well-named skill in a predictable location, a clear description of what a good output must contain, a rubric. Say what the deliverable must satisfy rather than showing one instance of it.

### Redundant process ceremony

Multi-step protocols the agent was told to announce and follow. "First, acknowledge the task. Second, restate your understanding. Third, outline your plan. Fourth..."

This produces preamble, not quality. It also duplicates what a plan file or a dispatch prompt already carries, which puts two versions of the workflow in play.

### Verification stacking

"Verify your work." "Double-check before reporting." "Re-read the file to confirm the edit applied." "Validate your output against the requirements."

Anthropic's Opus 5 guidance is explicit that these should be removed, because they cause over-verification with no quality gain. Deterministic gates stayed, because a gate is a checkable action rather than an instruction to be diligent. "Run the focused security suite and the full web suite" survived. "Be thorough" did not.

## What Survived

Four categories, and between them they account for nearly all 664 remaining lines.

### Domain workflow with real specifics

Not "audit the code for security issues" but an ordered approach with named attack classes:

> Probe privilege-escalation paths explicitly: mass assignment on user-update endpoints, role and ban fields outside allowlists, layout-level gating mistaken for authorization.

Every item there is a specific thing that has actually gone wrong, in this codebase or one like it. That is not something the model derives from "be a good security auditor," because it is not general knowledge, it is accumulated incident history.

### Operator opinions

Standing judgments a model cannot infer and would not guess. From the code simplifier:

> Prefer readable, explicit code over compact code. Nested ternaries lose to if/else chains or switch statements; dense one-liners lose to two clear lines.

Both options are defensible. A capable model could argue either. **The line exists precisely because there is no correct answer to derive**, only a house preference, and encoding it is the entire reason the file exists.

The same file carries the guardrail against over-applying it, which is the other half of a real opinion:

> Do not over-simplify: merging too many concerns into one function, deleting helpful structure, or producing clever code that is hard to debug is a regression, not a refinement.

### Named integrations and pointers

Which skills to load and why:

> `auth` for session management, cookie behavior, OAuth flows, and admin gating; it carries incident-derived failure modes worth checking for explicitly.

This is progressive disclosure at the agent level, and it is what makes the 92.5% cut safe rather than lossy. The deep material did not get deleted. It **moved behind a pointer**, and the pointer costs three lines instead of three hundred. The agent loads it when the work calls for it.

### Proof standards

The most valuable surviving category, and the least obvious:

> Authorization findings must be proven from both sides: the permitted caller succeeds AND the logged-out, unverified, and wrong-role callers fail before any mutation. A gate tested only from the happy path is unverified.

That is not a reminder to be careful. It defines what counts as done, and it is falsifiable. Replacing vague diligence instructions with specific proof standards was the change that most improved actual output, because it converts "try hard" into "produce this artifact."

## The Shape of a Cut Definition

Nineteen lines, complete, as an existence proof:

```
---
name: code-simplifier
description: Use this agent for simplifying and refining code for clarity,
  consistency, and maintainability while preserving all functionality.
model: opus
effort: medium
---
 
You are a code simplification specialist: you refine recently modified code
for clarity, consistency, and maintainability while preserving its exact
behavior. All original features, outputs, and side effects must remain
intact; you change how the code does things, never what it does.
 
Scope: the code touched in the current session, unless explicitly asked to
go wider.
 
Apply the project's own standards first: read CLAUDE.md and the surrounding
code, and match their conventions for naming, module style, error handling,
and comment density rather than imposing a house style.
 
[four judgment-call bullets]
```

Role statement, scope boundary, deference to project conventions, judgment calls. No persona, no examples, no emphasis, no process ceremony.

Note the frontmatter, because the cut freed attention for something that matters more. Both `model` and `effort` are pinned. **The `effort` field is supported subagent frontmatter that almost nobody sets**, and it overrides the session level, which makes it the only way to say how hard a specialist should work. All eighteen definitions now pin both dials. That reasoning is its own post: [model vs effort](/blog/model-vs-effort).

## Reconciling With Persona Injection

This site has published the opposite advice, and it still ranks, so it deserves a straight answer rather than quiet deletion.

Human-like agents is a persona-injection playbook: experience claims, personality strings, "uncertainty signals expertise." It extends that doctrine to agent definitions directly.

**It was real advice, and it worked.** Persona injection was a genuine steering technique for models that needed steering. Telling a model to be a senior engineer measurably changed output when the alternative was a model with no strong default stance. That is not a mistake anyone should be embarrassed about; it is a technique that was correct for its generation.

What changed is the trade. Current models have a strong default stance and better judgment about when to apply it. The persona no longer supplies something missing, so all it does is occupy context and compete with your later, more specific instructions. Same technique, inverted value, because the thing it compensated for stopped being a deficiency.

The honest summary: **persona injection substituted for judgment the model did not have. Now it overrides judgment the model does have.** That page carries a dated note and a link here; it is not being deleted, because the history is genuinely useful for understanding why so many agent files look the way they do.

## Run This on Your Fleet

Agent definitions are the best place to start a context-engineering cut, for three reasons: the ratio is enormous, each file is individually low-risk, and you get a fast read on whether the method works before touching anything load-bearing.

1. **Delete the persona block.** Keep one role sentence, plus a stance line if it genuinely reframes the work.
2. **Delete every emphasis marker.** THINK HARD, CRITICAL, all-caps, emoji.
3. **Delete restated general knowledge.** Keep only where you deviate from the default.
4. **Delete worked examples.** Replace with a statement of what the output must satisfy.
5. **Delete verification nudges.** Keep named, checkable gates.
6. **Convert deep reference material into skill pointers.** Three lines instead of three hundred.
7. **Rewrite vague quality bars as proof standards.** "Prove both sides of the gate" beats "be thorough."
8. **Pin `model` and `effort` in frontmatter** while you are in the file.

Then dispatch the agent on real work and read the transcript rather than judging the output. That is how the counterintuitive results here were established: the fleet did not merely stay as good, it followed plans more closely, because there was less competing instruction to reconcile against the plan.

## Next Steps

- Get the full method and the six shifts behind it in [the new rules of context engineering](/blog/claude-5-context-engineering)
- See all 16 supported frontmatter fields in custom agent definitions
- Set effort deliberately per specialist with [model vs effort](/blog/model-vs-effort)
- Apply the same cut to your always-loaded file with [what to delete from your CLAUDE.md](/blog/what-to-delete-from-claude-md)
- Understand why reports need proof standards in [your subagent said it was done](/blog/subagent-reported-done)

Custom Agents
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** installs a structured workflow for agent work on top of Claude Code: `/spec` plans the change, runs implementation under TDD, and verifies with an automated reviewer pass. The orchestration loop most agent setups end up writing by hand.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
