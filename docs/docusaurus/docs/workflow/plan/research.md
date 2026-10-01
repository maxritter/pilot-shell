---
title: Research
description: How the code works today, with a picture of the parts involved and findings that point to the code.
---

![The Feature route with Research highlighted](pathname:///img/diagrams/track-research-light.svg)
![The Feature route with Research highlighted](pathname:///img/diagrams/track-research-dark.svg)

Research describes the system as it is, before anything is designed. A helper agent answers the frame's research questions without seeing your goal, so it reports facts instead of arguing for a plan. Your agent checks the findings against the code and writes them up.

![Research: a picture of the parts involved, and findings that each point to the code](pathname:///img/diagrams/research-light.svg)
![Research: a picture of the parts involved, and findings that each point to the code](pathname:///img/diagrams/research-dark.svg)

## In the Cockpit

| Version | File | What it holds |
| --- | --- | --- |
| For you | `01-research.md` | A picture of the parts involved, and the findings that matter |
| For the agent | `01-research-details.md` | Each finding with its evidence, the code references, the open questions |

Questions only you can answer, such as a product fact or an account setting, come to you in your agent's chat, as options to pick, before the research is up for review.

The research also names the existing code the change should reuse, so the build does not write it again.

## You decide

Correct anything that is wrong; a correction is checked against the code and fixed in place. Then approve.

Next: [Design](design.md).
