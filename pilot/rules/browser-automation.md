---
paths:
  - "**/*.{ts,tsx,js,jsx,mjs,cjs,html,css,scss,vue,svelte,astro}"
  - "**/{tests,test,e2e,playwright,cypress,__tests__}/**"
  - "**/playwright.config.*"
  - "**/cypress.config.*"
---

## Browser Automation for E2E Testing

**MANDATORY for E2E testing of any app with a UI.** API tests verify backend; browser automation verifies what the user sees.

### ⛔ Ask the project first — the ladder below is the fallback

**Before taking the 4-tier ladder, check whether the project already says which driver reaches ITS interface.** Grep `.claude/rules/`, `CLAUDE.md` and `AGENTS.md` for the tool it names, and use that.

The ladder is written for a page in a desktop browser. These do not have one, and each has a different driver a project usually has already learned the hard way:

| The UI actually is | The ladder reaches it |
|---|---|
| A mobile WebView (Capacitor, Cordova, React Native WebView) | No — needs the platform's own remote-debug bridge; see `mobile-development.md` |
| A native mobile screen | No — see `mobile-development.md` |
| A native desktop window (Electron main, Swift, GTK, WinUI) | No — needs the platform's UI-automation driver |
| A terminal UI | No |
| A canvas or game surface | Partly — pixels only, no a11y tree |

A project that names a tool has measured something. Taking the generic ladder over it is how a verification pass turns into an afternoon of selectors that never land.

### Tool Selection: 4-Tier Priority

Applies when the project names nothing and the UI is a page in a browser. Pick the tool that gives the most accurate verification for the situation, not the fastest.

