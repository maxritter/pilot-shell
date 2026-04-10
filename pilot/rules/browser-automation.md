## Browser Automation for E2E Testing

**MANDATORY for E2E testing of any app with a UI.** API tests verify backend; browser automation verifies what the user sees.

### Tool Selection: 3-Tier Priority

Each tool has a distinct strength. **Quality and reliability are the priority** — use the tool that gives the most accurate verification for the situation.

| Priority | Tool | Best For | Key Advantage |
|----------|------|----------|---------------|
| **1st** | Claude Code Chrome | Quick E2E, visual verification | Shares existing browser session, natural language `find` |
| **2nd** | playwright-cli | Thorough E2E, complex workflows | Most reliable element targeting, persistent sessions, network mocking, tracing, multi-tab |
| **3rd** | agent-browser | Lightweight checks, simple interactions | Concise output, fast startup |

### When to Override Priority

| Situation | Use Instead |
|-----------|-------------|
| Need network mocking, tracing, or video | playwright-cli |
| Multi-tab workflow | playwright-cli |
| Need persistent browser profile | playwright-cli (`--persistent`) |
| Auth flow testing (Clerk, OAuth) | playwright-cli (most reliable) or agent-browser |
| Already logged in, quick visual check | Claude Code Chrome |
| Simple click-and-verify | agent-browser (lightweight) |

### Detection

1. **Claude Code Chrome:** Check your available/deferred tools list for `mcp__claude-in-chrome__*` entries.
2. **agent-browser:** `which agent-browser` (installed by Pilot Shell).
3. **playwright-cli:** `which playwright-cli` (installed by Pilot Shell).

**Fallback warning (output when neither Chrome nor agent-browser is available):**

```
⚠️ Neither Claude Code Chrome nor agent-browser is available.
Install the Claude Chrome extension or run the Pilot Shell installer.
Falling back to playwright-cli.
```

---

### Claude Code Chrome (Preferred)

Load tools via `ToolSearch(query="select:mcp__claude-in-chrome__<tool_name>")` before first use.

**Core workflow:**

1. `tabs_context_mcp()` — Get current browser state (always call first)
2. `tabs_create_mcp(url=...)` — Open new tab with URL
3. `read_page()` — Read page content and interactive elements
4. `form_input(...)` / `computer(...)` — Interact with elements
5. `read_page()` — Re-read to verify result

**Key tool mapping:**

| Need | Chrome Tool |
|------|------------|
| Navigate | `navigate` or `tabs_create_mcp` |
| Read page / find elements | `read_page` |
| Click / type / scroll | `computer` |
| Fill forms | `form_input` |
| Find element by text | `find` |
| Get full page text | `get_page_text` |
| Execute JavaScript | `javascript_tool` |
| Read console output | `read_console_messages` |
| Record interaction GIF | `gif_creator` |

**No session isolation needed** — Chrome tools operate on the user's actual browser instance. Each tool call targets a specific tab.

**Important:** Avoid triggering JavaScript alerts/confirms/prompts — these block the extension. Use `javascript_tool` with `console.log` for debugging instead.

---

### agent-browser (Lightweight Fallback)

**Best for simple interactions and quick checks.** Concise output (200-400 tokens/page), fast startup.

#### Session Isolation (Parallel Workflows)

**MANDATORY when running inside `/spec` or any parallel workflow.** Without session isolation, parallel agents share the default browser instance and overwrite each other's state.

**Use `--session $PILOT_SESSION_ID` on ALL `agent-browser` commands:**

```bash
AB_SESSION="${PILOT_SESSION_ID:-default}"

agent-browser --session "$AB_SESSION" open <url>
agent-browser --session "$AB_SESSION" snapshot -i
agent-browser --session "$AB_SESSION" click @e1
agent-browser --session "$AB_SESSION" close
```

#### Core Workflow

