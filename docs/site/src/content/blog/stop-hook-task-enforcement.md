---
slug: "stop-hook-task-enforcement"
title: "Claude Code Stop Hook: Force Task Completion"
description: "Use the Stop Hook to ensure Claude finishes tasks before responding. Run tests automatically, validate output, and prevent incomplete work."
date: "2026-01-24"
author: "Max Ritter"
tags: [Guide, Hooks]
readingTime: 5
keywords: "claude, code, completion, enforcement, force, hook, stop, task"
---

Hooks

# Claude Code Stop Hook: Force Task Completion Before Claude Stops

Use the Stop Hook to ensure Claude finishes tasks before responding. Run tests automatically, validate output, and prevent incomplete work.

**Problem**: Claude finishes responding but the task is incomplete. Tests are failing. Files are half-written. You ask "are you done?" and Claude says yes, but the build is broken.

**Quick Win**: Add this Stop hook and Claude cannot stop until tests pass:

```p-4
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/test-gate.py"
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
import subprocess
 
input_data = json.load(sys.stdin)
 
# CRITICAL: Prevent infinite loops
if input_data.get('stop_hook_active', False):
    sys.exit(0)
 
# Run tests
result = subprocess.run(['npm', 'test'], capture_output=True, timeout=60)
 
if result.returncode != 0:
    output = {
        "decision": "block",
        "reason": "Tests are failing. Fix them before completing."
    }
    print(json.dumps(output))
    sys.exit(0)
 
sys.exit(0)
```

Now Claude literally cannot stop responding until tests pass.

## [How the Stop Hook Works](#how-the-stop-hook-works)

The Stop hook fires every time Claude finishes a response. You can:

1. **Allow stopping** - Exit 0, Claude stops normally
2. **Block stopping** - Return `{"decision": "block", "reason": "..."}`, Claude continues working
3. **Run validations** - Execute tests, checks, or validations automatically

### [The Payload](#the-payload)

```p-4
{
  "session_id": "uuid-string",
  "stop_hook_active": false,
  "transcript_path": "/path/to/transcript.jsonl"
}
```

The `stop_hook_active` flag is **critical**. When true, Claude is already in a "forced continuation" state from a previous block. Always check this to prevent infinite loops.

## [Pattern 1: Test Gate](#pattern-1-test-gate)

Block Claude until all tests pass:

```p-4
#!/usr/bin/env python3
import json
import sys
import subprocess
 
input_data = json.load(sys.stdin)
 
if input_data.get('stop_hook_active', False):
    sys.exit(0)
 
result = subprocess.run(
    ['npm', 'test', '--passWithNoTests'],
    capture_output=True,
    timeout=120
)
 
if result.returncode != 0:
    # Extract last 10 lines of test output for context
    stderr = result.stderr.decode()[-500:] if result.stderr else ""
    print(json.dumps({
        "decision": "block",
        "reason": f"Tests failing. Output: {stderr}"
    }))
    sys.exit(0)
 
sys.exit(0)
```

## [Pattern 2: Build Validation](#pattern-2-build-validation)

Ensure the project builds before Claude stops:

```p-4
#!/usr/bin/env python3
import json
import sys
import subprocess
 
input_data = json.load(sys.stdin)
 
if input_data.get('stop_hook_active', False):
    sys.exit(0)
 
result = subprocess.run(
    ['npm', 'run', 'build'],
    capture_output=True,
    timeout=180
)
 
if result.returncode != 0:
    print(json.dumps({
        "decision": "block",
        "reason": "Build failed. Fix compilation errors before completing."
    }))
    sys.exit(0)
 
sys.exit(0)
```

## [Pattern 3: Lint Check](#pattern-3-lint-check)

No stopping with lint errors:

```p-4
#!/usr/bin/env python3
import json
import sys
import subprocess
 
input_data = json.load(sys.stdin)
 
if input_data.get('stop_hook_active', False):
    sys.exit(0)
 
result = subprocess.run(
    ['npx', 'eslint', 'src/', '--max-warnings=0'],
    capture_output=True,
    timeout=60
)
 
if result.returncode != 0:
    print(json.dumps({
        "decision": "block",
        "reason": "Lint errors detected. Run eslint --fix or resolve manually."
    }))
    sys.exit(0)
 
sys.exit(0)
```

