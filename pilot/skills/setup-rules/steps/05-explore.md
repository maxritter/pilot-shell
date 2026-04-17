## Step 5: Explore Codebase

### Step 5.1: Setup

1. Check `probe --version` — if available, use Probe for semantic exploration (Step 5.2). If not installed, skip Step 5.2 and use Grep/Glob/Read in Step 5.3.
2. **Ensure `docs/plans/` exists** — `/spec` stores plans here: `mkdir -p ./docs/plans`
3. **Directory structure:** `tree -L 3 -I 'node_modules|.git|__pycache__|dist|build|.venv|.next|coverage|.cache|cdk.out'`
4. **Technologies:** Check `package.json`, `pyproject.toml`, `tsconfig.json`, `go.mod`
5. **Source documents:** Find and read canonical docs — `docs/`, `**/ARCHITECTURE.md`, `**/CONTRIBUTING.md`, `**/docs/*.md`. These are the source of truth for generated rules — keep them open when writing.

### Step 5.2: Semantic Exploration with Probe — OPTIONAL

**Skip if Probe is not installed.** Use `probe search` (via Bash) to understand each area that rules need to cover. **Always use `--max-results 5 --max-tokens 2000`** to keep context lean. Adapt queries to what the project actually does — these are starting points, not a checklist:

```bash
# Architecture & structure
probe search "how is the application structured and what are the main entry points" ./ --max-results 5 --max-tokens 2000
probe search "how are services or modules organized" ./ --max-results 5 --max-tokens 2000

# Patterns & conventions
probe search "how are API endpoints defined and routed" ./ --max-results 5 --max-tokens 2000
probe search "how is authentication and authorization handled" ./ --max-results 5 --max-tokens 2000
probe search "how is configuration loaded and environment variables used" ./ --max-results 5 --max-tokens 2000
probe search "how is error handling done" ./ --max-results 5 --max-tokens 2000
probe search "how are database models or data access patterns structured" ./ --max-results 5 --max-tokens 2000

# Testing
probe search "how are tests organized and what testing patterns are used" ./ --max-results 5 --max-tokens 2000
probe search "test fixtures and helpers" ./ --max-results 5 --max-tokens 2000

# Build & deploy
probe search "how is the application built and deployed" ./ --max-results 5 --max-tokens 2000
probe search "CI/CD pipeline configuration" ./ --max-results 5 --max-tokens 2000
```

**Follow up with `probe extract`** to pull concrete examples for rules:

```bash
probe extract src/routes/users.ts#createUser
probe extract tests/conftest.py:1-30
```

### Step 5.3: Fill Gaps

**This is the primary exploration step when Probe is not available.**

1. **Grep** for key patterns — entry points, route definitions, config loading, error handling, auth, test organization
2. **Glob** for file structure — `**/*.test.*`, `**/routes/**`, `**/config/**`, `**/middleware/**`
3. **Read** 5-10 representative files in key directories
4. For each gap from Step 2: run a targeted search (Probe if available, otherwise Grep) to find current patterns
5. **Use CodeGraph** (`codegraph_context` to orient, `codegraph_search` → `codegraph_explore` for deep understanding, `codegraph_callers`/`codegraph_files` for structure) — CodeGraph is the primary exploration tool, not a fallback

**Monorepo:** Repeat Steps 5.1-5.3 for each sub-project identified in Step 2. Each sub-project gets its own exploration context.
