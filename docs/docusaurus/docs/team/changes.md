---
title: Change reviews
description: After the build, your team sees why and how a change was made, with its proof; the code is reviewed in your pull request.
---

![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-light.svg)
![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-dark.svg)

Once Verify has passed, your team sees what the change was meant to do, the proof for each point, the screenshots, the steps to try it and the Plan's decisions. The code itself is reviewed in the pull request, as always.

![Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again what the fix touched before the re-review](pathname:///img/diagrams/team-change-light.svg)
![Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again what the fix touched before the re-review](pathname:///img/diagrams/team-change-dark.svg)

1. **Teammates comment** on any line, and approve or ask for changes.
2. **You run** `/ql review <task>` (`$ql` in Codex): your agent goes through each thread with you, the pull request's code comments included.
3. **Only what a fix touched** is checked again, and your team looks once more.
4. **You approve** when the threads are settled.

People outside the team can comment through a link, but their word is no vote. Sharing never sends your code, the diff or your logs.
