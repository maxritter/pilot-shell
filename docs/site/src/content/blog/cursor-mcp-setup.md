---
slug: "cursor-mcp-setup"
title: "Cursor MCP Servers: Complete Setup Guide for 2026"
description: "Set up MCP servers in Cursor IDE. Step-by-step guide to configure Cursor MCP servers for AI-powered development with Model Context Protocol."
date: "2026-01-17"
author: "Max Ritter"
tags: [Guide, MCP]
readingTime: 6
keywords: "2026, complete, cursor, guide, mcp, servers, setup"
---

MCP & Extensions

# Cursor MCP Servers: Complete Setup Guide for 2026

Set up MCP servers in Cursor IDE. Step-by-step guide to configure Cursor MCP servers for AI-powered development with Model Context Protocol.

**Problem**: You want to extend Cursor with external tools and data sources, but the MCP configuration process feels unclear. Where do the files go? What format do they use? How does it compare to Claude Code?

**Quick Win**: Create a `.cursor/mcp.json` file in your project root and add your first MCP server:

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

Restart Cursor, and you now have web search capabilities inside the IDE.

## [What Are Cursor MCP Servers?](#what-are-cursor-mcp-servers)

Cursor MCP servers connect Cursor's AI to external tools, databases, and APIs through the [Model Context Protocol](/blog/tools/mcp-extensions/mcp-basics). They work identically to MCP servers in Claude Code and Claude Desktop since they all use the same underlying protocol.

With MCP servers configured, Cursor can:

- Search the web and fetch documentation
- Query databases with natural language
- Interact with GitHub, Slack, and other services
- Automate browser tasks for testing
- Access any service with an MCP server implementation

The MCP ecosystem is shared across all compatible tools. Any MCP server that works with Claude Desktop also works with Cursor.

## [Setting Up MCP Servers in Cursor](#setting-up-mcp-servers-in-cursor)

### [Configuration File Locations](#configuration-file-locations)

Cursor supports two configuration locations:

| Location | Path | Scope |
| --- | --- | --- |
| **Project-level** | `.cursor/mcp.json` | Only this project |
| **Global** | `~/.cursor/mcp.json` | All Cursor workspaces |

Use project-level configs for project-specific tools (like a database server for your app). Use global configs for tools you want everywhere (like web search or GitHub).

### [Step-by-Step Setup](#step-by-step-setup)

**Method 1: Manual Configuration**

