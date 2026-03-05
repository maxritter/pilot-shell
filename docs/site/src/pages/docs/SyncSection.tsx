import { RefreshCw, CheckCircle2 } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const syncPhases = [
  {
    phase: 0,
    action: "Load reference guidelines, output locations, error handling",
  },
  { phase: 1, action: "Read existing rules and standards from .claude/" },
  {
    phase: 2,
    action: "Build Vexor semantic search index (first run may take 5–15 min)",
  },
  { phase: 3, action: "Explore codebase with Vexor/Grep to find patterns" },
  { phase: 4, action: "Compare discovered vs documented patterns" },
  { phase: 5, action: "Sync/update project rule with tech stack and commands" },
  { phase: 6, action: "Sync MCP server documentation" },
  { phase: 7, action: "Update existing custom skills that have changed" },
  {
    phase: 8,
    action: "Discover and document new undocumented patterns as rules",
  },
  { phase: 9, action: "Create new skills via /learn command" },
  { phase: 10, action: "Report summary of all changes made" },
];

const whenToRun = [
  "After installing Pilot in a new project",
  "After making significant architectural changes",
  "When adding new MCP servers to .mcp.json",
  "Before starting a complex /spec task on an unfamiliar codebase",
  "After onboarding to a project you didn't write",
];

const SyncSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section id="sync" className="py-10 border-b border-border/50 scroll-mt-24">
      <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
            <RefreshCw className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-foreground">
              /sync — Codebase Sync
            </h2>
            <p className="text-sm text-muted-foreground">
              Learn your existing codebase and sync rules with it
            </p>
          </div>
        </div>

        <p className="text-sm text-muted-foreground mb-5 leading-relaxed">
          Run{" "}
          <code className="text-primary bg-primary/10 px-1.5 py-0.5 rounded">
            /sync
          </code>{" "}
          to explore your project structure, build a semantic search index,
          discover your conventions and undocumented patterns, update project
          documentation, and create new custom skills. This is how Pilot adapts
          to your project — not the other way around. Run it once initially,
          then any time your codebase changes significantly.
        </p>

        <div className="bg-background/80 rounded-lg p-3 font-mono text-sm border border-border/50 text-muted-foreground mb-6">
          <div>
            <span className="text-primary">$</span> pilot
          </div>
          <div className="pl-2">
            <span className="text-primary">&gt;</span> /sync
          </div>
        </div>

        <h3 className="font-semibold text-foreground text-sm mb-3">
          What /sync does — 11 phases (zero-indexed)
        </h3>
        <div className="rounded-xl border border-border/50 overflow-hidden mb-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50 bg-card/40">
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-muted-foreground w-16">
                  Phase
                </th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-muted-foreground">
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {syncPhases.map((p, i) => (
                <tr
                  key={p.phase}
                  className={`border-b border-border/50 last:border-0 ${i % 2 === 0 ? "" : "bg-card/20"}`}
                >
                  <td className="px-4 py-2.5 text-xs font-mono text-primary font-bold">
                    {p.phase}
                  </td>
                  <td className="px-4 py-2.5 text-xs text-muted-foreground">
                    {p.action}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="rounded-xl p-4 border border-primary/20 bg-primary/5">
          <h3 className="font-semibold text-foreground text-sm mb-3">
            When to run /sync
          </h3>
          <div className="grid sm:grid-cols-2 gap-1.5">
            {whenToRun.map((when) => (
              <div
                key={when}
                className="flex items-start gap-2 text-xs text-muted-foreground"
              >
                <CheckCircle2 className="h-3.5 w-3.5 text-primary flex-shrink-0 mt-0.5" />
                <span>{when}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default SyncSection;
