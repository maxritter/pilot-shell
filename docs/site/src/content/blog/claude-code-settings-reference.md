---
slug: "claude-code-settings-reference"
title: "Claude Code Settings: What You Can Configure"
description: "A concise reference for Claude Code settings: scopes, permissions, hooks, MCP servers, environment variables, and project vs user configuration."
date: "2026-02-07"
author: "Max Ritter"
tags: [Reference, Configuration]
readingTime: 5
keywords: "Claude Code settings, settings.json, Claude Code configuration, Claude Code permissions, Claude Code environment variables"
---

# Claude Code Settings: What You Can Configure

Claude Code has a layered settings system with five scopes, from broad defaults to project-specific overrides. Understanding what you can configure — and where — helps you set up Claude exactly how your team needs it.

## The Five Scopes

Settings are applied in order of specificity. More specific scopes override broader ones:

| Scope | Location | Applies To |
|-------|----------|-----------|
| **Default** | Built into Claude Code | Everyone |
| **Enterprise** | Managed policy | Your organization |
| **User** | `~/.claude/settings.json` | All your projects |
| **Project** | `.claude/settings.json` | This project |
| **Local** | `.claude/settings.local.json` | Only you, this project |

The local scope is gitignored — use it for personal preferences that shouldn't affect teammates.

## Key Settings

### Allowed and Blocked Tools

Control which tools Claude can use without asking:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run build)",
      "Read",
      "Edit",
      "Write"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force)"
    ]
  }
}
```

### Model Selection

Set the default model:

```json
{
  "model": "claude-sonnet-4-20250514"
}
```

### MCP Servers

Configure external tool integrations:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstreamapi/context7-mcp@latest"]
    }
  }
}
```

### Hooks

Run scripts on specific events:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "ruff check $CLAUDE_FILE_PATH" }]
      }
    ]
  }
}
```

### Custom Slash Commands

Create project-specific commands in `.claude/commands/`:

```markdown
<!-- .claude/commands/deploy.md -->
Run the deployment pipeline:
1. Run all tests
2. Build the production bundle
3. Deploy to staging
4. Run smoke tests
```

Invoke with `/deploy` in any session.

## Environment Variables

Some settings can also be set via environment variables:

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_USE_BEDROCK` | Use AWS Bedrock as the API provider |
| `CLAUDE_CODE_USE_VERTEX` | Use Google Vertex AI as the API provider |
| `ANTHROPIC_API_KEY` | API key for direct Anthropic access |
| `CLAUDE_CODE_MAX_TURNS` | Maximum agentic turns per session |

## Project vs User Settings

**User settings** (`~/.claude/settings.json`):
- Your preferred model
- Global tool permissions
- Personal MCP servers
- Editor preferences

**Project settings** (`.claude/settings.json`, committed to git):
- Team-agreed tool permissions
- Project-specific hooks (linting, testing)
- Shared MCP servers
- Custom commands

**Local settings** (`.claude/settings.local.json`, gitignored):
- API key overrides
- Personal tool permissions that differ from team
- Debug MCP servers

## How Pilot Configures Settings

During installation, Pilot sets up:

- **Hooks** for TDD enforcement, context monitoring, and tool redirection
- **MCP servers** for persistent memory, web search, and documentation
- **Custom commands** for `/spec`, `/sync`, `/learn`, and `/vault`
- **Rules** for coding standards, testing strategies, and workflow enforcement

These are installed as project settings so they're shared with your team and version-controlled. You can customize any of them by editing the files directly.
