---
title: Discuss
description: Your agent reads the code and asks until it knows what you want and what done means.
---

![The eight steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-light.svg)
![The eight steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-dark.svg)

Describe the change in your own words: **+ New** in the App, or `/ql <request>` in your agent (`$ql` in Codex). The task appears in the App at once. Your agent reads the code and groups the questions it can ask together into one batch of three to six, each with a recommendation. With nothing open, it asks nothing.

![Discuss in the App: one question in Your turn with its choices, a visible own-answer field and Send, a strip of the batch above it, and the Discuss document below](pathname:///img/app/discuss-light.webp)
![Discuss in the App: one question in Your turn with its choices, a visible own-answer field and Send, a strip of the batch above it, and the Discuss document below](pathname:///img/app/discuss-dark.webp)

*Example task in a fictional project.*

## Answer the batch {#the-question}

**Your turn** shows one question at a time. Pick a choice, type in **Your own answer** and press **Send**, or ask **Tell me more**. Answer in any order: **Skip for now** moves on ([all controls and shortcuts](../app.md#questions)). Each answer reaches your agent immediately, and [Research](research.md) starts while the batch is still open. A second batch comes only when your answers raise a new decision.

## The document {#the-page}

`01-discuss.md` holds your request in your words, the problem, the scope, what you **decided with** your agent, and **Done means**. Comment on any passage to correct it; **Change** corrects an answer while you are still in Discuss.

## What done means {#done-means}

**Done means** is the numbered list of results you will accept the change by. Verify checks every point. You approve it together with the Plan, and changing it later withdraws that approval.

## Too small for a plan {#too-small}

For one small, clear edit, the App hands you a ready prompt for your plain agent. **Plan it anyway** keeps the full flow.

## What to build is still open {#prd}

When no ticket says what to build, the document grows into a PRD with the success measure, the first release and what is left out. **Copy** exports it.

## A bug {#a-bug}

You agree on when it happens, what goes wrong, what should happen and what must keep working. [Research](research.md) reproduces it and finds the cause, under **Why it breaks**.

![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-light.svg)
![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-dark.svg)

## At the Product level

Every new feature starts as a product brief, and Discuss asks in two batches, in product words with no code names:

| Batch | What it settles |
| --- | --- |
| **The foundation** | The **Problem** in your words, the **Success measure**, the **First release** and what comes later |
| **The solution** | **What the user sees**, with a grey wireframe of each screen that changes; the behaviour; **Not doing** |

A bug keeps its bug table. See [two levels](../intro.md#two-levels).

Next: [Research](research.md).
