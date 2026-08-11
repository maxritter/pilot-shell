---
title: "Model Stacking: Give Claude Code a Second Set of Eyes"
description: "A second AI model that doesn't share Claude's blind spots catches more bugs than Claude reviewing itself. Here's how model stacking works."
slug: model-stacking
date: 2026-07-04
authors:
  - max-ritter
tags:
  - tools
  - orchestrators
---

A second AI model that doesn't share Claude's blind spots catches more bugs than Claude reviewing itself. Here's how model stacking works.

<!-- truncate -->

You ask Claude Code to review its own work. It just finished a 400-line refactor, so you type the obvious follow-up: "look this over, anything wrong?" It reads its own diff, thinks for a few seconds, and tells you it looks solid, edge cases handled, ship it. Then a null check it quietly removed takes down staging two hours later. Claude was not lazy. It read the diff carefully. It just read it with the same assumptions it used to write it, so the blind spot that created the bug was the same blind spot that missed it.

That is the gap **model stacking** closes. Model stacking means layering a second, different-provider AI model on top of Claude's work as a reviewer, so the thing checking the code is not the thing that wrote it. Borrow the name from machine learning, where "stacking" combines several independently trained models because their errors do not line up, and where one is blind another tends to see. The same logic holds for coding models. A reviewer trained by a different lab, on different data, is blind in different places than Claude, which is exactly what you want a reviewer to be.

> **The short version:** a second Claude reviewing Claude shares Claude's blind spots. A different model does not. Stacking a rival model as a read-only auditor catches the class of bug that same-model self-review is structurally built to miss.

Developers have been doing this by hand for months, ad hoc: a Reddit thread about having one agent check another, a small "second opinion" skill on a marketplace, a LinkedIn post about running a diff past Codex before merging. The move is real and the community has found it. Nobody had named it or made it repeatable. This post does both. You will learn why self-review fails at a structural level, what model stacking actually is (and the two things people confuse it with), the two backends you can stack today, and the exact moments a second model pays for itself.

## Why Self-Review Fails: The Same-Model Blind Spot

Ask any engineer why code review exists and they will not say "because the author is careless." They will say the author is too close to the work. You cannot proofread your own writing well, because your brain reads what you meant, not what you typed. A second person reads what is actually on the page.

Claude reviewing its own output has the same problem, except the closeness is not psychological, it is architectural. When Claude writes a function, it builds an internal model of the problem: which inputs are possible, which invariants hold, what "done" means. Ask it to review that same function and it reasons from that same internal model. If it assumed the upstream caller always passes a non-null user, it wrote code that trusts that assumption, and it reviews the code trusting that assumption. The review confirms the bug instead of catching it.

This surfaces as something that looks a lot like sycophancy. You ask "is this correct?" and Claude leans toward finding reasons the answer is yes. People blame the model being agreeable, and there is some of that baked into any assistant's training. But the deeper cause is not personality, it is shared priors. A model grading its own homework is using the same answer key it used to take the test.

Running a second Claude agent does not fix this. Spin up a builder agent and a validator agent, the [builder-validator team orchestration](/blog/team-orchestration) pattern, and you get real value: the validator has fresh context, it is not anchored on the act of building, and it catches plenty. But both agents are the same model. They share a training distribution, the same instincts, the same weak spots around a particular concurrency pattern or a specific security footgun. Same-model validation is good at catching attention errors, the things one instance simply overlooked. It is structurally weak against the errors that come from what the model does not know it does not know. Those are the ones that reach production.

## What Model Stacking Actually Is

Model stacking has one core discipline that separates it from everything adjacent: the second model is a read-only auditor, not a second builder. It does not touch your files. It reads the plan, the diff, or the session, and it reports what it found, ordered by severity, with file and line evidence. You stay the one who decides what to act on. The moment you let the second model start editing, you have two builders and no reviewer, and you are back to hoping.

That discipline is what makes stacking different from two things it gets confused with.

