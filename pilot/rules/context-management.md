# Context Management

**Context management is fully automatic.** Auto-compaction fires at 100%, preserves state via hooks, restores seamlessly. No context is ever lost.

## How It Works

1. **PreCompact hook** → captures Pilot state (plan, tasks, decisions) to Memory
2. **Compaction** → summarizes conversation, preserving recent work
3. **SessionStart(compact) hook** → re-injects Pilot context
4. You continue working — no interruption needed

## ⛔ NEVER Rush or Skip

Context limits are not the enemy. After compaction, you continue exactly where you left off.

- Do NOT cut corners, skip steps, skip sub-agents, reduce test coverage, or compress output
- Do NOT try to "finish quickly before context runs out"
- Context level is NEVER a valid reason to skip a workflow step (reviewer, verification, tests)
- Complete current task with full quality — compaction handles the rest

## Preservation Checklist

When compaction occurs, preserve these in your summary:

- **Active Plan:** file path, status (PENDING/COMPLETE/VERIFIED), task progress, current objective
- **Technical Context:** key decisions, files being modified, errors being debugged, dependencies discovered
- **Task State:** current objective, TDD phase (red/green/refactor), blockers

**Condensable:** pleasantries, intermediate file reads (keep the understanding, not the reads), repetitive patterns ("explored N similar implementations")

## Context Levels

| Level | Action |
|-------|--------|
| < 80% | Work normally |
| 80%+ | Work normally — auto-compact handles it when needed |
| 100% | Auto-compaction fires — state preserved, context restored |
