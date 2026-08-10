---
paths:
  - "**/capacitor.config.*"
  - "**/ionic.config.json"
  - "**/android/app/build.gradle*"
  - "**/android/app/src/main/AndroidManifest.xml"
  - "**/*.xcodeproj/project.pbxproj"
  - "**/*.xcworkspace/contents.xcworkspacedata"
  - "**/Podfile"
  - "**/pubspec.yaml"
  - "**/react-native.config.*"
  - "**/metro.config.*"
  - "**/expo.json"
  - "**/app.config.{js,ts}"
---

## Mobile Development

Loaded only in a repository that actually builds a mobile app — the path list above is the gate, so this costs nothing to anyone else.

### ⛔ This file is the starting point, not the answer

**A project's own rules outrank every line below.** These are platform constants and the traps that catch a first attempt; a repository that has shipped to a store has measured things this file cannot know — its emulator name, its JDK pin, its bundle id, which of two drivers actually reached its UI. Grep `.claude/rules/`, `CLAUDE.md` and `AGENTS.md` before acting on anything here.

The failure this ordering prevents: reading a generic page, feeling informed, and never opening the file where the answer was written down.

### Reaching the UI

**A mobile app's UI is not a page in a desktop browser**, so the 4-tier ladder in `browser-automation.md` does not reach it. That rule says so and sends you here.

| Platform | Read the screen | Drive the app |
|---|---|---|
| Android, WebView (Capacitor / Cordova / RN WebView) | a11y-tree reader (Maestro, UIAutomator) or CDP | **CDP** over `adb forward` — see below |
| Android, native | a11y-tree reader | the same reader, or UIAutomator |
| iOS, WebView | a chii-style bridge, or screenshots | the bridge, else coordinate taps |
| iOS, native | screenshots | coordinate taps (`xcrun simctl`, mobile-mcp) |

⛔ **Reading and driving are usually different tools, and reaching for one to do both is the expensive mistake.** An a11y-tree reader gives you the whole flattened tree — excellent for asserting what is on screen, poor for hitting one specific control, because its text matchers are full-string regexes over that flattened tree and match things you never meant. Where a WebView exposes CSS selectors, drive by selector.

**Android WebView → CDP**, the one bridge worth memorising:

```bash
adb forward tcp:9222 localabstract:$(adb shell 'cat /proc/net/unix' \
  | grep -o 'webview_devtools_remote_[0-9]*' | head -1)
curl -s http://localhost:9222/json/version    # sanity check: expect Android-Package
```

⛔ **The socket name carries the app's PID, so this must be redone after every app launch.** A forward set up before a relaunch points at a dead socket and the tooling reports an empty page list — which reads as "the app has no UI" and is not that.

Debug builds enable the socket by themselves. Release builds do not, and should not — an app that sets `webContentsDebuggingEnabled` unconditionally ships a debugger to its users.

⛔ **iOS has no CDP.** WKWebView speaks a different protocol, and Safari's Web Inspector has no automation surface. Either a chii-style bridge with a **dev-only** script injection, or coordinate taps read back with screenshots. If a project injects such a bridge, check the injection is gated on the dev server *and* an env var — a bridge that ships in a release build is a remote debugger in production.

### Traps that cost a first attempt

- **Reinstalling fails with `INSTALL_FAILED_VERSION_DOWNGRADE`** when the local build's version code is below what is already installed. Android reports it to the user as "App not installed", which reads as a corrupt build. Pass a higher version code, and stay well below whatever offset CI uses for real releases.
- **Wait for the condition, not the clock.** `until [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ]; do sleep 3; done` beats any fixed sleep, and the same holds for a scan or a build finishing inside the app.
- **A driver that dismisses the keyboard may be sending BACK.** With the keyboard already down that unwinds a wizard, and from the first screen it exits the app to the launcher — which looks exactly like a crash.
- **Clearing app state between runs throws away what you just typed.** Convenient for a clean start, expensive in the middle of a flow.
- **Coordinate taps drift** the moment an overlay opens: the same percentage means two different things one call apart. Resolve fresh bounds, or use selectors.

### Design checks on a device

`impeccable detect` and the contract in `browser-automation.md` → *Design-Quality Detector* apply unchanged. Two things are specific here:

- **A mobile app's built `index.html` is an SPA shell** — scanning it undercounts badly. The bridge you set up for driving is also how you get real markup: pull `document.documentElement.outerHTML` through the WebView's CDP session, write it to a file, and point `impeccable detect` at that file.
- **Bound the target to the UI files the change touched.** Never the repo root: a mobile repo carries a whole native tree, and directory mode walks all of it.

**Some things only a device shows, and no detector catches them.** Take a screenshot on a real screen size and look:

- Content under the notch, the status bar, or the home indicator.
- A control the thumb cannot reach, or two controls too close to hit individually.
- Text that fits the design and not the OS font-size setting the user actually chose.
- A dark-theme surface that borrows the host's background because the page never set its own.

### What the desktop frontend rules miss on a phone

`standards-frontend.md` applies in full — including its touch-target floor (44x44 iOS, 48x48 Android) and its contrast requirements. These are the additions:

- **Safe areas.** Use `env(safe-area-inset-*)` for anything at a screen edge, and set `viewport-fit=cover` in the viewport meta — without it those insets are zero and the padding silently does nothing. Recent Android enforces edge-to-edge by target SDK, so the insets are not optional on either platform.
- **`100vh` is wrong on a phone.** It ignores the browser chrome and the on-screen keyboard. Use `100dvh`, and expect the viewport to resize when the keyboard opens.
- **The keyboard covers the bottom of the screen.** A submit button pinned there is unreachable exactly when it is needed; scroll the focused field into view, or keep the action above the fold.
- **The WebView follows the OS theme.** A surface with no explicit background inherits whatever the host paints, so a light-only design can render as unreadable in dark mode. Set background and colour explicitly.
- **Native text scaling is a real range, not a rounding error.** Layouts that only survive the default size break on the size a lot of people actually use.
