import {
  Shield,
  FileCode2,
  Brain,
  Eye,
  Terminal,
  GitBranch,
  Search,
  Globe,
  BookOpen,
  CheckCircle2,
  Activity,
  Layers,
  Cpu,
  RefreshCw,
  Route,
  Box,
} from "lucide-react";
import { useInView } from "@/hooks/use-in-view";

const claudeHooksPipeline = [
  {
    trigger: "SessionStart",
    description: "On startup, clear, or after compaction",
    hooks: [
      "Worker bootstrap restores session context",
      "post_compact_restore.py restores plan state after compaction",
      "Background session tracking starts asynchronously",
    ],
    color: "text-sky-400",
    bgColor: "bg-sky-400/10",
    borderColor: "border-sky-400/30",
  },
  {
    trigger: "UserPromptSubmit",
    description: "When the user sends a message",
    hooks: [
      "spec_mode_guard.py enforces /spec only while that workflow is active",
      "Session registration starts in the background",
    ],
    color: "text-emerald-400",
    bgColor: "bg-emerald-400/10",
    borderColor: "border-emerald-400/30",
  },
  {
    trigger: "PreToolUse",
    description: "Before Bash, search, web, or agent tools",
    hooks: [
      "tool_redirect.py maps unavailable tool names to supported equivalents",
      "An active workflow can reject conflicting plan-mode operations",
      "tool_token_saver.py routes supported shell output through RTK",
    ],
    color: "text-amber-400",
    bgColor: "bg-amber-400/10",
    borderColor: "border-amber-400/30",
  },
  {
    trigger: "PostToolUse",
    description: "After edits, reads, searches, and task tools",
    hooks: [
      "file_checker.py runs lint, type, and TDD checks on edits",
      "context_monitor.py tracks usage before compaction",
      "Memory observations are captured asynchronously",
    ],
    color: "text-primary",
    bgColor: "bg-primary/10",
    borderColor: "border-primary/30",
  },
  {
    trigger: "PreCompact",
    description: "Before auto-compaction fires",
    hooks: [
      "pre_compact.py snapshots the active plan and task list",
      "Current progress is persisted before context is compacted",
    ],
    color: "text-violet-400",
    bgColor: "bg-violet-400/10",
    borderColor: "border-violet-400/30",
  },
  {
    trigger: "Stop",
    description: "When the agent tries to finish",
    hooks: [
      "spec_stop_guard.py blocks incomplete /spec verification",
      "Session summaries save observations asynchronously",
    ],
    color: "text-rose-400",
    bgColor: "bg-rose-400/10",
    borderColor: "border-rose-400/30",
  },
  {
    trigger: "SessionEnd",
    description: "When the session closes",
    hooks: [
      "session_end.py stops the worker if no sessions remain",
      "A dashboard notification marks the session complete",
    ],
    color: "text-slate-400",
    bgColor: "bg-slate-400/10",
    borderColor: "border-slate-400/30",
  },
];

const rulesCategories = [
  {
    icon: Shield,
    category: "Core Workflow",
    rules: [
      "Pilot workflow orchestration and completion guards",
      "TDD & test strategy",
      "Execution verification & completion",
    ],
  },
  {
    icon: Brain,
    category: "Development Practices",
    rules: [
      "Project policies, debugging, and git hygiene",
      "Context management and compaction resilience",
      "Code review reception and change handling",
      "Documentation sync — keep README, API docs, and AGENTS.md current with code changes",
      "Response shape — answer first, numbered steps, no preamble or filler",
    ],
  },
  {
    icon: Search,
    category: "Tools",
    rules: [
      "Pilot CLI, Semble code search, and RTK token optimization",
      "Browser automation: Chrome, Chrome DevTools MCP, playwright-cli, agent-browser",
      "MCP server selection and tool-routing rules",
    ],
  },
  {
    icon: GitBranch,
    category: "Extensions",
    rules: [
      "Skills, rules, commands, agents, MCP servers, hooks, and settings",
      "Project, global, plugin, and remote scopes with diff view",
      "Team sharing via git — push, pull, and compare extensions",
    ],
  },
  {
    icon: Cpu,
    category: "Language Standards",
    rules: [
      "Python — uv, pytest, ruff, basedpyright",
      "TypeScript — npm/pnpm, Jest, ESLint, Prettier",
      "Go — Modules, testing, formatting, error handling",
    ],
  },
  {
    icon: Layers,
    category: "Architecture Standards",
    rules: [
      "Frontend — Components, CSS, accessibility, responsive",
      "Backend — API design, data models, migrations",
      "Activated by file type — loaded only when needed",
    ],
  },
];

