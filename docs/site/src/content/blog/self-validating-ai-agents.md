# Building Self-Validating AI Agents with Claude Code

The most common failure mode in AI-assisted development: Claude says "done" but the work is incomplete. Self-validating agents solve this by checking their own output before responding.

## The Problem

Claude is optimistic. It writes code, sees no syntax errors, and declares victory. But "no errors" isn't the same as "correct." Missing edge cases, broken integrations, and untested paths slip through.

Without validation, you become the quality gate — reviewing every change manually, running tests yourself, checking that the output actually matches what you asked for.

## Stop Hooks: The Validation Gate

The Stop hook fires right before Claude responds. If your validation script returns a non-zero exit code, Claude continues working instead of stopping.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/validate-before-stop.py"
          }
        ]
      }
    ]
  }
}
```

A basic validation script:

```python
import subprocess
import sys

# Run tests
result = subprocess.run(["pytest", "-q"], capture_output=True)
if result.returncode != 0:
    print("Tests failing - continue working")
    sys.exit(1)

# Check types
result = subprocess.run(["basedpyright", "src"], capture_output=True)
if result.returncode != 0:
    print("Type errors found - fix before stopping")
    sys.exit(1)

sys.exit(0)  # All clear, Claude can respond
```

## PostToolUse: Incremental Validation

Don't wait until the end to validate. PostToolUse hooks check work after each tool call:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check \"$CLAUDE_FILE_PATH\" --fix --quiet"
          }
        ]
      }
    ]
  }
}
```

Every file edit gets linted immediately. Errors are caught in real-time rather than accumulating.

## Read-Only Validator Agents

For complex validation, Pilot uses dedicated review agents that run in parallel:

- **Compliance reviewer** — Checks implementation matches the plan
- **Quality reviewer** — Checks code quality, testing, security

These agents have read-only access — they can analyze code but can't modify it. Their findings are collected and the main agent fixes issues automatically.

## The Validation Stack

Combine all three layers for comprehensive self-validation:

| Layer | When | What It Catches |
|-------|------|----------------|
| PostToolUse hooks | Every edit | Syntax errors, lint violations |
| Stop hook | Before responding | Failing tests, type errors |
| Review agents | After all tasks | Design issues, missing coverage |

Each layer catches different types of problems. Together, they ensure Claude's output is verified before you ever see it.

## Key Principle

The best AI agent isn't the one that writes the most code — it's the one that catches its own mistakes. Self-validation turns Claude from a code generator into a reliable engineering partner.
