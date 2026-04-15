# Changelog

All notable changes to Pilot Shell will be documented in this file.

## [8.1.0] - 2026-04-15

### Features

- Add session details with JSONL stats, cost calculation, and enhanced UI

## [8.0.10] - 2026-04-14

### Bug Fixes

- Codegraph native SQLite repair, /spec new-branch option, session prompt display

## [8.0.9] - 2026-04-13

### Bug Fixes

- Deduplicate plugin extensions across marketplaces and add progressive dashboard loading

## [8.0.8] - 2026-04-13

### Bug Fixes

- Add Chrome DevTools MCP plugin, update browser automation to 4-tier, fix auto-mode flag and docs

### Miscellaneous

- Updated Demo Gif
- Updated Readme

## [8.0.7] - 2026-04-10

### Bug Fixes

- Restore dom globals after terminal-preview-xss test to prevent portal ssr leak
- Stop incomplete child_process mocks poisoning CI test runs
- Add tool output compression + sandboxed content cards to Usage view
- Hook venv sync, console annotation writes, codegraph native sqlite

## [8.0.6] - 2026-04-09

### Bug Fixes

- Walk up directory tree for git repo detection in CodeGraph guard

## [8.0.5] - 2026-04-09

### Bug Fixes

- Skip CodeGraph indexing in non-git directories

### Miscellaneous

- Updated Readme
- Improved Readme

## [8.0.4] - 2026-04-09

### Bug Fixes

- Improved PRD and Spec Sharing / Annotation UI on pilot-shell.com
- Improved Dependency Installation Speed for Installer and Updater

## [8.0.3] - 2026-04-09

### Bug Fixes

- Improved Code Reviewer Stability, Codegraph Usage and Context Mode

### Miscellaneous

- Updated specifications images

## [8.0.2] - 2026-04-09

### Bug Fixes

- Console dashboard overhaul — 2x2 recent cards, usage model breakdown, session filtering, spec tab consistency

## [8.0.1] - 2026-04-08

### Bug Fixes

- Use correct CronCreate parameter name (cron, not schedule) in bot skills

## [8.0.0] - 2026-04-08

### Bug Fixes

- Pin Bun to 1.3.11 (1.2.15 lacks compression APIs, latest is unstable)

### Features

- Add Pilot Bot — persistent automation agent with scheduled tasks, background jobs, and optional Telegram
- Complete Console overhaul — v8.0.0 

## [7.11.4] - 2026-04-07

### Bug Fixes

- Console UI overhaul — dashboard sessions card, sidebar worker status, motion system, skeleton loaders

## [7.11.3] - 2026-04-06

### Bug Fixes

- Replace isomorphic-dompurify with dompurify to fix CI ESM incompatibility
- Whitelist web-search-agent in tool_redirect hook for /prd deep research

### Miscellaneous

- Add Homebrew to Linux Dev Container Setup

## [7.11.2] - 2026-04-02

### Bug Fixes

- Pass chromium argument to playwright-cli install-browser and increase timeout
- Symlink RTK to ~/.pilot/bin/ for PATH availability on Linux

## [7.11.1] - 2026-04-02

### Bug Fixes

- Add playwright-cli as 3-tier browser tool, optimize viewer bundle, improve installer UX

## [7.11.0] - 2026-04-01

### Features

- Rename /shape to /prd, add tiered research, fix Console PRD view, restructure docs

## [7.10.2] - 2026-04-01

### Bug Fixes

- Filter Pilot skills from extensions listing and fix CI test failures
- Migrate commands to skills format

## [7.10.1] - 2026-03-31

### Bug Fixes

- Shorten share URLs ~25% by streamlining encoding pipeline

### Miscellaneous

- Optimize website image performance
- Fix self-referencing SHARE_BASE_URL constant on /shared page

## [7.10.0] - 2026-03-31

### Bug Fixes

- Security audit hardening across console, launcher, and installer
- Improve Codex CLI invocation and reviewer agent prompting 

### Features

- Codex adversarial reviewers, spec sharing, and Console improvements 

## [7.9.0] - 2026-03-30

### Features

- Add E2E encrypted spec sharing with collaborative annotation feedback

## [7.8.5] - 2026-03-30

### Bug Fixes

- Added sudo prompt for npm if needed

## [7.8.4] - 2026-03-30

### Bug Fixes

- Use AskUserQuestion at code review gate so stop guard allows exit

## [7.8.3] - 2026-03-30

### Bug Fixes

