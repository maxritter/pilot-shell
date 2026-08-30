import {
  ArrowRight,
  Boxes,
  Cable,
  Layers3,
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
    title: "Automatic routing",
    description:
      "Describe the work normally. The matching design workflow loads in the background.",
  },
  {
    icon: Boxes,
    title: "Product context",
    description:
      "Existing components, tokens, content, themes, and interaction states remain authoritative.",
  },
  {
    icon: ScanSearch,
    title: "Runtime proof",
    description:
      "Rendered interactions, Impeccable hook evidence, and focused rechecks replace visual guesswork.",
  },
];

const designPackages = [
  {
    name: "Open Claude Design",
    title: "Design access and product judgment",
    description:
      "Conflict-aware Claude Design sync, codebase-grounded creation, design-system extraction, and structured review.",
    icon: Cable,
    href: "https://github.com/maxritter/open-claude-design",
  },
  {
    name: "Impeccable",
    title: "Refinement and deterministic checks",
    description:
      "Named refinements, supporting agents, edit and stop hooks, and context-aware detector findings.",
    icon: ScanSearch,
    href: "https://github.com/pbakaus/impeccable",
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
            Design joins the work automatically
          </h2>
          <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg">
            Pilot brings Open Claude Design and Impeccable together for Claude
            Code and Codex. Design starts from the real product, stays visually
            inspectable, and finishes with runtime proof.
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
              Two packages, built to work together
            </h3>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              Loaded only when the request is visual.
            </p>
          </div>

          <div className="divide-y divide-border/60">
            {designPackages.map((designPackage) => {
              const Icon = designPackage.icon;
              return (
                <a
                  key={designPackage.name}
                  href={designPackage.href}
                  target="_blank"
                  rel="noreferrer"
                  className="group grid gap-3 px-5 py-5 transition-colors hover:bg-primary/[0.04] sm:grid-cols-[2.5rem_minmax(0,1fr)_auto] sm:items-center sm:px-6"
                  aria-label={
                    "Open " + designPackage.name + " in a new tab"
                  }
                >
                  <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <Icon className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <span>
                    <span className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                      <span className="text-sm font-semibold text-primary">
                        {designPackage.name}
                      </span>
                      <span className="text-sm font-medium text-foreground">
                        {designPackage.title}
                      </span>
                    </span>
                    <span className="mt-1 block text-sm leading-relaxed text-muted-foreground">
                      {designPackage.description}
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
            How the automatic design stack works
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </a>
        </div>
      </div>
    </section>
  );
};

export default DesignExpertiseSection;
