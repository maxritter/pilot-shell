---
slug: "troubleshooting"
title: "Claude Code Not Working? 5 Fixes (90% Success)"
description: "Command not found, invalid API key, 503 errors, slow responses. Run these 5 Claude Code checks in order and you're back to coding fast."
date: "2025-08-16"
author: "Max Ritter"
tags: [Guide]
readingTime: 6
keywords: "5, 90, claude, code, fixes, not, success, troubleshooting, working"
---

# Claude Code Not Working? 5 Fixes That Solve 90% of Problems

Command not found, invalid API key, 503 errors, slow responses. Run these 5 Claude Code checks in order and you're back to coding fast.

Claude Code not working? Here's the fix: 90% of issues are solved by these five quick checks. Run them in order, and you'll be back to coding in minutes.

**Quick diagnosis checklist:**

```p-4
# 1. Check your installation
claude --version
 
# 2. Test your internet connection
ping claude.ai
 
# 3. Verify your API key
echo $ANTHROPIC_API_KEY
 
# 4. Clear session state (inside Claude Code)
/clear
 
# 5. Restart with fresh config
claude config
```

If any command fails, jump to the matching section below for the exact fix.

## [Installation Problems](#installation-problems)

**Error: "command not found: claude"**

Your installation failed or PATH isn't configured. The native installer fixes this automatically:

```p-4
# Reinstall with native installer (recommended)
curl -fsSL https://claude.ai/install.sh | bash  # macOS/Linux
# Windows PowerShell: irm https://claude.ai/install.ps1 | iex
 
# Verify installation
which claude
```

See the [native installer guide](/blog/guide/native-installer) for details.

**Error: "Node.js version not supported"**

Claude Code requires Node.js 18+. Check your version:

```p-4
# Check current version
node --version
 
# If below 18.0, install latest Node.js
# Visit nodejs.org and download the LTS version
```

**Error: "EACCES permission denied"**

Fix npm permissions on macOS/Linux:

```p-4
# Fix npm ownership
sudo chown -R $(whoami) ~/.npm
 
# Alternative: use a version manager like nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

For Windows, run Command Prompt as Administrator and retry installation.

## [Authentication Issues](#authentication-issues)

**Error: "Invalid API key"**

Your API key is missing or incorrect. Set it properly:

```p-4
# Reconfigure Claude Code
claude config
 
