/**
 * The home page's tour: one change followed from request to pull request in a pinned App
 * window, then designs, the team and the setup. Each chapter draws a screen of the App as it is
 * built: live status and a quiet step track in the top bar, one Your turn card beside the document,
 * question batches, agreement per point, and the Plan read full size with comments. The website's
 * own visual language stays in place. Tasks, people and numbers are an illustration.
 */

/** Who acts: you (amber ring), an agent (blue turning ring), or nobody because it is done. */
export type Who = "you" | "ag" | "ok";

/**
 * The live status names what the agent is doing or waiting for. The amber dot belongs to the
 * separate Your turn indicator. `head` is the bold part, `text` follows it.
 */
export type Pill = { kind: "you" | "ag" | "move" | "ok"; head: string; text: string; meta?: string };

/** The live status and what awaits the person in the single Your turn card. */
export type Status = { pill: Pill; turn?: string };

export type SideItem = { name: string; sub: string; who: Who; on?: boolean };
/** A sidebar group: its label, how many items it holds, and the ones worth drawing. */
export type Group = { label: string; count: number; items: SideItem[]; amber?: boolean };

/** What the window's main column shows: a task's step, a design open full size, the Team space, Settings or Home. */
export type View = "task" | "design" | "team" | "settings" | "home";

/** A step tab's mark: done (filled), your turn (amber ring), an agent at work (blue ring) or not reached. */
export type Mark = "done" | "you" | "ag" | "todo";

export type Tab = { label: string; mark: Mark; /** Open items for you, or tasks done of all. */ count?: number | string; /** The dashed approval line after the Plan, lit once the Plan is approved. */ lit?: boolean };

export interface Chapter {
  id: string;
  /** The chapter's label in the step bar above the window. */
  step: string;
  who: Who;
  /** How many moments the chapter's scene plays, one per second. */
  steps: number;
  title: string;
  text: string;
  bullets: string[];
  /** A heading that opens a new part of the story before this chapter. */
  act?: { id: string; title: string; text: string };
  win: {
    title: string;
    view: View;
    /** The Personal | Team switch, shown with a Team licence; `team` is the side that is on. */
    switch?: "personal" | "team";
    groups: Group[];
    /** The sidebar foot: the person and the licence. */
    foot: [string, string];
    /** The task's title, or the page's. */
    doc: string;
    /** A page's one-sentence subtitle (Team, Settings, Home). */
    sub?: string;
    /** For a task: which of the five steps is current, and the cost so far. */
    stage: number;
    cost?: string;
    /** The step's own document and who writes it: one page per step. */
    file?: [string, string];
    /** The right sidebar, open on one of its two tabs. */
    right?: "comments" | "designs";
  };
}

export const STAGES = ["Discuss", "Plan", "Implement", "Verify", "Review"];

const item = (name: string, sub: string, who: Who, on = false): SideItem => ({ name, sub, who, on });

const TASK = "Retry failed webhooks";
const TITLE = `${TASK} · QualityLayer`;
const OTHER = item("Invoice PDFs", "Implement", "ag");

/** The sidebar moves the task from Your turn to Running when the batch is answered. */
const sidebar = (turn: Who, sub: string): Group[] => {
  const current = item(TASK, sub, turn === "you" ? "you" : "ag", true);
  return turn === "you"
    ? [
        { label: "Your turn", count: 1, items: [current], amber: true },
        { label: "Running", count: 1, items: [OTHER] },
        { label: "Shipped", count: 4, items: [] },
      ]
    : [
        { label: "Your turn", count: 0, items: [], amber: true },
        { label: "Running", count: 2, items: [current, OTHER] },
        { label: "Shipped", count: 4, items: [] },
      ];
};

/** Dana's and Max's Team sidebars: questions for you first, then the shared tasks. */
const teamSide = (questions: SideItem[], shared: SideItem[]): Group[] => [
  { label: "Questions for you", count: questions.length, items: questions, amber: true },
  { label: "Shared with the team", count: shared.length, items: shared },
];

const SOLO: [string, string] = ["Max Ritter", "Solo licence"];
const TEAM: [string, string] = ["Max Ritter", "Team licence"];

