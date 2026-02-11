## Browser Automation with playwright-cli

### When to Use playwright-cli

**MANDATORY for E2E testing of any app with a UI (web apps, dashboards, forms).**

| Scenario | Use playwright-cli? |
|----------|-------------------|
| Full-stack app with frontend | **YES** - Test UI renders and workflows complete |
| API-only backend | No - Use curl/httpie |
| CLI tool | No - Use Bash |
| React/Vue/Svelte app | **YES** - Verify components render correctly |
| Admin dashboard | **YES** - Test CRUD operations in UI |
| Auth flows (login/signup) | **YES** - Verify forms and redirects work |

**Why this matters:** API tests verify the backend works. playwright-cli verifies **what the user actually sees**. A working API with broken frontend = broken app.

### Quick start

```bash
playwright-cli open https://example.com   # Open browser and navigate
playwright-cli snapshot                    # Get elements with refs (e1, e2, ...)
playwright-cli click e1                    # Click element by ref
playwright-cli fill e2 "text"             # Fill input by ref
playwright-cli screenshot                  # Take screenshot
playwright-cli close                       # Close browser
```

### Core workflow

1. Open browser: `playwright-cli open <url>`
2. Snapshot: `playwright-cli snapshot` (returns elements with refs like `e1`, `e2`)
3. Interact using refs from the snapshot
4. Re-snapshot after navigation or significant DOM changes

### Commands

#### Navigation
```bash
playwright-cli open <url>             # Open browser and navigate
playwright-cli goto <url>             # Navigate to URL
playwright-cli go-back                # Go back
playwright-cli go-forward             # Go forward
playwright-cli reload                 # Reload page
playwright-cli close                  # Close browser
```

#### Snapshot
```bash
playwright-cli snapshot               # Full accessibility tree with refs
playwright-cli snapshot --filename=f  # Save snapshot to file
```

#### Interactions (use refs from snapshot)
```bash
playwright-cli click e1               # Click
playwright-cli dblclick e1            # Double-click
playwright-cli fill e2 "text"         # Clear and type
playwright-cli type "text"            # Type without clearing
playwright-cli press Enter            # Press key
playwright-cli press Control+a        # Key combination
playwright-cli hover e1               # Hover
playwright-cli check e1               # Check checkbox
playwright-cli uncheck e1             # Uncheck checkbox
playwright-cli select e1 "value"      # Select dropdown
playwright-cli drag e1 e2             # Drag and drop
playwright-cli upload ./file.pdf      # Upload file
```

#### JavaScript evaluation
```bash
playwright-cli eval "document.title"           # Get page title
playwright-cli eval "el => el.textContent" e5  # Get element text
```

#### Dialogs
```bash
playwright-cli dialog-accept           # Accept dialog
playwright-cli dialog-accept "text"    # Accept with prompt text
playwright-cli dialog-dismiss          # Dismiss dialog
```

#### Keyboard
```bash
playwright-cli press Enter             # Press key
playwright-cli press ArrowDown         # Arrow keys
playwright-cli keydown Shift           # Key down
playwright-cli keyup Shift             # Key up
```

#### Mouse
```bash
playwright-cli mousemove 150 300       # Move mouse
playwright-cli mousedown               # Mouse down
playwright-cli mouseup                 # Mouse up
playwright-cli mousewheel 0 100        # Scroll (dx, dy)
```

#### Screenshots & PDF
```bash
playwright-cli screenshot              # Screenshot to stdout
playwright-cli screenshot e5           # Screenshot element
playwright-cli screenshot --filename=p # Save to file
playwright-cli pdf --filename=page.pdf # Save as PDF
```

#### Tabs
```bash
playwright-cli tab-list                # List all tabs
playwright-cli tab-new                 # New tab
playwright-cli tab-new https://url     # New tab with URL
playwright-cli tab-select 0            # Select tab by index
playwright-cli tab-close               # Close current tab
playwright-cli tab-close 2             # Close tab by index
```

#### Storage state
```bash
playwright-cli state-save              # Save cookies + localStorage
playwright-cli state-save auth.json    # Save to specific file
playwright-cli state-load auth.json    # Restore state from file
```

#### Cookies
```bash
playwright-cli cookie-list             # List all cookies
playwright-cli cookie-list --domain=x  # Filter by domain
playwright-cli cookie-get session_id   # Get specific cookie
playwright-cli cookie-set name value   # Set cookie
playwright-cli cookie-set name value --domain=x --httpOnly --secure
playwright-cli cookie-delete name      # Delete cookie
playwright-cli cookie-clear            # Clear all cookies
```