## [Pattern 4: Task Completion Marker](#pattern-4-task-completion-marker)

Check if a specific task was completed:

```p-4
#!/usr/bin/env python3
import json
import sys
from pathlib import Path
 
input_data = json.load(sys.stdin)
 
if input_data.get('stop_hook_active', False):
    sys.exit(0)
 
# Check for incomplete task marker
marker = Path('.claude/incomplete-task')
if marker.exists():
    task_info = marker.read_text().strip()
    print(json.dumps({
        "decision": "block",
        "reason": f"Task incomplete: {task_info}. Finish it before stopping."
    }))
    sys.exit(0)
 
sys.exit(0)
```

Create the marker when starting work:

```p-4
echo "Implement user authentication" > .claude/incomplete-task
```

Delete it when done:

```p-4
rm .claude/incomplete-task
```

## [Preventing Infinite Loops](#preventing-infinite-loops)

The `stop_hook_active` flag prevents loops. Here's why it matters:

```p-4
Claude responds → Stop hook fires → "block" → Claude continues
                                            ↓
Claude responds → Stop hook fires → INFINITE LOOP (without flag check)
```

**Always check the flag first**:

```p-4
if input_data.get('stop_hook_active', False):
    sys.exit(0)  # Allow stopping, break the loop
```

## [Combining Multiple Checks](#combining-multiple-checks)

Chain validations in a single hook:

```p-4
#!/usr/bin/env python3
import json
import sys
import subprocess
 
input_data = json.load(sys.stdin)
 
if input_data.get('stop_hook_active', False):
    sys.exit(0)
 
checks = [
    (['npm', 'run', 'lint'], "Lint errors"),
    (['npm', 'run', 'typecheck'], "Type errors"),
    (['npm', 'test'], "Test failures"),
]
 
for cmd, error_msg in checks:
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    if result.returncode != 0:
        print(json.dumps({
            "decision": "block",
            "reason": f"{error_msg} detected. Fix before completing."
        }))
        sys.exit(0)
 
sys.exit(0)
```

## [When to Use Stop Hooks](#when-to-use-stop-hooks)

**Good use cases**:

- Ensuring tests pass before "task complete"
- Validating builds succeed
- Checking lint/type errors
- Custom completion criteria

**Bad use cases**:

- Long-running operations (60 second timeout)
- Network-dependent checks (flaky)
- Blocking on user input (can't interact)

## [Configuration](#configuration)

Add to `.claude/settings.json`:

```p-4
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/stop-validation.py"
          }
        ]
      }
    ]
  }
}
```

Multiple hooks run in parallel. If any returns `block`, Claude continues.

## [Debugging](#debugging)

**Infinite loop?**

- Check that you're reading `stop_hook_active` correctly
- Add logging: `echo "stop_hook_active: $stop_hook_active" >> ~/.claude/stop-debug.log`

**Hook not blocking?**

- Verify JSON output format: `{"decision": "block", "reason": "..."}`
- Check exit code is 0 (not 2 for blocking)

**Tests timing out?**

- 60 second hook timeout
- Run subset of tests or increase efficiency

## [The "Ralph Wilgum" Pattern](#the-ralph-wilgum-pattern)

Named after a community technique, this pattern uses Stop hooks to create persistent task loops:

1. Create task marker at session start
2. Stop hook blocks until marker removed
3. Claude must explicitly complete task to remove marker
4. No accidental "I'm done" when work is incomplete

This transforms Claude from "best effort" to "guaranteed completion."

## [Next Steps](#next-steps)

- Set up the main [Hooks Guide](/blog/tools/hooks/hooks-guide) for all hook types
- Configure [Context Recovery](/blog/tools/hooks/context-recovery-hook) to survive compaction
- Learn [Skill Activation](/blog/tools/hooks/skill-activation-hook) for automatic skill loading
- Explore [Permission Hooks](/blog/tools/hooks/permission-hook-guide) for auto-approval

Last updated on

[Previous

Setup Hooks](/blog/tools/hooks/claude-code-setup-hooks)[Next

Self-Validating Agents](/blog/tools/hooks/self-validating-agents)
