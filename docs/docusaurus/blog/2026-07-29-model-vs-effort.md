---
title: "Claude Code Model vs Effort: Which Setting to Change"
description: "Claude got it wrong. Model problem or effort problem? The diagnostic that tells you which dial to turn, plus the effort field on every subagent."
slug: model-vs-effort
date: 2026-07-29
authors:
  - max-ritter
tags:
  - guide
  - development
---

Claude got it wrong. Model problem or effort problem? The diagnostic that tells you which dial to turn, plus the effort field on every subagent.

<!-- truncate -->

Claude just got something wrong. You have two settings in front of you and no principled way to choose between them, so you do what everyone does: bump the model to the biggest one available, bump effort to `max`, and re-run. It works often enough to feel like a method.

It is not a method. It is paying for both dials because you cannot tell which one was the problem.

There is a diagnostic that tells you, and it comes from Anthropic's own framing. Lydia Hallie of the Claude Code team drew the distinction in [Choosing a Claude model and effort level in Claude Code](https://claude.com/blog/claude-model-and-effort-level-in-claude-code) (July 7, 2026): the model is the fixed weights, and effort is how much work Claude does on your request. **Knowing more versus trying harder.** Once you have that distinction the choice stops being a guess. This post is that diagnostic, plus the thing almost nobody knows about the effort dial: it is declarable per subagent, in frontmatter, and the field has been shipping for months.

## Two Dials, Two Different Jobs

Start with what each setting actually controls, because the popular mental model ("bigger is better, harder is better") flattens two genuinely different mechanisms into one slider.

**Model is the weights.** A model is a fixed artifact. Training finished, the weights froze, and nothing you type changes them. When you send a prompt you are running inference against a static object: what that object knows, what patterns it internalised, how it reasons about an unfamiliar API, all of that was set before you opened your terminal. Your prompt steers the model. It does not teach it.

This is also the cleanest way to understand hallucination. A model that does not know a fact does not have a gap where the fact should be. It has weights that produce a plausible continuation, and a confident wrong answer is a plausible continuation. Nothing in the mechanism distinguishes "recalling" from "generating something that reads like recall," which is why a knowledge gap surfaces as fluent invention rather than as an error.

**Effort is the budget.** Effort controls how much work the model does before it answers: how far it reasons, how many files it opens, how many alternatives it considers, how long it pushes before checking in with you. Same weights, same knowledge, different amount of thinking applied. The ladder runs `low`, `medium`, `high`, `xhigh`, `max`, and the full range is available on Opus 5, Sonnet 5, Opus 4.8, and Opus 4.7.

Defaults differ by surface, which is worth knowing before you reason about anyone's benchmark. **In Claude Code**, the default is `high` on every model that supports the setting, except Opus 4.7, which defaults to `xhigh`. **On the Claude API**, the default is `high` across the board, including 4.7, and you set `xhigh` explicitly to get it. The two are consistent rather than contradictory: Anthropic's guidance for Opus 4.7 is to start at `xhigh` for coding and agentic work, and Claude Code encodes that recommendation as its default while the raw API leaves it to you.

One breaking-change note worth having in your head before you script anything: on Opus 5, thinking cannot be disabled at `xhigh` or `max`. Requests setting `thinking: {"type":"disabled"}` at those levels return a 400.

The ladder itself, the `xhigh` versus `max` versus `ultrathink` versus `ultracode` distinctions, and the full model support matrix all live in [the ultracode guide](/blog/ultracode), which covers them properly. This post is about choosing between the two dials rather than about the rungs on one of them.

## Check the Context First

Before either dial, there is a step almost everyone skips, and it resolves more failures than both settings combined.

**Look at what Claude was actually given.**

An enormous share of "the model got it wrong" is really "the model was working from bad inputs." The file it needed was never in context. Your CLAUDE.md contained a rule that contradicted the request. The tool description was ambiguous, so it called the wrong one. A stale comment described behaviour the code stopped having six months ago. In every one of those cases, a bigger model and a higher effort level both produce a more elaborate, more confident version of the same wrong answer, because the input that caused the failure did not change.

The tell is specific: **if you are raising effort on a task that should not have needed it, the fix is almost always upstream.** A three-line change to a file the model already had should not require `xhigh`. When it does, something in the context is fighting the request. Fix the prompt, the CLAUDE.md rule, or the tool description, and the task usually completes at the level you started on.

This is not a preamble to the real advice. It is the first branch of the diagnostic, and it catches the majority of cases.

## The Diagnostic: Did It Not Know, or Did It Not Try?

Context checks out and the answer is still wrong. Now the question is answerable, and it has exactly two shapes.

**It did not know enough. That is a model problem.**

The signature is confident wrongness about something factual or structural. It invented an API that does not exist. It used a pattern from an older version of the framework. It misread how an unfamiliar system fits together and built confidently on the misreading. Crucially, more thinking would not have helped, because the thing it was missing was not derivable from what it had. It would simply have reasoned longer from the same wrong premise, and arrived somewhere more elaborate.

