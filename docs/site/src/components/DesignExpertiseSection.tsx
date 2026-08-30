import {
  ArrowRight,
  Boxes,
  Cable,
  Layers3,
  Palette,
  ScanSearch,
  type LucideIcon,
} from "lucide-react";

import { useInView } from "@/hooks/use-in-view";
import { cn } from "@/lib/utils";

interface ExpertiseLayer {
  icon: LucideIcon;
  title: string;
  description: string;
}

const expertiseLayers: ExpertiseLayer[] = [
  {
    icon: Layers3,
    title: "Path-gated rule",
    description:
      "Stable visual principles enter context only for UI components, markup, and styles.",
  },
  {
    icon: ScanSearch,
    title: "Compact skill router",
    description:
      "The request selects creation, system extraction, or review before detailed guidance loads.",
  },
  {
    icon: Boxes,
    title: "Focused reference",
    description:
      "Only the procedure needed for this task enters the working context. The other design material stays out.",
  },
];

const expertSkills = [
  {
    command: "/ui-design",
    title: "Create and redesign",
    description:
      "Product-grounded direction, wireframes, real variations, and repository-native prototypes.",
    icon: Palette,
  },
  {
    command: "/design-system",
    title: "Extract the system",
    description:
      "Traceable tokens, themes, components, variants, and states—without invented values.",
    icon: Boxes,
  },
  {
    command: "/ui-design-review",
    title: "Review and polish",
    description:
      "Accessibility, hierarchy, brand fidelity, interaction states, responsive themes, and runtime proof.",
    icon: ScanSearch,
  },
  {
    command: "/claude-design",
    title: "Use the real workspace",
    description:
      "On-demand project access and guarded sync—even from current Codex, without always-loaded MCP schemas.",
    icon: Cable,
  },
];

const DesignExpertiseSection = () => {
  const [sectionRef, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="design-expertise"
      tabIndex={-1}
      aria-labelledby="design-expertise-heading"
      className="relative px-4 py-16 focus:outline-none sm:px-6 lg:py-24"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
      <div
        ref={sectionRef}
        className={cn(
          "mx-auto grid max-w-6xl gap-10 lg:grid-cols-[minmax(0,0.9fr)_minmax(32rem,1.1fr)] lg:items-start",
          inView ? "animate-fade-in-up" : "opacity-0",
        )}
      >
        <div>
          <h2
            id="design-expertise-heading"
            className="max-w-2xl text-3xl font-bold text-foreground sm:text-4xl md:text-5xl"
          >
            Design expertise, without context blur
          </h2>
          <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg">
            Claude Code and Codex get product-design judgment modeled after
            Claude Design, engineered for real repositories and loaded only
            when the work needs it.
          </p>

          <div className="mt-8 border-y border-border/70">
            {expertiseLayers.map((layer) => {
              const Icon = layer.icon;
              return (
                <div
                  key={layer.title}
                  className="grid gap-3 border-b border-border/50 py-5 last:border-b-0 sm:grid-cols-[11rem_minmax(0,1fr)]"
                >
                  <div className="flex items-center gap-2.5 text-sm font-semibold text-foreground">
                    <Icon
                      className="h-4 w-4 text-primary"
                      aria-hidden="true"
                    />
                    {layer.title}
                  </div>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {layer.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="overflow-hidden rounded-lg border border-border/70 bg-card">
          <div className="border-b border-border/70 px-5 py-4 sm:px-6">
            <h3 className="text-base font-semibold text-foreground">
              Four expert lanes
            </h3>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              Use <code>/</code> in Claude Code and <code>$</code> on Codex.
            </p>
          </div>

          <div className="divide-y divide-border/60">
            {expertSkills.map((skill) => {
              const Icon = skill.icon;
              return (
                <a
                  key={skill.command}
                  href="/docs/workflows/ui-design"
                  className="group grid gap-3 px-5 py-5 transition-colors hover:bg-primary/[0.04] sm:grid-cols-[2.5rem_minmax(0,1fr)_auto] sm:items-center sm:px-6"
                  aria-label={"Learn more about " + skill.command}
                >
                  <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <Icon className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <span>
                    <span className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                      <code className="text-sm font-semibold text-primary">
                        {skill.command}
                      </code>
                      <span className="text-sm font-medium text-foreground">
                        {skill.title}
                      </span>
                    </span>
                    <span className="mt-1 block text-sm leading-relaxed text-muted-foreground">
                      {skill.description}
                    </span>
                  </span>
                  <ArrowRight
                    className="hidden h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-primary sm:block"
                    aria-hidden="true"
                  />
                </a>
              );
            })}
          </div>

          <a
            href="/docs/workflows/ui-design"
            className="flex items-center justify-between border-t border-border/70 px-5 py-4 text-sm font-medium text-primary transition-colors hover:bg-primary/[0.04] sm:px-6"
          >
            How the context architecture works
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </a>
        </div>
      </div>
    </section>
  );
};

export default DesignExpertiseSection;