# Or set environment variable
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from [console.anthropic.com](https://console.anthropic.com) and ensure no extra spaces.

**Error: "Subscription not recognized"**

Claude Max/Pro authentication problems:

1. Log out of Claude completely in your browser
2. Clear cookies and browser cache
3. Use incognito/private mode to log back in
4. Run `claude config` to re-authenticate

## [Connection Problems](#connection-problems)

**Error: "503 Service Unavailable"**

This is a server-side issue, not your setup:

- Wait 2-5 minutes for Anthropic servers to recover
- Check [status.anthropic.com](https://status.anthropic.com) for service updates
- Don't reinstall - this won't fix server problems

**Claude Code starts but doesn't respond**

Reset your session state:

```p-4
# Clear conversation history (run inside Claude Code)
/clear
 
# Or restart with fresh session
exit
claude
```

If still unresponsive, check your internet connection and try again.

## [Performance Issues](#performance-issues)

**Slow responses or hanging**

Switch to a faster model and optimize context:

```p-4
# Use Claude Sonnet 4 for speed
claude --model claude-sonnet-4-20250514
 
# Compress conversation history (run inside Claude Code)
/compact keep only function names and current errors
```

**"Context window full" errors**

Your conversation is too long. Reset or compress:

```p-4
# Quick fix: start fresh (run inside Claude Code)
/clear
 
# Better fix: compress intelligently
/compact preserve main components and recent changes only
```

## [File Permission Errors](#file-permission-errors)

**Error: "Permission denied on file operations"**

Fix directory permissions:

```p-4
# Check current permissions
ls -la
 
# Fix ownership of project directory
sudo chown -R $(whoami) .
 
# Verify Claude Code can access files
claude --add-dir $(pwd)
```

## [Settings and Configuration Issues](#settings-and-configuration-issues)

**Settings not applying as expected**

When settings behave unexpectedly, the cause is almost always scope precedence. Settings follow this priority: Managed > Command line > Local > Project > User. A setting in `.claude/settings.local.json` overrides the same key in `.claude/settings.json`, which overrides `~/.claude/settings.json`.

```p-4
# Check which settings files exist
ls ~/.claude/settings.json
ls .claude/settings.json
ls .claude/settings.local.json
```

**Managed settings overriding your preferences**

If your IT team deployed `managed-settings.json`, those settings take highest priority and cannot be overridden. On macOS, managed settings live at `/Library/Application Support/ClaudeCode/`. On Linux/WSL, check `/etc/claude-code/`. On Windows, check `C:\Program Files\ClaudeCode\`. If a setting refuses to change, ask your admin whether a managed policy is enforcing it.

**Settings autocomplete not working**

Add the `$schema` line to the top of your settings.json for editor validation and autocomplete:

```p-4
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json"
}
```

For a complete walkthrough of the scope system, see our [configuration basics guide](/blog/guide/configuration-basics#the-settingsjson-scope-system). For the full settings key reference, see the [settings reference](/blog/guide/settings-reference).

## [Sandbox and Security Issues](#sandbox-and-security-issues)

**Error: "bubblewrap not installed" (Linux/WSL2)**

Sandboxing on Linux requires the `bubblewrap` and `socat` packages. Install them and try again:

```p-4
# Debian/Ubuntu
sudo apt install bubblewrap socat
 
# Fedora
sudo dnf install bubblewrap socat
```

**Watchman conflicts with sandbox**

Facebook's Watchman file watcher is incompatible with Claude Code's sandbox. If you see errors related to watchman, disable it or exclude it from the sandbox. The sandbox isolates filesystem access, which conflicts with watchman's monitoring approach.

**Docker commands failing inside sandbox**

Docker needs to run outside the sandbox. Add it to `excludedCommands` in your settings.json:

```p-4
{
  "sandbox": {
    "enabled": true,
    "excludedCommands": ["docker", "docker-compose"]
  }
}
```

For more on sandbox configuration, see our [sandboxing guide](/blog/guide/sandboxing-guide).

## [Debug Environment Variables](#debug-environment-variables)

When diagnosing persistent issues, these environment variables help isolate the problem:

| Variable | What It Does |
| --- | --- |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disables auto-updates, telemetry, error reporting, and bug reports all at once. Useful for isolating network issues. |
| `DISABLE_AUTOUPDATER` | Stops automatic updates only. Set to `1` if updates are causing problems. |
| `DISABLE_ERROR_REPORTING` | Opts out of Sentry error reporting (set to `1`). |
| `DISABLE_TELEMETRY` | Opts out of Statsig telemetry (set to `1`). |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | Disables all background task functionality (set to `1`). |

```p-4
# Run Claude Code with all non-essential traffic disabled
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 claude
 
# Or set just the auto-updater off
DISABLE_AUTOUPDATER=1 claude
```

If you suspect network or proxy issues, you can also set `HTTP_PROXY` or `HTTPS_PROXY` to route traffic through a proxy, or use `NO_PROXY` to bypass proxy for specific domains.

For the full environment variable reference, see [configuration basics](/blog/guide/configuration-basics#essential-environment-variables) or the [settings reference](/blog/guide/settings-reference).

## [Advanced Fixes](#advanced-fixes)

**Nothing else worked? Complete reset:**

```p-4
# 1. Uninstall any existing installation
npm uninstall -g @anthropic-ai/claude-code  # if installed via npm
 
# 2. Remove config files
rm ~/.claude.json
rm -rf ~/.claude/
 
# 3. Fresh install with native installer (recommended)
curl -fsSL https://claude.ai/install.sh | bash  # macOS/Linux
# Windows PowerShell: irm https://claude.ai/install.ps1 | iex
 
# 4. Reconfigure
claude config
```

The [native installer](/blog/guide/native-installer) handles PATH configuration automatically and includes auto-updates.

## [Success Verification](#success-verification)

After fixing issues, verify everything works:

```p-4
# Test basic functionality
claude "write hello world in Python"
 
# Test file operations
echo "# Test" > test.md
claude "read and improve test.md"
 
# Test help command (inside Claude Code)
/help
```

Your Claude Code should now respond normally. If problems persist, the issue may be service-side - wait a few minutes and try again.

## [Next Steps](#next-steps)

Now that Claude Code is working:

- Explore the [complete guide](/blog/guide) for an overview of all features
- Set up your [first project](/blog/guide/first-project) properly
- Learn [context management](/blog/guide/mechanics/context-management) to avoid future issues
- Configure [optimal settings](/blog/guide/configuration-basics) for your workflow
- Switch to the [native installer](/blog/guide/native-installer) for automatic updates
- Check our [installation guide](/blog/guide/installation-guide) for platform-specific tips
- Review [common errors](/blog/guide/faq) to prevent future problems

Last updated on

[Previous

Examples & Templates](/blog/guide/examples-templates)[Next

FAQ](/blog/guide/faq)
