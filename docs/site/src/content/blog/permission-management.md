---
slug: "permission-management"
title: "Claude Code Permissions: Safe vs Fast Development Modes"
description: "Configure Claude Code permissions for your workflow. Learn when to use auto-accept mode and when to maintain strict controls for safety."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, Development]
readingTime: 9
keywords: "claude, code, development, fast, management, modes, permission, permissions, safe, vs"
---

Development

# Claude Code Permissions: Safe vs Fast Development Modes

Configure Claude Code permissions for your workflow. Learn when to use auto-accept mode and when to maintain strict controls for safety.

**Problem**: Claude Code asking for permission on every file edit and command kills your flow and burns time.

**Quick Win**: Press `Shift+Tab` to cycle through permission modes instantly:

```p-4
# Press Shift+Tab to cycle:
normal → auto-accept edits → plan mode → normal
```

You can also [customize this keybinding](/blog/tools/keybindings-guide) if `Shift+Tab` conflicts with your terminal. Now you control your workflow without touching config files. Match your mode to your task and stop the interruption cycle.

## [All Permission Modes](#all-permission-modes)

Claude Code supports five permission modes, each optimized for different development scenarios. The three core modes cycle via `Shift+Tab`, while two additional modes are available through configuration.

### [Normal Mode (`default`)](#normal-mode-default)

Normal mode prompts for every potentially dangerous operation. You'll see confirmation dialogs for:

- File edits and modifications
- Terminal command execution
- System operations
- Directory changes

This mode prioritizes security over speed, making it perfect for:

- Working on production code
- Unfamiliar codebases
- Learning new techniques
- High-risk operations

### [Auto-Accept Mode (`acceptEdits`)](#auto-accept-mode-acceptedits)

Auto-accept mode eliminates permission prompts for file edits, enabling uninterrupted execution for the session. Claude proceeds immediately with approved operations.

Activate by pressing `Shift+Tab` until you see "auto-accept edit on" in the interface.

Best for:

- Large refactoring sessions
- Following well-defined implementation plans
- Research and documentation tasks
- Repetitive operations across multiple files

### [Plan Mode (`plan`)](#plan-mode-plan)

Plan mode restricts Claude to read-only operations, preventing any modifications while allowing comprehensive analysis.

Perfect for:

- Initial codebase exploration
- Architecture analysis
- Planning complex features
- Code review sessions

### [Don't Ask Mode (`dontAsk`)](#dont-ask-mode-dontask)

Don't Ask mode auto-denies all tool usage **unless** the tool is explicitly pre-approved via `/permissions` or your `permissions.allow` rules. Claude will not prompt you for confirmation. If a tool is not in the allow list, it gets silently denied.

Best for:

- CI/CD pipelines where no human is present to approve
- Locked-down environments with a known set of allowed operations
- Running Claude with a strict, pre-configured permission policy

### [Bypass Permissions Mode (`bypassPermissions`)](#bypass-permissions-mode-bypasspermissions)

Bypass mode skips **all** permission checks. Claude executes any tool without prompting.

```p-4
# CLI flag equivalent:
claude --dangerously-skip-permissions
```

**Only use this in fully isolated environments** like containers, VMs, or ephemeral CI runners where Claude cannot cause lasting damage. This mode exists for automation scenarios where the environment itself provides the safety boundary.

> **Warning**: Administrators can disable this mode entirely by setting `disableBypassPermissionsMode` to `"disable"` in managed settings. If your organization blocks this mode, neither the setting nor the CLI flag will work.

### [Setting a Persistent Default Mode](#setting-a-persistent-default-mode)

Instead of cycling modes each session, set your preferred default in `settings.json`:

```p-4
{
  "defaultMode": "acceptEdits"
}
```

Valid values: `default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions`. This saves your preference across sessions so you start in the right mode every time.

## [Managing Permissions with /permissions](#managing-permissions-with-permissions)

Instead of manually editing JSON files, use the built-in `/permissions` command:

```p-4
# Launch the interactive permissions UI
/permissions
```

This interface lets you:

- View currently allowed and denied tools
- Grant permission to specific tools or patterns
- Block access to tools you want to restrict
- See which settings file each rule comes from
- Make changes without restarting Claude Code

## [Permission Rule Syntax](#permission-rule-syntax)

Permission rules follow the format `Tool` or `Tool(specifier)`. Rules live in the `permissions` object of your `settings.json`:

