import {
  Workflow,
  Plug2,
  GitBranch,
  Sparkles,
  Search,
  Terminal,
  Eye,
  DollarSign,
} from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

interface InsideItem {
  icon: React.ElementType;
  title: string;
  description: string;
  summary: string;
}

const insideItems: InsideItem[] = [
  {
    icon: Workflow,
    title: "Spec-Driven Development",
    description: "Replaces plan mode",
    summary:
      "/spec plans features and bugfixes, gets your approval, implements each task with TDD, then verifies with automated code review. Loops back if any check fails.",
  },
  {
    icon: GitBranch,
    title: "Context Engineering",
    description: "Keep your context window lean",
    summary:
      "RTK compresses CLI output by 60\u201390%. Rules load only for matching file types. When compaction fires, hooks preserve and restore plan state automatically.",
  },
  {
    icon: Terminal,
    title: "Quality Hooks & Testing",
    description: "Deterministic checks on every edit",
    summary:
      "15 hooks across 7 lifecycle events. Auto-lint, format, and type-check every file edit. TDD enforcer warns when implementation is written without a failing test.",
  },
  {
    icon: Plug2,
    title: "MCP Servers",
    description: "Pre-configured, no API keys",
    summary:
      "Library docs, web search, GitHub code search, persistent memory, web page fetching, and code knowledge graphs. Six servers installed and ready to use.",
  },
  {
    icon: Eye,
    title: "Language Servers",
    description: "Real-time diagnostics on every edit",
    summary:
      "Python (basedpyright), TypeScript (vtsls), Go (gopls). Auto-installed and auto-configured. Hooks catch formatting; LSPs provide type-level intelligence.",
  },
  {
    icon: Search,
    title: "Semantic Search",
    description: "Find code by intent, not keywords",
    summary:
      "Probe CLI indexes your codebase for intent-based search and AST-aware extraction. codebase-memory-mcp traces call graphs and maps blast radius. Sub-300ms.",
  },
  {
    icon: DollarSign,
    title: "Cost Optimization",
    description: "Right model, right task, visible spend",
    summary:
      "Smart model routing: Opus for planning, Sonnet for implementation. RTK saves 60\u201390% on CLI token output. Usage tracking in Console shows daily cost and trends.",
  },
  {
    icon: Sparkles,
    title: "Extensions & Sharing",
    description: "Skills, rules, commands, agents",
    summary:
      "Create with /create-skill and /setup-rules. Share across machines via git, across teams via project repos. Seven extension types at four scopes \u2014 managed in Console.",
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
            One install command. Everything below is specific to Pilot Shell
            — not a repackage of Claude Code features.
          </p>
        </div>

        {/* Feature Grid */}
        <div
          ref={gridRef}
          className="grid md:grid-cols-2 lg:grid-cols-4 gap-5"
        >
          {insideItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={item.title}
                className={`group relative rounded-lg p-5 border border-border/50 bg-card
                  hover:border-primary/50 hover:bg-card hover:border-primary/50
                  transition-all duration-300
                  ${gridInView ? `animate-fade-in-up ${animationDelays[index]}` : "opacity-0"}`}
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

                {/* Subtle gradient overlay on hover */}
                <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default WhatsInside;
