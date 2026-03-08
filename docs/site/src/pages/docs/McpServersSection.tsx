import { Globe, Brain, Search, BookOpen } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const mcpServers = [
  {
    icon: BookOpen,
    name: "lib-docs",
    prefix: "mcp__plugin_pilot_context7__",
    purpose: "Library documentation lookup",
    desc: "Get up-to-date API docs and code examples for any library or framework. Two-step: resolve the library ID, then query for specific documentation.",
    example:
      'resolve-library-id(libraryName="react")\nquery-docs(libraryId="/npm/react", query="useEffect cleanup")',
  },
  {
    icon: Brain,
    name: "mem-search",
    prefix: "mcp__plugin_pilot_mem-search__",
    purpose: "Persistent memory search",
    desc: "Recall decisions, discoveries, and context from past sessions. Three-layer workflow: search → timeline → get_observations for token efficiency.",
    example:
      'search(query="authentication flow", limit=5)\ntimeline(anchor=22865, depth_before=3)\nget_observations(ids=[22865, 22866])',
  },
  {
    icon: Globe,
    name: "web-search",
    prefix: "mcp__plugin_pilot_web-search__",
    purpose: "Web search + article fetching",
    desc: "Web search via DuckDuckGo, Bing, and Exa (no API keys needed). Also fetches GitHub READMEs, Linux.do articles, and other content sources.",
    example:
      'search(query="React Server Components 2026", limit=5)\nfetchGithubReadme(url="https://github.com/org/repo")',
  },
  {
    icon: Search,
    name: "grep-mcp",
    prefix: "mcp__plugin_pilot_grep-mcp__",
    purpose: "GitHub code search",
    desc: "Find real-world code examples from 1M+ public repositories. Search by literal code patterns, filter by language, repo, or file path. Supports regex.",
    example:
      'searchGitHub(query="useServerAction", language=["TypeScript"])\nsearchGitHub(query="FastMCP", language=["Python"])',
  },
  {
    icon: Globe,
    name: "web-fetch",
    prefix: "mcp__plugin_pilot_web-fetch__",
    purpose: "Full web page fetching",
    desc: "Fetch complete web pages via Playwright (handles JS-rendered content, no truncation). Fetches single or multiple URLs in one call.",
    example:
      'fetch_url(url="https://docs.example.com/api")\nfetch_urls(urls=["https://a.com", "https://b.com"])',
  },
];

const McpServersSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="mcp-servers"
      className="py-10 border-b border-border/50 scroll-mt-24"
    >
      <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
            <Globe className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-foreground">MCP Servers</h2>
            <p className="text-sm text-muted-foreground">
              External context always available to every session
            </p>
          </div>
        </div>

        <p className="text-sm text-muted-foreground mb-5 leading-relaxed">
          Five MCP servers are pre-configured and always available. They're
          lazy-loaded via <code className="text-primary">ToolSearch</code> to
          keep context lean — discovered and called on demand. Add your own in{" "}
          <code className="text-primary">.mcp.json</code>, then run{" "}
          <code className="text-primary">/sync</code> to generate documentation.
        </p>

        <div className="space-y-3">
          {mcpServers.map((server) => {
            const Icon = server.icon;
            return (
              <div
                key={server.name}
                className="rounded-xl border border-border/50 bg-card/30 overflow-hidden"
              >
                <div className="px-4 py-3 border-b border-border/30 flex items-start gap-3">
                  <Icon className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <code className="text-sm font-semibold text-foreground">
                        {server.name}
                      </code>
                      <span className="text-xs text-muted-foreground">
                        — {server.purpose}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                      {server.desc}
                    </p>
                  </div>
                </div>
                <div className="px-4 py-2.5 bg-background/40">
                  <pre className="text-xs text-muted-foreground font-mono whitespace-pre-wrap leading-relaxed">
                    {server.example}
                  </pre>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-4 rounded-xl p-4 border border-primary/20 bg-primary/5">
          <p className="text-xs text-muted-foreground leading-relaxed">
            <span className="text-primary font-medium">Tool selection:</span>{" "}
            Rules specify the preferred order — Probe MCP first for codebase
            questions, lib-docs for library API lookups, grep-mcp for production
            code examples, web-search for current information. The{" "}
            <code className="text-primary">tool_redirect.py</code> hook blocks
            the built-in WebSearch/WebFetch and redirects to these MCP
            alternatives.
          </p>
        </div>
      </div>
    </section>
  );
};

export default McpServersSection;
