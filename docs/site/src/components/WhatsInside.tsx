import {
  Workflow,
  FileCode2,
  Plug2,
  ShieldCheck,
  Infinity as InfinityIcon,
  Users,
  GitBranch,
  Lightbulb,
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
    description: "Plan → Approve → Implement → Verify",
    summary:
      "A structured workflow with human review gates, sequential TDD, mandatory verification, and independent code review. Loops back automatically if any check fails.",
  },
  {
    icon: ShieldCheck,
    title: "Quality Automation",
    description: "Hooks on every file edit",
    summary:
      "Auto-formatting, linting, and type checking for Python, TypeScript, and Go. TDD enforcer warns when code changes lack tests. Status line shows live session info.",
  },
  {
    icon: FileCode2,
    title: "Rules, Commands & Standards",
    description: "Rules · Commands · Standards",
    summary:
      "Production-tested best practices loaded every session. Coding standards activate by file type. Structured workflows via /spec, /sync, /learn. Team sharing via Console dashboard. Custom rules survive updates.",
  },
  {
    icon: InfinityIcon,
    title: "Persistent Memory",
    description: "Context carries across sessions",
    summary:
      "Decisions, discoveries, and debugging insights captured automatically. Pick up any project after days or weeks — Claude already knows your architecture and past work.",
  },
  {
    icon: Plug2,
    title: "Enhanced Context",
    description: "MCP servers + language servers",
    summary:
      "Library docs, persistent memory, web search, GitHub code search, and real-time LSP diagnostics — all pre-configured. No setup, no API keys, always available.",
  },
  {
    icon: Lightbulb,
    title: "Online Learning",
    description: "Grows smarter with every session",
    summary:
      "Extracts non-obvious debugging discoveries, workarounds, and tool integrations into reusable skills. Knowledge compounds — solutions found once are available forever.",
  },
  {
    icon: Users,
    title: "Team Sharing",
    description: "Share knowledge across your team",
    summary:
      "Push and pull rules, commands, and skills via a private Git repo. Automatic versioning, scoped installs, and works with GitHub, GitLab, and Bitbucket.",
  },
  {
    icon: GitBranch,
    title: "Isolated Workspaces",
    description: "Safe experimentation, clean git history",
    summary:
      "Spec work runs in isolated git worktrees. Review changes independently, squash merge when verified, or discard without touching your main branch.",
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
                className={`group relative rounded-2xl p-5 border border-border/50 bg-card/30 backdrop-blur-sm
                  hover:border-primary/50 hover:bg-card/50 hover:shadow-lg hover:shadow-primary/5
                  hover:-translate-y-1 transition-all duration-300
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
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default WhatsInside;
