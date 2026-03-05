import { useState } from "react";
import { useInView } from "@/hooks/use-in-view";
import ImageModal from "@/components/ImageModal";

const consoleSlides = [
  {
    label: "Dashboard",
    src: "/console/dashboard.png",
    alt: "Console Dashboard — stats, workspace status, and spec progress",
    desc: "Workspace status, active sessions, spec progress, git info, and recent activity — all at a glance.",
  },
  {
    label: "Settings",
    src: "/console/settings.png",
    alt: "Settings view — model selection per command, sub-agent, and session with defaults",
    desc: "Choose models per command and sub-agent. Toggle extended context (1M tokens) globally.",
  },
  {
    label: "Specifications",
    src: "/console/specification.png",
    alt: "Specification view — plan details, task progress, and implementation notes",
    desc: "All spec plans with task progress, phase tracking, and iteration history.",
  },
  {
    label: "Memories",
    src: "/console/memories.png",
    alt: "Memories view — browsable observation cards with type filters",
    desc: "Decisions, discoveries, and bugfixes captured across sessions — searchable with type filters.",
  },
  {
    label: "Sessions",
    src: "/console/sessions.png",
    alt: "Sessions view — active sessions with observation and prompt counts",
    desc: "Active and past sessions with observation counts, duration, and project context.",
  },
  {
    label: "Usage",
    src: "/console/usage.png",
    alt: "Usage view — daily costs, token charts, and model routing strategy",
    desc: "Daily token costs, model routing breakdown, and usage trends over time.",
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
            <div className="rounded-xl overflow-hidden border border-border/50 shadow-2xl shadow-primary/10">
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

            {/* Thumbnail strip */}
            <div className="grid grid-cols-6 gap-2 sm:gap-3 mt-3">
              {consoleSlides.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setIndex(i)}
                  className={`group/thumb relative rounded-lg overflow-hidden border-2 transition-all duration-200
                    ${
                      i === index
                        ? "border-primary shadow-md shadow-primary/20"
                        : "border-transparent opacity-60 hover:opacity-100 hover:border-border"
                    }`}
                >
                  <img
                    src={s.src}
                    alt={s.label}
                    className="w-full rounded-md"
                  />
                  <div
                    className={`absolute inset-x-0 bottom-0 py-1 text-[10px] sm:text-xs font-medium text-center
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