1. Create the config file at `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global)
2. Add your MCP server configuration
3. Restart Cursor to load the new servers
4. Test by asking the AI to use a tool from your server

**Method 2: Command Palette**

1. Open Command Palette (Cmd+Shift+P on Mac, Ctrl+Shift+P on Windows)
2. Search for "MCP" and select "View: Open MCP Settings"
3. Click "New MCP Server" under MCP Tools
4. Cursor creates and opens the mcp.json file for editing

### [Configuration Format](#configuration-format)

Cursor MCP servers use the same JSON format as Claude Desktop:

```p-4
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "API_KEY": "your-key-here"
      }
    }
  }
}
```

For Python-based MCP servers:

```p-4
{
  "mcpServers": {
    "python-server": {
      "command": "python",
      "args": ["path/to/server.py"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    }
  }
}
```

### [Remote Server Configuration](#remote-server-configuration)

Cursor also supports remote MCP servers via HTTP:

```p-4
{
  "mcpServers": {
    "remote-server": {
      "url": "http://localhost:3000/mcp",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

This enables connecting to MCP servers running on remote machines or as shared services.

## [Best MCP Servers for Cursor](#best-mcp-servers-for-cursor)

These Cursor MCP servers provide the highest-impact capabilities. All configurations work directly in your `.cursor/mcp.json`:

### [Web Search and Research](#web-search-and-research)

```p-4
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "your-key" }
    }
  }
}
```

Enables web search directly in Cursor for documentation lookup and research.

### [GitHub Integration](#github-integration)

```p-4
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "your-token" }
    }
  }
}
```

Access repositories, create issues, manage PRs, and review code without leaving Cursor.

### [Database Access](#database-access)

```p-4
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "DATABASE_URL": "postgresql://user:pass@localhost/db" }
    }
  }
}
```

Query databases with natural language and get schema information for development.

### [Browser Automation](#browser-automation)

```p-4
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  }
}
```

Automate browser testing, scraping, and visual verification. See our [browser automation guide](/blog/tools/mcp-extensions/browser-automation) for advanced patterns.

### [File Operations](#file-operations)

```p-4
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/directory"
      ]
    }
  }
}
```

Enhanced file operations for reading and modifying files outside Cursor's default scope.

### [Memory and Knowledge](#memory-and-knowledge)

```p-4
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

Persistent memory across sessions using a knowledge graph structure.

Browse our [complete MCP servers list](/blog/tools/mcp-extensions/best-addons) for 50+ additional options.

## [Cursor vs Claude Code MCP](#cursor-vs-claude-code-mcp)

Cursor and Claude Code both use the same Model Context Protocol, making server configurations largely interchangeable. Key differences:

| Feature | Cursor | Claude Code |
| --- | --- | --- |
| **Config location** | `.cursor/mcp.json` | `~/.claude.json` or `.mcp.json` |
| **Transport types** | stdio, SSE, HTTP | stdio |
| **OAuth support** | Built-in | Manual |
| **Tool search** | Not available | [Available](/blog/tools/mcp-extensions/mcp-tool-search) |
| **Resources** | Not yet supported | Supported |

Claude Code's [MCP Tool Search](/blog/tools/mcp-extensions/mcp-tool-search) provides lazy loading that reduces context usage by 95%. Cursor loads all configured MCP tools at session start.

Both support the same server packages. A server configured for Claude Desktop works in Cursor and vice versa.

## [Troubleshooting Cursor MCP Servers](#troubleshooting-cursor-mcp-servers)

### [Server Not Loading](#server-not-loading)

**Symptom**: MCP server doesn't appear in available tools.

**Fix**:

1. Verify the JSON syntax is valid (no trailing commas)
2. Restart Cursor completely (not just reload window)
3. Check the Output panel for MCP-related errors

### [Authentication Failed](#authentication-failed)

**Symptom**: Server loads but API calls fail.

**Fix**: Verify environment variables are set correctly:

```p-4
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
      }
    }
  }
}
```

Use `${env:VAR_NAME}` to reference system environment variables instead of hardcoding secrets.

### [npx Command Not Found](#npx-command-not-found)

**Symptom**: Server fails with "command not found" error.

**Fix**: Ensure Node.js is installed and npx is in your PATH. On some systems, use the full path:

```p-4
{
  "mcpServers": {
    "server-name": {
      "command": "/usr/local/bin/npx",
      "args": ["-y", "@modelcontextprotocol/server-name"]
    }
  }
}
```

### [Remote Server Connection Issues](#remote-server-connection-issues)

**Symptom**: HTTP-based MCP server fails to connect.

**Fix**:

1. Verify the server is running and accessible
2. Check firewall rules allow the connection
3. Ensure the URL includes the correct protocol (http/https)

## [Next Steps](#next-steps)

Expand your Cursor MCP setup:

1. **Start simple**: Configure Brave Search for immediate web access
2. **Add development tools**: GitHub and database servers accelerate coding workflows
3. **Explore automation**: Set up [browser automation](/blog/tools/mcp-extensions/browser-automation) for testing
4. **Build custom servers**: Create MCP servers for your specific APIs and tools
5. **Browse all options**: Check the [complete MCP servers list](/blog/tools/mcp-extensions/best-addons)

Cursor MCP servers transform the IDE from an isolated editor into a connected development environment. Start with one server, prove the value, then expand as your workflow demands.

Sources:

- [Cursor MCP Documentation](https://cursor.com/docs/context/mcp)
- [How to Add MCP Server to Cursor](https://snyk.io/articles/how-to-add-a-new-mcp-server-to-cursor/)

Last updated on

[Previous

Extensions & Addons](/blog/tools/mcp-extensions/best-addons)[Next

Search Tools](/blog/tools/mcp-extensions/search-tools)
