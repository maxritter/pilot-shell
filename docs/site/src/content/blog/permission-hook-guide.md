---
slug: "permission-hook-guide"
title: "Claude Code Permission Hook: Skip Prompts Safely"
description: "Run Claude Code without constant permission prompts or dangerous skip flags. Delegate approvals to an AI reviewer that understands context."
date: "2025-12-07"
author: "Max Ritter"
tags: [Guide, Hooks]
readingTime: 4
keywords: "claude, code, guide, hook, permission, prompts, safely, skip"
---

Hooks

# Claude Code Permission Hook: Uninterrupted Coding Without the Risk

Run Claude Code without constant permission prompts or dangerous skip flags. Delegate approvals to an AI reviewer that understands context.

**Problem**: Every time Claude wants to read a file or run a command, you're clicking "approve." Twenty clicks later, you've lost your flow state and forgotten what you were building.

**Quick Win**: Install the Permission Hook and never click approve again:

```p-4
npm install -g @abdo-el-mobayad/claude-code-fast-permission-hook
cf-approve install
cf-approve config
```

Three commands. Now Claude runs uninterrupted while dangerous operations get blocked automatically. No `--dangerously-skip-permissions` required.

## [The Permission Dilemma](#the-permission-dilemma)

You have two bad options with vanilla Claude Code:

**Option 1: Click approve constantly.** Safe, but flow-destroying. Complex features mean 50+ permission prompts. You lose context. You lose momentum. You lose the magic of AI-assisted coding.

**Option 2: Use `--dangerously-skip-permissions`.** Fast, but terrifying. One hallucinated `rm -rf /` and your system is gone. Fine for throwaway projects. Unacceptable for real work.

The Permission Hook gives you a third option: **intelligent delegation**. Claude runs without interruption. Dangerous commands get blocked automatically. Edge cases go to a fast LLM for context-aware decisions.

## [How It Works: Three-Tier Decision System](#how-it-works-three-tier-decision-system)

When Claude requests permission, the hook evaluates it instantly:

**Tier 1 - Fast Approve (No AI Needed)**

Safe operations pass through immediately:

- Read, Glob, Grep, WebFetch, WebSearch
- Write, Edit, MultiEdit, NotebookEdit
- TodoWrite, Task, all MCP tools

No latency. No cost. Claude keeps working.

**Tier 2 - Fast Deny (No AI Needed)**

Dangerous operations get blocked instantly:

```p-4
# These never execute, period
rm -rf /                      # System destruction
git push --force origin main  # Protected branch overwrite
mkfs /dev/sda                 # Disk formatting
:(){ :|:& };:                  # Fork bomb
```

No AI evaluation needed. Hard-coded rules protect you from catastrophic mistakes.

**Tier 3 - LLM Analysis (Cached)**

Ambiguous operations get sent to a fast, cheap LLM (GPT-4o-mini via OpenRouter) for context-aware evaluation:

```p-4
{
  "tool": "Bash",
  "command": "docker system prune -af",
  "working_directory": "/home/user/project",
  "recent_context": "User asked to clean up Docker resources"
}
```

The LLM sees what you're trying to accomplish and makes an intelligent decision. Decisions are cached - repeat the same command and it's instant.

## [Configuration](#configuration)

The hook stores settings at `~/.claude-code-fast-permission-hook/config.json`:

```p-4
{
  "llm": {
    "provider": "openai",
    "model": "openai/gpt-4o-mini",
    "apiKey": "sk-or-v1-your-key",
    "baseUrl": "https://openrouter.ai/api/v1"
  },
  "cache": {
    "enabled": true,
    "ttlHours": 168
  }
}
```

OpenRouter is recommended for best latency. Get your key at [openrouter.ai](https://openrouter.ai). Cost: roughly **$1 per 5,000+ LLM decisions**. In practice, most operations hit Tier 1 or 2, so a dollar lasts months.

## [Installation Levels](#installation-levels)

**Device Level** (recommended): Configure once in `~/.claude/settings.json`, applies everywhere. Set it and forget it.

**Project Level**: Configure in `.claude/settings.local.json` for project-specific rules.

The installer adds this to your settings:

```p-4
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "cf-approve permission"
          }
        ]
      }
    ]
  }
}
```

## [When Things Go Wrong](#when-things-go-wrong)

**Error: "Permission denied" on all operations**

Fix: Your API key is missing or invalid:

```p-4
cf-approve config
```

Re-enter your OpenRouter key.

**Error: "Hook not triggering"**

Fix: Verify installation:

```p-4
cf-approve doctor
cf-approve status
```

**Behavior seems inconsistent**

Fix: Clear the decision cache:

```p-4
cf-approve clear-cache
```

## [You Can Now Code Without Interruption](#you-can-now-code-without-interruption)

- You just installed context-aware permission automation
- Set up the main [Hooks Guide](/blog/tools/hooks/hooks-guide) for complete hook coverage
- Configure the [Stop Hook](/blog/tools/hooks/stop-hook-task-enforcement) to ensure task completion
- Try [Context Recovery](/blog/tools/hooks/context-recovery-hook) to survive compaction
- Go deeper: Explore [skills](/blog/guide/mechanics/claude-skills-guide) for specialized agent workflows

No more permission fatigue. No more dangerous flags. Just Claude doing what Claude does best - building your software while you focus on the big picture.

Last updated on

[Previous

Skill Activation Hook](/blog/tools/hooks/skill-activation-hook)[Next

MCP Basics](/blog/tools/mcp-extensions/mcp-basics)
