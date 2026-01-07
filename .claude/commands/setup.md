---
description: Initialize project context and indexing with Claude CodePro
model: opus
---
# SETUP MODE: Project Initialization and Context Building

**Purpose:** Scan project structure, create project documentation, initialize semantic search, configure MCP tools documentation, and store project knowledge in persistent memory.

---

## Execution Sequence

### Phase 0: Custom MCP Servers Configuration

**Purpose:** Document any custom MCP servers the user has added beyond the standard ones (tavily, Ref).

1. **Ask user about custom MCP servers:**

   Use AskUserQuestion:
   ```
   Question: "Do you have custom MCP servers to add to this project?"
   Options:
   - "Yes, let me add them now" - User will edit .mcp.json
   - "No, skip this step" - Proceed without custom servers
   ```

2. **If user selects "Yes":**

   Display instructions:
   ```
   Please add your custom MCP servers to .mcp.json now.

   The file is located at: [project_dir]/.mcp.json

   Example format:
   {
     "mcpServers": {
       "your-server-name": {
         "command": "npx",
         "args": ["-y", "your-mcp-package"]
       }
     }
   }

   Note: tavily and Ref are already configured.
   ```

   Then ask for confirmation:
   ```
   Question: "Have you finished adding your MCP servers?"
   Options:
   - "Yes, I've added them" - Proceed to create documentation
   - "Skip for now" - Continue without documenting custom servers
   ```

3. **Read .mcp.json and identify custom servers:**

   ```python
   Read(file_path=".mcp.json")
   ```

   Parse the JSON and filter out standard servers:
   - Exclude: `tavily`, `Ref`
   - Keep: All other servers as "custom"

4. **If custom servers found, create `.claude/rules/custom/mcp-tools.md`:**

   Generate content with this structure:

   ```markdown
   ## Custom MCP Servers

   This project uses the following custom MCP servers in addition to the standard ones (tavily, Ref).

   ### [Server Name]

   **Command:** `[command from config]`
   **Args:** `[args from config]`

   **When to use:**
   - [Brief description - ask user or infer from server name]

   **Example usage:**
   ```
   mcp__[server-name]__[tool_name](param="value")
   ```

   [Repeat for each custom server]
   ```

5. **Write the custom MCP tools rule:**
   ```python
   Write(file_path=".claude/rules/custom/mcp-tools.md", content=generated_content)
   ```

   If no custom servers found, skip creating this file.

---

### Phase 1: Project Discovery

1. **Scan Directory Structure:**
   ```bash
   tree -L 3 -I 'node_modules|.git|__pycache__|*.pyc|dist|build|.venv|.next|coverage|.cache|cdk.out|.mypy_cache|.pytest_cache|.ruff_cache'
   ```

2. **Identify Technologies by checking for:**
   - `package.json` → Node.js/JavaScript/TypeScript
   - `tsconfig.json` → TypeScript
   - `pyproject.toml`, `requirements.txt`, `setup.py` → Python
   - `Cargo.toml` → Rust
   - `go.mod` → Go
   - `pom.xml`, `build.gradle` → Java
   - `Gemfile` → Ruby
   - `composer.json` → PHP

3. **Identify Frameworks by checking for:**
   - React, Vue, Angular, Svelte (frontend)
   - Next.js, Nuxt, Remix (fullstack)
   - Express, Fastify, NestJS (Node backend)
   - Django, FastAPI, Flask (Python backend)
   - Check `package.json` dependencies or `pyproject.toml` for framework indicators

4. **Analyze Configuration:**
   - Read README.md if exists for project description
   - Check for .env.example to understand required environment variables
   - Identify build tools (webpack, vite, rollup, esbuild)
   - Check testing frameworks (jest, pytest, vitest, mocha)

### Phase 2: Create Project Documentation

1. **Check if project.md already exists:**
   - If exists, ask user: "project.md already exists. Overwrite? (y/N)"
   - If user says no, skip to Phase 3

2. **Generate `.claude/rules/custom/project.md` with this structure:**

```markdown
# Project: [Project Name from package.json/pyproject.toml or directory name]

**Last Updated:** [Current date/time]

## Overview

[Brief description from README.md or ask user]

## Technology Stack

- **Language:** [Primary language]
- **Framework:** [Main framework if any]
- **Build Tool:** [Vite, Webpack, etc.]
- **Testing:** [Jest, Pytest, etc.]
- **Package Manager:** [npm, yarn, pnpm, uv, cargo, etc.]

## Directory Structure

```
[Simplified tree output - key directories only]
```

## Key Files

- **Configuration:** [List main config files]
- **Entry Points:** [Main entry files like src/index.ts, main.py]
- **Tests:** [Test directory location]

## Development Commands

- **Install:** [e.g., `npm install` or `uv sync`]
- **Dev:** [e.g., `npm run dev` or `uv run python main.py`]
- **Build:** [e.g., `npm run build`]
- **Test:** [e.g., `npm test` or `uv run pytest`]
- **Lint:** [e.g., `npm run lint` or `uv run ruff check`]

## Architecture Notes

[Brief description of architecture patterns used, e.g., "Monorepo with shared packages", "Microservices", "MVC pattern"]

## Additional Context

[Any other relevant information discovered or provided by user]
```

