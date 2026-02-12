# Terminal Setup Tips for Claude Code

A well-configured terminal makes Claude Code faster and more pleasant to use. These tips cover line breaks, vim mode, notifications, and settings for popular terminals.

## Multi-Line Input with Shift+Enter

By default, pressing Enter sends your message. For multi-line prompts, you need Shift+Enter — but not all terminals support it out of the box.

### VS Code Terminal

VS Code handles Shift+Enter natively. No configuration needed.

### iTerm2

Add a key mapping in Preferences → Profiles → Keys → Key Mappings:

- Key combination: `Shift+Enter`
- Action: Send text with "vim" special chars
- Value: `\n`

### Ghostty

Add to your Ghostty config:

```
keybind = shift+enter=text:\n
```

### Warp

Warp supports multi-line input natively with Shift+Enter.

## Vim Mode

If you use vim keybindings in your shell, Claude Code respects them. Enable vi mode in your shell:

**Bash:**
```bash
set -o vi
```

**Zsh:**
```zsh
bindkey -v
```

## Desktop Notifications

Get notified when Claude finishes a long task. Claude Code supports system notifications on macOS and Linux. Enable in settings:

```json
{
  "notifications": {
    "enabled": true,
    "sound": true
  }
}
```

## Custom Status Line

Claude Code supports a custom status bar that shows live information. Configure it in settings:

```json
{
  "statusLine": {
    "enabled": true,
    "command": ["python", "-m", "launcher.statusline"]
  }
}
```

Pilot's status line shows: license tier, active plan, context usage percentage, and Claude Code version — all updating in real time.

## Font and Theme

Claude Code output uses Unicode characters for boxes and indicators. Make sure your terminal font supports:

- Box-drawing characters (╭╮╰╯│─)
- Common emoji (✓ ✗ ▸ ⏳)
- ANSI 256-color codes

Nerd Fonts (like FiraCode Nerd Font or JetBrainsMono Nerd Font) work well.

## Recommended Terminal Settings

| Setting | Recommended Value |
|---------|------------------|
| Scrollback | 10,000+ lines |
| Font | Monospace with Unicode support |
| Color scheme | 256-color capable |
| Cursor | Block or beam (not underline) |
| Bell | Disabled (use notifications instead) |
