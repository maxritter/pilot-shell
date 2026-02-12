---
slug: "hooks-guide"
title: "Claude Code Hooks: Complete Guide to All 12 Lifecycle Events"
description: "Master Claude Code hooks with exit codes, JSON output, and production patterns. Stop clicking approve and fully automate your workflow."
date: "2025-12-13"
author: "Max Ritter"
tags: [Guide, Hooks]
readingTime: 11
keywords: "12, all, claude, code, complete, events, guide, hooks, lifecycle"
---

Hooks

# Claude Code Hooks: Complete Guide to All 12 Lifecycle Events

Master Claude Code hooks with exit codes, JSON output, and production patterns. Stop clicking approve and fully automate your workflow.

**Problem**: You're deep in flow state, building a feature. Claude needs to write a file. Click approve. Run a command. Click approve. Format code. Click approve. Twenty interruptions later, you've forgotten what you were building.

**Quick Win**: Add this to `.claude/settings.json` and never approve a Prettier format again:

```p-4
{
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
  }
}
```

Every file Claude writes now auto-formats. Zero clicks. Zero context switches.

## [The 12 Hook Lifecycle Events](#the-12-hook-lifecycle-events)

Hooks intercept Claude Code events and execute shell commands or LLM prompts. Here's the complete list:

| Hook | When It Fires | Can Block? | Best Use |
| --- | --- | --- | --- |
| **SessionStart** | Session begins or resumes | NO | Load context, set env vars |
| **UserPromptSubmit** | You hit enter | YES | Context injection, validation |
| **PreToolUse** | Before tool runs | YES | Security blocking, auto-approve (extends [permission system](/blog/guide/development/permission-management#permission-rule-syntax)) |
| **PermissionRequest** | Permission dialog appears | YES | Auto-approve/deny |
| **PostToolUse** | After tool succeeds | NO\* | Auto-format, lint, log |
| **PostToolUseFailure** | After tool fails | NO | Error handling |
| **SubagentStart** | Spawning subagent | NO | Subagent initialization |
| **SubagentStop** | Subagent finishes | YES | Subagent validation |
| **Stop** | Claude finishes responding | YES | Task enforcement |
| **PreCompact** | Before compaction | NO | Transcript backup |
| **Setup** | With --init/--maintenance | NO | One-time setup |
| **SessionEnd** | Session terminates | NO | Cleanup, logging |
| **Notification** | Claude sends notification | NO | Desktop alerts, TTS |

\*PostToolUse can prompt Claude with feedback but cannot undo the tool execution.

## [Exit Codes: The Control Mechanism](#exit-codes-the-control-mechanism)

Every hook communicates via exit codes:

| Exit Code | What Happens |
| --- | --- |
| **0** | Success - hook ran, stdout processed for JSON |
| **2** | Block - operation stopped, stderr sent to Claude |
| **Other** | Error - stderr shown to user, execution continues |

**Exit code 2 is your power tool.** A PreToolUse hook that exits 2 stops the tool. A Stop hook that exits 2 forces Claude to keep working.

## [Hook Types: Command vs Prompt](#hook-types-command-vs-prompt)

**Command hooks** run bash scripts:

```p-4
{
  "type": "command",
  "command": "python validator.py",
  "timeout": 30
}
```

**Prompt hooks** use LLM evaluation (great for Stop/SubagentStop):

```p-4
{
  "type": "prompt",
  "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks complete.",
  "timeout": 30
}
```

The LLM responds with `{"ok": true}` or `{"ok": false, "reason": "..."}`.

## [Async Hooks (Non-Blocking) New - Jan 2026](#async-hooks-non-blocking-new---jan-2026)

Add `async: true` to run hooks in the background without blocking Claude's execution. Released by Anthropic in January 2026:

```p-4
{
  "type": "command",
  "command": "node backup-script.js",
  "async": true,
  "timeout": 30
}
```

**Best for:**

- Logging and analytics
- Backup creation (PreCompact)
- Notifications
- Any side-effect that shouldn't slow things down

**Not suitable for:**

- Security blocking (PreToolUse with exit code 2)
- Auto-approve decisions (PermissionRequest)
- Any hook where Claude needs the result

## [JSON Output: Advanced Control](#json-output-advanced-control)

Beyond exit codes, hooks can return structured JSON for precise control.

### [PreToolUse Decisions](#pretooluse-decisions)

```p-4
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Safe read operation",
    "updatedInput": { "command": "modified-command" },
    "additionalContext": "Context for Claude"
  }
}
```

- `"allow"`: Bypasses permission system
- `"deny"`: Blocks tool, tells Claude why
- `"ask"`: Prompts user for confirmation
- `updatedInput`: Modify tool parameters before execution

### [PermissionRequest Decisions](#permissionrequest-decisions)

```p-4
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": { "command": "npm run lint" }
    }
  }
}
```

### [Stop/SubagentStop Enforcement](#stopsubagentstop-enforcement)

```p-4
{
  "decision": "block",
  "reason": "Tests failing. Fix them before completing."
}
```

## [Hook 1: Auto-Format on Save](#hook-1-auto-format-on-save)

Run formatters after every file write:

```p-4
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\""
          },
          {
            "type": "command",
            "command": "npx eslint --fix \"$CLAUDE_TOOL_INPUT_FILE_PATH\""
          }
        ]
      }
    ]
  }
}
```

Multiple hooks run in parallel. Format AND lint before Claude's response appears.

## [Hook 2: Session Context Injection](#hook-2-session-context-injection)

Load context when sessions start:

```p-4
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '## Git Status' && git status --short && echo '## TODOs' && grep -r 'TODO:' src/ | head -5"
          }
        ]
      }
    ]
  }
}
```

### [Persist Environment Variables](#persist-environment-variables)

SessionStart and Setup hooks can set environment variables for the session:

```p-4
#!/bin/bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export API_KEY=your-key' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

## [Hook 3: Security Blocking](#hook-3-security-blocking)

Block dangerous operations with PreToolUse:

```p-4
#!/usr/bin/env python3
import json
import sys
import re

DANGEROUS_PATTERNS = [
    r'\brm\s+.*-[a-z]*r[a-z]*f',
    r'sudo\s+rm',
    r'chmod\s+777',
    r'git\s+push\s+--force.*main',
]

input_data = json.load(sys.stdin)
if input_data.get('tool_name') == 'Bash':
    command = input_data.get('tool_input', {}).get('command', '')
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print("BLOCKED: Dangerous pattern", file=sys.stderr)
            sys.exit(2)

sys.exit(0)
```

## [Hook 4: Auto-Approve Safe Commands](#hook-4-auto-approve-safe-commands)

Use PermissionRequest to auto-approve without prompts:

```p-4
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/auto-approve.py"
          }
        ]
      }
    ]
  }
}
```

```p-4
#!/usr/bin/env python3
import json
import sys

