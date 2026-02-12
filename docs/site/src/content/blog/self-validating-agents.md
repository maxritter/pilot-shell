---
slug: "self-validating-agents"
title: "Self-Validating Claude Code Agents: Automated Quality Checks"
description: "Build Claude Code agents that validate their own output using PostToolUse hooks, Stop hooks, and read-only validator agents."
date: "2026-02-03"
author: "Max Ritter"
tags: [Guide, Hooks]
readingTime: 6
keywords: "agents, automated, checks, claude, code, quality, self, selfvalidating, validating"
---

Hooks

# Self-Validating Agents in Claude Code: Automated Quality at Every Step

Build Claude Code agents that validate their own output using PostToolUse hooks, Stop hooks, and read-only validator agents.

**Problem**: Your Claude Code agents produce output that looks right but fails linting, misses required exports, or skips files entirely. You catch it during review, 20 minutes after the agent finished.

**Quick Win**: Add a PostToolUse hook directly to an agent definition. Every file this agent writes gets linted automatically, before it ever reaches you:

```p-4
# .claude/agents/frontend-builder.md
---
name: frontend-builder
description: Build React components with automatic quality checks
model: sonnet
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: 'npx eslint --fix "$CLAUDE_TOOL_INPUT_FILE_PATH" && npx prettier --write "$CLAUDE_TOOL_INPUT_FILE_PATH"'
---
You are a frontend builder agent. Create React components following
the project's established patterns. Every file you write is automatically
linted and formatted by your embedded hooks.
```

This agent cannot produce unlinted code. The validation is part of its identity, not an afterthought you bolt on later.

## [Three Tiers of Embedded Validation](#three-tiers-of-embedded-validation)

Self-validating agents work at three levels. Each catches different categories of problems, and they stack.

**Micro validation** fires on every tool use. PostToolUse hooks on [agent definitions](/blog/guide/agents/agent-fundamentals) run linters, formatters, and type checkers after each file write. Problems get caught within seconds of creation.

**Macro validation** fires when the agent tries to stop. [Stop hooks](/blog/tools/hooks/stop-hook-task-enforcement) check that the full output meets structural requirements: required files exist, exports are present, tests pass. The agent cannot declare "done" until the checks pass.

**Team validation** uses a separate agent. A read-only validator agent reviews the builder's complete output with fresh context. This is the [builder-validator pattern](/blog/guide/agents/team-orchestration) applied at the orchestration level.

## [PostToolUse: Micro Validation on Every Write](#posttooluse-micro-validation-on-every-write)

[Hooks embedded in agent frontmatter](/blog/tools/hooks/hooks-guide) run only while that agent is active. This scopes validation precisely. Your frontend agent runs ESLint. Your Python agent runs Ruff. Neither interferes with the other.

Here's a Python agent with Black and mypy validation:

```p-4
# .claude/agents/python-builder.md
---
name: python-builder
description: Build Python modules with automatic formatting and type checking
model: sonnet
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: 'black "$CLAUDE_TOOL_INPUT_FILE_PATH" && mypy "$CLAUDE_TOOL_INPUT_FILE_PATH" --ignore-missing-imports'
---
You are a Python builder agent. Write clean, typed Python code.
Your hooks automatically format with Black and check types with mypy.
```

The key advantage: these hooks are scoped to the agent. Your project-level [settings](/blog/guide/settings-reference) stay clean. When the orchestrator spawns this agent via the [Task tool](/blog/guide/agents/sub-agent-best-practices), validation travels with the agent automatically.

## [Stop Hooks: Macro Validation Before Completion](#stop-hooks-macro-validation-before-completion)

Micro validation catches syntax and formatting. But it won't catch missing files or incomplete implementations. For that, use a Stop hook that runs a validation script when the agent finishes.

Agent-level Stop hooks in frontmatter are converted to SubagentStop events. This script checks that required output files exist and contain expected content:

```p-4
#!/bin/bash
# .claude/scripts/validate-output.sh
# Validates that agent output meets structural requirements
 
INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
 
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  exit 0
fi
 
# Check that required files exist
REQUIRED_FILES=("src/components/index.ts" "src/components/Button.tsx")
MISSING=""
 
for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    MISSING="$MISSING $file"
  fi
done
 
if [ -n "$MISSING" ]; then
  echo "{\"decision\": \"block\", \"reason\": \"Missing required files:$MISSING\"}"
  exit 0
fi
 
# Check that index.ts contains exports
if ! grep -q "export" src/components/index.ts; then
  echo "{\"decision\": \"block\", \"reason\": \"index.ts has no exports. Add barrel exports for all components.\"}"
  exit 0
fi
 
exit 0
```

Wire it into the agent definition:

```p-4
---
name: component-builder
description: Build component libraries with output validation
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: 'npx prettier --write "$CLAUDE_TOOL_INPUT_FILE_PATH"'
  Stop:
    - hooks:
        - type: command
          command: "bash .claude/scripts/validate-output.sh"
---
```

Now this agent has both tiers. Every file gets formatted on write (micro). The full output gets validated before completion (macro). If the Stop hook blocks, the agent continues working until all checks pass.

## [Read-Only Validator Agents](#read-only-validator-agents)

For the third tier, create a dedicated validator agent that cannot modify files. The `disallowedTools` field enforces this at the tool level:

```p-4
# .claude/agents/output-validator.md
---
name: output-validator
description: Validate agent output without modifying files. Use after builder agents complete.
model: haiku
disallowedTools: Write, Edit, NotebookEdit
---
 
You are a read-only validator. Your job:
 
1. Read all files the builder created or modified
2. Verify exports, type safety, and error handling
3. Run the test suite with Bash
4. Report issues as a list. Do NOT fix anything.
 
If all checks pass, say "Validation passed" with a summary.
If issues exist, list each one with file path and line reference.
```

This agent literally cannot write files. It can only read and report. Pair it with a builder using [task dependencies](/blog/guide/agents/team-orchestration):

```p-4
TaskCreate(subject="Build auth module", description="...")
TaskCreate(subject="Validate auth module", description="Run output-validator on src/auth/")
TaskUpdate(taskId="2", addBlockedBy=["1"])
```

## [When to Use Each Tier](#when-to-use-each-tier)

**Micro only** (PostToolUse) works well for small, focused tasks where formatting and linting are the main quality concerns. Low overhead, immediate feedback.

**Micro + macro** (PostToolUse + Stop) fits agents that produce multiple files with structural requirements. The Stop hook catches what linting cannot: missing files, incomplete implementations, failing tests.

**All three tiers** suits critical code paths where you need both automated checks and an independent review. The validator agent provides a second opinion that the builder's hooks cannot.

Start with micro validation on your most-used agent. Add a Stop hook the first time an agent delivers incomplete output. Add the validator pattern when you need confidence that the output works as a whole, not just file by file. You can define these agent configurations in your [CLAUDE.md](/blog/guide/mechanics/claude-md-mastery) or as standalone agent files in `.claude/agents/`, whichever fits your [project structure](/blog/guide/agents/sub-agent-design) better.

## [Beyond Single Agents](#beyond-single-agents)

Self-validation and team validation aren't competing strategies. They're layers. An agent with embedded PostToolUse hooks and a Stop script handles 90% of quality issues before a validator ever looks at the output. The validator then focuses on integration concerns and architectural correctness instead of catching lint errors.

Build [custom agents](/blog/guide/agents/custom-agents) with validation baked in from the start. Set up the full [hooks system](/blog/tools/hooks/hooks-guide) for project-wide lifecycle events. And when you need team-level quality assurance, pair your self-validating builders with [read-only validators](/blog/guide/agents/team-orchestration) that catch what automation misses.

Last updated on

[Previous

Stop Hook](/blog/tools/hooks/stop-hook-task-enforcement)[Next

Session Lifecycle](/blog/tools/hooks/session-lifecycle-hooks)