| Priority | Tool | Best For | Key Advantage |
|----------|------|----------|---------------|
| 1st | Claude Code Chrome (`mcp__claude-in-chrome__*`) | Quick E2E, visual check | Shares user's existing browser session, natural-language `find` |
| 2nd | Chrome DevTools MCP (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`) | DevTools-level debugging, perf audits | Direct CDP, Lighthouse, tracing — no extension needed |
| 3rd | `playwright-cli` | Thorough E2E, complex flows | Most reliable targeting, persistent sessions, network mocking, tracing, multi-tab |
| 4th | `agent-browser` | Lightweight checks | Concise output (200–400 tk/page), fast startup |

### Override the Default

| Situation | Use |
|-----------|-----|
| Lighthouse / performance trace | Chrome DevTools MCP |
| Network mocking, tracing, video | playwright-cli |
| Multi-tab workflow | playwright-cli |
| Persistent browser profile | playwright-cli (`--persistent`) |
| Auth flow (Clerk, OAuth) | playwright-cli (most reliable) or agent-browser |
| Already logged in, quick visual | Claude Code Chrome |
| Simple click-and-verify | agent-browser |

### Detection

1. **Claude Code Chrome:** `mcp__claude-in-chrome__*` in your tools list.
2. **Chrome DevTools MCP:** `mcp__plugin_chrome-devtools-mcp_chrome-devtools__*` in your tools list.
3. **playwright-cli / agent-browser:** `which playwright-cli` / `which agent-browser` (installed by Pilot Shell).

**Fallback chain:** Claude Code Chrome → Chrome DevTools MCP → playwright-cli → agent-browser.

### ⛔ E2E Hard Rules — read before claiming "verified"

**1. Tier error → next tier in the chain. Period.**
If tier N errors (e.g., Chrome DevTools MCP "no Chrome binary"), the ONLY allowed next step is tier N+1. Never substitute a non-browser tool. If tiers 1–4 all fail, STOP and tell the user — do not claim E2E.

**Forbidden as E2E substitutes** (each only proves what's in parentheses, not user behavior):
`web-fetch` / `fetch_url` / `curl` (SSR HTML ships) · reading source files (code exists) · API 200s (backend works) · typecheck / unit tests (code shape) · "no console errors on load" (page parsed).

**2. E2E = interaction, not load.**
For every user-facing path the change touches, you MUST: snapshot → **click the primary action** (button, link, form submit) → re-snapshot → confirm new state. No click + re-snapshot pair = not E2E.

**3. Three failed interactions with the same driver → the driver is wrong, not the selector.**
Distinct from rule 1, and the more expensive of the two. Rule 1 is a tool that will not START — loud, obvious, one step down the ladder. This is a tool that starts fine and half-works: it attaches, it screenshots, it answers every call, and every interaction fails with something that reads like a fixable typo (*element not found*, *matched the wrong node*, *the tap did nothing*). Nothing announces itself, and each retry is cheap, so the loop can run for an hour.

So count them. After the third consecutive failure, stop and spend one call on the question you skipped: **does this project document a different driver?** Then take it. Do not try a fourth selector, a coordinate tap, or a longer timeout.

Two symptoms that mean you are already in this loop:
- You are converting selectors into coordinates because the selectors will not match.
- A tool sent the app somewhere you did not ask for — the home screen, a native dialog, a different route — and you are working around it rather than reading why.

**4. Self-check before saying "verified" / "works" / "done":**
- [ ] Used the driver the project names, or a tier 1–4 tool when it names none (say which)?
- [ ] Actually clicked the thing the change affects?
- [ ] Re-snapshotted and saw the expected new state?

Any "no" → not verified. Say so explicitly; do not claim done.

### Design-Quality Detector (best-effort, advisory)

After the browser E2E passes, run the `impeccable detect` design anti-pattern detector on the changed UI for a deterministic, no-API-key signal (overused fonts, gray-on-color text, side-tab borders, purple gradients, layout-thrash transitions, and similar AI-generated-design tells). **Best-effort means run-when-available, not discretionary:** when `impeccable` is on PATH and you have a bounded UI target, run it — skip (with a one-line note) only when the binary is absent or no concrete target exists. The **findings** are advisory and non-blocking — suggestions, never a verification failure or a reason to withhold "done".

**Invocation contract (follow exactly — `impeccable detect` is a linter):**

```bash
which impeccable >/dev/null 2>&1 || echo "impeccable not installed — skip design check"
impeccable detect --json <explicit-changed-ui-files-or-rendered-output> || true
```

- **Decide from the JSON, not the exit code.** `impeccable detect` exits `0` when clean and `2` when it finds something — both mean it ran successfully; parse stdout JSON for findings. Treat only a missing binary, a non-0/non-2 exit, or unparseable output as "could not run" → record a one-line skip note and move on.
- **Bound the target.** Pass only the explicit changed UI files, or one narrowly-scoped built-output directory. Never point it at the repo root or cwd (directory mode walks every file and builds an import graph — it can hang). Run it under a timeout; on timeout or oversize, record a skip note rather than waiting.
- **Scan rendered output, not a client-rendered SPA's static shell.** A Vite/React/SPA `index.html` is a near-empty shell — scanning it undercounts badly. For SSG/SSR builds (Docusaurus, Astro, Next static) scan the built HTML directly; for an SPA, scan the rendered DOM you already have from the E2E browser (save the live page's HTML, then `impeccable detect` that file), or record a skip note.
- **Vendored noise:** findings on third-party UI primitives (e.g. a `components/ui/**` shadcn tree) are expected. A project that wants them suppressed can add a `.impeccable/config.json` `detector.ignoreFiles` entry; do not create that config automatically.

### Common Workflow Shape (all tools)

1. Get current state (tab/page/snapshot)
2. Navigate to target URL
3. Snapshot / read elements (gives you refs)
4. Interact (click / fill / press)
5. Re-snapshot to verify

### Session Isolation — MANDATORY in /spec or any parallel workflow

Without session isolation, parallel agents share one browser instance and clobber each other.

```bash
# agent-browser
agent-browser --session "${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}" <command>

# playwright-cli
playwright-cli -s="${PILOT_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-${CODEX_THREAD_ID:-default}}}" <command>
```

Chrome MCP and Chrome DevTools MCP target tabs/pages directly — no session ID needed.

### Tool-Specific Notes

<!-- CC-ONLY -->
- **Claude Code Chrome:** load tools via `ToolSearch(query="select:mcp__claude-in-chrome__<tool>")` first. Avoid triggering `alert/confirm/prompt` — they block the extension. Use `javascript_tool` + `console.log` for debugging.
- **Chrome DevTools MCP:** load via `ToolSearch(query="chrome-devtools-mcp", max_results=30)`. Snapshots use `uid=` refs that go stale after navigation — re-snapshot. Unique: `lighthouse_audit`, `performance_start_trace`, `evaluate_script`, `emulate`, network/console listing.
<!-- /CC-ONLY -->
<!-- CODEX-START
- **Claude Code Chrome:** Not available in Codex — skip to playwright-cli or agent-browser.
- **Chrome DevTools MCP:** If configured as an MCP server in Codex, use `mcp__plugin_chrome-devtools-mcp_chrome-devtools__*` tools directly. Snapshots use `uid=` refs that go stale after navigation — re-snapshot. Unique: `lighthouse_audit`, `performance_start_trace`, `evaluate_script`, `emulate`, network/console listing.
CODEX-END -->
- **agent-browser:** uses `@e1`/`@e2` refs from `snapshot -i`. Refs invalidate after navigation/forms/dynamic loads — re-snapshot. Full command reference: see `agent-browser --help` or the `agent-browser` skill.
- **playwright-cli:** refs are bare numbers (`e1`, not `@e1`). Snapshots saved to files. Unique: `--persistent` profiles, `route` for mocking, `tracing-start/stop`, `video-start/stop`, cookie/localStorage management, `run-code` for raw Playwright. Full reference: `/playwright-cli` skill.

### E2E Checklist

- [ ] User can complete the main workflow
- [ ] Forms validate and show errors correctly
- [ ] Success states display after operations
- [ ] Navigation works between pages
- [ ] Error states render properly
