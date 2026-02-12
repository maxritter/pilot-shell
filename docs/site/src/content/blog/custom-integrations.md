---
slug: "custom-integrations"
title: "Claude Code Integrations: Build Your Own MCP Servers"
description: "Create custom Claude Code integrations with MCP servers. Learn to extend Claude's capabilities with your tools, APIs, and database connections."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, MCP]
readingTime: 4
keywords: "build, claude, code, custom, integrations, mcp, own, servers"
---

MCP & Extensions

# Claude Code Integrations: Build Your Own MCP Servers

Create custom Claude Code integrations with MCP servers. Learn to extend Claude's capabilities with your tools, APIs, and database connections.

**Problem**: Available MCP servers don't connect to YOUR specific tools - your company's database, internal APIs, or custom workflows. You need Claude Code integrated with systems only you use.

**Quick Win**: Build a basic MCP server in 5 minutes that connects Claude to any REST API:

```p-4
// my-api-server.js - Connect Claude to your API
const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
 
const server = new Server({ name: "my-api-server", version: "1.0.0" });
 
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "fetch_user_data",
      description: "Get user information from our internal API",
      inputSchema: {
        type: "object",
        properties: {
          userId: { type: "string", description: "User ID to fetch" },
        },
        required: ["userId"],
      },
    },
  ],
}));
 
server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;
 
  if (name === "fetch_user_data") {
    const response = await fetch(
      `https://api.yourcompany.com/users/${args.userId}`,
      {
        headers: { Authorization: `Bearer ${process.env.API_TOKEN}` },
      },
    );
    return {
      content: [{ type: "text", text: JSON.stringify(await response.json()) }],
    };
  }
});
 
server.connect(process.stdio);
```

Save this as `my-api-server.js` and test: `node my-api-server.js` - you've created your first custom integration.

## [MCP Server Development Essentials](#mcp-server-development-essentials)

MCP servers are Node.js applications that expose tools to Claude Code. They run as separate processes, giving Claude access to APIs, databases, and services.

**Every MCP Server Needs**:

- **Tool definitions**: Functions Claude can call
- **Tool handlers**: Code that executes those functions
- **Error handling**: Meaningful responses when things fail
- **Authentication**: Secure access to external systems

## [Essential Integration Patterns](#essential-integration-patterns)

### [REST API Integration](#rest-api-integration)

Connect Claude to any HTTP API or web service:

```p-4
// Generic API connector pattern
const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
 
const server = new Server({ name: "api-connector", version: "1.0.0" });
 
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "api_get",
      description: "GET request to any endpoint",
      inputSchema: {
        type: "object",
        properties: {
          endpoint: { type: "string", description: "API endpoint path" },
          params: { type: "object", description: "Query parameters" },
        },
        required: ["endpoint"],
      },
    },
  ],
}));
 
server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;
 
  if (name === "api_get") {
    const url = new URL(`${process.env.API_BASE_URL}${args.endpoint}`);
    if (args.params) {
      Object.entries(args.params).forEach(([key, value]) =>
        url.searchParams.append(key, value),
      );
    }
 
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${process.env.API_TOKEN}` },
    });
 
    return {
      content: [
        { type: "text", text: JSON.stringify(await response.json(), null, 2) },
      ],
    };
  }
});
 
server.connect(process.stdio);
```

Works with Stripe, Shopify, internal APIs, or any HTTP service.

### [Database Integration](#database-integration)

Connect Claude to your databases:

```p-4
// Database connector for PostgreSQL, MySQL, SQLite
const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { Client } = require("pg");
 
const server = new Server({ name: "database-connector", version: "1.0.0" });
const client = new Client({ connectionString: process.env.DATABASE_URL });
 
server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "query_database") {
    const result = await client.query(request.params.arguments.query);
    return {
      content: [{ type: "text", text: JSON.stringify(result.rows, null, 2) }],
    };
  }
});
```

Now Claude can run queries and help with database operations.

## [Setup and Testing](#setup-and-testing)

Create your server project:

```p-4
mkdir my-mcp-server && cd my-mcp-server
npm init -y && npm install @modelcontextprotocol/sdk
```

Configure Claude Code by adding your server to the MCP settings file. The location depends on your setup:

- **Claude Code CLI**: `~/.claude.json` (user-level) or `.mcp.json` (project-level)
- **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```p-4
{
  "mcpServers": {
    "my-custom-server": {
      "command": "node",
      "args": ["/path/to/your/server.js"],
      "env": { "API_TOKEN": "your-token" }
    }
  }
}
```

After saving the configuration, restart Claude Code to load your new server.

## [Common Issues and Solutions](#common-issues-and-solutions)

**Server not found**: Check your configuration file path and JSON syntax. Ensure the command path is absolute.

**Tool timeout**: Add timeout handling to prevent hanging operations.

**Authentication failed**: Check environment variables in your server configuration.

## [Best Practices](#best-practices)

- Wrap external calls in try-catch blocks for error handling
- Store tokens in environment variables, never hardcode them
- Add rate limiting for APIs with usage restrictions
- Use console.log for debugging - shows in Claude's logs

## [Next Steps](#next-steps)

Start building your custom integrations:

1. **Pick your first API**: Choose one tool you use daily
2. **Use the REST pattern**: Follow the connector template above
3. **Test thoroughly**: Ask Claude "What MCP tools are available?" to verify your server loaded
4. **Add server instructions**: Include descriptive instructions for [MCP Tool Search](/blog/tools/mcp-extensions/mcp-tool-search) compatibility
5. **Learn more**: Check our [MCP basics guide](/blog/tools/mcp-extensions/mcp-basics) and [popular MCP servers](/blog/tools/mcp-extensions/best-addons)

MCP servers transform Claude Code into your personalized development environment.

Last updated on

[Previous

Social Media MCPs](/blog/tools/mcp-extensions/social-media-mcps)[Next

Claude Code VS Code](/blog/tools/extensions/claude-code-vscode)
