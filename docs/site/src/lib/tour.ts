/**
 * The home page's tour: one change followed from request to pull request in a pinned App
 * window, then the team and the setup. Each chapter draws a screen of the App as it is built:
 * the sidebar, the step line (whose turn it is, one sentence, the main action), Needs you,
 * the violet "Checked by agents" line and the work below. Ported from the Claude Design page
 * "QualityLayer Website"; change the copy in both places. Tasks, people and numbers are an
 * illustration.
 */

/** Who acts: you (amber ring), an agent (blue turning ring), or nobody because it is done. */
export type Who = "you" | "ag" | "ok";

/** The step line under the tabs: who it waits for, its sentence, a command, and its buttons (label, style). */
export type Line = { who: Who; head: string; text: string; code?: string; /** A segmented switch before the buttons; the first label is on. */ seg?: [string, string]; buttons: [string, string][] };

export type SideItem = { name: string; sub: string; who: Who; on?: boolean };
/** A sidebar group: its label, how many items it holds, and the ones worth drawing. */
export type Group = { label: string; count: number; items: SideItem[]; amber?: boolean };

/** What the window's main column shows: a task's step, the Team space, Settings or Home. */
export type View = "task" | "team" | "settings" | "home";

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
  };
}

export const STAGES = ["Discuss", "Plan", "Implement", "Verify", "Review"];

const item = (name: string, sub: string, who: Who, on = false): SideItem => ({ name, sub, who, on });

const TASK = "Retry failed webhooks";
const TITLE = `${TASK} · QualityLayer`;
const OTHER = item("Invoice PDFs", "Implement", "ag");