3. **Write the file:**
   ```python
   Write(file_path=".claude/rules/custom/project.md", content=generated_content)
   ```

### Phase 3: Initialize Semantic Search with Vexor

1. **Get current working directory as absolute path:**
   ```bash
   pwd
   ```

2. **Check if Vexor is available:**
   ```bash
   vexor --version
   ```

   If not installed, inform user:
   ```
   Vexor CLI is not installed. Please install it to enable semantic code search.
   See: https://github.com/anthropics/vexor for installation instructions.
   ```

3. **Run initial indexing with a test search:**
   ```bash
   vexor search "main entry point" --path /absolute/path/to/project --mode code --top 3
   ```

   Note: First search will trigger indexing automatically (may take a minute for large codebases).

   Common exclusion patterns are respected via `.gitignore`. For additional exclusions:
   ```bash
   vexor search "query" --exclude-pattern "tests/**" --exclude-pattern ".js"
   ```

4. **Verify indexing with a broader search:**
   ```bash
   vexor search "configuration loading" --path /absolute/path/to/project --mode code --top 5
   ```

5. **Document available search modes for the project:**

   | Mode | Best For | Example |
   |------|----------|---------|
   | `code` | Python, JS, TS source files | `vexor search "API handler" --mode code` |
   | `outline` | Markdown documentation | `vexor search "authentication" --mode outline --ext .md` |
   | `name` | Finding files by name | `vexor search "config" --mode name` |
   | `auto` | Mixed content (default) | `vexor search "database connection"` |

### Phase 4: Completion Summary

Display a summary like:

```
┌─────────────────────────────────────────────────────────────┐
│                     Setup Complete!                         │
├─────────────────────────────────────────────────────────────┤
│ Created:                                                    │
│   ✓ .claude/rules/custom/project.md                        │
│   ✓ .claude/rules/custom/mcp-tools.md (if custom servers)  │
│                                                             │
│ Semantic Search (Vexor):                                    │
│   ✓ Vexor CLI available                                    │
│   ✓ Initial index built (respects .gitignore)              │
│   ✓ Test search successful                                 │
│                                                             │
│ MCP Servers:                                                │
│   ✓ Standard: tavily, Ref                                  │
│   ✓ Custom: [list custom server names or "none"]           │
├─────────────────────────────────────────────────────────────┤
│ Next Steps:                                                 │
│   1. Run 'ccp' to reload with new rules in context         │
│   2. Use /plan to create a feature plan                    │
│   3. Use /implement to execute the plan                    │
│   4. Use /verify to verify implementation                  │
│                                                             │
│ Semantic Search Usage:                                      │
│   vexor search "your query" --mode code --top 5            │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling

- **If tree command not available:** Use `ls -la` recursively with depth limit
- **If Vexor not installed:** Inform user and provide installation link, continue with other steps
- **If Vexor indexing is slow:** Run `vexor search` with `--no-cache` to rebuild the index fresh
- **If README.md missing:** Ask user for brief project description
- **If package.json/pyproject.toml missing:** Infer from file extensions and directory structure
- **If Vexor search returns no results:** Check path is correct, try broader query, or use `--no-respect-gitignore` if files are ignored

## Important Notes

- Use absolute paths when specifying `--path` for Vexor
- Don't overwrite existing project.md without confirmation
- Keep project.md concise - it will be included in every Claude Code session
- Focus on information that helps Claude understand how to work with this codebase
- Vexor respects `.gitignore` by default - use `--no-respect-gitignore` to include ignored files

## Indexing Exclusion Patterns

Vexor respects `.gitignore` by default, so common patterns like `node_modules/`, `__pycache__/`, `.venv/`, etc. are automatically excluded if they're in your `.gitignore`.

**For additional exclusions during search, use `--exclude-pattern`:**

```bash
# Exclude test files
vexor search "database" --exclude-pattern "tests/**"

# Exclude specific extensions
vexor search "config" --exclude-pattern ".js" --exclude-pattern ".css"

# Multiple exclusions
vexor search "handler" --exclude-pattern "vendor/**" --exclude-pattern "*.min.js"
```

**Common patterns typically in `.gitignore`:**

| Pattern | Reason |
|---------|--------|
| `node_modules/` | NPM dependencies |
| `__pycache__/`, `*.pyc` | Python bytecode |
| `.venv/`, `venv/` | Python virtual environments |
| `dist/`, `build/` | Build outputs |
| `.mypy_cache/`, `.pytest_cache/` | Tool caches |
| `coverage/` | Test coverage data |
| `.next/` | Next.js build output |

**To include ignored files:** Use `--no-respect-gitignore`
**To include hidden files:** Use `--include-hidden`
