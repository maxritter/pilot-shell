---
title: "Claude Code Hooks on Windows, Linux, and macOS (2026)"
description: "Claude Code hooks for Windows, Linux, and macOS. One Node.js file, zero platform wrappers. Cross-platform patterns and working examples."
slug: cross-platform-hooks
date: 2026-02-17
authors:
  - max-ritter
tags:
  - tools
  - hooks
---

Claude Code hooks for Windows, Linux, and macOS. One Node.js file, zero platform wrappers. Cross-platform patterns and working examples.

<!-- truncate -->

**Problem**: You built a [Claude Code hook](/blog/hooks-guide) on Windows using `cmd /c` or PowerShell. A teammate on Linux opens the project and every hook throws errors. Now you're maintaining three wrapper scripts per hook -- `.cmd` for Windows, `.sh` for Linux, `.ps1` for PowerShell -- and they all do the same thing: call the actual `.mjs` file.

**Quick Win**: Delete every wrapper. Invoke Node.js directly in your Claude Code hooks config:

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/formatter.mjs"
          }
        ]
      }
    ]
  }
}
```

This works on Windows, Linux, and macOS. Claude Code requires Node.js, so `node` is always available.

## Why Claude Code Hooks Break on Different Operating Systems

If you're the only person using your Claude Code setup, platform compatibility isn't a concern. But the moment you share `.claude/settings.json` with a teammate, open-source a project, or switch between a Windows workstation and a macOS laptop, platform-specific hooks become a maintenance burden. Every hook that uses `bash` or `powershell` in the command field is a hook that breaks on half your team's machines.

Most tutorials show platform-specific invocations:

```
// Windows-only
"command": "cmd /c \".claude\\hooks\\formatter.cmd\""
 
// Linux-only
"command": "bash .claude/hooks/formatter.sh"
 
// PowerShell-only
"command": "powershell -NoProfile -File .claude/hooks/statusline.ps1"
```

Each wrapper is a 2-line file that just calls `node`. Three files maintained across three platforms, all doing the same thing. When the wrapper is the only platform-dependent layer, eliminate it.

## How to Write Claude Code Hooks for Windows, Linux, and macOS

Every hook in `settings.json` follows this universal pattern:

```
{
  "statusLine": {
    "type": "command",
    "command": "node .claude/hooks/statusline-monitor.mjs"
  },
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/skill-activation.mjs"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/backup.mjs",
            "async": true
          }
        ]
      }
    ]
  }
}
```

No `cmd /c`. No `bash`. No `powershell`. Just `node`. This pattern works for every [Claude Code hook type](/blog/hooks-guide) -- PostToolUse, [SessionStart/SessionEnd](/blog/session-lifecycle-hooks), Stop, and all 12 lifecycle events.

## Three Rules for Cross-Platform Hook Logic

Inside your `.mjs` files, three rules keep Claude Code hooks universal across Windows, Linux, and macOS:

### Use `os.homedir()` Instead of Platform Variables

```
import { homedir } from "os";
import { join } from "path";
 
// Cross-platform: resolves to C:\Users\you or /home/you
const settingsPath = join(homedir(), ".claude", "settings.json");
```

Never hardcode `$HOME`, `$env:USERPROFILE`, or `%USERPROFILE%`.

### Use `os.tmpdir()` for Temporary File Paths

```
import { tmpdir } from "os";
import { join } from "path";
 
// Cross-platform: resolves to C:\Users\you\AppData\Local\Temp or /tmp
const cacheFile = join(tmpdir(), "my-hook-cache.json");
```

Never hardcode `/tmp` or `$env:TEMP`.

### Use `path.join()` for All File Path Construction

```
import { join } from "path";
 
// Cross-platform path construction
const logFile = join(".claude", "hooks", "logs", "hook.log");
```

Never concatenate paths with `/` or `\\`. Node.js handles the separator for each OS automatically.

## Setting Up Cross-Platform Permissions in Claude Code

Your `settings.json` permissions should include equivalents for both platforms:

```
{
  "permissions": {
    "allow": [
      "Bash(where:*)",
      "Bash(which:*)",
      "Bash(tasklist:*)",
      "Bash(ps:*)",
      "Bash(taskkill:*)",
      "Bash(kill:*)",
      "Bash(findstr:*)",
      "Bash(node:*)"
    ]
  }
}
```

Commands that don't exist on a platform simply won't be used. Including both costs nothing, and your Claude Code hooks can reference whichever command is available without hitting permission prompts. For more advanced permission automation, see the Permission Hook guide.

## Complete Example: Cross-Platform File Logger Hook

Here's a complete Claude Code hook that works everywhere -- a file logger that records every Write/Edit operation:

```
#!/usr/bin/env node
import { readFileSync, appendFileSync, mkdirSync } from "fs";
import { join } from "path";
 
