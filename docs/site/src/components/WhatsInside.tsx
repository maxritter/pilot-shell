import {
  Workflow,
  Plug2,
  GitBranch,
  Lightbulb,
  Sparkles,
  Search,
  Smartphone,
  Terminal,
  Cpu,
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
    title: "Spec-Driven",
    description: "Plan → Implement → Verify",
    summary:
      "A structured workflow with human review gates, sequential TDD, mandatory verification, and independent code review. Loops back automatically if any check fails.",
  },
  {
    icon: Sparkles,
    title: "Customize & Share",
    description: "Create assets, share everywhere",
    summary:
      "Create and sharerules, commands, skills, and agents across machines via git, across teams via project repos, or org-wide via tracked repos. One source of truth for all your AI assets.",
  },
  {
    icon: Plug2,
    title: "MCP Servers",
    description: "Pre-configured external context",
    summary:
      "Library docs, web search, GitHub code search, and persistent memory — all pre-configured MCP servers. No setup, no API keys, always available.",
  },
  {
    icon: Smartphone,
    title: "Remote Control",
    description: "Control sessions from your phone",
    summary:
      "Start a task at your desk, monitor and steer from your phone. Connect via the Claude Mobile App or any browser — your full local environment stays available.",
  },
  {
    icon: Search,
    title: "Semantic Search",
    description: "Find code by intent, not keywords",
    summary:
      "Probe CLI indexes your codebase for instant semantic search. Find authentication flows, error handling patterns, or any concept in under 300ms.",
  },
  {
    icon: Lightbulb,
    title: "Reusable Skills",
    description: "Capture workflows as reusable knowledge",
    summary:
      "Build skills from any topic — /create-skill explores the codebase and creates well-structured skills interactively. Team knowledge compounds and stays consistent.",
  },
  {
    icon: GitBranch,
    title: "Isolated Workspaces",
    description: "Safe experimentation, clean git history",
    summary:
      "Spec work runs in isolated git worktrees. Review changes independently, squash merge when verified, or discard without touching your main branch.",
  },
  {
    icon: Cpu,
    title: "Headless Mode",
    description: "CI/CD, scripts, and automation",
    summary:
      "Run Pilot non-interactively with -p for CI/CD pipelines, PR reviews, and automated workflows. Full Claude Code CLI compatibility with license validation and Pilot plugin included.",
  },
  {
    icon: Terminal,
    title: "Console Dashboard",
    description: "Monitor, configure, and browse",
    summary:
      "Web-based dashboard for memory browsing, model configuration, team asset management, and real-time session notifications. Runs locally on port 41777.",
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
            A production-grade system — not a prompt template. Installs into any
            project and enforces quality automatically.
          </p>
        </div>

        {/* Feature Grid */}
        <div
          ref={gridRef}
          className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5"
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
