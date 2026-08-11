---
title: "Claude Code Interactive Mode: Complete Reference (2026)"
description: "Complete Claude Code interactive mode reference. Keyboard shortcuts, vim mode, bash mode, background tasks, and slash commands."
slug: interactive-mode
date: 2026-03-11
authors:
  - max-ritter
tags:
  - guide
  - mechanics
---

Complete Claude Code interactive mode reference. Keyboard shortcuts, vim mode, bash mode, background tasks, and slash commands.

<!-- truncate -->

**Problem**: You use Claude Code every day, but you're only touching a fraction of what Claude Code's interactive mode can do. You type prompts, hit Enter, and wait. Meanwhile, there are shortcuts that kill stalled agents instantly, a way to ask side questions while Claude is mid-response, a full vim editor built into the input, and a bash mode that lets you run shell commands with conversation context. You're leaving speed on the table because the interactive features aren't documented in one place.

**Quick Win**: Press `Ctrl+F` right now in any Claude Code session. Press it again within 3 seconds to confirm. It kills all background agents. If you've ever had a runaway sub-agent chewing through tokens while you waited for it to stop, that shortcut alone is worth reading this page. Or try `/btw` while Claude is processing a response to ask a side question without touching the conversation history.

```
# Kill all background agents instantly
Ctrl+F
 
# Ask a side question while Claude is working
/btw what file was that error in?
 
# Toggle vim mode for full modal editing
/vim
```

Claude Code's interactive mode goes far deeper than a chat prompt. It's a terminal application with keyboard shortcuts, input modes, quick commands, and workflow features that most users never discover. If you're spending hours in Claude Code sessions, knowing these features is the difference between fighting the interface and flowing through it. New to working in the terminal? Start with the terminal-first development model to understand Claude Code's execution model.

## /btw: Side Questions Without Breaking Flow

This is the newest interactive feature, and it solves a genuine pain point. `/btw` lets you ask Claude a question without adding it to the conversation history. The response doesn't become part of the context window. It doesn't change what Claude "remembers" about your session.

Here's what makes it interesting: `/btw` works while Claude is already processing a response. You don't have to wait for Claude to finish before asking your question. You type `/btw`, ask your thing, get an answer, and the main response keeps generating.

```
# While Claude is mid-response:
/btw which test file covers the auth middleware?
 
# Quick clarification without polluting context:
/btw what's the difference between useEffect and useLayoutEffect?
 
# Check something without derailing the current task:
/btw did we already update the error types in types.ts?
```

The mental model that helps: `/btw` is the inverse of a sub-agent. A sub-agent has full tool access but starts with an empty context. `/btw` has full visibility into your current conversation but has no tools. It can only answer from what's already in context. No file reads, no web searches, no code execution. Just a quick answer based on everything Claude already knows about your session.

**Key constraints:**

- Single response only. No follow-ups within a `/btw` thread.
- No tool access. It answers from conversation context only.
- Low cost. It reuses the prompt cache, so tokens are minimal.
- Dismiss with Space, Enter, or Escape and continue working.

This was built by Erik Schluntz on the Claude Code team as a side project. Thariq Shihipar (Claude Code lead) announced it on March 11, 2026, and the tweet hit 2.2M views. The demand for "ask a question without derailing context" has been loud for months, and this is the answer.

`/btw` is most useful during long-running tasks. If Claude is refactoring a large module and you suddenly need to check something, you no longer have to cancel the response, ask your question, then re-prompt. You just `/btw` and keep going.

## Keyboard Shortcuts That Actually Matter

Claude Code has dozens of keyboard shortcuts. Rather than listing them all alphabetically, here are the ones grouped by when you'll actually reach for them.

**macOS users**: Shortcuts using `Alt` (like `Alt+P`, `Alt+T`, `Alt+B`, `Alt+F`) require configuring the Option key as Meta in your terminal. In iTerm2, go to Settings, Profiles, Keys and set Left/Right Option to "Esc+". In Terminal.app, check "Use Option as Meta Key" under Profiles, Keyboard. Run `/terminal-setup` if you're unsure about your configuration.