const logDir = join(".claude", "hooks", "logs");
mkdirSync(logDir, { recursive: true });
 
try {
  const input = JSON.parse(readFileSync(0, "utf-8"));
  const toolName = input.tool_name;
  const filePath = input.tool_input?.file_path || "unknown";
  const timestamp = new Date().toISOString();
 
  appendFileSync(
    join(logDir, "file-changes.log"),
    `${timestamp} | ${toolName} | ${filePath}\n`,
  );
} catch {
  // Silent fail -- don't block Claude
}
 
process.exit(0);
```

Register it in your `settings.json`:

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/file-logger.mjs"
          }
        ]
      }
    ]
  }
}
```

Works identically on Windows 11, Arch Linux, and macOS Sequoia. No wrappers needed.

## Debugging Cross-Platform Hook Issues

When a Claude Code hook works on one OS but fails on another, check these three things in order:

1. **Hardcoded path separators.** Search your `.mjs` files for `/` or `\\` used in file paths. Replace with `path.join()`.
2. **Environment variable references.** Look for `process.env.HOME`, `process.env.USERPROFILE`, or `process.env.TEMP`. Replace with `os.homedir()` and `os.tmpdir()`.
3. **Shell-specific commands in settings.json.** Any `command` field containing `bash`, `cmd`, `powershell`, or `sh` breaks on other platforms. Replace with `node`.

Run hooks manually to isolate the failure:

```
echo '{"tool_name":"Write","tool_input":{"file_path":"test.js"}}' | node .claude/hooks/your-hook.mjs
echo $?  # Should output 0
```

If it exits 0 on one OS and fails on another, the issue is in the `.mjs` file's path handling, not the hook configuration.

## Cross-Platform Release Checklist

Before shipping Claude Code hooks to a team or open-source project, verify:

- All `settings.json` commands use `node` (not `cmd`, `powershell`, `bash`)
- All `.mjs` files use `os.homedir()` (not `$HOME` or `%USERPROFILE%`)
- All `.mjs` files use `os.tmpdir()` (not `/tmp` or `$env:TEMP`)
- All `.mjs` files use `path.join()` (not hardcoded separators)
- Permissions include both Windows and Unix equivalents
- StatusLine command uses `node` (not `powershell`)

## Frequently Asked Questions

### Do Claude Code hooks work on Windows?

Yes. Claude Code hooks work on Windows, Linux, and macOS when you invoke them with `node` instead of platform-specific shells. Since Claude Code requires Node.js on every platform, the `node` command is always available. Use `node .claude/hooks/your-hook.mjs` in `settings.json` and your hooks run identically on all three operating systems.

### Can I use Python instead of Node.js for hooks?

Python works for cross-platform hooks if your team has Python installed everywhere. Use `python3` (not `python`, which may not exist on some Linux distributions) in the `command` field. However, Node.js is the safer default since Claude Code guarantees its availability on every platform.

### How do I handle line endings across platforms?

Node.js handles line endings automatically when using `readFileSync` and `writeFileSync`. If you're reading stdin (which all hooks do), the JSON parsing is line-ending agnostic. The only place line endings matter is if you're generating shell scripts from a hook -- in that case, use `\n` and let Git's `autocrlf` setting handle conversion.

## Next Steps

- Read the [complete hooks guide](/blog/hooks-guide) for all 12 lifecycle events and exit code patterns
- Set up [Context Recovery](/blog/context-recovery-hook) with cross-platform backup triggers
- Configure Skill Activation for automatic skill loading
- Explore [Setup Hooks](/blog/claude-code-setup-hooks) for cross-platform onboarding
- Master permission rules alongside cross-platform hook permissions
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** ships a configured hook pipeline for Claude Code — formatter and linter on `PostToolUse`, type-check before stop, context capture on session events. Installed once, applied across every project.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