- Prefer Claude Code Chrome over agent-browser for browser automation

## [7.8.2] - 2026-03-30

### Bug Fixes

- Agent-browser ARM64 Linux support, dynamic devcontainer naming
- Ensure codegraph is in PATH via ~/.pilot/bin symlink

## [7.8.1] - 2026-03-28

### Bug Fixes

- Replace mock.module with spyOn for logger in timeline-formatting tests
- Enhanced CI debug for logger test — check test file content and single-file run
- Add debug step to release.yml (runs on main, not dev)
- Add debug step to diagnose CI logger.formatTool failure
- Pin Bun version to 1.3.9 in CI workflows
- Skip quality hooks when project has no linter config
- Replace codebase-memory-mcp with CodeGraph across project
- Add Claude CLI flag passthrough and relax /spec permission mode enforcement

### Miscellaneous

- Improved Website Content
- Updated Pricing Section and Readme

## [7.8.0] - 2026-03-27

### Features

- Plan annotations, code review mode, E2E test scenarios in spec workflow 

## [7.7.6] - 2026-03-25

### Bug Fixes

- Replace broken auto-mode probe with retry-on-failure

## [7.7.5] - 2026-03-25

### Bug Fixes

- Safe fallback for --enable-auto-mode on older Claude Code versions

## [7.7.4] - 2026-03-25

### Bug Fixes

- Enable auto mode for team/enterprise/api users

## [7.7.3] - 2026-03-25

### Bug Fixes

- Improve light mode readability and console UI fixes

## [7.7.2] - 2026-03-22

### Bug Fixes

- Add compatibility with Telegram Plugin

### Miscellaneous

- Updated Readme and Website

## [7.7.1] - 2026-03-20

### Bug Fixes

- Add APM format support for team remote extensions, fix category counts, edit modal height, remote content loading, and team gate

### Miscellaneous

- Updated Website and Readme

## [7.7.0] - 2026-03-19

### Features

- Redesign extensions page with color-coded categories, project deletion, and console improvements 

## [7.6.5] - 2026-03-18

### Bug Fixes

- Shorten full model IDs in statusline display
- Use env vars for extended context instead of model name suffix

## [7.6.4] - 2026-03-18

### Bug Fixes

- Optimize rules by converting reference-heavy content to on-demand skills

## [7.6.3] - 2026-03-18

### Bug Fixes

- Add 1M extended context toggle, config migration, and update skillshare extras docs

## [7.6.2] - 2026-03-18

### Bug Fixes

- Improve create-skill with eval testing, description optimization, and writing guidance

## [7.6.1] - 2026-03-18

### Bug Fixes

- Add Remote Control documentation and installer improvements

### Miscellaneous

- Updated Demo Gif with Latest Changes

## [7.6.0] - 2026-03-16

### Features

- Rename /learn to /create-skill and /sync to /setup-rules

## [7.5.11] - 2026-03-16

### Bug Fixes

- Statusline restyle, session reactivation, memory cleanup, context cache preservation

## [7.5.10] - 2026-03-15

### Bug Fixes

- Block plan mode and Explore agent, consolidate hook tests, add /clear instruction

### Miscellaneous

- Updated Demo gifs

## [7.5.9] - 2026-03-15

### Bug Fixes

- Integrate codebase-memory-mcp and sync all documentation

## [7.5.8] - 2026-03-15

### Bug Fixes

- Add RTK CLI installation and standardize dependency UI

## [7.5.7] - 2026-03-14

### Bug Fixes

- Add trivy security scan to pre-commit hook and fix undici CVEs
- Auto-detect context window size from Claude Code statusline

## [7.5.6] - 2026-03-13

### Bug Fixes

- Use IS_SANDBOX=1 instead of permission patching for root support

## [7.5.5] - 2026-03-13

### Bug Fixes

- Support running as root in containers and remove remote fetch/browse UI
- Enable git worktrees and reviewer subagents by default

## [7.5.4] - 2026-03-12

### Bug Fixes

- Clean up memory observer session files from claude -r resume list

## [7.5.3] - 2026-03-12

### Bug Fixes

- Warn instead of block Agent sub-agent calls, allow /spec reviewers silently

## [7.5.2] - 2026-03-12

### Bug Fixes

- Prevent Vercel auto-deploy from overwriting git-crypt CI/CD deployments

## [7.5.1] - 2026-03-12

### Bug Fixes

- Share page detection, sync/collect buttons, skillshare via brew, README cleanup