SAFE_PREFIXES = ['npm test', 'npm run lint', 'git status', 'ls']

input_data = json.load(sys.stdin)
command = input_data.get('tool_input', {}).get('command', '')

for prefix in SAFE_PREFIXES:
    if command.startswith(prefix):
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {"behavior": "allow"}
            }
        }
        print(json.dumps(output))
        sys.exit(0)

sys.exit(0)  # Normal flow for other commands
```

## [Hook 5: Transcript Backup](#hook-5-transcript-backup)

Save transcripts before compaction with PreCompact. Use `async: true` since backups don't need to block Claude:

```p-4
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/backup-transcript.py",
            "async": true
          }
        ]
      }
    ]
  }
}
```

Use matchers `manual` or `auto` to distinguish between `/compact` and auto-compact.

## [Hook 6: Task Completion Enforcement](#hook-6-task-completion-enforcement)

Use Stop hooks to ensure work is complete:

```p-4
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all tasks are complete: $ARGUMENTS. Return {\"ok\": false, \"reason\": \"...\"} if work remains."
          }
        ]
      }
    ]
  }
}
```

See the [Stop Hook guide](/blog/tools/hooks/stop-hook-task-enforcement) for command-based patterns.

## [Hook 7: Skill Activation](#hook-7-skill-activation)

The [Skill Activation Hook](/blog/tools/hooks/skill-activation-hook) intercepts prompts and appends skill recommendations:

```p-4
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/SkillActivationHook/skill-activation-prompt.mjs"
          }
        ]
      }
    ]
  }
}
```

## [Hook 8: Threshold-Based Backups via StatusLine](#hook-8-threshold-based-backups-via-statusline)

StatusLine is the only mechanism that receives live context metrics. Use it to trigger backups at thresholds:

```p-4
{
  "statusLine": {
    "type": "command",
    "command": "node .claude/hooks/ContextRecoveryHook/statusline-monitor.mjs"
  }
}
```

**Critical**: The `remaining_percentage` field includes the 22.5% autocompact buffer. To get actual "free until autocompact":

```p-4
const AUTOCOMPACT_BUFFER_PCT = 22.5;
const freeUntilCompact = Math.max(
  0,
  remaining_percentage - AUTOCOMPACT_BUFFER_PCT,
);
```

Trigger backups when crossing thresholds:

```p-4
const THRESHOLDS = [30, 15, 5]; // Free until autocompact %

