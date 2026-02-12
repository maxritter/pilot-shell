---
slug: "keybindings-guide"
title: "Claude Code Keybindings: Complete Keyboard Shortcuts Guide"
description: "Configure custom keyboard shortcuts in Claude Code. Reference for all 17 contexts, keystroke syntax, and keybindings.json examples."
date: "2026-02-03"
author: "Max Ritter"
tags: [Guide, Tools]
readingTime: 14
keywords: "claude, code, complete, guide, keybindings, keyboard, shortcuts"
---

# Claude Code Keybindings: Customize Every Keyboard Shortcut

Configure custom keyboard shortcuts in Claude Code. Reference for all 17 contexts, keystroke syntax, and keybindings.json examples.

Your muscle memory says `Ctrl+K` should open a command palette. Claude Code disagrees. Every time you reach for a familiar shortcut and get the wrong action, you lose focus and break your flow.

This friction compounds. Developers who spend hours in Claude Code sessions build unconscious habits around keyboard shortcuts. When the defaults don't match your mental model, you're fighting the tool instead of using it. If you've come from VS Code, Vim, Emacs, or any terminal-heavy workflow, you already have years of shortcut patterns wired into your fingers. Forcing yourself to learn new ones is a waste of cognitive effort.

Claude Code solves this with a fully customizable keybinding system. You define every shortcut in a single JSON file, organized by context, with support for chord sequences, modifier combinations, and the ability to unbind any default. Changes apply instantly without restarting. Here's how to set it up and make Claude Code feel like an extension of your existing workflow.

## [Getting Started with Custom Keybindings](#getting-started-with-custom-keybindings)

Run the `/keybindings` slash command inside Claude Code. This creates (or opens) your configuration file at `~/.claude/keybindings.json`. If you're new to [configuring Claude Code](/blog/guide/configuration-basics), this file sits alongside your other settings in the `~/.claude/` directory.

The file structure is straightforward:

```p-4
{
  "$schema": "https://platform.claude.com/docs/schemas/claude-code/keybindings.json",
  "$docs": "https://code.claude.com/docs/en/keybindings",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor",
        "ctrl+u": null
      }
    }
  ]
}
```

Three top-level fields control everything:

- **`$schema`** - Optional. Point this at Claude's JSON Schema URL and your editor gives you autocompletion and validation for free. Worth adding.
- **`$docs`** - Optional. Documentation URL for quick reference.
- **`bindings`** - The array where all your custom shortcuts live. Each entry targets a specific context.

The `$schema` field alone makes configuration significantly easier. If you use VS Code or any editor with JSON Schema support, you get inline suggestions for every valid action and context name.

Changes to `keybindings.json` are detected and applied automatically. No restart needed. Edit, save, and your new shortcuts are live immediately.

## [Understanding Contexts](#understanding-contexts)

Every binding belongs to a **context**, which tells Claude Code when that shortcut is active. A shortcut bound in the `Chat` context only fires when you're typing in the main chat input. The same key combination can do different things in different contexts.

Claude Code has 17 contexts:

| Context | When It's Active |
| --- | --- |
| `Global` | Everywhere in the app |
| `Chat` | Main chat input area |
| `Autocomplete` | Autocomplete menu is open |
| `Settings` | Settings menu is open |
| `Confirmation` | Permission and confirmation dialogs |
| `Tabs` | Tab navigation components |
| `Help` | Help menu is visible |
| `Transcript` | Transcript viewer |
| `HistorySearch` | History search mode (Ctrl+R) |
| `Task` | Background task is running |
| `ThemePicker` | Theme picker dialog |
| `Attachments` | Image/attachment bar navigation |
| `Footer` | Footer indicator navigation |
| `MessageSelector` | Rewind dialog message selection |
| `DiffDialog` | Diff viewer navigation |
| `ModelPicker` | Model picker effort level |
| `Select` | Generic select/list components |
| `Plugin` | Plugin dialog (browse, discover, manage) |

The `Global` context is special. Bindings here apply everywhere, regardless of what dialog or view is active. Use it sparingly. If you bind `Ctrl+K` globally, it fires whether you're in chat, browsing autocomplete suggestions, or reviewing diffs.

## [Complete Action Reference](#complete-action-reference)

Actions follow a `namespace:action` naming format. Here's every action available in each context, along with its default binding.

### [Global Actions](#global-actions)

These work everywhere in Claude Code:

| Action | Default | What It Does |
| --- | --- | --- |
| `app:interrupt` | Ctrl+C | Cancel current operation |
| `app:exit` | Ctrl+D | Exit Claude Code |
| `app:toggleTodos` | Ctrl+T | Toggle task list visibility |
| `app:toggleTranscript` | Ctrl+O | Toggle verbose transcript |