## [7.5.0] - 2026-03-12

### Features

- Replace Teams with Skillshare-based Share system, streamline spec workflow and hooks 

## [7.4.7] - 2026-03-10

### Bug Fixes

- Improvements for learn and sync commands

## [7.4.6] - 2026-03-10

### Bug Fixes

- Add spec workflow toggles, console settings UI, dark theme, and site redesign

## [7.4.5] - 2026-03-09

### Bug Fixes

- Added settings toggle for subagents and improve their token usage

## [7.4.4] - 2026-03-09

### Bug Fixes

- Optimized runtime of Plan and Spec Reviewer subagents

## [7.4.3] - 2026-03-09

### Bug Fixes

- Enhance Changes tab with git operations, AI commit messages, and model routing

## [7.4.2] - 2026-03-09

### Bug Fixes

- Quality Improvements to Agents, Rules and Spec-Commands

## [7.4.1] - 2026-03-09

### Bug Fixes

- Improve /sync with quality audit phase, consistent structure, and optional dependencies
- Auto-Install Native Claude Code if not already installed on system

## [7.4.0] - 2026-03-08

### Features

- Add Changes view with git diff viewer to Console

## [7.3.2] - 2026-03-08

### Bug Fixes

- Improved /sync Command

## [7.3.1] - 2026-03-08

### Bug Fixes

- Usage summary dashboard showing wrong costs and add token counts

## [7.3.0] - 2026-03-08

### Features

- Replace Vexor with Probe for code search 

## [7.2.2] - 2026-03-06

### Bug Fixes

- Re-Enabled auto-updater for Claude Code in Settings

## [7.2.1] - 2026-03-06

### Bug Fixes

- Redesign bugfix /spec flow with root cause investigation and make reviewers mandatory

### Miscellaneous

- Improve install section after-install guidance
- Streamline landing page sections and remove Under the Hood

## [7.2.0] - 2026-03-05

### Features

- New Teams asset sharing dashboard for skills, rules, commands and agents 

## [7.1.5] - 2026-03-05

### Bug Fixes

- Make hooks read-only, stop blocking plan mode, silence hook errors, optimize git statusline

## [7.1.4] - 2026-03-05

### Bug Fixes

- Clean stale session state on /clear and prevent reviewer skip at high context

## [7.1.3] - 2026-03-02

### Bug Fixes

- Add hash redirect so console dashboard loads without explicit /#/ fragment

## [7.1.2] - 2026-03-02

### Bug Fixes

- Strengthen spec stop guard to prevent premature stops during /spec

## [7.1.1] - 2026-03-02

### Bug Fixes

- Prevent worker from stopping when another session is still active
- Optimize commands and rules for 52% token reduction without quality loss

## [7.1.0] - 2026-03-01

### Features

- Merge 5 spec sub-agents into 2 unified agents for optimized token usage

### Miscellaneous

- Add team rollout section with contact links to README

## [7.0.6] - 2026-02-26

### Bug Fixes

- Update vault workflow for sx 0.11.1+ and improve site/installer/console

## [7.0.5] - 2026-02-26

### Bug Fixes

- Remove aggressive comment stripping from quality hooks and preserve user permission settings
- Mock all subprocess-calling functions in unit tests

## [7.0.4] - 2026-02-25

### Bug Fixes

- Right-size bugfix spec workflow and improve site/installer/console

### Miscellaneous

- Add positioning statement to hero section

## [7.0.3] - 2026-02-25

### Bug Fixes

- Add bugfix verify phase, Linux Homebrew fallback, and site/console improvements

### Miscellaneous

- Restructure docs page TOC into grouped categories and trim verbose sections
- Trim site sections, reorder layout, and add compatibility FAQ
- Streamline README structure and reduce visual clutter

## [7.0.2] - 2026-02-24

### Bug Fixes

- Vexor test mocking, site responsiveness, and README consolidation
- Add vexor runtime check to installer and update dependencies

### Miscellaneous

- Update logo images and fix footer tagline wrapping

## [7.0.1] - 2026-02-24

### Bug Fixes

- Update version to 7.0.0 in console and plugin packages

## [7.0.0] - 2026-02-24

### Features

- Rename Claude Pilot to Pilot Shell

## [6.11.0] - 2026-02-24

### Features

- Add bugfix spec workflow and viewer enhancements 

## [6.10.3] - 2026-02-23

### Bug Fixes

- Enhance rules, agents, and workflow prompts for better review handling and debugging

