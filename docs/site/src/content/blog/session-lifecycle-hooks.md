---
slug: "session-lifecycle-hooks"
title: "Claude Code Session Hooks: Auto-Load Context Every Time"
description: "SessionStart, SessionEnd, Setup, and PreCompact hooks for Claude Code. Auto-load context at startup and clean up on session end automatically."
date: "2026-01-24"
author: "Max Ritter"
tags: [Guide, Hooks]
readingTime: 7
keywords: "autoload, claude, code, context, every, hooks, lifecycle, session, time"
---

Hooks

# Claude Code Session Hooks: Auto-Load Context Every Time

SessionStart, SessionEnd, Setup, and PreCompact hooks for Claude Code. Auto-load context at startup and clean up on session end automatically.

**Problem**: Every time you start a Claude Code session, you manually remind it about your project state, environment setup, or current tasks. When sessions end, cleanup tasks are forgotten.

**Quick Win**: Add this SessionStart hook and Claude always knows your git state:

```p-4
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '## Git' && git branch --show-current && git status --short | head -10"
          }
        ]
      }
    ]
  }
}
```

Now every session starts with context. Zero manual setup.

## [The Session Lifecycle Hooks](#the-session-lifecycle-hooks)

Four hooks control session lifecycle:

| Hook | When It Fires | Can Block? | Use Case |
| --- | --- | --- | --- |
| **Setup** | With `--init` or `--maintenance` | NO | One-time setup, migrations |
| **SessionStart** | Every session start/resume | NO | Load context, set env vars |
| **PreCompact** | Before context compaction | NO | Backup transcripts |
| **SessionEnd** | Session terminates | NO | Cleanup, logging |

## [SessionStart: Load Context Every Time](#sessionstart-load-context-every-time)

SessionStart fires when sessions begin or resume. Use it for context that should always be present.

### [Basic Context Injection](#basic-context-injection)

```p-4
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '## Project State' && cat .claude/tasks/session-current.md 2>/dev/null || echo 'No active session'"
          }
        ]
      }
    ]
  }
}
```

### [With JSON Output](#with-json-output)

For structured context injection:

```p-4
#!/usr/bin/env python3
import json
import sys
import subprocess
 
def get_project_context():
    try:
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        changes = len(status.split('\n')) if status else 0
    except:
        branch, changes = "unknown", 0
 
    return f"""=== SESSION CONTEXT ===
Git Branch: {branch}
Uncommitted Changes: {changes}
=== END ===""".strip()
 
output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": get_project_context()
    }
}
print(json.dumps(output))
sys.exit(0)
```

### [SessionStart Matchers](#sessionstart-matchers)

Target specific session events:

```p-4
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [{ "type": "command", "command": "echo 'Fresh session'" }]
      },
      {
        "matcher": "resume",
        "hooks": [{ "type": "command", "command": "echo 'Resumed session'" }]
      },
      {
        "matcher": "compact",
        "hooks": [{ "type": "command", "command": "echo 'Post-compaction'" }]
      }
    ]
  }
}
```

- `startup` - New session
- `resume` - From `--resume`, `--continue`, or `/resume`
- `clear` - After `/clear`
- `compact` - After compaction

### [Persist Environment Variables](#persist-environment-variables)

SessionStart has access to `CLAUDE_ENV_FILE` for setting session-wide environment variables:

```p-4
#!/bin/bash
 
# Persist environment changes from nvm, pyenv, etc.
ENV_BEFORE=$(export -p | sort)
 
# Setup commands that modify environment
source ~/.nvm/nvm.sh
nvm use 20
 
if [ -n "$CLAUDE_ENV_FILE" ]; then
  ENV_AFTER=$(export -p | sort)
  comm -13 <(echo "$ENV_BEFORE") <(echo "$ENV_AFTER") >> "$CLAUDE_ENV_FILE"
fi
 
exit 0
```

Variables written to `CLAUDE_ENV_FILE` are available in all subsequent bash commands Claude runs.

## [Setup: One-Time Operations](#setup-one-time-operations)

Setup hooks run only when explicitly invoked with `--init`, `--init-only`, or `--maintenance`. Use them for operations you don't want on every session.

### [When to Use Setup vs SessionStart](#when-to-use-setup-vs-sessionstart)

| Operation | Use Setup | Use SessionStart |
| --- | --- | --- |
| Install dependencies | Yes | No |
| Run database migrations | Yes | No |
| Load git status | No | Yes |
| Set environment variables | Yes | Yes |
| Inject project context | No | Yes |
| Cleanup temp files | Yes (maintenance) | No |

### [Setup Configuration](#setup-configuration)

```p-4
{
  "hooks": {
    "Setup": [
      {
        "matcher": "init",
        "hooks": [
          {
            "type": "command",
            "command": "npm install && npm run db:migrate"
          }
        ]
      },
      {
        "matcher": "maintenance",
        "hooks": [
          {
            "type": "command",
            "command": "npm prune && npm dedupe && rm -rf .cache"
          }
        ]
      }
    ]
  }
}
```

Invoke with:

```p-4
claude --init          # Runs 'init' matcher
claude --init-only     # Runs 'init' matcher, then exits
claude --maintenance   # Runs 'maintenance' matcher
```

Setup hooks also have access to `CLAUDE_ENV_FILE` for persisting environment variables.

## [PreCompact: Before Context Loss](#precompact-before-context-loss)

