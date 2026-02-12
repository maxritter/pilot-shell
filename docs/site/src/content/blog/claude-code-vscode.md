---
slug: "claude-code-vscode"
title: "Claude Code VS Code Extension: Setup & Integration Guide"
description: "Connect Claude Code to VS Code for the best of both worlds. Terminal power meets IDE convenience with this complete integration setup guide."
date: "2025-11-13"
author: "Max Ritter"
tags: [Guide, Tools]
readingTime: 5
keywords: "claude, code, extension, guide, integration, setup, vs, vscode"
---

Extensions

# Claude Code VS Code Extension: Setup & Integration Guide

Connect Claude Code to VS Code for the best of both worlds. Terminal power meets IDE convenience with this complete integration setup guide.

**Problem**: Want Claude Code's terminal power inside VS Code?

Here's your 2-minute quick win: Open VS Code, go to Extensions (Ctrl+Shift+X), and search "Claude Code". Install the official Anthropic extension (2M+ installs, verified publisher).

Click the Spark icon in your sidebar, and Claude Code runs directly in your IDE. No terminal switching. No context loss. Over 2 million developers already use it.

## [Why Use Claude Code in VS Code](#why-use-claude-code-in-vs-code)

The Claude Code VS Code extension brings terminal AI power into your IDE:

- **Autonomous exploration**: Claude reads, writes, and navigates your codebase independently
- **Real-time diffs**: See changes as inline diffs with accept/reject buttons
- **Subagents**: Run parallel AI tasks for complex multi-file operations
- **Custom slash commands**: Access CLI commands directly in the extension
- **MCP support**: Use [MCP servers](/blog/tools/mcp-extensions/mcp-basics) for browser automation and search
- **Extended thinking**: Toggle Claude's reasoning visibility for [deep thinking](/blog/guide/performance/deep-thinking-techniques)
- **Plan mode**: Review and edit Claude's [plans](/blog/guide/mechanics/planning-modes) before accepting changes

Your [first project](/blog/guide/first-project) becomes faster when Claude edits files directly in your workspace.

## [Installing the Claude Code Extension](#installing-the-claude-code-extension)

**Via VS Code Marketplace** (recommended):

1. Open VS Code
2. Click Extensions (Ctrl+Shift+X)
3. Search "Claude Code"
4. Install the official Anthropic extension (verified publisher badge)

**Requirements**: VS Code 1.98.0+ and one of these:

- Claude Pro or Max subscription
- Team or Enterprise plan
- API key (pay-as-you-go)

Check your setup with our [installation guide](/blog/guide/installation-guide). The extension also works with Cursor, Windsurf, and VSCodium.

## [Setting Up Your First Session](#setting-up-your-first-session)

Click the Spark icon in the VS Code sidebar to open Claude Code. Start a new conversation with `Cmd+N` (Mac) or `Ctrl+N` (Windows).

Ask Claude something practical:

```p-4
Create a React component with useState hook for a counter
```

Watch the real-time diff appear. Drag the sidebar wider to see inline diffs:

1. **Highlighted changes** showing what Claude wants to add
2. **Accept/Reject buttons** at the diff level
3. **File preview** before committing

Accept the changes. Code appears in your workspace immediately.

Want modifications? Just ask:

```p-4
Add a reset button to the counter
```

Claude updates the same file with another diff. You maintain full control. Learn more in our [configuration basics](/blog/guide/configuration-basics) guide.

## [Configuration Options](#configuration-options)

### [Extended Thinking Mode](#extended-thinking-mode)

Toggle Claude's reasoning visibility with the Extended Thinking button (bottom-right of prompt input). See Claude's thought process before changes - invaluable for debugging complex logic.

### [Auto-Accept Mode](#auto-accept-mode)

Enable auto-accept to automatically apply Claude's changes. Best for trusted workflows where you want to watch implementation without interruption.

### [File Attachments](#file-attachments)

Drag files into the chat or use @-mentions:

```p-4
@readme.md explain this project structure
@src/components/Header.tsx refactor to TypeScript generics
```

Claude already knows your workspace context. No manual setup needed.

### [Multiple Sessions](#multiple-sessions)

Run separate Claude sessions per workspace folder - perfect for microservices. Each session maintains its own context. Learn about [agent workflows](/blog/guide/agents/agent-fundamentals) for advanced patterns.

## [Terminal Setup in VS Code](#terminal-setup-in-vs-code)

The VS Code integrated terminal needs a small configuration to support **Shift+Enter** for multi-line prompts. Run `/terminal-setup` inside a Claude Code session and it auto-configures the keybinding for you. No manual editing required.

If you prefer multi-line input through Option+Enter, open Settings, then Profiles, then Keys, and set the Left/Right Option key to "Esc+".

For the full terminal optimization walkthrough, see the [terminal setup guide](/blog/guide/terminal-setup-guide).

### [Windows-Specific Keybindings](#windows-specific-keybindings)

On Windows, two default keybindings differ from macOS:

- **Alt+V** for image paste (instead of Ctrl+V, which is reserved for clipboard paste)
- **Meta+M** for cycling permission modes on older Node.js versions (below 24.2.0 or 22.17.0) that lack VT mode support

These are the defaults, but you can customize any shortcut through the [keybindings configuration](/blog/tools/keybindings-guide).

### [Controlling Extension Auto-Installation](#controlling-extension-auto-installation)

Claude Code's CLI automatically installs the VS Code extension when it detects a VS Code environment. To prevent this behavior, set the environment variable:

```p-4
export CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL=1
```

This is useful when managing extension installations through a corporate policy, using a locked-down VS Code profile, or running Claude Code in CI/CD pipelines where the extension is not needed.

## [When Things Go Wrong](#when-things-go-wrong)

| Error | Fix |
| --- | --- |
| Extension not loading | Update VS Code to 1.98.0+ (`code --version`) |
| Claude not responding | `Ctrl+Shift+P` → "Developer: Reload Window" |
| Authentication failed | Verify Pro/Max/Team/Enterprise subscription or API key |
| Never gets a response | Check internet, start new conversation, try CLI fallback |

See our [troubleshooting guide](/blog/guide/troubleshooting) for more fixes.

## [Enterprise: Third-Party Providers](#enterprise-third-party-providers)

Using Amazon Bedrock or Google Vertex AI? Add to your settings.json:

```p-4
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "us-east-2"
  }
}
```

Disable login prompts with `"claudeCode.disableLoginPrompt": true`.

## [You Can Now Code with Claude in VS Code](#you-can-now-code-with-claude-in-vs-code)

- You connected terminal AI power to your IDE
- Try next: [MCP extensions](/blog/tools/mcp-extensions/mcp-basics) for browser automation
- Go deeper: [Agent workflows](/blog/guide/agents/agent-fundamentals) for multi-step tasks
- Compare: [Claude Code vs Cursor](/blog/tools/extensions/claude-code-vs-cursor)
- Configure: [Terminal setup](/blog/guide/terminal-setup-guide) and [keyboard shortcuts](/blog/tools/keybindings-guide) for your workflow
- Customize: [Settings reference](/blog/guide/settings-reference) for all configuration options

The extension updates regularly. Currently in beta - [report issues on GitHub](https://github.com/anthropics/claude-code/issues).

Last updated on

[Previous

Custom Integrations](/blog/tools/mcp-extensions/custom-integrations)[Next

Claude Code vs Cursor](/blog/tools/extensions/claude-code-vs-cursor)