const DISCUSS: [string, string] = ["01-discuss.md", "by Claude Code"];
const PLAN: [string, string] = ["02-plan.md", "by Claude Code"];
const IMPLEMENT: [string, string] = ["03-implement.md", "by QualityLayer"];
const VERIFY: [string, string] = ["04-verify.md", "by QualityLayer"];
const REVIEW: [string, string] = ["05-review.md", "by QualityLayer"];

/** The design the Designs chapters draw, ask about and open full size. */
export const DESIGN = { name: "Failed deliveries", purpose: "Every delivery that failed, and when it tries again" };

/** The words a new task starts from, in the "+ New" card. */
export const REQUEST = "Retry failed webhooks, then mail the customer once";

export const CHAPTERS: Chapter[] = [
  {
    id: "discuss",
    step: "Discuss",
    who: "you",
    steps: 6,
    act: { id: "steps", title: "From your request to a pull request", text: "On your own or with your team, a change goes through the same five steps. You decide where a decision is needed, and your agents do the rest." },
    title: "Your agent asks until the goal is clear",
    text: "Describe the change in your own words. Questions arrive together in Your turn. Answer in any order; each answer reaches your agent at once, while it keeps reading the code.",
    bullets: ["A bug is reproduced and its cause found", "Too small for a plan? You get a ready prompt", "What you decide is written down as Done means"],
    win: { title: TITLE, view: "task", groups: sidebar("you", "Discuss · 3 questions"), foot: SOLO, doc: TASK, stage: 0, cost: "$2.10", file: DISCUSS },
  },
  {
    id: "plan",
    step: "Plan",
    who: "you",
    steps: 5,
    title: "You approve one plan before any code",
    text: "Read the Plan full size, with its design, diagrams and comments. Settle decisions in Your turn and agree to each Done means point, then approve; only a reworded point needs agreement again.",
    bullets: ["Comment on any line or diagram", "Everything the agent decided for you is listed, so you can change it", "A second agent reads the Plan before it reaches you"],
    win: { title: TITLE, view: "task", groups: sidebar("you", "Plan · 2 to answer"), foot: SOLO, doc: TASK, stage: 1, cost: "$5.95", file: PLAN },
  },
  {
    id: "start",
    step: "Start",
    who: "you",
    steps: 3,
    title: "One command starts the build",
    text: "Implement opens with your Build defaults: an orchestrator that plans each slice and writes no code, and workers that build them. Change anything for this build, or copy the command as it is.",
    bullets: ["Claude Code, Codex or another agent", "Reset brings your Build defaults back", "In the session that planned it, it lists what to type first"],
    win: { title: TITLE, view: "task", groups: sidebar("you", "start"), foot: SOLO, doc: TASK, stage: 2, cost: "$5.95", file: IMPLEMENT },
  },
  {
    id: "implement",
    step: "Implement",
    who: "ag",
    steps: 6,
    title: "It is built in slices, on its own",
    text: "From that command on, your agent works on its own until the final review. Every task starts with a failing test, and slices that don’t overlap build side by side.",
    bullets: ["QualityLayer records every test run itself", "What the agent decided on the way is listed, and you can ask why", "Anything only you can do is listed first in the final review"],
    win: { title: TITLE, view: "task", groups: sidebar("ag", "Implement"), foot: SOLO, doc: TASK, stage: 2, cost: "$15.35", file: IMPLEMENT },
  },
  {
    id: "verify",
    step: "Verify",
    who: "ag",
    steps: 7,
    title: "Agents that did not write the code check it",
    text: "Every check is listed from the start and fills in live: your project checks, each scenario, each point of Done means and a review of every changed file.",
    bullets: ["Polish and security review come before the checks", "A failure is fixed by the agent, and only what it touched is checked again", "Anything only you can confirm goes to Review"],
    win: { title: TITLE, view: "task", groups: sidebar("ag", "Verify"), foot: SOLO, doc: TASK, stage: 3, cost: "$20.95", file: VERIFY },
  },
  {
    id: "review",
    step: "Review",
    who: "you",
    steps: 5,
    title: "You approve the finished change, with its proof",
    text: "The App asks only what the checks could not settle: what only you can confirm, the result to look at and what the checks found. The last question is “Approve the change?”, and the pull request opens with its proof.",
    bullets: ["Every changed file is tagged with the task that made it", "Approve and open a pull request, or approve only", "Ask for changes and your notes become the agent’s work"],
    win: { title: TITLE, view: "task", groups: sidebar("you", "Review · 3 to answer"), foot: SOLO, doc: TASK, stage: 4, cost: "$20.95", file: REVIEW },
  },
  {
    id: "draw",
    step: "Draw",
    who: "ag",
    steps: 5,
    act: { id: "designs", title: "See the page before it is built", text: "Ask your agent to draw a page, open it full size in the App, and point at what should change. It never leaves your computer." },
    title: "Ask, and your agent draws the page",
    text: "Say “mock up the failed deliveries page”. Your agent draws it as one page, and the App lists it under Designs with what it is for and when it last changed. The Plan shows the one it is about.",
    bullets: ["Inside a task, or for the whole project", "A dot marks a design you have not opened yet", "Share links include a still; the interactive page stays on your computer"],
    win: { title: TITLE, view: "task", groups: sidebar("you", "Plan · 2 to answer"), foot: SOLO, doc: TASK, stage: 1, cost: "$4.80", file: PLAN, right: "designs" },
  },
  {
    id: "comment",
    step: "Comment",
    who: "you",
    steps: 6,
    title: "Open it full size and point at what to change",
    text: "A design opens across the whole window. Click a spot and say what should change. Your agent changes the same page and says in one line what changed, so you always see the latest.",
    bullets: ["Your comment reaches the agent like any other", "Jump to any part of a long page", "Full screen hides everything else"],
    win: { title: `${DESIGN.name} · QualityLayer`, view: "design", groups: sidebar("you", "Plan · 2 to answer"), foot: SOLO, doc: DESIGN.name, stage: 1 },
  },
  {
    id: "ask",
    step: "Ask",
    who: "you",
    steps: 5,
    act: { id: "team", title: "Bring your team in while it is still a plan", text: "With a Team plan, teammates help shape the plan and review the change, each from their own App." },
    title: "Ask a teammate about any part of the plan",
    text: "Select a passage or a diagram and choose who to ask. They get a Slack message that opens the question in their App.",
    bullets: ["They answer: Looks right, Suggest a change or Reply", "You get a Slack message and a notification with their answer", "Your agent updates the plan with what they suggest"],
    win: { title: TITLE, view: "task", switch: "personal", groups: sidebar("you", "Plan · 1 to answer"), foot: TEAM, doc: TASK, stage: 1, cost: "$5.95", file: PLAN },
  },
  {
    id: "answer",
    step: "Answer",
    who: "ag",
    steps: 5,
    title: "Teammates see the questions for them first",
    text: "Questions for you lists every question with the passage or diagram in view. Answer in the App, or let your own agent draft it. Nothing is sent without your yes.",
    bullets: ["Looks right, Suggest a change, Reply or Hand to someone else", "A draft from your agent shows as not sent yet", "Open the Plan at the exact diagram"],
    win: {
      title: "Team · QualityLayer",
      view: "team",
      switch: "team",
      groups: teamSide([item(TASK, "Max", "you", true), item("Billing export", "Anna", "you")], [item("Invoice PDFs", "Ben", "ag"), item("SSO group sync", "Chen", "ag")]),
      foot: ["Dana Weiss", "Team licence"],
      doc: "Team",
      sub: "Questions from teammates come first. Only these send you a notification.",
      stage: -1,
    },
  },
  {
    id: "space",
    step: "Team space",
    who: "you",
    steps: 3,
    title: "See your team’s work in one place",
    text: "Your questions to others, what each teammate is building and the step it is at, in one list. Remind or hand a question on from here.",
    bullets: ["A question waiting over a day turns amber", "Reminders go out at most every 4 hours", "Team activity folds into one line"],
    win: {
      title: "Team · QualityLayer",
      view: "team",
      switch: "team",
      groups: teamSide([], [item("Billing export", "Anna", "ag"), item("Invoice PDFs", "Ben", "ag"), item(TASK, "you", "ag", true)]),
      foot: TEAM,
      doc: "Team",
      sub: "Questions from teammates come first. Only these send you a notification.",
      stage: -1,
    },
  },
  {
    id: "together",
    step: "Review together",
    who: "you",
    steps: 5,
    title: "Review the finished change together",
    text: "Teammates read what changed and its proof, comment on any part and approve. The code itself is reviewed in your pull request.",
    bullets: ["Their comments reach you in the Comments tab", "People outside the team reopen the same link to read changes", "Sharing sends the plan, progress and a still of its design"],
    win: { title: TITLE, view: "task", switch: "personal", groups: sidebar("you", "Review · 1 to answer"), foot: TEAM, doc: TASK, stage: 4, cost: "$20.95", file: REVIEW, right: "comments" },
  },
  {
    id: "settings",
    step: "Settings",
    who: "you",
    steps: 3,
    act: { id: "setup", title: "You stay in charge of models and cost", text: "QualityLayer works inside the coding agents you already pay for, and shows what each step costs." },
    title: "Choose the models, and see what each step costs",
    text: "Planning defaults and Build defaults set the model, the effort and where each session starts. Plan with Claude Code and build with Codex if you like. The cost of every step is estimated at list price.",
    bullets: ["Change anything for one build when you start it", "An agent that never wrote the code decides whether it passes", "A second opinion from the other coding agent on risky plans"],
    win: { title: "Settings · QualityLayer", view: "settings", groups: sidebar("you", "Review · 3 to answer"), foot: SOLO, doc: "Settings", sub: "For every project on this computer. Changes save at once.", stage: -1 },
  },
  {
    id: "agents",
    step: "Your agents",
    who: "ag",
    steps: 5,
    title: "It works where your agents already work",
    text: "“+ New” starts a task: say what you want, pick the model and where it starts, and copy one command for Claude Code, Codex or another agent. The App runs on macOS, Windows and Linux. On a server or in WSL, it opens in your browser.",
    bullets: ["Close the App and the agents keep working", "A notification tells you when something needs you", "Updates download quietly and install when you restart"],
    win: { title: "Home · QualityLayer", view: "home", groups: sidebar("you", "Review · 3 to answer"), foot: SOLO, doc: "Home", stage: -1 },
  },
];

