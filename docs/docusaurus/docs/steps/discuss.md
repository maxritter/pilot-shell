---
title: Discuss
description: Your agent reads the code and asks until it knows what you want and what done means.
---

![The seven steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-light.svg)
![The seven steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-dark.svg)

Describe the change in your own words: **+ New** in the App, or `/ql <request>` in your agent (`$ql` in Codex). Your agent first names and creates the task with its Discuss document, so it appears in the task list immediately. It then reads the code and groups the questions it can ask together into one batch of three to six, each with its recommendation. When nothing is open, there is no batch: your agent never adds a question to fill one.

## Questions in a batch {#the-question}

The **Your turn** card shows one question at a time, with its recommendation and relevant context; a strip above it lists the whole batch and ticks what you have answered. Answer in any order: **Skip for now** moves to another open question. Click a choice, write in the visible **Your own answer** field and press **Send**, choose **Tell me more**, or take the recommendation when you are not sure.

Each answer reaches your agent immediately. It keeps working on anything that does not depend on an open answer, and writes the research questions meanwhile: [Research](research.md) starts while your batch is still open. A second batch comes only when your answers raise a new decision. The card and its counts update together. See [Answering questions and shortcuts](../app.md#questions).

The named agent status at the top says what your agent is doing. Open **Agent status** to see whether it is working, waiting for you, quiet or stopped.

![Discuss: one focused question in Your turn, with a visible own-answer field and Send, while the agent works on the scope](pathname:///img/diagrams/discuss-light.svg)
![Discuss: one focused question in Your turn, with a visible own-answer field and Send, while the agent works on the scope](pathname:///img/diagrams/discuss-dark.svg)

## The page {#the-page}

Discuss is one document, `01-discuss.md`: your request in your own words, the problem, proposed **Done means**, the scope and what you **decided with** your agent. The step page shows these; a strip, **More in this document**, names the rest, such as the first look at the code and the links you gave. **Files** opens the whole document in the reader, with its outline. Comment on a passage to request a correction, or ask your agent to update the local Markdown file. Each answer lands in **Decided with you** at once. Use **Change** while still in Discuss to correct an earlier answer.

## What done means {#done-means}

**Done means** is the proposed numbered list of results you will accept the change by. Verify later checks every point. You approve the current criteria together with the final Plan. Earlier answers and agreements remain in the history; a separate confirmation of each point is unnecessary. Changes to the criteria invalidate the Plan's approval.

## Too small for QualityLayer {#too-small}

When the change is one small, clear edit, the App says "Too small for a plan" and gives you a ready prompt for your plain agent. **Plan it anyway** if you want the full flow.

## When what to build is still open {#prd}

When no ticket says what to build, the Discuss document grows into a PRD: the success measure, the first release and what is left out. **Copy** exports it to share with your team.

## A bug {#a-bug}

For a bug, you agree on when it happens, what goes wrong, what should happen and what must keep working. Your agent reproduces it and finds the cause in [Research](research.md), before anything is planned; that document is titled **Why it breaks**.

![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-light.svg)
![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-dark.svg)

Next: [Research](research.md).
