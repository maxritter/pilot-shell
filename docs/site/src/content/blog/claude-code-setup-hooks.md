---
slug: "claude-code-setup-hooks"
title: "Claude Code Setup Hooks: Automate Onboarding and Maintenance"
description: "Setup hooks combine deterministic scripts with agentic oversight. Automate installation, maintenance, and CI/CD with Claude Code."
date: "2026-01-27"
author: "Max Ritter"
tags: [Guide, Hooks]
readingTime: 7
keywords: "automate, claude, code, hooks, maintenance, onboarding, setup"
---

Hooks

# Claude Code Setup Hooks: Onboard Engineers in Minutes, Not Days

Setup hooks combine deterministic scripts with agentic oversight. Automate installation, maintenance, and CI/CD with Claude Code.

You can tell how great an engineering team is by the time it takes for a new engineer to run the project locally.

For great teams, it's one link, one doc, a few commands. For most teams, it's one to two days of pair programming, Slack messages, rummaging through outdated docs, and tons of back and forth testing.

In the age of agents, we can do better.

## [The Problem with Traditional Approaches](#the-problem-with-traditional-approaches)

Setting up a codebase forces you to choose between bad options:

**Pure scripts** are predictable but brittle. They run the same commands every time, but they can't adapt when something goes wrong. When the database connection fails or a dependency is missing, the script just crashes.

**Pure agents** are smart but unpredictable. You can't rely on them for CI/CD pipelines where you need the exact same behavior every time.

**Pure docs** are flexible but manual. Nobody reads them, and they drift out of sync with reality within weeks.

The trick is combining all three. Your deterministic scripts handle execution. Agents provide oversight. The result: **a living document that executes**.

## [What Setup Hooks Do](#what-setup-hooks-do)

Setup hooks were released in Claude Code on January 25th, 2026. They're a special hook type that runs *before* your session starts. When you run:

```p-4
claude --init
```

The setup hook runs first, then Claude boots up. The hook can install dependencies, initialize databases, and set up your environment. When it finishes, Claude sees the results and knows what happened.

Here's where it gets interesting. You can pass a prompt *after* the init flag:

```p-4
claude --init "/install"
```

Now the hook runs first, then the `/install` command executes automatically. The agent reads the log files, analyzes what happened, and reports the results.

## [Three Modes of Operation](#three-modes-of-operation)

This creates three ways to set up your codebase:

```p-4
┌─────────────────────────────────────────────────────────┐
│  DETERMINISTIC          AGENTIC           INTERACTIVE   │
│  (hooks only)           (hooks + prompt)  (hooks + Qs)  │
│                                                         │
│  claude --init          /install          /install true │
│                                                         │
│  - Fast                 - Supervised      - Asks Qs     │
│  - Predictable          - Diagnostic      - Adapts      │
│  - CI-friendly          - Reports status  - Context-    │
│                                             aware       │
└─────────────────────────────────────────────────────────┘
```

**Deterministic mode**: The script runs alone. Fast, predictable, perfect for CI/CD where you need identical behavior every time.

**Agentic mode**: The script runs, then an agent analyzes the results. It reads log files, interprets errors, and tells you what happened in plain language.

**Interactive mode**: The script runs, then the agent asks questions. "Fresh database or keep existing data? Full install or minimal? Should I verify your environment first?"

The script is the source of truth. Both hooks and prompts execute the same script. The difference is whether an agent supervises, and whether it asks you questions first.

## [A Command Launcher for Everything](#a-command-launcher-for-everything)