It is not Anthropic's own multi-agent review. Claude Code ships a [multi-agent code review](/blog/code-review) that dispatches several agents to hunt bugs across a PR, and it is genuinely good. But every one of those agents is a Claude model. That is parallelism inside one model family, which raises coverage without adding diversity. Six Claude agents find more than one Claude agent, and they all still share the same structural blind spots. Model stacking adds a model from a different lab, trained on different data toward different objectives, precisely so the second opinion is not a louder echo of the first.

It is also not switching your daily driver to a cheaper model. There is a well-known move where you point Claude Code at a low-cost provider like z.ai and run your one and only agent on GLM to [cut your Claude Code bill to near zero](/blog/free-claude-code). That is the same underlying trick, an Anthropic-compatible endpoint, aimed at the opposite goal. Cost-routing swaps your single engine for a cheaper one. Model stacking keeps Claude as the builder and adds a second, different engine on top as the auditor. One is about spending less. The other is about catching more. A replacement is not a stack.

## Two Ways to Stack a Model on Claude Code

There are two practical backends, and they differ mostly in where the second model lives.

**A separate CLI on its own subscription.** OpenAI's Codex CLI is a standalone coding agent you install as its own binary and sign into with your ChatGPT account. Its default model is now OpenAI's GPT-5.6, trained by a different lab on a different corpus. Because it is a wholly separate tool, the isolation comes for free: different vendor, different login, different process. You aim it at your repository in a read-only review posture and it audits Claude's plan or diff from the outside. This is the most straightforward stack to reason about, because there is no shared configuration to get wrong. It is also a useful reframe: developers usually weigh Codex CLI vs Claude Code as an either-or choice of daily driver, but stacking turns that versus into an and. Claude Code builds, Codex CLI reviews, and one task gets two independent models.

**A second, headless model inside Claude Code's own harness.** This is the more surprising option, and the one people get wrong. Claude Code reads its model endpoint from configuration: give it an Anthropic-compatible base URL and a key, and it will talk to whatever serves that API. z.ai publishes an endpoint that speaks the Anthropic API but is backed by Zhipu's [GLM 5.2](/blog/glm-5-2) rather than Claude. Launch a second Claude Code process in headless mode, its non-interactive print mode built for scripted, one-shot runs, pointed at that endpoint, and you get a completely different model auditing your work through the exact harness you already know. It is not "install a GLM plugin." There is no plugin. It is a second instance of Claude Code wearing a different engine, running quietly next to your main session.

| Dimension | Codex backend | GLM backend |
| --- | --- | --- |
| Model | OpenAI GPT-5.6 | Zhipu GLM 5.2 |
| Where it runs | Its own standalone CLI (separate binary) | A second, headless Claude Code instance |
| Sign-in | Your ChatGPT plan | A z.ai API key |
| How Claude reaches it | You install and drive a different tool | Point Claude Code's Anthropic-compatible endpoint at z.ai |
| Isolation | Automatic: different vendor, auth, process | You configure it: separate instance, scoped permissions |

Whichever backend you pick, the operating discipline is the same, and it matters more than the choice of model:

- **Read-only by default.** The auditor reads and reports. It earns edit access only when you explicitly ask, which should be rare.
- **Run it in the background.** A real audit runs at maximum effort across many files and takes minutes, not seconds. Kick it off as a background task, keep working, and collect the findings when they land. Blocking your terminal on it defeats the point.
- **Prompt it like an operator, not a chat partner.** Give it a specific task, tell it to ground every claim in files it actually read, to label anything it is only inferring, and to return findings in a fixed shape with severity and file-and-line evidence. Vague prompts produce vague audits.
- **Surface, never auto-apply.** Present the findings and stop. Let the human decide what is real. A second model is a second opinion, not a second pair of hands on your codebase.

That last rule is the whole philosophy in one line. The open-source tooling growing up around this has landed on the same place independently: the small projects that let one coding agent consult another default to a read-only "consult" mode, deliberately separate from a "work" mode. Consult, do not let it write. The value of a stacked model is judgment you did not have, delivered by something that does not share your blind spots. The moment it starts silently applying its own fixes, you have traded a known blind spot for an unknown one.