## [6.10.1] - 2026-02-22

### Bug Fixes

- Minimize external data to license key and fingerprint only
- Simplify Vercel rewrite rule to fix SPA routing 404s

### Miscellaneous

- Improve mobile responsiveness for hero buttons, pricing cards, and workflow diagram
- Add Vercel ignored build step to skip redundant deployments
- Replace hero Get Started button with View on GitHub and Read Documentation

## [6.10.0] - 2026-02-22

### Features

- Add goal verification sub-agent, documentation pages, and installer fixes

## [6.9.4] - 2026-02-21

### Bug Fixes

- Trigger release for AlmaLinux git prerequisite fix
- Install git via system package manager before Homebrew on RHEL-based distros
- Add uninstall script for clean Pilot removal

### Miscellaneous

- Updated Demo Video Link
- Updated Readme
- Added Demo to Readme and Website

## [6.9.3] - 2026-02-20

### Bug Fixes

- Detect native Windows in install.sh and guide users to WSL2 or Dev Container

## [6.9.2] - 2026-02-20

### Bug Fixes

- Improve vault command with correct client IDs and disable non-Claude clients
- Migrate from deprecated mcp-cli to ToolSearch for MCP tool access

## [6.9.1] - 2026-02-20

### Bug Fixes

- Make vexor model pre-download best-effort during installation
- Use sys.executable instead of uv in spec_validators tests
- Consolidate test infrastructure, harden parallel spec workflows 

## [6.9.0] - 2026-02-19

### Bug Fixes

- Grant prepare-release job write permission for semantic-release dry-run
- Remove Dependabot configuration
- Resolve Trivy security scan findings and add pre-commit hook
- Improved MCP-CLI system as CC default

### Features

- Implement spec/release-security-hardening

## [6.8.3] - 2026-02-19

### Bug Fixes

- Create ~/.pilot/bin directory before writing mcp-cli script
- Remove mcp-cli dependency, refactor console infrastructure, and add real-time notifications
- Real-time notification system with SSE and auto-notify on plan transitions

## [6.8.2] - 2026-02-18

### Bug Fixes

- Global extended context toggle, compact settings UI, and hook improvements 

## [6.8.1] - 2026-02-18

### Bug Fixes

- Go/gopls auto-install, npx zod peer dep fix, and update prompt TTY handling

## [6.8.0] - 2026-02-18

### Features

- Model selection settings, Apple Silicon Vexor acceleration, and worktree sync fixes 

## [6.7.7] - 2026-02-17

### Bug Fixes

- Improve network connectivity for corporate proxy and firewall environments

## [6.7.6] - 2026-02-17

### Bug Fixes

- Improve ChromaDB reliability and harden worktree lifecycle

### Miscellaneous

- Update bug report section in README

## [6.7.5] - 2026-02-17

### Bug Fixes

- Harden worktree lifecycle against data loss and improve project config

## [6.7.4] - 2026-02-17

### Bug Fixes

- Use --autostash on rebase during worktree sync
- Prevent stash data loss during worktree sync

## [6.7.3] - 2026-02-17

### Bug Fixes

- Improve worktree isolation and multi-session reliability

### Miscellaneous

- Updated Installer Instructions for Local Mode

## [6.7.2] - 2026-02-17

### Bug Fixes

- Add retry logic to installer network operations

### Miscellaneous

- Updated Demo Gif

## [6.7.1] - 2026-02-17

### Bug Fixes

- Move settings to global ~/.claude/settings.json with SSL and platform fixes

## [6.7.0] - 2026-02-16

### Features

- Effective context display, non-destructive installer, and npm sudo handling

## [6.6.0] - 2026-02-16

### Features

- Compaction-based context preservation, branding overhaul, and bugfixes 

## [6.5.9] - 2026-02-15

### Bug Fixes

- Prevent installer hang on Homebrew installation and improve UX

### Miscellaneous

- Re-stage worktree files with correct filters

## [6.5.8] - 2026-02-15

### Bug Fixes

- Remove unreliable session ID cross-check in context monitor
- Use runtime container detection in installer, improve UX and polling

## [6.5.7] - 2026-02-14

### Bug Fixes

- Use uv tool install for vexor to work on macOS and dev containers

## [6.5.6] - 2026-02-14

### Bug Fixes

- Clarify existing project support, streamline installer UX

## [6.5.5] - 2026-02-14

### Bug Fixes

- Consolidate Search into Memories, add Vault view, remove custom modes, improve hooks

