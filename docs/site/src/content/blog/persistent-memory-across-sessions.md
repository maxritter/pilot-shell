---
slug: "persistent-memory-across-sessions"
title: "Persistent Memory: How Claude Remembers Across Sessions"
description: "Stop repeating yourself every session. Learn how Pilot gives Claude persistent memory for decisions, discoveries, and project context."
date: "2026-02-08"
author: "Max Ritter"
tags: [Feature, Memory]
readingTime: 4
keywords: "Claude Code memory, persistent memory, Claude Code sessions, AI memory, Claude Code context, session continuity"
---

# Persistent Memory: How Claude Remembers Across Sessions

Every Claude Code session starts with a blank slate. Claude doesn't remember what you did yesterday, what decisions you made, or what bugs you fixed. Persistent memory changes this — it gives Claude access to observations from every past session.

## The Problem

Without memory, you repeat yourself constantly:

- "We decided to use PostgreSQL, not SQLite" — again
- "The auth module is in `src/services/auth.py`" — again
- "Don't modify the legacy API, it's frozen" — again

Each session costs time re-explaining context that Claude should already know. Worse, Claude might make decisions that contradict past ones because it has no record of them.

## How Persistent Memory Works

Pilot's memory system runs as a background service that observes your sessions. It automatically captures:

- **Decisions** — Why you chose one approach over another
- **Discoveries** — Bugs found, workarounds identified, undocumented behavior
- **Changes** — What was built, modified, or refactored
- **Patterns** — Recurring workflows and project conventions

Observations are stored in a local SQLite database with full-text search. At the start of each session, relevant observations are injected into Claude's context based on recency and the current project.

## What Gets Captured

The system categorizes observations automatically:

| Type | Example |
|------|---------|
| **Discovery** | "The payment API returns 429 after 100 requests/minute" |
| **Decision** | "Chose JWT over sessions for stateless auth" |
| **Bugfix** | "Fixed race condition in queue worker by adding mutex" |
| **Change** | "Added retry logic to S3 upload with exponential backoff" |
| **Refactor** | "Split 400-line UserService into UserAuth and UserProfile" |

## Searching Past Work

You can search memory directly during a session. The system uses a 3-layer approach to minimize token usage:

1. **Search** — Find observations by keyword (returns IDs and titles)
2. **Timeline** — See chronological context around a result
3. **Get details** — Fetch full observation text only for relevant IDs

This layered approach means Claude doesn't load hundreds of observations into context — it fetches only what's needed for the current task.

## Privacy

Content wrapped in `<private>` tags is never stored:

```
The API key is <private>sk-abc123...</private>
```

Secrets, credentials, and sensitive data stay out of the memory database entirely.

## The Web Viewer

Pilot includes a real-time viewer at `http://localhost:41777` where you can browse all observations as they're captured. This is useful for:

- Verifying what Claude learned during a session
- Finding past decisions when onboarding new team members
- Debugging why Claude made a particular choice

## Practical Impact

With persistent memory, session 50 of a project is as productive as session 1. Claude knows your architecture, your conventions, your past decisions, and your preferences — without you repeating any of it.

Combined with Endless Mode, this means Claude can work on multi-week projects with full continuity. The context window limits a single session, but memory bridges the gaps between them.
