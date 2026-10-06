---
title: Discuss
description: Your agent reads the code and asks until it knows what you want and what done means.
---

![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-light.svg)
![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-dark.svg)

Describe the change in your own words: **+ New** in the App, or `/ql <request>` in your agent (`$ql` in Codex). Your agent reads the code first, then asks one question at a time, each with its recommendation, so one click is often all it takes.

![Discuss: your agent asks one question at a time in the App, with its recommendation, while its terminal shows one line; what you decide is written down on the page; a change too small for QualityLayer gets a ready prompt instead](pathname:///img/diagrams/discuss-light.svg)
![Discuss: your agent asks one question at a time in the App, with its recommendation, while its terminal shows one line; what you decide is written down on the page; a change too small for QualityLayer gets a ready prompt instead](pathname:///img/diagrams/discuss-dark.svg)

## The question you are asked {#the-question}

The question sits in a card above the page, with how many are probably still to come. Click a choice, type your own answer, ask the agent to **Tell me more**, or say you're not sure and take its recommendation. An easy question gets one line of context; a hard one gets the facts for each choice, and the hardest a small diagram. Your agent's terminal shows a single line while it waits. See [Answering a question](../app.md#questions).

## The page {#the-page}

Discuss is one document, `01-discuss.md`: the problem in your own words, **Done means**, what you **decided with** your agent, and the scope. Each answer lands in its row of **Decided with you**, and **Change** reopens it.

## What done means {#done-means}

**Done means** is the numbered list of results you will accept the change by. Verify later checks every point, so read them with care: **Looks right**, or **Change**. You approve them together with the Plan.

## Too small for QualityLayer {#too-small}

When the change is one small, clear edit, the App says "Too small for a plan" and gives you a ready prompt for your plain agent. **Plan it anyway** if you want the full flow.

## When what to build is still open {#prd}

When no ticket says what to build, the Discuss document grows into a PRD: the success measure, the first release and what is left out. **Copy** exports it to share with your team.

## A bug {#a-bug}

For a bug, your agent reproduces it and finds the cause before anything is planned. You agree on when it happens, what goes wrong, what should happen and what must keep working.

![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-light.svg)
![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-dark.svg)

Next: [Plan](plan.md).
