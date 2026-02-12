---
slug: "mcp-basics"
title: "Claude Code MCP: Model Context Protocol Extensions Explained"
description: "Master Claude Code MCP servers to extend AI capabilities beyond default tools. Learn to install and configure powerful extensions in minutes."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, MCP]
readingTime: 5
keywords: "basics, claude, code, context, explained, extensions, mcp, model, protocol"
---

MCP & Extensions

# Claude Code MCP: Model Context Protocol Extensions Explained

Master Claude Code MCP servers to extend AI capabilities beyond default tools. Learn to install and configure powerful extensions in minutes.

**Problem**: Claude Code feels limited - it can only do basic tasks and you're constantly hitting walls when trying to access external services, databases, or specialized tools.

**Quick Win**: Configure your first MCP server to unlock web browsing, database connections, and dozens of other capabilities. Add this to your MCP settings file:

```p-4
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "your-api-key" }
    }
  }
}
```

After restarting Claude Code, test by asking Claude to "search for the latest Next.js 15 features" and watch it browse the web in real-time.

## [What Are MCP Servers?](#what-are-mcp-servers)

Model Context Protocol (MCP) servers are extensions that give Claude Code superpowers. Think of them as plugins that connect Claude to external services, databases, APIs, and tools that it normally can't access.

**New in 2026**: Claude Code now includes [MCP Tool Search](/blog/tools/mcp-extensions/mcp-tool-search) - automatic lazy loading that reduces MCP context usage by up to 95%. Configure as many servers as you need without worrying about context limits.

Without MCP servers, Claude Code is isolated - it can only work with files you give it. With MCP servers, Claude Code becomes a connected AI assistant that can:

- Browse the web and fetch current information
- Query databases and APIs
- Interact with services like GitHub, Slack, or Google Sheets
- Access specialized tools for different industries
- Automate complex workflows across multiple systems

## [How MCP Servers Work](#how-mcp-servers-work)

MCP servers run as separate processes that Claude Code communicates with through a standardized protocol. When you install an MCP server:

1. **Connection**: Claude Code establishes a connection to the MCP server
2. **Discovery**: The server tells Claude what tools/functions it provides
3. **Integration**: These tools become available in Claude's context
4. **Execution**: Claude can call these tools during conversations

```p-4
// Claude Code CLI: ~/.claude.json or project-level .mcp.json
// Claude Desktop: claude_desktop_config.json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key"
      }
    }
  }
}
```

## [Essential MCP Servers to Install](#essential-mcp-servers-to-install)

Start with these high-impact MCP servers that solve common problems:

**Web Access & Research**:

- **Brave Search** (`@modelcontextprotocol/server-brave-search`) - Web search capability
- **Fetch** (`@modelcontextprotocol/server-fetch`) - Fetch and parse web content

**Development Tools**:

- **GitHub** (`@modelcontextprotocol/server-github`) - Repository access and management
- **Git** (`@modelcontextprotocol/server-git`) - Local git operations
- **PostgreSQL** (`@modelcontextprotocol/server-postgres`) - Database queries

**File Operations**:

- **Filesystem** (`@modelcontextprotocol/server-filesystem`) - Enhanced file operations
- **Google Drive** (`@modelcontextprotocol/server-gdrive`) - Cloud file access

Add any of these to your `mcpServers` config using the pattern shown above.

Each MCP server unlocks specific capabilities. [Browse popular MCP servers](/blog/tools/mcp-extensions/best-addons) to find ones matching your workflow.

## [Configuration Process](#configuration-process)

MCP servers are configured through JSON files, not CLI commands:

1. **Locate your config file**:

   - Claude Code CLI: `~/.claude.json` or `.mcp.json` in project root
   - Claude Desktop (macOS): `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Claude Desktop (Windows): `%APPDATA%\Claude\claude_desktop_config.json`
2. **Add the server configuration**:

```p-4
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": { "API_KEY": "your-key-here" }
    }
  }
}
```

3. **Restart Claude Code** to load the new configuration.
4. **Test in Claude Code**:
   Ask Claude: "What MCP tools are available?" to see your installed extensions.

## [Common Setup Issues and Fixes](#common-setup-issues-and-fixes)

**Error: "MCP server not found"**
Fix: Ensure the package is installed globally and accessible:

```p-4
# Reinstall with explicit global flag
npm install -g @modelcontextprotocol/server-brave-search
```

**Error: "Authentication failed"**  
Fix: Verify your API keys are properly set:

```p-4
# Check environment variables
echo $BRAVE_API_KEY
echo $GITHUB_TOKEN
```

**Error: "Server connection timeout"**
Fix: Restart Claude Code to refresh MCP connections. Exit your current session and start a new one to reload all MCP servers.

## [Quick Enable/Disable Commands](#quick-enabledisable-commands)

Toggle MCP servers on the fly without editing config files:

```p-4
# Disable a server temporarily
/mcp disable supabase
 
# Re-enable when needed
/mcp enable supabase
```

This is useful when an MCP server causes issues or you want to reduce noise from tools you're not currently using. The server configuration stays in your config file - you're just toggling its active state for the current session.

## [Advanced Configuration](#advanced-configuration)

Fine-tune MCP servers for optimal performance:

```p-4
{
  "mcpServers": {
    "custom-server": {
      "command": "node",
      "args": ["path/to/your/server.js"],
      "env": {
        "LOG_LEVEL": "debug",
        "TIMEOUT": "30000"
      }
    }
  }
}
```

Custom server configurations allow you to:

- Run local Node.js or Python MCP servers
- Pass custom environment variables for API keys and settings
- Enable debug logging for troubleshooting
- Connect to any service with a compatible MCP server

## [Next Actions](#next-actions)

Your MCP journey starts now:

1. **Install your first MCP server**: Pick Brave Search for immediate web access
2. **Explore popular options**: Check our [Popular MCP Servers guide](/blog/tools/mcp-extensions/best-addons) for curated recommendations
3. **Set up browser automation**: Learn [browser automation with MCP](/blog/tools/mcp-extensions/browser-automation) for advanced web interactions
4. **Create custom integrations**: Build your own MCP servers with our [Custom Integrations tutorial](/blog/tools/mcp-extensions/custom-integrations)

MCP servers transform Claude Code from an isolated assistant into a connected powerhouse. Start with one server today and gradually build your extension library as your needs evolve.

Last updated on

[Previous

Permission Hook](/blog/tools/hooks/permission-hook-guide)[Next

MCP Tool Search](/blog/tools/mcp-extensions/mcp-tool-search)