```p-4
{
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "deny": ["Bash(rm *)"],
    "ask": ["Bash(git push *)"]
  }
}
```

Three rule types control behavior:

- **Allow** rules let Claude use the tool without prompting
- **Ask** rules prompt for confirmation each time
- **Deny** rules block the tool entirely

Rules evaluate in order: **deny first, then ask, then allow**. The first matching rule wins, so deny rules always take precedence.

### [Matching All Uses of a Tool](#matching-all-uses-of-a-tool)

Use just the tool name to match all invocations:

| Rule | Effect |
| --- | --- |
| `Bash` | Matches all Bash commands |
| `WebFetch` | Matches all web fetch requests |
| `Read` | Matches all file reads |
| `Edit` | Matches all file edits |

`Bash(*)` is equivalent to `Bash` and matches all Bash commands.

### [Bash Wildcard Patterns](#bash-wildcard-patterns)

Bash rules support glob patterns with `*`. Wildcards can appear at any position:

```p-4
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git commit *)",
      "Bash(git * main)",
      "Bash(* --version)",
      "Bash(* --help *)"
    ],
    "deny": ["Bash(git push *)"]
  }
}
```

**Word boundary semantics**: The space before `*` matters. `Bash(ls *)` matches `ls -la` but not `lsof`, while `Bash(ls*)` matches both.

**Shell operator awareness**: Claude Code understands shell operators. A rule like `Bash(safe-cmd *)` will **not** match `safe-cmd && malicious-cmd`. This prevents chained command exploitation.

> **Warning**: Bash patterns that constrain command arguments are fragile. For example, `Bash(curl http://github.com/ *)` intends to restrict curl to GitHub URLs, but won't match variations like options before the URL, different protocols, or variable expansion. For reliable URL filtering, restrict Bash network tools and use `WebFetch` with domain rules instead.

### [Read and Edit Patterns](#read-and-edit-patterns)

Read and Edit rules follow gitignore-style path patterns with four distinct types:

| Pattern | Meaning | Example |
| --- | --- | --- |
| `//path` | Absolute path from filesystem root | `Read(//Users/alice/secrets/**)` |
| `~/path` | Path from home directory | `Read(~/Documents/*.pdf)` |
| `/path` | Relative to the settings file | `Edit(/src/**/*.ts)` |
| `path` or `./path` | Relative to current directory | `Read(*.env)` |

> **Important**: A pattern like `/Users/alice/file` is **not** an absolute path. It resolves relative to your settings file. Use `//Users/alice/file` for true absolute paths.

In gitignore patterns, `*` matches files in a single directory while `**` matches recursively across directories. To allow all file access, use just the tool name without parentheses: `Read`, `Edit`, or `Write`.

### [WebFetch Domain Rules](#webfetch-domain-rules)

Control which domains Claude can fetch from:

```p-4
{
  "permissions": {
    "allow": ["WebFetch(domain:docs.anthropic.com)"],
    "deny": ["WebFetch(domain:internal.company.com)"]
  }
}
```

### [MCP Tool Patterns](#mcp-tool-patterns)

Control MCP server access at the server or tool level:

| Rule | Effect |
| --- | --- |
| `mcp__puppeteer` | Matches any tool from the puppeteer server |
| `mcp__puppeteer__*` | Same as above (wildcard syntax) |
| `mcp__puppeteer__puppeteer_navigate` | Matches only the navigate tool specifically |

### [Task (Subagent) Rules](#task-subagent-rules)

Control which subagents Claude can spawn using `Task(AgentName)`:

```p-4
{
  "permissions": {
    "deny": ["Task(Explore)"]
  }
}
```

Available agent names include `Explore`, `Plan`, and `Verify`. You can also use the `--disallowedTools` CLI flag to disable specific agents at startup.

### [Extending Permissions with Hooks](#extending-permissions-with-hooks)

[PreToolUse hooks](/blog/tools/hooks/hooks-guide) run before the permission system and can approve, deny, or modify tool calls at runtime. This gives you programmatic control over permissions beyond static rules. See the [Permission Hook guide](/blog/tools/hooks/permission-hook-guide) for a production-ready implementation.

## [How Permissions Work with Sandboxing](#how-permissions-work-with-sandboxing)

Permissions and sandboxing are complementary security layers providing defense-in-depth:

- **Permissions** control which tools Claude can use and which files or domains it can access. They apply to all tools (Bash, Read, Edit, WebFetch, MCP, and others).
- **Sandboxing** provides OS-level enforcement that restricts what Bash commands can access at the filesystem and network level. It applies **only** to Bash commands and their child processes.