### Session Control

| Shortcut | What It Does | When You Need It |
| --- | --- | --- |
| `Ctrl+C` | Cancel current response | Claude is going down the wrong path |
| `Ctrl+F` | Kill all background agents (press twice to confirm) | A sub-agent is burning tokens |
| `Ctrl+D` | Exit Claude Code | Done with the session |
| `Ctrl+L` | Clear screen | Terminal is cluttered |
| `Esc Esc` | Rewind or summarize from any point | Claude made a mistake, undo it |

The `Esc Esc` double-tap is underrated. It lets you restore code and conversation to a previous point, or generate a summary from a selected message. This is significantly better than `Ctrl+C` when you want to undo rather than just stop.

### Input and Navigation

| Shortcut | What It Does | When You Need It |
| --- | --- | --- |
| `Up/Down` arrows | Scroll through prompt history | Re-running a previous prompt |
| `Ctrl+R` | Reverse search through history | Finding a specific past prompt |
| `Ctrl+G` | Open external text editor | Writing a long, complex prompt |
| `Ctrl+V` / `Cmd+V` | Paste image from clipboard | Sharing screenshots for debugging |
| `Shift+Tab` or `Alt+M` | Toggle permission modes | Switching between plan/auto-accept/normal |

The `Ctrl+G` shortcut opens your system's default text editor (usually whatever `$EDITOR` is set to). This is invaluable for multi-paragraph prompts where the single-line terminal input feels cramped. Write your prompt in a real editor, save and close, and it sends. If you're already configuring your [CLAUDE.md](/blog/claude-md-mastery) for project context, complex prompts benefit from the same editing treatment.

### Model and Thinking Controls

| Shortcut | What It Does | When You Need It |
| --- | --- | --- |
| `Alt+P` | Switch model | Changing between Sonnet and Opus mid-session |
| `Alt+T` | Toggle extended thinking | Enabling deep reasoning for complex problems |
| `Ctrl+O` | Toggle verbose output | Seeing full tool call details |
| `Ctrl+T` | Toggle task list | Tracking multi-step work |
| `Ctrl+B` | Background the current task | Moving a long response to the background |

`Alt+T` for toggling extended thinking is worth highlighting. When you're working through complex reasoning tasks, turning on extended thinking mid-session changes how Claude approaches the problem. You don't need to start a new session or adjust configuration. Just toggle it when you need deeper analysis.

### Text Editing in the Input

These work in the prompt input line before you send:

| Shortcut | What It Does |
| --- | --- |
| `Ctrl+K` | Delete from cursor to end of line |
| `Ctrl+U` | Delete entire line |
| `Ctrl+Y` | Paste last deleted text |
| `Alt+Y` | Cycle through paste history |
| `Alt+B` | Move cursor back one word |
| `Alt+F` | Move cursor forward one word |

If you want to go further with shortcut customization, the [keybindings system](/blog/keybindings-guide) lets you remap every shortcut in a single JSON file.

## Multiline Input

The terminal input is a single line by default, but there are four ways to write multiline prompts without reaching for `Ctrl+G`:

- **Backslash + Enter**: Type `\` at the end of a line, then hit Enter. Continues on the next line.
- **Option+Enter** (macOS) or **Shift+Enter**: Inserts a newline without sending.
- **Ctrl+J**: Inserts a newline in the input.
- **Paste mode**: Pasting multi-line text from your clipboard automatically enters multi-line mode.

For truly long prompts, `Ctrl+G` to open an external editor is still the better option. But for a quick two or three-line prompt, `\` + Enter is the fastest.

## Quick Commands: /, !, and @

Three prefix characters unlock different input modes without needing a slash command.

### / for Slash Commands and Skills

Type `/` to see all available commands and custom skills defined in your project. The list filters as you type. This is your entry point to everything from `/compact` (compress context) to `/diff` (view recent changes) to `/theme` (change syntax highlighting).

### ! for Bash Mode

Type `!` followed by any shell command to run it directly with full conversation context. This is different from Claude executing bash for you. When you type `! git log --oneline -5`, the command runs immediately in your shell, and the output becomes part of the conversation.

```
# Run git commands without leaving the session
! git status
 
