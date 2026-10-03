---
title: Discuss
description: Your agent reads the code and asks until it understands what you want and what done means. A bug is reproduced first.
---

![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-light.svg)
![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-dark.svg)

Describe the change in your own words: `/ql <request>` (`$ql` in Codex). Opus 5.5 is recommended for this session. Your agent reads the relevant code first. Then it asks one question at a time, each with its recommendation, so "yes" is often all you type.

![Discuss: your agent asks one question at a time with a recommendation and fills the Discuss document in the App; a change too small for QualityLayer gets a ready prompt instead](pathname:///img/diagrams/discuss-light.svg)
![Discuss: your agent asks one question at a time with a recommendation and fills the Discuss document in the App; a change too small for QualityLayer gets a ready prompt instead](pathname:///img/diagrams/discuss-dark.svg)

It asks about everything that matters: the scope, the behaviour, what done means, product choices and the technical shape. Most questions come here, so the Plan mostly confirms what you already agreed.

## Too small for QualityLayer {#too-small}

After the first questions, your agent checks the size. When Done means fits one line, the change stays in one area of the code and nothing needs deciding, it says so in one line. It writes a short prompt for your plain agent and offers to run it here or copy it. No task is created and nothing appears in the App. You can still insist on a QualityLayer task.

## In the App

The task appears in the App once your agent starts it. `00-discuss.md` fills in while you answer.

| Section | What it holds |
| --- | --- |
| Problem | What is wrong or missing today, in your words |
| Done means | The numbered, visible results you will accept the change by |
| Decided with you | The questions your agent asked, with your answers |
| Research questions | What your agent still has to find out in the code |

`00-discuss-details.md` keeps your request word for word and the starting points in the code.

Done means deserves the most attention. Every later check is measured against it.

## When what to build is still open {#prd}

Sometimes no ticket says what to build, or several first versions seem plausible, or it is unclear who the feature is for. Then the Discuss document grows into a PRD. It adds the success measure, the first release, what the user sees and what is left out. It also says when the work is worth it and which alternatives were considered. You can also ask for it: "write it as a PRD". **Copy** exports it as a PRD at any time, to share where your team already works.

## Research

Your agent reads the code itself. When the questions span several areas it cannot trace, helper agents research them without seeing your goal, so their findings describe the code as it is. Your agent checks their findings against the code. The findings go to `01-research.md`, for the agent only.

## A bug {#a-bug}

For a bug, your agent reproduces it and finds the cause before anything is planned. The reproduction output and the investigation go to `01-diagnosis.md`, for the agent. The Plan then states the reproduction, the root cause, the behaviour you need and the fix.

![Diagnosis of a bug: how to reproduce it, its root cause in the code, and the behaviour the fix must have](pathname:///img/diagrams/diagnose-light.svg)
![Diagnosis of a bug: how to reproduce it, its root cause in the code, and the behaviour the fix must have](pathname:///img/diagrams/diagnose-dark.svg)

## No approval here

Discuss has no gate. When your agent knows enough, it moves on and writes the Plan. You approve everything together there.

Next: [Plan](plan.md).
