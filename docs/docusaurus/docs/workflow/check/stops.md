---
title: When it stops
description: What you decide when verification keeps failing, and how to stop, archive or delete a task.
---

![The Feature route with Verify stopped](pathname:///img/diagrams/track-stopped-light.svg)
![The Feature route with Verify stopped](pathname:///img/diagrams/track-stopped-dark.svg)

## When verification keeps failing

After three failed rounds in a row the task stops, so the agent does not repeat the same fix without you. The Verify tab shows the failed rounds and what still fails, and your browser notifies you.

![Stopped verification: three failed rounds, then you choose to continue, pivot or abandon](pathname:///img/diagrams/stopped-light.svg)
![Stopped verification: three failed rounds, then you choose to continue, pivot or abandon](pathname:///img/diagrams/stopped-dark.svg)

The agent explains what it tried and why the approach seems stuck. You choose in its chat:

| Choice | Meaning |
| --- | --- |
| Continue | Keep the approach and try again; the count starts over |
| Pivot | Agree on a different approach and review the changed plan |
| Abandon | Stop the task and keep its documents |

The same three choices come up when an [end-to-end check](../build/checks.md) fails three times during the build.

## Stop, archive or delete a task

![Abandon stops the work and keeps the documents; Archive hides a task; Delete removes an archived task after asking](pathname:///img/diagrams/abandon-light.svg)
![Abandon stops the work and keeps the documents; Archive hides a task; Delete removes an archived task after asking](pathname:///img/diagrams/abandon-dark.svg)

- **Abandon:** tell your agent at any time. The work stops; the documents and evidence stay in your repository.
- **Archive:** takes a task off the Cockpit's list. **Restore** brings it back.
- **Delete:** for archived tasks only. It asks first, then moves the files to the Trash.
