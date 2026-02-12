---
slug: "mcp-tool-search"
title: "Claude Code MCP Tool Search: Save 95% Context"
description: "Configure enable_tool_search for Claude Code MCP lazy loading. Reduce context usage by 95% with MCP Tool Search and optimize your context window."
date: "2026-01-15"
author: "Max Ritter"
tags: [Guide, MCP]
readingTime: 5
keywords: "95, claude, code, context, mcp, save, search, tool"
---

MCP & Extensions

# MCP Tool Search: Claude Code Lazy Loading for 95% Context Reduction

Configure enable\_tool\_search for Claude Code MCP lazy loading. Reduce context usage by 95% with MCP Tool Search and optimize your context window.

**Problem**: Your MCP servers are eating your context window alive. With 7+ servers configured, you're losing 50-70% of your 200K context before writing a single prompt. Complex tasks become impossible when you start each session with only 60-90K tokens remaining.

**Quick Win**: Claude Code now automatically enables MCP Tool Search when your MCP tools would consume more than 10% of context. No configuration needed - it just works. Check your context usage with `/context` to see the difference.

## [What is MCP Tool Search?](#what-is-mcp-tool-search)

MCP Tool Search is Claude Code's new lazy loading system for MCP servers. Instead of loading all tool definitions at session start, Claude Code loads a lightweight search index and fetches tool details on-demand when you actually need them.

Before MCP Tool Search:

```p-4
Starting session...
Loading 73 MCP tools... [39.8k tokens]
Loading 56 agents... [9.7k tokens]
Loading system tools... [22.6k tokens]
Ready with 92k tokens remaining.
```

After MCP Tool Search:

```p-4
Starting session...
Loading tool registry... [5k tokens]
Ready with 195k tokens available.

User: "I need to query the database"
> Auto-loading: postgres-mcp [+1.2k tokens]
> 193.8k tokens remaining
```

The difference is dramatic: **95% reduction** in initial context consumption for users with multiple [MCP servers](/blog/tools/mcp-extensions/mcp-basics).

## [How MCP Tool Search Works](#how-mcp-tool-search-works)

MCP Tool Search activates automatically when your MCP tool descriptions would use more than 10% of your context window. When triggered:

1. **Registry Creation**: Claude Code builds a lightweight index of tool names and descriptions
2. **On-Demand Loading**: Tools load only when Claude determines they're needed for your request
3. **Intelligent Caching**: Loaded tools stay available for the session duration
4. **Seamless Experience**: MCP tools work exactly as before - no workflow changes required

The system analyzes your input, matches relevant keywords, and loads only the tools likely to help with your current task.

## [For MCP Server Builders](#for-mcp-server-builders)

If you're building MCP servers, the `server instructions` field becomes critical with MCP Tool Search enabled. This field helps Claude know when to search for your tools.

Think of server instructions like skills - they tell Claude what capabilities your server provides and when to look for them:

```p-4
{
  "mcpServers": {
    "my-custom-server": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "serverInstructions": "Database operations for PostgreSQL including queries, schema management, and data migrations. Use for any database-related tasks."
    }
  }
}
```

Good server instructions should:

- Describe the server's capabilities clearly
- Include keywords users might use in prompts
- Specify when the tools should be activated
- Be concise but comprehensive

## [Checking Your Context Usage](#checking-your-context-usage)

Monitor how MCP Tool Search affects your context consumption:

```p-4
# Check current context usage
/context
 
# See which MCP tools are loaded
/mcp
```

With MCP Tool Search active, you'll see significantly lower initial token counts. As you work and Claude loads relevant tools, the count increases - but only for tools you actually use.

## [Configuration Options](#configuration-options)

MCP Tool Search works automatically, but you can influence its behavior through settings and commands.

### [Enable or Disable Tool Search](#enable-or-disable-tool-search)

Control MCP Tool Search globally via your Claude Code settings:

```p-4
{
  "enable_tool_search": true
}
```

Set `enable_tool_search` to `false` if you prefer all MCP tools loaded at session start (legacy behavior).

### [Per-Server Control](#per-server-control)

**Disable for specific servers** (if you always need certain tools immediately):

```p-4
/mcp disable tool-search my-always-needed-server
```

**Force load specific tools** when you know you'll need them:

```p-4
Load the github and postgres MCP tools for this session
```

## [Real-World Impact](#real-world-impact)

The GitHub issue that drove this feature ([#7336](https://github.com/anthropics/claude-code/issues/7336)) documented the problem precisely:

| Resource | Before | After |
| --- | --- | --- |
| MCP tools | 39.8k tokens (19.9%) | ~5k tokens (2.5%) |
| Available context | 92k tokens | 195k tokens |
| Usable for work | 46% | 97.5% |

Users with complex setups - database servers, GitHub integrations, browser automation, custom APIs - can now run full workloads without hitting context limits.

## [Compatibility Notes](#compatibility-notes)

MCP Tool Search works with all existing MCP servers. However, some considerations:

- **Older servers**: May work less efficiently if they lack good tool descriptions
- **Custom servers**: Add clear `serverInstructions` for best results
- **High-frequency tools**: Consider disabling MCP Tool Search for servers you use constantly

## [What This Enables](#what-this-enables)

With 95% more available context, you can now:

- Run longer, more complex coding sessions
- Use more MCP servers simultaneously without penalty
- Maintain conversation history across extended workflows
- Execute multi-step tasks that previously hit context limits

## [Next Steps](#next-steps)

Maximize your MCP setup with MCP Tool Search:

1. **Audit your servers**: Run `/context` to see your current usage
2. **Update server instructions**: Add descriptive instructions to custom servers
3. **Explore more servers**: Check our [popular MCP servers guide](/blog/tools/mcp-extensions/best-addons) - you can now run more without penalty
4. **Learn MCP fundamentals**: Review [MCP basics](/blog/tools/mcp-extensions/mcp-basics) if you're new to the protocol

MCP Tool Search removes the primary constraint that limited MCP adoption. Configure the servers you need, and let Claude Code handle the context management automatically.

Last updated on

[Previous

MCP Basics](/blog/tools/mcp-extensions/mcp-basics)[Next

Context7 MCP](/blog/tools/mcp-extensions/context7-mcp)