Raise the model.

**It did not try hard enough. That is an effort problem.**

The signature is a shallow but not wrong answer. It fixed the symptom and did not look for the cause. It edited one call site when four exist. It stopped at the first plausible solution without checking whether it held. It did not read the file it plainly needed to read. Everything it produced is consistent with the knowledge it has; there is just less of it than the task required.

Raise the effort.

The distinction is sharper than it looks, and it survives the awkward cases. Ask whether the failure would have been avoided by **more knowledge** or by **more work**. An invented API is a knowledge failure at any budget. An unexamined second call site is a work failure at any model size. When you genuinely cannot tell, that itself is information: it usually means the context is the problem after all, and you are back at the previous section.

## The Cost Curve Inverts, Which Is Why This Matters

If the two dials cost the same you could just max both and stop reading. They do not, and the way they trade off is counterintuitive enough to be worth stating.

On **routine work**, both model tiers get it right. The task was never hard enough to separate them. Here the larger model is pure overhead: you paid a premium for an outcome the smaller model was going to reach anyway, at a fraction of the price. This is the majority of what most sessions actually contain, and it is where model-tier discipline saves real money.

On **hard, multi-step work**, the arithmetic flips. The smaller model does not fail outright; it grinds. It takes an approach, discovers it does not hold, backs up, tries again, and burns tokens on every iteration of that loop. The larger model reaches the bar in fewer steps. Per token it is more expensive, and **per completed task it can easily be cheaper**, because it did not pay for six rounds of rediscovery.

So the rule is not "use the cheap model" and it is not "use the good model." It is that the crossover point is real, it sits somewhere in the middle of your workload, and the tasks on either side of it want different answers. For the fuller economics of that, including where delegation stops paying for itself, see cost optimization and [multi-agent orchestration cost](/blog/multi-agent-orchestration-cost).

### Capping Output Is Not the Same as Lowering Effort

One adjacent control that gets misused. `max_tokens` is the only hard cap in the system, and it is genuinely hard: the model stops mid-sentence when it hits the ceiling. That makes it a blunt instrument for cost control, because a truncated answer is usually worth less than nothing, and you pay for the truncated tokens either way.

The softer controls work better precisely because they are not caps. Stating a budget in the task ("keep this under about 200 words," "look at these three files and no more") is something the model is trained to respect, and it lets the model decide where to economise rather than having the cut land wherever the counter ran out. Lower effort does the same job structurally: less work, complete answers.

Reach for `max_tokens` as a safety rail against runaway generation, not as a dial you tune.

## Effort Is a Per-Subagent Field, and Almost Nobody Sets It

Here is the part that changes how you configure a fleet rather than how you configure a session.

