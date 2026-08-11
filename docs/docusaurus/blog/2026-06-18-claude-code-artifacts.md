---
title: "Claude Code Artifacts: Stop Losing Session Work"
description: "Claude Code Artifacts turn session work into live, shareable pages at a versioned URL. Private by default, in beta for Team and Enterprise."
slug: claude-code-artifacts
date: 2026-06-18
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Claude Code Artifacts turn session work into live, shareable pages at a versioned URL. Private by default, in beta for Team and Enterprise.

<!-- truncate -->

Claude Code Artifacts turn the work inside a session into a live, shareable page. They fix a problem that anyone who works in Claude Code will recognize: the hardest thing you built this week lives in your terminal scrollback, and it dies when you close the tab. You walked Claude Code through a gnarly PR, watched it reason through the diff, confirmed what you tested. The reviewer who needs that context gets a Slack paste of raw text with no annotations. You traced where personal data flows across the codebase for a privacy review, and the output is a wall of file paths nobody else will read. You kept an incident timeline as Claude worked the outage, then the session ended and the timeline went with it.

This is the quiet tax on terminal-first work: the reasoning is the valuable part, and the reasoning is exactly what does not survive the session. Your teammates never see the context, only the conclusion. Every time you want someone else to understand what happened, you rebuild it by hand in a doc, a comment, a screenshot, a Loom. The work is done and you are still working.

Claude Code Artifacts close that gap. An artifact is a live, interactive web page that Claude Code publishes from your session to a private URL on claude.ai. You open it in a browser, it updates in place as the session continues, and you share it with a teammate from the page header. The reasoning stops being scrollback you have to translate. It becomes a page you send.

## Claude Code Artifacts in 30 Seconds

- **What it is:** a live, interactive web page Claude Code publishes from your session to a private URL on claude.ai.
- **How to make one:** ask in plain language. There is no slash command. Claude writes an `.html`, `.htm`, or `.md` file and publishes it.
- **How to update:** ask again, or let a long-running task republish. Every publish is a new version at the same URL, and you can roll back.
- **How to share:** the Share control in the page header. Private to you by default, shareable only with members of your organization.
- **How to reopen:** press `Ctrl+]` for the most recent artifact.
- **Availability:** beta, on Team and Enterprise plans, from the Claude Code CLI or the desktop app.

## What a Claude Code Artifact Actually Is

An artifact is a capture of work, not an application. Claude builds the page from everything your session can reach: your codebase, the conversation itself, and any data it pulls through your connected MCP tools. That full-session context is the whole point. The page can show things that would take paragraphs to describe, because Claude already has the diff, the file tree, the tokens, and the relationships in working memory.

A few mechanics make it different from "Claude wrote an HTML file":

**It is one self-contained page, served from claude.ai.** Claude Code wraps the file in an HTML document shell and serves it under a strict Content Security Policy. No external requests, no backend, no second route. For multi-section content, Claude uses in-page anchors rather than separate files.

**Every publish is a new version at the same URL.** When Claude updates an artifact, the open page refreshes in place and anyone with it open sees the change the moment it lands. Each publish becomes a version, and from the Share control you choose which version viewers see. You can roll back to an earlier one at any time.

**A gallery collects everything you have made.** Your gallery at claude.ai/code/artifacts lists every artifact you have created, each with the title and tab icon Claude picked for it.

Here is the boundary worth internalizing early: an artifact has no backend. It cannot store form input, authenticate viewers itself, or call an API at view time. The published file must be `.html`, `.htm`, or `.md`, and the rendered page must come in at 16 MiB or smaller. If you need a hosted internal tool with a live backend, deploy that on your own infrastructure. An artifact is for showing finished thinking, not for running a service.

## How to Create One

