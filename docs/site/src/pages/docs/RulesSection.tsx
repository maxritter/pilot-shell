import { Shield, Brain, Search, GitBranch, Cpu, Layers } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const ruleCategories = [
  {
    icon: Shield,
    category: "Core Workflow",
    count: 3,
    rules: [
      {
        file: "task-and-workflow.md",
        desc: "Task management, /spec orchestration, deviation handling",
      },
      {
        file: "testing.md",
        desc: "TDD workflow, test strategy, coverage requirements (≥80%)",
      },
      {
        file: "verification.md",
        desc: "Execution verification, completion requirements",
      },
    ],
  },
  {
    icon: Brain,
    category: "Development Practices",
    count: 3,
    rules: [
      {
        file: "development-practices.md",
        desc: "Project policies, systematic debugging, git rules",
      },
      {
        file: "context-management.md",
        desc: "Auto-compaction and context preservation",
      },
      {
        file: "pilot-memory.md",
        desc: "Online learning triggers",
      },
    ],
  },
  {
    icon: Search,
    category: "Tools",
    count: 3,
    rules: [
      {
        file: "research-tools.md",
        desc: "Search priority and tool selection guide",
      },
      { file: "cli-tools.md", desc: "Pilot CLI, Vexor semantic search" },
      {
        file: "playwright-cli.md",
        desc: "Browser automation for E2E UI testing",
      },
    ],
  },
  {
    icon: GitBranch,
    category: "Collaboration",
    count: 1,
    rules: [{ file: "team-sharing.md", desc: "Teams asset sharing via sx" }],
  },
];

const codingStandards = [
  {
    standard: "Python",
    activates: "*.py",
    coverage: "uv, pytest, ruff, basedpyright, type hints",
  },
  {
    standard: "TypeScript",
    activates: "*.ts, *.tsx, *.js, *.jsx",
    coverage: "npm/pnpm, Jest, ESLint, Prettier, React patterns",
  },
  {
    standard: "Go",
    activates: "*.go",
    coverage: "Modules, testing, formatting, error handling",
  },
  {
    standard: "Frontend",
    activates: "*.tsx, *.jsx, *.html, *.vue, *.css",
    coverage: "Components, CSS, accessibility, responsive design",
  },
  {
    standard: "Backend",
    activates: "**/models/**, **/routes/**, **/api/**",
    coverage: "API design, data models, query optimization, migrations",
  },
];

const RulesSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="rules"
      className="py-10 border-b border-border/50 scroll-mt-24"
    >
      <div ref={ref} className={inView ? "animate-fade-in-up" : "opacity-0"}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
            <Layers className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-foreground">
              Rules & Standards
            </h2>
            <p className="text-sm text-muted-foreground">
              Production-tested best practices loaded into every session
            </p>
          </div>
        </div>

        <p className="text-sm text-muted-foreground mb-5 leading-relaxed">
          Rules are loaded automatically at session start. They're not
          suggestions — they're enforced standards. Coding standards load
          conditionally based on the file type being edited, keeping context
          lean. Your project-level rules in{" "}
          <code className="text-primary">.claude/rules/</code> are loaded
          alongside Pilot's built-ins and take precedence when they overlap.
        </p>

        {/* Rule categories */}
        <h3 className="font-semibold text-foreground text-sm mb-3">
          Built-in rule categories
        </h3>
        <div className="grid sm:grid-cols-2 gap-3 mb-6">
          {ruleCategories.map((cat) => {
            const Icon = cat.icon;
            return (
              <div
                key={cat.category}
                className="rounded-xl p-4 border border-border/50 bg-card/30"
              >
                <div className="flex items-center gap-2 mb-2">
                  <Icon className="h-4 w-4 text-primary" />
                  <h4 className="font-semibold text-foreground text-sm">
                    {cat.category}
                  </h4>
                  <span className="text-xs text-muted-foreground ml-auto">
                    {cat.count} rules
                  </span>
                </div>
                <ul className="space-y-1.5">
                  {cat.rules.map((rule) => (
                    <li
                      key={rule.file}
                      className="text-xs text-muted-foreground"
                    >
                      <code className="text-primary">{rule.file}</code> —{" "}
                      {rule.desc}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>

        {/* Coding standards */}
        <h3 className="font-semibold text-foreground text-sm mb-3">
          Coding standards — activated by file type
        </h3>
        <div className="rounded-xl border border-border/50 overflow-hidden mb-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50 bg-card/40">
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-muted-foreground">
                  Standard
                </th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-muted-foreground hidden sm:table-cell">
                  Activates On
                </th>
                <th className="text-left px-4 py-2.5 text-xs font-semibold text-muted-foreground">
                  Coverage
                </th>
              </tr>
            </thead>
            <tbody>
              {codingStandards.map((s, i) => (
                <tr
                  key={s.standard}
                  className={`border-b border-border/50 last:border-0 ${i % 2 === 0 ? "" : "bg-card/20"}`}
                >
                  <td className="px-4 py-2.5 text-xs font-medium text-foreground">
                    {s.standard}
                  </td>
                  <td className="px-4 py-2.5 text-xs font-mono text-muted-foreground hidden sm:table-cell">
                    {s.activates}
                  </td>
                  <td className="px-4 py-2.5 text-xs text-muted-foreground">
                    {s.coverage}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="rounded-xl p-4 border border-primary/20 bg-primary/5">
          <div className="flex items-start gap-2">
            <Cpu className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
            <p className="text-xs text-muted-foreground leading-relaxed">
              <span className="text-primary font-medium">Custom rules:</span>{" "}
              Create{" "}
              <code className="text-primary">.claude/rules/my-rule.md</code> in
              your project. Add{" "}
              <code className="text-primary">paths: ["*.py"]</code> frontmatter
              to activate only for specific file types. Run{" "}
              <code className="text-primary">/sync</code> to auto-discover
              patterns and generate project-specific rules for you.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default RulesSection;
