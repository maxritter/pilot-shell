---
title: Research
description: Agents read the code before anything is designed. You settle only what the code leaves open.
---

![The eight steps, with Research highlighted](pathname:///img/diagrams/track-research-light.svg)
![The eight steps, with Research highlighted](pathname:///img/diagrams/track-research-dark.svg)

Research maps how the code works today. It can start while you answer Discuss and needs no approval.

![Research in the App: the code today and the findings](pathname:///img/app/research-light.webp)
![Research in the App: the code today and the findings](pathname:///img/app/research-dark.webp)

*Example task in a fictional project.*

## What your agent does {#what-the-agent-does}

| | |
| --- | --- |
| **Reads blind** | Research helpers do not see your request; without helpers, your agent reads the code as it is before proposing changes |
| **Checks claims** | Each cited file is reopened before a finding is written |
| **Names risks** | Code to reuse, files that change often, how it is tested |

For a bug, Research is the diagnosis: how to reproduce it, the cause, what was ruled out.

## What you do {#what-you-do}

Usually nothing. Comment on a finding you disagree with. If the code leaves a real choice open, **Your turn** asks a batch of questions.

## The document {#the-page}

`02-research.md` opens with a plain summary. Read the findings and any unresolved uncertainty before approving the later Plan. Open questions remain visible until you answer them.

The page follows the file. An open batch stands first. **Look here** points to what the goal puts at risk and to any open question. Below the summary come the risks, marked ones first, then the open questions, which are what the code could not answer, and then the findings. Each finding is one row with its title, the questions it answers and its first sentence; open it for the full text and how that code is tested today. While helpers are still reading, the page lists the questions instead, each with its helper's state. The questions, your earlier answers and how the code is tested today are collapsed under the findings, each with a one-line summary. Code references are in the document.

Next: [Plan](plan.md).
