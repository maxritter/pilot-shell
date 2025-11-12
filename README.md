<div align="center">

<img src="docs/img/logo.png" alt="Claude CodePro" width="400">

### A Professional System for Building Quality Code

Stop vibe coding, start shipping systematically with Spec-Driven Development, TDD, and automated workflows.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Optimized-blue)](https://claude.ai)
![Spec-Driven](https://img.shields.io/badge/Spec-Driven-orange.svg)
![TDD](https://img.shields.io/badge/TDD-Test--Driven--Development-green.svg)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](http://makeapullrequest.com)

---

#### 🆕 What's New in v2.1.0

- **Automated Rules Builder** - Modular system that auto-generates Slash Commands and Skills
- **`/quick` Command** - Alternative to spec-driven workflow for fast fixes and refactoring

---

#### [⭐ Star this repo](https://github.com/maxritter/claude-codepro) • [🚀 Releases](https://github.com/maxritter/claude-codepro/releases) • [🎓 Join the Academy](https://www.claude-code.pro)

</div>

---

## 📦 What's Inside

<img src="docs/img/ide-screenshot.png" alt="IDE Screenshot" width="600">

### 📋 Flexible Development Workflows via Slash Commands

**Quick Development** (For fast fixes, refactoring, experiments):
- `/quick` - Fast, focused development without spec-driven overhead → No mandatory TDD (Sonnet 4.5)

**Spec-Driven Workflow** (For complex features requiring planning and testing):
- `/plan` - Based on your input asks the right questions → Detailed spec with exact code (Opus 4.1)
- `/implement` - Execute spec with mandatory TDD → Auto-manages context when full (Sonnet 4.5)
- `/remember` - Stores learnings in cross-session memory → Continue after /clear (Sonnet 4.5)
- `/verify` - E2E spec verification with CodeRabbit AI review → All tests, quality, security (Sonnet 4.5)

### 💡 Modular Rules System with Auto-Generated Commands & Skills
- **Rules Builder** - Automatically assembles commands and skills from markdown rules on every `cc` startup
- **Core Rules** - Coding standards, TDD enforcement, error handling, validation, context management
- **Extended Rules** - Domain-specific rules auto-converted to skills (@backend-api, @frontend-components, etc.)
- **Workflow Rules** - Command-specific behavior for /plan, /implement, /verify, /quick, /remember
- **Flexible Customization** - Edit `.claude/rules/config.yaml` to adjust which rules apply to which commands

### 🔌 Enhanced Context and Capabilities via MCP Servers
- **Cipher & Claude Context** - Cross-session memory and semantic code search for optimal context
- **Context7 & Ref** - Up-to-date library documentation with limited context blur
- **DBHub & FireCrawl** - Database access and web scraping for dynamic data retrieval
- **MCP Funnel** - Allows to plug-in more MCP servers as needed without wasting context

### 🛠️ Testing and Quality via Automated Tool Installation
- **CodeRabbit** - AI-powered code review for quality and security
- **Qlty** - Automated code quality hooks for all programming languages
- **Newman** - API end-to-end testing with Postman collections
- **uv, ruff, mypy, basedpyright** - Python linter, formatter, and type checker

### 🏗️ Automated Dev Container Setup (VS Code / Cursor / Windsurf)
- **Integrated Features** - Zsh, Node.js, Docker-in-Docker, uv, ruff, basedpyright, git, fzf
- **IDE Extensions** - Python, Docker, SQL, testing, formatting, and development tools
- **CLI Tools** - qlty, Claude Code, Statusline, dotenvx, CodeRabbit, Cipher, Newman
- **Local Database** - Local PostgreSQL instance on port 5433 for development and testing

---

## 🚀 Getting Started

### 📋 Prerequisites

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** or **[OrbStack](https://orbstack.dev/download)**
- **[VS Code](https://code.visualstudio.com/)** or **[Cursor](https://cursor.com/)** or **[Windsurf](https://windsurf.dev/)**
- **[Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)**
- **Optional**: **[Warp](https://www.warp.dev/)** for the best terminal experience

### 📥 Installation

1. Clone this repository: `git clone https://github.com/maxritter/claude-codepro.git`
2. Copy `.env.example` to `.env` and add your credentials and API keys
```bash
cp .env.example .env
vim .env
```
3. Open folder in VS Code, click on the button on the bottom-left: `Reopen in Container` or open the command pallette via `Ctrl + Shift + P` and then use `> Dev Containers: Reopen in Container`
4. Wait for automatic build to finish, this can take a couple of minutes (feel free to watch the logs in `Terminal`)
<img src="docs/img/ide-setup-finish.png" alt="Setup finish Screenshot" width="600">
5. Run `cc` (which is an alias we created) in the Terminal to finish CC Setup, `cr` to finish CodeRabbit setup
```bash
# alias to spawn claude code with loaded environment varaibles
cc
# code rabbit cmd line tool and setup
cr
```

---

## 📒 How-to-use

### ⚙️ Configuration

1. Open Claude Code in the IDE Terminal, Extension or an external Terminal like Warp with the `cc` command

2. In CC, run `/config` to set auto-connect to IDE to true and set `Auto-compact=false` for best experience
<img src="docs/img/ide-setup-config.png" alt="Setup config Screenshot" width="600">

3. In CC, run `/ide` to connect to VS Code diagnostics and make sure all MCP servers for `/mcp` are online
<img src="docs/img/ide-setup-mcp.png" alt="Setup mcp Screenshot" width="600">

4. In CC, run `/context` to verify context looks similar to this screenshot with less than 20% used
<img src="docs/img/ide-setup-context.png" alt="Setup context Screenshot" width="600">

5. In VS Code, click `START` in the lower bar of the IDE to start a split terminal and monitor CC usage with `/usage`
<img src="docs/img/ide-setup-start.png" alt="Start command Screenshot" width="600">

### 👣 First Steps

**For Quick Changes:**
- Use `/quick` - Fast development for fixes, refactoring, or experiments without spec overhead
- TDD not enforced, but best practices still apply via core rules and auto-injected skills

**For Complex Features (Spec-Driven & TDD):**
- Start with `/plan` - Provide your input and it will ask clarifying questions to create a spec
- Use `/implement` to execute the spec with automatic TDD, best practices and context management
- When context fills, `/remember` automatically updates your plan and stores learnings
- After spec completion, run `/verify` to run CodeRabbit AI review, all tests, and quality checks

### 🎯 Rules Builder
The system uses a modular rules-based architecture that automatically generates slash commands and skills:

- `.claude/rules/core/` - Fundamental rules injected into all commands
- `.claude/rules/workflow/` - Command-specific behavior (plan.md, implement.md, verify.md, quick.md, remember.md)
- `.claude/rules/extended/` - Domain-specific rules auto-converted to individual skills
- `.claude/rules/config.yaml` - Defines which rules are included in which commands
- `.claude/rules/builder.py` - Assembles markdown rules into commands and skills

**Auto-Rebuild:** Commands and skills are automatically regenerated on every `cc` startup, making customization seamless.

## ⚖️ What Makes This Different

**Compared to Other Spec-Driven Frameworks (SpecKit, AgentOS, OpenSpec):**

- 💾 **Persistent Memory** - Cross-session memory maintains knowledge between resets
- ⚡ **Token-Optimized** - No tokens wasted during too complex planning, just works
- ✅ **Production-Grade** - Actively used in client and enterprise projects
- 📝 **Enforced TDD** - Code written before tests gets deleted automatically
- 💯 **Real Verification** - Must show actual outputs based on tests, not assumptions
- 🛠️ **Complete Ecosystem** - Skills, MCP servers, testing tools are integrated and configured
- 📦 **Works Immediately** - Pre-configured automated setup with everything you need

---

## 👥 Who This Is For

- **Professional Developers** - Shipping to production with quality standards
- **Solo Builders** - Managing complex features without losing context
- **Engineering Teams** - Ensuring consistent TDD and code quality
- **Frustrated Coders** - Tired of half-tested, "should work" implementations

---

## 🎓 Claude CodePro Academy Coming Soon!

If you want to dive deeper into the setup and advanced usage of Claude CodePro, check out the upcoming  academy that starts with 10 comprehensive modules where we do a deep-dive into all important topics:

### ➡️ [www.claude-code.pro](https://www.claude-code.pro)

---

## 🤝 Contributing

Contributions welcome: custom skills, MCP integrations, workflow improvements, bug reports.

---

## 🙏 Acknowledgments

- **[astral-sh/uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[astral-sh/ruff](https://github.com/astral-sh/ruff)** - Fast Python linter and formatter
- **[DetachHead/basedpyright](https://github.com/DetachHead/basedpyright)** - Enhanced Python type checker
- **[python/mypy](https://github.com/python/mypy)** - Static type checker for Python
- **[dotenvx/dotenvx](https://github.com/dotenvx/dotenvx)** - Environment variable management
- **[postmanlabs/newman](https://github.com/postmanlabs/newman)** - End-to-End API testing
- **[pytest-dev/pytest](https://github.com/pytest-dev/pytest)** - Python testing framework
- **[qltysh/qlty](https://github.com/qltysh/qlty)** - Code quality automation
- **[obra/superpowers](https://github.com/obra/superpowers)** - CC Skills inspiration
- **[buildermethods/agent-os](https://github.com/buildermethods/agent-os)** - CC Spec-Driven inspiration
- **[campfirein/cipher](https://github.com/campfirein/cipher)** - CC Cross-session memory
- **[zilliztech/claude-context](https://github.com/zilliztech/claude-context)** - CC Semantic code search
- **[hagan/claudia-statusline](https://github.com/hagan/claudia-statusline)** - CC Status line integration
- **[upstash/context7](https://github.com/upstash/context7)** - MCP Library documentation
- **[ref-tools/ref-tools-mcp](https://github.com/ref-tools/ref-tools-mcp)** - MCP Documentation search
- **[mendableai/firecrawl-mcp](https://github.com/mendableai/firecrawl)** - MCP Web scraping
- **[bytebase/dbhub](https://github.com/bytebase/dbhub)** - MCP PostgreSQL connectivity
- **[chris-schra/mcp-funnel](https://github.com/chris-schra/mcp-funnel)** - MCP Tool filtering

---

Made with ❤️ by [Max Ritter](https://www.maxritter.net)

[🌐 claude-code.pro](https://www.claude-code.pro)
