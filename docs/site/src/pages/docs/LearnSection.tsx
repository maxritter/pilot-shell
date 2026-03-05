import { Brain, CheckCircle2 } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const autoTriggers = [
  "Non-obvious debugging solution discovered after 10+ minutes",
  "Workaround for a library limitation found during work",
  "Undocumented tool or API integration pattern",
  "Multi-step workflow that will likely recur",
  "External service query pattern (Jira, GitHub, Confluence)",
];

const whatGetsExtracted = [
  "The problem context and why standard approaches failed",
  "Step-by-step solution with exact commands and code",
  "When to apply this knowledge in future sessions",
  "Edge cases and caveats to watch out for",
];

const LearnSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="learn"
      className="py-10 border-b border-border/50 scroll-mt-24"
    >
      <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
            <Brain className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-foreground">
              /learn — Online Learning
            </h2>
            <p className="text-sm text-muted-foreground">
              Capture non-obvious discoveries as reusable skills
            </p>
          </div>
        </div>

        <p className="text-sm text-muted-foreground mb-5 leading-relaxed">
          When Pilot solves a non-obvious problem — a tricky debugging session,
          an undocumented API pattern, a workaround for a framework quirk —{" "}
          <code className="text-primary bg-primary/10 px-1.5 py-0.5 rounded">
            /learn
          </code>{" "}
          extracts that knowledge into a reusable skill. Future sessions load
          and apply it automatically. Triggered automatically when relevant, or
          invoked manually after significant investigations.
        </p>

        <div className="grid sm:grid-cols-2 gap-5 mb-5">
          <div>
            <h3 className="font-semibold text-foreground text-sm mb-3">
              Automatic trigger conditions
            </h3>
            <div className="space-y-1.5">
              {autoTriggers.map((t) => (
                <div
                  key={t}
                  className="flex items-start gap-2 text-xs text-muted-foreground"
                >
                  <CheckCircle2 className="h-3.5 w-3.5 text-primary flex-shrink-0 mt-0.5" />
                  <span>{t}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-foreground text-sm mb-3">
              What gets extracted into a skill
            </h3>
            <div className="space-y-1.5">
              {whatGetsExtracted.map((item) => (
                <div
                  key={item}
                  className="flex items-start gap-2 text-xs text-muted-foreground"
                >
                  <CheckCircle2 className="h-3.5 w-3.5 text-primary flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-background/80 rounded-lg p-3 font-mono text-sm border border-border/50 text-muted-foreground mb-4">
          <div className="text-xs font-sans text-muted-foreground/70 mb-2">
            Manual invocation:
          </div>
          <div>
            <span className="text-primary">&gt;</span> /learn "Extract the
            debugging workflow we used for the race condition"
          </div>
          <div>
            <span className="text-primary">&gt;</span> /learn "Save the
            PostgreSQL connection pooling pattern we discovered"
          </div>
        </div>

        <div className="rounded-xl p-3 border border-primary/20 bg-primary/5">
          <p className="text-xs text-muted-foreground leading-relaxed">
            <span className="text-primary font-medium">
              Skills are plain markdown files
            </span>{" "}
            stored in <code className="text-primary">.claude/skills/</code>.
            They're loaded on-demand when relevant, created by{" "}
            <code className="text-primary">/learn</code>, and shareable across
            your team via the <strong>Teams dashboard</strong>. Skills
            follow a frontmatter format that describes when they apply.
          </p>
        </div>
      </div>
    </section>
  );
};

export default LearnSection;
