## Browser Automation with playwright-cli

**MANDATORY for E2E testing of any app with a UI.** API tests verify backend; playwright-cli verifies what the user sees.

### Session Isolation (Parallel Workflows)

**⛔ MANDATORY when running inside `/spec` or any parallel workflow.** Without session isolation, parallel agents share the default browser instance and overwrite each other's state (wrong pages, failed snapshots, broken interactions).

**Use `-s=$PILOT_SESSION_ID` on ALL `playwright-cli` commands:**

```bash
# Resolve session name once at the start of E2E testing
PW_SESSION="${PILOT_SESSION_ID:-default}"

# All subsequent commands use -s=
playwright-cli -s="$PW_SESSION" open <url>
playwright-cli -s="$PW_SESSION" snapshot
playwright-cli -s="$PW_SESSION" click e1
playwright-cli -s="$PW_SESSION" close       # Always close when done
```

**Why:** Each `/spec` session gets a unique `PILOT_SESSION_ID`. The `-s=` flag gives each session its own isolated browser instance, preventing parallel workflows from interfering with each other.

**⛔ NEVER use bare `playwright-cli` commands (without `-s=`) during `/spec` workflows.** This causes cross-session interference that is extremely difficult to debug.

### Core Workflow

```bash
PW_SESSION="${PILOT_SESSION_ID:-default}"
playwright-cli -s="$PW_SESSION" open <url>        # 1. Open browser
playwright-cli -s="$PW_SESSION" snapshot          # 2. Get elements with refs (e1, e2, ...)
playwright-cli -s="$PW_SESSION" fill e1 "text"    # 3. Interact using refs
playwright-cli -s="$PW_SESSION" click e2
playwright-cli -s="$PW_SESSION" snapshot          # 4. Re-snapshot to verify result
playwright-cli -s="$PW_SESSION" close             # 5. Clean up
```

### Command Reference

**Navigation:** `open <url>`, `goto <url>`, `go-back`, `go-forward`, `reload`, `close`

**Interactions (use refs from snapshot):**

| Command | Example |
|---------|---------|
| Click | `click e1`, `dblclick e1` |
| Text input | `fill e2 "text"` (clear+type), `type "text"` (append) |
| Keys | `press Enter`, `press Control+a` |
| Forms | `check e1`, `uncheck e1`, `select e1 "value"` |
| Other | `hover e1`, `drag e1 e2`, `upload ./file.pdf` |

**JavaScript:** `eval "document.title"`, `eval "el => el.textContent" e5`

**Screenshots:** `screenshot`, `screenshot e5`, `screenshot --filename=p`, `pdf --filename=page.pdf`

**Dialogs:** `dialog-accept`, `dialog-accept "text"`, `dialog-dismiss`

**Tabs:** `tab-list`, `tab-new [url]`, `tab-select 0`, `tab-close [index]`

**State:** `state-save [file]`, `state-load file` — persist cookies + localStorage across sessions

**Storage:** `cookie-list`, `cookie-get name`, `cookie-set name value`, `cookie-delete name`, `cookie-clear`. Same API for `localstorage-*` and `sessionstorage-*` (`list`, `get`, `set`, `delete`, `clear`).

**Network mocking:** `route "**/*.jpg" --status=404`, `route "**/api/**" --body='{"mock":true}'`, `route-list`, `unroute [pattern]`

**DevTools:** `console [level]`, `network`

**Tracing/Video:** `tracing-start`, `tracing-stop`, `video-start`, `video-stop demo.webm`

**Mouse:** `mousemove x y`, `mousedown`, `mouseup`, `mousewheel dx dy`

**Custom code:** `run-code "async page => { await page.waitForLoadState('networkidle'); }"`

**Browser config:** `open --browser=chrome|firefox|webkit`, `open --headed`, `open --persistent`, `resize 1920 1080`

### Parallel Sessions

```bash
playwright-cli -s=auth open https://app.com/login
playwright-cli -s=public open https://example.com
playwright-cli list          # List sessions
playwright-cli close-all     # Close all
```

**In `/spec` workflows**, the session name is always `$PILOT_SESSION_ID` — never invent custom names. This ensures each parallel spec run is fully isolated.

### E2E Checklist

- [ ] User can complete the main workflow
- [ ] Forms validate and show errors correctly
- [ ] Success states display after operations
- [ ] Navigation works between pages
- [ ] Error states render properly
