/**
 * The home page's tour: one change followed from request to pull request, then designs, the team
 * and the setup. Each chapter shows one close-up of the QualityLayer App at reading size, drawn
 * from the App's design (qualitylayer/design/app): the top bar with the seven steps and the agent,
 * the step's own track, and the one Your turn card or the agent's turn. Tasks, people and numbers
 * are an illustration.
 */

/** Who acts: you (amber), an agent (blue turning ring), or nobody because it is done. */
export type Who = "you" | "ag" | "ok";

export interface Chapter {
  id: string;
  /** The chapter's label in the step bar. */
  step: string;
  who: Who;
  /**
   * How many moments follow the first. A close-up opens on the first, which already shows what the
   * chapter's text says, then adds to it one moment per second; it never takes the claim away.
   */
  steps: number;
  title: string;
  text: string;
  bullets: string[];
  /** A heading that opens a new part of the story before this chapter. */
  act?: { id: string; title: string; text: string };
}

export const STAGES = ["Discuss", "Research", "Plan", "Outline", "Implement", "Verify", "Review"];

export const TASK = "Retry failed webhooks";

/** The design the Designs chapters draw, ask about and open full size. */
export const DESIGN = { name: "Failed deliveries", purpose: "Every delivery that failed, and when it tries again" };

/** The words a new task starts from, in the New task card. */
export const REQUEST = "Retry failed webhooks, then mail the customer once";

