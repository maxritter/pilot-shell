/**
 * The home page's tour: one change followed from request to pull request in a pinned App
 * window, then the team and the setup. Ported from the Claude Design page "QualityLayer
 * Website"; change the copy in both places. Tasks, people and numbers are an illustration.
 */

/** Who acts: you (amber ring), an agent (blue turning ring), or nobody because it is done. */
export type Who = "you" | "ag" | "ok";

/** The bar at the bottom of the App: who it waits for, the text, a command, and its buttons (label, style). */
export type Next = { who: Who; text: string; code?: string; buttons: [string, string][] };

export type SideItem = { name: string; sub: string; who: Who; on?: boolean };

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
    /** The highlighted entry in the App's sidebar: Tasks, Team or Settings. */
    nav: number;
    head: string;
    side: SideItem[];
    doc: string;
    /** Which of the five steps is current; -1 for none. */
    stage: number;
    chip: [Who, string];
    /** A fixed bar; chapters without one change it as the scene plays (see nextBar). */
    next: Next | null;
  };
}

export const STAGES = ["Discuss", "Plan", "Implement", "Verify", "Review"];

const item = (name: string, sub: string, who: Who, on = false): SideItem => ({ name, sub, who, on });

const tasks = (current: string) => [
  item("Retry failed webhooks", current, "you", true),
  item("Invoice PDFs", "Implement · slice 2 of 4", "ag"),
  item("SSO group sync", "Plan waits for you", "you"),
];

const TITLE = "Retry failed webhooks · QualityLayer";
const TASK = "Retry failed webhooks";

export const CHAPTERS: Chapter[] = [
  {
    id: "discuss",
    step: "Discuss",
    who: "you",
    steps: 7,
    title: "Your agent asks until the goal is clear",
    text: "Describe the change in your own words. Your agent reads the code and asks one question at a time, each with its recommendation.",
    bullets: ["A bug is reproduced and its cause found", "Too small? You get a ready prompt instead", "Still deciding what to build? Copy it as a PRD"],
    win: { title: TITLE, nav: 0, head: "Your tasks", side: tasks("Discuss"), doc: TASK, stage: 0, chip: ["you", "Your answers"], next: { who: "you", text: "Question 3 of 5 waits in Claude Code", buttons: [] } },
  },
  {
    id: "plan",
    step: "Plan",
    who: "you",
    steps: 6,
    title: "You approve one plan before any code",
    text: "Decisions come first, as diagrams and a clickable mockup. Then the slices, and the scenarios that prove the change works.",
    bullets: ["Comment on any line or diagram", "Decisions made for you, listed so you can overturn them", "Read by a fresh agent before it reaches you"],
    win: { title: TITLE, nav: 0, head: "Your tasks", side: tasks("Plan waits for you"), doc: TASK, stage: 1, chip: ["you", "Needs you"], next: null },
  },
  {
    id: "implement",
    step: "Implement",
    who: "ag",
    steps: 7,
    title: "It is built in slices, each test first",
    text: "Start a fresh session your way and type /ql implement. Every task starts with a failing test, and slices that don’t overlap build side by side.",
    bullets: ["QualityLayer records every test run itself", "A risky slice stops so you can try it", "A failure goes to a fresh agent to fix"],
    win: { title: TITLE, nav: 0, head: "Your tasks", side: tasks("Implement"), doc: TASK, stage: 2, chip: ["ag", "Building"], next: null },
  },
  {
    id: "verify",
    step: "Verify",
    who: "ag",
    steps: 7,
    title: "An AI that did not write the code checks it",
    text: "It checks every point of your definition of done against the running program and the diff, citing the test runs QualityLayer recorded.",
    bullets: ["Polish and security review run side by side", "Security when it touches outside input, sign-in or secrets", "Evidence for every point"],
    win: { title: TITLE, nav: 0, head: "Your tasks", side: tasks("Verify"), doc: TASK, stage: 3, chip: ["ag", "Checking"], next: null },
  },
  {
    id: "review",
    step: "Review",
    who: "you",
    steps: 4,
    title: "You approve the finished change, with its proof",
    text: "What changed, the evidence and the diff in one view, with the pull request description already written.",
    bullets: ["Teammates comment on any line", "Comments go back to your agent", "Approve, then create the pull request"],
    win: { title: TITLE, nav: 0, head: "Your tasks", side: tasks("Review waits for you"), doc: TASK, stage: 4, chip: ["you", "Needs you"], next: null },
  },
  {
    id: "ask",
    step: "Ask",
    who: "you",
    steps: 5,
    act: { id: "team", title: "Bring your team in while it is still a plan", text: "With a Team plan, teammates help shape the plan and review the change, each from their own App." },
    title: "Ask a teammate about any part of the plan",
    text: "Pick a passage, a diagram or the whole plan, and choose who to ask. They get a Slack message that opens the question in their App.",
    bullets: ["They answer: looks right, a change, or a reply", "The answer goes straight to your agent", "Ask about build steps the same way"],
    win: { title: TITLE, nav: 0, head: "Your tasks", side: tasks("Plan waits for you"), doc: TASK, stage: 1, chip: ["you", "Needs you"], next: null },
  },
  {
    id: "answer",
    step: "Answer",
    who: "ag",
    steps: 5,
    title: "Teammates can answer with their own agent",
    text: "Dana hands your question to her Claude Code, Codex or Grok Bot. It reads the plan and her code, asks her what it needs, and drafts the answer.",
    bullets: ["Nothing is sent without her yes", "The answer shows which agent wrote it", "Her agent runs on her own computer"],
    win: {
      title: "QualityLayer · Dana",
      nav: 1,
      head: "Asked of you",
      side: [item(TASK, "Max asks · Plan", "you", true), item("Billing export", "Anna asks · Plan", "you")],
      doc: "A question from Max",
      stage: -1,
      chip: ["you", "Your answer"],
      next: { who: "you", text: "Your agent drafts. You decide what is sent.", buttons: [] },
    },
  },
  {
    id: "space",
    step: "Team space",
    who: "you",
    steps: 3,
    title: "See your team’s work in one place",
    text: "The Team space lists every shared task by person and step, with the questions waiting for you on top.",
    bullets: ["Share a link with people outside the team", "Their comments reach your agent too", "Sharing sends the plan and progress, never your code"],
    win: {
      title: "Team · QualityLayer",
      nav: 1,
      head: "Team",
      side: [item("Anna", "2 shared tasks", "you"), item("Ben", "1 shared task", "ag"), item("Chen", "1 shared task", "ag"), item("Dana", "answered you", "ag")],
      doc: "Team space",
      stage: -1,
      chip: ["you", "2 asks for you"],
      next: { who: "you", text: "Two teammates wait for your answer", buttons: [["Open the first", "p"]] },
    },
  },
  {
    id: "settings",
    step: "Settings",
    who: "you",
    steps: 3,
    act: { id: "setup", title: "You stay in charge of models and cost", text: "QualityLayer works inside the coding agents you already pay for, and shows what each step costs." },
    title: "Choose the subagents’ models, and see what each step costs",
    text: "Opus 5.5 is recommended for Discuss and Plan, and judges the result. Sonnet 5.5 builds in subagents. The App estimates the cost of every step.",
    bullets: ["Pick the model of the workers and the judge, or no subagents", "A second opinion from another vendor on risky plans", "Tokens and estimated cost of every step"],
    win: {
      title: "Settings · QualityLayer",
      nav: 2,
      head: "Settings",
      side: [item("Workflow", "subagents, second opinion", "ag", true), item("Agents", "Claude Code, Codex", "ag"), item("Team", "5 members", "ag"), item("Licence", "Team plan", "ag")],
      doc: "Workflow",
      stage: -1,
      chip: ["ok", "Saved"],
      next: { who: "ag", text: "For Discuss and Plan, Opus 5.5 is recommended in your own session.", buttons: [] },
    },
  },
  {
    id: "agents",
    step: "Your agents",
    who: "ag",
    steps: 5,
    title: "It works where your agents already work",
    text: "Claude Code and Codex do the work in their own apps. The QualityLayer App is where you review and approve, on macOS, Windows and Linux.",
    bullets: ["Close the App, and tasks keep running", "A band in Claude Code shows what waits for you", "On a server or in WSL, the App opens in your browser"],
    win: { title: TITLE, nav: 0, head: "Your tasks", side: tasks("Plan waits for you"), doc: TASK, stage: 1, chip: ["you", "Needs you"], next: { who: "you", text: "The plan waits for you", buttons: [["Open it", "p"]] } },
  },
];

