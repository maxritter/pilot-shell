---
title: The Cockpit
description: Where you read your agent's documents, comment on them, approve each step and follow the build.
---

The Cockpit runs on your computer and opens in your browser by itself: when a task starts, and whenever a step waits for your approval and no Cockpit tab is open. It never opens a second tab. To open it yourself, run `qualitylayer cockpit`.

![The Cockpit with numbered parts: the task list, the step tabs, the review bar, a diagram, a comment and a clickable mockup](pathname:///img/diagrams/cockpit-marked-light.svg)
![The Cockpit with numbered parts: the task list, the step tabs, the review bar, a diagram, a comment and a clickable mockup](pathname:///img/diagrams/cockpit-marked-dark.svg)

| Part | What it does |
| --- | --- |
| **1** Task list | Tasks by who acts next: **Needs you**, **In progress**, **Shipped**. Filter by project or agent, or search |
| **2** Step tabs | Every step of the task; steps not reached yet stay greyed out |
| **3** Review bar | Who acts next, and **Request changes** or **Approve** |
| **4** Diagrams | Pictures of the system; open them full screen |
| **5** Comments | Select a passage or press **+** beside a block; your comments go to the agent together |
| **6** Mockups | Clickable, with their empty, loading and error states, running sandboxed |

Each document has a short version **For you** and a detailed one **For the agent**; the switch sits in the review bar. **Show me** collects the pictures the agent made for the task, and **Share** lets your [team](team/plans.md) in.

Above the tabs, a route card shows the task's route. Your approvals have an amber edge, optional steps are dashed, and a step you switched off is struck through. It shrinks to one line once the build starts.

## Approve in the Cockpit or in the chat

**Approve** in the review bar records your decision. You can also type `approve` as your message in the chat of the agent session that runs the task, in Claude Code or Codex. QualityLayer's own prompt hook, which the installer adds, records it and tells the agent; Codex asks you once to trust the hook. The agent cannot approve for you: if it runs the approve command itself, QualityLayer refuses.

## Follow the build

**Build**, **Verify** and **Review** form one timeline: what the agent is doing now, each slice with its tasks and notes, each end-to-end check with its runs, the quality pass with the optional steps, and every verification round with its evidence. Several helpers at work show side by side in the bar at the top. *Changes so far* lists only the files changed since the build began. You can comment at any time; the agent reads it at its next step. See [Slices](workflow/build/slices.md) and [Verify](workflow/check/verify.md).

## The first screen and Settings

The first time you open the Cockpit, it asks whether you mostly work as a **Developer** or a **Product manager** and shows the documents each one reviews. [Settings](reference/settings.md) holds that choice, four models and the switches for the optional steps.

## Copy a document out

Every document has a **Copy** menu. **Copy formatted** pastes into Confluence, Google Docs, Notion or Word with headings, tables, code, diagrams and mockups as pictures. **Copy as Markdown** pastes into Jira, GitHub or Linear. A message tells you how many diagrams and mockups went along. People outside QualityLayer then read the PRD, the design or any other document where they already work, and come back to the Cockpit to comment.

## In your terminal

With Claude Code 2.1.287 or later, the installer also adds a small QualityLayer add-on. It shows a line above your prompt while a gate waits for you, a pane with the stages and the build's progress (type `/ql-pane` to open it inline), and a message when a gate opens. It only shows; it never approves or changes anything. Without it, and in Codex, everything works as before.

## Notifications

While the Cockpit is open in a tab, your browser tells you when a document or the final change waits for you, when the build or verification stops, and when a task ships; allow notifications once when the Cockpit asks. With no tab open, a step that waits for you opens the Cockpit and shows a notification from your system (Notification Center on macOS, `notify-send` on Linux). Everything also collects under the bell.

Nothing opens over SSH or in CI. To keep the Cockpit from opening by itself anywhere, set `QUALITYLAYER_NO_BROWSER=1`; the link still appears in the chat.

## Keep it tidy

**Archive** takes a task off the list; **Restore** brings it back, and **Delete** removes an archived task and its files for good, after asking once more; commits and branches in git stay. The Cockpit follows your system's light or dark mode until you pick one, remembers your filters, and works on a phone, where the task list and the review open as drawers.
