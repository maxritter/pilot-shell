import { Users, CheckCircle2, Lock } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const teamsFeatures = [
  {
    title: "Teams Dashboard",
    desc: "Browse, push, and manage shared assets directly in the Console UI",
  },
  {
    title: "Push & Pull",
    desc: "Share custom rules, skills, and commands with teammates via Git vault",
  },
  {
    title: "Vault Setup",
    desc: "Configure your team vault (Git repo, local path, or Skills.new) from the UI",
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
  { type: "hook", path: "Hook scripts", desc: "Quality enforcement hooks" },
  {
    type: "mcp",
    path: "MCP server configs",
    desc: "External tool integrations",
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
            <h2 className="text-xl font-bold text-foreground">Teams</h2>
            <p className="text-sm text-muted-foreground">
              Share assets across your team via the Console dashboard
            </p>
          </div>
        </div>

        <div className="rounded-xl p-3 border border-indigo-500/30 bg-indigo-500/5 mb-5 flex items-center gap-2">
          <Lock className="h-4 w-4 text-indigo-500 flex-shrink-0" />
          <p className="text-xs text-muted-foreground">
            <span className="font-semibold text-indigo-400">
              Team plan feature.
            </span>{" "}
            Teams functionality requires a Team plan subscription. Solo users
            can browse assets in read-only mode.
          </p>
        </div>

        <p className="text-sm text-muted-foreground mb-5 leading-relaxed">
          The Teams page in the Pilot Shell Console lets your team share custom
          assets — rules, commands, skills, hooks — via a private Git
          repository. Browse assets, push local assets to the vault, configure
          vault settings, and manage roles — all from the dashboard UI. Assets
          are versioned, so updates propagate automatically on next sync.
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

        <h3 className="font-semibold text-foreground text-sm mb-2">
          Advanced: sx CLI
        </h3>
        <p className="text-xs text-muted-foreground mb-3">
          Power users and CI/CD pipelines can use the sx CLI directly. The
          Console Teams page wraps these commands.
        </p>
        <div className="bg-background/80 rounded-lg p-3 font-mono text-xs border border-border/50 text-muted-foreground mb-5">
          <div className="text-muted-foreground/60 mb-1">
            # Pull team assets and install to current project
          </div>
          <div>
            <span className="text-primary">$</span> sx install --repair --target
            .
          </div>
          <div className="mt-2 text-muted-foreground/60">
            # Push a custom skill
          </div>
          <div>
            <span className="text-primary">$</span> sx add
            .claude/skills/my-skill --yes --type skill --name "my-skill"
            --scope-repo $REPO
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

        <div className="mt-4 rounded-xl p-3 border border-border/50 bg-card/30">
          <div className="flex items-start gap-2">
            <CheckCircle2 className="h-3.5 w-3.5 text-primary flex-shrink-0 mt-0.5" />
            <p className="text-xs text-muted-foreground leading-relaxed">
              Assets are auto-versioned — each push creates v1, v2, v3…
              Teammates pull the latest version. Use{" "}
              <code className="text-primary">sx vault show &lt;name&gt;</code>{" "}
              to see all versions of an asset.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TeamsSection;
