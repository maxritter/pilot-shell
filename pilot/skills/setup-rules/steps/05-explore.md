## Step 5: Explore Codebase

### Step 5.1: Setup

1. Check `semble --help` — if available, use Semble for semantic exploration (Step 5.2). If not installed, skip Step 5.2 and use Grep/Glob/Read in Step 5.3.
2. **Ensure `docs/plans/` exists** — `/spec` stores plans here: `mkdir -p ./docs/plans`
3. **Directory structure:** `tree -L 3 -I 'node_modules|.git|__pycache__|dist|build|.venv|.next|coverage|.cache|cdk.out'`
4. **Technologies:** Check `package.json`, `pyproject.toml`, `tsconfig.json`, `go.mod`
5. **Source documents:** Find and read canonical docs — `docs/`, `**/ARCHITECTURE.md`, `**/CONTRIBUTING.md`, `**/docs/*.md`. These are the source of truth for generated rules — keep them open when writing.

### Step 5.2: Semantic Exploration with Semble — OPTIONAL

**Skip if Semble is not installed.** Use `semble search` (via Bash) or `mcp__semble__search` to understand each area that rules need to cover. Defaults return ~5 ranked chunks — no manual token-cap flags needed. Adapt queries to what the project actually does — these are starting points, not a checklist:

```bash
# Architecture & structure
semble search "how is the application structured and what are the main entry points" ./
semble search "how are services or modules organized" ./

# Patterns & conventions
semble search "how are API endpoints defined and routed" ./
semble search "how is authentication and authorization handled" ./
semble search "how is configuration loaded and environment variables used" ./
semble search "how is error handling done" ./
semble search "how are database models or data access patterns structured" ./

# Testing
semble search "how are tests organized and what testing patterns are used" ./
semble search "test fixtures and helpers" ./

# Build & deploy
semble search "how is the application built and deployed" ./
semble search "CI/CD pipeline configuration" ./
```

**Follow up with `semble find-related`** to discover parallel implementations from a promising hit:

```bash
semble find-related src/routes/users.ts 42 ./
```

For extracting an enclosing function/class at a known line, use `Read` with `offset`/`limit`, or `codegraph_node` when you have a symbol name.

### Step 5.3: Fill Gaps

**This is the primary exploration step when Semble is not available.**

1. **Grep** for key patterns — entry points, route definitions, config loading, error handling, auth, test organization
2. **Glob** for file structure — `**/*.test.*`, `**/routes/**`, `**/config/**`, `**/middleware/**`
3. **Read** 5-10 representative files in key directories
4. For each gap from Step 2: run a targeted search (Semble if available, otherwise Grep) to find current patterns
5. **Use CodeGraph** (`codegraph_context` to orient, `codegraph_search` → `codegraph_explore` for deep understanding, `codegraph_callers`/`codegraph_files` for structure) — CodeGraph is the primary exploration tool, not a fallback

**Monorepo:** Repeat Steps 5.1-5.3 for each sub-project identified in Step 2. Each sub-project gets its own exploration context.
