---
title: Review changes as a team
description: After the build, your team reviews why and how a change was made, with its proof; the code is reviewed in your pull request.
---

![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-light.svg)
![Two moments for your team: review the plan before any code, and review the finished change after the build](pathname:///img/diagrams/team-timeline-dark.svg)

QualityLayer shows your team why and how a change was made, and the proof that it works. Create the pull request from Review; the code is reviewed there, as always.

Once Verify has passed, the task moves to **Review**. Your teammates see what the change was meant to do and the proof for each point of Done means. They also see the checks and scenarios, the pictures, the steps to try it, and the decisions from the Plan. The review links your branch's pull request and shows its number, state and checks.

![Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again before the re-review](pathname:///img/diagrams/team-change-light.svg)
![Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again before the re-review](pathname:///img/diagrams/team-change-dark.svg)

## How it works on both sides

| | Your side | Your teammates' side |
| --- | --- | --- |
| **Start** | **Create pull request** in Review: it pushes the branch and opens the pull request with the written description, only when you click. An existing pull request is shown instead | They are asked to review once the pull request exists |
| **Read** | Review shows the pull request's number, state and checks | Done means with its proof, the checks, the pictures, the steps to try it, and the Plan's decisions |
| **Code** | You keep a diff of your local change; your comments there go to your agent | They review the code in the pull request, as usual |
| **Comment** | Open threads collect on the review | They comment on any line and approve or ask for changes, over as many days as it takes |
| **Fix** | Run `/ql review <task>` (`$ql review <task>` in Codex); your agent goes through each thread with you, the pull request's open code comments included | Each thread ends **fixed**, **answered** or **replanned** |
| **Re-review** | Every fix is checked again before the next round | They are asked to look again |
| **Ship** | **Approve and ship** once the threads are settled | |

## People outside your team

Reviewers with a link see the overview, the evidence and the steps to try it, and their comments are advice. They have no vote.

## Notifications

You get a notification and an entry under the bell when someone asks you something or asks you to review again. The same goes for a reply in a thread you started or were asked in. Everything else, such as a task shipping, waits in the team's activity.

## What is shared

Sharing never sends your code, the diff or your logs. The review shares Done means with its proof, the steps to try it, the check results and the screenshots they cite. See [Files and privacy](../reference/files.md).
