---
slug: "claude-3-5-sonnet-v2"
title: "Claude 3.5 Sonnet v2 and Haiku: Computer Use Arrives"
description: "October 2024 brought an upgraded Claude 3.5 Sonnet, Claude 3.5 Haiku, and the groundbreaking Computer Use feature in public beta."
date: "2024-10-22"
author: "Max Ritter"
tags: [Reference, Models]
readingTime: 4
keywords: "3, 35, 5, arrives, claude, computer, haiku, sonnet, use, v2"
---

# Claude 3.5 Sonnet v2 and Haiku: Computer Use Arrives

October 2024 brought an upgraded Claude 3.5 Sonnet, Claude 3.5 Haiku, and the groundbreaking Computer Use feature in public beta.

The October 22, 2024 release was a double launch: an upgraded Claude 3.5 Sonnet with meaningful performance gains, a new Claude 3.5 Haiku for fast and cheap workloads, and a feature that no one saw coming. Computer Use put Claude in control of a desktop, complete with cursor movement, clicking, and typing. AI models could now interact with software the same way humans do.

## [Key Specs](#key-specs)

| Spec | Claude 3.5 Sonnet v2 | Claude 3.5 Haiku |
| --- | --- | --- |
| **API ID** | `claude-3-5-sonnet-20241022` | `claude-3-5-haiku-20241022` |
| **Context window** | 200K tokens | 200K tokens |
| **Input pricing** | $3 / 1M tokens | $0.80 / 1M tokens |
| **Output pricing** | $15 / 1M tokens | $4 / 1M tokens |
| **Max output tokens** | 8,192 | 8,192 |
| **Release date** | October 22, 2024 | October 22, 2024 |

## [What This Release Brought to the Table](#what-this-release-brought-to-the-table)

**Computer Use (public beta).** The headline feature. Claude could now look at a screen, move the mouse, click buttons, and type text. This was not a browser automation tool or a scripted macro. The model received screenshots, interpreted what was on screen, and decided where to click and what to type. It could fill out forms, navigate between applications, search the web, and operate any software with a GUI.

No major AI model had shipped anything like this before. Computer Use opened a new category of agentic capabilities: instead of building custom API integrations for every tool, you could point Claude at the interface and let it work.

**Upgraded Sonnet.** The v2 Sonnet was not a minor patch. It delivered significant improvements in coding, tool use, and instruction-following over the [original 3.5 Sonnet](/blog/models/claude-3-5-sonnet). Agentic coding tasks, multi-step tool use, and following complex instructions all improved. For developers using Claude as a coding assistant, the upgrade was immediately noticeable.

**Claude 3.5 Haiku.** The new Haiku brought 3.5-generation intelligence to the budget tier. At $0.80/$4 per million tokens, it offered strong performance for classification, content moderation, chat applications, and any high-volume workload where cost matters more than peak capability.

## [Computer Use in Practice](#computer-use-in-practice)

Computer Use launched in public beta through the API. Developers could build agents that:

- Navigate web applications and fill out forms
- Move between desktop applications
- Extract information from visual interfaces
- Perform repetitive GUI-based tasks
- Test software by interacting with the actual UI

The feature required sending screenshots to the model and receiving coordinates for mouse actions. Anthropic built it with safety constraints: the model could not perform irreversible actions without confirmation, and rate limits were applied to prevent abuse.

## [How It Compared to the Original 3.5 Sonnet](#how-it-compared-to-the-original-35-sonnet)

The v2 release kept the same pricing ($3/$15) while improving output quality. The gains were most visible in agentic workflows where Claude needed to chain multiple tool calls, interpret results, and adjust its approach. Instruction-following accuracy also improved, reducing the "close but not quite" moments that frustrated developers using the original version.

## [Current Status](#current-status)

| Model | Status |
| --- | --- |
| Claude 3.5 Sonnet v2 | Superseded by Claude 3.7 Sonnet (February 2025) |
| Claude 3.5 Haiku | Still referenced in some deployments |

Both models have been superseded by newer generations, but they marked the moment Claude became more than a text generator. Computer Use was the proof of concept that led to increasingly sophisticated agentic capabilities in the [Claude 3.7 Sonnet](/blog/models/claude-3-7-sonnet) and [Claude 4](/blog/models/claude-4) releases.

## [Navigation](#navigation)

- [All Claude Models](/blog/models) for the complete model index
- [Claude 3.5 Sonnet](/blog/models/claude-3-5-sonnet), the original June 2024 release
- [Claude 3.7 Sonnet](/blog/models/claude-3-7-sonnet), the next generation with hybrid reasoning

Last updated on

[Previous

Claude 3.7 Sonnet](/blog/models/claude-3-7-sonnet)[Next

Claude 3.5 Sonnet](/blog/models/claude-3-5-sonnet)
