---
title: Artifacts
description: Create screen mockups, wireframes and diagrams with your agent, keep the ones every task builds on, and review, edit and share them in QualityLayer.
---

An artifact is an HTML page, or a folder of pages that clicks through like an app. A **draft** belongs to one task. A **lasting artifact** belongs to the project: every task starts from it and leaves it matching what shipped.

![Ask your agent for an artifact, open its compact entry in Files and comment on a spot. Artifacts stay local until you include them in an encrypted shared task](pathname:///img/diagrams/artifacts-light.svg)
![Ask your agent for an artifact, open its compact entry in Files and comment on a spot. Artifacts stay local until you include them in an encrypted shared task](pathname:///img/diagrams/artifacts-dark.svg)

## Create an artifact

Ask your agent, for example: “Using QL, show two layouts for the settings page.” A standalone artifact does not start a workflow. A task's draft appears in **Files**; reusable artifacts appear in the **Library**.

| Made | Saved in |
| --- | --- |
| In a task | The task's `artifacts/` folder |
| For the project | `.qualitylayer/artifacts/<name>/` in the repository |
| On this computer only | `docs/artifacts/`, out of git |

From the terminal:

```sh
qualitylayer artifact guide
qualitylayer artifact new settings --project
qualitylayer artifact show settings --project
```

Your agent reads `qualitylayer artifact guide` once per artifact assignment and reuses it
while revising. For an artifact audit, `qualitylayer artifact guide review` returns the
review instructions. Both work without starting a workflow and need no repository.

All commands: [CLI reference](reference/commands.md#artifacts).

## The Artifacts place {#artifacts-place}

![The artifact Library: compact rows grouped by project, collapsible groups, search and sort, with previews opened on demand and Archived beside Library](pathname:///img/app/artifacts-light.webp)
![The artifact Library: compact rows grouped by project, collapsible groups, search and sort, with previews opened on demand and Archived beside Library](pathname:///img/app/artifacts-dark.webp)

**Artifacts** in the sidebar opens the reusable **Library**. Fold a project, search names and pages, or choose a project and sort order. Large groups reveal more rows as you need them; a preview loads when you open it. **New artifact** starts a reusable artifact. Working drafts stay in their task's **Files**, where their base artifact and the pages being changed are visible.

The row menu and full viewer offer rename, copy, show in another project, archive and delete. Renaming keeps existing links. A cross-project copy is independent; **Also show** adds a listing of the same original, and **Stop showing** removes that listing. **Archived** holds archived artifacts and a folded **Recently deleted** section for Restore. Deleting a source-backed entry keeps its application files.

## A lasting artifact open {#lasting}

![A reusable artifact open: page tabs, a return to the Library, a management menu and New task on this artifact, with current work and history in its sidebar](pathname:///img/app/artifacts-open-light.webp)
![A reusable artifact open: page tabs, a return to the Library, a management menu and New task on this artifact, with current work and history in its sidebar](pathname:///img/app/artifacts-open-dark.webp)

| Tab | What it holds |
| --- | --- |
| **Activity** | Current work, past changes, and folded **Details and history** |
| **Feedback** | Threads and pinned feedback per page |
| **Agent** | The conversation working on this artifact, or the choices to start one |

An artifact’s **Agent** conversation can work on its selected page without creating a workflow task. Choose an installed agent, model and effort, or copy a request and its validated artifact context into your terminal, app or IDE.

The viewer refreshes when an agent changes the artifact's HTML, styles or imported code. It keeps the selected page and viewer state. The expand button fills the current window by hiding both sidebars and fitting the width; press it again to restore their previous state and refit the artifact.

Ask to open the artifact you are working on: “Open the current QL artifact in my browser at Billing.” The agent keeps the exact artifact and page from the conversation. Missing or ambiguous sections are reported rather than silently selecting another one. From the CLI:

```sh
qualitylayer artifact open settings --project --page billing.html --section billing
qualitylayer artifact open settings --project --page billing.html --section billing --browser
```

Library management is also available through `qualitylayer artifact library inspect|rename|copy|archive|restore|delete`. Read its management revision first and pass it with `--if-match`; renaming keeps the artifact's identity, and deleting a source-backed entry keeps its application files. See the [CLI reference](reference/commands.md#artifacts).

## An artifact of many pages {#folders}

A folder artifact is interactive: buttons, menus and links between pages work, and React with JSX is provided. Nothing loads from the network. Start one with `qualitylayer artifact new <name> --folder`.

## Draft on a lasting artifact {#draft-on}

Your agent changes a lasting artifact by drafting on it in the task:

```sh
qualitylayer artifact new <name> --on <artifact>[/<page>]
```

The lasting artifact stays as it is until you fold the draft in at Review. A draft's menu (right-click or **…**) also offers **Keep as a lasting artifact…**, **Compare with …** and **Share with the team**.

Outside a task, the same command creates a personal copy in `docs/artifacts/` and remembers its base. It does not change the lasting artifact or start a workflow.

To draft on an artifact your team shares, use `--on shared:<name>` instead. See [Let your agent change a shared artifact](#shared-save).

## Keep as a lasting artifact {#keep}

Choose **Keep as a lasting artifact…** on a draft, or run `qualitylayer artifact keep <name>`.

| Where it lives | Saved in | Who sees it |
| --- | --- | --- |
| **In the repository** | `.qualitylayer/artifacts/<name>/` | Anyone who can read the repository. It goes into pull requests like code |
| **Only on this computer** | `docs/artifacts/` | Only you; git does not see it |

QualityLayer always saves to `.qualitylayer/artifacts/`. Artifacts stored earlier in a `.qualitylayer/designs/` folder are still read as artifacts, and their next save goes to the artifacts folder.

## Fold in at Review {#fold-in}

When a task drafted on a lasting artifact, Review shows a card such as **This task changes App Model**.

1. Uncheck pages to leave out. **Compare** shows the lasting page beside the draft.
2. Click **Fold 3 pages in**. The pages become one revision, in the task's pull request.

If the lasting artifact changed since the draft began, the card asks you to compare first, then offers **Fold anyway**.

## Publish to Claude {#claude-design}

A lasting artifact can store its Claude Design link for **Open in Claude Design**. QualityLayer keeps the link and changes nothing on Claude until you ask.

To publish a lasting artifact to Claude, install [Open Claude Design](https://github.com/maxritter/open-claude-design) 1.8.0 or later and sign in once with `open-claude-design login --backend artifact`. Then ask your agent, or run:

```sh
qualitylayer artifact claude settings status
qualitylayer artifact claude settings publish --if-match <revision>
qualitylayer artifact claude settings update
qualitylayer artifact claude settings comments
```

- **Status** shows the stored link, the artifact's revision and whether Open Claude Design is ready. It contacts nothing.
- **Publish** sends the artifact's first page as one self-contained file and creates a Claude artifact. It is private to you on Claude until you share it there. QualityLayer stores the returned link as the artifact's Claude Design link. An artifact that already has a link is not published again.
- **Update** sends the current page again, only when you ask. If the page on Claude changed since it was read, nothing is written.
- **Comments** lists the threads on the Claude artifact. Threads you sent to Claude come back to your agent to answer; other threads are left to people. Replies and resolves go through Open Claude Design. Your agent treats comment text as information, not as instructions.

Open Claude Design keeps your Claude sign-in. QualityLayer never reads or stores it.

## Check the page {#checks}

Your agent checks each change before you see it:

```sh
qualitylayer artifact check settings --render
qualitylayer artifact shot settings --matrix
```

`check --render` loads the page at its width and at 390 px, light and dark. A script error, a blocked network request or a picture that fails to draw is reported as a finding. `shot --matrix` saves those four pictures, each with the errors and blocked requests the page raised. Both need Chrome; without it `check` stays a source check and says so. They do not judge the design, so you still review the pictures.

Your agent keeps each artifact in step with the project's design file, so a page does not fall behind when the design file moves. It compares the page's colours, type and spacing with it, light and dark separately, and updates a value only when the design file used to have it. Colours you chose on purpose stay as they are: a colour set on one component, or any value the design file never held, is treated as deliberate, and a page that draws with its own palette is left alone. For a lasting artifact it makes the update in a task draft of it, and it writes nothing if the page changed in the meantime. When a comment points at a section that is gone, your agent asks what you meant.

## Review and comment {#full-size}

![A task artifact with Give feedback, zoom and View controls, alongside numbered feedback and the agent's reply](pathname:///img/app/artifact-light.webp)
![A task artifact with Give feedback, zoom and View controls, alongside numbered feedback and the agent's reply](pathname:///img/app/artifact-dark.webp)

*Example artifact in a fictional project.*

Press **C** (**Comment**), click a spot and say what should change. Your agent edits the page and answers in the thread. The toolbar also switches **Light**, **Dark**, **Desktop** and **Phone**; **F** goes full screen.

## Compare, edit and restore

**Open artifact canvas** shows artboards side by side. The **Actions** menu keeps rename, copy and revision controls; metadata lives under **Activity → Details and history**. Agents use `artifact inspect`, `push`, `pull` and `history`; a push cannot overwrite a newer version.

## Share an artifact with your team {#team-shared}

With a Team plan, you can share a whole artifact. Teammates open its real pages in their App, not a picture of them. The pages run in the same sandboxed frame as your own artifacts: scripts work and nothing loads from the network.

Choose **Share with the team…** on the artifact. **Who can open it** sets the audience. **People with access** gives each person **Can comment** or **Can edit**. The default is **Can comment**.

| Access | What the person can do |
| --- | --- |
| **You own it** | Everything an editor can do, plus change the audience and the editors, and stop sharing |
| **Can edit** | Open it, comment, and have their agent save new versions. Restore an older version |
| **Can comment** | Open it and comment. A save is refused |

Every save is a new version, and every version is kept. **Version history…** lists each one with who saved it and through what, such as “Claude Code · fix the sidebar”. **Restore** saves an older version again as the newest; the older one stays in the list. Nobody can change or remove a saved version.

**Stop sharing** removes the artifact from the team and from everyone’s shared list. Every version stays on the owner’s computer. Earlier picture previews of an artifact are not carried over; share it again.

## Let your agent change a shared artifact {#shared-save}

Your agent drafts on the shared artifact in a task, then saves the next version:

```sh
qualitylayer artifact shared list
qualitylayer artifact new app-model-draft --on shared:app-model
qualitylayer artifact shared save app-model-draft --note "Tighter spacing"
```

- `--on shared:<name>[/<page>]` copies the newest version, or one page and the files it uses, into the task. The draft remembers the version it started from.
- `save` makes the next version for everyone; teammates see it within about a minute. A page draft changes only its own files; the other pages stay. Add `--delete <path>` to remove a file.
- A save from an out-of-date draft is refused instead of overwriting: “app-model has version 3 now; your draft started from 2.” Run `artifact shared pull <draft>`. It merges the newer version in, file by file. A file changed on both sides stays unmerged with the team’s copy beside it, and `save` waits until you resolve it.
- A person with **Can comment** is told whom to ask for edit access.

All commands: [CLI reference](reference/commands.md#artifacts).

## Share a preview {#never-shared}

For a task draft, choose **Share › Include artifacts** to add previews to that task’s encrypted shared copy or link. These previews run no scripts.

People invited through a question can retain access while the artifact is shared. **Stop sharing** ends fresh access; it cannot remove a copy someone already downloaded. Shared Feedback supports questions, replies and attachments. Person-only feedback is kept out of the owner’s agent context. A remote viewer’s Agent tab does not start an agent from somebody else’s artifact.

An artifact kept in the repository also travels with its commits and pull requests. That is separate from sharing a preview.