PreCompact fires before compaction (manual `/compact` or automatic when context fills).

### [Backup Transcripts](#backup-transcripts)

```p-4
#!/usr/bin/env python3
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
 
input_data = json.load(sys.stdin)
transcript_path = input_data.get('transcript_path', '')
trigger = input_data.get('trigger', 'unknown')
 
if transcript_path and Path(transcript_path).exists():
    backup_dir = Path('.claude/backups')
    backup_dir.mkdir(parents=True, exist_ok=True)
 
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"transcript_{trigger}_{timestamp}.jsonl"
    shutil.copy2(transcript_path, backup_dir / backup_name)
 
    # Keep only last 10 backups
    backups = sorted(backup_dir.glob('transcript_*.jsonl'))
    for old_backup in backups[:-10]:
        old_backup.unlink()
 
sys.exit(0)
```

### [PreCompact Matchers](#precompact-matchers)

```p-4
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [{ "type": "command", "command": "echo 'Auto-compacting...'" }]
      },
      {
        "matcher": "manual",
        "hooks": [{ "type": "command", "command": "echo 'Manual /compact'" }]
      }
    ]
  }
}
```

- `auto` - Context window filled, automatic compaction
- `manual` - User ran `/compact`

### [Create Recovery Markers](#create-recovery-markers)

Use PreCompact with SessionStart for context recovery. See the [Context Recovery Hook](/blog/tools/hooks/context-recovery-hook) for the complete pattern.

## [SessionEnd: Cleanup](#sessionend-cleanup)

SessionEnd fires when sessions terminate. It cannot block termination but can perform cleanup.

### [Log Session Stats](#log-session-stats)

```p-4
#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime
 
input_data = json.load(sys.stdin)
session_id = input_data.get('session_id', 'unknown')
reason = input_data.get('reason', 'unknown')
 
log_dir = Path('.claude/logs')
log_dir.mkdir(parents=True, exist_ok=True)
 
log_entry = {
    "session_id": session_id,
    "ended_at": datetime.now().isoformat(),
    "reason": reason
}
 
with open(log_dir / 'session-history.jsonl', 'a') as f:
    f.write(json.dumps(log_entry) + '\n')
 
sys.exit(0)
```

### [SessionEnd Reasons](#sessionend-reasons)

The `reason` field indicates why the session ended:

- `clear` - User ran `/clear`
- `logout` - User logged out
- `prompt_input_exit` - User exited while prompt was visible
- `other` - Other exit reasons

## [Complete Lifecycle Example](#complete-lifecycle-example)

Here's a complete lifecycle configuration:

```p-4
{
  "hooks": {
    "Setup": [
      {
        "matcher": "init",
        "hooks": [
          {
            "type": "command",
            "command": "npm install && echo 'Dependencies installed'"
          }
        ]
      }
    ],
 
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '## Context' && git status --short && echo '## Tasks' && cat .claude/tasks/session-current.md 2>/dev/null | head -20"
          }
        ]
      }
    ],
 
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cp \"$CLAUDE_TRANSCRIPT_PATH\" .claude/backups/last-transcript.jsonl 2>/dev/null || true"
          }
        ]
      }
    ],
 
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Session ended: $(date)\" >> .claude/logs/sessions.log"
          }
        ]
      }
    ]
  }
}
```

## [Input Payloads](#input-payloads)

### [SessionStart Input](#sessionstart-input)

```p-4
{
  "session_id": "abc123",
  "hook_event_name": "SessionStart",
  "source": "startup",
  "model": "claude-sonnet-4-20250514",
  "cwd": "/path/to/project"
}
```

### [Setup Input](#setup-input)

```p-4
{
  "session_id": "abc123",
  "hook_event_name": "Setup",
  "trigger": "init",
  "cwd": "/path/to/project"
}
```

### [PreCompact Input](#precompact-input)

```p-4
{
  "session_id": "abc123",
  "hook_event_name": "PreCompact",
  "transcript_path": "~/.claude/projects/.../transcript.jsonl",
  "trigger": "auto",
  "custom_instructions": ""
}
```

### [SessionEnd Input](#sessionend-input)

```p-4
{
  "session_id": "abc123",
  "hook_event_name": "SessionEnd",
  "reason": "clear",
  "cwd": "/path/to/project"
}
```

## [Best Practices](#best-practices)

1. **Keep SessionStart fast** - It runs every session. Heavy operations go in Setup.
2. **Use Setup for one-time work** - Dependency installation, migrations, initial setup.
3. **Backup before compaction** - PreCompact is your last chance to save context.
4. **Log session ends** - SessionEnd is useful for analytics and debugging.
5. **Use matchers wisely** - Different behavior for `startup` vs `resume` vs `compact`.

## [Next Steps](#next-steps)

- Set up the main [Hooks Guide](/blog/tools/hooks/hooks-guide) for all 12 hooks
- Configure [Context Recovery](/blog/tools/hooks/context-recovery-hook) for compaction survival
- Use [Stop Hooks](/blog/tools/hooks/stop-hook-task-enforcement) for task enforcement
- Explore [Skill Activation](/blog/tools/hooks/skill-activation-hook) for automatic skill loading

Last updated on

[Previous

Self-Validating Agents](/blog/tools/hooks/self-validating-agents)[Next

Context Recovery Hook](/blog/tools/hooks/context-recovery-hook)
