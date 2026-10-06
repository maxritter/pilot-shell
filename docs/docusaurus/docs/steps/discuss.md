---
title: Discuss
description: Your agent reads the code and asks until it knows what you want and what done means.
---

![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-light.svg)
![The five steps, with Discuss highlighted](pathname:///img/diagrams/track-discuss-dark.svg)

Describe the change in your own words: `/ql <request>` (`$ql` in Codex). Your agent reads the code first, then asks one question at a time, each with its recommendation, so "yes" is often all you type.

![Discuss: your agent asks in Claude Code or Codex and the App shows the question; Done means lists the points you will agree with the Plan; a change too small for QualityLayer gets a ready prompt instead](pathname:///img/diagrams/discuss-light.svg)
![Discuss: your agent asks in Claude Code or Codex and the App shows the question; Done means lists the points you will agree with the Plan; a change too small for QualityLayer gets a ready prompt instead](pathname:///img/diagrams/discuss-dark.svg)

## The question you are asked {#the-question}

You answer in your agent. The App beside it shows the question, the recommended choice and what your agent read to get there.

## What done means {#done-means}

At the end, your agent shows its reading of your request next to your own words, and **Done means**: the numbered results you will accept the change by. Verify later checks every point, so read them with care. You approve them together with the Plan.

## Too small for QualityLayer {#too-small}

When the change is one small, clear edit, the App says "Too small for a plan" and gives you a ready prompt for your plain agent. **Plan it anyway** if you want the full flow.

## When what to build is still open {#prd}

When no ticket says what to build, the Discuss document grows into a PRD: the success measure, the first release and what is left out. **Copy** exports it to share with your team.

## A bug {#a-bug}

For a bug, your agent reproduces it and finds the cause before anything is planned. You agree on when it happens, what goes wrong, what should happen and what must keep working.

![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-light.svg)
![Diagnosis of a bug: when it happens, what happens today, what is expected, and what must keep working](pathname:///img/diagrams/diagnose-dark.svg)

Next: [Plan](plan.md).
