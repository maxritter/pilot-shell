---
title: Change reviews
description: After the build, your team sees why and how a change was made, with its proof; the code is reviewed in your pull request.
---

Once Verify passes, your team reads the walkthrough of the change with its proof. The code is reviewed in the pull request.

![Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again what the fix touched before the re-review](pathname:///img/diagrams/team-change-light.svg)
![Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again what the fix touched before the re-review](pathname:///img/diagrams/team-change-dark.svg)

1. Teammates comment, approve or ask for changes.
2. Run `/ql review <task>` (`$ql` in Codex) to settle each thread with your agent.
3. What a fix touched is checked again, and your team looks once more.
4. You approve.

Pull request threads and failing checks come back the same way ([Pull request](../steps/pull-request.md)). Shared tasks do not automatically include source files, diffs or host logs. Review any text or attachments you add before sending.