/** The story's three parts, as the step bar groups them: a part starts at a chapter with an act heading. */
export const PARTS: { label: string; from: number; to: number }[] = (() => {
  const starts = CHAPTERS.flatMap((c, i) => (i === 0 || c.act ? [i] : []));
  const labels = ["Steps", "Team", "Setup"];
  return starts.map((from, k) => ({ label: labels[k] ?? CHAPTERS[from].step, from, to: (starts[k + 1] ?? CHAPTERS.length) - 1 }));
})();

export const partOf = (ch: number) => PARTS.findIndex((p) => ch >= p.from && ch <= p.to);

/** The bar at the bottom of the App for chapter `ch` at moment `step` of its scene. */
export function nextBar(ch: number, step: number): Next {
  const fixed = CHAPTERS[ch].win.next;
  if (fixed) return fixed;
  const at = (n: number) => step >= n;
  switch (CHAPTERS[ch].id) {
    case "plan":
      return at(6)
        ? { who: "you", text: "Approved. Start a fresh session your way and type", code: "/ql implement retry-webhooks", buttons: [["Copy", "p"]] }
        : { who: "you", text: "The plan waits for your approval", buttons: [["Request changes", ""], ["Approve", step === 5 ? "p press" : "p"]] };
    case "implement":
      return at(7)
        ? { who: "you", text: "Slice 2 is marked risky. Try it before the build goes on.", buttons: [["Try it", "p"]] }
        : { who: "ag", text: "Slices 1 and 3 build side by side. Sonnet 5.5 recommended.", buttons: [] };
    case "verify":
      return at(7)
        ? { who: "you", text: "Every point of Done holds. Your turn to review.", buttons: [["Review", "p"]] }
        : { who: "ag", text: "Checking the change against Done means", buttons: [] };
    case "review":
      return { who: "you", text: "Approve, then create the pull request", buttons: [["Request changes", ""], ["Approve and ship", at(4) ? "p glow" : "p"]] };
    case "ask":
      return at(5)
        ? { who: "you", text: "Dana answered. The plan has her change.", buttons: [["Approve", "p"]] }
        : { who: "you", text: at(2) ? "Waiting for Dana" : "Select a passage to ask about it", buttons: [] };
    default:
      return { who: "ag", text: "", buttons: [] };
  }
}
