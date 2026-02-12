# Custom Slash Commands and --init for Claude Code

Slash commands let you package complex instructions into single invocations. Combined with `--init`, they enable session-type-specific workflows without custom hooks.

## Creating Slash Commands

Add markdown files to `.claude/commands/`:

```markdown
<!-- .claude/commands/review.md -->
Review the current git diff for:
1. Logic errors and edge cases
2. Missing error handling
3. Security vulnerabilities (OWASP top 10)
4. Performance issues

Show findings grouped by severity (critical → low).
```

Invoke with `/review` in any session.

## Command Parameters

Commands can accept arguments using `$ARGUMENTS`:

```markdown
<!-- .claude/commands/test.md -->
Write comprehensive tests for: $ARGUMENTS

Follow TDD methodology:
1. Write failing test first
2. Verify it fails for the right reason
3. Implement minimum code to pass
4. Verify all tests pass
```

Usage: `/test the calculateDiscount function in src/pricing.ts`

## Project vs User Commands

| Location | Scope | Shared? |
|----------|-------|---------|
| `.claude/commands/` | Project | Yes (committed to git) |
| `~/.claude/commands/` | Global | No (personal) |

Project commands are team-shared workflows. Global commands are personal shortcuts.

## Using --init for Session Context

The `--init` flag runs a slash command at session start:

```bash
claude --init /commands/backend-context.md
```

This loads specific context before you start working. Different init files for different work types:

```bash
# Backend development
claude --init /commands/backend.md

# Frontend work
claude --init /commands/frontend.md

# Code review session
claude --init /commands/review-mode.md
```

## Practical Command Examples

### Deploy checklist

```markdown
<!-- .claude/commands/deploy.md -->
Pre-deployment checklist:
1. Run full test suite
2. Check for uncommitted changes
3. Verify build succeeds
4. Run linter with zero warnings
5. Check for TODO/FIXME comments in changed files

Report status for each item. Block if any critical item fails.
```

### Quick refactor

```markdown
<!-- .claude/commands/refactor.md -->
Refactor $ARGUMENTS:
- Extract duplicated logic into shared functions
- Improve variable names for clarity
- Split functions longer than 30 lines
- Keep all existing tests passing
- Run tests after each change
```

### Onboarding context

```markdown
<!-- .claude/commands/onboard.md -->
You're working on [Project Name]. Key architecture:
- Backend: Python/FastAPI in src/api/
- Frontend: React/TypeScript in src/web/
- Database: PostgreSQL with SQLAlchemy ORM
- Tests: pytest (backend), vitest (frontend)

Always run `uv run pytest -q` after backend changes.
Always run `npm test` after frontend changes.
```

## How Pilot Uses Commands

Pilot installs several commands that power its workflow:

- `/spec` — Triggers the spec-driven development pipeline
- `/sync` — Synchronizes rules and skills with the codebase
- `/learn` — Extracts reusable knowledge into skills
- `/vault` — Manages shared team assets

These commands are markdown files that orchestrate multi-step workflows, proving that slash commands scale from simple shortcuts to complex automations.