export const CHAPTERS: Chapter[] = [
  {
    id: "discuss",
    step: "Discuss",
    who: "you",
    steps: 5,
    act: { id: "steps", title: "From your request to a pull request", text: "On your own or with your team, a change goes through the same seven steps. You decide where a decision is needed, and your agents do the rest." },
    title: "Your agent asks one batch until the goal is clear",
    text: "Describe the change in your own words. Questions arrive together in Your turn as one batch of three to six, each with a recommendation. Answer in any order; each answer reaches your agent at once, while it keeps reading the code.",
    bullets: ["A bug is reproduced and its cause found", "Too small for a plan? You get a ready prompt", "Each answer becomes part of Done means"],
  },
  {
    id: "research",
    step: "Research",
    who: "you",
    steps: 4,
    title: "Agents read the code before anything is designed",
    text: "Research starts while you answer. Agents read the code without your request in front of them, so they report how it works today; when it leaves real choices open, you get one more batch, and a clear task goes straight to the Plan.",
    bullets: ["Findings are folded to one headline each", "Each choice shows what the code says, side by side", "Nothing in Research needs your approval"],
  },
  {
    id: "plan",
    step: "Plan",
    who: "you",
    steps: 2,
    title: "You approve one plan before any code",
    text: "Another agent reads the Plan first when it can, and yours folds in what it found before you are told. Read the complete Plan with its diagrams, the contracts the build is held to and its proposed outcomes, then approve it or give feedback from its header.",
    bullets: ["Comment on any line or diagram", "Everything the agent decided for you is listed, so you can change it", "The review is recorded under Reviewed by; a local fallback is a self-review"],
  },
  {
    id: "outline",
    step: "Outline",
    who: "ag",
    steps: 3,
    title: "The build is cut into slices while you read the Plan",
    text: "While you read, your agent cuts the Plan into slices: what is built first, which can run side by side, and the scenario that proves each Done means point. An agent that did not write it reads it the way a builder would, and you do not approve it.",
    bullets: ["Every Done means point is tied to a scenario", "Nothing runs that the Plan did not allow", "Approve the Plan and the build can start at once"],
  },
  {
    id: "start",
    step: "Start",
    who: "you",
    steps: 2,
    title: "One command starts the build",
    text: "Implement opens with your Build defaults in one line: the model that plans each slice, the model that builds them, and the effort. Change them for this build, or copy the command as it is.",
    bullets: ["Claude Code, Codex or another agent", "Your defaults come back for the next build", "Paste it in a fresh session"],
  },
  {
    id: "implement",
    step: "Implement",
    who: "ag",
    steps: 5,
    title: "It is built in slices, on its own",
    text: "From that command on, your agent works on its own until the final review. Every task starts with a failing test, and slices that don’t overlap build side by side.",
    bullets: ["QualityLayer records every test run itself", "What the agent decided on the way is listed, and you can ask why", "A login or secret waits in Your turn while other slices keep building"],
  },
  {
    id: "verify",
    step: "Verify",
    who: "ag",
    steps: 7,
    title: "Agents that did not write the code check it",
    text: "Six checks run in a fixed order. Every point of Done means is checked against the running program, with its evidence beside it, and the agent chip names what runs now.",
    bullets: ["Polish and security review come first, then your project's checks", "A second opinion reads a risky change, and a failure is fixed by the agent", "Anything only you can confirm goes to Review"],
  },
  {
    id: "review",
    step: "Review",
    who: "you",
    steps: 5,
    title: "You read the finished change top to bottom, then approve it",
    text: "Your turn holds only what agents could not settle: a live result only you can confirm, and what the agent decided while building. Below it the change reads top to bottom, from why to how it was checked; approve, and the pull request opens in the same order and stays open until it is merged.",
    bullets: ["Every changed file is tagged with the task that made it, and any line takes a comment", "Approve and open a pull request, or approve only", "Threads and failing checks on the pull request come back to you"],
  },
  {
    id: "draw",
    step: "Draw",
    who: "ag",
    steps: 2,
    act: { id: "designs", title: "See the page before it is built", text: "Ask your agent to draw a page, and it shows inside the question it belongs to. Open it full size and point at what should change. The interactive page stays on your computer." },
    title: "Ask, and your agent draws the page",
    text: "Say “mock up the failed deliveries page”. Your agent draws it as one page, and the Plan asks you about it with the page in view: looks right, or say what to change.",
    bullets: ["Inside a task, or for the whole project", "Every design is listed in Files", "Share links include a still; the interactive page stays on your computer"],
  },
  {
    id: "comment",
    step: "Comment",
    who: "you",
    steps: 3,
    title: "Open it full size and point at what to change",
    text: "Click a spot and say what should change. Your agent changes the same page and says in one line what changed, so you always see the latest.",
    bullets: ["Your comment reaches the agent like any other answer", "The page stays clickable while you comment", "Full screen hides everything else"],
  },
  {
    id: "ask",
    step: "Ask",
    who: "you",
    steps: 4,
    act: { id: "team", title: "Bring your team in while it is still a plan", text: "With a Team plan, teammates help shape the plan and review the change, each from their own App." },
    title: "Ask a teammate about any part of the plan",
    text: "Select a passage or a diagram and choose who to ask. They get a Slack message that opens the question in their App.",
    bullets: ["They answer: Looks right, Suggest a change or Reply", "You get a Slack message and a notification with their answer", "Your agent updates the plan with what they suggest"],
  },
  {
    id: "answer",
    step: "Answer",
    who: "ag",
    steps: 2,
    title: "Teammates see the questions for them first",
    text: "Questions for you shows each question with the passage in view. Answer in the App, or let your own agent draft it. Nothing is sent without your yes.",
    bullets: ["Looks right, Suggest a change, Reply or Hand to someone else", "A draft from your agent shows as not sent yet", "Open the Plan at the exact passage"],
  },
  {
    id: "space",
    step: "Team space",
    who: "you",
    steps: 2,
    title: "See your team’s work in one place",
    text: "Your questions to others, what each teammate is building and the step it is at, in one list. Remind or hand a question on from here.",
    bullets: ["A question waiting over a day turns amber", "Reminders go out at most every 4 hours", "Team activity folds into one line"],
  },
  {
    id: "together",
    step: "Review together",
    who: "you",
    steps: 2,
    title: "Review the finished change together",
    text: "Teammates read what changed and its proof. They comment on any part and approve. The code itself is reviewed in your pull request.",
    bullets: ["Their comments reach you in the Comments tab", "The same link follows the task through all seven steps", "Sharing sends the plan, progress and a still of its design"],
  },
  {
    id: "settings",
    step: "Settings",
    who: "you",
    steps: 1,
    act: { id: "setup", title: "You stay in charge of models and cost", text: "QualityLayer works inside the coding agents you already pay for, and shows what each step costs." },
    title: "Choose the models, and see what each step costs",
    text: "Planning defaults and Build defaults set the model, the effort and where each session starts. Plan with Claude Code and build with Codex if you like. The cost of every step is estimated at list price.",
    bullets: ["Change anything for one build when you start it", "An agent that never wrote the code decides whether it passes", "The other coding agent reads the Plan, and risky changes"],
  },
  {
    id: "agents",
    step: "Your agents",
    who: "ag",
    steps: 3,
    title: "It works where your agents already work",
    text: "New task: say what you want, pick the model and where it starts, and copy one command for Claude Code, Codex or another agent. The App runs on macOS, Windows and Linux. On a server or in WSL, it opens in your browser.",
    bullets: ["Close the App and the agents keep working", "A notification tells you when something needs you", "Updates download quietly and install when you restart"],
  },
];

