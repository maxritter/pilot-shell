import { CreditCard, Monitor, CheckCircle2, Terminal } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const subscriptionTiers = [
  {
    name: "Max 5x",
    audience: "Solo — moderate usage",
    note: "Good for part-time or focused coding sessions",
  },
  {
    name: "Max 20x",
    audience: "Solo — heavy usage",
    note: "Recommended for full-time AI-assisted development",
  },
  {
    name: "Team Premium",
    audience: "Teams",
    note: "6.25× usage per member + SSO, admin tools, billing management",
  },
  {
    name: "Enterprise",
    audience: "Companies",
    note: "For organizations with compliance, procurement, or security requirements",
  },
];

const systemReqs = [
  {
    platform: "macOS",
    note: "10.15 Catalina or later, Apple Silicon and Intel",
  },
  {
    platform: "Linux",
    note: "Debian, Ubuntu, RHEL-based distros, and most others",
  },
  { platform: "Windows", note: "WSL2 required — native Windows not supported" },
];

const PrerequisitesSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="prerequisites"
      className="py-10 border-b border-border/50 scroll-mt-24"
    >
      <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
            <CreditCard className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-foreground">Prerequisites</h2>
            <p className="text-sm text-muted-foreground">
              What you need before installing Pilot
            </p>
          </div>
        </div>

        <div className="rounded-xl p-4 border border-primary/20 bg-primary/5 mb-6">
          <div className="flex items-center gap-2 mb-2">
            <Terminal className="h-4 w-4 text-primary" />
            <h3 className="font-semibold text-foreground text-sm">
              Claude Code (Required)
            </h3>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Pilot Shell installs <span className="text-foreground font-medium">on top of Claude Code</span> — you must install it first.
            Install via npm:{" "}
            <code className="text-primary bg-primary/10 px-1 py-0.5 rounded">npm install -g @anthropic-ai/claude-code</code>
            {" "}or use the{" "}
            <a
              href="https://docs.anthropic.com/en/docs/claude-code/setup"
              className="text-primary hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              native installer
            </a>
            . Pilot Shell does not install or update Claude Code for you.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <CreditCard className="h-4 w-4 text-primary" />
              <h3 className="font-semibold text-foreground text-sm">
                Claude Subscription
              </h3>
            </div>
            <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
              Pilot enhances Claude Code — it doesn't replace it. You need an
              active Claude subscription. Solo developers, teams, and enterprise
              organizations are all supported.
            </p>
            <div className="space-y-2">
              {subscriptionTiers.map((tier) => (
                <div
                  key={tier.name}
                  className="rounded-xl p-3 border border-border/50 bg-card/30"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-foreground">
                      {tier.name}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {tier.audience}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{tier.note}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <Monitor className="h-4 w-4 text-primary" />
              <h3 className="font-semibold text-foreground text-sm">
                System Requirements
              </h3>
            </div>
            <p className="text-xs text-muted-foreground mb-3 leading-relaxed">
              Pilot installs once and works across all your projects. Each
              project can have its own{" "}
              <code className="text-primary">.claude/</code> rules and skills.
            </p>
            <div className="space-y-2 mb-4">
              {systemReqs.map((req) => (
                <div
                  key={req.platform}
                  className="rounded-xl p-3 border border-border/50 bg-card/30 flex items-start gap-3"
                >
                  <span className="text-sm font-medium text-foreground w-20 flex-shrink-0">
                    {req.platform}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {req.note}
                  </span>
                </div>
              ))}
            </div>
            <div className="rounded-xl p-3 border border-primary/20 bg-primary/5">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-primary flex-shrink-0 mt-0.5" />
                <p className="text-xs text-muted-foreground leading-relaxed">
                  <span className="text-primary font-medium">
                    Dev Container option:
                  </span>{" "}
                  A pre-configured isolated environment with all tools ready. No
                  system conflicts, works on any OS.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PrerequisitesSection;
