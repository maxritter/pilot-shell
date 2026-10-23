/**
 * The workflow as the home page tells it: the seven steps under the hero, and the same seven
 * plus the pull request in the tour. Each `id` is also the step's anchor and screenshot name.
 */

/** Who acts in a step, in the App's colours: amber when you decide, blue when agents work, violet when agents check. */
export type Who = "you" | "agent" | "check";
export type Step = { id: string; name: string; who: Who; line: string; text: string; alt: string };

export const WHO: Record<Who, string> = { you: "You decide", agent: "Agents work", check: "Agents check" };

export const STEPS: Step[] = [
  { id: "discuss", name: "Discuss", who: "you", line: "Settle what you want", text: "Your agent asks only questions that change the result, each with a recommendation. Answer in any order.", alt: "A question about a webhook retry policy, with three choices and a recommendation, in the QualityLayer App" },
  { id: "research", name: "Research", who: "agent", line: "Read the code first", text: "Agents trace how the code works today and what can be reused.", alt: "Research on identity provisioning: a diagram of the existing services and a table of what the change can reuse" },
  { id: "plan", name: "Plan", who: "you", line: "Approve it before any code", text: "Read the plan with its diagrams and artifacts. Comment on any part, then approve it.", alt: "A visual billing architecture explains retries, buffering and replay beside Claude Code messages and tool calls in QualityLayer's Conversation view" },
  { id: "outline", name: "Outline", who: "agent", line: "Split it into tasks", text: "Your agent splits the plan into tasks, each with a scenario that proves it works.", alt: "A queue migration split into six slices in build order, with the scenarios that prove them" },
  { id: "implement", name: "Implement", who: "agent", line: "Build it test first", text: "One agent session builds the slices in order, each task test first, and fixes what fails. Each finished turn of the conversation folds into one line with the files it changed.", alt: "The billing build: slice 3 of 7 in progress, its tasks listed, finished slices marked done" },
  { id: "verify", name: "Verify", who: "check", line: "Check every point on the running program", text: "An agent that did not write the code adds missing tests and checks every point of the plan. A change that crosses a trust boundary gets a security review, and a risky one a second opinion.", alt: "Verification for the billing change: security review, project checks, an independent review and the outcome checks" },
  { id: "review", name: "Review", who: "you", line: "Read the change and its proof", text: "Read the change and its checks in the Review workspace, and open any file in your editor. Approve, or ask for changes.", alt: "Visual Review of a captured billing screen, with invoice totals and controls to accept it or request a change" },
  { id: "pull-request", name: "Pull request", who: "agent", line: "Follow it until it is merged", text: "QualityLayer watches the pull request until it merges. A failing check, a review asking for changes or a conflict appears in Needs you and wakes your agent.", alt: "An open pull request with its checks and review threads kept on the task" },
];

/** The seven steps of every change; the pull request follows them. */
export const WORKFLOW_STEPS = STEPS.slice(0, 7);

/** The step the tour opens on. */
export const FIRST_STEP = "plan";
