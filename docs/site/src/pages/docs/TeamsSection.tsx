import { Users, CheckCircle2 } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const teamsFeatures = [
  {
    title: "Console Dashboard",
    desc: "Browse, push, install, and remove assets from a visual Teams page",
  },
  {
    title: "Private Git Repo",
    desc: "Use any Git repo — GitHub, GitLab, Bitbucket, public or private",
  },
  {
    title: "Push & Install",
    desc: "Push local assets to the repo, install team assets to your project",
  },
  {
    title: "Versioned",
    desc: "Assets auto-increment versions (v1, v2, v3…) on each push",
  },
];

const assetTypes = [
  {
    type: "rule",
    path: ".claude/rules/<name>.md",
    desc: "Guidelines loaded every session",
  },
  {
    type: "skill",
    path: ".claude/skills/<name>/",
    desc: "Reusable knowledge from /learn",
  },
  {
    type: "command",
    path: ".claude/commands/<name>.md",
    desc: "Slash commands (/mycommand)",
  },
  {
    type: "agent",
    path: ".claude/agents/<name>.md",
    desc: "Sub-agent definitions",
  },
];

const TeamsSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="teams"
      className="py-10 border-b border-border/50 scroll-mt-24"
    >
      <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
            <Users className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-foreground">
              Teams — Asset Sharing
            </h2>
            <p className="text-sm text-muted-foreground">
              Share rules, commands, and skills across your team via the Console
              dashboard
            </p>
          </div>
        </div>

        <p className="text-sm text-muted-foreground mb-5 leading-relaxed">
          The Teams page in the Pilot Console lets your team share custom
          assets — rules, skills, commands, and agents — via a private Git
          repository. Browse assets, push local files, install team assets, and
          manage versions — all from a visual dashboard. No CLI needed.
        </p>

        <div className="grid sm:grid-cols-2 gap-3 mb-6">
          {teamsFeatures.map((f) => (
            <div
              key={f.title}
              className="rounded-xl p-4 border border-border/50 bg-card/30"
            >
              <h3 className="font-semibold text-foreground text-sm mb-1">
                {f.title}
              </h3>
              <p className="text-xs text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>

        <h3 className="font-semibold text-foreground text-sm mb-2">Setup</h3>
        <p className="text-xs text-muted-foreground mb-3">
          Open the Console dashboard and navigate to the Teams page. Click{" "}
          <strong>Configure Repository</strong> to connect your team's Git repo.
          Or use the CLI:
        </p>
        <div className="bg-background/80 rounded-lg p-3 font-mono text-xs border border-border/50 text-muted-foreground mb-5">
          <div className="text-muted-foreground/60 mb-1">
            # Initialize with your team's private repo
          </div>
          <div>
            <span className="text-primary">$</span> sx init --type git
            --repo-url git@github.com:org/team-repo.git
          </div>
        </div>

        <h3 className="font-semibold text-foreground text-sm mb-3">
          Shareable Asset Types
        </h3>
        <div className="rounded-xl border border-border/50 overflow-hidden mb-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50 bg-card/40">
                <th className="text-left px-4 py-2 text-xs font-semibold text-muted-foreground">
                  Type
                </th>
                <th className="text-left px-4 py-2 text-xs font-semibold text-muted-foreground">
                  Source Path
                </th>
                <th className="text-left px-4 py-2 text-xs font-semibold text-muted-foreground hidden sm:table-cell">
                  Purpose
                </th>
              </tr>
            </thead>
            <tbody>
              {assetTypes.map((a, i) => (
                <tr
                  key={a.type}
                  className={`border-b border-border/50 last:border-0 ${i % 2 === 0 ? "" : "bg-card/20"}`}
                >
                  <td className="px-4 py-2.5">
                    <code className="text-xs text-primary">{a.type}</code>
                  </td>
                  <td className="px-4 py-2.5 text-xs text-muted-foreground font-mono">
                    {a.path}
                  </td>
                  <td className="px-4 py-2.5 text-xs text-muted-foreground hidden sm:table-cell">
                    {a.desc}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="grid sm:grid-cols-2 gap-3">
          <div className="rounded-xl p-4 border border-primary/30 bg-primary/5">
            <h4 className="font-medium text-foreground text-sm mb-1">
              Project-scoped
              <span className="text-xs text-primary font-medium ml-2">
                Recommended
              </span>
            </h4>
            <p className="text-xs text-muted-foreground">
              Assets install to the project's{" "}
              <code className="text-primary">.claude/</code>. Stays with the
              repo, visible to all contributors.
            </p>
          </div>
          <div className="rounded-xl p-4 border border-border/50 bg-card/30">
            <h4 className="font-medium text-foreground text-sm mb-1">Global</h4>
            <p className="text-xs text-muted-foreground">
              Assets install to <code className="text-primary">~/.claude/</code>{" "}
              and apply across all your projects on this machine.
            </p>
          </div>
        </div>

        <div className="mt-4 rounded-xl p-3 border border-border/50 bg-card/30">
          <div className="flex items-start gap-2">
            <CheckCircle2 className="h-3.5 w-3.5 text-primary flex-shrink-0 mt-0.5" />
            <p className="text-xs text-muted-foreground leading-relaxed">
              Assets are auto-versioned — each push creates v1, v2, v3…
              Teammates install the latest version from the Teams dashboard.
              Background sync keeps everything up to date when you open the
              page.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TeamsSection;