/** The story's parts, as the step bar groups them: a part starts at a chapter with an act heading. */
export const PARTS: { label: string; from: number; to: number }[] = (() => {
  const starts = CHAPTERS.flatMap((c, i) => (c.act ? [i] : []));
  const labels = ["Steps", "Designs", "Team", "Setup"];
  return starts.map((from, k) => ({ label: labels[k] ?? CHAPTERS[from].step, from, to: (starts[k + 1] ?? CHAPTERS.length) - 1 }));
})();

export const partOf = (ch: number) => PARTS.findIndex((p) => ch >= p.from && ch <= p.to);

/** How many of the build's 5 tasks are committed at moment `step` of the Implement scene. */
export const committedTasks = (step: number) => (step >= 3 ? 2 : 0) + (step >= 4 ? 1 : 0);

/** The moment each of the Verify checklist's 12 checks passes; a check runs for the moment before. */
export const PASS_AT = [1, 2, 2, 2, 2, 2, 3, 4, 3, 4, 5, 6];
export const checksPassed = (step: number) => PASS_AT.filter((when) => step >= when).length;

/** The three questions leave the batch as their answers reach the agent. */
export const questionsLeft = (step: number) => step >= 5 ? 0 : step >= 4 ? 1 : step >= 3 ? 2 : 3;

