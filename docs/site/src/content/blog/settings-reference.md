---
slug: "settings-reference"
title: "Claude Code Settings Reference (Complete Config Guide)"
description: "Complete reference for Claude Code settings.json, environment variables, and the 5-scope hierarchy. Every setting key documented."
date: "2026-02-03"
author: "Max Ritter"
tags: [Guide]
readingTime: 16
keywords: "claude, code, complete, config, guide, reference, settings"
---

# Claude Code Settings Reference: Every Config Option Explained

Complete reference for Claude Code settings.json, environment variables, and the 5-scope hierarchy. Every setting key documented.

Most Claude Code frustrations trace back to one root cause: configuration that doesn't match how you actually work. You're either approving every command manually, missing team-shared defaults, or wondering why a setting you changed has no effect.

The fix is understanding Claude Code's settings system. Not just the keys and values, but the hierarchy that decides which setting wins when multiple scopes conflict.

**Quick Win**: Add a `$schema` line to your `settings.json` and get instant autocomplete for every option:

```p-4
{
  "$schema": "https://json-schema.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

That schema enables autocompletion and inline validation in VS Code, Cursor, and any editor with JSON schema support.

## [The 5-Scope Hierarchy](#the-5-scope-hierarchy)

Claude Code settings follow a strict precedence system. Understanding this hierarchy is the difference between "my setting isn't working" and "I put it in the wrong scope."

### [Scope Precedence (Highest to Lowest)](#scope-precedence-highest-to-lowest)

| Priority | Scope | Location | Who It Affects | Shared? |
| --- | --- | --- | --- | --- |
| 1 | **Managed** | System directories | All users on machine | Yes (IT-deployed) |
| 2 | **Command line** | CLI flags | Current session only | No |
| 3 | **Local** | `.claude/settings.local.json` | You, this project | No (gitignored) |
| 4 | **Project** | `.claude/settings.json` | All collaborators | Yes (in git) |
| 5 | **User** | `~/.claude/settings.json` | You, all projects | No |

The rule is straightforward: higher-scoped settings always override lower ones. If your IT team sets a managed policy that denies `Bash(curl *)`, no user or project setting can override it. Period.

### [When to Use Each Scope](#when-to-use-each-scope)

**Managed** is for organizations that need enforcement without exceptions:

- Security policies (deny access to credentials, block destructive commands)
- Compliance rules that apply across every developer and every project
- Standardized hooks or MCP server configurations deployed by IT

**Command line** is for one-off session overrides:

- Testing with a different model: `claude --model claude-sonnet-4-5-20250929`
- Running with extra permissions for a specific task
- Debugging with `--debug` flag

**Local** is your personal playground for a specific repo:

- Override a project setting that doesn't fit your machine
- Test a hook before proposing it to the team
- Machine-specific paths (your SSH key location, local proxy port)

**Project** is for team alignment:

- [Permission rules](/blog/guide/development/permission-management) everyone should follow
- Shared hooks for auto-formatting or linting
- MCP server configurations the whole team uses
- CLAUDE.md instructions for project context

**User** is your personal defaults:

- Preferred language, theme, and output style
- Plugins you use across every project
- Global permission rules (like always denying access to `~/.ssh`)

### [Managed Settings Paths by OS](#managed-settings-paths-by-os)

Managed settings require administrator privileges and live outside user home directories:

| Operating System | Path |
| --- | --- |
| **macOS** | `/Library/Application Support/ClaudeCode/` |
| **Linux / WSL** | `/etc/claude-code/` |
| **Windows** | `C:\Program Files\ClaudeCode\` |

Two files go here: `managed-settings.json` for settings and `managed-mcp.json` for MCP servers.

## [Complete Settings File Locations](#complete-settings-file-locations)

Every configuration surface in Claude Code maps to a specific file at each scope:

| Feature | User | Project (shared) | Local (personal) |
| --- | --- | --- | --- |
| **Settings** | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| **Subagents** | `~/.claude/agents/` | `.claude/agents/` | N/A |
| **MCP servers** | `~/.claude.json` | `.mcp.json` | `~/.claude.json` (per-project) |
| **Plugins** | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| **CLAUDE.md** | `~/.claude/CLAUDE.md` | `CLAUDE.md` or `.claude/CLAUDE.md` | `CLAUDE.local.md` |

Claude Code automatically creates timestamped backups of configuration files and retains the five most recent. So if you break something, your last working config is recoverable.

## [All Settings Keys by Category](#all-settings-keys-by-category)

Here is every available key you can put in `settings.json`, organized by what it controls.

### [General Settings](#general-settings)

| Key | Description | Default | Example |
| --- | --- | --- | --- |
| `model` | Override the default model | (system default) | `"claude-sonnet-4-5-20250929"` |
| `language` | Claude's preferred response language | English | `"japanese"` |
| `outputStyle` | Adjust system prompt style | (none) | `"Explanatory"` |
| `cleanupPeriodDays` | Days before inactive sessions are deleted | `30` | `20` |
| `autoUpdatesChannel` | Release channel: `"stable"` or `"latest"` | `"latest"` | `"stable"` |
| `showTurnDuration` | Show response timing ("Cooked for 1m 6s") | `true` | `false` |
| `spinnerVerbs` | Customize spinner text | (defaults) | `{"mode": "append", "verbs": ["Pondering"]}` |
| `spinnerTipsEnabled` | Show tips while Claude works | `true` | `false` |
| `terminalProgressBarEnabled` | Terminal progress bar (iTerm2, Windows Terminal) | `true` | `false` |
| `alwaysThinkingEnabled` | Enable extended thinking by default | `false` | `true` |
| `plansDirectory` | Where plan files are stored | `~/.claude/plans` | `"./plans"` |
| `respectGitignore` | `@` file picker respects `.gitignore` | `true` | `false` |
| `companyAnnouncements` | Messages shown at startup (random cycle) | (none) | `["Review guidelines at docs.acme.com"]` |

### [Permission Settings](#permission-settings)

These live inside the `"permissions"` object. For a deep dive into how permissions work in practice, see the [permission management guide](/blog/guide/development/permission-management).

| Key | Description | Example |
| --- | --- | --- |
| `allow` | Rules to auto-allow tool use | `["Bash(npm run lint)", "Read(~/.zshrc)"]` |
| `ask` | Rules that require confirmation | `["Bash(git push *)"]` |
| `deny` | Rules to block tool use entirely | `["WebFetch", "Bash(curl *)", "Read(./.env)"]` |
| `additionalDirectories` | Extra directories Claude can access | `["../docs/", "../shared/"]` |
| `defaultMode` | Default permission mode at launch | `"acceptEdits"` |
| `disableBypassPermissionsMode` | Block `--dangerously-skip-permissions` | `"disable"` |

**Permission rule evaluation order**: Deny rules are checked first, then ask, then allow. First match wins.

**Rule syntax examples:**

| Rule | What It Matches |
| --- | --- |
| `Bash` | All Bash commands |
| `Bash(npm run *)` | Commands starting with `npm run` |
| `Read(./.env)` | Reading the `.env` file |
| `Read(./secrets/**)` | Reading anything in secrets/ |
| `WebFetch(domain:example.com)` | Fetch requests to example.com |

### [Sandbox Settings](#sandbox-settings)

These live inside the `"sandbox"` object and control bash command isolation. Filesystem and network restrictions use permission rules (Read, Edit, WebFetch), not sandbox settings.

| Key | Description | Default | Example |
| --- | --- | --- | --- |
| `enabled` | Enable bash sandboxing | `false` | `true` |
| `autoAllowBashIfSandboxed` | Auto-approve commands when sandboxed | `true` | `true` |
| `excludedCommands` | Commands that run outside sandbox | (none) | `["git", "docker"]` |
| `allowUnsandboxedCommands` | Allow `dangerouslyDisableSandbox` escape | `true` | `false` |
| `enableWeakerNestedSandbox` | Weaker sandbox for Docker (Linux/WSL2) | `false` | `true` |
| `network.allowedDomains` | Outbound domains whitelist | (none) | `["github.com", "*.npmjs.org"]` |
| `network.allowUnixSockets` | Unix socket paths accessible in sandbox | (none) | `["~/.ssh/agent-socket"]` |
| `network.allowAllUnixSockets` | Allow all Unix socket connections | `false` | `true` |
| `network.allowLocalBinding` | Allow binding to localhost (macOS only) | `false` | `true` |
| `network.httpProxyPort` | Custom HTTP proxy port | (auto) | `8080` |
| `network.socksProxyPort` | Custom SOCKS5 proxy port | (auto) | `8081` |

### [Attribution Settings](#attribution-settings)

These live inside the `"attribution"` object and control how Claude marks its contributions in git.

| Key | Description | Default |
| --- | --- | --- |
| `commit` | Text appended to git commit messages | `"Generated with Claude Code..."` + Co-Authored-By trailer |
| `pr` | Text appended to pull request descriptions | `"Generated with Claude Code..."` |

Set either to an empty string `""` to hide that attribution. The older `includeCoAuthoredBy` key still works but is deprecated.

```p-4
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI <your-ai-alias>",
    "pr": ""
  }
}
```

### [Plugin Settings](#plugin-settings)

| Key | Description | Example |
| --- | --- | --- |
| `enabledPlugins` | Toggle plugins on/off | `{"formatter@acme-tools": true}` |
| `extraKnownMarketplaces` | Additional plugin sources | See example below |
| `strictKnownMarketplaces` | (Managed only) Restrict marketplace sources | `[{"source": "github", "repo": "acme/plugins"}]` |

```p-4
{
  "enabledPlugins": {
    "formatter@acme-tools": true,
    "deployer@acme-tools": true,
    "analyzer@security-plugins": false
  },
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": "github",
      "repo": "acme-corp/claude-plugins"
    }
  }
}
```

Marketplace source types include `github` (repo), `git` (any URL), `directory` (local path for development), and `hostPattern` (regex matching).

### [MCP Server Settings](#mcp-server-settings)

| Key | Description | Example |
| --- | --- | --- |
| `enableAllProjectMcpServers` | Auto-approve all project MCP servers | `true` |
| `enabledMcpjsonServers` | Specific MCP servers to approve | `["memory", "github"]` |
| `disabledMcpjsonServers` | Specific MCP servers to reject | `["filesystem"]` |
| `allowedMcpServers` | (Managed only) MCP server allowlist | `[{"serverName": "github"}]` |
| `deniedMcpServers` | (Managed only) MCP server denylist | `[{"serverName": "filesystem"}]` |

For a full walkthrough of MCP configuration, see the [MCP basics guide](/blog/tools/mcp-extensions/mcp-basics).

### [Authentication and Provider Settings](#authentication-and-provider-settings)

| Key | Description | Example |
| --- | --- | --- |
| `apiKeyHelper` | Script to generate auth value | `"/bin/generate_temp_api_key.sh"` |
| `forceLoginMethod` | Restrict to `claudeai` or `console` | `"claudeai"` |
| `forceLoginOrgUUID` | Auto-select organization during login | `"xxxxxxxx-xxxx-..."` |
| `awsAuthRefresh` | Script to refresh AWS credentials | `"aws sso login --profile myprofile"` |
| `awsCredentialExport` | Script outputting AWS credential JSON | `"/bin/generate_aws_grant.sh"` |
| `otelHeadersHelper` | Script generating OpenTelemetry headers | `"/bin/generate_otel_headers.sh"` |

### [Hook and Advanced Settings](#hook-and-advanced-settings)

| Key | Description | Example |
| --- | --- | --- |
| `hooks` | Lifecycle event hook configuration | See [hooks guide](/blog/tools/hooks/hooks-guide) |
| `disableAllHooks` | Disable all hooks | `true` |
| `allowManagedHooksOnly` | (Managed only) Block user/project hooks | `true` |
| `allowManagedPermissionRulesOnly` | (Managed only) Block user/project permission rules | `true` |
| `fileSuggestion` | Custom `@` file autocomplete script | `{"type": "command", "command": "~/.claude/file-suggestion.sh"}` |
| `statusLine` | Custom status line display | `{"type": "command", "command": "~/.claude/statusline.sh"}` |
| `env` | Environment variables for every session | `{"FOO": "bar"}` |

### [File Suggestion Configuration](#file-suggestion-configuration)

If your project is a large monorepo where the default file picker is slow, you can replace it with a custom command:

```p-4
{
  "fileSuggestion": {
    "type": "command",
    "command": "~/.claude/file-suggestion.sh"
  }
}
```

The command receives JSON via stdin with a `query` field (`{"query": "src/comp"}`) and outputs newline-separated file paths to stdout (limited to 15 results). The same environment variables available to [hooks](/blog/tools/hooks/hooks-guide) are accessible here, including `CLAUDE_PROJECT_DIR`.

## [Essential Environment Variables](#essential-environment-variables)

Claude Code recognizes roughly 70 environment variables. Most are niche, but about 20 of them show up regularly in real workflows. Here are the ones worth knowing, organized by what you're trying to do.

### [Model and Provider](#model-and-provider)

| Variable | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | API key for direct API access |
| `ANTHROPIC_MODEL` | Override the default model |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Model name for Sonnet alias |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents (separate from main model) |
| `CLAUDE_CODE_USE_BEDROCK` | Route through AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Route through Google Vertex |

The model aliases (`ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`) are useful when your organization runs custom fine-tuned models behind the standard aliases. Set the alias once and every session picks it up.

### [Performance Tuning](#performance-tuning)

| Variable | Purpose |
| --- | --- |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens (default: 32K, max: 64K) |
| `MAX_THINKING_TOKENS` | Extended thinking budget (default: 31,999, set 0 to disable) |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | % of context capacity (1-100) triggering auto-compaction |
| `BASH_DEFAULT_TIMEOUT_MS` | Default bash command timeout |
| `BASH_MAX_TIMEOUT_MS` | Maximum bash timeout Claude can set |
| `BASH_MAX_OUTPUT_LENGTH` | Max bash output chars before truncation |

`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` is particularly worth knowing about. By default, auto-compaction triggers when context fills to a certain threshold. If you're working on a task that needs deep context and you'd rather compact later (or earlier), this variable gives you control. For more on managing your context window effectively, see the [context management guide](/blog/guide/mechanics/context-management).

### [Privacy and Telemetry](#privacy-and-telemetry)

| Variable | Purpose |
| --- | --- |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable updates, telemetry, error reporting all at once |
| `DISABLE_TELEMETRY` | Opt out of Statsig telemetry |
| `DISABLE_ERROR_REPORTING` | Opt out of Sentry error reporting |
| `CLAUDE_CODE_HIDE_ACCOUNT_INFO` | Hide email and org name from UI |
| `DISABLE_AUTOUPDATER` | Disable automatic version updates |

`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is the all-in-one toggle. It bundles `DISABLE_AUTOUPDATER`, `DISABLE_BUG_COMMAND`, `DISABLE_ERROR_REPORTING`, and `DISABLE_TELEMETRY` into a single switch. Useful for air-gapped or privacy-sensitive environments where you want to minimize outbound connections.

### [Session Control](#session-control)

| Variable | Purpose |
| --- | --- |
| `CLAUDE_CODE_TASK_LIST_ID` | Share a task list across multiple sessions |
| `CLAUDE_CODE_ENABLE_TASKS` | Set `false` to revert to old TODO list |
| `CLAUDE_CODE_SHELL` | Override automatic shell detection |
| `CLAUDE_CONFIG_DIR` | Custom config/data directory location |
| `MCP_TIMEOUT` | Timeout in ms for MCP server startup |
| `MCP_TOOL_TIMEOUT` | Timeout in ms for MCP tool execution |

The MCP timeout variables are worth setting if you run resource-heavy MCP servers (database connections, browser automation). The defaults work for lightweight tools, but anything that needs initialization time benefits from explicit timeouts.

You can set environment variables in two ways: export them in your shell profile, or add them to the `"env"` object in `settings.json` for persistence across sessions without modifying shell configs.

## [Practical Configuration Examples](#practical-configuration-examples)

### [Starter Config (Personal Use)](#starter-config-personal-use)

A minimal `~/.claude/settings.json` for individual developers:

```p-4
{
  "$schema": "https://json-schema.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(~/.ssh/**)"]
  },
  "showTurnDuration": true,
  "autoUpdatesChannel": "stable"
}
```

### [Team Config (Project Scope)](#team-config-project-scope)

A `.claude/settings.json` committed to your repo:

```p-4
{
  "$schema": "https://json-schema.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Bash(npx prettier --write *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(rm -rf *)",
      "Bash(git push --force *)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\""
          }
        ]
      }
    ]
  },
  "attribution": {
    "commit": "Generated with Claude Code\n\nCo-Authored-By: Claude <noreply>",
    "pr": "Generated with Claude Code"
  }
}
```

### [Enterprise Config (Managed Scope)](#enterprise-config-managed-scope)

A `managed-settings.json` deployed to system directories:

```p-4
{
  "$schema": "https://json-schema.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Bash(curl *)",
      "Bash(wget *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./config/credentials.*)"
    ],
    "disableBypassPermissionsMode": "disable"
  },
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false,
    "network": {
      "allowedDomains": [
        "github.com",
        "*.npmjs.org",
        "registry.yarnpkg.com",
        "*.internal.acme.com"
      ]
    }
  },
  "allowManagedHooksOnly": true,
  "allowManagedPermissionRulesOnly": true,
  "forceLoginMethod": "console",
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "acme-corp/approved-plugins"
    }
  ],
  "companyAnnouncements": [
    "All code requires review before merge. See docs.acme.com/security",
    "Report AI-related security concerns to the security team"
  ]
}
```

This locks down network access, forces sandbox mode, restricts plugins to approved sources, and prevents users from bypassing permissions.

## [Settings Precedence in Practice](#settings-precedence-in-practice)

Understanding precedence prevents the most common configuration headaches. Here are the scenarios that trip people up, with clear answers.

**Scenario 1: Permission conflict across scopes**

Your user settings allow `Bash(curl *)`, but the project settings deny it. Which wins? The project scope (priority 4) beats the user scope (priority 5). So the deny applies. But if you really need curl for your machine, add the allow rule to `.claude/settings.local.json` instead. Local scope (priority 3) beats project scope (priority 4), so your local allow overrides the project deny.

**Scenario 2: Managed override**

Your team's project `settings.json` allows `Bash(rm -rf *)`. IT deploys a managed setting that denies it. The managed setting wins. Always. No user, local, or project setting can override managed scope. This is by design for security compliance.

**Scenario 3: Local experimentation**

You want to test a hook before proposing it to the team. Add it to `.claude/settings.local.json`. It takes priority over the shared `.claude/settings.json` but only applies to you. Claude Code automatically configures git to ignore `.local.` files, so there's no risk of accidentally committing personal settings.

**Scenario 4: Settings merging**

Settings don't simply replace each other. They merge. If your user settings allow `Bash(git status)` and your project settings allow `Bash(npm run lint)`, both rules apply. The merge combines permission arrays. But if the same key has different values at different scopes, the higher-priority scope wins for that specific key.

**Scenario 5: Environment variables in settings vs shell**

If you set `ANTHROPIC_MODEL` both as a shell export and inside `settings.json`'s `env` object, the shell environment variable takes precedence. The `env` object in settings applies at Claude Code startup, but pre-existing shell variables aren't overwritten.

## [How Settings Relate to Other Configuration](#how-settings-relate-to-other-configuration)

Settings files don't exist in isolation. They work alongside several other configuration surfaces.

**[CLAUDE.md files](/blog/guide/mechanics/claude-md-mastery)** contain instructions and context that Claude reads at startup. Think of settings as "what Claude can do" and CLAUDE.md as "what Claude should know." Settings control permissions, tools, and behavior. CLAUDE.md controls knowledge, conventions, and project context.

**[MCP servers](/blog/tools/mcp-extensions/mcp-basics)** extend Claude with additional tools. Their configurations live in separate files (`.mcp.json` for project, `~/.claude.json` for user), but settings control which MCP servers get approved and which get blocked.

**[Hooks](/blog/tools/hooks/hooks-guide)** are configured inside `settings.json` under the `hooks` key. They execute shell commands or LLM prompts at lifecycle events. The `disableAllHooks` and `allowManagedHooksOnly` settings provide top-level control.

**Plugins** are also managed through `settings.json` via `enabledPlugins` and marketplace configuration. The `strictKnownMarketplaces` managed setting gives administrators control over which plugin sources are allowed.

**Subagents** live as Markdown files in `~/.claude/agents/` (user) or `.claude/agents/` (project). They aren't configured through `settings.json` directly, but the same scope hierarchy applies to where they're stored.

## [Config Backup Behavior](#config-backup-behavior)

Claude Code automatically creates timestamped backups when configuration files change. It keeps the five most recent backups per file. If an update breaks your setup, the previous working version is recoverable without git archaeology.

This applies to `settings.json`, `.claude.json`, and other core config files. Combined with the local scope for experimentation, you have a solid safety net for trying new configurations.

## [What to Configure First](#what-to-configure-first)

If you're just getting started with Claude Code settings, tackle these in order:

1. **Permission rules** in project settings. Deny access to `.env` files and secrets. Allow your common build/test commands
2. **A PostToolUse hook** for auto-formatting. This eliminates the single biggest source of approval fatigue
3. **Attribution settings** if you want to customize (or hide) the co-authored-by trailer
4. **User-level defaults** for preferences that apply across all your projects

For a broader overview of the three configuration surfaces (CLAUDE.md, MCP, settings), start with the [configuration basics guide](/blog/guide/configuration-basics).

## [Next Steps](#next-steps)

- Set up [CLAUDE.md files](/blog/guide/mechanics/claude-md-mastery) for persistent project context
- Configure [hooks](/blog/tools/hooks/hooks-guide) to automate your workflow
- Explore [MCP servers](/blog/tools/mcp-extensions/mcp-basics) for extending Claude's capabilities
- Learn [permission management](/blog/guide/development/permission-management) patterns for team security
- Review [configuration basics](/blog/guide/configuration-basics) for the full configuration picture

Last updated on

[Previous

Sandboxing Guide](/blog/guide/sandboxing-guide)[Next

Context Engineering](/blog/guide/mechanics/context-engineering)