**The economics of running both just crossed a threshold.** Until this week, keeping a second subscription for the auditor was a judgment call you made per project. [GPT-5.6's general availability on July 9](/blog/gpt-5-6) put OpenAI's frontier model inside ChatGPT's $100 tier, and with both labs now anchoring competing $100 plans, the stacking technique has an obvious procurement plan: a $100 Claude Max seat for the builder and a $100 ChatGPT Pro seat for the Codex auditor out-cover paying $200 to a single lab. We ran the full [Claude Max versus ChatGPT Pro math](/blog/claude-max-chatgpt-stack) separately, but the short version is that a second-lab auditor needs a second-lab subscription anyway, so the stack pays for the exact read-only review posture this whole approach depends on.

## When to Reach for a Second Model

You do not stack a model on every prompt. It costs a second subscription's worth of tokens and your attention on the findings. Reach for it at the moments where a missed error is expensive.

**Before you ship.** The highest-value moment is right before a merge. You have a plan you are about to execute, or a diff you are about to commit, and it is large enough or load-bearing enough that a silent flaw would hurt. Stack a model to audit it cold. This is the pre-mortem that costs ten minutes and occasionally saves a weekend. It sits naturally alongside the [self-validating hooks](/blog/self-validating-agents) you may already run, except the check now comes from outside the model family instead of inside it.

**When you are stuck.** If Claude has taken three passes at a bug and keeps circling the same fix, the problem is often that the bug lives in one of its blind spots. A different model, arriving fresh with different priors, will sometimes propose the approach Claude structurally could not see. Here you might let it attempt a second implementation, in isolation, and diff the two. You are not hoping the second model is right. You are hoping it is differently wrong, because the gap between two different kinds of wrong is where the real bug is hiding.

**Auditing an autonomous run.** This is where stacking earns its keep. Let Claude run overnight in a [Ralph Wiggum style autonomous loop](/blog/ralph-wiggum-technique) and you wake up to hundreds of lines you never watched get written. Having the same model review its own unsupervised output is the weakest check available. Having a different model sweep the entire session, read-only, and flag what looks wrong is the difference between trusting the loop and auditing it. For anyone leaning into overnight and agentic workflows, a cross-model audit is fast becoming the safety layer that makes them defensible.

| Moment | What to audit | What you want from the second model |
| --- | --- | --- |
| Before a merge | The plan or the diff | A cold pre-mortem on the flaw you both missed |
| When Claude is stuck | A second, isolated implementation | To be differently wrong, exposing the real bug |
| After an autonomous run | The whole unsupervised session | An outside sweep of code you never watched land |

If you are assembling a larger setup, it helps to see where stacking fits among the multi-agent orchestration frameworks. Orchestration is about running more agents. Stacking is about running a differently-minded one. They compose: you can orchestrate a fleet of Claude builders and still stack a rival model as the final auditor over all of them.

## Cross-Model Verification Is the New Second Reviewer

The pattern underneath all of this is old and boring, which is exactly why it works. Every serious engineering org already requires a second reviewer on a pull request, not because the author is bad, but because one set of eyes, however sharp, has a fixed set of blind spots. Model stacking is that same principle moved one layer up. The author is an AI now, so the reviewer should be a different AI, one that does not inherit the author's assumptions. This is not "two models are better than one." A second Claude is still one perspective wearing two hats. It is that a model trained elsewhere is blind in different places, and where its blindness and Claude's fail to overlap, a bug has nowhere left to hide.

A year ago, running your AI's work past a second, rival AI sounded like paranoia. Now it reads as the obvious move, the same way a second reviewer on a PR stopped being optional somewhere in the last decade. The models will keep getting better, and they will keep sharing their blind spots with themselves. Cross-model verification is on its way to being table stakes. The teams that adopt it early will ship at the same speed as everyone else and quietly break production a lot less.

Multi-Agent Orchestrators
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** is a single install on top of Claude Code that adds `/spec`, `/fix`, `/prd`, project-aware rules, persistent memory across sessions, and a configured hook pipeline. Open source, MIT-licensed.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
