import { useInView } from "@/hooks/use-in-view";

const stack = [
  { name: "Python", detail: "3.12+" },
  { name: "TypeScript", detail: "Strict" },
  { name: "basedpyright", detail: "Type Checker" },
  { name: "ruff", detail: "Linter" },
  { name: "Vexor", detail: "Semantic Search" },
  { name: "MCP", detail: "Protocol" },
  { name: "Context7", detail: "Library Docs" },
  { name: "Playwright", detail: "E2E Testing" },
  { name: "gopls", detail: "Go LSP" },
  { name: "vtsls", detail: "TS LSP" },
];

const TechStack = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section className="py-10 lg:py-14 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`${inView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <p className="text-center text-xs text-muted-foreground/60 uppercase tracking-widest font-medium mb-6">
            Built With
          </p>

          <div className="flex flex-wrap justify-center gap-3">
            {stack.map((tech) => (
              <div
                key={tech.name}
                className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-border/40 bg-card/20
                  hover:border-primary/30 hover:bg-card/40 transition-all duration-200"
              >
                <span className="text-sm font-medium text-foreground">{tech.name}</span>
                <span className="text-[10px] text-muted-foreground">{tech.detail}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default TechStack;