There is no slash command. You ask for it in plain language, the same way you ask for anything else. Name the feature or describe the visual output you want, and Claude either publishes an artifact on its own when the output suits a page, or builds one because you asked. The [official Claude Code docs](https://code.claude.com/docs/en/artifacts) give two starter prompts verbatim:

```
Make an artifact that walks through this PR with the diff annotated inline.
```

```
Build a dashboard artifact of last week's deploy failures by service and keep it updated as you investigate.
```

Claude writes the page to an HTML or Markdown file in your project, then asks permission before publishing the first time. The prompt reads something like `Claude wants to publish "Deploy failures by service" (deploy-failures.html) to a private page on claude.ai`. Approve it once and republishing the same artifact does not prompt again. Claude prints the URL and your browser opens to the page. Press `Ctrl+]` to reopen the most recent artifact from the terminal at any time.

Updating works the same way. Ask Claude to revise the page, or let a long-running task republish as it makes progress, and Claude edits the underlying file and publishes to the same URL. To update an artifact from a different session, hand Claude the artifact URL and ask it to revise. Without the URL, a new session always creates a new artifact instead of editing the old one.

```
Update https://claude.ai/code/artifact/5fbea6f3-... with today's numbers.
```

If you do not want the browser to open automatically on every publish, set `CLAUDE_CODE_ARTIFACT_AUTO_OPEN=0` in your environment.

## The Prompts That Map to Real Roles

The reason artifacts matter is that the same mechanic serves a dozen different jobs. [Anthropic's announcement](https://claude.com/blog/artifacts-in-claude-code) frames artifacts around concrete role-based prompts, and they read like a tour of who is stuck pasting context into docs today. These are the prompts as published:

| Role | Prompt |
| --- | --- |
| **Software engineers** | "Make an artifact walking through this PR, the diff, the reasoning, and what I tested." |
| **Staff engineers and architects** | "Map how the payments service fits together into an artifact, from the code." |
| **SRE and on-call** | "Turn this incident into an artifact, timeline, suspect commits, error spike from our monitoring, and republish as I work through it." |
| **Engineering managers** | "Build an artifact of what merged on my team this week from the PRs, grouped by project." |
| **Security** | "Build an artifact of the auth findings from this review, each linked to the code." |
| **Privacy** | "Trace where we touch personal data across the codebase into an artifact for the privacy review." |
| **Legal and open source** | "Build an artifact listing every third-party dependency and its license, flagging anything copyleft." |
| **FinOps and platform finance** | "Map our cloud resources from the Terraform into an artifact, grouped by service, with the big cost drivers." |
| **Designers and frontend engineers** | "Give me an artifact with 5 UX variations of this signup form, built from our component library." |

Notice the pattern. Every one of these is output that is easier to look at than to read line by line, produced from context the session already holds. The SRE prompt is the sharpest example: "republish as I work through it" means the incident page fills in live while the outage is still active, so anyone with the link follows along without reading your terminal. That timeline pulls its error spike from your [monitoring tool data](/blog/monitor), which is exactly the kind of live signal an artifact is built to surface.

Beyond the role prompts, the docs describe a handful of interaction patterns worth knowing. You can ask for several variants on one page to compare layouts or API shapes side by side. You can request sliders and toggles bound to a value you are tuning, like an easing curve, and watch it update live. You can even ask for a "Copy as prompt" button that turns your interaction with the page back into text you paste into the terminal, so a triage board you reorder on the page flows its final ordering back into the session.

## Where Artifacts Pay Off for Teams

Solo, an artifact is a nicer way to look at output. On a team, it changes who can see your reasoning without you doing extra work.

A PR walkthrough is the obvious case. Instead of a reviewer reconstructing your intent from a description, you publish a page with the diff rendered, your reasoning in the margin, and findings color-coded by severity. The reviewer reads your thinking next to the code. This is the lightweight, single-session cousin of a full [multi-agent code review](/blog/code-review), where several agents analyze a PR in parallel. An artifact captures and shares the result of that analysis as a page anyone on the team can open.

Incident timelines are the other standout. During an outage, the on-call engineer keeps a single page current: timeline, suspect commits, the error spike from monitoring. Everyone watching the incident reads the same live page instead of pinging for status. When the incident closes, the timeline is already written, already shareable, already a postmortem draft.

Then there is the engineering manager's weekly summary, built from the PRs that merged, grouped by project. No more assembling a status update by hand on Friday. The same goes for architecture maps that new hires can actually read, license audits legal can review, and data-flow maps a privacy team can sign off on. In every case the artifact is the deliverable, not a thing you build after the deliverable.

Artifacts also pair naturally with the kind of parallel, multi-session work that an [agent dashboard](/blog/agent-view) coordinates. When several sessions are running at once, each can publish its own artifact, and the gallery becomes a shared surface for the team to see what every session produced.

## Privacy, Access, and Admin Controls

This is where the design is deliberately conservative, and it matters for anyone evaluating artifacts inside a company.

**Private by default.** A new artifact is visible only to you. You open it, then use the Share control in the page header to grant access to specific people in your organization or to everyone in it. The header names you as the author, so anyone you share with can see who published the page.

**Sharing stops at your organization.** Viewers must sign in to claude.ai as a member of the same organization that published the artifact. There is no option to make an artifact viewable outside it, and no public link. If you need to send the content to someone outside the org, ask Claude for the underlying HTML file and share that file directly. Artifacts are also viewable, not co-edited: people you share with see each version you publish but cannot change the page. You remain the only writer.

For admins, the controls live in claude.ai admin settings:

- **Org-level toggle.** Turn artifacts on or off for the whole organization under Settings > Claude Code > Capabilities. On Enterprise plans with role-based access control, you can scope artifacts to specific roles under Settings > Roles.
- **Retention policies.** Under Settings > Data & privacy controls, set how long artifacts are kept before automatic deletion, with separate retention periods for artifacts still private to their author versus artifacts that have been shared.
- **Audit log.** Publishing, sharing, and deleting each appear under the `claude_artifact_*` event types.
- **Compliance API.** Endpoints to list an organization's artifacts, retrieve a specific version's content, and delete an artifact, for org-wide visibility and cleanup.

Artifact content is stored on Anthropic-operated infrastructure and is visible only to authenticated members of the publishing organization. If your org restricts outbound network access, note that the viewer loads each artifact from a sandboxed `*.claudeusercontent.com` origin, so that domain needs to be allowlisted alongside claude.ai.

## Availability and How to Get Access

Artifacts are in beta, and access depends on every condition below being met. When one is not, Claude writes a local HTML file or says it cannot publish.

| Requirement | Available when |
| --- | --- |
| **Plan** | Team or Enterprise. On Team plans, artifacts are on by default. On Enterprise, an admin enables them in claude.ai admin settings. |
| **Authentication** | Signed in to claude.ai with `/login`. API key, gateway token, and cloud-provider credentials cannot publish. |
| **Model provider** | Anthropic API. Not available on Amazon Bedrock, Google Cloud Vertex AI, or Microsoft Foundry. |
| **Org policy** | Customer-managed encryption keys, HIPAA, and Zero Data Retention must not be enabled for the org. |
| **Surface** | Claude Code CLI, or the Claude desktop app version 1.13576.0 or later. Off by default in Agent SDK, GitHub Action, and MCP-server contexts. |

Pages are viewable in any browser once published, even though you create them from the CLI or desktop app. If you want to turn artifacts off for your own sessions regardless of the org setting, you have three options: set `"disableArtifact": true` in your settings file, set `CLAUDE_CODE_DISABLE_ARTIFACT=1` in your environment, or add `Artifact` to `permissions.deny`.

One practical caveat on cost: generating an artifact uses output tokens like any response, and a styled page is more token-intensive than the same content as terminal text. Inline CSS, interactive JavaScript, and especially images embedded as data URIs are the main drivers. Prefer SVG or HTML and CSS over raster images for diagrams, skip interactivity you do not need, and have the page summarize large datasets rather than inline them in full.

## Where Artifacts Fit Among Claude's Shareable Outputs

Artifacts are not the first time Anthropic has shipped a cloud-hosted, browser-reviewable output from a Claude Code session. They are the third move in a clear pattern.

[Ultraplan](/blog/ultraplan) offloads a planning task to the cloud and gives you a browser review UI with inline comments to refine the plan before it executes. [Claude Design](/blog/claude-design-handoff) builds a prototype on a shared canvas and hands it to Claude Code as a structured spec. Artifacts complete the set on the output side: they take work the session already did and publish it as a page a teammate can open.

That is the real shift. The valuable part of a Claude Code session has always been the reasoning, and the reasoning has always been the part that did not survive. Artifacts make it a page. Ask your session for one the next time you finish something worth showing, and watch how much less time you spend explaining it afterward.

## Frequently Asked Questions

### Is there a slash command for Claude Code Artifacts?

No. There is no `/artifact` command. You ask for an artifact in plain language, and Claude publishes one when the output suits a page. Press `Ctrl+]` to reopen the most recent artifact from your terminal.

### What do I do when Claude says it cannot publish an artifact?

That means the tool is not enabled for your session, so Claude writes a local HTML file instead of a link. Work down the availability requirements in order: confirm you are on a Team or Enterprise plan, that you are signed in to claude.ai with `/login` (an API key or cloud-provider credential cannot publish), that you are on the Anthropic API rather than Bedrock, Vertex, or Foundry, and that your org does not enforce customer-managed encryption keys, HIPAA, or Zero Data Retention. On Enterprise, an admin also has to switch artifacts on.

### Can I share a Claude Code Artifact publicly or outside my organization?

No. Artifacts are private to you by default and can only be shared with authenticated members of the same organization. There is no public link. To send the content outside your org, ask Claude for the underlying HTML file and share that file directly.

### Are Claude Code Artifacts available on the Max, Pro, or Free plan?

Not yet. Claude Code Artifacts are in beta on Team and Enterprise plans only, so individual Max, Pro, and Free plans cannot publish them from a Claude Code session. Do not confuse this with the artifacts Claude generates inside claude.ai chats, which Max, Pro, and Free users already have. Those are a separate feature. The rest of Claude Code's session features work on every plan, so if you are on Max or Pro, start with what Claude Code is and the terminal-first workflow.

---

*New to working in the terminal? Start with the terminal-first development model to understand how Claude Code's execution surface works, then see [Ultraplan](/blog/ultraplan) and [Claude Design](/blog/claude-design-handoff) for the other half of Anthropic's cloud-hosted, shareable output story. Primary sources: [Anthropic's Artifacts announcement](https://claude.com/blog/artifacts-in-claude-code) and the [official Claude Code Artifacts docs](https://code.claude.com/docs/en/artifacts).*
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
