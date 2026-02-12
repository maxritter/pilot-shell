---
slug: "configuration-basics"
title: "3 Claude Code Config Files (Stop Generic Responses)"
description: "CLAUDE.md, MCP servers, and slash commands. Set up once and Claude Code knows your stack, conventions, and workflows every single session."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide]
readingTime: 8
keywords: "3, basics, claude, code, config, configuration, files, generic, responses, stop"
---

# 3 Claude Code Config Files That Stop Generic Responses Forever

CLAUDE.md, MCP servers, and slash commands. Set up once and Claude Code knows your stack, conventions, and workflows every single session.

Configure Claude Code for your workflow in 3 steps. Proper setup separates productive sessions from frustrating ones.

**Problem**: Claude Code gives generic responses because it lacks context about your project.

**Quick Win**: Create a CLAUDE.md file in your project root:

```p-4
# Project Name: [Your App Name]
 
## Tech Stack
 
- Framework: React 18 / Next.js 15 / Express / Django
- Database: PostgreSQL / MongoDB / MySQL
- Deployment: Vercel / AWS / DigitalOcean
 
## Current Priority
 
[What you're working on this week]
 
## Coding Rules
 
- Use TypeScript for all new files
- Test critical functions
- Comment complex logic
- Use semantic commits
 
## Don't Change
 
- Authentication system (unless explicitly requested)
- Database schema (migration required)
- Production environment variables
```

**Result**: Claude now understands your project and gives contextual advice instead of generic tutorials.

## [Step 1: Essential Project Configuration](#step-1-essential-project-configuration)

Create your configuration files:

```p-4
touch CLAUDE.md                    # Project root - required
mkdir -p .claude/commands          # Custom workflows - optional
```

**CLAUDE.md in project root (Required)** - Your project's AI briefing document:

```p-4
# [Project Name] - Development Context
 
## What This Project Does
 
[2-sentence description of your app's purpose]
 
## Tech Stack & Version
 
- Frontend: React 18.2.0 with TypeScript 5.0
- Backend: Node.js with Express or Next.js App Router
- Database: PostgreSQL 15 with Prisma ORM
- Styling: Tailwind CSS 3.4
 
## File Structure
```

src/
├── app/ # Next.js pages (App Router)
├── components/ # Reusable UI components
├── lib/ # Utilities and configurations
└── types/ # TypeScript definitions

```p-4
## Current Sprint Goals
- [ ] User authentication system
- [ ] Dashboard with user data
- [ ] API endpoints for CRUD operations

## Never Touch Without Permission
- package.json dependencies (ask first)
- Database migrations (explain changes)
- Production environment variables
```

**Success Check**: Claude now mentions your tech stack and current goals in responses.

## [Step 2: MCP Server Setup (Power Features)](#step-2-mcp-server-setup-power-features)

MCP (Model Context Protocol) servers extend Claude's capabilities. Add this to your global settings at `~/.claude/settings.json`:

```p-4
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ACCESS_DIRECTORIES": "/Users/yourname/projects"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

**What This Enables**:

- Claude can read/write files directly
- Search your GitHub repositories
- Access project documentation
- Understand your coding patterns

**Success Check**: Claude can now access files and GitHub repos directly.

## [Step 3: Custom Slash Commands](#step-3-custom-slash-commands)

Create reusable workflows in `.claude/commands/`. Each markdown file becomes a slash command.

**Debug Workflow** (`.claude/commands/debug.md`):

```p-4
# Debug Workflow
 
When debugging:
 
1. Reproduce the error in isolation
2. Check browser console and network tab
3. Add console.logs to trace execution
4. Test with minimal data
5. Check recent changes in git log
6. Ask before suggesting major architecture changes
```

**Test Generation** (`.claude/commands/test.md`):

```p-4
# Test Generation Guidelines
 
For new functions:
 
1. Write unit tests with Jest/Vitest
2. Test happy path and edge cases
3. Mock external dependencies
4. Use descriptive test names
5. Aim for 80% coverage on critical paths
```

**Usage**: Type `/debug` or `/test` in any Claude Code session to invoke these workflows.

**Success Check**: Claude follows your documented processes consistently.

## [Common Configuration Fixes](#common-configuration-fixes)

**Error**: "MCP server not responding"
**Fix**: Check token permissions and directory paths in `settings.json`

**Error**: "Context window exceeded"
**Fix**: Keep CLAUDE.md under 10KB. Split into multiple files if needed:

```p-4
# Main CLAUDE.md (keep short)
 
See also:
 