const mcpServers = [
  {
    icon: BookOpen,
    name: "context7",
    desc: "Library documentation lookup for frameworks and dependencies",
  },
  {
    icon: Box,
    name: "codegraph",
    desc: "Code knowledge graph for callers, impact analysis, and structural queries",
  },
  {
    icon: Brain,
    name: "mem-search",
    desc: "Persistent memory search — recall context from past sessions",
  },
  {
    icon: Globe,
    name: "web-search",
    desc: "Web search via DuckDuckGo, Bing, and Exa",
  },
  {
    icon: Search,
    name: "grep-mcp",
    desc: "GitHub code search — find real-world usage patterns",
  },
  {
    icon: Globe,
    name: "web-fetch",
    desc: "Web page fetching — read documentation, APIs, references",
  },
  {
    icon: Search,
    name: "semble",
    desc: "Hybrid semantic+lexical code search (BM25 + Model2Vec embeddings, ~1.5ms queries)",
  },
];

const DeepDiveSection = () => {
  const [headerRef, headerInView] = useInView<HTMLDivElement>();
  const [hooksRef, hooksInView] = useInView<HTMLDivElement>();
  const [routingRef, routingInView] = useInView<HTMLDivElement>();
  const [rulesRef, rulesInView] = useInView<HTMLDivElement>();
  const [mcpRef, mcpInView] = useInView<HTMLDivElement>();

  return (
    <section id="deep-dive" className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        {/* Header */}
        <div
          ref={headerRef}
          className={`text-center mb-16 ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            Under the Hood
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
            Pilot adapts its rules, hooks, search, and verification to the
            capabilities each agent exposes.
          </p>
        </div>

        {/* Hooks Pipeline */}
        <div
          ref={hooksRef}
          className={`mb-16 ${hooksInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
              <Activity className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-foreground">
                Claude Code hook pipeline
              </h3>
              <p className="text-sm text-muted-foreground">
                Lifecycle quality enforcement through Claude Code&apos;s public
                hook surface.
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {claudeHooksPipeline.map((stage) => (
              <div
                key={stage.trigger}
                className={`rounded-lg p-5 border ${stage.borderColor} bg-card`}
              >
                <div className="mb-3">
                  <div
                    className={`${stage.bgColor} px-3 py-1.5 rounded-lg inline-flex items-center gap-2 w-fit mb-2`}
                  >
                    <Terminal className={`h-4 w-4 ${stage.color}`} />
                    <code className={`text-sm font-semibold ${stage.color}`}>
                      {stage.trigger}
                    </code>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {stage.description}
                  </p>
                </div>
                <div className="space-y-1.5">
                  {stage.hooks.map((hook) => (
                    <div
                      key={hook}
                      className="flex items-start gap-2 text-xs text-muted-foreground"
                    >
                      <CheckCircle2
                        className={`h-3.5 w-3.5 ${stage.color} flex-shrink-0 mt-0.5`}
                      />
                      <span>{hook}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Context Optimization — keeping context lean */}
          <div className="mt-6 rounded-lg border border-violet-400/20 bg-card p-5">
            <div className="flex items-start gap-4">
              <div className="w-9 h-9 bg-violet-400/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <RefreshCw className="h-4 w-4 text-violet-400" />
              </div>
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">
                  Context Optimization
                </h4>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  <span className="text-violet-400">Semble</span> returns focused
                  code matches, while <span className="text-violet-400">RTK</span>{" "}
                  compresses supported CLI output. Claude Code hooks can capture
                  and restore active workflow state around compaction. Rules
                  still load by file type, and skills use progressive disclosure.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Model Switching */}
        <div
          ref={routingRef}
          className={`mb-16 ${routingInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-violet-400/10 rounded-xl flex items-center justify-center">
              <Route className="h-5 w-5 text-violet-400" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-foreground">
                Model Switching <span className="text-xs font-normal text-muted-foreground">(Claude Code only)</span>
              </h3>
              <p className="text-sm text-muted-foreground">
                Automated by default — /spec runs opusplan (Opus plans, Sonnet
                executes) — or switch models yourself, or turn it off entirely.
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div className="rounded-lg p-5 border border-violet-400/30 bg-violet-400/5">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-sm font-mono font-semibold text-violet-400 bg-violet-400/10 px-3 py-1 rounded-lg">
                  Manual
                </span>
                <span className="text-sm text-muted-foreground">
                  you pick the models
                </span>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Plan on your frontier model, implement on your fast one.{" "}
                <code>/spec</code> pauses once after plan approval so your{" "}
                <code>/model</code> switch lands before code is written.
              </p>
            </div>
            <div className="rounded-lg p-5 border border-primary/30 bg-primary/5">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-sm font-mono font-semibold text-primary bg-primary/10 px-3 py-1 rounded-lg">
                  Automated
                </span>
                <span className="text-sm text-muted-foreground">
                  default — opusplan
                </span>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                <code>/spec</code> runs on Claude Code's native{" "}
                <code>opusplan</code>: Opus 5 plans, Sonnet 5 executes —
                switched automatically, with a pre-flight check that warns when
                your conversation is too large for the Opus plan leg.
              </p>
            </div>
          </div>

          <div className="rounded-lg p-4 border border-border/30 bg-card/20">
            <p className="text-xs text-muted-foreground text-center">
              Three modes in Console Settings → Model Switching:{" "}
              <strong>Automated</strong> (default), <strong>Manual</strong>, and{" "}
              <strong>Off</strong> — no model management at all. Pilot never
              remaps the model aliases, so <code>/model</code> always means
              what it says — including <strong>Claude Fable 5</strong>, whose
              saved selection Pilot preserves.
            </p>
          </div>
        </div>

        {/* Rules System */}
        <div
          ref={rulesRef}
          className={`mb-16 ${rulesInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
              <Layers className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-foreground">
                Built-in Rules & Standards
              </h3>
              <p className="text-sm text-muted-foreground">
                Project practices and file-specific standards, applied through
                the mechanisms each agent supports
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rulesCategories.map((cat) => {
              const Icon = cat.icon;
              return (
                <div
                  key={cat.category}
                  className="rounded-lg p-5 border border-border/50 bg-card hover:border-primary/30 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className="h-5 w-5 text-primary" />
                    <h4 className="font-semibold text-foreground text-sm">
                      {cat.category}
                    </h4>
                  </div>
                  <ul className="space-y-1.5">
                    {cat.rules.map((rule) => (
                      <li
                        key={rule}
                        className="text-xs text-muted-foreground flex items-start gap-1.5"
                      >
                        <span className="text-primary mt-0.5">&#x25B8;</span>
                        <span>{rule}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>

        {/* MCP Servers + LSP + Languages */}
        <div
          ref={mcpRef}
          className={`${mcpInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <div className="grid md:grid-cols-2 gap-8">
            {/* MCP Servers */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                  <Globe className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-foreground">
                    MCP Servers
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Seven preconfigured servers, lazy-loaded on demand
                  </p>
                </div>
              </div>
              <div className="space-y-3">
                {mcpServers.map((server) => {
                  const Icon = server.icon;
                  return (
                    <div
                      key={server.name}
                      className="flex items-start gap-3 rounded-xl p-3 border border-border/50 bg-card"
                    >
                      <Icon className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                      <div>
                        <code className="text-sm font-medium text-foreground">
                          {server.name}
                        </code>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {server.desc}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* LSP + Languages */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                  <Eye className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-foreground">
                    Language Servers <span className="text-xs font-normal text-muted-foreground">(Claude Code only)</span>
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Real-time diagnostics and go-to-definition
                  </p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="rounded-xl p-4 border border-border/50 bg-card">
                  <div className="flex items-center gap-2 mb-2">
                    <FileCode2 className="h-4 w-4 text-primary" />
                    <span className="font-medium text-foreground text-sm">
                      Python
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    basedpyright — strict type checking, auto-restart on crash
                  </p>
                </div>
                <div className="rounded-xl p-4 border border-border/50 bg-card">
                  <div className="flex items-center gap-2 mb-2">
                    <FileCode2 className="h-4 w-4 text-primary" />
                    <span className="font-medium text-foreground text-sm">
                      TypeScript
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    vtsls — full TypeScript support with Vue compatibility
                  </p>
                </div>
                <div className="rounded-xl p-4 border border-border/50 bg-card">
                  <div className="flex items-center gap-2 mb-2">
                    <FileCode2 className="h-4 w-4 text-primary" />
                    <span className="font-medium text-foreground text-sm">
                      Go
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    gopls — official Go language server, auto-restart on crash
                  </p>
                </div>
                <p className="text-xs text-muted-foreground mt-3 pl-1">
                  Pilot Shell works with all programming languages. Add more
                  language servers via Claude Code's LSP plugin marketplace.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DeepDiveSection;