# Check file contents
! cat src/config.ts
 
# Run tests
! npm test
 
# Tab autocomplete works from ! history
! npm <Tab>
```

Bash mode preserves conversation context, so if Claude suggested a command and you want to run a modified version of it, type `!` and go. The output feeds back into Claude's context, which means you can follow up with "now fix the errors from that test run" and Claude sees exactly what happened.

### @ for File Path Mentions

Type `@` followed by a file path to explicitly reference a file in your prompt. This tells Claude to look at that specific file, making your intent unambiguous. Tab completion works for file paths after `@`.

## The Slash Command Reference

Claude Code ships with a substantial list of built-in slash commands. Here are the ones organized by category, with notes on when each matters.

### Session Management

| Command | Purpose |
| --- | --- |
| `/add-dir` | Add a new working directory to the current session |
| `/clear` | Reset conversation history (also resets per-directory command history) |
| `/compact` | Compress context to free up token space |
| `/exit` | Exit Claude Code |
| `/fork` | Branch conversation into a new session |
| `/resume` | Resume a previous session |
| `/rename` | Rename current session |
| `/rewind` | Undo the last turn |

`/compact` is essential for long sessions. When your context window fills up, `/compact` summarizes the conversation to reclaim space. If you're doing extended work, run it proactively before hitting limits rather than waiting for the automatic compaction.

### Information and Status

| Command | Purpose |
| --- | --- |
| `/cost` | Show token usage and cost for this session |
| `/usage` | Show plan usage and rate limits |
| `/extra-usage` | Configure extra usage when rate-limited |
| `/stats` | Show session statistics |
| `/status` | Show account status |
| `/diff` | Show recent file changes |
| `/doctor` | Diagnose common configuration issues |
| `/keybindings` | Open or create keybindings config file |
| `/release-notes` | Show latest release notes |

### Configuration

| Command | Purpose |
| --- | --- |
| `/config` | Open settings |
| `/context` | Visualize context usage as a colored grid |
| `/init` | Initialize Claude Code in a project |
| `/memory` | Edit CLAUDE.md memory file |
| `/model` | Switch the active model |
| `/permissions` | Manage tool permissions |
| `/theme` | Change syntax highlighting and display theme |
| `/statusline` | Configure the terminal status line |
| `/terminal-setup` | Configure terminal integration |
| `/privacy-settings` | Manage privacy preferences |
| `/vim` | Toggle vim editing mode |

### Tools and Integrations

| Command | Purpose |
| --- | --- |
| `/mcp` | Manage MCP server connections |
| `/hooks` | Manage automation hooks |
| `/ide` | Connect to IDE integration |
| `/chrome` | Connect to Chrome for browser automation |
| `/desktop` | Connect to Claude Desktop |
| `/mobile` | Show QR code to download Claude mobile |
| `/plugin` | Manage plugins |
| `/reload-plugins` | Reload all plugins |

### Collaboration

| Command | Purpose |
| --- | --- |
| `/agents` | Manage running sub-agents |
| `/tasks` | View and manage task list |
| `/plan` | Enter planning mode |
| `/sandbox` | Run in isolated sandbox |
| `/pr-comments` | Fetch comments from a GitHub PR |
| `/remote-control` | Enable remote control |
| `/remote-env` | Manage remote environments |
| `/security-review` | Analyze branch changes for security vulnerabilities |
| `/stickers` | Order physical Claude Code stickers |

### Account

| Command | Purpose |
| --- | --- |
| `/login` | Log in to your Anthropic account |
| `/logout` | Log out |
| `/upgrade` | Upgrade your plan |
| `/install-github-app` | Install the GitHub integration |
| `/install-slack-app` | Install the Slack integration |
| `/fast` | Toggle fast mode (same model, faster output) |
| `/feedback` | Send feedback to Anthropic |
| `/export` | Export conversation |
| `/copy` | Copy last response to clipboard |
| `/passes` | Share free weeks of Claude Code with friends |
| `/skills` | View available skills |
| `/insights` | View conversation insights |
| `/help` | Show help |

### The New /btw Command

| Command | Purpose |
| --- | --- |
| `/btw` | Ask a side question without affecting conversation history |

Already covered in detail above. This is the standout command from the March 2026 release.

One previously available command worth noting: `/review` is now deprecated. If you were using it for code reviews, the [/simplify command](/blog/simplify-batch-commands) is its replacement, running a three-agent parallel review instead.

## Vim Mode: Full Modal Editing in the Input

Type `/vim` to enable vim keybindings for the prompt input. This isn't a stripped-down vim emulation. It includes mode switching (Normal and Insert), navigation (`h/j/k/l`, `w/b/e`, `0/$`, `f/F/t/T` character jumps), editing operators (`d`, `c`, `y`, `p`), and text objects (`iw`, `aw`, `i"`, `a(`).