- .claude/database-schema.md (detailed schema)
- .claude/api-patterns.md (endpoint conventions)
```

**Error**: "Claude forgot my project details"
**Fix**: Verify CLAUDE.md exists in project root (not inside `.claude/` folder)

**Error**: "Generic responses despite configuration"
**Fix**: Run `/init` to regenerate CLAUDE.md, or reference it explicitly in your prompt

## [The settings.json Scope System](#the-settingsjson-scope-system)

Beyond CLAUDE.md, Claude Code uses `settings.json` files to configure permissions, environment variables, model defaults, and tool behavior. Settings follow a **4-scope hierarchy** where more specific scopes override broader ones:

| Scope | Location | Who It Affects | Shared? |
| --- | --- | --- | --- |
| **Managed** | System-level `managed-settings.json` | All users on the machine | Yes (deployed by IT) |
| **User** | `~/.claude/settings.json` | You, across all projects | No |
| **Project** | `.claude/settings.json` | All collaborators on the repo | Yes (committed to git) |
| **Local** | `.claude/settings.local.json` | You, in this repo only | No (gitignored) |

**Precedence order** (highest to lowest): Managed > Command line args > Local > Project > User. Managed settings cannot be overridden, so organizational policies always apply.

Add the `$schema` line to your settings.json for autocomplete and inline validation in VS Code, Cursor, or any editor that supports JSON schemas:

```p-4
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1"
  }
}
```

Claude Code automatically creates timestamped backups of your configuration files and retains the five most recent backups, so you won't lose settings if something goes wrong.

For the complete list of every settings key and its options, see our [settings reference guide](/blog/guide/settings-reference).

### [Key Settings Categories](#key-settings-categories)

Settings.json covers several categories that each have dedicated guides:

- **Permissions** - Control which tools Claude can use, which files it can read, and which commands it can run. Define `allow`, `deny`, and `ask` rules. See [permission management](/blog/guide/development/permission-management).
- **Sandbox** - Isolate bash commands from your filesystem and network with OS-level enforcement. Enable with `/sandbox` or the `sandbox.enabled` setting. See our [sandboxing guide](/blog/guide/sandboxing-guide).
- **Attribution** - Customize or disable the `Co-Authored-By` trailer on git commits and PR descriptions. Configure separately for commits and PRs.
- **Plugins** - Extend Claude Code with skills, agents, hooks, and MCP servers distributed through marketplaces. Control with `enabledPlugins` and `extraKnownMarketplaces`.
- **Model** - Set a permanent default model via the `model` key instead of passing `--model` every session. See [model selection strategies](/blog/models/model-selection).
- **Status Line** - Display live context usage, git branch, model name, or cost data in a persistent status bar. See our [status line guide](/blog/tools/statusline-guide).
- **Keybindings** - Customize keyboard shortcuts with `/keybindings` to create `~/.claude/keybindings.json`. See our [keybindings guide](/blog/tools/keybindings-guide).

## [Essential Environment Variables](#essential-environment-variables)

Environment variables give you fine-grained control over Claude Code behavior. You can set them in your shell profile, pass them inline, or add them to the `env` key in settings.json. Here are the most useful ones for daily development:

| Variable | What It Does |
| --- | --- |
| `ANTHROPIC_MODEL` | Set the default model (e.g., `claude-sonnet-4-20250514`) |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens per response. Default: 32,000. Max: 64,000 |
| `MAX_THINKING_TOKENS` | Control the extended thinking budget. Default: 31,999. Set to `0` to disable |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Trigger auto-compaction at a specific context % (1-100) |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Set the model for sub-agents separately from your main model |
| `BASH_DEFAULT_TIMEOUT_MS` | Default timeout for long-running bash commands |
| `BASH_MAX_OUTPUT_LENGTH` | Max characters in bash output before truncation |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable auto-updates, telemetry, error reporting, and bug reports in one variable |
| `DISABLE_AUTOUPDATER` | Disable automatic updates only (set to `1`) |
| `CLAUDE_CODE_ENABLE_TASKS` | Set to `false` to revert to the previous TODO list system |
| `MAX_MCP_OUTPUT_TOKENS` | Max tokens in MCP tool responses (default: 25,000) |
| `MCP_TIMEOUT` | Timeout in ms for MCP server startup |
| `CLAUDE_CODE_SHELL` | Override automatic shell detection |
| `CLAUDE_CONFIG_DIR` | Store configuration and data files in a custom directory |
| `HTTP_PROXY` / `HTTPS_PROXY` | Route connections through a proxy server |

Set variables inline for a single session or add them to your shell profile for persistence:

```p-4
# Single session
ANTHROPIC_MODEL=claude-sonnet-4-20250514 claude
 
# Persistent (add to ~/.bashrc or ~/.zshrc)
export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
export MAX_THINKING_TOKENS=10000
```

Or configure them in settings.json so they apply automatically:

```p-4
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80",
    "MAX_THINKING_TOKENS": "10000"
  }
}
```

For the full list of ~70 environment variables, see the [settings reference](/blog/guide/settings-reference). For terminal-specific setup like line breaks and notifications, see our [terminal setup guide](/blog/guide/terminal-setup-guide).

## [Global vs Project Configuration](#global-vs-project-configuration)

**Global Settings** (`~/.claude/settings.json`):

- MCP server configurations
- Personal preferences and model defaults
- Universal coding standards

**Project Settings** (project root):

- `CLAUDE.md` - Project context and rules
- `.claude/commands/` - Custom slash commands
- `.claude/settings.json` - Team-shared permissions, hooks, and MCP servers
- `.claude/settings.local.json` - Your personal overrides for this project (gitignored)

**Priority**: Managed > Local > Project > User. Use `/init` to auto-generate a starter CLAUDE.md.

**Multi-Project Setup**: For monorepos or shared team standards, you can load CLAUDE.md files from additional directories using the `--add-dir` flag. See [Loading CLAUDE.md from Additional Directories](/blog/guide/mechanics/claude-md-mastery#loading-claudemd-from-additional-directories) for details.

## [What's Next](#whats-next)

You now have Claude Code configured for maximum productivity. Next steps:

- **Try your first AI-powered build**: [Create your first project](/blog/guide/first-project) with proper configuration
- **Master advanced features**: Learn [terminal control techniques](/blog/guide/mechanics/terminal-main-thread)
- **Optimize performance**: Explore [context management strategies](/blog/guide/mechanics/context-management)
- **Add more power**: Set up [popular MCP servers](/blog/tools/mcp-extensions/best-addons)
- **Join the community**: Get help in our [troubleshooting guide](/blog/guide/troubleshooting)

**Pro Tip**: Keep your CLAUDE.md updated. When you change tech stack or priorities, update the file. Claude's effectiveness depends on current context.

Last updated on

[Previous

First Project](/blog/guide/first-project)[Next

Terminal Setup](/blog/guide/terminal-setup-guide)
