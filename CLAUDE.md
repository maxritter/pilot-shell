# CLAUDE.md — Pilot Shell DevSecOps Fork

This file provides guidance for AI assistants (Claude Code and others) working in this repository.

---

## What This Project Is

**Pilot Shell** is a proprietary AI-assisted development tool that wraps Claude Code with structured workflows, lifecycle hooks, memory persistence, and a multi-platform binary distribution system. This fork repositions the upstream project toward a **DevSecOps posture**: hardened permission defaults, explicit trust boundaries, and auditable controls.

**Architecture layers:**

| Layer | Path | Language | Purpose |
|-------|------|----------|---------|
| Launcher | `launcher/` | Python/Cython (compiled) | CLI entry, license validation, session/worktree management |
| Installer | `installer/` | Python | Step-based installation pipeline |
| Console | `console/` | TypeScript/React | Web UI for memory system (localhost:41777) |
| Pilot config | `pilot/` | JSON/Markdown/Python | Rules, commands, agents, hooks |
| Hooks | `pilot/hooks/` | Python | Lifecycle event interceptors |

> **Note:** `launcher/`, `console/`, and `docs/site/api/` are git-crypt encrypted. You cannot read their contents without the decryption key.

---

## Repository Layout

```
.
├── installer/           # Python step-based installer
│   ├── cli.py           # Installer entry point
│   ├── steps/           # Installation steps (prerequisites → finalize)
│   └── tests/           # Installer unit tests
├── launcher/            # [git-crypt] Core Python/Cython launcher
│   └── tests/           # Launcher unit/integration tests
├── console/             # [git-crypt] TypeScript/React console UI
├── pilot/               # Claude Code configuration and hooks
│   ├── settings.json    # Environment vars, permissions, spinner tips
│   ├── claude.json      # Claude Code settings
│   ├── .mcp.json        # MCP server definitions
│   ├── hooks/           # Python lifecycle hooks
│   ├── rules/           # Agent behavior rule files
│   ├── commands/        # Custom slash commands
│   └── agents/          # Agent specifications
├── docs/                # Documentation (Docusaurus site + fork-specific docs)
├── .github/workflows/   # CI/CD pipelines
├── install.sh           # Main installer script
├── uninstall.sh         # Uninstall script
├── pyproject.toml       # Python project config (Python 3.12, uv)
├── uv.lock              # Locked dependency manifest
├── cliff.toml           # git-cliff changelog config
└── .releaserc.json      # semantic-release config
```

---

## Development Environment

### Prerequisites

- **Python 3.12** (exact, not 3.11 or 3.13 — enforced in `pyproject.toml`)
- **uv** — package manager (`pip install uv` or via installer)
- **Bun** — for console TypeScript work
- **git-crypt** — to decrypt `launcher/` and `console/`

### Setup

```bash
# Install Python dependencies
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate
```

---

## Running Tests

```bash
# All Python tests
uv run pytest

# With coverage
uv run pytest --cov

# Specific test path
uv run pytest installer/tests/
uv run pytest launcher/tests/

# Console (TypeScript) tests
cd console && bun test
```

**Test configuration** (`pyproject.toml`):
- Test paths: `launcher/tests`, `installer/tests`, `pilot/hooks/tests`
- Async mode: `auto` (pytest-asyncio)
- Excluded: `.venv/`, `target/`, `.tox/`, `build/`, `misc/`

---

## Linting and Type Checking

```bash
# Lint and format (Ruff)
uv run ruff check .
uv run ruff format .

# Type checking
uv run basedpyright

# Dead code detection
uv run vulture .

# Run all checks via tox
uv run tox
```

**Ruff settings:**
- Line length: 120
- Quotes: double
- Docstrings: Google convention
- Rules enabled: `E, F, I, ERA, PLR0913, PLR0915`
- Key ignores: `D100, D104, E501, F401, F403, C901, B008`
- Tests exempt from `D` (docstring) and `UP` (upgrade) rules

---

## Code Conventions

### Python

- Python **3.12 only** — do not use 3.13+ features
- Use **double quotes** for strings
- **120-character** line limit
- Follow **Google docstring** format where docstrings are written
- Avoid unnecessary docstrings in test files
- Import order managed by Ruff (`I` rules)
- Type annotations expected (basedpyright in standard mode)

### TypeScript (console/)

- Runtime: **Bun**
- Framework: React 18 + Vite 6
- Styling: TailwindCSS + DaisyUI
- Run `bun run typecheck` before committing

### Commits

This project uses **Conventional Commits** for semantic versioning:

```
feat: add new feature          # triggers minor version bump
fix: correct a bug             # triggers patch bump
feat!: breaking change         # triggers major bump
chore: maintenance tasks       # no release
docs: documentation only       # no release
```

The CI release pipeline (`release.yml`) uses `semantic-release` to determine version bumps from commit history. Always use conventional commit format.

---

## Installer Architecture

The installer (`installer/`) runs a sequential pipeline of steps:

1. `prerequisites.py` — Verify OS, Python version, required tools
2. `claude_files.py` — Install Claude Code configuration files
3. `config_files.py` — Set up project config files
4. `dependencies.py` — Install runtime dependencies
5. `shell_config.py` — Shell integration (PATH, aliases)
6. `vscode_extensions.py` — Install recommended VSCode extensions
7. `finalize.py` — Final validation and cleanup