```bash
AB_SESSION="${PILOT_SESSION_ID:-default}"
agent-browser --session "$AB_SESSION" open <url>        # 1. Open browser
agent-browser --session "$AB_SESSION" snapshot -i       # 2. Interactive elements only
agent-browser --session "$AB_SESSION" fill @e1 "text"   # 3. Interact using @refs
agent-browser --session "$AB_SESSION" click @e2
agent-browser --session "$AB_SESSION" snapshot -i       # 4. Re-snapshot to verify
agent-browser --session "$AB_SESSION" close             # 5. Clean up
```

#### Command Reference

**Navigation:** `open <url>`, `goto <url>`, `close`, `close --all`

**Snapshot:** `snapshot -i` (interactive elements — always use `-i`), `snapshot -s "#selector"` (scoped)

**Interactions (use @refs from snapshot):**

| Command | Example |
|---------|---------|
| Click | `click @e1`, `click @e1 --new-tab` |
| Text input | `fill @e2 "text"` (clear+type), `type @e2 "text"` (append) |
| Keys | `press Enter`, `press Control+a` |
| Forms | `check @e1`, `select @e1 "value"` |
| Scroll | `scroll down 500`, `scroll down 500 --selector "div.content"` |
| Other | `hover @e1`, `find text "Sign In" click` |

**Get info:** `get text @e1`, `get url`, `get title`

**Wait:** `wait @e1`, `wait --load networkidle`, `wait --url "**/page"`, `wait --text "Welcome"`, `wait 2000`

**Screenshots:** `screenshot`, `screenshot --full`, `screenshot --annotate`, `screenshot file.png`, `pdf output.pdf`

**JavaScript:** `eval 'document.title'`, `eval --stdin <<'EOF'` (complex JS)

**Dialogs:** `dialog accept`, `dialog dismiss`, `dialog status`

**Network:** `network requests`, `network route "**/api/*" --abort`

**Diff:** `diff snapshot` (compare vs last snapshot), `diff screenshot --baseline before.png`

**Viewport:** `set viewport 1920 1080`, `set device "iPhone 14"`

**Browser config:** `--headed`, `--color-scheme dark`, `--auto-connect` (attach to user's Chrome)

#### Ref Lifecycle

Refs (`@e1`, `@e2`, etc.) are invalidated when the page changes. Always re-snapshot after clicking links/buttons that navigate, form submissions, or dynamic content loading.

---

### playwright-cli (Complex Automation)

**Use when you need:** persistent browser sessions, network mocking/interception, tracing, video recording, multi-tab workflows, or storage management (cookies, localStorage).

See the `playwright-cli` skill (`/playwright-cli`) for the full command reference.

#### Core Workflow

```bash
playwright-cli open <url>          # 1. Open browser
playwright-cli snapshot            # 2. Get accessibility tree with refs
playwright-cli fill e1 "text"      # 3. Interact using refs (bare, no @)
playwright-cli click e2
playwright-cli snapshot            # 4. Re-snapshot to verify
playwright-cli close               # 5. Clean up
```

**Key differences from agent-browser:** Refs are bare numbers (`e1` not `@e1`). Snapshots are saved to files. Use `--persistent` for sessions that survive restarts.

#### Session Isolation

```bash
playwright-cli -s=$PILOT_SESSION_ID open <url>
playwright-cli -s=$PILOT_SESSION_ID click e1
playwright-cli -s=$PILOT_SESSION_ID close
```

#### Unique Capabilities (not in agent-browser)

| Capability | Command |
|-----------|---------|
| Persistent profile | `open --persistent` or `open --profile=/path` |
| Network mocking | `route "**/*.jpg" --status=404` |
| Tracing | `tracing-start` / `tracing-stop` |
| Video recording | `video-start` / `video-stop output.webm` |
| Cookie management | `cookie-list`, `cookie-set`, `cookie-clear` |
| localStorage | `localstorage-get key`, `localstorage-set key val` |
| Run Playwright code | `run-code "async page => ..."` |
| Console/Network logs | `console`, `network` |

---

### E2E Checklist

- [ ] User can complete the main workflow
- [ ] Forms validate and show errors correctly
- [ ] Success states display after operations
- [ ] Navigation works between pages
- [ ] Error states render properly