/** The sidebar of a task's window: the task under Needs you on your turn, under Running on an agent's. */
const sidebar = (turn: Who, sub: string): Group[] => {
  const current = item(TASK, sub, turn === "you" ? "you" : "ag", true);
  return turn === "you"
    ? [
        { label: "Needs you", count: 1, items: [current], amber: true },
        { label: "Running", count: 1, items: [OTHER] },
        { label: "Shipped", count: 4, items: [] },
      ]
    : [
        { label: "Needs you", count: 0, items: [], amber: true },
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

export const CHAPTERS: Chapter[] = [
  {
    id: "discuss",
    step: "Discuss",
    who: "you",
    steps: 6,
    act: { id: "steps", title: "From your request to a pull request", text: "On your own or with your team, a change goes through the same five steps. You decide where a decision is needed, and your agents do the rest." },
    title: "Your agent asks until the goal is clear",
    text: "Describe the change in your own words. Your agent reads the code. It asks each decision in the terminal, one at a time, and the App beside it shows only what the current question is about.",
    bullets: ["A bug is reproduced and its cause found", "Too small for a plan? You get a ready prompt", "What you decide is written down as Done means"],
    win: { title: TITLE, view: "task", groups: sidebar("you", "question"), foot: SOLO, doc: TASK, stage: 0, cost: "$2.10" },
  },
  {
    id: "plan",
    step: "Plan",
    who: "you",
    steps: 6,
    title: "You approve one plan before any code",
    text: "What needs a decision comes first, shown as it will look: a clickable mockup and a diagram for each engineering decision. Your agent asks them one by one, and the last question is the approval.",
    bullets: ["Comment on any line or diagram", "Everything the agent decided for you is listed, so you can change it", "A second agent reads the Plan before it reaches you"],
    win: { title: TITLE, view: "task", groups: sidebar("you", "Plan · 5"), foot: SOLO, doc: TASK, stage: 1, cost: "$5.95" },
  },
  {
    id: "implement",
    step: "Implement",
    who: "ag",
    steps: 6,
    title: "It is built in slices, each test first",
    text: "After you approve, the App opens Implement with one command that starts the build. Every task starts with a failing test, and slices that don’t overlap build side by side.",
    bullets: ["QualityLayer records every test run itself", "Nothing waits for you: what the agent decided on the way is listed", "Comment on the build while it runs"],
    win: { title: TITLE, view: "task", groups: sidebar("ag", "Implement"), foot: SOLO, doc: TASK, stage: 2, cost: "$15.35" },
  },
  {
    id: "verify",
    step: "Verify",
    who: "ag",
    steps: 7,
    title: "Agents that did not write the code check it",
    text: "Every check is listed from the start and fills in live: your project checks, each scenario, each point of Done means and a review of every changed file.",
    bullets: ["Polish and security review come before the checks", "A failure is fixed by the agent, and only what it touched is checked again", "Anything only you can confirm goes to Review"],
    win: { title: TITLE, view: "task", groups: sidebar("ag", "Verify"), foot: SOLO, doc: TASK, stage: 3, cost: "$20.95" },
  },
  {
    id: "review",
    step: "Review",
    who: "you",
    steps: 5,
    title: "You approve the finished change, with its proof",
    text: "Your agent asks what needs you in the terminal: what only you can confirm, the result to look at, and what the checks found. The App shows the summary and the diff.",
    bullets: ["Every changed file is tagged with the task that made it", "Approve and open a pull request, or approve only", "Ask for changes and your notes become the agent’s work"],
    win: { title: TITLE, view: "task", groups: sidebar("you", "Review · 3"), foot: SOLO, doc: TASK, stage: 4, cost: "$20.95" },
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
    win: { title: TITLE, view: "task", switch: "personal", groups: sidebar("you", "Plan · 1"), foot: TEAM, doc: TASK, stage: 1, cost: "$5.95" },
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
    bullets: ["Their comments reach you as items that need you", "People outside the team comment through a link", "Sharing sends the plan and progress, never your code"],
    win: { title: TITLE, view: "task", switch: "personal", groups: sidebar("you", "Review · 1"), foot: TEAM, doc: TASK, stage: 4, cost: "$20.95" },
  },
  {
    id: "settings",
    step: "Settings",
    who: "you",
    steps: 3,
    act: { id: "setup", title: "You stay in charge of models and cost", text: "QualityLayer works inside the coding agents you already pay for, and shows what each step costs." },
    title: "Choose the models, and see what each step costs",
    text: "Pick the model the workers use in Claude Code and in Codex, or no subagents at all. The cost of every step is estimated at list price.",
    bullets: ["No subagents: your agent does every step itself", "A second opinion from the other coding agent on risky plans", "One switch for notifications when something needs you"],
    win: { title: "Settings · QualityLayer", view: "settings", groups: sidebar("you", "Review · 3"), foot: SOLO, doc: "Settings", sub: "For every project on this computer. Changes save at once.", stage: -1 },
  },
  {
    id: "agents",
    step: "Your agents",
    who: "ag",
    steps: 5,
    title: "It works where your agents already work",
    text: "Claude Code and Codex do the work in their own apps and ask you each decision there. The QualityLayer App shows the detail, on macOS, Windows and Linux. On a server or in WSL, it opens in your browser.",
    bullets: ["Close the App and the agents keep working", "A notification tells you when something needs you", "Updates download quietly and install when you restart"],
    win: { title: "Needs you · QualityLayer", view: "home", groups: sidebar("you", "Review · 3"), foot: SOLO, doc: "Needs you", sub: "3 items on 1 task", stage: -1 },
  },
];

/** The story's parts, as the step bar groups them: a part starts at a chapter with an act heading. */
export const PARTS: { label: string; from: number; to: number }[] = (() => {
  const starts = CHAPTERS.flatMap((c, i) => (c.act ? [i] : []));
  const labels = ["Steps", "Team", "Setup"];
  return starts.map((from, k) => ({ label: labels[k] ?? CHAPTERS[from].step, from, to: (starts[k + 1] ?? CHAPTERS.length) - 1 }));
})();

export const partOf = (ch: number) => PARTS.findIndex((p) => ch >= p.from && ch <= p.to);

/** How many of the build's 5 tasks are committed at moment `step` of the Implement scene. */
export const committedTasks = (step: number) => (step >= 3 ? 2 : 0) + (step >= 4 ? 1 : 0);

/** The moment each of the Verify checklist's 12 checks passes; a check runs for the moment before. */
export const PASS_AT = [1, 2, 2, 2, 2, 2, 3, 4, 3, 4, 5, 6];
export const checksPassed = (step: number) => PASS_AT.filter((when) => step >= when).length;

/** The sidebar of chapter `ch` at moment `step`: what you have answered leaves the count. */
export function sidebarOf(ch: number, step: number): Group[] {
  const win = CHAPTERS[ch].win;
  switch (CHAPTERS[ch].id) {
    case "discuss":
      return step >= 3 ? sidebar("ag", "Discuss") : win.groups;
    case "plan":
      return step >= 6 ? sidebar("you", "start") : win.groups;
    case "implement":
      return sidebar("ag", `${committedTasks(step)}/5`);
    case "verify":
      return step >= 7 ? sidebar("you", "Review · 3") : sidebar("ag", `${checksPassed(step)}/12`);
    case "together":
      return step >= 4 ? sidebar("you", "Review") : win.groups;
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
  const turn: Mark = CHAPTERS[ch].who === "you" ? "you" : "ag";
  const counts: Record<string, number | undefined> = { discuss: step >= 3 ? undefined : 1, plan: 5, review: 3, ask: 1, together: step >= 4 ? undefined : 1 };
  return STAGES.map((label, k): Tab => {
    // Verify ends with its three items waiting in Review; the Plan is settled once approved, and the build waits for you to start it.
    if (id === "verify" && step >= 7 && k >= 3) return k === 3 ? { label, mark: "done" } : { label, mark: "you", count: 3 };
    if (id === "plan" && step >= 6) return k === 1 ? { label, mark: "done", lit: true } : k === 2 ? { label, mark: "you" } : { label, mark: k < 1 ? "done" : "todo" };
    if (id === "discuss" && step >= 3 && k === 0) return { label, mark: "ag" };
    if (k < stage) return { label, mark: "done" };
    if (k > stage) return { label, mark: "todo" };
    if (id === "implement") return { label, mark: "ag", count: `${committedTasks(step)}/5` };
    if (id === "verify") return { label, mark: "ag", count: `${checksPassed(step)}/12` };
    return { label, mark: turn, count: turn === "you" ? counts[id] : undefined };
  });
}

/** The step line of a task chapter at moment `step` of its scene. */
export function stepLine(ch: number, step: number): Line {
  const at = (n: number) => step >= n;
  switch (CHAPTERS[ch].id) {
    case "discuss":
      return at(3)
        ? { who: "ag", head: "Your answer is recorded", text: "The agent asks the next question in Claude Code and waits there.", buttons: [] }
        : { who: "you", head: "Waits for your answer", text: "Question 3 of about 5. The agent asks it in Claude Code and waits there.", buttons: [] };
    case "plan":
      return at(6)
        ? { who: "you", head: "Start the build", text: "Copy one command, with the model and effort the App recommends (Sonnet 5.5). It ends with", code: "/ql implement retry-webhooks", seg: ["Claude Code", "Codex"], buttons: [["Copy", "p"]] }
        : { who: "you", head: "Waits for your approval", text: "5 items need you before the build starts.", buttons: [["Request changes…", ""], ["Approve", step === 5 ? "p split press" : "p split"]] };
    case "implement":
      return { who: "ag", head: "Agents are building", text: "Slices 1 and 3 run side by side. Nothing needs you.", buttons: [] };
    case "verify":
      return at(7)
        ? { who: "ok", head: "Checked", text: "All 12 checks passed. 3 items wait for you in Review.", buttons: [["Open Review", "p"]] }
        : { who: "ag", head: "Agents are checking", text: "Three AI agents that did not write the code test every point. Nothing needs you yet.", buttons: [["Stop checking and review", ""]] };
    case "review":
      return { who: "you", head: "Waits for your review", text: "Every check passed. 3 items need you.", buttons: [["Request changes…", ""], ["Approve", at(5) ? "p split glow" : "p split"]] };
    case "ask":
      return at(5)
        ? { who: "you", head: "Waits for your approval", text: "Dana answered. Her change is in the Plan.", buttons: [["Request changes…", ""], ["Approve", "p split"]] }
        : { who: "you", head: "Waits for your approval", text: at(2) ? "You asked Dana about one passage. Approve waits for her." : "Select a passage to ask someone about it.", buttons: [["Request changes…", ""], ["Approve", "p split off"]] };
    case "together":
      return at(5)
        ? { who: "you", head: "Waits for your review", text: "Dana approved. Ben’s comment is answered.", buttons: [["Request changes…", ""], ["Approve", "p split glow"]] }
        : { who: "you", head: "Waits for your review", text: "Dana approved. Ben commented on a point of Done means.", buttons: [["Request changes…", ""], ["Approve", "p split off"]] };
    default:
      return { who: "ag", head: "", text: "", buttons: [] };
  }
}
