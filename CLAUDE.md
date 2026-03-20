# CLAUDE.md — Pilot Shell DevSecOps

This file documents the codebase structure, development workflows, and conventions for AI assistants working in this repository.

---

## Project Overview

**Pilot Shell** is a professional development environment layered on top of Claude Code. It enforces quality, testing, and planning workflows through:

- A Python CLI **installer** (7-step setup)
- A Python **launcher** (session manager and runtime wrapper)
- A **pilot plugin** (rules, commands, hooks, agents installed into `~/.claude/`)
- A TypeScript/React **console** (web dashboard for specs, memory, usage, settings)

**Current version:** 7.7.1
**Python:** 3.12 (strictly pinned)
**Node:** 18+ / Bun 1.0+

---

## Repository Structure

```
pilot-shell-devsecops/
├── installer/              # Python CLI installer (7-step setup)
│   ├── cli.py              # Argparse CLI, step orchestration, license validation
│   ├── context.py          # Installation context (platform, paths, env state)
│   ├── ui.py               # Rich console UI (spinners, progress, colors)
│   ├── downloads.py        # Binary/artifact downloading
│   ├── errors.py           # Custom exception hierarchy
│   ├── platform_utils.py   # macOS/Linux/WSL2 platform detection
│   └── steps/              # One file per installation step (1–7)
├── launcher/               # Session manager (git-crypt encrypted)
│   ├── cli.py              # Main CLI interface
│   ├── wrapper.py          # Claude Code execution wrapper
│   ├── auth.py             # OAuth/license authentication
│   ├── session.py          # Session state management
│   ├── model_config.py     # Model routing (Opus vs Sonnet)
│   ├── settings_injector.py
│   ├── statusline/         # Three-line status display (widgets, providers)
│   └── ...
├── pilot/                  # Rules, commands, hooks, agents
│   ├── rules/              # Always-loaded markdown context rules
│   ├── commands/           # Custom slash commands (spec, setup-rules, etc.)
│   ├── agents/             # Sub-agents (plan-reviewer, spec-reviewer)
│   ├── hooks/              # Pre-commit quality enforcement (TypeScript)
│   └── scripts/            # Helper scripts
├── console/                # TypeScript/React web dashboard (git-crypt encrypted)
│   ├── src/                # React components, hooks, utilities
│   └── tests/              # Bun/Jest tests
├── docs/                   # Docusaurus + SPA website
├── .github/
│   └── workflows/
│       ├── claude.yml      # Claude Code AI assistance on PRs/issues
│       ├── release.yml     # Full multi-stage release pipeline
│       ├── release-dev.yml # Dev release workflow
│       └── deploy-website.yml
├── install.sh              # Global one-liner installation script
├── uninstall.sh
├── pyproject.toml          # Python build config, linting, test config
├── .releaserc.json         # Semantic release config (Angular preset)
└── uv.lock                 # Python dependency lock file
```

---

## Development Commands

### Python (installer + launcher)

```bash
# Install dev dependencies
uv sync

# Run all Python tests with coverage
uv run pytest -v --cov=installer --cov=launcher

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Type checking
uv run basedpyright
```

### TypeScript (console)

```bash
cd console

# Install dependencies
bun install

# Run tests
bun test

# Type check + build
bun run typecheck
bun run build

# Build hooks bundle
node scripts/build-hooks.js
```

### Release

Releases are fully automated via `release.yml`. Commit with `feat:` or `fix:` prefix to trigger. Manual approval gate exists before publishing.

---

## Testing Requirements

**This project enforces TDD — never write code without a corresponding test.**

| Requirement | Rule |
|-------------|------|
| Minimum coverage | 80% (enforced in CI, blocks releases) |
| Failing tests | Zero tolerance — CI blocks on any failure |
| Cycle | RED → GREEN → REFACTOR |
| External deps | Always mock: HTTP, subprocess, file I/O, database |
| Mock audit | When a dependency signature changes, update ALL tests using it |
| E2E | Use playwright-cli with session isolation |

**Test locations:**
- `installer/tests/unit/` — Unit tests per module + steps
- `launcher/tests/unit/` and `launcher/tests/integration/`
- `pilot/hooks/tests/`
- `console/tests/` (sqlite, context, worker)

---

## Code Style and Linting

### Python
- **Formatter:** Ruff (`uv run ruff format .`)
- **Linter:** Ruff with rules: `E`, `F`, `I`, `ERA`, `PLR0913`, `PLR0915`
- **Line length:** 120 characters
- **Quotes:** Double quotes
- **Docstrings:** Google style
- **Type checker:** basedpyright (standard mode, Python 3.12)
- **Max function args:** 13 (`PLR0913`)
- **Max statements per function:** 50 (`PLR0915`)

### TypeScript / JavaScript
- **Formatter:** Prettier (120 char print width)
- **Linter:** ESLint
- **Mode:** Strict TypeScript

### Conventions
- All Python code targets Python 3.12+ syntax exclusively
- No backwards-compat shims for older Python versions
- Dead code detected by ERA rules is removed, not commented out
- Test files may relax some complexity limits (see pyproject.toml per-file ignores)

---

## Architecture Patterns

### 1. Step-Based Installer
Each installation step is a class inheriting from `BaseStep`. Steps must be idempotent (safe to re-run). Installation can rollback on failure. Progress is tracked via Rich UI.

```python
# Pattern: each step in installer/steps/
class SomeStep(BaseStep):
    def run(self, context: InstallContext) -> StepResult: ...
    def rollback(self, context: InstallContext) -> None: ...
```

### 2. Spec-Driven Development (`/spec`)
The primary workflow for non-trivial work:

```
Feature mode:
  Plan (search, questions, write spec)
  → Approve (plan-reviewer sub-agent)
  → Implement (git worktree, TDD, hooks)
  → Verify (tests, spec-reviewer sub-agent, merge)

Bugfix mode:
  Investigate (trace root cause)
  → Test-Before-Fix (regression test, minimal fix)
  → Verify (lightweight review)
```

Use `/spec` for features and bugs. Use quick mode only for trivial, isolated changes.

### 3. Pre-Commit Hooks Pipeline
Hooks run on every file edit and enforce:
- ruff (Python lint + format)
- ESLint + Prettier (TypeScript/JavaScript)
- basedpyright (type checking)
- TDD enforcement (blocks committing untested code)
- RTK output compression (token optimization, 60–90% savings)
- Memory capture for persistent context

### 4. Rules + Skills System
- **Rules** (`pilot/rules/*.md`) — Always-loaded context rules, scoped by file type
- **Skills** (`~/.claude/skills/`) — Lazy-loaded on trigger, frontmatter always available
- **Agents** (`pilot/agents/*.md`) — Sub-agents for planning review and code review
- **Commands** (`pilot/commands/*.md`) — Custom prompts via `/command-name`

Rule loading is conditional based on the file types being edited to minimize context usage.

### 5. Model Routing
- **Opus 4.6** — Planning phase (higher intelligence)
- **Sonnet 4.6** — Implementation and verification (faster, cost-effective)
- Configurable per-phase via Console Settings

### 6. MCP Integration
Six built-in MCP servers: library docs, persistent memory, web search, GitHub code search, web fetching, code knowledge graph. All are lazily initialized. User MCP servers are auto-discovered.

### 7. Memory System
Persistent observations (decisions, discoveries, bugfixes) stored in Console-backed SQLite. Browsable by type, searchable, cross-session. Integrated with `/spec` workflow.

---

## CI/CD Pipeline

**`release.yml`** stages (in order):

1. **check-trigger** — Detect releasable commits (`feat:` or `fix:`)
2. **security-scan** — Trivy vulnerability + secret scanner (critical/high blocking)
3. **python-tests** — pytest with 80% coverage requirement
4. **console-tests** — Bun test runner
5. **console-build** — TypeScript typecheck + Vite build
6. **prepare-release** — Semantic release dry-run or manual version bump
7. **build-pilot-\*** — Binary compilation matrix (Linux/macOS × x86_64/arm64)
8. **approve-release** — Manual approval gate (environment: `production`)
9. **publish-release** — GitHub release, artifact upload, CHANGELOG generation
10. **deploy-website** — Vercel production deployment

**`claude.yml`** — Triggered by `@claude` mentions in issues/PRs. Uses `anthropics/claude-code-action@v1`.

---

## Versioning and Releases

- **Scheme:** Semantic versioning (SemVer) via `semantic-release` with Angular preset
- `feat:` → minor bump, `fix:` → patch bump, breaking change → major bump
- Version updated automatically in `installer/__init__.py`, `launcher/__init__.py`, and `package.json` files
- **Never manually edit version numbers** — let semantic-release handle it

---

## Git Conventions

- Branch naming for Claude: `claude/<description>-<sessionId>`
- Commit messages follow Angular convention: `type(scope): message`
  - Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`
- Never skip pre-commit hooks (`--no-verify`)
- Never force-push to `main` or `master`
- Prefer specific `git add <file>` over `git add -A`

---

## Encrypted Files

Several paths are encrypted with **git-crypt** and are not readable without the key:

- `launcher/**`
- `console/**`
- `docs/site/api/**`

Do not attempt to decode or modify these files without the `GIT_CRYPT_KEY` secret available.

---

## Security and Privacy

- **Code never leaves the machine** through Pilot Shell itself
- External network calls are limited to: license validation (license key + org ID), activation (machine fingerprint), trial start (hashed fingerprint)
- All tools run locally: Probe, RTK, codebase-memory-mcp, persistent memory, hooks
- Dependency vulnerability scanning runs in every release via Trivy
- `.trivyignore` contains documented exemptions for known non-issues

---

## Key Dependencies

### Python
| Package | Purpose |
|---------|---------|
| `rich` | CLI UI (spinners, progress, colors) |
| `platformdirs` | Cross-platform config paths |
| `cryptography` | Encryption utilities |
| `pytest` + `pytest-cov` | Testing + coverage |
| `ruff` | Linting + formatting |
| `basedpyright` | Type checking |
| `tox` | Test environment matrix |

### TypeScript / Console
| Package | Purpose |
|---------|---------|
| `@anthropic-ai/claude-agent-sdk` | Agent runtime |
| `@modelcontextprotocol/sdk` | MCP tool integration |
| `@xenova/transformers` | Embeddings |
| `express` | Web server |
| `zod` | Schema validation |
| `react` 18 + `vite` | UI framework + build |
| `tailwindcss` + `daisyui` | Styling |
| `recharts` | Usage charts |

---

## Common Pitfalls

1. **Do not run `pytest` directly** — use `uv run pytest` to ensure the correct virtualenv
2. **Do not skip hooks** — pre-commit hooks enforce quality gates; fix root causes instead
3. **80% coverage is a hard gate** — CI fails if coverage drops below this threshold
4. **Encrypted files** — `launcher/` and `console/` are git-crypt encrypted; modifications without the key will corrupt them
5. **Python 3.12 only** — do not use syntax or APIs from older Python versions
6. **TDD first** — write failing tests before implementation, always
7. **Use `/spec` for non-trivial work** — quick mode is only for isolated, trivial changes
8. **Version numbers** — never manually edit; controlled by semantic-release automation
