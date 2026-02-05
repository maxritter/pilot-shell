import {
  Workflow,
  FileCode2,
  Plug2,
  ShieldCheck,
  Container,
  Infinity as InfinityIcon,
} from "lucide-react";
import { useInView } from "@/hooks/use-in-view";
import ImageModal from "@/components/ImageModal";

interface InsideItem {
  icon: React.ElementType;
  title: string;
  description: string;
  items: string[];
}

const insideItems: InsideItem[] = [
  {
    icon: InfinityIcon,
    title: "Endless Mode",
    description: "Never lose context mid-task",
    items: [
      "Seamless continuity across sessions",
      "Automatic handoffs at context limits",
      "Persistent memory bridges sessions",
      "Zero manual intervention required",
    ],
  },
  {
    icon: Workflow,
    title: "Spec-Driven Development",
    description: "Structured planning with verification",
    items: [
      "Plan → Approve → Implement → Verify",
      "Automatic TDD enforcement",
      "Code review before completion",
      "Loop until verified correct",
    ],
  },
  {
    icon: FileCode2,
    title: "Rules, Commands & Skills",
    description: "Best practices, customizable",
    items: [
      "12+ standard rules for quality",
      "/spec, /sync, /learn commands",
      "Online learning extracts patterns",
      "Team Vault via private Git repo",
    ],
  },
  {
    icon: Plug2,
    title: "Enhanced Context",
    description: "Memory, search & visual dashboard",
    items: [
      "Pilot Console at localhost:41777",
      "Persistent memory across sessions",
      "Semantic search (local embeddings)",
      "Context7 docs + GitHub code search",
    ],
  },
  {
    icon: ShieldCheck,
    title: "Quality Automation",
    description: "Enforced standards on every edit",
    items: [
      "TDD enforcer - tests before code",
      "Quality hooks for Python/TS/Go",
      "LSP integration (auto-installed)",
      "Status line with live metrics",
    ],
  },
  {
    icon: Container,
    title: "One-Command Installer",
    description: "Ready in minutes",
    items: [
      "Dev Container auto-setup",
      "Python, TypeScript & Go support",
      "Auto-updater included",
      "macOS, Linux, Windows (WSL2)",
    ],
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
          <p className="text-muted-foreground text-lg sm:text-xl max-w-2xl mx-auto">
            Everything you need to make Claude Code production-ready
          </p>
        </div>

        {/* Feature Grid */}
        <div
          ref={gridRef}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {insideItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={item.title}
                className={`group relative rounded-2xl p-6 border border-border/50 bg-card/30 backdrop-blur-sm
                  hover:border-primary/50 hover:bg-card/50 hover:shadow-lg hover:shadow-primary/5
                  hover:-translate-y-1 transition-all duration-300
                  ${gridInView ? `animate-fade-in-up ${animationDelays[index]}` : "opacity-0"}`}
              >
                {/* Icon and Title */}
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-11 h-11 bg-primary/10 rounded-xl flex items-center justify-center
                    group-hover:bg-primary/20 group-hover:scale-110 transition-all duration-300">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">
                      {item.title}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {item.description}
                    </p>
                  </div>
                </div>

                {/* Feature List */}
                <ul className="space-y-2 mt-4">
                  {item.items.map((listItem, i) => (
                    <li
                      key={i}
                      className="text-muted-foreground text-sm flex items-start gap-2"
                    >
                      <span className="text-primary mt-1 text-xs">▸</span>
                      <span className="group-hover:text-foreground/80 transition-colors duration-200">
                        {listItem}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* Subtle gradient overlay on hover */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
              </div>
            );
          })}
        </div>

        {/* Console Screenshot */}
        <div className={`mt-16 ${gridInView ? "animate-fade-in-up animation-delay-500" : "opacity-0"}`}>
          <div className="text-center mb-6">
            <h3 className="text-xl sm:text-2xl font-semibold text-foreground mb-2">
              Pilot Console
            </h3>
            <p className="text-muted-foreground text-sm sm:text-base">
              Visual dashboard at localhost:41777
            </p>
          </div>
          <div className="relative rounded-xl overflow-hidden border border-border/50 shadow-2xl shadow-primary/10 max-w-4xl mx-auto">
            <ImageModal
              src="/console.png"
              alt="Claude Pilot Console Dashboard"
              className="w-full rounded-xl"
            />
            <p className="text-xs text-muted-foreground text-center mt-2 mb-1">Click to enlarge</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhatsInside;