Each step is a class with `run()` and `rollback()` methods. When adding a new step, follow this pattern and register it in `installer/cli.py`.

---

## Pilot Hooks System

Hooks in `pilot/hooks/` intercept Claude Code lifecycle events:

| Event | Purpose |
|-------|---------|
| `SessionStart` | Initialize context, check prerequisites |
| `UserPromptSubmit` | Validate prompts, enforce spec mode |
| `PreToolUse` | Guard dangerous tool calls |
| `PostToolUse` | Validate outputs, trigger linting |
| `Stop` | Cleanup, persist memory |
| `SessionEnd` | Final teardown |
| `PreCompact` | Prepare for context compression |

Hooks run via `uv run python` (Python hooks) or `bun` (TypeScript hooks). Hook scripts live in `pilot/hooks/` and are referenced in `pilot/settings.json` under the `hooks` key.

---

## Security Posture (Fork-Specific)

This fork hardens the following upstream defaults:

| Setting | Upstream | This Fork |
|---------|----------|-----------|
| `defaultMode` | `bypassPermissions` | `default` |
| `skipDangerousModePermissionPrompt` | `true` | `false` |
| `enableAllProjectMcpServers` | `true` | `false` |

**Known remaining gaps** (tracked in `docs/devsecops-fork-roadmap.md`):
- Unsigned installer binaries
- `npx -y` unpinned MCP servers (non-deterministic deps)
- External HTTP MCP endpoint (`mcp.grep.app`)

When modifying `pilot/settings.json` or `pilot/.mcp.json`, do not re-introduce permissive defaults. Any new MCP server should be pinned to a specific version and reviewed.

---

## MCP Servers

Defined in `pilot/.mcp.json`:

| Server | Command | Purpose |
|--------|---------|---------|
| `context7` | `npx @upstash/context7-mcp@2.1.4` | Library documentation lookup |
| `codebase-memory-mcp` | `~/.local/bin/codebase-memory-mcp` | Code knowledge graph |
| `web-search` | `npx open-websearch@1.2.7` | DuckDuckGo search |
| `grep-mcp` | `https://mcp.grep.app` | Remote code search |
| `web-fetch` | `npx fetcher-mcp@0.3.9` | Web scraping |

`enableAllProjectMcpServers` is `false` — servers must be explicitly enabled.

---

## CI/CD Pipelines

### `release.yml` — Production Release

Triggers on push to `main` with qualifying conventional commits, or manual dispatch.

**Job sequence:**
1. `check-trigger` — semantic-release dry-run to decide if release needed
2. `security-scan` — Trivy (CRITICAL/HIGH vulnerabilities + secrets)
3. `python-tests` — pytest with coverage
4. `console-tests` — Bun tests
5. `console-build` — TypeScript typecheck + Vite build
6. `build-pilot-*` — Multi-platform binaries (Linux/Darwin × x86_64/arm64)
7. `prepare-release` — git-cliff changelog generation
8. `approve-release` — **Manual approval gate** (production environment)
9. `publish-release` — Create GitHub release + upload artifacts + provenance attestation
10. `deploy-website` — Vercel deployment (parallel with publish)

### `claude.yml` — AI Code Review

- Triggers on `@claude` mentions in issues/PRs and PR open/reopen events
- Runs full review on PR open, incremental review on push
- Uses Anthropic's Claude Code action

### Security Scanning

- Tool: **Trivy** (configured via `.trivyignore`)
- Scope: CRITICAL and HIGH severity only
- Skips: `.venv/`, `node_modules/`, `console/node_modules/`, `launcher/`, `docs/site/api/`

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python deps, test config, ruff/pyright settings |
| `pilot/settings.json` | Claude Code env vars, permissions, hooks, spinner tips |
| `pilot/.mcp.json` | MCP server definitions |
| `pilot/claude.json` | Claude Code feature flags |
| `docs/fork-delta.md` | Audit of divergences from upstream |
| `docs/devsecops-fork-roadmap.md` | Security improvement roadmap |
| `FEATURE_TEMPLATES.md` | Stubs for planned features |
| `.releaserc.json` | Semantic-release configuration |
| `cliff.toml` | Changelog generation rules |

---

## What NOT to Do

- Do not change `defaultMode` to `bypassPermissions` in `pilot/settings.json`
- Do not set `skipDangerousModePermissionPrompt: true`
- Do not set `enableAllProjectMcpServers: true`
- Do not add MCP servers using `npx -y` (unpinned) without documenting the risk
- Do not commit to `main` directly — use feature branches and PRs
- Do not use Python 3.13+ syntax
- Do not skip the manual approval gate in `release.yml` without explicit authorization
- Do not attempt to read or modify git-crypt encrypted paths without the key

---

## Fork Identity

This is a DevSecOps fork of `maxritter/pilot-shell`. The fork divergence is tracked in `docs/fork-delta.md`. Upstream identity artifacts (plugin.json author fields, etc.) are being replaced incrementally. Do not treat upstream conventions as authoritative — prefer the security-hardened defaults in this fork.