for (const threshold of THRESHOLDS) {
  if (state.lastFree > threshold && freeUntilCompact <= threshold) {
    runBackup(sessionId, `crossed_${threshold}pct`);
  }
}

// Below 5%: backup on every decrease
if (freeUntilCompact < 5 && freeUntilCompact < state.lastFree) {
  runBackup(sessionId, "continuous");
}
```

Unlike PreCompact (which triggers on compaction), StatusLine-based backups capture state proactively at configurable thresholds.

### [Architecture: Three-File Structure](#architecture-three-file-structure)

The backup system uses a clean separation of concerns:

```p-4
.claude/hooks/ContextRecoveryHook/
├── backup-core.mjs        # Shared backup logic (parsing, formatting, saving)
├── statusline-monitor.mjs # Threshold detection + display (calls backup-core)
└── conv-backup.mjs        # PreCompact trigger (calls backup-core)
```

| File | Trigger | Responsibility |
| --- | --- | --- |
| `backup-core.mjs` | Called by others | Parse transcript, format markdown, save file, update state |
| `statusline-monitor.mjs` | StatusLine (continuous) | Monitor context %, detect thresholds, display status |
| `conv-backup.mjs` | PreCompact hook | Handle pre-compaction event |

This architecture means backup logic lives in one place. Changes to formatting, file naming, or state management only need to be made in `backup-core.mjs`.

### [Backup File Naming](#backup-file-naming)

Backups use numbered filenames with timestamps for history:

```p-4
.claude/backups/1-backup-26th-Jan-2026-4-30pm.md
.claude/backups/2-backup-26th-Jan-2026-5-15pm.md
.claude/backups/3-backup-26th-Jan-2026-5-45pm.md
```

### [StatusLine Display](#statusline-display)

When context drops below 30%, the statusline shows the current backup path:

```p-4
[!] 25.0% free (50.0K/200K)
-> .claude/backups/3-backup-26th-Jan-2026-5-45pm.md
```

This tells you exactly which file to load after compaction.

## [Hook 9: Setup Hooks for Installation and Maintenance](#hook-9-setup-hooks-for-installation-and-maintenance)

Setup hooks run *before* your session starts, triggered by special CLI flags:

```p-4
claude --init           # Triggers Setup hook with matcher "init"
claude --init-only      # Same as above, but exits after hook (CI-friendly)
claude --maintenance    # Triggers Setup hook with matcher "maintenance"
```

Configure them with matchers in settings.json:

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

**The power move**: Pass a prompt after the flag:

```p-4
claude --init "/install"
```

The hook runs first (deterministic), then the `/install` command executes (agentic). This combines predictable script execution with intelligent agent oversight.

See the complete [Setup Hooks Guide](/blog/tools/hooks/claude-code-setup-hooks) for the full pattern including interactive onboarding and justfile integration.

## [Configuration Locations](#configuration-locations)

| Location | Scope | Priority |
| --- | --- | --- |
| Managed policy | Enterprise | Highest |
| `.claude/settings.json` | Project (shared) | High |
| `.claude/settings.local.json` | Project (personal) | Medium |
| `~/.claude/settings.json` | All projects | Lowest |

## [Disabling and Restricting Hooks](#disabling-and-restricting-hooks)

### [Disable All Hooks](#disable-all-hooks)

If hooks are causing issues or you want a clean baseline, set `disableAllHooks` to `true` in your settings:

```p-4
{
  "disableAllHooks": true
}
```

This turns off all hooks across every scope (user, project, and local settings). Useful for debugging or when a hook causes unexpected behavior.

### [Managed Hook Restrictions](#managed-hook-restrictions)

For organizations that need centralized control, administrators can set `allowManagedHooksOnly` to `true` in [managed settings](/blog/guide/development/permission-management#managed-permission-settings):

```p-4
{
  "allowManagedHooksOnly": true
}
```

When enabled, only hooks defined in the managed settings file and SDK hooks are allowed. User-level, project-level, and plugin hooks are all blocked. This prevents developers from adding hooks that could bypass organizational security policies.

This pairs well with `allowManagedPermissionRulesOnly`, which applies the same restriction to [permission rules](/blog/guide/development/permission-management#permission-rule-syntax). Together, these settings give administrators full control over both the permission system and its hook-based extensions.

## [Matcher Syntax](#matcher-syntax)

| Pattern | Matches |
| --- | --- |
| `""` or omitted | All tools |
| `"Bash"` | Only Bash (exact, case-sensitive) |
| `"Write|Edit"` | Write OR Edit (regex) |
| `"mcp__memory__.*"` | All memory MCP tools |

**Critical**: No spaces around `|`. Matchers are case-sensitive.

### [Event-Specific Matchers](#event-specific-matchers)

**SessionStart**: `startup`, `resume`, `clear`, `compact`
**PreCompact**: `manual`, `auto`
**Setup**: `init`, `maintenance`
**Notification**: `permission_prompt`, `idle_prompt`, `auth_success`

## [Environment Variables](#environment-variables)

| Variable | Description |
| --- | --- |
| `CLAUDE_PROJECT_DIR` | Project root (all hooks) |
| `CLAUDE_ENV_FILE` | Persist env vars (SessionStart, Setup) |
| `CLAUDE_CODE_REMOTE` | "true" if web, empty if CLI |

## [Debugging](#debugging)

**Hook not triggering?**

- Check matcher syntax (case-sensitive, no spaces)
- Verify settings file location
- Test: `echo '{"session_id":"test"}' | python your-hook.py`

**Command failing?**

- Add logging: `command 2>&1 | tee ~/.claude/hook-debug.log`
- Run with debug: `claude --debug`

**Infinite loops with Stop?**

- Always check `stop_hook_active` flag first

## [Start With One Hook](#start-with-one-hook)

Pick your biggest friction point:

- Constant formatting? PostToolUse formatter
- Approving safe commands? PermissionRequest auto-approve
- Missing context? SessionStart injection
- Losing progress? PreCompact backup
- Incomplete tasks? Stop enforcement

One hook. One friction point eliminated. Then iterate.

## [Next Steps](#next-steps)

- Configure [Setup Hooks](/blog/tools/hooks/claude-code-setup-hooks) for automated onboarding and maintenance
- Configure the [Stop Hook](/blog/tools/hooks/stop-hook-task-enforcement) to enforce task completion
- Install the [Permission Hook](/blog/tools/hooks/permission-hook-guide) for intelligent auto-approval
- Set up [Skill Activation](/blog/tools/hooks/skill-activation-hook) for automatic skill loading
- Configure [Context Recovery](/blog/tools/hooks/context-recovery-hook) to survive compaction
- Explore [Session Lifecycle Hooks](/blog/tools/hooks/session-lifecycle-hooks) for setup and cleanup
- Master [permission rules and modes](/blog/guide/development/permission-management) for static permission control alongside hooks
- Learn [configuration basics](/blog/guide/configuration-basics) for complete Claude Code setup

Last updated on

[Previous

Status Line Guide](/blog/tools/statusline-guide)[Next

Setup Hooks](/blog/tools/hooks/claude-code-setup-hooks)
