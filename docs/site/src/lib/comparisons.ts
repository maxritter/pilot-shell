export interface ComparisonSource {
  label: string;
  url: string;
}

export interface Comparison {
  slug: string;
  name: string;
  summary: string;
  lead: string;
  strengths: string;
  agents: string;
  rows: { topic: string; qualitylayer: string; other: string; source: number }[];
  chooseOther: string;
  chooseQualityLayer: string;
  sources: ComparisonSource[];
}

export const COMPARISONS: Comparison[] = [
  {
    slug: "humanlayer",
    name: "HumanLayer",
    summary: "Collaborative agent workspaces and portable RPI skills, compared with QualityLayer's verification and approval flow.",
    lead: "HumanLayer and QualityLayer both put people into agent planning. If you want a HumanLayer alternative, compare how each handles collaboration and what you review after implementation.",
    strengths: "HumanLayer brings sessions, artifacts and worktrees into a shared workspace. Its design documents support inline team comments that feed back to agents. That makes it a strong option when coordinating people and agent sessions is your main problem.",
    agents: "HumanLayer's portable RPI skill runs in Claude Code and Codex: /rpi in Claude Code and $rpi in Codex. Its app also supports both agents. Working inside these tools is shared ground with QualityLayer.",
    rows: [
      { topic: "Agree on the change", qualitylayer: "Review architecture diagrams and clickable designs, then approve the Plan before code.", other: "Use structured planning phases and collaborative design documents.", source: 1 },
      { topic: "Work in your agent", qualitylayer: "Use Claude Code or Codex, with the App for planning and review.", other: "Use portable RPI skills in Claude Code or Codex, or work in the HumanLayer app.", source: 2 },
      { topic: "Check the result", qualitylayer: "Verify records evidence for each agreed outcome; review independence depends on risk and settings.", other: "RPI works from local documents, with fresh sessions for its phases by default.", source: 2 },
    ],
    chooseOther: "Choose HumanLayer if shared workspaces, inline design discussions and managing multiple agent sessions are central to your day.",
    chooseQualityLayer: "Choose QualityLayer if you want an explicit Verify and Review flow, with evidence for the approved outcomes and unresolved checks visible before you approve.",
    sources: [
      { label: "HumanLayer product, collaboration and agent support", url: "https://www.humanlayer.dev/" },
      { label: "HumanLayer portable skills and RPI", url: "https://github.com/humanlayer/skills#rpi" },
    ],
  },
  {
    slug: "spec-kit",
    name: "GitHub Spec Kit",
    summary: "Customizable specifications, plans and convergence checks, compared with QualityLayer's visual planning and review.",
    lead: "GitHub Spec Kit gives your coding agent structured processes and reusable artifacts. A Spec Kit alternative is worth considering when you also want visual planning and a dedicated place to review the proof.",
    strengths: "Spec Kit is an open source toolkit with project principles, specifications, technical plans and implementation tasks. Extensions, presets and workflows let teams adapt the process to their own standards.",
    agents: "Spec Kit supports both Claude Code and Codex, alongside other coding agents. QualityLayer also works in those sessions. The decision is about the process you want around the agent.",
    rows: [
      { topic: "Define the work", qualitylayer: "Plan visually with diagrams and clickable designs; approve the Plan before implementation.", other: "Create a constitution, specification, technical plan and dependency-ordered tasks.", source: 1 },
      { topic: "Check the artifacts", qualitylayer: "Keep the agreed outcomes with the task through implementation and Review.", other: "Use clarification, requirements checklists and cross-artifact analysis as quality checks.", source: 2 },
      { topic: "Check the implementation", qualitylayer: "Record running-program evidence for each outcome, then bring gaps to human Review.", other: "Converge assesses code against spec, plan and tasks, appending remaining work. The bug-fixing extension records verification too.", source: 1 },
      { topic: "Adapt the process", qualitylayer: "Use the documented planning, build, Verify and Review flow in the App and your agent.", other: "Customize with extensions, presets, workflows and project-local overrides.", source: 1 },
    ],
    chooseOther: "Choose Spec Kit if you want a toolkit you can customize around your repository's own specification and review conventions. Its convergence checks deserve credit; it goes beyond generating a plan.",
    chooseQualityLayer: "Choose QualityLayer if you want the App to carry visual planning, human approval and recorded outcome checks into one review flow, including follow-up on the pull request.",
    sources: [
      { label: "Spec Kit repository and available processes", url: "https://github.com/github/spec-kit" },
      { label: "Spec Kit commands, checklists and convergence", url: "https://github.github.io/spec-kit/reference/agentic-sdd.html" },
      { label: "Spec Kit supported coding agents", url: "https://github.github.io/spec-kit/reference/integrations.html" },
    ],
  },
  {
    slug: "openspec",
    name: "OpenSpec",
    summary: "Flexible change proposals, evolving specs and optional verification, compared with QualityLayer's evidence and human review.",
    lead: "OpenSpec organizes a change around a proposal, requirements, a design and tasks. QualityLayer puts visual planning and outcome evidence into an approval flow. Both help you agree on the work before implementation.",
    strengths: "OpenSpec is an open source option for evolving an existing codebase. Each change has its own planning artifacts, and archiving folds spec updates into the main specifications. You can revise artifacts as your understanding changes.",
    agents: "OpenSpec supports Claude Code and Codex through tool-specific commands or skills. QualityLayer works with both too. Keeping your agent is a shared capability; compare how each process checks and closes the change.",
    rows: [
      { topic: "Plan a change", qualitylayer: "Review diagrams and clickable designs in the App, then approve the Plan.", other: "Create a proposal with spec deltas, design and tasks; revise artifacts as needed.", source: 1 },
      { topic: "Verify the code", qualitylayer: "Record output, screenshots or files against each agreed outcome, with risk-based independent review.", other: "The optional verify skill reports completeness, correctness and coherence against the artifacts.", source: 2 },
      { topic: "Finish the change", qualitylayer: "Review the evidence and open checks; approve locally, or ask QualityLayer to open and follow a pull request.", other: "Archive the change and sync its spec updates. Archive warns about incomplete artifacts or tasks.", source: 2 },
    ],
    chooseOther: "Choose OpenSpec if maintaining evolving specifications and small change proposals in your repository is the main goal. Its flexible artifact editing fits work where requirements change during implementation.",
    chooseQualityLayer: "Choose QualityLayer if you want explicit human approvals and evidence for the running result in the App. OpenSpec also checks implementation; QualityLayer's emphasis is how that proof reaches your review and pull request.",
    sources: [
      { label: "OpenSpec repository and change workflow", url: "https://github.com/Fission-AI/OpenSpec" },
      { label: "OpenSpec skills, verify and archive behavior", url: "https://openspec.dev/docs/skills" },
      { label: "OpenSpec supported tools", url: "https://openspec.dev/docs/supported-tools" },
    ],
  },
  {
    slug: "kiro",
    name: "Kiro",
    summary: "Integrated spec workflows and property-based testing, compared with QualityLayer's process in Claude Code and Codex.",
    lead: "Kiro integrates specifications into its coding environment. QualityLayer works with agents such as Claude Code and Codex. Compare the environment you want to use and the evidence you want before approval.",
    strengths: "Kiro turns requirements into technical designs and trackable tasks. Feature Specs support requirements-first and design-first approaches. Its IDE also supports property-based testing that connects specified behavior to executable checks.",
    agents: "Kiro documents its own spec workflow in its IDE, CLI and web surfaces. QualityLayer's workflow runs with your Claude Code or Codex session. Kiro has a CLI too, so describing this as a choice between an IDE and a terminal would miss the point.",
    rows: [
      { topic: "Shape the specification", qualitylayer: "Use visual architecture and clickable designs, with a human-approved Plan.", other: "Generate requirements, design and tasks; start from requirements or a technical design.", source: 1 },
      { topic: "Verify behavior", qualitylayer: "Check each agreed outcome on the running program and retain the evidence for Review.", other: "In the IDE, derive executable properties from specs and test generated inputs for counterexamples.", source: 2 },
      { topic: "Review planning", qualitylayer: "Approve the Plan before code, then inspect outcome evidence at final Review.", other: "Review spec documents with comments on exact passages. Quick Spec can generate artifacts without approval steps.", source: 3 },
    ],
    chooseOther: "Choose Kiro if you want specifications and task execution integrated into Kiro's environment. Its property-based testing is a substantive verification capability, with availability that varies by surface.",
    chooseQualityLayer: "Choose QualityLayer if you want to keep building in Claude Code or Codex and review an explicit record of outcomes, unresolved checks and approval decisions in the App.",
    sources: [
      { label: "Kiro Feature Specs and workflow variants", url: "https://kiro.dev/docs/specs/feature-specs/" },
      { label: "Kiro correctness and property-based testing", url: "https://kiro.dev/docs/specs/correctness/" },
      { label: "Kiro specs, supported surfaces and review", url: "https://kiro.dev/docs/specs/" },
    ],
  },
];