[Just](https://github.com/casey/just) is a simple command runner that works perfectly with setup hooks. Think of it as a launchpad for your engineering work. Instead of remembering flags and syntax, you type `just` and see all available commands:

```p-4
just          # See all commands
just cldi     # Deterministic setup
just cldii    # Agentic setup (with reporting)
just cldit    # Interactive setup (asks questions)
```

Here's what the justfile looks like:

```p-4
# Deterministic codebase setup
cldi:
  claude --init
 
# Agentic codebase setup
cldii:
  claude --init "/install"
 
# Interactive setup (asks questions)
cldit:
  claude --init "/install true"
 
# Deterministic maintenance
cldm:
  claude --maintenance
 
# Agentic maintenance (with reporting)
cldmm:
  claude --maintenance "/maintenance"
```

You, your team, and your agents don't need to remember flags more than once. They just run `just cldii` and everything works.

## [When to Use Each Mode](#when-to-use-each-mode)

| Scenario | Mode | Command |
| --- | --- | --- |
| CI/CD pipeline | Deterministic | `claude --init-only` |
| Quick local setup | Deterministic | `just cldi` |
| Setup failed, need diagnosis | Agentic | `just cldii` |
| New engineer, unfamiliar codebase | Interactive | `just cldit` |
| Weekly dependency updates | Agentic | `just cldmm` |

The `--init-only` flag is specifically for pipelines. It runs the hook and exits cleanly with a return code, no interactive session.

## [The Interactive Experience](#the-interactive-experience)

This is where it gets powerful for onboarding. When a new engineer runs `just cldit`, the agent walks them through setup:

```p-4
Agent: How should I handle the database?

┌─ Database Setup ─────────────────────────────────┐
│  ○ Fresh database (Recommended)                  │
│  ○ Keep existing                                 │
│  ○ Skip database setup                           │
└──────────────────────────────────────────────────┘
```

The agent asks about installation mode, environment variables, and whether to verify prerequisites. It adapts to the answers and runs the appropriate steps.

This is something scripts can never do. They run the same way every time. Agents can ask clarifying questions mid-workflow and adapt to the context.

## [How It Works Under the Hood](#how-it-works-under-the-hood)

Setup hooks are one of [12 lifecycle events](/blog/tools/hooks/hooks-guide) in Claude Code's hook system. They're configured in `.claude/settings.json`:

```p-4
{
  "hooks": {
    "Setup": [
      {
        "matcher": "init",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/setup_init.py",
            "timeout": 120
          }
        ]
      },
      {
        "matcher": "maintenance",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/setup_maintenance.py",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

The hook script runs commands and logs everything:

```p-4
def main():
    # Install backend dependencies
    run(["uv", "sync"], cwd="apps/backend")
 
    # Install frontend dependencies
    run(["npm", "install"], cwd="apps/frontend")
 
    # Initialize database
    run(["uv", "run", "python", "init_db.py"], cwd="apps/backend")
 
    # Tell Claude what happened
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "Setup",
            "additionalContext": "Setup complete. Run 'just be' and 'just fe' to start."
        }
    }))
```

The `/install` [slash command](/blog/guide/mechanics/claude-skills-guide) then reads the log file and reports the results:

```p-4
---
description: Run setup and report installation results
---
 
## Workflow
 
1. Run /prime to understand the codebase
2. Read the log file at .claude/hooks/setup.init.log
3. Analyze for successes and failures
4. Write results to app_docs/install_results.md
5. Report to user
```

If something fails, the agent has context to diagnose it. You can add common issues and solutions to the prompt, and the agent will follow them automatically.

## [Why This Pattern Matters](#why-this-pattern-matters)

Think about the time it takes to onboard a new engineer. Now think about how fast you want your team to grow. Can you build a prompt that runs the setup and installation process? Can you make it interactive to make every step clear?

The answer is yes. Agents are good enough. You just need to standardize it.

**Determinism preserved**: The hook runs the same script every time. No LLM variance in execution. Agents only analyze *after* the deterministic work is done.

**CI compatible**: GitHub Actions can run `claude --init-only` and get a clean exit code.

**Interactive when it matters**: New hires get walked through setup. Veterans run the fast deterministic version.

**A living document that executes**: Your installation process is now in natural language, embedded in prompts that agents follow. When you need to update something, you update the prompt.

## [Getting Started](#getting-started)

Start with the basics: create a `.claude/hooks/setup_init.py` script that installs your dependencies, and configure it in [`.claude/settings.json`](/blog/guide/configuration-basics). Add a `/install` command that reads the log file and reports results. Then wrap it all in a justfile so your team can run `just install` and be done.

For simpler scenarios where you just need to load different context for different session types, see [conditional context loading with slash commands](/blog/guide/mechanics/claude-code-session-context). When you don't need installation scripts, a slash command is often enough.

Setup hooks shine when you want **one command** that installs everything, diagnoses problems, and walks new engineers through the process. Combine deterministic scripts with intelligent agents, and you get the best of both worlds.

Last updated on

[Previous

Hooks Guide](/blog/tools/hooks/hooks-guide)[Next

Stop Hook](/blog/tools/hooks/stop-hook-task-enforcement)
