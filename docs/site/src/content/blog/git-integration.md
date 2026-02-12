---
slug: "git-integration"
title: "Claude Code Git Integration: Automated Version Control"
description: "Set up Claude Code's git integration for seamless commits and version control. Learn best practices for AI-assisted development workflows."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, Development]
readingTime: 5
keywords: "automated, claude, code, control, git, integration, version"
---

Development

# Claude Code Git Integration: Automated Version Control

Set up Claude Code's git integration for seamless commits and version control. Learn best practices for AI-assisted development workflows.

**Problem**: You made a bunch of changes with Claude Code and now you need to commit them properly without losing track of what happened.

**Quick Win**: After Claude makes changes, just ask it to commit:

```p-4
claude "commit these changes with a descriptive message"
```

Claude reads the diff, writes a meaningful commit message, and runs `git commit` for you. No fake config commands - just ask.

## [How Claude Code Actually Works with Git](#how-claude-code-actually-works-with-git)

Claude Code runs git commands directly in your terminal. There's no special "auto-commit" mode or configuration - you simply ask Claude to handle git operations and it does.

What Claude can do:

- **Run any git command**: add, commit, push, pull, branch, merge
- **Write commit messages**: Based on the actual changes it made
- **Create branches**: For features or experiments
- **Create PRs**: Using the `gh` CLI if installed
- **Resolve conflicts**: By reading both versions and merging intelligently

The key insight: Claude sees your git history and understands context, so its commit messages actually describe what changed and why.

## [Setting Git Conventions in CLAUDE.md](#setting-git-conventions-in-claudemd)

Instead of fake config commands, use your CLAUDE.md file to set commit conventions:

```p-4
## Git Conventions
 
- Use conventional commits: feat:, fix:, docs:, refactor:
- Keep subject lines under 72 characters
- Always run tests before committing
- Create feature branches for new work
```

Now when you ask Claude to commit, it follows your team's conventions automatically. Learn more in our [CLAUDE.md Mastery guide](/blog/guide/mechanics/claude-md-mastery).

## [Real Git Workflows](#real-git-workflows)

### [Simple Commit After Changes](#simple-commit-after-changes)

```p-4
# Claude just finished implementing a feature
claude "commit these changes"
 
# Or be more specific
claude "commit with message: add user authentication flow"
```

### [Feature Branch Workflow](#feature-branch-workflow)

```p-4
# Start new work on a branch
claude "create a feature branch called auth-improvements and switch to it"
 
# Make changes, then commit
claude "commit the auth changes with a descriptive message"
 
# When ready, create a PR
claude "push this branch and create a PR with a summary of changes"
```

### [Reviewing Before Committing](#reviewing-before-committing)

```p-4
# See what changed first
claude "show me a summary of all uncommitted changes"
 
# Then commit selectively
claude "commit only the changes in src/auth/ with message: refactor auth module"
```

## [Commit Attribution](#commit-attribution)

When Claude Code creates git commits or pull requests, it adds attribution by default. This lets your team (and your future self) know which changes were AI-assisted. The `attribution` setting in your [settings.json](/blog/guide/settings-reference) controls exactly what gets added.

### [Default Attribution](#default-attribution)

**Commits** get two things appended to the commit message:

```p-4
Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply>
```

The first line is a plain-text message. The second is a [git trailer](https://git-scm.com/docs/git-interpret-trailers) that GitHub and other platforms recognize, showing Claude as a co-author on the commit.

**Pull requests** get a simpler attribution in the description:

```p-4
Generated with Claude Code (https://claude.com/claude-code)
```

### [Customizing Attribution](#customizing-attribution)

Configure commit and PR attribution separately in your `settings.json`:

```p-4
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI Assistant <your-ai-alias>",
    "pr": "AI-assisted PR"
  }
}
```

You can change the message text, the Co-Authored-By name and email, or both. The `\n\n` separates the message from git trailers, which is required by the git trailers format.

### [Disabling Attribution](#disabling-attribution)

Set either value to an empty string to hide it:

```p-4
{
  "attribution": {
    "commit": "",
    "pr": ""
  }
}
```

This removes attribution from commits, PRs, or both. Useful for teams that track AI usage through other mechanisms.

### [Migration from includeCoAuthoredBy](#migration-from-includecoauthoredby)

The older `includeCoAuthoredBy` boolean setting is deprecated. If you were using `"includeCoAuthoredBy": false`, migrate to the `attribution` setting:

```p-4
// Old (deprecated)
{ "includeCoAuthoredBy": false }
 
// New (recommended)
{
  "attribution": {
    "commit": "",
    "pr": ""
  }
}
```

The new `attribution` setting gives you finer control since you can disable commit attribution while keeping PR attribution, or vice versa. Place this in your [user, project, or local settings](/blog/guide/settings-reference) depending on your needs.

## [Troubleshooting Git Issues](#troubleshooting-git-issues)

**Error: "nothing to commit"**
Fix: Claude already committed, or changes aren't staged. Ask Claude to check:

```p-4
claude "what's the current git status?"
```

**Error: "permission denied" on push**
Fix: You need to authenticate with your remote. Claude can't do this for you, but it can help diagnose:

```p-4
claude "help me debug this git push error"
```

**Error: Merge conflicts**
Fix: Claude can help resolve them:

```p-4
claude "there are merge conflicts in auth.js - resolve them keeping our new changes"
```

## [Next Steps](#next-steps)

- Set up [feedback loops](/blog/guide/development/feedback-loops) for faster iteration
- Configure [todo workflows](/blog/guide/development/todo-workflows) to track work
- Learn [planning modes](/blog/guide/mechanics/planning-modes) for complex changes
- Customize attribution and other options in the [settings reference](/blog/guide/settings-reference)
- Optimize costs with [usage optimization](/blog/guide/development/usage-optimization)

Git with Claude Code is simple: ask Claude to do git operations, and it does them. No special setup required.

Last updated on

[Previous

InfraOps VPS Guide](/blog/guide/development/infraops-vps-guide)[Next

Permission Management](/blog/guide/development/permission-management)