## [6.5.4] - 2026-02-14

### Bug Fixes

- Stop deleting native Claude Code binary, fix spec UI staleness, improve TDD enforcer

## [6.5.3] - 2026-02-13

### Bug Fixes

- Add pre-commit hook for console build artifacts and rebuild bundles

## [6.5.2] - 2026-02-13

### Bug Fixes

- Add .cursor/ to .gitignore and update vault docs
- Improve vault workflow and usage tab performance

## [6.5.1] - 2026-02-13

### Bug Fixes

- Clean up orphaned pending messages to prevent unbounded queue growth

## [6.5.0] - 2026-02-13

### Features

- Add Usage tab with cost/token tracking

## [6.4.5] - 2026-02-12

### Bug Fixes

- Allow background Bash tasks for long-running processes like dev servers
- Install Playwright system dependencies after browser download
- Optimize subagent models and reduce token waste in review agents
- Run plan verification agents in parallel with run_in_background
- Fix npx MCP server pre-caching leaving incomplete installations

### Miscellaneous

- Update website and README messaging and FAQ transparency

## [6.4.4] - 2026-02-12

### Bug Fixes

- Fix npx package cache detection for versioned packages like open-websearch@latest
- Pre-cache npx MCP servers during install and reorder post-install steps

## [6.4.3] - 2026-02-12

### Bug Fixes

- Improve installer reliability, console UX, and vault auth flow

## [6.4.2] - 2026-02-12

### Bug Fixes

- Add cryptography dependency to pilot wrapper for trial activation

## [6.4.1] - 2026-02-12

### Bug Fixes

- Improve License Activation during Trial

### Miscellaneous

- Restore STANDARDS in agent roster, remove from hero, add sessions command to docs
- Remove STANDARDS from hero section, consolidate footer links, restore lightweight website deploy

## [6.4.0] - 2026-02-12

### Bug Fixes

- Consolidate website deployment into release pipelines and fix changelog duplication
- Prevent changelog duplication from squash merge commits

### Features

- Parallel multi-agent verification, standards migration, blog & dashboard

### Miscellaneous

- Updated Readme header

## [6.3.3] - 2026-02-11

### Bug Fixes

- Auto-start trial when no license found instead of prompting for key

### Miscellaneous

- Updated changelog for 6.3.2

## [6.3.2] - 2026-02-11

### Bug Fixes

- Various improvements to quality in spec workflow, rules and hooks
- Fix for trial endpoint so users can reactivate if license file gots corrupted
- Correct seat display for solo/team licenses and enrich activation output
- Replace seats with activations, refactor hooks and spec workflow
- Prevent incremental review from overwriting initial PR analysis

### Miscellaneous

- Add model routing docs and Pilot CLI reference to README and website

## [6.3.1] - 2026-02-11

### Bug Fixes

- Fixing Stale Context Monitor on session restart and statusline
- Update spec implementation agent to produce better quality
- Replace raw Python worktree calls with pilot CLI commands in spec instructions

### Miscellaneous

- Fix team checkout seat selection and update changelog

## [6.3.0] - 2026-02-11

### Bug Fixes

- Updated models for commands and agents
- Add MCP server smoke-testing step to sync command
- Resolve console test failures from parallel execution and mock contamination
- Show server-side license dates and seat count in banner
- Promote parallel execution as primary implement strategy and add license display
- Resolve trial activation failures caused by www subdomain redirects
- Sandbox support improvements and UX polish
- Move worktree question to beginning of spec flow
- Add staleness check to context-pct.json cache
- Migrate licensing from Gumroad to Polar.sh
- Simplify dashboard layout and add delta-aware PR reviews
- Make worktree isolation optional and fix worker startup crash
- Remove working-directory from deploy step to prevent doubled path
- Remove dead code and simplify auth module
- Migrate service integrations and enrich system metadata
- Simplify Vercel deploy to single step (fixes spawn sh ENOENT)
- Add npm install to deploy workflow and handle init timeout rejection
- Migrate to playwright-cli, backport console stability fixes, and harden CI/CD

### Features

- Add parallel execution, goal verification, and workflow improvements
- Add git worktree isolation for /spec workflow

## [6.2.2] - 2026-02-08

### Bug Fixes

- Resolve signal handler deadlock and improve session cleanup

### Miscellaneous

- Small changes to Website and Readme

## [6.2.1] - 2026-02-07

### Bug Fixes

