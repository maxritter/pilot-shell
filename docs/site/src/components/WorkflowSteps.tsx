import {
  ArrowRight,
  Bug,
  Code2,
  FileText,
  Lightbulb,
  ListChecks,
  MessageSquare,
  MonitorCheck,
  ShieldCheck,
  Trophy,
  type LucideIcon,
} from "lucide-react";

interface Workflow {
  icon: LucideIcon;
  title: string;
  kicker: string;
  summary: string;
  href: string;
}

const workflows: Workflow[] = [
  {
    icon: Lightbulb,
    title: "Requirements",
    kicker: "/prd — brainstorm what to build",
    summary:
      "Invoke it when the product itself is still unclear. The agent pressure-tests directions and writes a PRD you can deliberately hand to /spec or /build.",
    href: "/docs/workflows/prd",
  },
  {
    icon: FileText,
    title: "Specifications",
    kicker: "/spec — plan, build, and verify",
    summary:
      "Use it when an ordered task list should be written and approved before code. It implements with TDD and verifies against that approved plan.",
    href: "/docs/workflows/spec",
  },
  {
    icon: Trophy,
    title: "Build",
    kicker: "/build — name a goal, walk away",
    summary:
      "Use it when the end state matters more than a pre-approved task list. It sharpens the goal, then builds and judges autonomously against explicit pass/fail criteria.",
    href: "/docs/workflows/build",
  },
  {
    icon: Bug,
    title: "Bugfix",
    kicker: "/fix — investigate, test, fix, audit",
    summary:
      "The focused TDD bugfix process: reproduce, trace the root cause, fix at the source, and verify the behavior end-to-end.",
    href: "/docs/workflows/fix",
  },
];

const flowSteps: Array<{ icon: LucideIcon; label: string }> = [
  { icon: MessageSquare, label: "Requirement" },
  { icon: ListChecks, label: "Plan / criteria" },
  { icon: Code2, label: "TDD implementation" },
  { icon: ShieldCheck, label: "Quality gates" },
  { icon: MonitorCheck, label: "Review & verification loop" },
];

const onDemandCommands = [
  {
    command: "/setup-rules",
    desc: "Generates modular project rules and MCP docs from the real codebase.",
    href: "/docs/workflows/setup-rules",
  },
  {
    command: "/create-skill",
    desc: "Captures a repeatable procedure as a tested, reusable skill.",
    href: "/docs/workflows/create-skill",
  },
  {
    command: "/benchmark",
    desc: "Measures whether a rule or skill actually changes agent behavior, with before/after evals.",
    href: "/docs/workflows/benchmark",
  },
  {
    command: "/investigate",
    desc: "Traces one codebase question with cited evidence, without changing the project.",
    href: "/docs/workflows/investigate",
  },
  {
    command: "/cleanup",
    desc: "Corroborates dead-code candidates into a report-only cleanup inventory with file-and-line evidence.",
    href: "/docs/workflows/cleanup",
  },
];

const WorkflowSteps = () => (
  <section className="ps-sec" id="workflows" aria-labelledby="workflows-heading">
    <div className="ps-ctr">
      <div className="ps-sec-hd ps-left ps-rv">
        <p className="ps-eyebrow">Coordinated parts</p>
        <h2 className="ps-h2" id="workflows-heading">
          Workflows put the harness around the work.
        </h2>
        <p className="ps-lead">
          Direct requests, native Plan/Goal tools, and Pilot workflows are peers.
          Use a Pilot workflow when its durable product, planning, or
          verification contract fits the work.
        </p>
      </div>

      <div className="ps-wcards ps-stg">
        {workflows.map((workflow) => (
          <a key={workflow.href} className="ps-wcard" href={workflow.href}>
            <span className="ps-tile">
              <workflow.icon className="h-5 w-5" aria-hidden="true" />
            </span>
            <span>
              <span className="ps-h3">{workflow.title}</span>
              <span className="ps-kick">{workflow.kicker}</span>
            </span>
            <span className="ps-sup">{workflow.summary}</span>
            <span className="ps-more">
              Learn more
              <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
            </span>
          </a>
        ))}
      </div>

      <ol className="ps-flow ps-stg" aria-label="Workflow stages">
        {flowSteps.map((step) => (
          <li key={step.label} className="ps-fstep">
            <span className="ps-tile">
              <step.icon className="h-5 w-5" aria-hidden="true" />
            </span>
            <span className="ps-fstep-t">{step.label}</span>
            <ArrowRight className="ps-arr" aria-hidden="true" />
          </li>
        ))}
      </ol>

      <div className="ps-ledger-wrap">
        <div className="ps-rv">
          <h3 className="ps-h3" style={{ fontSize: 24 }}>
            Rules, skills, and memory
          </h3>
          <p className="ps-body" style={{ marginTop: 16 }}>
            They are coordinated parts of the harness — they supply context; they
            are not the product by themselves. Pilot generates, tests, and
            measures them with dedicated workflows.
          </p>
        </div>
        <div className="ps-ledger ps-stg">
          {onDemandCommands.map((entry) => (
            <div key={entry.command} className="ps-lrow">
              <a className="ps-lnk" href={entry.href}>
                {entry.command}
              </a>
              <span className="ps-sup">{entry.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
);

export default WorkflowSteps;
