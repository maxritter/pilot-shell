# How Endless Mode Keeps Claude Working Without Limits

Claude Code has a context window — a fixed amount of text it can process at once. When a session fills up, Claude loses track of earlier work, makes mistakes, or stops entirely. Endless Mode solves this by automatically saving state and restarting sessions before context runs out.

## The Context Problem

Every message, file read, and tool output consumes context tokens. A typical session hits 80% context usage after 30–60 minutes of active development. At 100%, the session is over — Claude can't process any more information.

Without Endless Mode, you have two options when context fills up:

1. **Start fresh** — Lose all context about what you were doing
2. **Manually summarize** — Copy-paste notes into a new session and hope you captured everything

Both are error-prone and break flow.

## How Endless Mode Works

Endless Mode adds three components:

### 1. Context Monitoring

A hook tracks context usage after every tool call. At 80%, it warns Claude to wrap up current work. At 90%, it triggers mandatory handoff.

### 2. State Persistence

Before clearing context, Claude writes a continuation file that captures:

- What was completed (with verification status)
- What's in progress
- Exact next steps (file paths, line numbers, specific commands)
- The active plan file (if using spec-driven development)

This state is also saved to Pilot's persistent memory system, providing a backup that survives across any number of sessions.

### 3. Automatic Restart

Pilot clears the session and restarts Claude with:

- The continuation file from the previous session
- Memory observations from persistent storage
- The active plan file (maintaining full project context)

The new session picks up exactly where the old one left off. From your perspective, work continues uninterrupted.

## What Gets Preserved

| Preserved | How |
|-----------|-----|
| Task progress | Plan file with checked/unchecked tasks |
| Implementation state | Continuation file with exact file:line references |
| Past decisions | Persistent memory observations |
| Verification status | Test results and linter output in continuation file |
| Git state | Worktree branch preserves all commits |

## What You See

When Endless Mode triggers a handoff:

1. Claude announces it's saving state
2. A brief pause (10–15 seconds) while the session restarts
3. Claude says "Continuing from previous session..." and resumes work

No manual intervention needed. You can even walk away and come back — Pilot handles everything.

## Configuration

Endless Mode is built into Pilot and works out of the box. The context monitor hook is installed automatically. The thresholds (80% warning, 90% mandatory handoff) are calibrated to leave enough headroom for a clean save.

If you're using `/spec` for structured development, Endless Mode integrates with the plan file to maintain task tracking across any number of sessions. A feature that takes 5 sessions to implement works just as smoothly as one that takes 1.

## The Result

Context limits become invisible. Instead of worrying about session length, you focus on the work. Pilot ensures continuity regardless of how large or complex the task is.