For developers who live in vim or neovim, this removes the cognitive switch between their editor and Claude Code's input. You get the same muscle memory for editing prompts that you have for editing code.

Key vim operations supported:

| Category | Commands |
| --- | --- |
| **Mode switching** | `i`, `I`, `a`, `A`, `o`, `O`, `Esc` |
| **Navigation** | `h`, `j`, `k`, `l`, `w`, `b`, `e`, `0`, `$`, `^`, `gg`, `G` |
| **Character jump** | `f{char}`, `F{char}`, `t{char}`, `T{char}`, `;`, `,` |
| **Editing** | `d`, `dd`, `D`, `c`, `cc`, `C`, `x`, `J`, `.`, `>>`, `<<` |
| **Text objects** | `iw`, `aw`, `iW`, `aW`, `i"`, `a"`, `i(`, `a(`, `i{`, `a{` |
| **Clipboard** | `y`, `yy`, `p`, `P` |

Toggle it off with `/vim` again. The mode persists across prompts within a session but resets when you start a new session.

## Background Tasks with Ctrl+B

When Claude is working on a long response, you don't have to sit and watch. Press `Ctrl+B` to push the current task to the background. (Tmux users: press `Ctrl+B` twice, since tmux uses the same prefix key.) Claude keeps working, and you get your prompt back to start something else or run shell commands.

Background task behavior:

- Output buffers in the background and displays when you return to it.
- Multiple tasks can run simultaneously.
- `Ctrl+F` kills all background agents if something goes wrong.
- The task list (`Ctrl+T`) shows background task status.

This pairs well with the terminal-first model where you're the scheduler coordinating multiple work streams. Push a long refactoring task to the background, start a quick bug fix in the foreground, and check back when the refactoring finishes.

Common use cases for backgrounding:

- Long code generation that you know will take a few minutes
- Test suite runs where you want to work on something else while waiting
- Research tasks where Claude is reading multiple files
- Any task where watching the output stream doesn't add value

## Prompt Suggestions

Claude Code auto-generates prompt suggestions based on your git history and conversation context. You'll see suggested prompts appear below the input. Press Tab to accept a suggestion.

This works well after git operations. If you just committed, Claude might suggest "write tests for the changes in the last commit." If you have uncommitted changes, it might suggest "review the current diff for issues." The suggestions use cache reuse, so they add minimal cost to your session.

The suggestions get smarter over your conversation. Early on they're based on git state. After a few exchanges, they incorporate conversation context and suggest logical next steps based on what you've been working on.

