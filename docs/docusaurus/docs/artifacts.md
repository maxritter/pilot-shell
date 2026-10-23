---
title: Artifacts
description: Create and review mockups, diagrams and clickable pages with your agent, then keep and share them.
---

An artifact is a mockup, diagram or clickable set of pages you work on with your agent. A **draft** belongs to one task. A **lasting artifact** is kept for the project and reused by later tasks.

![Ask for an artifact, open its compact entry in Files and comment on a spot. Share it when you choose.](pathname:///img/diagrams/artifacts-light.svg)
![Ask for an artifact, open its compact entry in Files and comment on a spot. Share it when you choose.](pathname:///img/diagrams/artifacts-dark.svg)

## Create an artifact

Ask “Using QL, show two layouts for the settings page.” This creates an artifact without starting a workflow. A task's draft appears as a compact entry in **Files**; reusable artifacts appear in the **Library**.

## The Artifacts place {#artifacts-place}

![The artifact Library, grouped by project, with search, Favorites, List and Gallery views](pathname:///img/app/artifacts-light.webp)
![The artifact Library, grouped by project, with search, Favorites, List and Gallery views](pathname:///img/app/artifacts-dark.webp)

Open **Artifacts** in the sidebar. Choose **All**, **Yours** or **Shared with you**, then search or browse by project. Switch between **List** and **Gallery**; star an artifact to keep it in **Favorites**.

- **New artifact** starts a reusable artifact.
- The row menu offers rename, copy, archive and delete. A copy is independent.
- **Also show** lists the same artifact under another project.
- **Archived** includes **Recently deleted**, where you can restore an entry.

Deleting a source-backed entry keeps its application files.

## Open a lasting artifact {#lasting}

![A lasting artifact with page tabs, feedback and its agent conversation](pathname:///img/app/artifacts-open-light.webp)
![A lasting artifact with page tabs, feedback and its agent conversation](pathname:///img/app/artifacts-open-dark.webp)

Choose a page tab to explore it. Buttons and links work, so you can review a flow before it is built. The right sidebar holds activity, feedback and the agent conversation.

Work with an installed agent, or copy a request into your own terminal, app or IDE. No workflow task is needed. Changes refresh in the viewer and keep your selected page. The expand control hides both sidebars; use it again to restore them.

Ask “Open the current QL artifact in my browser at Billing” to return to a specific page or section.

## Review and comment {#full-size}

![A queue migration console drawn as an artifact, with pinned comments and the agent's reply](pathname:///img/app/artifact-light.webp)
![A queue migration console drawn as an artifact, with pinned comments and the agent's reply](pathname:///img/app/artifact-dark.webp)

*Example artifacts and people are fictional.*

Press **C** for **Comment**, click a spot and say what should change. Your agent edits the page and answers in the thread. The viewer offers **Light**, **Dark**, **Desktop** and **Phone**; **F** goes full screen.

## An artifact of many pages {#folders}

Use a folder artifact for a flow with several screens. Pages can include their own scripts, styles and pictures. Scripts run in the viewer, but nothing loads from the network.

## Draft on a lasting artifact {#draft-on}

Ask your agent to draft a change on the project's artifact. The original stays in place until you fold the draft in at Review. Outside a task, your agent creates a personal copy instead.

A draft's menu offers **Keep as a lasting artifact…**, **Compare with …** and **Task sharing…**, which opens the sharing controls for its task.

## Keep as a lasting artifact {#keep}

Choose **Keep as a lasting artifact…** on a draft, then where it lives:

| Where | Who can read it |
| --- | --- |
| **In the repository** | Anyone with repository access; it travels with commits and pull requests |
| **Only on this computer** | Only you; it stays out of Git |

## Fold in at Review {#fold-in}

When a task changes a lasting artifact, Review shows a card such as **This task changes App Model**.

1. Choose the pages to include. **Compare** opens the lasting page beside the draft.
2. Choose **Fold pages in**. The selected pages become one revision in the task's pull request.

If the original changed meanwhile, compare before folding. For a team artifact, folding also saves a new shared version; resolve any conflict first.

## Compare, edit and restore

**Open artifact canvas** opens the full workspace. Rename or copy an artifact from the management menu. To compare or restore an earlier revision, ask your agent. Restoring keeps the previous history.

## Share an artifact with your team {#team-shared}

With a Team plan, choose **Share with the team…**. Teammates open the real pages in their App. **Sharing and access…** sets who can open and who can edit.

| Access | What the person can do |
| --- | --- |
| **Owner** | Edit, manage access and stop sharing |
| **Can edit** | Comment and save versions; ask their agent to restore a version |
| **Can comment** | Open pages and leave feedback |

Every save keeps a new version. The owner can open **Version history…** and restore an older one as the newest.

When your local files change, **Save for the team** publishes them as the next version. A teammate's newer version is brought in first. If the same file changed on both sides, your agent helps resolve the conflict.

**Stop sharing** ends team access. Keep any older version you need first: the dialog warns about versions this computer cannot open. See [Files and privacy](reference/files.md#privacy).

## Let your agent change a shared artifact {#shared-save}

Ask your agent to draft on the shared artifact, then save the next version for the team. It merges newer versions before saving. A person with **Can comment** needs an editor or owner to make the change.

## Share a preview {#never-shared}

For a task draft, choose **Share › Include artifacts**. This adds previews to the task's encrypted shared copy or link. The previews run no scripts.

**Stop sharing** ends fresh access; it cannot remove a copy someone already downloaded. Sharing through a task is separate from keeping an artifact in the repository.

## Publish to Claude {#claude-design}

If you use Open Claude Design, ask your agent to publish or update a lasting artifact there. It sends a copy only when you ask and keeps the link for **Open in Claude Design**. [Commands and setup](reference/commands.md#artifacts).

## Check the page {#checks}

Your agent checks the page in light and dark, at desktop and phone widths, for script errors, missing pictures and clipped content. You still decide whether it works for you.

Ask for a design review to check the artifact against your project's design guidance. Intentional choices stay.

[Artifact commands, file locations and revisions](reference/commands.md#artifacts).
