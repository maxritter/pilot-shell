## MCP Tools Available

**Standards:** Query first | Store learnings | Search before asking

### Memory & Search

**Cipher** (`mcp__cipher__ask_cipher`)
- Query patterns: "How did we implement X?"
- Store learnings: "Store: Fixed Y using Z pattern"
- Project memory and past decisions

**Claude Context** (`mcp__claude-context__`)
- `index_codebase(path)` - Index for semantic search
- `search_code(path, query)` - Search codebase
- `get_indexing_status(path)` - Check index status

### Development Tools

**IDE** (`mcp__ide__`)
- `getDiagnostics()` - Check errors/warnings
- `executeCode(code)` - Run code in Jupyter kernel (notebooks only)

### Documentation & Research

**Ref** (`mcp__Ref__`)
- `ref_search_documentation(query)` - Unified search for:
  - Web documentation and GitHub docs
  - Code snippets and examples
  - Library documentation
  - Private code repositories
  - Technical articles and guides
- `ref_read_url(url)` - Read and parse content from URLs (including raw GitHub URLs)

**Ref.tools is the unified solution for:**
- Code snippets
- Web search and documentation
- Web scraping
- Private code search
- GitHub repository search

**Usage patterns:**
- Always search first: `ref_search_documentation("library feature")`
- Read specific pages: `ref_read_url("https://raw.githubusercontent.com/...")`
- Use exact URLs from search results including hash fragments
- For GitHub content, use raw.githubusercontent.com URLs

### Tool Discovery

**MCP Funnel** (`mcp__mcp-funnel__`)
- `discover_tools_by_words(words, enable)` - Find tools by keywords
- `get_tool_schema(tool)` - Get tool parameters
- `bridge_tool_request(tool, arguments)` - Execute discovered tools

**When to use MCP Funnel:**
- Looking for specialized tools not covered by core MCP servers
- Exploring available capabilities
- Need to extend functionality with additional MCP servers

Use MCP Funnel to discover additional tools when needed - many more MCP servers available.

### Usage Patterns

**Start every task:**
1. `mcp__ide__getDiagnostics()` - Check existing errors
2. `mcp__cipher__ask_cipher("How did we do X?")` - Query knowledge
3. `mcp__claude-context__search_code(path, query)` - Find patterns

**End every task:**
1. `mcp__ide__getDiagnostics()` - Verify no new errors
2. `mcp__cipher__ask_cipher("Store: [learning]")` - Save knowledge

**When stuck:**
- Query Cipher for past solutions
- Search codebase for similar patterns
- Use Ref to find external documentation, code examples, and library docs
- Use MCP Funnel to discover specialized tools when needed