## Command History

Every prompt you type is saved to per-directory command history. Use the Up and Down arrows to scroll through previous prompts, or `Ctrl+R` for reverse incremental search (type a fragment and it finds matching past prompts).

Two things to know:

1. **History is per-directory.** Different projects maintain separate history. This prevents cross-project prompt contamination.
2. **`/clear` resets history.** When you clear the conversation, it also wipes the command history for that directory. If you want to preserve access to old prompts, use `/compact` instead of `/clear`.

## Task List

Press `Ctrl+T` to toggle the task list overlay. This tracks multi-step work within a session, showing what's been completed, what's in progress, and what's queued. The task list persists across context compactions, so even if Claude's conversation gets summarized, the task tracking survives.

For team workflows, set the `CLAUDE_CODE_TASK_LIST_ID` environment variable to share a task list across multiple Claude Code sessions. This is useful when you have parallel sessions working on different parts of the same project and want a unified view of progress.

## PR Review Status

If you're working in a branch with an open pull request, Claude Code shows the PR status in the footer. A colored underline on the PR link tells you the review state at a glance:

| Color | Status |
| --- | --- |
| Green | Approved |
| Yellow | Review pending |
| Red | Changes requested |
| Gray | Draft PR |
| Purple | Merged |

This auto-updates every 60 seconds. No more switching to the browser to check if your PR got approved. You see it right in the terminal while you work. This feature requires the `gh` CLI to be installed and authenticated (`gh auth login`).

## Combining Features for Real Workflows

These interactive features get powerful when combined. Here are patterns that work well together.

**Deep work with background tasks and /btw**: Push a complex implementation to the background with `Ctrl+B`. While it runs, use `/btw` to ask quick questions about the codebase without adding noise to the main task's context. Check task progress with `Ctrl+T`.

**Rapid iteration with bash mode and fast mode**: Toggle [fast mode](/blog/fast-mode) for quick responses, use `!` to run tests between iterations, and `Ctrl+R` to recall previous prompts when you want to re-run with modifications. The combination compresses the feedback loop between prompting, testing, and adjusting.

**Careful work with planning mode and vim input**: Enter planning mode for analysis, write detailed prompts using vim mode for editing comfort, review the plan, then exit planning mode and let Claude execute. For long instructions, `Ctrl+G` opens a full editor.

**Multi-agent coordination with task list and agents**: Use `/agents` to see running sub-agents, `Ctrl+T` to track their tasks, `Ctrl+F` to kill any that go off-track, and `/btw` to ask about their status without interrupting the main conversation.

## Next Steps

- Learn the [keybindings customization system](/blog/keybindings-guide) to remap any shortcut to match your muscle memory
- Explore planning mode for separating thinking from execution
- Read about the terminal-first model that frames how all these features fit together
- Try [voice mode](/blog/voice-mode) for hybrid typed and spoken input
- Check [/simplify and /batch](/blog/simplify-batch-commands) for bundled multi-agent workflows
- See the context management guide for strategies on keeping your session efficient

Claude Code's interactive mode is what separates "I use Claude for code" from "Claude Code is my development environment." The features covered here, from `/btw` side questions to vim editing to background tasks, aren't nice-to-haves. They're the interface layer that makes long Claude Code sessions productive instead of tedious. Learn the shortcuts that match your workflow, ignore the ones that don't, and revisit this reference when you hit a friction point that feels like it should have a shortcut. It probably does.
<!-- pilot-shell-cta -->

---

## About Pilot Shell

**Pilot Shell** wraps Claude Code in three slash commands: `/prd` to scope the work, `/spec` to plan-implement-verify it under TDD, `/fix` for the smaller bugs. Plus persistent memory, code-graph search, and a configured hook pipeline.

[See Pilot Shell on GitHub →](https://github.com/maxritter/pilot-shell)
