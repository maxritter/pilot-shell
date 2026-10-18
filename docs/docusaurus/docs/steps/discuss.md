---
title: Discuss
description: Your agent reads the code and asks until it knows what you want and what done means.
---

![The eight steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-light.svg)
![The eight steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-dark.svg)

Describe the change with **+ New** in QualityLayer or ask your agent: “Using QL, plan a CSV export.” Your agent reads the code and groups the questions it can ask together into one batch of three to six, each with a recommendation.

![Discuss in the App: one question with its choices](pathname:///img/app/discuss-light.webp)
![Discuss in the App: one question with its choices](pathname:///img/app/discuss-dark.webp)

*Example task in a fictional project.*

## Answer the batch {#the-question}

1. **Your turn** shows one question at a time. Pick a choice, or write your own answer and press **Send**.
2. Answer in any order. **Skip for now** moves on; **Tell me more** explains.
3. Each answer reaches your agent immediately. A second batch comes only if your answers raise a new decision.

[Research](research.md) can start while you answer ([all controls](../app.md#questions)).

## What done means {#done-means}

`01-discuss.md` records your request, the scope and **Done means**: the numbered results you accept the change by. Verify checks each one. You approve it with the Plan; changing it later withdraws that approval.

The page follows the file. An open batch stands first. **Look here** then points to anything only you can confirm and any area the agent could not trace in the code. Below the task title and a short summary, **Done means** is a list of numbered rows, each with how it will show; a point changed after you agreed stays in place, marked as changed, and a withdrawn one is struck through. **Scope** follows as two short columns, in this task and not in this task. Your earlier answers and anything added while building are collapsed under them, each with a one-line summary. The context and the first look at the code are in the document.

## Too small for a plan {#too-small}

Small requests keep a short Plan and one slice. If you ask for a plain prompt instead, your agent hands one back and closes the task.

## What to build is still open {#prd}

Without a ticket, the document becomes a PRD with a success measure and a first release. **Copy** exports it.

## A bug {#a-bug}

You agree on when it happens, what goes wrong, what should happen and what must keep working. Research finds the cause.

![Bug diagnosis: when, what happens, what is expected, what must keep working](pathname:///img/diagrams/diagnose-light.svg)
![Bug diagnosis: when, what happens, what is expected, what must keep working](pathname:///img/diagrams/diagnose-dark.svg)

At the **Product** level, questions use product words: the problem and first release, then what the user sees, with grey wireframes ([two levels](../intro.md#two-levels)). The page keeps the PRD's sections open, since the file is the PRD.

Next: [Research](research.md).