/** The sidebar of chapter `ch` at moment `step`: what you have answered leaves the count. */
export function sidebarOf(ch: number, step: number): Group[] {
  const win = CHAPTERS[ch].win;
  switch (CHAPTERS[ch].id) {
    case "discuss":
      return questionsLeft(step) ? sidebar("you", `Discuss · ${questionsLeft(step)} questions`) : sidebar("ag", "Discuss · writing Done means");
    case "plan":
      return sidebar("you", step >= 3 ? "Plan · approve" : `Plan · ${step >= 2 ? 1 : 2} to agree`);
    case "review":
      return sidebar("you", step >= 3 ? "Review · ready to approve" : `Review · ${3 - step} to answer`);
    case "implement":
      return sidebar("ag", `${committedTasks(step)}/5`);
    case "verify":
      return step >= 7 ? sidebar("you", "Review · 3 to answer") : sidebar("ag", `${checksPassed(step)}/12`);
    case "together":
      return step >= 4 ? sidebar("you", "Review · ready to approve") : win.groups;
    case "answer":
      return step >= 5
        ? teamSide([item("Billing export", "Anna", "you")], [item("Invoice PDFs", "Ben", "ag"), item("SSO group sync", "Chen", "ag"), item(TASK, "Max", "ag")])
        : win.groups;
    default:
      return win.groups;
  }
}