If you use [task management features](/blog/guide/development/todo-workflows), `app:toggleTodos` is one you'll reach for constantly. Consider binding it to something more accessible if `Ctrl+T` conflicts with your terminal.

### [Chat Actions](#chat-actions)

The main input area where you spend most of your time:

| Action | Default | What It Does |
| --- | --- | --- |
| `chat:cancel` | Escape | Cancel current input |
| `chat:cycleMode` | Shift+Tab | Cycle permission modes |
| `chat:modelPicker` | Cmd+P / Meta+P | Open model picker |
| `chat:thinkingToggle` | Cmd+T / Meta+T | Toggle extended thinking |
| `chat:submit` | Enter | Submit message |
| `chat:undo` | Ctrl+\_ | Undo last action |
| `chat:externalEditor` | Ctrl+G | Open in external editor |
| `chat:stash` | Ctrl+S | Stash current prompt |
| `chat:imagePaste` | Ctrl+V (Alt+V on Windows) | Paste image |

Note: `chat:cycleMode` defaults to `Meta+M` on Windows without VT mode (Node versions before 24.2.0/22.17.0, or Bun before 1.2.23). This ties directly into [permission management](/blog/guide/development/permission-management) for controlling what Claude can and can't do.

### [History Actions](#history-actions)

Navigate through your command history:

| Action | Default | What It Does |
| --- | --- | --- |
| `history:search` | Ctrl+R | Open history search |
| `history:previous` | Up | Previous history item |
| `history:next` | Down | Next history item |

### [Autocomplete Actions](#autocomplete-actions)

When the autocomplete menu appears:

| Action | Default | What It Does |
| --- | --- | --- |
| `autocomplete:accept` | Tab | Accept suggestion |
| `autocomplete:dismiss` | Escape | Dismiss menu |
| `autocomplete:previous` | Up | Previous suggestion |
| `autocomplete:next` | Down | Next suggestion |

### [Confirmation Actions](#confirmation-actions)

Permission and confirmation dialogs:

| Action | Default | What It Does |
| --- | --- | --- |
| `confirm:yes` | Y, Enter | Confirm action |
| `confirm:no` | N, Escape | Decline action |
| `confirm:previous` | Up | Previous option |
| `confirm:next` | Down | Next option |
| `confirm:nextField` | Tab | Next field |
| `confirm:previousField` | (unbound) | Previous field |
| `confirm:cycleMode` | Shift+Tab | Cycle permission modes |
| `confirm:toggleExplanation` | Ctrl+E | Toggle permission explanation |
| `permission:toggleDebug` | Ctrl+D | Toggle permission debug info |

### [Transcript Actions](#transcript-actions)

| Action | Default | What It Does |
| --- | --- | --- |
| `transcript:toggleShowAll` | Ctrl+E | Toggle show all content |
| `transcript:exit` | Ctrl+C, Escape | Exit transcript view |

### [History Search Actions](#history-search-actions)

| Action | Default | What It Does |
| --- | --- | --- |
| `historySearch:next` | Ctrl+R | Next match |
| `historySearch:accept` | Escape, Tab | Accept selection |
| `historySearch:cancel` | Ctrl+C | Cancel search |
| `historySearch:execute` | Enter | Execute selected command |

### [Task Actions](#task-actions)

| Action | Default | What It Does |
| --- | --- | --- |
| `task:background` | Ctrl+B | Background current task |

### [Theme, Help, and Settings Actions](#theme-help-and-settings-actions)

| Action | Context | Default | What It Does |
| --- | --- | --- | --- |
| `theme:toggleSyntaxHighlighting` | ThemePicker | Ctrl+T | Toggle syntax highlighting |
| `help:dismiss` | Help | Escape | Close help menu |
| `settings:search` | Settings | / | Enter search mode |
| `settings:retry` | Settings | R | Retry loading usage data |

### [Navigation Actions](#navigation-actions)

These cover tabs, attachments, footer, diffs, model picker, selects, and the message selector:

| Action | Context | Default | What It Does |
| --- | --- | --- | --- |
| `tabs:next` | Tabs | Tab, Right | Next tab |
| `tabs:previous` | Tabs | Shift+Tab, Left | Previous tab |
| `attachments:next` | Attachments | Right | Next attachment |
| `attachments:previous` | Attachments | Left | Previous attachment |
| `attachments:remove` | Attachments | Backspace, Delete | Remove attachment |
| `attachments:exit` | Attachments | Down, Escape | Exit attachment bar |
| `footer:next` | Footer | Right | Next footer item |
| `footer:previous` | Footer | Left | Previous footer item |
| `footer:openSelected` | Footer | Enter | Open selected item |
| `footer:clearSelection` | Footer | Escape | Clear selection |
| `messageSelector:up` | MessageSelector | Up, K | Move up in list |
| `messageSelector:down` | MessageSelector | Down, J | Move down in list |
| `messageSelector:top` | MessageSelector | Ctrl+Up, Shift+Up | Jump to top |
| `messageSelector:bottom` | MessageSelector | Ctrl+Down, Shift+Down | Jump to bottom |
| `messageSelector:select` | MessageSelector | Enter | Select message |
| `diff:dismiss` | DiffDialog | Escape | Close diff viewer |
| `diff:previousSource` | DiffDialog | Left | Previous diff source |
| `diff:nextSource` | DiffDialog | Right | Next diff source |
| `diff:previousFile` | DiffDialog | Up | Previous file |
| `diff:nextFile` | DiffDialog | Down | Next file |
| `diff:viewDetails` | DiffDialog | Enter | View details |
| `modelPicker:decreaseEffort` | ModelPicker | Left | Decrease effort level |
| `modelPicker:increaseEffort` | ModelPicker | Right | Increase effort level |
| `select:next` | Select | Down, J, Ctrl+N | Next option |
| `select:previous` | Select | Up, K, Ctrl+P | Previous option |
| `select:accept` | Select | Enter | Accept selection |
| `select:cancel` | Select | Escape | Cancel selection |
| `plugin:toggle` | Plugin | Space | Toggle plugin |
| `plugin:install` | Plugin | I | Install plugins |

## [Keystroke Syntax](#keystroke-syntax)

Claude Code uses a readable syntax for defining key combinations.

### [Modifiers](#modifiers)

Combine modifier keys with `+`:

- **`ctrl`** or **`control`** for the Control key
- **`alt`**, **`opt`**, or **`option`** for Alt/Option
- **`shift`** for Shift
- **`meta`**, **`cmd`**, or **`command`** for Meta/Command

Examples:

```p-4
ctrl+k          Single modifier + key
shift+tab       Shift + Tab
meta+p          Command/Meta + P
ctrl+shift+c    Multiple modifiers
```

### [Uppercase Letters and Shift](#uppercase-letters-and-shift)

A standalone uppercase letter implies Shift. Writing `K` in your bindings is the same as writing `shift+k`. This is particularly useful for Vim-style bindings where `j` and `J` (or `k` and `K`) do different things.

One important detail: uppercase letters *with modifiers* do NOT imply Shift. So `ctrl+K` is identical to `ctrl+k`. The uppercase is treated as purely stylistic when modifiers are present.

### [Chord Sequences](#chord-sequences)

Chords let you create multi-key shortcuts. Separate the keystrokes with a space:

```p-4
ctrl+k ctrl+s   Press Ctrl+K, release, then press Ctrl+S
```

This gives you a much larger namespace for shortcuts. If you're running out of single-key combinations, chords open up hundreds of possibilities without conflicting with existing bindings.

### [Special Keys](#special-keys)

Use these names for non-character keys:

- `escape` or `esc`
- `enter` or `return`
- `tab`
- `space`
- `up`, `down`, `left`, `right`
- `backspace`, `delete`

## [Unbinding Default Shortcuts](#unbinding-default-shortcuts)

Set any action to `null` to disable it:

```p-4
{
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+s": null
      }
    }
  ]
}
```

This is useful when a default shortcut conflicts with your terminal, your OS, or a tool you use alongside Claude Code. You can also unbind a default and then rebind the same key to a different action.

## [Reserved Shortcuts](#reserved-shortcuts)

Two shortcuts are hardcoded and cannot be rebound:

| Shortcut | Reason |
| --- | --- |
| Ctrl+C | Hardcoded interrupt/cancel |
| Ctrl+D | Hardcoded exit |

Don't try to rebind these. Claude Code won't accept it, and for good reason. `Ctrl+C` as interrupt and `Ctrl+D` as exit are Unix conventions that every terminal user expects.

## [Terminal Multiplexer Conflicts](#terminal-multiplexer-conflicts)

If you run Claude Code inside tmux, GNU screen, or another multiplexer, watch out for prefix key conflicts:

| Shortcut | Conflict |
| --- | --- |
| Ctrl+B | tmux prefix (press twice to send through) |
| Ctrl+A | GNU screen prefix |
| Ctrl+Z | Unix process suspend (SIGTSTP) |

The default `task:background` action uses `Ctrl+B`, which directly conflicts with tmux. If you're a tmux user, rebind it immediately:

```p-4
{
  "bindings": [
    {
      "context": "Task",
      "bindings": {
        "ctrl+b": null,
        "ctrl+shift+b": "task:background"
      }
    }
  ]
}
```

