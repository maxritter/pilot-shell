import { useState } from "react";
import { useInView } from "@/hooks/use-in-view";
import ImageModal from "@/components/ImageModal";

const consoleSlides = [
  {
    label: "Dashboard",
    src: "/console/dashboard.png",
    alt: "Console Dashboard — grouped stats, workspace status, and spec progress",
    desc: "Grouped stats for memory, specifications, and extensions. Workspace cards for usage, git, specs, and worker.",
  },
  {
    label: "Specifications",
    src: "/console/specifications.png",
    alt: "Specification view — plan details, task progress, and phase tracking",
    desc: "All spec plans with task progress, phase tracking, and iteration history.",
  },
  {
    label: "Extensions",
    src: "/console/extensions.png",
    alt: "Extensions view — local, plugin, and remote extensions with team sharing",
    desc: "Browse, edit, and share extensions. Team sharing via git with push, pull, and diff. Plugin extensions auto-discovered.",
  },
  {
    label: "Changes",
    src: "/console/changes.png",
    alt: "Changes view — git diff, staged files, and branch info",
    desc: "Git changes, staged files, and diff viewer with branch and worktree context.",
  },
  {
    label: "Memories",
    src: "/console/memories.png",
    alt: "Memories view — captured decisions and patterns with semantic search",
    desc: "Decisions, discoveries, and patterns captured automatically. Semantic search across all memories.",
  },
  {
    label: "Sessions",
    src: "/console/sessions.png",
    alt: "Sessions view — active sessions with observation and prompt counts",
    desc: "Active and past sessions with observation counts, duration, and expandable timelines.",
  },
  {
    label: "Usage",
    src: "/console/usage.png",
    alt: "Usage view — daily costs, token charts, and model routing",
    desc: "Daily token costs, model routing breakdown, and usage trends over time.",
  },
  {
    label: "Settings",
    src: "/console/settings.png",
    alt: "Settings view — model selection per command, spec workflow toggles",
    desc: "Choose models per command and sub-agent. Spec workflow toggles and reviewer configuration.",
  },
  {
    label: "Help",
    src: "/console/help.png",
    alt: "Help view — embedded documentation and quick-start guides",
    desc: "Embedded documentation from pilot-shell.com — full technical reference without leaving the Console.",
  },
];

const ConsoleSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();
  const [index, setIndex] = useState(0);
  const slide = consoleSlides[index];

  return (
    <section id="console" className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`${inView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
              Pilot Shell Console
            </h2>
            <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
              Real-time notifications, session management, usage analytics, and
              semantic search.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            {/* Main image */}
            <div className="rounded-xl overflow-hidden border border-border/50">
              <ImageModal
                src={slide.src}
                alt={slide.alt}
                className="w-full rounded-xl"
              />
            </div>

            {/* Active view description */}
            <div className="mt-3 text-center">
              <p className="text-sm text-muted-foreground transition-all duration-200">
                <span className="font-medium text-foreground">
                  {slide.label}
                </span>
                {" — "}
                {slide.desc}
              </p>
            </div>

            {/* Thumbnail strip — 9 tabs */}
            <div className="grid grid-cols-9 gap-1.5 sm:gap-2 mt-3">
              {consoleSlides.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setIndex(i)}
                  className={`group/thumb relative rounded-lg overflow-hidden border-2 transition-all duration-200
                    ${
                      i === index
                        ? "border-primary"
                        : "border-transparent opacity-60 hover:opacity-100 hover:border-border"
                    }`}
                >
                  <img
                    src={s.src}
                    alt={s.label}
                    className="w-full rounded-md"
                  />
                  <div
                    className={`absolute inset-x-0 bottom-0 py-0.5 text-[8px] sm:text-[10px] font-medium text-center
                    ${
                      i === index
                        ? "bg-primary/90 text-primary-foreground"
                        : "bg-background/80 text-muted-foreground group-hover/thumb:text-foreground"
                    }`}
                  >
                    {s.label}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ConsoleSection;
