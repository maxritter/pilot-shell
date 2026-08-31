import { Bot, Terminal } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";
import IconTile from "@/components/IconTile";

const MonoName = ({ children }: { children: string }) => (
  <span className="font-mono text-xs">{children}</span>
);

const AgentsSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      aria-label="Supported agents"
      className="py-16 lg:py-24 px-4 sm:px-6 relative"
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`grid md:grid-cols-2 gap-5 ${
            inView ? "animate-fade-in-up" : "opacity-0"
          }`}
        >
          <div className="rounded-lg border border-border/50 bg-card p-6">
            <div className="flex items-center gap-3 mb-3">
              <IconTile icon={Bot} sizeClass="w-11 h-11" iconClass="h-[22px] w-[22px]" />
              <div>
                <h2 className="text-base font-semibold text-foreground">
                  Claude Code
                </h2>
                <p className="text-[11.5px] text-muted-foreground">
                  Primary — full feature coverage
                </p>
              </div>
            </div>
            <p className="text-[13px] leading-relaxed text-muted-foreground">
              All workflows, lifecycle hooks, model switching (Opus plans,
              Sonnet executes), language servers, and the complete Console
              integration. Requires a Claude Max, Team Premium, or Enterprise
              subscription.
            </p>
          </div>

          <div className="rounded-lg border border-border/50 bg-card p-6">
            <div className="flex items-center gap-3 mb-3">
              <IconTile
                icon={Terminal}
                sizeClass="w-11 h-11"
                iconClass="h-[22px] w-[22px]"
              />
              <div>
                <h2 className="text-base font-semibold text-foreground">Codex</h2>
                <p className="text-[11.5px] text-muted-foreground">
                  All workflows, fewer platform features
                </p>
              </div>
            </div>
            <p className="text-[13px] leading-relaxed text-muted-foreground">
              Via Codex CLI or the ChatGPT desktop app —{" "}
              <MonoName>$prd</MonoName>, <MonoName>$spec</MonoName>,{" "}
              <MonoName>$build</MonoName>, and <MonoName>$fix</MonoName> are
              explicit-only; native /goal, safety settings, and bounded
              subagents stay available. Requires an OpenAI Plus, Pro, Business,
              or Enterprise subscription.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AgentsSection;