This is one of the most common sources of confusion for developers running Claude Code inside [terminal sessions with multiplexers](/blog/guide/mechanics/terminal-main-thread).

## [Vim Mode Interaction](#vim-mode-interaction)

When vim mode is enabled (toggle with `/vim`), keybindings and vim mode operate on different layers:

- **Vim mode** controls text input: cursor movement, modes (INSERT, NORMAL), motions, and text objects
- **Keybindings** control application actions: toggling the task list, submitting messages, opening the model picker

The key distinction is the Escape key. In vim mode, Escape switches from INSERT to NORMAL mode. It does *not* trigger `chat:cancel`. Most `Ctrl+key` shortcuts pass through vim mode to the keybinding system, so `Ctrl+T` still toggles your task list even when you're in NORMAL mode.

In NORMAL mode, pressing `?` shows the help menu (standard vim behavior), not the Claude Code help.

If you rely on [planning modes](/blog/guide/mechanics/planning-modes) heavily and use vim mode, consider binding `chat:thinkingToggle` to a chord that won't conflict with vim motions.

## [Validation and Diagnostics](#validation-and-diagnostics)

Claude Code validates your keybindings file automatically and warns you about:

- **Parse errors** in JSON syntax or structure
- **Invalid context names** that don't match the 17 supported contexts
- **Reserved shortcut conflicts** if you try to rebind Ctrl+C or Ctrl+D
- **Terminal multiplexer conflicts** for Ctrl+B, Ctrl+A, and Ctrl+Z
- **Duplicate bindings** in the same context

Run `/doctor` to see all keybinding warnings at once. This is the fastest way to diagnose why a shortcut isn't working as expected.

## [Practical Configuration Examples](#practical-configuration-examples)

Here are real-world configurations that solve common problems.

### [VS Code User Configuration](#vs-code-user-configuration)

If you're coming from VS Code and want familiar shortcuts:

```p-4
{
  "$schema": "https://platform.claude.com/docs/schemas/claude-code/keybindings.json",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+k ctrl+s": "chat:stash",
        "ctrl+shift+p": "chat:modelPicker",
        "ctrl+g": "chat:externalEditor"
      }
    },
    {
      "context": "Global",
      "bindings": {
        "ctrl+shift+t": "app:toggleTodos"
      }
    }
  ]
}
```

### [tmux-Friendly Setup](#tmux-friendly-setup)

Avoids all tmux prefix conflicts:

```p-4
{
  "$schema": "https://platform.claude.com/docs/schemas/claude-code/keybindings.json",
  "bindings": [
    {
      "context": "Task",
      "bindings": {
        "ctrl+b": null,
        "ctrl+shift+b": "task:background"
      }
    }
  ]
}
```

### [Minimal Distraction Setup](#minimal-distraction-setup)

Unbind shortcuts you keep hitting accidentally:

```p-4
{
  "$schema": "https://platform.claude.com/docs/schemas/claude-code/keybindings.json",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+s": null,
        "ctrl+u": null
      }
    }
  ]
}
```

### [Chord-Based Power User](#chord-based-power-user)

Use chords to access less-common features without burning single-key combos:

```p-4
{
  "$schema": "https://platform.claude.com/docs/schemas/claude-code/keybindings.json",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+k ctrl+t": "chat:thinkingToggle",
        "ctrl+k ctrl+m": "chat:modelPicker",
        "ctrl+k ctrl+e": "chat:externalEditor"
      }
    }
  ]
}
```

This keeps your most-used single-key shortcuts clean while still giving you fast access to everything else.

## [Building Your Own Configuration](#building-your-own-configuration)

Start small. Don't try to remap everything at once. Here's a practical approach:

1. **Run `/keybindings`** to create the config file
2. **Identify your top 3 pain points** (conflicting shortcuts, missing shortcuts, accidental triggers)
3. **Fix those first** with targeted bindings
4. **Run `/doctor`** to validate
5. **Use Claude Code for a full session** and note any remaining friction
6. **Iterate** by adding or adjusting bindings as needed

The goal isn't to customize every possible shortcut. It's to eliminate the friction between your muscle memory and Claude Code's behavior. Most developers only need 5-10 custom bindings to feel completely at home.

If you're building a more comprehensive Claude Code setup, your keybindings work alongside [CLAUDE.md configuration](/blog/guide/mechanics/claude-md-mastery) and custom slash commands to create a fully personalized environment. The keybindings handle the physical interface. The configuration files handle the behavioral interface. Together, they make Claude Code feel like it was built specifically for your workflow.

Last updated on

[Previous

Claude Code Tools](/blog/tools)[Next

Status Line Guide](/blog/tools/statusline-guide)
