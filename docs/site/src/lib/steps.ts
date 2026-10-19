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
  { id: "plan", name: "Plan", who: "you", line: "Approve it before any code", text: "Read the plan with its diagrams and artifacts. Comment on any part, then approve it.", alt: "A visual billing architecture explains retries, buffering and replay beside Claude Code, with its QualityLayer approval band and custom status line" },
  { id: "outline", name: "Outline", who: "agent", line: "Split it into tasks", text: "Your agent splits the plan into tasks, each with a scenario that proves it works.", alt: "A queue migration split into six slices in build order, with the scenarios that prove them" },
  { id: "implement", name: "Implement", who: "agent", line: "Build it test first", text: "Work on separate files runs in parallel. Every test run is recorded.", alt: "The billing build: slice 3 of 7 in progress, its tasks listed, finished slices marked done" },
  { id: "verify", name: "Verify", who: "check", line: "Polish it, then check every point", text: "An agent that did not write the code polishes it, adds missing tests and checks every point of the plan. Risky changes get an independent review.", alt: "Verification lanes for the billing change: polish, security, checks, an independent review and the outcome checks" },
  { id: "review", name: "Review", who: "you", line: "Read the change and its proof", text: "See what changed, why, and the evidence for each agreed point. Approve, or ask for another pass.", alt: "The finished billing change with what you asked for, what changed and how each point was checked" },
  { id: "pull-request", name: "Pull request", who: "agent", line: "Follow it until it is merged", text: "Review threads and failing checks return to the task until the pull request merges.", alt: "An open pull request with its checks and review threads kept on the task" },
];

/** The seven steps of every change; the pull request follows them. */
export const WORKFLOW_STEPS = STEPS.slice(0, 7);

/** The step the tour opens on. */
export const FIRST_STEP = "plan";
