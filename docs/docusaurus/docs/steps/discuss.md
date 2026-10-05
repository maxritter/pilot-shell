---
title: Discuss
description: Your agent reads the code and asks until it understands what you want and what done means. You approve Done means together with the Plan. A bug is reproduced first.
---

![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-light.svg)
![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-dark.svg)

Describe the change in your own words: `/ql <request>` (`$ql` in Codex). Opus 5.5 is recommended for this session. Your agent reads the relevant code first. Then it asks one question at a time, each with its recommendation, so "yes" is often all you type.

Discuss is a conversation in your agent. The App beside it shows what the current question is about.

![Discuss: your agent asks in Claude Code or Codex and the App shows the question; Done means lists the points you will agree with the Plan; a change too small for QualityLayer gets a ready prompt instead](pathname:///img/diagrams/discuss-light.svg)
![Discuss: your agent asks in Claude Code or Codex and the App shows the question; Done means lists the points you will agree with the Plan; a change too small for QualityLayer gets a ready prompt instead](pathname:///img/diagrams/discuss-dark.svg)

It asks about everything that matters: the scope, the behaviour, what done means, product choices and the technical shape. Most questions come here, so the Plan mostly confirms what you already agreed.

## The question you are asked {#the-question}

The step line reads "Waits for your answer", with how far along the questions are. A card under **Needs you** shows the question, the recommended choice highlighted and the other choices. You answer in your agent's own picker, in Claude Code or Codex. The App records your answer as "answered in the chat" and keeps it under **Decided with you**.

A line under the card says what your agent read: the files, the live tests it ran with their output saved, and the research questions it still has.

## Is this what you asked for, and what done means {#done-means}

When the questions are done, the step line says "The agent writes the Plan". Your agent asks you two more things, and the App shows each in full:

- **Is this what you asked for?** Your own words next to your agent's reading of them. Answer Yes or Not quite.
- **Done means.** Every point in full, with a **Comment** on each in the App. This list is what Verify later checks against, so read it with care. A point only you can confirm, such as a call to a live service, is marked here in amber, so nobody finds out in Verify.

Below them, **In this task** and **Not in this task** draw the boundary of the change.

**There is no separate approval in Discuss.** You approve Done means together with the Plan. Your answers and comments are recorded and shown again there.

## Too small for QualityLayer {#too-small}

After the first questions, your agent checks the size. When Done means fits one line, the change stays in one area of the code and nothing needs deciding, the App says "Too small for a plan". It shows a ready prompt for your plain agent, with **Copy the prompt** and **Plan it anyway**. Nothing else happens unless you ask: copy the prompt to your plain agent, or choose **Plan it anyway** for the full flow.

## In the App

The task appears in the App once your agent starts it. `00-discuss.md` fills in while you answer.

| Section | What it holds |
| --- | --- |
| Problem | What is wrong or missing today, in your words |
| Done means | The numbered, visible results you will accept the change by |
| Decided with you | The questions your agent asked, with your answers |
| In and not in this task | Where the change starts and stops |

`00-discuss-details.md` keeps your request word for word and the starting points in the code.

## When what to build is still open {#prd}

Sometimes no ticket says what to build, or several first versions seem plausible, or it is unclear who the feature is for. Then the Discuss document grows into a PRD. It adds the success measure, the first release, what the user sees and what is left out. It also says when the work is worth it and which alternatives were considered. You can also ask for it: "write it as a PRD". **Copy** exports it as a PRD at any time, to share where your team already works.

## Research

Your agent reads the code itself. When the questions span several areas it cannot trace, other agents research them without seeing your goal, so their findings describe the code as it is. Your agent checks their findings against the code. The findings go to `01-research.md`, for the agent only.

## A bug {#a-bug}

For a bug, your agent reproduces it and finds the cause before anything is planned. The reproduction output and the investigation go to `01-diagnosis.md`, for the agent. The App shows the bug as a contract you agree with:

- **When** it happens.
- **Today**, what goes wrong.
- **Expected**, what should happen.
- **Must keep working**, what the fix may not break.

Done means follows, so the fix is checked against the bug you agreed on and against a new test. You answer **Is this the bug?** first.

![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-light.svg)
![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-dark.svg)

Next: [Plan](plan.md).
