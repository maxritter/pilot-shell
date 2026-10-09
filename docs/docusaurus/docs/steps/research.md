---
title: Research
description: Agents read the code before anything is designed, without your request in front of them, and you settle only what the code leaves open.
---

![The seven steps, with Research highlighted](pathname:///img/diagrams/track-research-light.svg)
![The seven steps, with Research highlighted](pathname:///img/diagrams/track-research-dark.svg)

Research is where QualityLayer finds out how the code works today, before it decides what to change. It needs no approval from you. The only thing it may ask is one batch of choices the code leaves open.

## What your agent does {#what-the-agent-does}

Right after its first look at the code, your agent writes the research questions into `02-research.md`, while your Discuss batch is still open. Your answers and the research overlap instead of adding up.

- **Agents read the code without your request.** A few research agents each take an area and answer questions such as "how does a retry reach the queue?" They never see what you asked for or what done means, so their findings describe the code as it is.
- **A small task is read by your agent itself.** With three questions or fewer and nothing left untraced, it answers them directly.
- **Your agent checks every claim.** It reopens each file it was pointed to before writing the findings, then adds what the goal puts at risk: code the change should reuse, files that change often, and parts that are hard to change.

For a bug, Research is the diagnosis. The document is titled **Why it breaks**: how to reproduce it, the cause with how sure your agent is, what was tried and ruled out, and the edges that were probed.

## What you do {#what-you-do}

Usually nothing. Read along if you like, and comment on a passage you disagree with.

When the code leaves real choices open, **Your turn** shows one batch of three to six questions, each with what the code says about every option and a link to the finding it rests on. Answer in any order, or use **Use the recommendations for all** of them when you trust them. A clear task has no batch and goes straight to the Plan. Your agent never adds a question to reach a number.

## The page {#the-page}

![Research: the questions with their state, the findings folded to their headlines, what the goal puts at risk and what you decided](pathname:///img/diagrams/research-light.svg)
![Research: the questions with their state, the findings folded to their headlines, what the goal puts at risk and what you decided](pathname:///img/diagrams/research-dark.svg)

Research is one document, `02-research.md`, titled **How the code works today**. The step page shows:

- **Summary:** what the findings add up to, in plain words.
- **The questions** the research agents answered, with the state of each.
- **Findings,** folded to one headline each. Open one for the call tree, file tree or data shape beside its explanation.
- **What the goal puts at risk,** and **How it is tested today**.
- **Open questions,** and **Decided with you:** your answers to the batch.

A strip, **More in this document**, names the sections that stay in the whole file, such as the code references. Open the whole document in the reader from **Files**.

Next: [Plan](plan.md).