#### LocalStorage / SessionStorage
```bash
playwright-cli localstorage-list       # List all items
playwright-cli localstorage-get key    # Get item
playwright-cli localstorage-set k v    # Set item
playwright-cli localstorage-delete key # Delete item
playwright-cli localstorage-clear      # Clear all

playwright-cli sessionstorage-list     # Same API for sessionStorage
playwright-cli sessionstorage-get key
playwright-cli sessionstorage-set k v
playwright-cli sessionstorage-delete k
playwright-cli sessionstorage-clear
```

#### Network mocking
```bash
playwright-cli route "**/*.jpg" --status=404           # Block requests
playwright-cli route "**/api/**" --body='{"mock":true}' --content-type=application/json
playwright-cli route-list                               # List active routes
playwright-cli unroute "**/*.jpg"                       # Remove route
playwright-cli unroute                                  # Remove all routes
```

#### DevTools
```bash
playwright-cli console                 # View console messages
playwright-cli console warning         # Filter by level
playwright-cli network                 # View network requests
```

#### Tracing & Video
```bash
playwright-cli tracing-start           # Start trace recording
playwright-cli tracing-stop            # Stop and save trace
playwright-cli video-start             # Start video recording
playwright-cli video-stop demo.webm    # Stop and save video
```

#### Run custom Playwright code
```bash
# For anything not covered by CLI commands
playwright-cli run-code "async page => {
  await page.waitForLoadState('networkidle');
}"

# Wait for element
playwright-cli run-code "async page => {
  await page.waitForSelector('.loading', { state: 'hidden' });
}"

# Get page info
playwright-cli run-code "async page => {
  return { title: await page.title(), url: page.url() };
}"
```

#### Browser configuration
```bash
playwright-cli open --browser=chrome   # Specific browser
playwright-cli open --browser=firefox
playwright-cli open --browser=webkit
playwright-cli open --headed           # Show browser window
playwright-cli open --persistent       # Persistent profile
playwright-cli open --config=conf.json # Config file
playwright-cli resize 1920 1080        # Resize window
```

### Browser sessions (parallel browsers)

```bash
playwright-cli -s=auth open https://app.com/login
playwright-cli -s=public open https://example.com
playwright-cli -s=auth fill e1 "user@example.com"
playwright-cli -s=public snapshot
playwright-cli list                    # List all sessions
playwright-cli close-all               # Close all browsers
playwright-cli kill-all                # Force kill all
```

### Example: Form submission

```bash
playwright-cli open https://example.com/form
playwright-cli snapshot
# Output shows: e1 [textbox "Email"], e2 [textbox "Password"], e3 [button "Submit"]

playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot  # Check result
playwright-cli close
```

### Example: Authentication with saved state

```bash
# Login once
playwright-cli open https://app.example.com/login
playwright-cli snapshot
playwright-cli fill e1 "username"
playwright-cli fill e2 "password"
playwright-cli click e3
playwright-cli state-save auth.json

# Later sessions: load saved state
playwright-cli state-load auth.json
playwright-cli open https://app.example.com/dashboard
```

### Example: Debugging with DevTools

```bash
playwright-cli open https://example.com
playwright-cli tracing-start
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli console
playwright-cli network
playwright-cli tracing-stop
playwright-cli close
```

### E2E Testing Pattern

**After implementing a feature with UI, always verify with playwright-cli:**

```bash
# 1. Start the app (if not running)
# npm run dev &

# 2. Open the app
playwright-cli open http://localhost:3000

# 3. Get interactive elements
playwright-cli snapshot

# 4. Test the user workflow
playwright-cli fill e1 "test data"
playwright-cli click e2
playwright-cli run-code "async page => { await page.waitForLoadState('networkidle'); }"

# 5. Verify the result
playwright-cli snapshot  # Check UI updated correctly
playwright-cli eval "el => el.textContent" e3  # Verify text content

# 6. Clean up
playwright-cli close
```

**E2E Test Checklist:**
- [ ] User can complete the main workflow
- [ ] Forms validate and show errors correctly
- [ ] Success states display after operations
- [ ] Navigation works between pages
- [ ] Data persists after refresh (if applicable)
- [ ] Error states render properly
