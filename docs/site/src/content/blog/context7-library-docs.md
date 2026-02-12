# Context7: Access Library Docs Directly in Claude Code

Claude's training data has a cutoff date. Libraries update constantly — new APIs, changed parameters, deprecated methods. Context7 gives Claude access to current documentation for thousands of libraries, directly in your session.

## The Problem

Claude knows React 18 patterns, but not the hook that was added last month. It knows Express 4, but not the breaking change in Express 5. Without current docs, Claude:

- Uses deprecated APIs
- Misses new features that would simplify your code
- Guesses at parameter types instead of checking

## Setup

Add Context7 as an MCP server in `.mcp.json`:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstreamapi/context7-mcp@latest"]
    }
  }
}
```

That's it. Claude can now query documentation during any session.

## How It Works

Context7 indexes documentation for thousands of libraries. Claude uses two steps:

1. **Resolve** — Find the library ID (`/npm/react`, `/pytest-dev/pytest`)
2. **Query** — Ask a specific question about the library

Claude does this automatically when it needs documentation. You don't have to prompt it.

## When Claude Uses Context7

| Situation | What Happens |
|-----------|-------------|
| New dependency added | Claude checks setup and usage patterns |
| Unfamiliar API | Claude looks up the method signature |
| Getting library errors | Claude checks correct usage |
| Implementation choice | Claude checks what the library supports |

## Query Tips

Descriptive queries get better results:

- "how to create fixtures in pytest" (specific)
- "useState and useEffect patterns" (focused)
- "JWT authentication with refresh tokens" (practical)

Vague queries like "hooks" or "auth" return less useful results.

## Supported Libraries

Context7 covers libraries across all major ecosystems:

- **npm** — React, Vue, Next.js, Express, Prisma, and thousands more
- **PyPI** — pytest, FastAPI, SQLAlchemy, Django, pandas
- **Go** — Standard library, Gin, GORM, Cobra
- **Rust** — Tokio, Serde, Actix, Diesel

If a library has published documentation, Context7 likely has it indexed.

## Impact

With Context7, Claude writes code using current APIs instead of guessing from training data. This means fewer "this method doesn't exist" errors, fewer deprecated patterns, and code that matches the library version you're actually using.

Pilot installs Context7 automatically during setup. No additional configuration needed.
