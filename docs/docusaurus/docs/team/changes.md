---
title: Change reviews
description: After the build, your team sees why and how a change was made, with its proof, and can read the code from your own Git remote.
---

Once Verify passes, your team reads the walkthrough of the change with its proof. With **Ask for review** they can also read the code and comment on its lines ([Review with your team](../steps/review.md#team-review)).

![Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again what the fix touched before the re-review](pathname:///img/diagrams/team-change-light.svg)
![Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again what the fix touched before the re-review](pathname:///img/diagrams/team-change-dark.svg)

1. Teammates comment, approve or ask for changes.
2. Ask “Using QL, review task retry-webhooks”, naming your actual task, to settle each thread with your agent.
3. What a fix touched is checked again, and your team looks once more.
4. You approve.

## Reading the code together {#code}

**Ask for review** pushes the task's branch to your team's own Git remote and asks the teammates you pick. It shows the remote and the commits first, and pushes only when you click. The shared task then carries where the code is: the repository, the branch and its commits, encrypted with your team's key.

- A teammate with a checkout of the same repository reads the code from that checkout and comments on lines. Who can read the code is decided by your Git remote, as today.
- A teammate without a checkout, or without access to the remote, sees the walkthrough with file names.
- Their comments sit on the lines they are about. You stay the one who approves the change.

Pull request threads and failing checks come back the same way ([Pull request](../steps/pull-request.md)). Shared tasks include no source files, diffs or host logs. Code reaches teammates through your Git remote, and a comment can quote a few lines of the code it is about ([What is shared](plans.md#privacy)). Review any text or attachments you add before sending.
