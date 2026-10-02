---
slug: /
title: QualityLayer documentation
description: How QualityLayer takes your coding agent from a request to a reviewed change, and where you decide along the way.
---

QualityLayer runs your coding agent through a proper engineering process. You approve the plan before any code is written, the agent builds it in small tested slices, and an AI that did not write the code checks the result against what you asked for. You review it all in the **Cockpit**, in your browser.

![The Cockpit: a design under review with a system diagram, a teammate's comment and a clickable mockup](pathname:///img/diagrams/cockpit-light.svg)
![The Cockpit: a design under review with a system diagram, a teammate's comment and a clickable mockup](pathname:///img/diagrams/cockpit-dark.svg)

**Start here:** [Install](install.md) · [Your first task](first-task.md) · [How a task works](workflow/overview.md)

## Videos {#videos}

A short overview, and a walkthrough of the Cockpit.

[![Watch the QualityLayer overview video (3:20)](pathname:///img/videos/overview.jpg)](https://www.youtube.com/watch?v=FQuSwPxdNzk)

[![Watch the QualityLayer walkthrough video (9:57)](pathname:///img/videos/walkthrough.jpg)](https://www.youtube.com/watch?v=VL3WPkWolPc)

## Agree on the plan before any code

Your agent suggests a route: **Feature**, **Bug** or **Quick change**. Each planning document waits for your approval, while a change of mind still costs minutes.

![Four routes: Feature runs every step, Product feature writes a PRD and a TDD in place of the frame and the design, Bug finds the cause before the fix, Quick change goes straight to a test and the change; the optional quality pass is dashed](pathname:///img/diagrams/routes-light.svg)
![Four routes: Feature runs every step, Product feature writes a PRD and a TDD in place of the frame and the design, Bug finds the cause before the fix, Quick change goes straight to a test and the change; the optional quality pass is dashed](pathname:///img/diagrams/routes-dark.svg)

## Build in vertical slices

Each slice goes through every layer, starts with a failing test, and runs end to end before the next one starts. One last pass makes the whole change simpler, with the same behaviour.

![Three slices, each through every layer, each starting with a failing test and ending with an end-to-end run; then an optional quality pass works on the whole change before Verify](pathname:///img/diagrams/slices-light.svg)
![Three slices, each through every layer, each starting with a failing test and ending with an end-to-end run; then an optional quality pass works on the whole change before Verify](pathname:///img/diagrams/slices-dark.svg)

## One agent plans with you. Others build and check.

Helper agents on smaller, cheaper models work from the plan documents, never your chat. With Claude Code and Codex both installed, an AI from the other vendor reviews too.

![You and your agent write the plan documents; helper agents research, build, test, run the quality pass and check from them; a second AI from another vendor reviews](pathname:///img/diagrams/agents-light.svg)
![You and your agent write the plan documents; helper agents research, build, test, run the quality pass and check from them; a second AI from another vendor reviews](pathname:///img/diagrams/agents-dark.svg)

**Look something up:** [Commands](reference/commands.md) · [Settings](reference/settings.md) · [Review plans as a team](team/plans.md)
