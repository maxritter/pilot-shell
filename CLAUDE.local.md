# CLAUDE.local.md

Direct development guidance for quick changes without spec-driven flow.

## Core Rules

**Git:** READ-ONLY - `git status/diff/log/show/branch` ✅ | `git add/commit/push` ❌
**Python:** `uv` not pip | One-line docstrings | No inline comments | Edit > Create
**Standards:** TDD mandatory | Check diagnostics | DRY/YAGNI | Clean imports
**Context:** If approaching 80% (160k tokens) → `/remember` → `/clear` → Continue

## Quick Change Workflow

**For small changes (< 5 files):**
1. `getDiagnostics()` → 2. Query Cipher → 3. Search code → 4. TodoWrite → 5. TDD → 6. Implement → 7. Verify → 8. Store in Cipher

**TDD (NON-NEGOTIABLE):** Test first → Verify fail → Minimal code → Verify pass → Refactor
**Test commands:** `uv run pytest -m unit` | `-m integration` | `--cov=.`
**API E2E:** Create Postman collection → Run `newman run postman/collections/feature.json`
**Code before test = DELETE and restart**

## MCP Tools

**Memory:** Cipher (`ask_cipher`) | Claude Context (`search_code`) | IDE (`getDiagnostics`)
**Docs:** Context7 (`resolve-library-id` → `get-library-docs`) | Ref (`ref_search_documentation`)
**Data:** Database (`execute_sql`) | FireCrawl (`discover_tools_by_words` → `firecrawl_scrape/search`)
**UI Testing**: Playwright (`discover_tools_by_words` → `playwright browser`)
**Discovery:** `discover_tools_by_words` → `get_tool_schema` → `bridge_tool_request`

## When to Use This vs /plan + /implement

**Use THIS for:**
- Bug fixes (< 5 files)
- Simple feature additions
- Refactoring existing code
- Adding tests to existing features
- Quick API endpoint changes

**Use `/plan` → `/implement` for:**
- New features (> 5 files)
- Architecture changes
- Database schema changes
- Complex integrations
- Multi-step implementations

## Key Principles

**Do exactly what's asked** | **Test-first always** | **Check Cipher first** | **Edit > Create** | **No unsolicited docs**

## Available Skills (Auto-Active)

**Testing:** @testing-test-driven-development | @testing-debugging | @testing-final-verification
**Global:** @global-coding-style | @global-error-handling | @global-validation
**Backend:** @backend-api | @backend-models | @backend-queries | @backend-migrations
**Frontend:** @frontend-accessibility | @frontend-components | @frontend-css | @frontend-responsive

## Final Checklist

Before claiming completion:
1. `getDiagnostics()` - Zero errors
2. `uv run pytest` - All pass
3. `uv run ruff check .` - Clean
4. Show actual output (no "should work" claims)
5. Store learnings in Cipher