- Move project selector to sidebar and add clear scope indicators across all views
- Restore emojis and add missing launcher features to docs

### Documentation

- Transform website and README with comprehensive system documentation

### Miscellaneous

- Add /vault and /learn to install section, remove remaining count, add custom LSP note
- Remove hardcoded counts and improve quality-focused messaging
- Add /vault to installer post-install and statusline tips, remove language servers stat
- Update branding to new slogan across entire codebase
- Restructure README and website to eliminate duplicate content
- Convert favicon from JPG to PNG for browser compatibility
- Reorder README sections
- Simplify license section in README
- Add license and changelog links to README and website footer
- Update license support contact and remove version line

## [6.2.0] - 2026-02-06

### Bug Fixes

- Resolve continuation path bug, clean up console UI, and add Vexor search backend
- Remove remote mode, extract worker daemon, add offline grace period, and refine hooks/UI
- Address PR #45 review findings and refine console UI
- Clean stale npm temp dirs before Claude Code install and block Explore agent
- Split spec command into phases, add design skill, and optimize skill descriptions
- Remove dead code, unused imports, and legacy integrations

### Features

- Add multi-session parallel support with isolated session state

### Miscellaneous

- Update site tagline
- Update site meta tags

## [6.1.1] - 2026-02-05

### Bug Fixes

- Add console branding and update settings defaults

### Miscellaneous

- Add pricing to website

## [6.1.0] - 2026-02-05

### Bug Fixes

- Rebuild console assets with latest changes
- Address code review findings
- Stale session cleanup, context hook, install docs, and CI pipeline
- Continue reworking towards Pilot Shell Console

### Features

- Pilot Console improvements and enhanced development workflow
- Rebrand memory system to Pilot Console

### Miscellaneous

- Fix changelog generation to prepend-only, restore clean v6 changelog

## [6.0.13] - 2026-02-04

### Bug Fixes

- Prevent blocking on worker restart and shutdown

## [6.0.12] - 2026-02-04

### Bug Fixes

- Show combined changelog for all versions during update
- Remove aggressive process cleanup on startup

## [6.0.11] - 2026-02-04

### Bug Fixes

- Improve hook performance and memory viewer facts display

### Documentation

- Updated Demo Gif

## [6.0.10] - 2026-02-04

### Bug Fixes

- Remove Settings tab from UI, update messaging, improve installer description

## [6.0.9] - 2026-02-03

### Bug Fixes

- Release pipeline now updates files for manual triggers
- Parallel downloads, box alignment, TypeScript errors, remove analytics

## [6.0.8] - 2026-02-03

### Bug Fixes

- Add memory system source from other repo
- Added grep-mcp server

## [6.0.7] - 2026-02-03

### Bug Fixes

- Move worker lifecycle to hooks, simplify launcher cleanup

## [6.0.6] - 2026-02-02

### Bug Fixes

- Improved Plan and Spec Verifier Flow

## [6.0.5] - 2026-02-02

### Bug Fixes

- Add demo gif to README
- Make sx vault setup mandatory when sx installed but not configured

## [6.0.4] - 2026-02-02

### Bug Fixes

- Reduce GitHub API calls and simplify installer cleanup

## [6.0.3] - 2026-02-02

### Bug Fixes

- Shorten banner tagline to fit within box width
- Remove claude alias and update branding to Production-Grade Development

## [6.0.2] - 2026-02-02

### Bug Fixes

- Preserve user's .claude/skills folder and clean up empty rules/custom

## [6.0.1] - 2026-02-02

### Bug Fixes

- Remove duplicate sync step in release workflow
- Resolve release pipeline failure and remove codepro fallbacks
- Emphasize running installer in project folder and remove git setup step
- Add backwards compatibility for --restart-ccp argument

### Documentation

- Simplify install command for easier copying

## [6.0.0] - 2026-02-02

### BREAKING CHANGES

- Major workflow changes for Pilot Shell v6.0
- Project renamed from Claude CodePro to Pilot Shell

### Features

- Add multi-pass plan verification and installer auto-version
- Renamed Project to Pilot Shell

### Bug Fixes

- Update documentation to use claude command instead of pilot alias
- Improve installer location and sync workflow
- Make SEO descriptions consistent with new messaging
- Update favicon to local file and fix remaining old messaging in index.html
- Address PR review findings for installer robustness
- Unquote multi-argument variables in install.sh
- Add multi-pass verification with spec-verifier agent
- Add sx tool and update rules paths
- Improve worker cleanup and installer reliability