/** The story's parts, as the step bar groups them: a part starts at a chapter with an act heading. */
export const PARTS: { label: string; from: number; to: number }[] = (() => {
  const starts = CHAPTERS.flatMap((c, i) => (c.act ? [i] : []));
  const labels = ["Steps", "Designs", "Team", "Setup"];
  return starts.map((from, k) => ({ label: labels[k] ?? CHAPTERS[from].step, from, to: (starts[k + 1] ?? CHAPTERS.length) - 1 }));
})();

export const partOf = (ch: number) => PARTS.findIndex((p) => ch >= p.from && ch <= p.to);

/**
 * Discuss asks one batch of four questions, answered in any order. At each moment: which questions
 * are answered, the one in focus, whether its recommendation is picked, and the answer just sent.
 */
export const DISCUSS_BATCH = 4;
const DISCUSS_MOMENTS: { answered: number[]; focus: number; picked: boolean; sent: number | null }[] = [
  { answered: [], focus: 0, picked: false, sent: null },
  { answered: [], focus: 0, picked: true, sent: null },
  { answered: [0], focus: 2, picked: false, sent: 0 },
  { answered: [0], focus: 2, picked: true, sent: 0 },
  { answered: [0, 2], focus: 1, picked: false, sent: 2 },
  { answered: [0, 2], focus: 1, picked: true, sent: 2 },
];
export const discussAt = (step: number) => DISCUSS_MOMENTS[Math.min(step, DISCUSS_MOMENTS.length - 1)];

/** How many of the build's 5 tasks are committed at moment `step` of the Implement close-up: slice 1 is done when it opens, slices 2 and 3 build side by side. */
export const committedTasks = (step: number) => 2 + (step >= 1 ? 1 : 0) + (step >= 2 ? 1 : 0) + (step >= 3 ? 1 : 0);

/** The moment each of the Verify checklist's 12 checks passes; a check runs for the moment before. */
export const PASS_AT = [1, 2, 2, 2, 2, 2, 3, 4, 3, 4, 5, 6];
export const checksPassed = (step: number) => PASS_AT.filter((when) => step >= when).length;

/** The check that runs at moment `step` of the Verify close-up, in the order the chapter names them. */
export const VERIFY_CHECKS = ["Polish", "Security review", "Project checks", "Independent review", "Second opinion", "Fixes"];
export const checkRunning = (step: number) => VERIFY_CHECKS[Math.max(0, Math.min(VERIFY_CHECKS.length - 1, step - 1))];

/**
 * Which chapter is in view. Each chapter's first line (its act heading, when it opens a part)
 * counts as read once it has risen past a line down the screen: 72 % down when the close-up is
 * pinned beside the text, 60 % when every chapter carries its own. Those are the lines where the
 * chapter entering from below shows as much text as the one leaving above (fitted on sampled scrolls
 * of the page at 1440 x 900 and 390 x 844). The chapter in view is the last one read, and the first
 * before any is, so the close-up belongs to the text on screen.
 */
export const READ_LINE = { pinned: 0.72, inline: 0.6 };
export function chapterInView(tops: number[], viewport: number, line: number): number {
  let best = 0;
  tops.forEach((top, i) => {
    if (top <= viewport * line) best = i;
  });
  return best;
}
