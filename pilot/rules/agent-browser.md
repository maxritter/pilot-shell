## Browser Automation with agent-browser

**MANDATORY for E2E testing of any app with a UI.** API tests verify backend; agent-browser verifies what the user sees.

### Session Isolation (Parallel Workflows)

**MANDATORY when running inside `/spec` or any parallel workflow.** Without session isolation, parallel agents share the default browser instance and overwrite each other's state (wrong pages, failed snapshots, broken interactions).

**Use `--session $PILOT_SESSION_ID` on ALL `agent-browser` commands:**

```bash
# Resolve session name once at the start of E2E testing
AB_SESSION="${PILOT_SESSION_ID:-default}"

# All subsequent commands use --session
agent-browser --session "$AB_SESSION" open <url>
agent-browser --session "$AB_SESSION" snapshot -i
agent-browser --session "$AB_SESSION" click @e1
agent-browser --session "$AB_SESSION" close       # Always close when done
```

**Why:** Each `/spec` session gets a unique `PILOT_SESSION_ID`. The `--session` flag gives each session its own isolated browser instance, preventing parallel workflows from interfering with each other.

**NEVER use bare `agent-browser` commands (without `--session`) during `/spec` workflows.** This causes cross-session interference that is extremely difficult to debug.

### Core Workflow

```bash
AB_SESSION="${PILOT_SESSION_ID:-default}"
agent-browser --session "$AB_SESSION" open <url>        # 1. Open browser
agent-browser --session "$AB_SESSION" snapshot -i       # 2. Get interactive elements with refs (@e1, @e2, ...)
agent-browser --session "$AB_SESSION" fill @e1 "text"   # 3. Interact using @refs
agent-browser --session "$AB_SESSION" click @e2
agent-browser --session "$AB_SESSION" snapshot -i       # 4. Re-snapshot to verify result
agent-browser --session "$AB_SESSION" close             # 5. Clean up
```

### Command Reference

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

### Parallel Sessions

```bash
agent-browser --session site1 open https://site-a.com
agent-browser --session site2 open https://site-b.com
agent-browser session list
agent-browser close --all
```

**In `/spec` workflows**, the session name is always `$PILOT_SESSION_ID` — never invent custom names. This ensures each parallel spec run is fully isolated.

### Ref Lifecycle

Refs (`@e1`, `@e2`, etc.) are invalidated when the page changes. Always re-snapshot after clicking links/buttons that navigate, form submissions, or dynamic content loading.

### E2E Checklist

- [ ] User can complete the main workflow
- [ ] Forms validate and show errors correctly
- [ ] Success states display after operations
- [ ] Navigation works between pages
- [ ] Error states render properly
