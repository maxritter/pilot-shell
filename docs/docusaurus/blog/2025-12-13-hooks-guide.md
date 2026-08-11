---
title: "Claude Code Hooks: Complete Guide to All 12 Lifecycle Events"
description: "Master Claude Code hooks with exit codes, JSON output, and production patterns. Stop clicking approve and fully automate your workflow."
slug: hooks-guide
date: 2025-12-13
authors:
  - max-ritter
tags:
  - tools
  - hooks
---

Master Claude Code hooks with exit codes, JSON output, and production patterns. Stop clicking approve and fully automate your workflow.

<!-- truncate -->

**Problem**: You're deep in flow state, building a feature. Claude needs to write a file. Click approve. Run a command. Click approve. Format code. Click approve. Twenty interruptions later, you've forgotten what you were building.

**Quick Win**: Add this to `.claude/settings.json` and never approve a Prettier format again:

```
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

## The 12 Hook Lifecycle Events

Hooks intercept Claude Code events and execute shell commands or LLM prompts. Here's the complete list:

| Hook | When It Fires | Can Block? | Best Use |
| --- | --- | --- | --- |
| **SessionStart** | Session begins or resumes | NO | Load context, set env vars |
| **UserPromptSubmit** | You hit enter | YES | Context injection, validation |
| **PreToolUse** | Before tool runs | YES | Security blocking, auto-approve (extends permission system) |
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

## Exit Codes: The Control Mechanism

Every hook communicates via exit codes:

| Exit Code | What Happens |
| --- | --- |
| **0** | Success - hook ran, stdout processed for JSON |
| **2** | Block - operation stopped, stderr sent to Claude |
| **Other** | Error - stderr shown to user, execution continues |

**Exit code 2 is your power tool.** A PreToolUse hook that exits 2 stops the tool. A Stop hook that exits 2 forces Claude to keep working.

## Hook Types: Command, HTTP, Prompt, and Agent

Claude Code supports four hook handler types. Pick the one that fits your use case:

**Command hooks** run shell scripts:

```
{
  "type": "command",
  "command": "python validator.py",
  "timeout": 30
}
```

**HTTP hooks** POST to an endpoint and receive JSON back: New - Feb 2026

```
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "timeout": 30,
  "headers": {
    "Authorization": "Bearer $MY_TOKEN"
  },
  "allowedEnvVars": ["MY_TOKEN"]
}
```

HTTP hooks send the event's JSON input as the POST body (`Content-Type: application/json`). The response uses the same JSON output format as command hooks. Key differences from command hooks:

- **Non-blocking errors**: Non-2xx responses, connection failures, and timeouts produce non-blocking errors (execution continues). To actually block a tool call, return a 2xx response with `decision: "block"` in the JSON body.
- **Header env vars**: Use `$VAR_NAME` or `${VAR_NAME}` in header values. Only variables listed in `allowedEnvVars` get resolved; unlisted ones become empty strings.
- **Deduplication**: HTTP hooks are deduplicated by URL (command hooks by command string).
- **Config only**: Must be added by editing settings JSON directly. The `/hooks` interactive menu only supports command hooks.

**Prompt hooks** use LLM evaluation (great for Stop/SubagentStop):

```
{
  "type": "prompt",
  "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks complete.",
  "timeout": 30
}
```

The LLM responds with `{"ok": true}` or `{"ok": false, "reason": "..."}`.

**Agent hooks** spawn a subagent with tool access (Read, Grep, Glob) for deeper verification:

```
{
  "type": "agent",
  "prompt": "Verify all test files have corresponding implementation files",
  "timeout": 60
}
```

Agent hooks can explore the codebase before making a decision, making them more thorough than prompt hooks but slower (default timeout: 60s vs 30s for prompts).

## Async Hooks (Non-Blocking) New - Jan 2026

Add `async: true` to run hooks in the background without blocking Claude's execution. Released by Anthropic in January 2026:

```
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