Effort is usually discussed as a session-level control: you set it for yourself, for the work in front of you, and that is where every guide leaves it. But `effort` is **supported frontmatter on a subagent definition**, verbatim from the field table in [Anthropic's subagent docs](https://code.claude.com/docs/en/sub-agents):

> `effort` | No | Effort level when this subagent is active. Overrides the session effort level. Default: inherits from session. Options: `low`, `medium`, `high`, `xhigh`, `max`; available levels depend on the model

So a subagent file can pin both dials independently of whatever the session is running:

```
---
name: security-auditor
description: Use for security reviews, RLS policy validation, and OWASP compliance
model: opus
effort: high
---
```

Note the word **overrides**. This is not a default the session can talk it out of. A subagent declaring `effort: medium` runs at medium in a session running at `max`, which is exactly what you want and exactly what surprises people the first time they see it.

The field's history is a small lesson in how quietly capabilities land. Someone opened a feature request on the Claude Code repo asking for essentially this capability, [#31536, "Per-subagent effortLevel in agent frontmatter"](https://github.com/anthropics/claude-code/issues/31536), opened in March 2026 and since closed; what shipped is the `effort` field in the supported-frontmatter table today. Somebody wanted it, it shipped, and the request closed without the capability ever getting the announcement that would have told the rest of us.

That is the normal way a frontmatter field arrives: a line in a reference table, no release-note fanfare. Which is why it is worth reading the subagent field table occasionally rather than waiting to hear about it. Sixteen fields are supported and most people use two.

### Three Limits That Bite

**There is no per-dispatch effort override.** The Agent tool accepts a `model` parameter at call time, so you can downgrade a specific dispatch to Sonnet without touching the definition file. There is no matching `effort` parameter. Effort is fixed by the definition, full stop. The one exception is dynamic workflows, where `agent(prompt, {model, effort})` takes both per call, which makes harness code the only place you can vary effort dynamically.

This is a claim from the absence of a parameter, so verify it in your own session rather than taking it from a blog post: read the Agent tool's schema and look for the field. We did exactly that before publishing, and `model` is there while `effort` is not.

**A resumed subagent keeps its spawn-time settings.** Same behaviour as `model`. Editing frontmatter changes nothing about agents already running or already completed; it affects fresh spawns only. If you want a warm specialist at a different effort level, you are starting a new one. That interacts directly with the [persistent sub-agent](/blog/persistent-subagents) pattern, where the whole point is keeping the same agent alive across many rounds.

**Available levels depend on the model.** `xhigh` and `max` are not universal. Pinning a level the target model does not support is a configuration bug that will not announce itself in a way you enjoy finding.

## Why Medium Is the Subagent Sweet Spot

Having the field is one thing. Knowing what to put in it is the actual question, and the answer surprised us.

This framework ships 18 agent definitions. Until recently, **not one of them declared `effort`.** All 18 inherited whatever the session happened to be running, and most pinned `model: sonnet`. That meant a session at `max` silently ran every specialist at `max`, and a session at `low` silently ran them all at `low`. The fleet had no opinion about its own behaviour; it just absorbed the operator's.

All 18 now pin both dials: `model: opus`, and `effort: medium` on 17 of them, with the deep researcher at `high`.

Medium looks like an odd default when the session-level instinct is "more is better." The reasoning is about **what you want a subagent to do**, which is not the same as what you want from your main thread.

A subagent working a plan should execute the plan. Higher effort does not make it follow instructions more faithfully; it makes it explore more, reconsider more, and range further past the brief. That is genuinely valuable when you are the one steering and can accept or decline what comes back. It is expensive noise in a specialist that was handed a specification and asked to apply it, because the operator is not present in that context to judge the extra ideas, and the extra ideas arrive as completed work rather than as suggestions.

So the split we landed on: **creative judgment and beyond-scope thinking belong on the main thread, where a human is watching. Sub-agents run at medium and do the work at the scope requested.** The one exception in the fleet is the deep researcher, pinned to `high`, because its entire deliverable is the breadth of its exploration. Effort is the product there, not overhead.

The counterpart rule is on the model dial and points the other way: when a pass turns mechanical, applying a spec verbatim or churning through config, downgrade that dispatch to a Sonnet-tier agent instead of continuing on a frontier model. Model is per-dispatch overridable; effort is not. Use each where it can actually be used.

For which model belongs on which specialist, [sub-agent best practices](/blog/sub-agent-best-practices) owns that question. This post owns how hard the specialist works once you have chosen it. The two settings are independent, and picking well on one does not excuse guessing on the other.

## What the Claude 5 Generation Changes

Two shifts worth folding into the diagnostic.

**The knowledge floor came up.** The failures that used to be model problems on smaller models are frequently not model problems anymore. A capable current-generation model has fewer of the gaps that produced confident invention, which pushes more of your real failures into the effort column and the context column. If your instinct was calibrated on older models, it is probably over-reaching for the model dial.

**Over-verification became a real cost.** Anthropic's own guidance for Opus 5 is blunt about it: if your prompt contains explicit verification instructions, remove them, because they cause over-verification and removing them reduces wasted tokens with no loss in quality. High effort plus instructions to double-check everything compounds into a model that spends its budget re-confirming things it already established. Two controls pushing the same direction is not twice the diligence, it is twice the bill. The same thinking applies across your whole context layer, which we cover in [the new rules of context engineering](/blog/claude-5-context-engineering).

There is a live community view that deliberate effort selection on the Claude 5 models produces a large quality difference, and it is a topic worth watching. Stated honestly: that is community sentiment right now, not something we have measured, and this post is not going to launder it into a benchmark. The mechanism above is what we are confident in. Treat specific effort-level performance claims, including anyone's, as untested until someone shows the methodology.

## The Routing Rule

The whole thing collapses to a short sequence you can run in about thirty seconds.

1. **Look at the context first.** Was the needed file there? Does a CLAUDE.md rule contradict the request? Is a tool description ambiguous? Fix that and re-run before touching a setting. This resolves most failures.
2. **Then ask: did it not know, or did it not try?** Confident wrongness about facts or structure means model. Shallow but sound means effort.
3. **Change one dial.** Changing both teaches you nothing and bills you for the privilege. If you cannot tell which, that is a signal to go back to step one.
4. **On subagents, pin both in the definition.** `model` for what it knows, `effort` for how hard it works. Medium for specialists executing a plan, high only where exploration is the deliverable.
5. **Downgrade mechanical passes on the model dial**, because it is the only one you can change per dispatch.

The frame is Anthropic's and it is the useful part: knowing more versus trying harder. A model that does not know cannot be made to know by working longer, and a model that did not work hard enough does not need to be replaced. Almost every wasted upgrade is one of those two mistakes.

## Next Steps

- Read [the ultracode guide](/blog/ultracode) for the effort ladder itself and the model support matrix
- See model selection for which model fits which class of work
- Configure the effort field alongside the other 15 supported fields in custom agent definitions
- Understand where delegation stops paying in [multi-agent orchestration cost](/blog/multi-agent-orchestration-cost)
- Apply the same subtraction thinking to your context layer with [the new rules of context engineering](/blog/claude-5-context-engineering)
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
