---
title: Shipped
description: What a finished task keeps, and how the pull request and release stay with your own process.
---

![The Feature route with Shipped highlighted](pathname:///img/diagrams/track-shipped-light.svg)
![The Feature route with Shipped highlighted](pathname:///img/diagrams/track-shipped-dark.svg)

Shipped means you gave the final approval and the task is finished.

![Shipped: the task keeps its documents and evidence; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-light.svg)
![Shipped: the task keeps its documents and evidence; the pull request, merge and deploy stay in your own process](pathname:///img/diagrams/shipped-dark.svg)

## What the task keeps

Its documents, the build record, the evidence and the approved pull request description, all in `docs/plans/` in your repository. A closing record is written into the frame, `00-frame.md`. In the Cockpit you can still open the diff and the evidence, or archive the task.

## The pull request and the release

**Create pull request** in [Review](review.md) opens a pull request with the approved description, only when you click it. QualityLayer never pushes or opens one by itself. Merging, deploying and releasing stay with your own process. Shipped does not mean any of them has happened.
