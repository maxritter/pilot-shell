---
title: Discuss
description: Your agent reads the code and asks until it knows what you want and what done means.
---

![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-light.svg)
![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-dark.svg)

Describe the change in your own words: **+ New** in the App, or `/ql <request>` in your agent (`$ql` in Codex). Your agent reads the code first, then groups the questions it can ask together into a batch. Each comes with its recommendation.

## Questions in batches {#the-question}

One **Your turn** card holds the open questions beside the document. Answer in any order: click a choice, type your own answer, choose **Tell me more**, or take the recommendation when you are not sure.

Each answer reaches your agent immediately. It keeps working on anything that does not depend on an open answer, and asks a follow-up batch when your answers raise another decision. The card and its counts update together; **Undo** is available for five seconds. See [Answering questions](../app.md#questions).

The live status at the top says what your agent is doing. Open it to see whether it is working, waiting for you, quiet or stopped.

## The page {#the-page}

Discuss is one document, `01-discuss.md`: the problem in your own words, **Done means**, what you **decided with** your agent, and the scope. Each answer lands in **Decided with you** at once. Use **Change** to correct an earlier answer. Open the document full size to read and comment with its outline beside it.

## What done means {#done-means}

**Done means** is the numbered list of results you will accept the change by. Verify later checks every point, so read and agree to each one separately. If the agent rewords a point, only that point comes back for agreement, with the old and new words shown. Your agreement to the others stays saved. Approving the Plan is a separate action.

## Too small for QualityLayer {#too-small}

When the change is one small, clear edit, the App says "Too small for a plan" and gives you a ready prompt for your plain agent. **Plan it anyway** if you want the full flow.

## When what to build is still open {#prd}

When no ticket says what to build, the Discuss document grows into a PRD: the success measure, the first release and what is left out. **Copy** exports it to share with your team.

## A bug {#a-bug}

For a bug, your agent reproduces it and finds the cause before anything is planned. You agree on when it happens, what goes wrong, what should happen and what must keep working.

![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-light.svg)
![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-dark.svg)

Next: [Plan](plan.md).