export const ROUNDUP_PATH = "/best-spec-driven-development-tools";
export const COMPARISON_PATHS = ["/compare", ...COMPARISONS.map(({ slug }) => `/compare/${slug}`), ROUNDUP_PATH];

export const ROUNDUP_FAQS = [
  {
    question: "Which spec-driven development tool is best?",
    answer: "Choose by the work you need to coordinate. Spec Kit offers customizable processes; OpenSpec manages evolving change proposals; HumanLayer coordinates shared agent work; Kiro integrates specs into its environment. QualityLayer emphasizes visual planning, human approval and recorded outcome evidence. This guide compares documented capabilities, not benchmark scores.",
  },
  {
    question: "Do these tools work inside Claude Code and Codex?",
    answer: "QualityLayer, HumanLayer's portable RPI skills, Spec Kit and OpenSpec all support Claude Code and Codex. Kiro documents its own agent environment, including an IDE and CLI. Agent compatibility alone does not distinguish QualityLayer; compare how a tool handles planning, verification evidence and human review.",
  },
  {
    question: "How can I verify AI generated code against a spec?",
    answer: "Define observable acceptance criteria, run the relevant project checks and exercise the behavior those criteria describe. Record what passed, failed or could not be checked. QualityLayer's Verify and Review steps carry that evidence to human approval; independence depends on task risk and settings. Spec Kit, OpenSpec and Kiro also document implementation checks.",
  },
];
