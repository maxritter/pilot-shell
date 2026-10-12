---
title: Research
description: Agents read the code before anything is designed, without your request in front of them. You settle only what the code leaves open.
---

![The eight steps, with Research highlighted](pathname:///img/diagrams/track-research-light.svg)
![The eight steps, with Research highlighted](pathname:///img/diagrams/track-research-dark.svg)

Research finds out how the code works today, before anything is designed. It starts while your Discuss batch is still open and needs no approval.

![Research in the App: a diagram of how the code works today, and the findings with what the change can reuse](pathname:///img/app/research-light.webp)
![Research in the App: a diagram of how the code works today, and the findings with what the change can reuse](pathname:///img/app/research-dark.webp)

*Example task in a fictional project.*

## What your agent does {#what-the-agent-does}

| | |
| --- | --- |
| **Reads without your request** | Research agents each take an area and answer questions like "how does a retry reach the queue?" They never see what you asked for, so the findings describe the code as it is. A small task is read by your agent itself |
| **Checks every claim** | Your agent reopens each file a finding points to before writing it down |
| **Names the risk** | Code the change should reuse, files that change often, parts that are hard to change, and how it is tested today |

For a bug, Research is the diagnosis, titled **Why it breaks**. It holds how to reproduce the bug, the cause and how sure your agent is, what was ruled out, and the edge cases tested.

## What you do {#what-you-do}

Usually nothing; comment on a finding you disagree with. When the code leaves a real choice open, **Your turn** shows one batch of three to six questions, each with what the code says about every option and a link to its finding. A clear task has no batch. At the **Product** level the batch asks only what a product person can judge: what the user sees, what it costs them, who it is for and what comes first.

## The document {#the-page}

`02-research.md` is titled **How the code works today**. It opens with a summary in plain words, then the questions and their state. Each finding folds to one headline; open it for its call tree or data shape. It ends with what the goal puts at risk and **Decided with you**. Your agent labels at most three findings or risks you should read first, **risky** or **unsure**, each with a **Look here** line saying why; sections with nothing marked, such as the questions and the code references, fold to their heading.

Next: [Plan](plan.md).