## HTTP Hooks: Post to Endpoints New - Feb 2026

HTTP hooks let you send hook events to a web server instead of running a local script. This opens up use cases that were previously awkward or impossible with command hooks:

- **Remote validation services** that enforce team-wide policies
- **Centralized logging** to a shared audit system
- **Webhook integrations** with Slack, PagerDuty, or custom dashboards
- **Microservice architectures** where hook logic runs alongside your API

### Basic HTTP Hook

Route all Bash commands through a validation endpoint:

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/pre-tool-use",
            "timeout": 30,
            "headers": {
              "Authorization": "Bearer $MY_TOKEN"
            },
            "allowedEnvVars": ["MY_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

Your server receives the exact same JSON that command hooks get via stdin, but as the POST request body. Return the same JSON output format in the response body.

### HTTP Response Handling

HTTP hooks interpret responses differently from command hooks. There are no exit codes, only HTTP status codes and response bodies:

| Response | Behavior |
| --- | --- |
| **2xx + empty body** | Success, equivalent to exit code 0 with no output |
| **2xx + plain text body** | Success, the text is added as context to Claude |
| **2xx + JSON body** | Success, parsed using the same JSON output schema as command hooks |
| **Non-2xx status** | Non-blocking error, execution continues |
| **Connection failure / timeout** | Non-blocking error, execution continues |

**The critical difference**: HTTP hooks cannot block via status codes alone. A 4xx or 5xx just logs an error and keeps going. To actually block a tool call or deny a permission, you must return a **2xx response** with the appropriate decision fields in the JSON body:

```
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked by security policy"
  }
}
```

### Secure Header Authentication

The `headers` field supports environment variable interpolation, but only for variables explicitly listed in `allowedEnvVars`. This prevents accidental secret leakage:

```
{
  "type": "http",
  "url": "https://hooks.example.com/validate",
  "headers": {
    "Authorization": "Bearer $API_KEY",
    "X-Team-Id": "$TEAM_ID"
  },
  "allowedEnvVars": ["API_KEY", "TEAM_ID"]
}
```

Any `$VAR` reference not in `allowedEnvVars` resolves to an empty string. No warnings, no errors. Just empty. So double-check your allowlist.

## JSON Output: Advanced Control

Beyond exit codes, hooks can return structured JSON for precise control.

### PreToolUse Decisions

```
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

### PermissionRequest Decisions

```
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

### Stop/SubagentStop Enforcement

```
{
  "decision": "block",
  "reason": "Tests failing. Fix them before completing."
}
```

## Hook 1: Auto-Format on Save

Run formatters after every file write:

```
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

## Hook 2: Session Context Injection

Load context when sessions start:

```
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

### Persist Environment Variables

SessionStart and Setup hooks can set environment variables for the session:

```
#!/bin/bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export API_KEY=your-key' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

## Hook 3: Security Blocking

Block dangerous operations with PreToolUse:

```
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

## Hook 4: Auto-Approve Safe Commands

Use PermissionRequest to auto-approve without prompts:

```
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

```
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

## Hook 5: Transcript Backup

Save transcripts before compaction with PreCompact. Use `async: true` since backups don't need to block Claude:

```
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

## Hook 6: Task Completion Enforcement

Use Stop hooks to ensure work is complete:

```
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

See the [Stop Hook guide](/blog/stop-hook-task-enforcement) for command-based patterns.

## Hook 7: Skill Activation

```
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

## Hook 8: Threshold-Based Backups via StatusLine

StatusLine is the only mechanism that receives live context metrics. Use it to trigger backups at thresholds:

```
{
  "statusLine": {
    "type": "command",
    "command": "node .claude/hooks/ContextRecoveryHook/statusline-monitor.mjs"
  }
}
```

**Critical**: The `remaining_percentage` field includes a fixed 33K-token autocompact buffer. To get actual "free until autocompact":

```
const AUTOCOMPACT_BUFFER_TOKENS = 33000;
const autocompactBufferPct = (AUTOCOMPACT_BUFFER_TOKENS / windowSize) * 100;
const freeUntilCompact = Math.max(0, pctRemainTotal - autocompactBufferPct);
```

The backup system uses two trigger systems simultaneously. The token-based system is the primary trigger, with percentage thresholds as a safety net:

```
// Token-based triggers (primary - works across all window sizes)
const TOKEN_FIRST_BACKUP = 50000; // First backup at 50k tokens used
const TOKEN_UPDATE_INTERVAL = 10000; // Update every 10k tokens after
 
if (currentTotalTokens >= TOKEN_FIRST_BACKUP) {
  if (lastBackupTokens < TOKEN_FIRST_BACKUP) {
    runBackup(
      sessionId,
      `tokens_${Math.round(currentTotalTokens / 1000)}k_first`,
    );
  } else if (currentTotalTokens - lastBackupTokens >= TOKEN_UPDATE_INTERVAL) {
    runBackup(
      sessionId,
      `tokens_${Math.round(currentTotalTokens / 1000)}k_update`,
    );
  }
}
 
// Percentage-based triggers (safety net, especially for 200k windows)
const THRESHOLDS = [30, 15, 5];
for (const threshold of THRESHOLDS) {
  if (state.lastFree > threshold && freeUntilCompact <= threshold) {
    runBackup(sessionId, `crossed_${threshold}pct`);
  }
}
if (freeUntilCompact < 5 && freeUntilCompact < state.lastFree) {
  runBackup(sessionId, "continuous");
}
```

Unlike PreCompact (which triggers on compaction), StatusLine-based backups capture state proactively. The token-based system ensures early backups on large context windows (1M) where percentage thresholds would fire too late.

### Architecture: Three-File Structure

The backup system uses a clean separation of concerns:

```
.claude/hooks/ContextRecoveryHook/
├── backup-core.mjs        # Shared backup logic (parsing, formatting, saving)
├── statusline-monitor.mjs # Threshold detection + display (calls backup-core)
└── conv-backup.mjs        # PreCompact trigger (calls backup-core)
```

| File | Trigger | Responsibility |
| --- | --- | --- |
| `backup-core.mjs` | Called by others | Parse transcript, format markdown, save file, update state |
| `statusline-monitor.mjs` | StatusLine (continuous) | Monitor tokens/context %, detect triggers, display status |
| `conv-backup.mjs` | PreCompact hook | Handle pre-compaction event |

This architecture means backup logic lives in one place. Changes to formatting, file naming, or state management only need to be made in `backup-core.mjs`.

### Backup File Naming

Backups use numbered filenames with timestamps for history:

```
.claude/backups/1-backup-26th-Jan-2026-4-30pm.md
.claude/backups/2-backup-26th-Jan-2026-5-15pm.md
.claude/backups/3-backup-26th-Jan-2026-5-45pm.md
```

### StatusLine Display

When a backup exists for the current session, the statusline shows the backup path:

```
[!] 25.0% free (50.0K/200K)
-> .claude/backups/3-backup-26th-Jan-2026-5-45pm.md
```

This tells you exactly which file to load after compaction.

### State Tracking

```
{
  "sessionId": "abc123",
  "lastFreeUntilCompact": 25.5,
  "currentBackupPath": ".claude/backups/3-backup-26th-Jan-2026-5-45pm.md"
}
```

**Recommended workflow**: When compaction occurs, run `/clear` to start a fresh session, then load the backup file shown in the statusline. This avoids confusion from having both compaction summary and injected context.

## Hook 9: Setup Hooks for Installation and Maintenance

Setup hooks run *before* your session starts, triggered by special CLI flags:

```
claude --init           # Triggers Setup hook with matcher "init"
claude --init-only      # Same as above, but exits after hook (CI-friendly)
claude --maintenance    # Triggers Setup hook with matcher "maintenance"
```

Configure them with matchers in settings.json:

```
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

```
claude --init "/install"
```

The hook runs first (deterministic), then the `/install` command executes (agentic). This combines predictable script execution with intelligent agent oversight.

See the complete [Setup Hooks Guide](/blog/claude-code-setup-hooks) for the full pattern including interactive onboarding and justfile integration.

## Configuration Locations

| Location | Scope | Priority |
| --- | --- | --- |
| Managed policy | Enterprise | Highest |
| `.claude/settings.json` | Project (shared) | High |
| `.claude/settings.local.json` | Project (personal) | Medium |
| `~/.claude/settings.json` | All projects | Lowest |

## Disabling and Restricting Hooks

### Disable All Hooks

If hooks are causing issues or you want a clean baseline, set `disableAllHooks` to `true` in your settings:

```
{
  "disableAllHooks": true
}
```

This turns off all hooks across every scope (user, project, and local settings). Useful for debugging or when a hook causes unexpected behavior.

### Managed Hook Restrictions

For organizations that need centralized control, administrators can set `allowManagedHooksOnly` to `true` in managed settings:

```
{
  "allowManagedHooksOnly": true
}
```

When enabled, only hooks defined in the managed settings file and SDK hooks are allowed. User-level, project-level, and plugin hooks are all blocked. This prevents developers from adding hooks that could bypass organizational security policies.

This pairs well with `allowManagedPermissionRulesOnly`, which applies the same restriction to permission rules. Together, these settings give administrators full control over both the permission system and its hook-based extensions.

## Matcher Syntax

| Pattern | Matches |
| --- | --- |
| `""` or omitted | All tools |
| `"Bash"` | Only Bash (exact, case-sensitive) |
| `"Write|Edit"` | Write OR Edit (regex) |
| `"mcp__memory__.*"` | All memory MCP tools |

**Critical**: No spaces around `|`. Matchers are case-sensitive.

### Event-Specific Matchers

**SessionStart**: `startup`, `resume`, `clear`, `compact`
**PreCompact**: `manual`, `auto`
**Setup**: `init`, `maintenance`
**Notification**: `permission_prompt`, `idle_prompt`, `auth_success`

## Environment Variables

| Variable | Description |
| --- | --- |
| `CLAUDE_PROJECT_DIR` | Project root (all hooks) |
| `CLAUDE_ENV_FILE` | Persist env vars (SessionStart, Setup) |
| `CLAUDE_CODE_REMOTE` | "true" if web, empty if CLI |

## Debugging

**Hook not triggering?**

- Check matcher syntax (case-sensitive, no spaces)
- Verify settings file location
- Test: `echo '{"session_id":"test"}' | python your-hook.py`

**Command failing?**

- Add logging: `command 2>&1 | tee ~/.claude/hook-debug.log`
- Run with debug: `claude --debug`
- Hooks breaking on other operating systems? See [cross-platform hook patterns](/blog/cross-platform-hooks)

**Infinite loops with Stop?**

- Always check `stop_hook_active` flag first

## Start With One Hook

Pick your biggest friction point:

- Constant formatting? PostToolUse formatter
- Approving safe commands? PermissionRequest auto-approve
- Missing context? SessionStart injection
- Losing progress? PreCompact backup
- Incomplete tasks? Stop enforcement

## Next Steps

- Configure [Setup Hooks](/blog/claude-code-setup-hooks) for automated onboarding and maintenance
- Configure the [Stop Hook](/blog/stop-hook-task-enforcement) to enforce task completion
- Install the Permission Hook for intelligent auto-approval
- Set up Skill Activation for automatic skill loading
- Configure [Context Recovery](/blog/context-recovery-hook) to survive compaction
- Explore [Session Lifecycle Hooks](/blog/session-lifecycle-hooks) for setup and cleanup
- Master permission rules and modes for static permission control alongside hooks
- Learn configuration basics for complete Claude Code setup
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** ships a configured hook pipeline for Claude Code — formatter and linter on `PostToolUse`, type-check before stop, context capture on session events. Installed once, applied across every project.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