Use both together for the strongest security posture:

- Permission deny rules stop Claude from even attempting to access restricted resources
- Sandbox restrictions prevent Bash commands from reaching resources outside defined boundaries, even if a prompt injection bypasses Claude's decision-making
- Filesystem restrictions in the sandbox use `Read` and `Edit` deny rules (not separate sandbox configuration)
- Network restrictions combine `WebFetch` permission rules with the sandbox's `allowedDomains` list

Enable sandboxing with the `/sandbox` command. On macOS it works out of the box using Seatbelt. On Linux and WSL2, install `bubblewrap` and `socat` first.

## [Managed Permission Settings](#managed-permission-settings)

For organizations that need centralized control, administrators can deploy managed settings files that cannot be overridden by users or projects:

| Setting | Effect |
| --- | --- |
| `allowManagedPermissionRulesOnly` | When `true`, only permission rules defined in managed settings apply. User and project rules are ignored. |
| `disableBypassPermissionsMode` | Set to `"disable"` to prevent `bypassPermissions` mode and the `--dangerously-skip-permissions` CLI flag. |

Managed settings file locations:

- **macOS**: `/Library/Application Support/ClaudeCode/managed-settings.json`
- **Linux/WSL**: `/etc/claude-code/managed-settings.json`
- **Windows**: `C:\Program Files\ClaudeCode\managed-settings.json`

These are system-wide paths (not user home directories) requiring administrator privileges. They follow the same format as regular settings files but take the highest precedence in the [settings hierarchy](/blog/guide/configuration-basics).

## [Development Scenario Strategies](#development-scenario-strategies)

### [Early Development (Use Normal Mode)](#early-development-use-normal-mode)

When starting new projects or exploring unfamiliar code:

- Keep all permissions manual
- Review each suggested change
- Learn how Claude approaches problems
- Build confidence in the AI's decisions

### [Active Development (Use Auto-Accept)](#active-development-use-auto-accept)

During intensive coding sessions:

- Enable auto-accept for trusted file types
- Allow common commands (npm, git status)
- Maintain prompts for system operations
- Enable uninterrupted workflow

### [Code Review (Use Plan Mode)](#code-review-use-plan-mode)

When analyzing existing codebases:

- Switch to plan mode for safety
- Let Claude explore without modifications
- Generate analysis and recommendations
- Switch modes only when ready to implement

## [Common Permission Pitfalls](#common-permission-pitfalls)

**Over-permissioning**: Avoid `bypassPermissions` mode unless you are running in a fully isolated container or VM. Use `dontAsk` mode with explicit allow rules for a safer "hands-off" approach.

**Under-permissioning**: Constantly clicking "Allow" defeats the purpose. Use `/permissions` to pre-approve repeat operations, or consider the `acceptEdits` mode for active development sessions.

**Mode Confusion**: Check your current mode before starting work. The mode indicator appears in the UI. Set `defaultMode` in settings.json if you always want to start in a specific mode.

**Blanket Permissions**: Avoid allowing all bash commands. Use specific patterns like `Bash(npm run *)` to limit scope. Remember that deny rules always win over allow rules.

**Fragile Argument Patterns**: Do not rely on Bash rules to restrict command arguments (like constraining `curl` to specific URLs). Use `WebFetch` domain rules for reliable URL filtering instead.

## [What's Next](#whats-next)

Master your development workflow by learning complementary techniques:

- Automate permission decisions with [hooks](/blog/tools/hooks/hooks-guide) and the [Permission Hook](/blog/tools/hooks/permission-hook-guide)
- Customize your [keybindings](/blog/tools/keybindings-guide) for faster mode cycling
- Optimize your [feedback loops](/blog/guide/development/feedback-loops) for faster iteration
- Set up efficient [todo workflows](/blog/guide/development/todo-workflows) for task management
- Configure [git integration](/blog/guide/development/git-integration) for seamless version control
- Explore [configuration basics](/blog/guide/configuration-basics) for settings.json and advanced setup

Five permission modes for five development scenarios. `default` for safety, `acceptEdits` for productivity, `plan` for exploration, `dontAsk` for automation, and `bypassPermissions` for isolated environments. Match the mode to your current needs, and layer sandboxing on top for defense-in-depth.

Last updated on

[Previous

Git Integration](/blog/guide/development/git-integration)[Next

Feedback Loops](/blog/guide/development/feedback-loops)
