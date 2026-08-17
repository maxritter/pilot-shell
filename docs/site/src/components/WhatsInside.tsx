import {
  Workflow,
  Plug2,
  GitBranch,
  Sparkles,
  Search,
  Terminal,
  DollarSign,
  SlidersHorizontal,
  Users,
  ArrowRight,
} from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

interface InsideItem {
  icon: React.ElementType;
  title: string;
  description: string;
  summary: string;
  href: string;
}

const insideItems: InsideItem[] = [
  {
    icon: Workflow,
    title: "Workflow-Driven Development",
    description: "Plan, build, fix, and verify",
    summary:
      "Use /prd for product discovery, /spec for an approved task list, /build for a judged goal loop, and /fix for defects. Development workflows carry TDD and verification through to evidence.",
    href: "/docs/workflows/spec",
  },
  {
    icon: GitBranch,
    title: "Context Engineering",
    description: "Keep your context window lean",
    summary:
      "Curated rules for best practices, TDD, debugging, and verification. Language- and architecture-specific standards for Python, TypeScript, Go, .NET, Blazor, frontend, and backend \u2014 modular, only what\u2019s relevant loads.",
    href: "/docs/features/context-optimization",
  },
  {
    icon: Terminal,
    title: "Hooks & Quality",
    description: "Quality checks around the workflow",
    summary:
      "Claude Code's lifecycle hooks run edit-time quality checks and preserve active workflow state. Pilot workflows require fresh tests and real execution evidence before completion.",
    href: "/docs/features/hooks",
  },
  {
    icon: Plug2,
    title: "MCP Servers",
    description: "Pre-configured, zero setup",
    summary:
      "Seven MCP servers ship pre-configured for both Claude Code and Codex: library docs, web search, persistent memory, code graphs, hybrid code search (Semble), GitHub code search, and web fetching.",
    href: "/docs/features/mcp-servers",
  },
  {
    icon: Search,
    title: "Semantic Search",
    description: "Find code by intent, not keywords",
    summary:
      "Search the codebase by intent, not keywords. AST-aware extraction pulls exactly what\u2019s needed. Call-graph tracing maps blast radius before you change anything. Sub-300ms results.",
    href: "/docs/features/open-source-tools",
  },
  {
    icon: DollarSign,
    title: "Cost Optimization",
    description: "Right model, right task, visible spend",
    summary:
      "Claude Code can switch models after /spec plan approval. A CLI proxy compresses tool output by 60\u201390%, while the Console tracks daily cost and trends.",
    href: "/docs/features/model-routing",
  },
  {
    icon: Sparkles,
    title: "Extensions & Sharing",
    description: "Skills, rules, commands, agents",
    summary:
      "Create custom skills and rules with built-in generators. Share them across machines and teams through a connected git repo. Seven extension types at four scopes, managed in the Console UI.",
    href: "/docs/features/extensions",
  },
  {
    icon: Users,
    title: "Team Memories",
    description: "Share the why, not just the code",
    summary:
      "Store a project's captured decisions and discoveries in the repo itself, so git carries them to every contributor. Teammates' context loads at session start on Claude Code and Codex — no cloud, no clock, you review the diff and commit.",
    href: "/docs/features/team-memories",
  },
  {
    icon: SlidersHorizontal,
    title: "Customization",
    description: "Modify what Pilot auto-installs",
    summary:
      "Tune workflows, rules, hooks, agents, and MCP servers. Share changes through a team git repo or local directory.",
    href: "/docs/features/customization",
  },
];

const WhatsInside = () => {
  const [headerRef, headerInView] = useInView<HTMLDivElement>();
  const [gridRef, gridInView] = useInView<HTMLDivElement>();

  const animationDelays = [
    "animation-delay-0",
    "animation-delay-100",
    "animation-delay-200",
    "animation-delay-300",
    "animation-delay-400",
    "animation-delay-500",
    "animation-delay-0",
    "animation-delay-100",
    "animation-delay-200",
  ];

  return (
    <section id="features" className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        {/* Header */}
        <div
          ref={headerRef}
          className={`text-center mb-16 ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            What's Inside
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
            One install for Claude Code, Codex CLI, and Codex in the ChatGPT
            app. Workflows, context, quality, memory, and search in one system.
          </p>
        </div>

        {/* Feature Grid */}
        <div
          ref={gridRef}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-5"
        >
          {insideItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <a
                key={item.title}
                href={item.href}
                className={`group relative rounded-lg p-5 border border-border/50 bg-card
                  hover:border-primary/50 hover:bg-card
                  transition-all duration-300 block
                  ${gridInView ? `animate-fade-in-up ${animationDelays[index]}` : "opacity-0"}`}
                aria-label={`Learn more about ${item.title}`}
              >
                {/* Icon and Title */}
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center
                    group-hover:bg-primary/20 group-hover:scale-110 transition-all duration-300"
                  >
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-foreground">
                      {item.title}
                    </h3>
                    <p className="text-[11px] text-muted-foreground">
                      {item.description}
                    </p>
                  </div>
                </div>

                {/* Summary */}
                <p className="text-muted-foreground text-xs leading-relaxed mt-3 group-hover:text-foreground/80 transition-colors duration-200">
                  {item.summary}
                </p>

                {/* Learn more link */}
                <div className="mt-3 flex items-center gap-1 text-xs text-primary group-hover:underline transition-colors">
                  <span>Learn more</span>
                  <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
                </div>

                {/* Subtle gradient overlay on hover */}
                <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
              </a>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default WhatsInside;
