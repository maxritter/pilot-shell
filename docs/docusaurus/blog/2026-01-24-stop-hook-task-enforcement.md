---
title: "Claude Code Stop Hook: Force Task Completion"
description: "Use the Stop Hook to ensure Claude finishes tasks before responding. Run tests automatically, validate output, and prevent incomplete work."
slug: stop-hook-task-enforcement
date: 2026-01-24
authors:
  - max-ritter
tags:
  - tools
  - hooks
---

Use the Stop Hook to ensure Claude finishes tasks before responding. Run tests automatically, validate output, and prevent incomplete work.

<!-- truncate -->

**Problem**: Claude finishes responding but the task is incomplete. Tests are failing. Files are half-written. You ask "are you done?" and Claude says yes, but the build is broken.

**Quick Win**: Add this Stop hook and Claude cannot stop until tests pass:

```
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

```
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

## How the Stop Hook Works

The Stop hook fires every time Claude finishes a response. You can:

1. **Allow stopping** - Exit 0, Claude stops normally
2. **Block stopping** - Return `{"decision": "block", "reason": "..."}`, Claude continues working
3. **Run validations** - Execute tests, checks, or validations automatically

### The Payload

```
{
  "session_id": "uuid-string",
  "stop_hook_active": false,
  "transcript_path": "/path/to/transcript.jsonl"
}
```

The `stop_hook_active` flag is **critical**. When true, Claude is already in a "forced continuation" state from a previous block. Always check this to prevent infinite loops.

## Pattern 1: Test Gate

Block Claude until all tests pass:

```
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

## Pattern 2: Build Validation

Ensure the project builds before Claude stops:

```
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

## Pattern 3: Lint Check

No stopping with lint errors:

```
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

## Pattern 4: Task Completion Marker

Check if a specific task was completed:

```
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

```
echo "Implement user authentication" > .claude/incomplete-task
```

Delete it when done:

```
rm .claude/incomplete-task
```

## Preventing Infinite Loops

The `stop_hook_active` flag prevents loops. Here's why it matters:

```
Claude responds → Stop hook fires → "block" → Claude continues
                                            ↓
Claude responds → Stop hook fires → INFINITE LOOP (without flag check)
```

**Always check the flag first**:

```
if input_data.get('stop_hook_active', False):
    sys.exit(0)  # Allow stopping, break the loop
```

## Combining Multiple Checks

Chain validations in a single hook:

```
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

## When to Use Stop Hooks

**Good use cases**:

- Ensuring tests pass before "task complete"
- Validating builds succeed
- Checking lint/type errors
- Custom completion criteria

**Bad use cases**:

- Long-running operations (60 second timeout)
- Network-dependent checks (flaky)
- Blocking on user input (can't interact)

## Configuration

Add to `.claude/settings.json`:

```
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

## Debugging

**Infinite loop?**

- Check that you're reading `stop_hook_active` correctly
- Add logging: `echo "stop_hook_active: $stop_hook_active" >> ~/.claude/stop-debug.log`

**Hook not blocking?**

- Verify JSON output format: `{"decision": "block", "reason": "..."}`
- Check exit code is 0 (not 2 for blocking)

**Tests timing out?**

- 60 second hook timeout
- Run subset of tests or increase efficiency

## The "Ralph Wilgum" Pattern

Named after a community technique, this pattern uses Stop hooks to create persistent task loops:

1. Create task marker at session start
2. Stop hook blocks until marker removed
3. Claude must explicitly complete task to remove marker
4. No accidental "I'm done" when work is incomplete

## Next Steps

- Set up the main [Hooks Guide](/blog/hooks-guide) for all hook types
- Configure [Context Recovery](/blog/context-recovery-hook) to survive compaction
- Learn Skill Activation for automatic skill loading
- Explore Permission Hooks for auto-approval
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** ships a configured hook pipeline for Claude Code — formatter and linter on `PostToolUse`, type-check before stop, context capture on session events. Installed once, applied across every project.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
