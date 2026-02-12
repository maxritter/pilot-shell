---
slug: "browser-automation"
title: "Claude Code Playwright MCP: Browser Automation"
description: "Set up Playwright MCP for Claude Code browser automation. Scrape data and test web apps with Playwright and Puppeteer MCP server configs."
date: "2025-08-23"
author: "Max Ritter"
tags: [Guide, MCP]
readingTime: 4
keywords: "automation, browser, claude, code, mcp, playwright"
---

MCP & Extensions

# Playwright MCP for Claude Code: AI-Powered Browser Automation

Set up Playwright MCP for Claude Code browser automation. Scrape data and test web apps with Playwright and Puppeteer MCP server configs.

**Problem**: Manually testing web applications, scraping data, and automating repetitive browser tasks wastes hours of development time. Browser automation through [MCP servers](/blog/tools/mcp-extensions/mcp-basics) solves this.

**Quick Win**: Configure the Puppeteer MCP server and automate your first browser task in minutes. Add this to your Claude Code settings file:

```p-4
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

Now tell Claude: "Open a browser, navigate to example.com, and take a screenshot" - it handles the rest automatically.

## [Why Browser Automation with Claude Code?](#why-browser-automation-with-claude-code)

Traditional browser automation requires writing complex scripts, handling selectors, and managing browser states. Claude Code with browser MCP servers turns natural language into browser actions.

Instead of writing 50 lines of Puppeteer code, you simply describe what you want: "Fill out this contact form with test data and submit it."

## [Setting Up Browser Automation](#setting-up-browser-automation)

### [Puppeteer MCP Server Configuration](#puppeteer-mcp-server-configuration)

Add the Puppeteer MCP server to your MCP configuration file (`~/.claude.json` for CLI or `claude_desktop_config.json` for Desktop):

```p-4
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

After saving, restart Claude Code to load the new MCP server. Test by asking Claude to launch a browser and navigate to any website.

### [Playwright MCP Server Setup](#playwright-mcp-server-setup)

For advanced browser testing with multi-browser support, use the Playwright MCP server. Install and configure `@modelcontextprotocol/server-playwright`:

```p-4
npm install -g @modelcontextprotocol/server-playwright
```

Then add to your MCP configuration:

```p-4
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"]
    }
  }
}
```

**Alternative Playwright MCP**: The community `@executeautomation/playwright-mcp-server` package offers similar functionality:

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

Playwright MCP provides cross-browser testing capabilities (Chrome, Firefox, Safari) and is preferred for comprehensive test automation with Claude Code.

## [Common Browser Automation Tasks](#common-browser-automation-tasks)

### [Web Scraping Made Simple](#web-scraping-made-simple)

Ask Claude to scrape data with natural language:

> "Open example.com, find all product listings, and extract the titles and prices into a CSV file"

Claude Code handles opening the browser, finding elements, extracting structured data, and formatting the output.

### [Form Testing Automation](#form-testing-automation)

> "Open my local development site at localhost:3000, fill out the signup form with test data, submit it, and verify the success message appears"

This replaces manual testing with a single request that navigates to your site, generates realistic test data, fills all form fields, and validates success states.

### [Visual Regression Testing](#visual-regression-testing)

> "Take screenshots of my homepage at different screen sizes (mobile, tablet, desktop) and save them to ./screenshots/"

## [Advanced Browser Automation Patterns](#advanced-browser-automation-patterns)

### [Multi-Step User Journeys](#multi-step-user-journeys)

Claude Code excels at complex workflows:

> "Simulate a complete e-commerce purchase flow: browse products, add to cart, go through checkout with test details, and verify the order confirmation page"

### [Authentication Flows](#authentication-flows)

> "Log into my staging environment, navigate to the admin dashboard, and verify all navigation links work correctly"

### [Performance Monitoring](#performance-monitoring)

> "Open my app, measure page load times for the dashboard, and report any pages that take longer than 3 seconds to load"

## [Troubleshooting Browser Automation](#troubleshooting-browser-automation)

**Browser launch fails**: Ensure Chrome or Chromium is installed on your system. On Linux:

```p-4
sudo apt-get install -y chromium-browser
```

**Elements not found**: Ask Claude to wait for dynamic content: "Wait for the login button to be visible before clicking it."

**Timeouts**: For slow-loading pages, specify longer waits: "Navigate to the page and wait up to 30 seconds for it to fully load."

## [Integration with Development Workflow](#integration-with-development-workflow)

Browser automation integrates naturally with your development process:

- **Testing**: Automate regression tests during builds
- **Debugging**: Capture visual proof of bugs
- **Monitoring**: Check production sites continuously
- **Development**: Test features across browsers instantly

## [Context Optimization with MCP Tool Search](#context-optimization-with-mcp-tool-search)

Browser automation MCP servers work seamlessly with Claude Code's [MCP Tool Search feature](/blog/tools/mcp-extensions/mcp-tool-search). MCP Tool Search ensures Playwright and Puppeteer tools only load when you actually need browser automation, keeping your context free for other tasks.

## [Next Steps](#next-steps)

Master browser automation by exploring these areas:

- Learn about [MCP server configuration](/blog/tools/mcp-extensions/mcp-basics) for customizing browser settings
- Set up [custom integration patterns](/blog/tools/mcp-extensions/custom-integrations) for your specific testing needs
- Explore [popular MCP servers](/blog/tools/mcp-extensions/best-addons) for additional automation capabilities
- Check out [MCP Tool Search](/blog/tools/mcp-extensions/mcp-tool-search) to optimize context usage with multiple MCP servers

Start with simple tasks like taking screenshots, then progress to complex user journey testing as you get comfortable with natural language browser control.

Last updated on

[Previous

Search Tools](/blog/tools/mcp-extensions/search-tools)[Next

Social Media MCPs](/blog/tools/mcp-extensions/social-media-mcps)
