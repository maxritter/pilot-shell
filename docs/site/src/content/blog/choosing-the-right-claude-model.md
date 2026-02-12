# Choosing the Right Claude Model for Your Task

Claude Code supports multiple models with different strengths. Picking the right one for each task saves money and gets better results.

## Available Models

| Model | Best For | Speed | Cost |
|-------|---------|-------|------|
| **Opus 4.6** | Complex architecture, multi-file refactors, debugging | Slower | Higher |
| **Sonnet 4** | General development, most coding tasks | Fast | Medium |
| **Haiku 3.5** | Quick lookups, simple edits, formatting | Fastest | Lowest |

## When to Use Each

### Opus 4.6

Use for tasks that require deep reasoning:

- Designing system architecture from scratch
- Debugging complex race conditions or state management issues
- Multi-file refactors that need to maintain consistency
- Understanding and modifying unfamiliar codebases
- Writing complex algorithms

Opus thinks more carefully and catches subtle issues that faster models miss.

### Sonnet 4

The default for most work:

- Implementing features from clear specifications
- Writing tests
- Code reviews
- Documentation
- Standard bug fixes
- API endpoint implementation

Sonnet handles 90% of coding tasks well. Start here unless you have a reason to upgrade.

### Haiku 3.5

Use for high-volume, low-complexity tasks:

- Formatting and style fixes
- Simple variable renames
- Generating boilerplate
- Quick file lookups
- Answering factual questions about the codebase

Haiku is 10x cheaper than Opus. For simple tasks, it's equally accurate and much faster.

## Switching Models

Change models mid-session with `/model`:

```
/model opus     # Switch to Opus for complex work
/model sonnet   # Back to Sonnet for implementation
/model haiku    # Haiku for quick tasks
```

Or set a default in settings:

```json
{
  "model": "claude-sonnet-4-20250514"
}
```

## Cost Optimization Strategy

1. **Start with Sonnet** — It handles most tasks
2. **Escalate to Opus** — When you hit complexity (deep bugs, architecture)
3. **Drop to Haiku** — For bulk simple operations
4. **Use sub-agents wisely** — Pilot uses Haiku for review sub-agents where appropriate

## Context Window

All current Claude models support 200K token context windows. Opus 4.6 also has a 1M token context beta for extremely large codebases. For most projects, 200K is sufficient — Pilot's Endless Mode handles the rest.

## Key Insight

The best model isn't always the most expensive one. Match the model to the task complexity and you'll get faster results at lower cost.