/** The five step tabs of chapter `ch` at moment `step`, each with its mark and the open items it counts. */
export function tabsOf(ch: number, step: number): Tab[] {
  const { stage } = CHAPTERS[ch].win;
  const id = CHAPTERS[ch].id;
  const turn: Mark = id === "discuss" && !questionsLeft(step) ? "ag" : CHAPTERS[ch].who === "you" ? "you" : "ag";
  const counts: Record<string, number | undefined> = { discuss: questionsLeft(step) || undefined, plan: step >= 2 ? 1 : 2, draw: 1, comment: 1, review: step >= 4 ? undefined : Math.max(0, 3 - step), ask: 1, together: step >= 4 ? undefined : 1 };
  return STAGES.map((label, k): Tab => {
    // Verify ends with its three items waiting in Review; the Plan, once approved, lights the line after it.
    if (id === "verify" && step >= 7 && k >= 3) return k === 3 ? { label, mark: "done" } : { label, mark: "you", count: 3 };
    if (k < stage) return { label, mark: "done", lit: k === 1 };
    if (k > stage) return { label, mark: "todo" };
    if (id === "start") return { label, mark: "you" };
    if (id === "implement") return { label, mark: "ag", count: `${committedTasks(step)}/5` };
    if (id === "verify") return { label, mark: "ag", count: `${checksPassed(step)}/12` };
    // The Designs chapters are the Plan, which waits for you while the agent draws.
    if (id === "draw" || id === "comment") return { label, mark: "you", count: counts[id] };
    return { label, mark: turn, count: turn === "you" ? counts[id] : undefined };
  });
}

/** The top bar's live status and Your turn indicator at each moment of a scene. */
export function statusOf(ch: number, step: number): Status {
  const at = (n: number) => step >= n;
  switch (CHAPTERS[ch].id) {
    case "discuss": {
      const left = questionsLeft(step);
      return { pill: { kind: "ag", head: "Working", text: left ? "reading notify.ts" : "writing Done means" }, ...(left ? { turn: `${left} questions` } : {}) };
    }
    case "plan":
      return { pill: { kind: "you", head: "Waits for you", text: at(3) ? "approve the Plan" : "agree to Done means" }, turn: at(3) ? "approve" : `${at(2) ? 1 : 2} to agree` };
    case "start":
      return { pill: { kind: "move", head: "Plan approved", text: "start the build" }, turn: "start" };
    case "implement":
      return { pill: { kind: "ag", head: "Working", text: `building slice ${at(3) ? 2 : 1} of 3` } };
    case "verify":
      return at(7)
        ? { pill: { kind: "you", head: "Waits for you", text: "review the change" }, turn: "3 items" }
        : { pill: { kind: "ag", head: "Working", text: `checking ${checksPassed(step)} of 12` } };
    case "review":
      return at(3)
        ? { pill: { kind: "you", head: "Waits for you", text: "approve the change" }, turn: "approve" }
        : { pill: { kind: "you", head: "Waits for you", text: "review the change" }, turn: `${Math.max(0, 3 - step)} to answer` };
    case "draw":
      return { pill: { kind: "ag", head: "Working", text: "drawing failed deliveries" }, turn: "1 design" };
    case "comment":
      return at(3) && !at(5)
        ? { pill: { kind: "ag", head: "Working", text: "changing the design" } }
        : { pill: { kind: "you", head: "Waits for you", text: "the design" }, turn: "1 design" };
    case "ask":
      return { pill: { kind: "you", head: "Waits for you", text: at(5) ? "Dana’s change" : "review the Plan" }, turn: "1 to answer" };
    case "together":
      return at(4)
        ? { pill: { kind: "you", head: "Waits for you", text: "approve the change" }, turn: "approve" }
        : { pill: { kind: "you", head: "Waits for you", text: "Ben’s comment" }, turn: "1 comment" };
    default:
      return { pill: { kind: "ok", head: "", text: "" } };
  }
}
